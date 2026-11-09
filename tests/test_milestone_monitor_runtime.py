"""M8: contrato consumidor do release fixado; não é integração real OpenCode."""
import argparse
import copy
import json
import tempfile
import unittest
from unittest.mock import patch

from milestone_monitor_fixtures import *
from milestone_monitor.common import MonitorError, utc_now
from milestone_monitor.runtime import Runtime, bind
from milestone_monitor.projection import analyze, incarnation_key
from milestone_monitor.store import Store


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT / "tests/fixtures/milestone-monitor-opencode-2.2.5.json").read_text())
        self.calls = []
        self.runtime = Runtime({"enabled": True, "expected_version": "2.2.5", "server": None}, self.call)
        self.key = "binding:fixture"
        self.binding = {"session_id": "ses_fixture", "worktree": "/fixture/worktree", "repository": REPO,
                        "branch": "feature", "context": self.runtime.context(), "revision": "revision-fixture"}
        self.git = patch("milestone_monitor.runtime.git_identity", return_value="feature")
        self.git.start()
        self.addCleanup(self.git.stop)

    def call(self, argv, timeout):
        self.calls.append(argv)
        if argv == ["opencode", "--version"]:
            return "2.2.5"
        operation = argv[argv.index("api")+1]
        value = self.fixture[operation]
        if isinstance(value, Exception):
            raise value
        return copy.deepcopy(value)

    def collect(self):
        return self.runtime.collect({self.key: self.binding}, {self.key})[self.key]

    def test_official_envelopes_subpath_not_concatenated_and_allowlist(self):
        self.fixture["session.active"]["data"]["ses_private"] = {"type": "running"}
        self.fixture["session.get"]["data"]["prompt"] = "PRIVATE_SECRET"
        self.fixture["server.info"]["token"] = "PRIVATE_SECRET"
        result = self.collect()
        self.assertEqual(result["state"], "active")
        self.assertEqual(result["binding_revision"], self.binding["revision"])
        self.assertNotIn("PRIVATE", json.dumps(result))
        self.assertNotIn("ses_private", json.dumps(result))
        self.assertTrue(all("--standalone" not in argv for argv in self.calls))
        self.assertIn(["opencode", "api", "location.get", "--param", "location[directory]=/fixture/worktree"], self.calls)

    def test_location_is_revalidated_every_cycle_even_same_project_and_running(self):
        self.assertEqual(self.collect()["state"], "active")
        self.fixture["session.get"]["data"]["location"]["directory"] = "/fixture/main"
        self.assertEqual(self.collect()["state"], "incompatible")
        self.assertEqual(sum("session.get" in args for args in self.calls), 2)

    def test_inactive_absent_unauthorized_timeout_and_invalid(self):
        self.fixture["session.active"]["data"] = {}
        self.assertEqual(self.collect()["state"], "inactive")
        self.fixture["session.get"] = MonitorError("ausente")
        self.assertEqual(self.collect()["state"], "absent")
        for category in ("não autorizado", "timeout", "resposta inválida", "fonte ausente"):
            self.fixture["session.get"] = MonitorError(category)
            with self.assertRaisesRegex(MonitorError, category):
                self.collect()

    def test_process_and_version_changes_do_not_transfer_confirmation(self):
        self.fixture["server.info"]["pid"] += 1
        self.assertEqual(self.collect()["state"], "context_changed")
        self.fixture["server.info"]["version"] = "2.3.0"
        with self.assertRaisesRegex(MonitorError, "incompatível"):
            self.collect()

    def test_explicit_server_applies_to_every_operation_and_terminal_not_polled(self):
        self.runtime.config["server"] = "http://localhost:4096"
        self.binding["context"] = self.runtime.context()
        self.assertEqual(self.collect()["state"], "active")
        for args in self.calls[1:]:
            if "--server" in args:
                self.assertEqual(args[:3], ["opencode", "--server", "http://localhost:4096"])
        self.assertEqual(self.runtime.collect({self.key: self.binding}, set()), {})

    def test_no_targets_or_open_binding_never_queries_runtime(self):
        before = len(self.calls)
        self.assertEqual(self.runtime.collect({self.key: self.binding}, set()), {})
        self.assertEqual(len(self.calls), before)
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            seed(store)
            from milestone_monitor.collector import Collector
            collector = Collector(store, {**CONFIG, "targets": []})
            self.assertEqual(collector.open_keys(), set())

    def test_bind_validation_rejection_preserves_prior_and_terminal_reuse_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            seed(store)
            args = argparse.Namespace(issue=ISSUE["url"], run_id="wf-test", stage="apply", worker_id="a",
                                      execution_kind="worker", execution_id="worker-a", session_id="ses_fixture",
                                      worktree="/fixture/worktree", branch="feature")
            key = bind(store, self.runtime, args)
            before = store.bindings()
            self.assertIn(key, before)
            args.worktree = "/fixture/other"
            with self.assertRaisesRegex(MonitorError, "localização"):
                bind(store, self.runtime, args)
            self.assertEqual(store.bindings(), before)
            args.worktree = "/fixture/worktree"
            value = record(event("stage_started"), event("state_observed", 10, state="completed", source="runtime_event"))
            publish(store, f"comments:{REPO}:7", snapshots(value))
            with self.assertRaisesRegex(MonitorError, "terminal"):
                bind(store, self.runtime, args)
            self.assertEqual(store.bindings(), before)

    def test_pending_queries_minimize_content_and_are_scoped_to_session(self):
        self.fixture["session.permission.list"] = {"data": [{"id": "per_fixture", "sessionID": "ses_fixture",
                "message": "PRIVATE_SECRET", "resources": ["PRIVATE_SECRET"]}]}
        self.fixture["session.form.list"] = {"data": [{"id": "frm_fixture", "sessionID": "ses_fixture",
                "title": "PRIVATE_SECRET", "fields": [{"default": "PRIVATE_SECRET"}]}]}
        sample = self.collect()
        self.assertEqual(sample["requests"], [{"kind": "permission", "request_id": "per_fixture"},
                                             {"kind": "form", "request_id": "frm_fixture"}])
        self.assertNotIn("PRIVATE_SECRET", json.dumps(sample))
        self.fixture["session.form.list"]["data"][0]["sessionID"] = "ses_other"
        with self.assertRaises(MonitorError):
            self.collect()

    def test_fact_revalidates_revision_context_checkout_and_temporal_boundary(self):
        from datetime import timedelta
        now = utc_now()
        self.binding["bound_at"] = (now - timedelta(seconds=1)).isoformat()
        fact = {"version": 1, "type": "permission.asked", "event_id": "evt_fixture", "context": self.binding["context"],
                "created": int(now.timestamp() * 1000), "received_at": now.isoformat(), "binding_key": self.key,
                "binding_revision": self.binding["revision"], "session_id": "ses_fixture", "request_id": "per_fixture",
                "collector_epoch": "epoch-fixture", "secret": "PRIVATE_SECRET"}
        def validate(value=fact):
            return self.runtime.validate_fact(value, {self.key: self.binding}, {self.key})
        self.assertNotIn("PRIVATE_SECRET", json.dumps(validate()))
        self.assertIsNone(validate({**fact, "created": fact["created"] - 2000}))
        self.binding["revision"] = "revision-B"
        self.assertIsNone(validate())
        self.binding["revision"] = fact["binding_revision"]
        self.fixture["server.info"]["pid"] += 1
        with self.assertRaisesRegex(MonitorError, "contexto"):
            validate()
        self.fixture["server.info"]["pid"] -= 1
        self.fixture["session.get"]["data"]["location"]["directory"] = "/fixture/moved"
        with self.assertRaisesRegex(MonitorError, "localização"):
            validate()

    def test_fact_consumption_requires_new_query_and_never_closes_workflow(self):
        from datetime import timedelta
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            self.binding["bound_at"] = (utc_now() - timedelta(seconds=5)).isoformat()
            store.bind(self.key, self.binding)
            self.binding = store.bindings()[self.key]
            with store.acquire_collector("observe") as lease:
                store.observation_gap(lease.epoch, "reinício do observador")
                now = utc_now()
                fact = {"version": 1, "type": "session.execution.failed", "event_id": "evt_failed",
                    "context": self.binding["context"], "created": int(now.timestamp() * 1000), "received_at": now.isoformat(),
                    "binding_revision": self.binding["revision"], "session_id": "ses_fixture", "sequence": 2}
                store.append_runtime_fact(fact, lease.epoch)
                self.runtime.project_facts(store, {self.key}, lease.epoch)
                self.assertIsNone(store.local(store.observation_key(self.key)))
                sample = {**self.collect(), "collector_epoch": lease.epoch}
                generation = store.begin("runtime", epoch=lease.epoch)
                store.publish("runtime", generation, {self.key: sample}, epoch=lease.epoch)
                self.runtime.project_facts(store, {self.key}, lease.epoch)
                self.assertEqual(store.local(store.observation_key(self.key))["type"], "session.execution.failed")
                self.assertEqual(store.source("runtime")["payload"][self.key]["state"], "active")
                self.assertTrue(store.runtime_facts()[0]["projected"])
                self.assertFalse(store.runtime_facts()[0]["consumed"])
                self.assertEqual(store.sources("comments:"), [])
