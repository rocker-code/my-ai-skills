"""Limites, retenção e minimização do domínio de fatos, sem fontes reais."""
from datetime import timedelta
import json
from pathlib import Path
import tempfile
import unittest

from milestone_monitor_fixtures import ROOT
from milestone_monitor.common import MonitorError, utc_now
from milestone_monitor.observations import MAX_BYTES, MAX_FACTS, normalize
from milestone_monitor.store import Store
from test_milestone_monitor_observer import CONTEXT


class ObservationStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        self.lease = self.store.acquire_collector("observe")
        self.addCleanup(self.lease.close)
        self.store.observation_gap(self.lease.epoch, "reinício do observador")

    def fact(self, event_id="evt_fixture"):
        now = utc_now()
        return {"version": 1, "type": "server.connected", "event_id": event_id,
                "created": int(now.timestamp() * 1000), "received_at": now.isoformat(), "context": CONTEXT,
                "secret": "SEGREDO_FIXTURE"}

    def test_second_projection_bounds_and_no_content_at_rest(self):
        raw = self.fact()
        raw["secret"] = "SEGREDO_FIXTURE"
        self.assertTrue(self.store.append_runtime_fact(raw, self.lease.epoch))
        saved = self.store.runtime_facts()[0]
        self.assertNotIn("secret", saved)
        self.assertEqual(saved["continuity"], self.store.local("observer:coverage")["continuity"])
        self.assertNotIn(b"SEGREDO_FIXTURE", self.store.path.read_bytes())
        with self.assertRaises(MonitorError):
            normalize(b"x" * (MAX_BYTES + 1), CONTEXT, {}, self.lease.epoch)
        with self.assertRaises(MonitorError):
            self.store.observer_health(self.lease.epoch, "degraded", "SEGREDO_FIXTURE")

    def seed(self, count, known=True, consumed=False, days=0):
        now = utc_now() - timedelta(days=days)
        with self.store.connect() as db:
            for index in range(count):
                value = {"version": 1 if known else 99, "event_id": f"evt_{index}",
                         "received_at": now.isoformat(), "consumed": consumed}
                db.execute("INSERT INTO local VALUES (?,?)", (f"runtime-event:evt_{index}", json.dumps(value)))

    def test_saturation_marks_gap_before_dropping_known_facts(self):
        self.seed(MAX_FACTS)
        coverage = self.store.local("observer:coverage")
        self.assertTrue(self.store.append_runtime_fact(self.fact(), self.lease.epoch))
        self.assertEqual(len(self.store.runtime_facts()), MAX_FACTS)
        current = self.store.local("observer:coverage")
        self.assertNotEqual(current["continuity"], coverage["continuity"])
        self.assertEqual(current["reason"], "saturação de fatos")
        self.assertFalse(current["complete"])

    def test_unknown_versions_and_canonical_operations_never_deleted(self):
        self.seed(MAX_FACTS, known=False)
        self.store.put_local("workflow-operation:fixture", {"version": 1, "state": "pending"})
        self.assertFalse(self.store.append_runtime_fact(self.fact(), self.lease.epoch))
        self.assertEqual(len(self.store.runtime_facts()), MAX_FACTS)
        self.assertTrue(all(value["version"] == 99 for value in self.store.runtime_facts()))
        self.assertEqual(self.store.local("workflow-operation:fixture")["state"], "pending")
        self.assertEqual(self.store.local("observer:coverage")["reason"], "saturação de fatos")

    def test_retention_only_consumed_older_than_seven_days_and_idempotent_fact(self):
        self.seed(3, consumed=True, days=8)
        self.store.put_local("runtime-event:unknown", {"version": 99})
        self.assertTrue(self.store.append_runtime_fact(self.fact(), self.lease.epoch))
        self.assertFalse(self.store.append_runtime_fact(self.fact(), self.lease.epoch))
        self.assertEqual(len(self.store.runtime_facts()), 2)
        self.store.consume_runtime_facts(["evt_fixture"])
        self.assertTrue(self.store.local("runtime-event:evt_fixture")["consumed"])

    def test_disk_full_rolls_back_fact_gap_and_health_without_renewing_source(self):
        self.store.observer_health(self.lease.epoch, "live")
        before = self.store.local("observer:health")
        coverage = self.store.local("observer:coverage")
        with self.store.connect() as db:
            db.execute("CREATE TRIGGER full_insert BEFORE INSERT ON local BEGIN SELECT RAISE(ABORT,'disk full'); END")
            db.execute("CREATE TRIGGER full_update BEFORE UPDATE ON local BEGIN SELECT RAISE(ABORT,'disk full'); END")
        for operation in (lambda: self.store.append_runtime_fact(self.fact(), self.lease.epoch),
                          lambda: self.store.observer_health(self.lease.epoch, "degraded"),
                          lambda: self.store.observation_gap(self.lease.epoch, "fluxo interrompido"),
                          lambda: self.lease.heartbeat()):
            with self.assertRaises(MonitorError):
                operation()
        self.assertEqual(self.store.runtime_facts(), [])
        self.assertEqual(self.store.local("observer:health"), before)
        self.assertEqual(self.store.local("observer:coverage"), coverage)
