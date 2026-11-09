"""Esperas v1 atômicas e gates conservadores com GitHub/runtime fake."""
import copy
import json
import unittest

from milestone_monitor_fixtures import ROOT
from milestone_monitor.common import MonitorError
from workflow_metrics import summarize_run
from workflow_waits import pairs
from test_milestone_monitor_journal import operation
import test_milestone_monitor_auto_bind as auto


class ReconciliationTests(unittest.TestCase):
    setUp = auto.AutoBindTests.setUp
    opening = auto.AutoBindTests.opening

    def seed_requests(self, requests, signal=None):
        payload = self.opening()
        if not self.store.bindings():
            self.coordinator.transition(payload)
        key, binding = next(iter(self.store.bindings().items()))
        state = {"version": 1, "binding_key": key, "binding_revision": binding["revision"], "collector_epoch": "fixture-epoch",
                 "identity": {field: binding[field] for field in ("repository", "issue", "run_id", "stage", "worker_id", "execution")},
                 "requests": requests}
        self.store.put_local(self.store.observation_key(key, "requests"), state)
        if signal:
            self.store.put_local(self.store.observation_key(key), {"version": 1, "type": signal})
        return payload, state

    def request(self, name, start, end, complete=True, pending=False):
        return {"request_id": name, "kind": "permission" if name.startswith("per") else "form", "pending": pending,
                "opened_at": "2026-11-08T" + start + "Z" if start else None,
                "resolved_at": "2026-11-08T" + end + "Z" if end else None, "complete": complete}

    def reconcile(self):
        return self.coordinator.reconcile(operation()["issue"], "wf-fixture", authorized=True)

    def record(self):
        from workflow_metrics import parse_run_comment
        return parse_run_comment(self.github.comments[0]["body"])

    def test_overlapping_requests_union_native_precision_and_repeat_without_duplicate_time(self):
        self.seed_requests({"per_A": self.request("per_A", "00:02:00.125", "00:05:00.250"),
                            "frm_B": self.request("frm_B", "00:04:00.100", "00:08:00.375")})
        value = self.reconcile()
        self.assertEqual(value["runtime"]["wait_intervals"], 1)
        self.assertEqual(summarize_run(self.record())["wait_seconds_by_reason"], {"owner_input": 360.25})
        waits = [event for event in self.record()["events"] if event["type"].startswith("wait_")]
        self.assertEqual(len(waits), 2)
        self.assertEqual(waits[0]["at"], "2026-11-08T00:02:00.125000Z")
        self.assertNotEqual(waits[0]["operation"]["id"], waits[1]["operation"]["id"])
        writes = self.github.writes
        self.reconcile()
        self.assertEqual(self.github.writes, writes)

    def test_lost_response_recovers_whole_atomic_pair(self):
        self.seed_requests({"per_A": self.request("per_A", "00:02:00", "00:05:00")})
        self.github.lose_response = True
        first = self.reconcile()
        self.assertGreater(first["remaining"], 0)
        self.assertEqual(len([e for e in self.record()["events"] if e["type"].startswith("wait_")]), 2)
        second = self.reconcile()
        self.assertEqual(second["remaining"], 0)
        self.assertEqual(self.github.writes, 3)
        self.assertEqual(summarize_run(self.record())["wait_seconds_by_reason"], {"owner_input": 180})

    def explicit_wait(self, command, at, op_id):
        payload = self.opening()
        del payload["binding"]
        payload.update(event=command, operation_id=op_id, reason="owner_input", at="2026-11-08T" + at + "Z", depends_on=["op-open"])
        return self.coordinator.transition(payload)

    def test_subtracts_canonical_wait_and_inserts_backdated_gaps_without_repairing_fifo(self):
        self.seed_requests({"per_A": self.request("per_A", "00:02:00", "00:05:00")})
        self.explicit_wait("wait-start", "00:03:00", "explicit-start")
        self.explicit_wait("wait-end", "00:04:00", "explicit-end")
        before = pairs(self.record())
        value = self.reconcile()
        self.assertEqual(value["runtime"]["wait_intervals"], 2)
        after = pairs(self.record())
        self.assertTrue(all(after[key] == end for key, end in before.items()))
        self.assertEqual(summarize_run(self.record())["wait_seconds_by_reason"], {"owner_input": 180})

    def test_open_explicit_or_overlapping_pending_request_is_not_closed_by_first_reply(self):
        self.seed_requests({"per_A": self.request("per_A", "00:02:00", "00:05:00"),
                            "frm_B": self.request("frm_B", "00:04:00", None, complete=False, pending=True)})
        writes = self.github.writes
        self.assertGreater(self.reconcile()["runtime"]["deferred"], 0)
        self.assertEqual(self.github.writes, writes)
        self.seed_requests({"per_A": self.request("per_A", "00:02:00", "00:05:00")})
        self.explicit_wait("wait-start", "00:03:00", "explicit-start")
        self.assertGreater(self.reconcile()["runtime"]["deferred"], 0)
        self.assertFalse(any(e["type"] == "wait_finished" for e in self.record()["events"]))

    def test_missing_resolution_and_turn_success_never_create_duration_or_stage_end(self):
        self.seed_requests({"per_A": self.request("per_A", "00:02:00", None, complete=False)}, "session.execution.succeeded")
        value = self.reconcile()
        self.assertEqual(value["runtime"]["unmeasured"], 1)
        self.assertEqual(value["runtime"]["results_unverified"], 1)
        self.assertFalse(any(e["type"] in {"stage_finished", "state_observed", "wait_finished"} for e in self.record()["events"]))

    def test_terminal_worker_or_test_observation_requires_own_proof_but_manual_v1_is_unchanged(self):
        payload, _state = self.seed_requests({})
        del payload["binding"]
        payload.update(operation_id="worker-return", event="observe", at="2026-11-08T00:09:00Z", state="completed", source="runtime_event")
        with self.assertRaises(MonitorError):
            self.coordinator.transition(payload)
        payload.update(evidence=["abcdef0"], log_ref="worker-result:execution-A")
        self.assertEqual(self.coordinator.transition(payload)["publication"], "published")
        self.assertFalse(any(e["type"] == "stage_finished" for e in self.record()["events"]))
        self.assertGreater(self.reconcile()["runtime"]["transitions_pending"], 0)
        test_payload = operation("test-open", event="dispatch", stage="tests", worker_id="test-worker", at="2026-11-08T00:10:00Z",
                                 execution={"kind": "test_run", "id": "ev-20261104T030000Z-1a2b3c4d"})
        self.coordinator.transition(test_payload)
        result = {**test_payload, "operation_id": "test-return", "event": "observe", "at": "2026-11-08T00:11:00Z", "state": "completed",
                  "source": "runtime_event", "report": "present", "evidence": ["evidence:ev-20261104T030000Z-1a2b3c4d"]}
        with self.assertRaises(MonitorError):
            self.coordinator.transition(result)
        result["source"] = "test_report"
        self.assertEqual(self.coordinator.transition(result)["publication"], "published")
