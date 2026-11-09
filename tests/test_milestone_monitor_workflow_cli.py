"""Comandos estruturados isolados: dados reais/config/cache nunca são usados."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from milestone_monitor_fixtures import ROOT, CONFIG
from milestone_monitor.common import MonitorError
from milestone_monitor.coordinator import Coordinator, read_input
from milestone_monitor.journal import Journal
from milestone_monitor.store import Store
from test_milestone_monitor_journal import operation
from test_workflow_execution_state import FAKE_GH


class WorkflowCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.config = self.path / "config.json"
        self.config.write_text(json.dumps(CONFIG))
        (self.path / "gh").write_text(FAKE_GH)
        (self.path / "gh").chmod(0o755)
        self.env = {**os.environ, "PATH": f"{self.path}:{os.environ['PATH']}", "FAKE_GH_STATE": str(self.path / "github.json"),
                    "XDG_CONFIG_HOME": str(self.path / "config"), "XDG_STATE_HOME": str(self.path / "state"), "PYTHONDONTWRITEBYTECODE": "1"}

    def invoke(self, action, *extra, payload=None, env=None):
        return subprocess.run([sys.executable, "-B", str(ROOT / "scripts/aew"), "workflow", action,
                               "--config", str(self.config), "--state-dir", str(self.path / "cache"), *extra],
                              input=json.dumps(payload) if payload is not None else None,
                              env=env or self.env, capture_output=True, text=True, timeout=15)

    def test_transition_replay_reconcile_and_help(self):
        first = self.invoke("transition", "--input", "-", payload=operation())
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        value = json.loads(first.stdout)
        self.assertTrue(value["accepted"])
        self.assertEqual(value["publication"], "published")
        second = self.invoke("transition", "--input", "-", payload=operation())
        self.assertEqual(second.returncode, 0, second.stdout)
        state = json.loads((self.path / "github.json").read_text())
        from workflow_metrics import parse_run_comment
        self.assertEqual(len(parse_run_comment(state["comments"][0]["body"])["events"]), 1)
        result = self.invoke("reconcile", "--issue", operation()["issue"], "--run-id", "wf-fixture", "--coordinator")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)["total"], 0)
        self.assertEqual(self.invoke("transition", "--help").returncode, 0)

    def test_no_authority_or_invalid_identity_never_accepts_or_calls_github(self):
        for payload in (operation(coordinator=False), operation(issue="https://evil/issues/7"),
                        operation(operation_id="bad id"), {**operation(), "prompt": "SEGREDO_FIXTURE"}):
            result = self.invoke("transition", "--input", "-", payload=payload)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(json.loads(result.stdout)["accepted"])
            self.assertNotIn("SEGREDO_FIXTURE", result.stdout + result.stderr)
        self.assertFalse((self.path / "cache/monitor.sqlite3").exists())
        self.assertFalse((self.path / "github.json").exists())
        result = self.invoke("reconcile", "--issue", operation()["issue"], "--run-id", "wf-fixture")
        self.assertFalse(json.loads(result.stdout)["accepted"])

    def test_missing_helper_accepts_durably_and_reports_pending_not_success(self):
        result = self.invoke("transition", "--input", "-", payload=operation(), env={**self.env, "PATH": "/caminho-inexistente"})
        self.assertNotEqual(result.returncode, 0)
        value = json.loads(result.stdout)
        self.assertTrue(value["accepted"])
        self.assertEqual(value["publication"], "pending")
        pending = Journal(Store(self.path / "cache")).get("op-start")
        self.assertEqual(pending["payload"]["at"], operation()["at"])
        replay = self.invoke("reconcile", "--issue", operation()["issue"], "--run-id", "wf-fixture", "--coordinator")
        self.assertEqual(replay.returncode, 0, replay.stdout)

    def test_conflicting_identity_and_wrong_record_scope_preserve_state(self):
        self.invoke("transition", "--input", "-", payload=operation())
        before = (self.path / "github.json").read_bytes()
        result = self.invoke("transition", "--input", "-", payload=operation(at="2026-11-08T00:01:00Z"))
        self.assertFalse(json.loads(result.stdout)["accepted"])
        self.assertEqual((self.path / "github.json").read_bytes(), before)

    def test_input_is_bounded_and_rejects_duplicate_keys(self):
        for raw in (b"x" * 16385, b'{"operation_id":"a","operation_id":"b"}', b"SEGREDO_FIXTURE"):
            with self.assertRaises(MonitorError):
                read_input("-", io.BytesIO(raw))

    def test_denied_github_sanitizes_error_and_preserves_accepted_operation(self):
        (self.path / "gh").write_text('#!/usr/bin/env python3\nimport sys\nprint("401 SEGREDO_FIXTURE",file=sys.stderr)\nsys.exit(1)\n')
        result = self.invoke("transition", "--input", "-", payload=operation())
        self.assertTrue(json.loads(result.stdout)["accepted"])
        self.assertEqual(json.loads(result.stdout)["publication"], "pending")
        self.assertNotIn("SEGREDO_FIXTURE", result.stdout + result.stderr)
        self.assertNotIn(b"SEGREDO_FIXTURE", (self.path / "cache/monitor.sqlite3").read_bytes())

    def test_wrong_canonical_scope_is_conflict_not_overwrite(self):
        self.invoke("transition", "--input", "-", payload=operation())
        path = self.path / "github.json"
        state = json.loads(path.read_text())
        state["comments"][0]["body"] = state["comments"][0]["body"].replace('"repository":"owner/repo"', '"repository":"other/repo"')
        path.write_text(json.dumps(state))
        before = path.read_bytes()
        payload = operation("op-stage", event="dispatch", stage="apply", worker_id="worker-A",
                            execution={"kind": "worker", "id": "execution-A"}, depends_on=["op-start"])
        result = self.invoke("transition", "--input", "-", payload=payload)
        self.assertEqual(json.loads(result.stdout)["publication"], "conflict")
        self.assertEqual(path.read_bytes(), before)

    def test_documented_pt_en_json_examples_run_only_against_fake_github(self):
        import re
        documents = []
        for language, heading in (("", "## Transições estruturadas do coordenador"), (".en", "## Structured coordinator transitions")):
            text = (ROOT / f"docs/milestone-monitor{language}.md").read_text().split(heading, 1)[1]
            documents.append([json.loads(block) for block in re.findall(r"```json\n(.*?)\n```", text, re.S)])
        self.assertEqual(documents[0], documents[1])
        run, opening, binding = documents[0]
        for name, payload in (("run.json", run), ("apply.json", opening), ("session.json", binding)):
            (self.path / name).write_text(json.dumps(payload))
        self.assertEqual(self.invoke("transition", "--input", str(self.path / "run.json")).returncode, 0)
        for _ in range(2):
            value = json.loads(self.invoke("transition", "--input", str(self.path / "apply.json")).stdout)
            self.assertEqual((value["publication"], value["binding"]), ("published", "pending"))
        value = json.loads(self.invoke("reconcile", "--issue", opening["issue"], "--run-id", opening["run_id"], "--coordinator",
                                      "--binding-input", str(self.path / "session.json")).stdout)
        self.assertEqual(value["operations"][0]["binding_reason"], "runtime_disabled")
        from workflow_metrics import parse_run_comment
        state = json.loads((self.path / "github.json").read_text())
        self.assertEqual(len(parse_run_comment(state["comments"][0]["body"])["events"]), 2)
