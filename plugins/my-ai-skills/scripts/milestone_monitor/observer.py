"""Observador opt-in foreground; encerra somente processos desta ponte."""
import json
import queue
import shutil
import signal
import sqlite3
import subprocess
import threading
import time
from pathlib import Path

from .collector import Collector
from .common import MonitorError, fresh, iso_time, utc_now
from .observations import MAX_BYTES, MAX_FACTS, normalize


class Bridge:
    def __init__(self, config, node=None, script=None, env=None):
        script = Path(script) if script else Path(__file__).resolve().parents[2] / "integrations/opencode-observer/main.js"
        node = node or shutil.which("node")
        if not node or not script.is_file() or not (script.parent / "node_modules/@opencode/client/package.json").is_file():
            raise MonitorError("ponte opcional indisponível")
        data = json.dumps(config).encode()
        if len(data) > MAX_BYTES:
            raise MonitorError("configuração da ponte excedida")
        self.events = queue.Queue(maxsize=MAX_FACTS)
        self.failed = threading.Event()
        self.process = subprocess.Popen([node, str(script)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, env=env)
        try:
            self.process.stdin.write(data)
            self.process.stdin.close()
        except (OSError, BrokenPipeError):
            self.close()
            raise MonitorError("ponte opcional indisponível") from None
        self.thread = threading.Thread(target=self.read, name="aew-bridge", daemon=True)
        self.thread.start()

    def read(self):
        try:
            while True:
                line = self.process.stdout.readline(MAX_BYTES + 1)
                if not line:
                    break
                if len(line) > MAX_BYTES or not line.endswith(b"\n"):
                    break
                try:
                    self.events.put_nowait(line)
                except queue.Full:
                    break
        except OSError:
            pass
        finally:
            self.failed.set()

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)
        for stream in (self.process.stdin, self.process.stdout):
            if stream and not stream.closed:
                stream.close()
        if hasattr(self, "thread"):
            self.thread.join(timeout=0.2)


class Observer:
    def __init__(self, store, config, collector=None, bridge_factory=Bridge, clock=utc_now):
        if not config["runtime"]["enabled"]:
            raise MonitorError("runtime desabilitado")
        if not config["targets"] or not any(target["milestones"] for target in config["targets"]):
            raise MonitorError("observação exige alvos explícitos")
        self.store, self.config, self.clock = store, config, clock
        self.collector = collector or Collector(store, config, clock=clock)
        self.bridge_factory = bridge_factory
        self.stop = threading.Event()
        self.runtime_refresh = threading.Event()
        self.github_refresh = threading.Event()
        self.bridge = self.bridge_config = self.lease = None
        self.workers = []
        self.retry_at = 0
        self.failures = 0
        self.error = None

    def health(self, state, error=None):
        self.store.observer_health(self.lease.epoch, state, error, iso_time(self.clock()))

    def source_loop(self, runtime):
        while not self.stop.is_set():
            try:
                if runtime:
                    force = self.runtime_refresh.is_set()
                    self.runtime_refresh.clear()
                    self.collector.collect_runtime(force)
                else:
                    force = self.github_refresh.is_set()
                    self.github_refresh.clear()
                    self.collector.collect(force=force, include_runtime=False)
            except (MonitorError, OSError, sqlite3.Error):
                # Nenhum erro bruto/resultado de ferramenta é copiado.
                self.error = "fonte de coleta indisponível"
            (self.runtime_refresh if runtime else self.github_refresh).wait(1)

    def start(self):
        deadline = time.monotonic() + self.config["timing"]["timeout"]
        while not self.stop.is_set():
            try:
                self.lease = self.store.acquire_collector("observe")
                break
            except MonitorError as error:
                owner = self.store.collector_status()
                if (error.category != "coleta já possui dono" or not owner or owner["kind"] != "dashboard"
                        or time.monotonic() >= deadline):
                    raise
                self.store.request_collection("handoff")
                self.stop.wait(0.1)
        if not self.lease:
            return
        self.collector.epoch = self.lease.epoch
        self.health("starting")
        self.store.observation_gap(self.lease.epoch, "reinício do observador", self.clock().isoformat())
        for runtime in (False, True):
            thread = threading.Thread(target=self.source_loop, args=(runtime,), daemon=True)
            self.workers.append(thread)
            thread.start()

    def configuration(self):
        open_keys = self.collector.open_keys()
        source = self.store.source("runtime")
        samples = source.get("payload") or {}
        bindings = {key: value for key, value in self.store.bindings().items()
                    if key in open_keys and not value.get("invalidated") and not source.get("error")
                    and samples.get(key, {}).get("collector_epoch") == self.lease.epoch
                    and samples.get(key, {}).get("binding_revision") == value.get("revision")
                    and fresh(samples.get(key, {}).get("at"), self.clock(), self.config["timing"]["activity_ttl"])
                    and samples.get(key, {}).get("state") in {"active", "inactive"}}
        contexts = [b["context"] for b in bindings.values()]
        if not contexts:
            return None
        context = contexts[0]
        if any(c != context for c in contexts) or context["endpoint"] != (self.config["runtime"].get("server") or "shared-discovery"):
            raise MonitorError("contexto da ponte incompatível")
        value = {"version": 1, "context": context,
                 "bindings": [{k: b[k] for k in ("session_id", "revision", "worktree", "bound_at")} for b in bindings.values()]}
        if self.config["runtime"].get("server"):
            value["server"] = self.config["runtime"]["server"]
        return value

    def step(self):
        if self.store.collection_requested(self.lease.epoch):
            self.runtime_refresh.set()
            self.github_refresh.set()
        config = self.configuration()
        if self.bridge and (config != self.bridge_config or self.bridge.failed.is_set()):
            self.bridge.close()
            self.bridge = None
            self.store.observation_gap(self.lease.epoch, "fluxo interrompido", self.clock().isoformat())
            self.runtime_refresh.set()
            self.retry_at = time.monotonic() + min(900, 15 * 2 ** min(self.failures, 6))
            self.failures += 1
        if not config:
            self.health("degraded", "sem vínculos runtime confirmados")
            return
        if not self.bridge and time.monotonic() >= self.retry_at:
            try:
                self.bridge = self.bridge_factory(config)
                self.bridge_config = config
            except (MonitorError, OSError):
                self.retry_at = time.monotonic() + min(900, 15 * 2 ** min(self.failures, 6))
                self.failures += 1
                self.health("degraded", "ponte opcional indisponível")
                return
        if self.bridge:
            for _ in range(MAX_FACTS):
                try:
                    line = self.bridge.events.get_nowait()
                except queue.Empty:
                    break
                try:
                    fact = normalize(line, config["context"], self.store.bindings(), self.lease.epoch)
                except MonitorError:
                    self.bridge.close()
                    self.bridge = None
                    self.store.observation_gap(self.lease.epoch, "envelope inválido", self.clock().isoformat())
                    self.runtime_refresh.set()
                    self.retry_at = time.monotonic() + min(900, 15 * 2 ** min(self.failures, 6))
                    self.failures += 1
                    self.health("degraded", "envelope de observação inválido")
                    return
                if fact:
                    self.store.append_runtime_fact(fact, self.lease.epoch)
                    self.runtime_refresh.set()
                    if fact["type"] == "server.connected":
                        self.store.observation_gap(self.lease.epoch, "reconexão do fluxo", self.clock().isoformat())
                        self.runtime_refresh.set()
            self.health("live", self.error)
        else:
            self.health("degraded", "ponte em backoff")

    def run(self):
        handlers = {}
        try:
            if threading.current_thread() is threading.main_thread():
                for sig in (signal.SIGTERM, signal.SIGINT):
                    handlers[sig] = signal.signal(sig, lambda *_args: self.stop.set())
            self.start()
            last_heartbeat = 0
            while not self.stop.is_set():
                self.step()
                if time.monotonic() - last_heartbeat >= 5:
                    self.lease.heartbeat(iso_time(self.clock()))
                    last_heartbeat = time.monotonic()
                self.stop.wait(0.25)
        finally:
            self.close()
            for sig, handler in handlers.items():
                signal.signal(sig, handler)

    def close(self):
        self.stop.set()
        self.runtime_refresh.set()
        self.github_refresh.set()
        self.collector.stop.set()
        if self.bridge:
            self.bridge.close()
            self.bridge = None
        for worker in self.workers:
            worker.join(timeout=0.2)
        if self.lease:
            try:
                self.health("stopped")
            finally:
                self.lease.close()
                self.lease = None
