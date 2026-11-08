"""M4/M5/M11: estados exclusivos sem reimplementar correlação canônica."""
import copy
import json
import unittest
from datetime import timedelta

from milestone_monitor_fixtures import *
from milestone_monitor.common import MonitorError
from milestone_monitor.ingest import record_of
from milestone_monitor.projection import analyze, incarnation_key, issue_view
from workflow_metrics import summarize_run


class StateTests(unittest.TestCase):
    def view(self, value, issue=None, runtime=None, bindings=None, now=NOW, started=STARTED):
        return issue_view(issue or ISSUE, snapshots(value), runtime or {}, bindings or {}, now, DEFAULTS, started)

    def test_pending_running_expired_future_and_cache_reopen(self):
        value = record(event("stage_started"), event("state_observed", 20, state="running", source="runtime_query"))
        self.assertEqual(self.view(value)["group"], "running")
        self.assertEqual(self.view(value, now=NOW+timedelta(seconds=60))["group"], "pending")
        self.assertEqual(self.view(value, now=STARTED)["group"], "pending")
        self.assertEqual(self.view(value, started=NOW)["group"], "pending")
        self.assertEqual(self.view(record())["label"], "inativa / sem confirmação recente")

    def test_waits_win_over_parallel_workers_and_closed_github_wins(self):
        for reason, label in [("owner_input", "aguardando decisão"), ("tests", "aguardando testes"), ("ci", "aguardando CI")]:
            value = record(event("stage_started"), event("state_observed", 20, state="running", source="runtime_query"),
                           event("wait_started", 21, reason=reason, worker_id="other"))
            view = self.view(value)
            self.assertEqual((view["group"], view["label"]), ("blocked", label))
            self.assertEqual(self.view(value, issue={**ISSUE, "state": "closed"})["group"], "done")
            self.assertEqual(len(view["workers"]), 1)

    def test_terminal_wins_later_running_and_rework_resolves(self):
        value = record(event("stage_started"), event("state_observed", 10, state="interrupted", source="runtime_event"),
                       event("state_observed", 20, state="running", source="runtime_query"))
        view = self.view(value)
        self.assertEqual((view["group"], view["label"]), ("blocked", "interrompida"))
        value["events"] += [event("stage_finished", 21), event("stage_started", 22, execution={"kind": "worker", "id": "b"}),
                            event("state_observed", 25, state="running", source="runtime_query", execution={"kind": "worker", "id": "b"})]
        self.assertEqual(self.view(value)["group"], "running")

    def test_callback_a_never_confirms_b_and_metrics_unchanged(self):
        value = record(event("stage_started"), event("stage_finished", 10),
                       event("stage_started", 11, execution={"kind": "worker", "id": "b"}),
                       event("state_observed", 9, state="completed", source="runtime_query"))
        raw = copy.deepcopy(value)
        before = json.dumps(summarize_run(value, NOW), sort_keys=True)
        summary, details = analyze(value, NOW)
        self.assertEqual(json.dumps(summary, sort_keys=True), before)
        self.assertEqual(value, raw)
        self.assertEqual(self.view(value)["workers"][-1]["state"], "unknown")
        self.assertEqual(details["intervals"][-1]["observations"], [])

    def test_report_and_reference_do_not_approve_and_stage_end_not_test_result(self):
        execution = {"kind": "test_run", "id": "test-a"}
        value = record(event("stage_started", execution=execution),
                       event("stage_finished", 20, execution=execution, evidence=["abcdef0"]))
        view = self.view(value)
        self.assertEqual(view["workers"][0]["state"], "closed")
        self.assertEqual(view["summary"]["incomplete_evidence"][0]["reason"], "missing_terminal")
        self.assertNotIn("approved", json.dumps(view))

    def test_legacy_wait_and_work_times_preserved(self):
        value = record(event("stage_started", execution=None), event("wait_started", 10, execution=None, reason="owner_input"))
        view = self.view(value)
        self.assertEqual(view["group"], "blocked")
        self.assertEqual(view["summary"], summarize_run(snapshots(value)[0]["record"], NOW))

    def test_snapshot_idempotency_last_seen_hash_identity_and_malformed(self):
        value = record(event("stage_started"), event("state_observed", 10, state="running", source="runtime_query"))
        one = snapshots(value)
        self.assertEqual(comments_snapshot([comment(value), comment(value)], REPO, 7), one)
        value["events"][-1]["last_seen_at"] = event("x", 20)["at"]
        self.assertNotEqual(snapshots(value)[0]["hash"], one[0]["hash"])
        for raw in ([1], {**value, "repository": "other/repo"}, {**value, "events": [None]}, {**value, "created_at": "bad"}):
            with self.assertRaises(MonitorError):
                record_of(comment(raw)["body"], REPO, 7)

    def test_run_tie_concurrency_and_conflicting_origins_are_visible(self):
        a, b = record(event("stage_started"), run_id="a"), record(event("stage_started"), run_id="b")
        records = comments_snapshot([comment(a, 1), comment(b, 2)], REPO, 7)
        view = issue_view(ISSUE, records, {}, {}, NOW, DEFAULTS, STARTED)
        self.assertEqual(view["run"], "b")
        self.assertIn("empate de criação de run", view["warnings"])
        self.assertIn("runs simultaneamente abertos", view["warnings"])
        b["events"].append(event("wait_started", 20, reason="tests"))
        records += snapshots(b, 3)
        view = issue_view(ISSUE, records, {}, {}, NOW, DEFAULTS, STARTED)
        self.assertIn("snapshots conflitantes do mesmo run", view["warnings"])
        self.assertNotEqual(view["group"], "running")

    def test_runtime_worker_only_absence_blocks_workflow_and_closed_is_separate(self):
        for kind, expected in [("worker", "running"), ("test_run", "pending"), ("job", "pending")]:
            value = record(event("stage_started", execution={"kind": kind, "id": "a"}))
            interval = analyze(value, NOW)[1]["intervals"][0]
            key = incarnation_key(REPO, 7, value["run_id"], interval)
            runtime = {key: {"state": "active", "at": NOW.isoformat()}}
            self.assertEqual(self.view(value, runtime=runtime, bindings={key: {"session_id": "ses_test"}})["group"], expected)
            value["events"].append(event("state_observed", 20, state="running", source="runtime_query", execution={"kind": kind, "id": "a"}))
            inactive = {key: {"state": "inactive", "at": NOW.isoformat()}}
            self.assertEqual(self.view(value, runtime=inactive, bindings={key: {"session_id": "ses_test"}})["group"], "pending" if kind == "worker" else "running")
