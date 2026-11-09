"""Bind posterior à publicação, sessão tardia e troca exata, com APIs fake."""
import copy
import json
import tempfile
import unittest
from unittest.mock import patch

from milestone_monitor_fixtures import ROOT, CONFIG, inventory
from milestone_monitor.common import MonitorError
from milestone_monitor.coordinator import Coordinator
from milestone_monitor.journal import Journal
from milestone_monitor.publisher import Publisher
from milestone_monitor.runtime import Runtime
from milestone_monitor.store import Store
from test_milestone_monitor_journal import operation
from test_milestone_monitor_publisher import FakeGitHub


class AutoBindTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        self.github = FakeGitHub(self.store)
        self.config = {**CONFIG, "runtime": {**CONFIG["runtime"], "enabled": True}}
        self.fixture = json.loads((ROOT / "tests/fixtures/milestone-monitor-opencode-2.2.5.json").read_text())
        self.calls = []
        def call(argv, timeout):
            self.calls.append(argv)
            return "2.2.5" if argv == ["opencode", "--version"] else copy.deepcopy(self.fixture[argv[argv.index("api") + 1]])
        self.runtime = Runtime(self.config["runtime"], call)
        publisher = Publisher(Journal(self.store), self.github.read, self.github.save)
        class Inventory:
            def inventory(self, *_args):
                return inventory()
        self.coordinator = Coordinator(self.store, self.config, publisher, self.runtime, Inventory())
        self.git = patch("milestone_monitor.runtime.git_identity", return_value="feature")
        self.git.start()
        self.addCleanup(self.git.stop)
        self.coordinator.transition(operation())

    def opening(self, session="ses_fixture", operation_id="op-open", **extra):
        binding = {"worktree": "/fixture/worktree", "branch": "feature"}
        if session is not None:
            binding["session_id"] = session
        return operation(operation_id, event="dispatch", stage="apply", worker_id="worker-A",
                         execution={"kind": "worker", "id": "execution-A"}, at="2026-11-08T00:01:00Z",
                         depends_on=["op-start"], binding=binding, **extra)

    def test_missing_session_never_uses_coordinator_then_late_id_binds_without_opening_again(self):
        payload = self.opening(None)
        value = self.coordinator.transition(payload)
        self.assertEqual((value["publication"], value["binding"], value["binding_reason"]), ("published", "pending", "session_unavailable"))
        self.assertEqual(self.calls, [])
        intent = {"version": 1, "operation_id": "op-open", "session_id": "ses_fixture"}
        value = self.coordinator.reconcile(payload["issue"], payload["run_id"], True, intent)
        self.assertEqual(value["remaining"], 0)
        key, binding = next(iter(self.store.bindings().items()))
        self.assertEqual(binding["session_id"], "ses_fixture")
        revision = binding["revision"]
        self.coordinator.reconcile(payload["issue"], payload["run_id"], True, intent)
        self.assertEqual(self.store.bindings()[key]["revision"], revision)
        self.assertEqual(self.github.writes, 2)
        with self.assertRaises(MonitorError):
            self.coordinator.reconcile(payload["issue"], payload["run_id"], True, {**intent, "session_id": "ses_other"})

    def test_lost_publication_response_does_not_bind_until_publication_confirmed(self):
        self.github.lose_response = True
        payload = self.opening()
        first = self.coordinator.transition(payload)
        self.assertEqual(first["publication"], "pending")
        self.assertEqual(self.store.bindings(), {})
        self.assertEqual(self.calls, [])
        second = self.coordinator.transition(payload)
        self.assertEqual((second["publication"], second["binding"]), ("published", "bound"))
        self.assertEqual(self.github.writes, 2)

    def test_bind_failure_preserves_published_opening_and_retry_only_repairs_binding(self):
        payload = self.opening()
        with patch("milestone_monitor.runtime.git_identity", side_effect=MonitorError("branch incompatível")):
            first = self.coordinator.transition(payload)
        self.assertEqual((first["publication"], first["binding"]), ("published", "failed"))
        self.assertEqual(self.github.writes, 2)
        self.assertEqual(self.coordinator.transition(payload)["binding"], "bound")
        self.assertEqual(self.github.writes, 2)

    def test_execution_switch_requires_exact_previous_unbind(self):
        first = self.opening()
        self.assertEqual(self.coordinator.transition(first)["binding"], "bound")
        key = next(iter(self.store.bindings()))
        end = {**first, "operation_id": "op-end", "event": "stage-end", "status": "completed", "at": "2026-11-08T00:02:00Z", "depends_on": ["op-open"]}
        del end["binding"]
        self.coordinator.transition(end)
        second = {**first, "operation_id": "op-next", "execution": {"kind": "worker", "id": "execution-B"},
                  "at": "2026-11-08T00:03:00Z", "depends_on": ["op-end"]}
        self.assertEqual(self.coordinator.transition(second)["binding"], "failed")
        self.assertIn(key, self.store.bindings())
        self.store.unbind(key)
        self.assertEqual(self.coordinator.transition(second)["binding"], "bound")
        self.assertNotIn(key, self.store.bindings())

    def test_runtime_disabled_and_wrong_binding_scope_are_explicit(self):
        self.coordinator.config = {**self.config, "runtime": {**self.config["runtime"], "enabled": False}}
        value = self.coordinator.transition(self.opening())
        self.assertEqual(value["publication"], "published")
        self.assertEqual(value["binding_reason"], "runtime_disabled")
        with self.assertRaisesRegex(MonitorError, "escopo"):
            self.coordinator.reconcile("https://github.com/owner/repo/issues/8", "wf-fixture", True,
                                       {"version": 1, "operation_id": "op-open", "session_id": "ses_fixture"})
