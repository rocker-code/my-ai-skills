"""M5/M6/M9: limites SQLite reais, rollback e escritores em processos distintos."""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from milestone_monitor_fixtures import *
from milestone_monitor.store import Store, ClosingConnection
from milestone_monitor.common import MonitorError
from milestone_monitor.projection import model


class StoreTests(unittest.TestCase):
    def test_rebind_rejects_cached_and_inflight_runtime_of_previous_revision(self):
        seed(self.store)
        key = model(self.store, CONFIG, STARTED, NOW)["milestones"][0]["issues"][0]["workers"][0]["key"]
        config = {**CONFIG, "runtime": {**CONFIG["runtime"], "enabled": True}}
        def group():
            return model(self.store, config, STARTED, NOW)["milestones"][0]["issues"][0]["group"]
        self.store.bind(key, {"session_id": "ses_A", "context": {}})
        first = self.store.bindings()[key]
        observation = {"state": "active", "at": NOW.isoformat(), "binding_revision": first.get("revision")}
        publish(self.store, "runtime", {key: observation})
        self.assertEqual(group(), "running")
        generation = self.store.begin("runtime")
        self.store.bind(key, {"session_id": "ses_B", "context": {}})
        second = self.store.bindings()[key]
        self.assertEqual(group(), "pending", "B has not been queried; A's cached confirmation is not B's")
        self.assertNotEqual(first["revision"], second["revision"])
        # A response already in flight must neither confirm nor invalidate B.
        for state in ("active", "incompatible", "context_changed"):
            with self.subTest(state=state):
                self.store.publish("runtime", generation, {key: {**observation, "state": state}})
                self.assertEqual(group(), "pending")
                self.assertNotIn(key, self.store.source("runtime")["payload"])
                self.assertNotIn("invalidated", Store(self.directory).bindings()[key])
        publish(self.store, "runtime", {key: {**observation, "state": "inactive", "binding_revision": second["revision"]}})
        self.assertEqual(group(), "pending")
        # Unbind/rebind to identical metadata must not reuse a revision (ABA).
        self.store.unbind(key)
        self.store.bind(key, {"session_id": "ses_B", "context": {}})
        self.assertNotEqual(second["revision"], self.store.bindings()[key]["revision"])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "state"
        self.store = Store(self.directory)

    def test_restart_permissions_and_older_generation_cannot_publish(self):
        self.assertEqual(self.directory.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.store.path.stat().st_mode & 0o777, 0o600)
        old = self.store.begin("inventory")
        new = self.store.begin("inventory")
        self.assertTrue(self.store.publish("inventory", new, {"ok": 2}))
        self.assertFalse(self.store.publish("inventory", old, {"ok": 1}))
        self.assertEqual(Store(self.directory).source("inventory")["payload"], {"ok": 2})

    def test_failure_retains_payload_and_last_success(self):
        publish(self.store, "a", {"valid": True})
        before = self.store.source("a")
        generation = self.store.begin("a")
        self.store.fail("a", generation, MonitorError("timeout"), NOW.isoformat())
        after = Store(self.directory).source("a")
        self.assertEqual(after["payload"], before["payload"])
        self.assertEqual(after["fetched_at"], before["fetched_at"])
        self.assertEqual(after["error"], "timeout")

    def test_future_schema_is_refused_without_downgrade(self):
        with self.store.connect() as db:
            db.execute("PRAGMA user_version=9")
        with self.assertRaisesRegex(MonitorError, "schema futuro"):
            Store(self.directory)
        with self.store.connect() as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 9)

    def test_valid_snapshot_remains_readable_with_readonly_connection(self):
        publish(self.store, "a", "stable")
        class ReadOnly(Store):
            def connect(self):
                db = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True, factory=ClosingConnection)
                db.row_factory = sqlite3.Row
                return db
        reader = ReadOnly(self.directory)
        self.assertEqual(reader.source("a")["payload"], "stable")
        with self.assertRaises(MonitorError): reader.begin("a")

    def test_two_writers_killed_transaction_and_busy_reader(self):
        publish(self.store, "a", "stable")
        script = """import sqlite3,sys,os
db=sqlite3.connect(sys.argv[1]); db.execute('BEGIN IMMEDIATE')
db.execute("UPDATE sources SET payload='null' WHERE key='a'")
os._exit(0)
"""
        subprocess.run([sys.executable, "-c", script, str(self.store.path)], check=True)
        self.assertEqual(self.store.source("a")["payload"], "stable")
        script = """import sys
sys.path.insert(0,sys.argv[1])
from milestone_monitor.store import Store
s=Store(sys.argv[2]);g=s.begin('two');s.publish('two',g,{'writer':sys.argv[3]})
"""
        processes = [subprocess.Popen([sys.executable, "-B", "-c", script, str(ROOT / "scripts"), str(self.directory), str(i)], stderr=subprocess.PIPE) for i in range(2)]
        for process in processes:
            _out, err = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, err)
        self.assertIn(self.store.source("two")["payload"]["writer"], {"0", "1"})
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self.assertEqual(self.store.source("a")["payload"], "stable")
            with self.assertRaisesRegex(MonitorError, "ocupado"):
                self.store.begin("a")

    def test_disk_full_error_does_not_replace_snapshot(self):
        publish(self.store, "a", "stable")
        generation = self.store.begin("a")
        with self.store.connect() as db:
            db.execute("CREATE TRIGGER full BEFORE UPDATE OF payload ON sources BEGIN SELECT RAISE(ABORT,'database or disk is full'); END")
        with self.assertRaisesRegex(MonitorError, "armazenamento"):
            self.store.publish("a", generation, "partial")
        self.assertEqual(self.store.source("a")["payload"], "stable")
        with patch("milestone_monitor.store.os.open", side_effect=OSError(28, "No space left on device")):
            with self.assertRaisesRegex(MonitorError, "armazenamento"):
                Store(self.directory / "other")

    def test_binding_conflict_keeps_previous_and_unbind_preserves_sources(self):
        publish(self.store, "a", "history")
        value = {"session_id": "ses_test", "context": {"pid": 1}}
        self.store.bind("binding:one", value)
        saved = self.store.bindings()["binding:one"]
        self.assertTrue(saved["revision"])
        self.assertEqual({k: v for k, v in saved.items() if k != "revision"}, value)
        with self.assertRaises(MonitorError):
            self.store.bind("binding:two", value)
        self.assertEqual(self.store.bindings(), {"binding:one": saved})
        self.store.unbind("binding:one")
        self.assertEqual(self.store.source("a")["payload"], "history")

    def test_binding_generation_guard_and_persistent_invalidation(self):
        seed(self.store)
        generation = self.store.source(f"comments:{REPO}:7")["accepted"]
        self.store.bind("binding:one", {"session_id": "ses_test", "context": {}}, guards=((f"comments:{REPO}:7", generation),))
        revision = self.store.bindings()["binding:one"]["revision"]
        publish(self.store, "runtime", {"binding:one": {"state": "incompatible", "at": NOW.isoformat(), "binding_revision": revision}})
        self.assertEqual(Store(self.directory).bindings()["binding:one"]["invalidated"], "incompatible")
        publish(self.store, f"comments:{REPO}:7", snapshots(record()))
        before = self.store.bindings()
        with self.assertRaisesRegex(MonitorError, "cache mudou"):
            self.store.bind("binding:one", {"session_id": "ses_changed", "context": {}}, guards=((f"comments:{REPO}:7", generation),))
        self.assertEqual(self.store.bindings(), before)
