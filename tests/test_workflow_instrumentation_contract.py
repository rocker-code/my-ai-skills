"""Contrato de conteúdo e walkthrough fake, não avaliação comportamental de LLM."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from milestone_monitor.projection import STAGES
from milestone_monitor.common import MonitorError
from test_milestone_monitor_journal import operation
import test_milestone_monitor_auto_bind as auto


class InstrumentationContractTests(unittest.TestCase):
    def test_thirteen_frontiers_single_writer_stable_identity_and_optin(self):
        protocol = (ROOT / "protocol/WORKFLOW_INSTRUMENTATION.md").read_text()
        for stage in STAGES:
            self.assertIn("| " + stage + " |", protocol)
        for field in ("issue_url", "run_id", "stage", "worker_id", "execution.kind", "execution.id", "operation_ids", "session_id", "worktree", "branch", "state_dir"):
            self.assertIn(field, protocol)
        self.assertIn("Invocar uma skill isoladamente não", protocol)
        self.assertIn("Workers, observador e dashboard nunca publicam", protocol)
        self.assertIn("não produz `observe completed`", protocol)
        skill = (ROOT / "skills/milestone-orchestrator/SKILL.md").read_text()
        shared = (ROOT / "protocol/AI_WORKFLOW.md").read_text()
        for body in (skill, shared):
            self.assertIn("WORKFLOW_INSTRUMENTATION.md", body)
            self.assertIn("workflow reconcile", body)
        self.assertIn("bundle_reference milestone-orchestrator protocol/WORKFLOW_INSTRUMENTATION.md", (ROOT / "scripts/sync-plugin").read_text())

    def test_executors_preserve_conditional_handoff_without_becoming_writers(self):
        names = ("issue-audit", "issue-explore", "resolve-questions", "implement-issue", "openspec-workflow", "apply-issue",
                 "prepare-pr", "pr-audit", "architecture-audit", "github-resolution", "address-pr-review", "post-pr-audit", "kaizen")
        for name in names:
            with self.subTest(skill=name):
                body = (ROOT / f"skills/{name}/SKILL.md").read_text()
                for token in ("workflow_instrumentation.enabled: true", "WORKFLOW_INSTRUMENTATION.md", "operation_ids", "session_id: null", "worktree"):
                    self.assertIn(token, body)
                self.assertIn("isolada", body)
                self.assertIn("gate", body)
                self.assertIn("coordenador", body)


class WalkthroughTests(unittest.TestCase):
    setUp = auto.AutoBindTests.setUp
    opening = auto.AutoBindTests.opening

    def test_one_issue_from_dispatch_to_correlated_result_has_one_writer(self):
        opening = self.opening()
        self.assertEqual(self.coordinator.transition(opening)["binding"], "bound")
        writes = self.github.writes
        # Simula o retorno do worker; nenhuma escrita/execução remota pelo worker.
        returned = {"issue_url": opening["issue"], "run_id": opening["run_id"], "stage": "apply", "worker_id": "worker-A",
                    "execution": opening["execution"], "session_id": "ses_fixture", "worktree": "/fixture/worktree",
                    "result": "completed", "candidate_sha": "abcdef0", "gates_verified": True,
                    "evidence_refs": ["abcdef0"], "finished_at": "2026-11-08T00:02:00Z"}
        self.assertEqual(self.github.writes, writes)
        self.assertEqual(returned["execution"], opening["execution"])
        self.assertTrue(returned["gates_verified"])
        result = {**opening, "operation_id": "op-result", "event": "observe", "at": returned["finished_at"],
                  "state": returned["result"], "source": "runtime_event", "log_ref": "worker-result:execution-A",
                  "evidence": returned["evidence_refs"], "depends_on": ["op-open"]}
        del result["binding"]
        self.assertEqual(self.coordinator.transition(result)["publication"], "published")
        end = {**result, "operation_id": "op-end", "event": "stage-end", "status": "completed", "depends_on": ["op-result"]}
        for field in ("state", "source", "log_ref"):
            del end[field]
        self.assertEqual(self.coordinator.transition(end)["publication"], "published")
        from workflow_metrics import parse_run_comment, summarize_run
        record = parse_run_comment(self.github.comments[0]["body"])
        self.assertEqual(len(self.github.comments), 1)
        self.assertEqual([e["type"] for e in record["events"]], ["run_started", "stage_started", "state_observed", "stage_finished"])
        self.assertEqual(summarize_run(record)["stages"][0]["verified_state"], "completed")

    def test_planning_to_apply_unknown_session_rework_and_another_issue_are_distinct(self):
        planning = {**self.opening(), "operation_id": "op-plan", "stage": "proposal", "execution": {"kind": "worker", "id": "execution-plan"}}
        self.assertEqual(self.coordinator.transition(planning)["binding"], "bound")
        planning_key = next(iter(self.store.bindings()))
        closing = {**planning, "operation_id": "op-plan-end", "event": "stage-end", "status": "completed",
                   "at": "2026-11-08T00:02:00Z", "depends_on": ["op-plan"]}
        del closing["binding"]
        self.coordinator.transition(closing)
        apply = {**self.opening(None), "at": "2026-11-08T00:03:00Z", "depends_on": ["op-plan-end"]}
        self.assertEqual(self.coordinator.transition(apply)["binding_reason"], "session_unavailable")
        self.assertEqual(self.store.bindings()[planning_key]["session_id"], "ses_fixture")
        self.store.unbind(planning_key)
        self.fixture["session.get"]["data"]["id"] = "ses_apply_fresh"
        report = self.coordinator.reconcile(apply["issue"], apply["run_id"], True,
            {"version": 1, "operation_id": "op-open", "session_id": "ses_apply_fresh"})
        self.assertEqual(report["operations"][0]["binding"], "bound")
        self.assertEqual(next(iter(self.store.bindings().values()))["session_id"], "ses_apply_fresh")
        failed = {**apply, "operation_id": "op-apply-failed", "event": "stage-end", "status": "failed", "at": "2026-11-08T00:04:00Z"}
        del failed["binding"]
        self.coordinator.transition(failed)
        self.store.unbind(next(iter(self.store.bindings())))
        rework = {**apply, "operation_id": "op-rework", "event": "rework", "reason": "review", "at": "2026-11-08T00:05:00Z",
                  "depends_on": ["op-apply-failed"]}
        del rework["binding"]
        self.coordinator.transition(rework)
        next_execution = {**apply, "operation_id": "op-reapply", "execution": {"kind": "worker", "id": "execution-rework"},
                          "at": "2026-11-08T00:06:00Z", "depends_on": ["op-rework"]}
        self.assertEqual(self.coordinator.transition(next_execution)["binding_reason"], "session_unavailable")
        other = operation("op-run-8", issue="https://github.com/owner/repo/issues/8")
        self.assertEqual(self.coordinator.transition(other)["publication"], "published")
        with self.assertRaises(MonitorError):
            self.coordinator.transition({**other, "operation_id": "op-other-dependency", "depends_on": ["op-open"]})
        self.assertEqual(len(self.github.comments), 2)
