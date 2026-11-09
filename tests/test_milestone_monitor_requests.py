"""Pedidos são individuais; ausência em consulta não é horário de resolução."""
from datetime import datetime, timedelta, timezone
import json
import unittest

from milestone_monitor_fixtures import ROOT
from milestone_monitor.requests import event, snapshot


BASE = datetime(2026, 11, 8, tzinfo=timezone.utc)
EPOCH = "epoch-fixture"
COVERAGE = {"collector_epoch": EPOCH, "continuity": "coverage-A", "complete": True,
            "reconciled_at": BASE.isoformat()}


def fact(kind, request_id, seconds):
    return {"type": kind, "request_id": request_id, "binding_revision": "revision-A",
            "created": int((BASE + timedelta(seconds=seconds)).timestamp() * 1000),
            "continuity": "coverage-A", "received_at": (BASE + timedelta(seconds=seconds + 1)).isoformat()}


def sample(requests, seconds):
    return {"binding_revision": "revision-A", "requests": requests,
            "query_started_at": (BASE + timedelta(seconds=seconds)).isoformat(),
            "at": (BASE + timedelta(seconds=seconds + 1)).isoformat(), "state": "inactive"}


class RequestTests(unittest.TestCase):
    def test_multiple_permissions_forms_and_individual_resolution(self):
        state = None
        for kind, request in (("permission.asked", "per_A"), ("permission.asked", "per_B"), ("form.created", "frm_C")):
            state = event(state, fact(kind, request, 2), EPOCH, COVERAGE)
        state = event(state, {**fact("permission.replied", "per_A", 5), "resolution": "rejected"}, EPOCH, COVERAGE)
        self.assertFalse(state["requests"]["per_A"]["pending"])
        self.assertEqual(state["requests"]["per_A"]["status"], "rejected")
        self.assertTrue(state["requests"]["per_A"]["complete"])
        self.assertTrue(state["requests"]["per_B"]["pending"])
        state = event(state, fact("form.cancelled", "frm_C", 6), EPOCH, COVERAGE)
        self.assertEqual(state["requests"]["frm_C"]["status"], "cancelled")
        self.assertTrue(state["requests"]["per_B"]["pending"])

    def test_inactive_without_request_never_invents_wait(self):
        state = snapshot(None, sample([], 2), EPOCH, COVERAGE)
        self.assertEqual(state["requests"], {})

    def test_query_recovers_current_state_not_missing_timestamps(self):
        state = snapshot(None, sample([{"kind": "form", "request_id": "frm_A"}], 2), EPOCH, COVERAGE)
        self.assertTrue(state["requests"]["frm_A"]["pending"])
        self.assertIsNone(state["requests"]["frm_A"]["opened_at"])
        state = snapshot(state, sample([], 5), EPOCH, COVERAGE)
        request = state["requests"]["frm_A"]
        self.assertFalse(request["pending"])
        self.assertIsNone(request["resolved_at"])
        self.assertFalse(request["complete"])

    def test_loss_reconnection_restart_preserve_incomplete_intervals(self):
        for epoch in (EPOCH, "epoch-restarted"):
            with self.subTest(epoch=epoch):
                state = event(None, fact("permission.asked", "per_A", 2), EPOCH, COVERAGE)
                coverage = {**COVERAGE, "collector_epoch": epoch, "continuity": "coverage-B", "complete": False}
                state = snapshot(state, sample([], 5), epoch, coverage)
                self.assertFalse(state["requests"]["per_A"]["pending"])
                self.assertIsNone(state["requests"]["per_A"]["resolved_at"])
                state = event(state, {**fact("permission.replied", "per_A", 6), "continuity": "coverage-B"}, epoch,
                              {**coverage, "complete": True, "reconciled_at": (BASE + timedelta(seconds=5)).isoformat()})
                self.assertFalse(state["requests"]["per_A"]["complete"])

    def test_delayed_reply_can_repair_only_same_continuous_native_interval(self):
        state = event(None, fact("form.created", "frm_A", 2), EPOCH, COVERAGE)
        state = snapshot(state, sample([], 6), EPOCH, COVERAGE)
        self.assertFalse(state["requests"]["frm_A"]["complete"])
        state = event(state, fact("form.replied", "frm_A", 5), EPOCH, COVERAGE)
        self.assertTrue(state["requests"]["frm_A"]["complete"])
        self.assertEqual(state["requests"]["frm_A"]["resolved_at"], (BASE + timedelta(seconds=5)).isoformat())

    def test_delayed_opening_does_not_reopen_resolved_request(self):
        state = event(None, fact("form.replied", "frm_A", 5), EPOCH, COVERAGE)
        state = event(state, fact("form.created", "frm_A", 2), EPOCH, COVERAGE)
        self.assertFalse(state["requests"]["frm_A"]["pending"])
        self.assertTrue(state["requests"]["frm_A"]["complete"])

    def test_snapshot_started_before_native_resolution_does_not_resurrect(self):
        state = event(None, fact("form.created", "frm_A", 2), EPOCH, COVERAGE)
        state = event(state, fact("form.replied", "frm_A", 5), EPOCH, COVERAGE)
        state = snapshot(state, sample([{"kind": "form", "request_id": "frm_A"}], 4), EPOCH, COVERAGE)
        self.assertFalse(state["requests"]["frm_A"]["pending"])

    def test_no_text_or_human_answer_in_state(self):
        state = event(None, {**fact("form.created", "frm_A", 2), "title": "SEGREDO_FIXTURE"}, EPOCH, COVERAGE)
        state = event(state, {**fact("form.replied", "frm_A", 3), "answer": "SEGREDO_FIXTURE"}, EPOCH, COVERAGE)
        self.assertNotIn("SEGREDO_FIXTURE", json.dumps(state))
