"""Posse entre processos, epochs e preservação do schema/cache existentes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from milestone_monitor_fixtures import ROOT
from milestone_monitor.common import MonitorError
from milestone_monitor.store import Store


class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.store = Store(self.directory)

    def lease(self, store=None, **kwargs):
        lease = (store or self.store).acquire_collector("observe", **kwargs)
        self.addCleanup(lease.close)
        return lease

    def test_owner_metadata_heartbeat_never_renews_source(self):
        lease = self.lease()
        generation = self.store.begin("inventory", epoch=lease.epoch)
        self.store.publish("inventory", generation, {"stable": True}, epoch=lease.epoch)
        source = self.store.source("inventory")
        lease.heartbeat("2026-11-08T00:00:00+00:00")
        self.assertEqual(self.store.source("inventory"), source)
        status = self.store.collector_status()
        self.assertTrue(status["live"])
        self.assertEqual(status["pid"], os.getpid())
        self.assertEqual(status["epoch"], lease.epoch)
        with self.store.connect() as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 1)
        with self.assertRaisesRegex(MonitorError, "dono"):
            Store(self.directory).acquire_collector("observe", now="2099-01-01T00:00:00Z")
        with self.assertRaisesRegex(MonitorError, "dono"):
            Store(self.directory).begin("inventory")

    def test_new_epoch_invalidates_inflight_generation_and_closed_owner(self):
        generation = self.store.begin("inventory")
        first = self.lease()
        first.close()
        self.assertFalse(self.store.collector_status()["live"])
        next_store = Store(self.directory)
        second = self.lease(next_store)
        self.assertNotEqual(first.epoch, second.epoch)
        self.assertFalse(next_store.publish("inventory", generation, "old", epoch=second.epoch))
        with self.assertRaises(MonitorError):
            self.store.publish("inventory", generation, "old", epoch=first.epoch)
        with self.assertRaises(MonitorError):
            first.heartbeat()

    def test_competing_process_and_process_crash_release_kernel_lock(self):
        script = '''import sys,os
sys.path.insert(0,sys.argv[1])
from milestone_monitor.store import Store
s=Store(sys.argv[2]); lease=s.acquire_collector('observe')
print(lease.epoch,flush=True)
sys.stdin.readline()
os._exit(0)
'''
        process = subprocess.Popen([sys.executable, "-B", "-c", script, str(ROOT / "scripts"), str(self.directory)],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        first = process.stdout.readline().strip()
        self.assertTrue(first)
        with self.assertRaisesRegex(MonitorError, "dono"):
            self.store.acquire_collector("observe")
        process.stdin.write("exit\n")
        process.stdin.flush()
        _out, errors = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 0, errors)
        second = self.lease()
        self.assertNotEqual(first, second.epoch)

    def test_future_owner_preserved_and_failed_acquisition_releases_lock(self):
        self.store.put_local("collector:owner", {"version": 99, "unknown": "preservar"})
        with self.assertRaisesRegex(MonitorError, "incompatível"):
            self.store.acquire_collector("observe")
        self.assertEqual(self.store.local("collector:owner"), {"version": 99, "unknown": "preservar"})
        with self.store.connect() as db:
            db.execute("DELETE FROM local WHERE key='collector:owner'")
        self.lease()

    def test_full_disk_preserves_previous_owner_and_snapshots(self):
        generation = self.store.begin("inventory")
        self.store.publish("inventory", generation, "stable")
        with self.store.connect() as db:
            db.execute("CREATE TRIGGER full BEFORE INSERT ON local BEGIN SELECT RAISE(ABORT,'disk full'); END")
        with self.assertRaises(MonitorError):
            self.store.acquire_collector("observe")
        self.assertIsNone(self.store.local("collector:owner"))
        self.assertEqual(self.store.source("inventory")["payload"], "stable")
        with self.store.connect() as db:
            db.execute("DROP TRIGGER full")
        self.lease()

    def test_corrupted_database_not_recreated(self):
        self.store.path.write_bytes(b"corrompido")
        before = self.store.path.read_bytes()
        with self.assertRaises(MonitorError):
            Store(self.directory)
        self.assertEqual(self.store.path.read_bytes(), before)
