"""Runtime observation contract, with a fake GitHub comment API."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from workflow_metrics import parse_run_comment, summarize_run  # noqa: E402

BASE = "2026-11-04T10:00:00Z"
EVIDENCE = "evidence:ev-20261104T030000Z-1a2b3c4d"


def event(kind, minute, **fields):
    return {"type": kind, "at": f"2026-11-04T10:{minute:02d}:00Z", "stage": "tests", "worker_id": "worker-1", **fields}


def record(*events):
    return {"schema_version": 1, "run_id": "wf-test", "created_at": BASE, "status": "running",
            "issue": {"number": 1, "url": "https://github.com/owner/repo/issues/1"}, "events": list(events)}


def summary(value, minute=55):
    return summarize_run(value, datetime(2026, 11, 4, 10, minute, tzinfo=timezone.utc))


FAKE_GH = '''#!/usr/bin/env python3
import json, os, sys
path = os.environ["FAKE_GH_STATE"]
try:
    with open(path) as source: state = json.load(source)
except FileNotFoundError:
    state = {"comments": [], "next_id": 1}
args = sys.argv[1:]
if args[0] == "api":
    endpoint = next((arg for arg in args if arg.startswith("repos/")), "")
    body = next((arg[5:] for arg in args if arg.startswith("body=")), None)
    if body is None:
        print(json.dumps([[item for item in state["comments"] if item["body"].split('"number":')[1].split(',')[0].strip() == endpoint.split('/')[4]]]))
    elif "--method" in args:
        item = next(item for item in state["comments"] if item["id"] == int(endpoint.split("/")[-1]))
        item["body"] = body
    else:
        state["comments"].append({"id": state["next_id"], "body": body})
        state["next_id"] += 1
    with open(path, "w") as target: json.dump(state, target)
    if body is not None: print("{}")
elif args[0] == "issue":
    url = next(arg for arg in args if arg.startswith("https://"))
    print(json.dumps({"number": int(url.split("/")[-1]), "url": url, "title": "Execution", "state": "OPEN"}))
elif args[0] == "pr": print("[]")
'''


class FakeGitHub(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "state.json"
        fake = Path(self.temp.name) / "gh"
        fake.write_text(FAKE_GH)
        fake.chmod(0o755)
        self.env = dict(os.environ, PATH=f"{self.temp.name}:{os.environ['PATH']}", FAKE_GH_STATE=str(self.path),
                        PYTHONDONTWRITEBYTECODE="1")
        self.issue = "https://github.com/owner/repo/issues/1"
        self.invoke("run-start")

    def invoke(self, name, *args, issue=None, ok=True):
        result = subprocess.run([str(ROOT / "scripts/workflow-event"), name, "--issue", issue or self.issue,
                                 "--run-id", "wf-test", *args], text=True, capture_output=True, env=self.env)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def saved(self, issue=1):
        state = json.loads(self.path.read_text())
        return parse_run_comment(state["comments"][issue - 1]["body"])

    def test_observe_records_correlation_and_rejects_unsafe_id(self):
        self.invoke("dispatch", "--stage", "tests", "--worker-id", "worker-1", "--execution-kind", "job", "--execution-id", "job-1")
        self.invoke("observe", "--stage", "tests", "--worker-id", "worker-1", "--state", "running", "--source", "runtime_query", "--execution-kind", "job", "--execution-id", "job-1")
        self.assertEqual(self.saved()["events"][-1]["execution"], {"kind": "job", "id": "job-1"})
        before = self.path.read_bytes()
        for unsafe in ("a b", "a?b", "a=b", "a&b"):
            self.invoke("observe", "--stage", "tests", "--state", "running", "--source", "runtime_query", "--execution-kind", "job", "--execution-id", unsafe, ok=False)
            self.assertEqual(self.path.read_bytes(), before)

    def test_observed_at_is_effective_time_and_validated(self):
        self.invoke("dispatch", "--stage", "tests", "--worker-id", "worker-1", "--execution-kind", "job", "--execution-id", "a")
        start = self.saved()["events"][-1]["at"]
        self.invoke("observe", "--stage", "tests", "--worker-id", "worker-1", "--state", "completed", "--source", "runtime_event", "--execution-kind", "job", "--execution-id", "a", "--observed-at", start)
        self.assertEqual(self.saved()["events"][-1]["at"], start)
        self.assertIn("recorded_at", self.saved()["events"][-1])
        before = self.path.read_bytes()
        for timestamp in ("2026-01-01T00:00:00Z", "2099-01-01T00:00:00Z", "2026-11-04T10:00:00", "2026-11-04T00:00:00Z"):
            self.invoke("observe", "--stage", "tests", "--worker-id", "worker-1", "--state", "completed", "--source", "runtime_event", "--execution-kind", "job", "--execution-id", "a", "--observed-at", timestamp, ok=False)
            self.assertEqual(self.path.read_bytes(), before)
        dispatch = datetime.fromisoformat(start.replace("Z", "+00:00"))
        # A second typed incarnation dispatched later cannot finish before its own start.
        future = (dispatch + timedelta(seconds=5)).isoformat().replace("+00:00", "Z")
        earlier = (dispatch + timedelta(seconds=2)).isoformat().replace("+00:00", "Z")
        self.invoke("dispatch", "--stage", "tests", "--worker-id", "worker-2", "--execution-kind", "job", "--execution-id", "b", "--observed-at", future)
        before = self.path.read_bytes()
        pair = ("--stage", "tests", "--worker-id", "worker-2", "--execution-kind", "job", "--execution-id", "b", "--observed-at", earlier)
        self.invoke("observe", *pair, "--state", "completed", "--source", "runtime_event", ok=False)
        self.assertEqual(self.path.read_bytes(), before)
        self.invoke("stage-end", *pair, "--status", "completed", ok=False)
        self.assertEqual(self.path.read_bytes(), before)

    def test_log_ref_validation(self):
        for ref in ("runtime:task-7f3a", "https://github.com/o/r/actions/runs/1", "abcdef0"):
            self.invoke("observe", "--stage", "tests", "--state", "running", "--source", "runtime_query", "--log-ref", ref)
        before = self.path.read_bytes()
        for ref in ("https://user:pass@example.com/x", "http://evil.example/x", "https://github.com/o/r?token=secret", "https://github.com/o/r#fragment", "https://github.com/user:pass@evil.example/x", "runtime:a b", "runtime:x?token=1"):
            self.invoke("observe", "--stage", "tests", "--state", "running", "--source", "runtime_query", "--log-ref", ref, ok=False)
            self.assertEqual(self.path.read_bytes(), before)
        self.invoke("observe", "--stage", "tests", "--state", "running", "--source", "runtime_query", "--evidence", "runtime:task-7f3a", ok=False)

    def test_observation_links_evidence_reference(self):
        self.invoke("dispatch", "--stage", "tests", "--worker-id", "worker-1", "--execution-kind", "test_run", "--execution-id", "ev-20261104T030000Z-1a2b3c4d")
        self.invoke("observe", "--stage", "tests", "--worker-id", "worker-1", "--state", "running", "--source", "runtime_query", "--execution-kind", "test_run", "--execution-id", "ev-20261104T030000Z-1a2b3c4d", "--evidence", EVIDENCE)
        self.assertEqual(summarize_run(self.saved())["status_summary"]["last_confirmed"]["evidence"], EVIDENCE)
        self.invoke("observe", "--stage", "tests", "--worker-id", "worker-1", "--state", "completed", "--source", "runtime_event", "--execution-kind", "test_run", "--execution-id", "ev-20261104T030000Z-1a2b3c4d", "--report", "present")
        self.assertEqual(summarize_run(self.saved())["status_summary"]["last_confirmed"]["evidence"], EVIDENCE)

    def test_documented_dispatch_observe_and_close_sequence(self):
        pair = ("--stage", "tests", "--worker-id", "worker-1", "--execution-kind", "job", "--execution-id", "job-42")
        self.invoke("dispatch", *pair)
        self.invoke("observe", *pair, "--state", "completed", "--source", "runtime_event", "--report", "present", "--log-ref", "runtime:job-42")
        self.invoke("stage-end", *pair, "--status", "completed")
        result = subprocess.run([str(ROOT / "scripts/workflow-report"), self.issue, "--format", "json"],
                                capture_output=True, text=True, env=self.env, check=True)
        self.assertEqual(json.loads(result.stdout)["runs"][0]["stages"][0]["executions"][0]["execution"],
                         {"kind": "job", "id": "job-42"})

    def test_repeated_observation_is_deduplicated(self):
        args = ("--stage", "tests", "--state", "completed", "--source", "runtime_event")
        self.invoke("stage-start", "--stage", "tests")
        self.invoke("observe", *args)
        count = len(self.saved()["events"])
        self.assertTrue(json.loads(self.invoke("observe", *args).stdout)["deduplicated"])
        self.assertEqual(len(self.saved()["events"]), count)
        self.assertIn("last_seen_at", self.saved()["events"][-1])
        self.invoke("observe", *args, "--evidence", EVIDENCE)
        self.assertEqual(len(self.saved()["events"]), count + 1)

    def test_reused_pair_stale_callback_isolated_by_execution(self):
        pair = ("--stage", "tests", "--worker-id", "worker-1")
        self.invoke("dispatch", *pair, "--execution-kind", "job", "--execution-id", "a")
        self.invoke("stage-end", *pair, "--status", "completed", "--execution-kind", "job", "--execution-id", "b", ok=False)
        self.invoke("stage-end", *pair, "--status", "completed", ok=False)
        self.invoke("stage-end", *pair, "--status", "completed", "--execution-kind", "job", "--execution-id", "a")
        self.invoke("dispatch", *pair, "--execution-kind", "job", "--execution-id", "a", ok=False)
        self.invoke("dispatch", *pair, "--execution-kind", "job", "--execution-id", "b")
        self.invoke("observe", *pair, "--state", "completed", "--source", "runtime_event", "--execution-kind", "job", "--execution-id", "a")
        self.assertEqual(summarize_run(self.saved())["status_summary"]["activity_state"], "unobserved")

    def test_untyped_second_incarnation_closes_and_does_not_deduplicate_first(self):
        start = datetime.fromisoformat(self.saved()["created_at"].replace("Z", "+00:00"))
        def at(seconds):
            return (start + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")
        self.invoke("stage-start", "--stage", "tests", "--observed-at", at(1))
        self.invoke("observe", "--stage", "tests", "--state", "running", "--source", "runtime_query", "--observed-at", at(2))
        self.invoke("stage-end", "--stage", "tests", "--status", "completed", "--observed-at", at(3))
        self.invoke("stage-start", "--stage", "tests", "--observed-at", at(4))
        result = self.invoke("observe", "--stage", "tests", "--state", "running", "--source", "runtime_query", "--observed-at", at(5))
        self.assertNotIn("deduplicated", result.stdout)
        self.invoke("stage-end", "--stage", "tests", "--status", "completed", "--observed-at", at(6))

    def test_two_issues_same_run_are_independent_and_finished_record_refuses_stage(self):
        self.invoke("run-end", "--status", "completed")
        before = self.path.read_bytes()
        for name, extra in (("stage-start", ("--stage", "tests")), ("dispatch", ("--stage", "tests", "--worker-id", "worker-1")), ("wait-start", ("--stage", "tests", "--reason", "ci"))):
            self.invoke(name, *extra, ok=False)
            self.assertEqual(self.path.read_bytes(), before)
        other = "https://github.com/owner/repo/issues/2"
        self.invoke("run-start", issue=other)
        self.invoke("stage-start", "--stage", "tests", issue=other)
        self.assertNotEqual(summarize_run(self.saved())["current_stage"], summarize_run(self.saved(2))["current_stage"])


class StateMetricsTest(unittest.TestCase):
    def test_async_dispatch_duration_until_worker_completion(self):
        run = record(event("stage_started", 0, dispatch="async", execution={"kind": "worker", "id": "a"}),
                     event("state_observed", 30, state="completed", source="runtime_event", execution={"kind": "worker", "id": "a"}))
        result = summary(run)
        self.assertEqual(result["recorded_work_seconds"], 1800)
        self.assertEqual(result["status_summary"]["activity_state"], "needs_reconciliation")

    def test_unknown_observation_stops_work_and_requires_reconciliation(self):
        run = record(event("stage_started", 0), event("state_observed", 10, state="unknown", source="runtime_query"),
                     event("state_observed", 20, state="running", source="runtime_query"))
        result = summary(run)
        self.assertEqual(result["recorded_work_seconds"], 600)
        self.assertEqual(result["status_summary"]["activity_state"], "unknown")
        self.assertEqual(result["status_summary"]["blocker"], "needs_reconciliation")
        self.assertEqual(result["status_summary"]["last_confirmed"]["state"], "unknown")

    def test_delayed_stage_end_uses_terminal_observation_for_closed_work(self):
        run = record(event("stage_started", 0), event("state_observed", 30, state="completed", source="runtime_event"),
                     event("wait_started", 35, reason="ci"), event("stage_finished", 40), event("wait_finished", 45, reason="ci"))
        result = summary(run)
        self.assertEqual(result["stages"][0]["elapsed_seconds"], 2400)
        self.assertEqual(result["recorded_work_seconds"], 1800)

    def test_reused_pair_stale_callback_isolated_by_execution(self):
        a, b = {"kind": "job", "id": "a"}, {"kind": "job", "id": "b"}
        run = record(event("stage_started", 0, execution=a), event("stage_finished", 40, execution=a),
                     event("stage_started", 45, execution=b, next="inspecionar B"),
                     event("state_observed", 30, state="completed", source="runtime_event", execution=a,
                           recorded_at="2026-11-04T10:50:00Z", next="fechar A"),
                     event("state_observed", 50, state="running", source="agent_prose"))
        result = summary(run)
        self.assertEqual(result["status_summary"]["activity_state"], "unobserved")
        self.assertIsNone(result["status_summary"]["last_confirmed"])
        self.assertIsNone(result["status_summary"]["verified_at"])
        self.assertEqual(result["status_summary"]["next_action"], "inspecionar B")
        self.assertEqual(result["recorded_work_seconds"], 1800 + 600)

    def test_untyped_observation_requires_unambiguous_window(self):
        run = record(event("stage_started", 0), event("stage_finished", 5),
                     event("state_observed", 10, state="completed", source="runtime_event"))
        self.assertEqual(summary(run)["recorded_work_seconds"], 300)
        self.assertIsNone(summary(run)["status_summary"]["last_confirmed"])

    def test_wait_open_state_and_resumption(self):
        run = record(event("stage_started", 0), event("state_observed", 1, state="running", source="runtime_event"),
                     event("wait_started", 10, reason="ci"))
        self.assertEqual(summary(run, 20)["status_summary"]["activity_state"], "waiting:ci")
        run["events"].append(event("wait_finished", 30, reason="ci"))
        self.assertEqual(summary(run)["status_summary"]["activity_state"], "working")

    def test_weak_sources_do_not_confirm_activity(self):
        run = record(event("stage_started", 0), event("state_observed", 5, state="running", source="agent_prose"))
        self.assertEqual(summary(run)["status_summary"]["activity_state"], "unconfirmed")
        self.assertIsNone(summary(run)["status_summary"]["last_confirmed"])

    def test_wait_classification_owner_input_ci_environment(self):
        for reason in ("owner_input", "ci", "environment", "tests"):
            run = record(event("stage_started", 0), event("state_observed", 0, state="running", source="runtime_event"),
                         event("wait_started", 10, reason=reason), event("wait_finished", 50, reason=reason))
            result = summary(run)
            self.assertEqual(result["recorded_work_seconds"], 900)
            self.assertEqual(result["wait_seconds_by_reason"][reason], 2400)

    def test_missing_report_is_incomplete_evidence(self):
        execution = {"kind": "test_run", "id": "junit-42"}
        run = record(event("stage_started", 0, execution=execution),
                     event("state_observed", 20, state="completed", source="test_report", report="absent", execution=execution),
                     event("stage_finished", 30, execution=execution))
        result = summary(run)
        self.assertEqual(result["incomplete_evidence"][0]["reason"], "missing_report")
        self.assertEqual(result["status_summary"]["last_confirmed"]["evidence"], "não verificada")

    def test_legacy_record_unchanged_and_unobserved(self):
        run = record(event("stage_started", 0), event("stage_finished", 30))
        self.assertEqual(summary(run)["recorded_work_seconds"], 1800)
        self.assertEqual(summary(run)["status_summary"]["activity_state"], "unobserved")

    def test_report_shows_status_summary(self):
        from importlib.machinery import SourceFileLoader
        from importlib.util import module_from_spec, spec_from_loader
        loader = SourceFileLoader("workflow_report_execution", str(ROOT / "scripts/workflow-report"))
        spec = spec_from_loader(loader.name, loader)
        report_cli = module_from_spec(spec)
        loader.exec_module(report_cli)
        execution = {"kind": "test_run", "id": "junit-42"}
        row = summary(record(event("stage_started", 0, execution=execution),
                             event("state_observed", 20, state="completed", source="test_report", report="present", execution=execution)))
        row["issue"]["title"] = "Execution"
        row["issue"]["state"] = "OPEN"
        row["quality"] = {"review_findings": {}, "failed_checks": [], "pending_checks": []}
        data = {"scope": "issue", "repository": "owner/repo", "generated_at": BASE, "tracked_issue_count": 1,
                "issue_count": 1, "runs": [row], "note": "note"}
        output = report_cli.render_markdown(data)
        self.assertIn("não verificada", output)
        self.assertIn("Estado verificado", output)
        self.assertNotIn("aprovada", output)
        self.assertIn("status_summary", json.dumps(row))


if __name__ == "__main__":
    unittest.main()
