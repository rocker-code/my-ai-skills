"""Frescor independente, espera local e registro canônico sem dupla contagem."""
import copy
import tempfile
import unittest

from milestone_monitor_fixtures import *
from milestone_monitor.common import MonitorError
from milestone_monitor.projection import model
from milestone_monitor.store import Store
from milestone_monitor.tui import detail_lines, expire_samples
from test_milestone_monitor_observer import CONTEXT


class ObserverProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        seed(self.store)
        self.config = {**CONFIG, "runtime": {**CONFIG["runtime"], "enabled": True}}
        self.key = model(self.store, CONFIG, STARTED, NOW)["milestones"][0]["issues"][0]["workers"][0]["key"]
        self.store.bind(self.key, {"session_id": "ses_fixture", "context": CONTEXT, "worktree": "/fixture/worktree"})
        self.binding = self.store.bindings()[self.key]
        self.lease = self.store.acquire_collector("observe", now=NOW.isoformat())
        self.addCleanup(self.lease.close)
        self.store.observer_health(self.lease.epoch, "live", now=NOW.isoformat())

    def sample(self, **extra):
        item = {"state": "active", "at": NOW.isoformat(), "binding_revision": self.binding["revision"],
                "collector_epoch": self.lease.epoch, "context": CONTEXT, "requests": [],
                "query_started_at": (NOW - timedelta(seconds=1)).isoformat(), **extra}
        generation = self.store.begin("runtime", epoch=self.lease.epoch)
        self.store.publish("runtime", generation, {self.key: item}, now=NOW.isoformat(), epoch=self.lease.epoch)

    def value(self, now=None):
        return model(self.store, self.config, NOW + timedelta(seconds=1), now or NOW + timedelta(seconds=2))

    def issue(self, now=None):
        return self.value(now)["milestones"][0]["issues"][0]

    def test_sample_before_ui_open_requires_current_live_healthy_owner(self):
        self.sample()
        self.assertEqual(self.issue()["group"], "running")
        self.assertTrue(self.issue()["workers"][0]["independent"])
        self.lease.close()
        self.assertEqual(self.issue()["group"], "pending")

    def test_old_epoch_ttl_and_heartbeat_without_new_sample_do_not_confirm(self):
        self.sample(collector_epoch="old-epoch")
        self.assertEqual(self.issue()["group"], "pending")
        self.sample()
        future = NOW + timedelta(seconds=60)
        self.lease.heartbeat(future.isoformat())
        self.store.observer_health(self.lease.epoch, "live", now=future.isoformat())
        self.assertEqual(self.issue(future)["group"], "pending")
        self.sample()
        generation = self.store.source("runtime")["generation"]
        self.store.fail("runtime", generation, MonitorError("timeout"), future.isoformat(), epoch=self.lease.epoch)
        self.assertEqual(self.issue()["group"], "pending")

    def test_observed_pending_blocks_once_without_canonical_duration(self):
        self.sample(requests=[{"kind": "permission", "request_id": "per_fixture"}])
        value = self.value()
        issue = value["milestones"][0]["issues"][0]
        self.assertEqual(issue["group"], "blocked")
        self.assertTrue(issue["local_block"])
        self.assertEqual(sum(value["milestones"][0]["totals"].values()), 1)
        self.assertEqual(issue["summary"]["wait_seconds_by_reason"], {})
        details = "\n".join(detail_lines(issue))
        self.assertIn("aguardando autorização (observada)", details)
        self.assertIn("sem duração canônica inferida", details)
        expired = expire_samples(value, DEFAULTS, NOW + timedelta(seconds=60))
        self.assertEqual(expired["milestones"][0]["issues"][0]["group"], "pending")
        self.assertEqual(sum(expired["milestones"][0]["totals"].values()), 1)

    def test_canonical_wait_and_github_closure_have_precedence(self):
        value = record(event("stage_started"), event("wait_started", 10, reason="owner_input"))
        generation = self.store.begin(f"comments:{REPO}:7", epoch=self.lease.epoch)
        self.store.publish(f"comments:{REPO}:7", generation, snapshots(value), epoch=self.lease.epoch)
        self.sample()
        self.assertEqual(self.issue()["group"], "blocked")
        self.assertEqual(self.issue()["label"], "aguardando decisão")
        self.assertFalse(self.issue()["local_block"])
        self.assertEqual(self.issue()["workers"][0]["state"], "running")
        generation = self.store.begin("inventory:" + REPO, epoch=self.lease.epoch)
        self.store.publish("inventory:" + REPO, generation, inventory([{**ISSUE, "state": "closed"}]), epoch=self.lease.epoch)
        self.assertEqual(self.issue()["group"], "done")

    def test_pending_publication_is_not_a_github_stage(self):
        self.sample()
        self.store.put_local("workflow-operation:fixture", {"version": 1, "operation_id": "op-fixture", "repository": REPO,
                             "issue": 7, "run_id": "wf-test", "state": "pending"})
        issue = self.issue()
        self.assertEqual(issue["group"], "running")
        self.assertEqual(len(issue["publication_pending"]), 1)
        self.assertEqual(list(issue["stages"]), ["apply"])
        self.assertIn("intenção local, não etapa publicada", "\n".join(detail_lines(issue)))
