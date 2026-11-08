"""M8: contrato consumidor do release fixado; não é integração real OpenCode."""
import argparse
import copy
import json
import tempfile
import unittest
from unittest.mock import patch

from milestone_monitor_fixtures import *
from milestone_monitor.common import MonitorError
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
