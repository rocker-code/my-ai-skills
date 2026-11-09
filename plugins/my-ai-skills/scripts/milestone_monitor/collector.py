"""Coleta por fonte independente, backoff persistente e fila coalescida."""
import queue
import sqlite3
import threading
import time
from datetime import timedelta

from .common import MonitorError, iso_time, parse_time, utc_now
from .github import GitHub
from .runtime import Runtime
from .projection import analyze, incarnation_key, model


class Collector:
    def __init__(self, store, config, github=None, runtime=None, clock=utc_now, epoch=None):
        self.store, self.config, self.clock = store, config, clock
        self.github = github or GitHub(timeout=config["timing"]["timeout"])
        self.runtime = runtime or Runtime(config["runtime"], timeout=config["timing"]["timeout"])
        self.stop = threading.Event()
        self.epoch = epoch

    def update(self, key, interval, operation, force=False):
        if self.stop.is_set():
            return
        now, source = self.clock(), self.store.source(key)
        retry = parse_time(source.get("retry_at"))
        previous = parse_time(source.get("attempted_at"))
        if retry and now < retry or not force and previous and (now - previous).total_seconds() < interval:
            return
        generation = self.store.begin(key, iso_time(now), epoch=self.epoch)
        try:
            payload = operation()
            if not self.stop.is_set():
                if key == "runtime" and self.epoch:
                    payload = {identity: {**item, "collector_epoch": self.epoch} for identity, item in payload.items()}
                self.store.publish(key, generation, payload, iso_time(self.clock()), epoch=self.epoch)
        except MonitorError as error:
            seconds = error.retry_after if error.retry_after is not None else min(900, 15 * 2 ** min(source.get("failures", 0), 6))
            if not self.stop.is_set():
                self.store.fail(key, generation, error, iso_time(self.clock() + timedelta(seconds=max(1, seconds))), epoch=self.epoch)

    def open_keys(self):
        result = set()
        allowed = set()
        for target in self.config["targets"]:
            inventory = self.store.source("inventory:" + target["repository"]).get("payload") or {}
            allowed.update((target["repository"], issue["number"]) for issue in inventory.get("issues", [])
                           if issue["milestone"] in target["milestones"] and issue["state"] == "open")
        for source in self.store.sources("comments:"):
            for snapshot in source.get("payload") or []:
                record = snapshot["record"]
                if record.get("finished_at") or (record["repository"], record["issue"]["number"]) not in allowed:
                    continue
                _summary, details = analyze(record, self.clock())
                for interval in details["intervals"]:
                    if not interval["closed_at"] and not interval["terminal"]:
                        result.add(incarnation_key(record["repository"], record["issue"]["number"], record["run_id"], interval))
        return result

    def collect_runtime(self, force=False):
        if self.config["runtime"]["enabled"]:
            self.update("runtime", self.config["timing"]["runtime_interval"],
                        lambda: self.runtime.collect(self.store.bindings(), self.open_keys()), force)
            if self.epoch and not self.stop.is_set():
                try:
                    self.runtime.project_facts(self.store, self.open_keys(), self.epoch)
                except MonitorError as error:
                    if error.category == "limite de pedidos observados":
                        self.store.observation_gap(self.epoch, "saturação de fatos")
                    raise

    def collect(self, force=False, include_runtime=True):
        for target in self.config["targets"]:
            repo = target["repository"]
            self.update("inventory:" + repo, self.config["timing"]["github_interval"],
                        lambda: self.github.inventory(repo, target["milestones"]), force)
            payload = self.store.source("inventory:" + repo).get("payload") or {}
            for issue in payload.get("issues", []):
                number = issue["number"]
                self.update(f"comments:{repo}:{number}", self.config["timing"]["github_interval"],
                            lambda: self.github.comments(repo, number), force)
                self.update(f"prs:{repo}:{number}", self.config["timing"]["github_interval"],
                            lambda: self.github.pull_requests(repo, number), force)
        if include_runtime:
            self.collect_runtime(force)


class Background:
    """Fila de modelos limitada; refresh não cria coletores concorrentes."""
    def __init__(self, collector, session_started, offline=False):
        self.collector, self.session_started, self.offline = collector, session_started, offline
        self.models = queue.Queue(maxsize=1)
        self.refresh = threading.Event()
        self.github_refresh, self.runtime_refresh = threading.Event(), threading.Event()
        self.error = None
        self.lease = None
        self.closed = threading.Event()
        self.ownership_lock = threading.Lock()
        self.last_heartbeat = 0
        self.thread = threading.Thread(target=self.run, name="aew-collector", daemon=True)
        self.workers = [] if offline else [
            threading.Thread(target=self.source_loop, args=(False,), name="aew-github", daemon=True),
            threading.Thread(target=self.source_loop, args=(True,), name="aew-runtime", daemon=True)]

    def start(self):
        if not self.offline:
            self.maintain_ownership()
        for worker in self.workers:
            worker.start()
        self.thread.start()

    def request(self):
        self.refresh.set()
        if self.lease:
            self.github_refresh.set()
            self.runtime_refresh.set()
        elif not self.offline:
            self.collector.store.request_collection()

    def maintain_ownership(self):
        with self.ownership_lock:
            self._maintain_ownership()

    def _maintain_ownership(self):
        if self.offline or self.closed.is_set():
            return
        store = self.collector.store
        if self.lease and store.collection_requested(self.lease.epoch, "handoff", consume=False):
            self.collector.stop.set()
            self.lease.close()
            self.lease = None
        if not self.lease:
            try:
                lease = store.acquire_collector("dashboard")
            except MonitorError as error:
                if error.category not in {"coleta já possui dono", "coleta reservada ao observador"}:
                    raise
                return
            if self.collector.stop.is_set():
                old = self.collector
                self.collector = Collector(store, old.config, old.github, old.runtime, old.clock)
            self.lease = lease
            self.collector.epoch = lease.epoch
        if time.monotonic() - self.last_heartbeat >= 5:
            self.lease.heartbeat()
            self.last_heartbeat = time.monotonic()
        if store.collection_requested(self.lease.epoch):
            self.github_refresh.set()
            self.runtime_refresh.set()

    def publish(self, value):
        try:
            self.models.get_nowait()
        except queue.Empty:
            pass
        self.models.put_nowait(value)

    def run(self):
        while not self.closed.is_set():
            self.refresh.clear()
            try:
                self.maintain_ownership()
                value = model(self.collector.store, self.collector.config, self.session_started)
                if self.error:
                    value["error"] = self.error
                self.publish(value)
            except (MonitorError, sqlite3.Error, OSError) as error:
                self.publish({"error": error.category if isinstance(error, MonitorError) else "armazenamento indisponível"})
            # Monotonic Event.wait: no refresh spin, coalesces repeated keys.
            self.refresh.wait(1)

    def source_loop(self, runtime):
        refresh = self.runtime_refresh if runtime else self.github_refresh
        while not self.closed.is_set():
            force = refresh.is_set()
            refresh.clear()
            try:
                current, lease = self.collector, self.lease
                if lease and not current.stop.is_set():
                    if runtime:
                        current.collect_runtime(force)
                    else:
                        current.collect(force, include_runtime=False)
            except (MonitorError, sqlite3.Error, OSError) as error:
                self.error = error.category if isinstance(error, MonitorError) else "armazenamento indisponível"
            refresh.wait(1)

    def close(self):
        self.closed.set()
        self.collector.stop.set()
        self.refresh.set()
        self.github_refresh.set()
        self.runtime_refresh.set()
        for worker in [self.thread, *self.workers]:
            worker.join(timeout=0.2)  # only panel tasks; never interrupt OpenCode
        with self.ownership_lock:
            if self.lease:
                self.lease.close()
                self.lease = None
