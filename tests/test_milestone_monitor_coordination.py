"""TUI, coleta pontual e observador compartilham um único publicador local."""
from datetime import timedelta
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest

from milestone_monitor_fixtures import CONFIG, ROOT
from milestone_monitor.collector import Background, Collector
from milestone_monitor.common import MonitorError, iso_time, utc_now
from milestone_monitor.observer import Observer
from milestone_monitor.store import Store
from test_milestone_monitor_observer import FakeCollector, FakeBridge, wait_for


class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        self.config = {**CONFIG, "targets": []}

    def background(self, store=None, collector=None):
        collector = collector or Collector(store or self.store, self.config)
        bg = Background(collector, utc_now())
        self.addCleanup(bg.close)
        bg.start()
        return bg

    def test_two_dashboards_only_one_collects_and_follower_refresh_coalesces(self):
        first = self.background()
        second = self.background(Store(self.temp.name))
        self.assertIsNotNone(first.lease)
        self.assertIsNone(second.lease)
        self.assertIn("milestones", second.models.get(timeout=3))
        for _ in range(10):
            second.request()
        request = self.store.local("collector:refresh")
        self.assertEqual(request["collector_epoch"], first.lease.epoch)
        self.assertTrue(self.store.collection_requested(first.lease.epoch))
        self.assertFalse(self.store.collection_requested(first.lease.epoch))
        second.close()
        self.assertTrue(self.store.collector_status()["live"])

    def test_observer_handoff_rejects_old_response_and_second_observer(self):
        collector = Collector(self.store, self.config)
        entered, release, finished = threading.Event(), threading.Event(), threading.Event()
        def operation():
            entered.set()
            release.wait(10)
            return {"old": True}
        def collect(force=False, include_runtime=False):
            try:
                collector.update("delayed", 0, operation)
            finally:
                finished.set()
        collector.collect = collect
        bg = self.background(collector=collector)
        self.addCleanup(release.set)
        self.assertTrue(entered.wait(2))
        first_epoch = bg.lease.epoch
        config = {**CONFIG, "runtime": {**CONFIG["runtime"], "enabled": True}}
        observer_store = Store(self.temp.name)
        observer = Observer(observer_store, config, collector=FakeCollector(observer_store), bridge_factory=FakeBridge)
        self.addCleanup(observer.close)
        observer.start()
        self.assertNotEqual(first_epoch, observer.lease.epoch)
        self.assertIsNone(bg.lease)
        release.set()
        self.assertTrue(finished.wait(3))
        self.assertIsNone(self.store.source("delayed")["payload"])
        other = Store(self.temp.name)
        second = Observer(other, config, collector=FakeCollector(other), bridge_factory=FakeBridge)
        self.addCleanup(second.close)
        with self.assertRaisesRegex(MonitorError, "dono"):
            second.start()
        self.assertEqual(self.store.collector_status()["epoch"], observer.lease.epoch)
        bg.close()
        self.assertTrue(self.store.collector_status()["live"])

    def test_collect_once_with_owner_reads_and_signals_without_sources(self):
        lease = self.store.acquire_collector("observe")
        self.addCleanup(lease.close)
        config_path = self.store.path.parent / "config.json"
        config_path.write_text(json.dumps(self.config))
        # PATH sem gh/opencode/node: qualquer coleta concorrente falharia.
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/aew"), "collect", "--once",
                                 "--config", str(config_path), "--state-dir", self.temp.name],
                                env={**os.environ, "PATH": "/caminho-inexistente"}, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["milestones"], [])
        self.assertTrue(self.store.collection_requested(lease.epoch))
        self.assertTrue(self.store.collector_status()["live"])

    def test_owner_refresh_does_not_bypass_retry_at(self):
        lease = self.store.acquire_collector("observe")
        self.addCleanup(lease.close)
        generation = self.store.begin("fixture", epoch=lease.epoch)
        self.store.fail("fixture", generation, MonitorError("rate limit"),
                        iso_time(utc_now() + timedelta(seconds=60)), epoch=lease.epoch)
        self.store.request_collection()
        self.assertTrue(self.store.collection_requested(lease.epoch))
        collector = Collector(self.store, self.config, epoch=lease.epoch)
        calls = []
        collector.update("fixture", 0, lambda: calls.append(True), force=True)
        self.assertEqual(calls, [])
