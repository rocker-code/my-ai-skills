"""Observador isolado: nenhuma descoberta/publicação ou sessão real."""
import copy
import json
import os
from pathlib import Path
import queue
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from milestone_monitor_fixtures import CONFIG, ROOT
from milestone_monitor.common import MonitorError, iso_time, utc_now
from milestone_monitor.observer import Bridge, Observer
from milestone_monitor.store import Store
from milestone_monitor.observations import MAX_BYTES


CONTEXT = {"endpoint": "shared-discovery", "version": "2.2.5", "pid": 1234}


class FakeCollector:
    def __init__(self, store):
        self.store, self.stop, self.epoch = store, threading.Event(), None
        self.github_calls = self.runtime_calls = 0

    def open_keys(self):
        return set(self.store.bindings())

    def collect(self, **_kwargs):
        self.github_calls += 1

    def collect_runtime(self, force=False):
        self.runtime_calls += 1
        if self.stop.is_set():
            return
        generation = self.store.begin("runtime", epoch=self.epoch)
        self.store.publish("runtime", generation, {key: {"state": "active", "at": iso_time(),
                           "binding_revision": b["revision"], "collector_epoch": self.epoch}
                           for key, b in self.store.bindings().items()}, epoch=self.epoch)


class FakeBridge:
    def __init__(self, config):
        self.config, self.events, self.failed = config, queue.Queue(), threading.Event()
        self.closed = False

    def close(self):
        self.closed = True


def wait_for(predicate, seconds=5):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError("condição isolada não atingida")


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.store = Store(self.path / "state")
        self.config = copy.deepcopy(CONFIG)
        self.config["runtime"]["enabled"] = True
        self.collector = FakeCollector(self.store)

    def binding(self):
        self.store.bind("binding:fixture", {"session_id": "ses_fixture", "context": CONTEXT,
                        "worktree": "/fixture/worktree", "bound_at": iso_time(utc_now())})

    def observer(self, factory=FakeBridge):
        value = Observer(self.store, self.config, collector=self.collector, bridge_factory=factory)
        self.addCleanup(value.close)
        return value

    def test_no_optin_or_targets_never_starts_sources(self):
        for override in ({"runtime": {"enabled": False}}, {"targets": []}):
            with self.assertRaises(MonitorError):
                Observer(self.store, {**self.config, **override}, collector=self.collector)
        self.assertEqual(self.collector.github_calls, 0)
        self.assertIsNone(self.store.collector_status())

    def test_missing_bridge_is_degraded_but_snapshots_continue(self):
        self.binding()
        def missing(_config):
            raise MonitorError("ponte opcional indisponível")
        observer = self.observer(missing)
        observer.start()
        wait_for(lambda: self.store.source("runtime").get("payload"))
        observer.step()
        self.assertEqual(self.store.local("observer:health")["state"], "degraded")
        self.assertGreater(self.collector.github_calls, 0)
        self.assertEqual(self.store.source("runtime")["payload"]["binding:fixture"]["state"], "active")

    def test_foreground_without_dashboard_persists_only_metadata_and_cancels(self):
        self.binding()
        observer = self.observer()
        failures = []
        def run():
            try:
                observer.run()
            except Exception as error:
                failures.append(type(error).__name__)
        thread = threading.Thread(target=run)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(observer.stop.set)
        wait_for(lambda: observer.bridge is not None)
        binding = self.store.bindings()["binding:fixture"]
        observer.bridge.events.put(json.dumps({"version": 1, "type": "form.created", "event_id": "evt_fixture",
            "created": int(utc_now().timestamp() * 1000), "received_at": utc_now().isoformat(), "context": CONTEXT,
            "session_id": "ses_fixture", "binding_revision": binding["revision"], "request_id": "frm_fixture",
            "answer": "SEGREDO_FIXTURE"}).encode() + b"\n")
        wait_for(lambda: len(self.store.runtime_facts()) == 1)
        bridge = observer.bridge
        observer.stop.set()
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(failures, [])
        self.assertTrue(bridge.closed)
        self.assertFalse(self.store.collector_status()["live"])
        self.assertEqual(self.store.local("observer:health")["state"], "stopped")
        self.assertNotIn(b"SEGREDO_FIXTURE", self.store.path.read_bytes())

    def test_bad_envelope_drops_continuity_not_periodic_collection(self):
        self.binding()
        observer = self.observer()
        observer.start()
        wait_for(lambda: self.store.source("runtime").get("payload"))
        observer.step()
        observer.bridge.events.put(b"SEGREDO_FIXTURE\n")
        observer.step()
        self.assertIsNone(observer.bridge)
        self.assertFalse(self.store.local("observer:coverage")["complete"])
        self.assertFalse(self.collector.stop.is_set())
        self.assertNotIn(b"SEGREDO_FIXTURE", self.store.path.read_bytes())

    def test_runtime_timeout_does_not_stop_github_or_foreground(self):
        def timeout(force=False):
            raise MonitorError("timeout")
        self.collector.collect_runtime = timeout
        observer = self.observer()
        observer.start()
        wait_for(lambda: observer.error is not None)
        observer.step()
        self.assertGreater(self.collector.github_calls, 0)
        self.assertEqual(self.store.local("observer:health")["state"], "degraded")
        self.assertFalse(observer.stop.is_set())

    def test_python_supervisor_limits_read_and_stops_only_its_child(self):
        bridge_root = self.path / "bridge"
        (bridge_root / "node_modules/@opencode/client").mkdir(parents=True)
        (bridge_root / "node_modules/@opencode/client/package.json").write_text('{"version":"fixture"}')
        script = bridge_root / "main.js"
        script.write_text("import sys,time\nsys.stdin.read()\nprint('x'*17000,flush=True)\nprint('SEGREDO_FIXTURE',file=sys.stderr,flush=True)\ntime.sleep(60)\n")
        bridge = Bridge({}, node=sys.executable, script=script)
        self.addCleanup(bridge.close)
        wait_for(bridge.failed.is_set)
        self.assertTrue(bridge.events.empty())
        bridge.close()
        self.assertIsNotNone(bridge.process.poll())

    def test_cli_no_tty_missing_runtime_and_sigterm(self):
        bin_dir = self.path / "bin"
        bin_dir.mkdir()
        (bin_dir / "python3").symlink_to(sys.executable)
        gh = bin_dir / "gh"
        gh.write_text('#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps({"number":1,"title":"fixture"} if "/milestones/" in sys.argv[-1] else []))\n')
        gh.chmod(0o755)
        config = self.path / "config.json"
        config.write_text(json.dumps(self.config))
        env = {**os.environ, "PATH": str(bin_dir), "PYTHONDONTWRITEBYTECODE": "1"}
        process = subprocess.Popen([str(ROOT / "scripts/aew"), "observe", "--config", str(config),
                                    "--state-dir", str(self.path / "cli-state")], env=env,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        state = self.path / "cli-state/monitor.sqlite3"
        wait_for(state.exists)
        store = Store(state.parent)
        wait_for(lambda: store.local("observer:health", {}).get("state") == "degraded")
        process.send_signal(signal.SIGTERM)
        out, err = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 0, err)
        self.assertEqual(out, b"")
        self.assertFalse(store.collector_status()["live"])
