"""Coleta por fonte independente, backoff persistente e fila coalescida."""
import queue
import sqlite3
import threading
from datetime import timedelta

from .common import MonitorError, iso_time, parse_time, utc_now
from .github import GitHub
from .runtime import Runtime
from .projection import analyze, incarnation_key, model


class Collector:
    def __init__(self, store, config, github=None, runtime=None, clock=utc_now):
        self.store, self.config, self.clock = store, config, clock
        self.github = github or GitHub(timeout=config["timing"]["timeout"])
        self.runtime = runtime or Runtime(config["runtime"], timeout=config["timing"]["timeout"])
        self.stop = threading.Event()

    def update(self, key, interval, operation, force=False):
        if self.stop.is_set():
            return
        now, source = self.clock(), self.store.source(key)
        retry = parse_time(source.get("retry_at"))
        previous = parse_time(source.get("attempted_at"))
        if retry and now < retry or not force and previous and (now - previous).total_seconds() < interval:
            return
        generation = self.store.begin(key, iso_time(now))
        try:
            payload = operation()
            if not self.stop.is_set():
                self.store.publish(key, generation, payload, iso_time(self.clock()))
        except MonitorError as error:
            seconds = error.retry_after if error.retry_after is not None else min(900, 15 * 2 ** min(source.get("failures", 0), 6))
            self.store.fail(key, generation, error, iso_time(self.clock() + timedelta(seconds=max(1, seconds))))

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
        self.thread = threading.Thread(target=self.run, name="aew-collector", daemon=True)
        self.workers = [] if offline else [
            threading.Thread(target=self.source_loop, args=(False,), name="aew-github", daemon=True),
            threading.Thread(target=self.source_loop, args=(True,), name="aew-runtime", daemon=True)]

    def start(self):
        for worker in self.workers:
            worker.start()
        self.thread.start()

    def request(self):
        self.refresh.set()
        self.github_refresh.set()
        self.runtime_refresh.set()

    def publish(self, value):
        try:
            self.models.get_nowait()
        except queue.Empty:
            pass
        self.models.put_nowait(value)

    def run(self):
        while not self.collector.stop.is_set():
            self.refresh.clear()
            try:
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
        while not self.collector.stop.is_set():
            force = refresh.is_set()
            refresh.clear()
            try:
                if runtime:
                    self.collector.collect_runtime(force)
                else:
                    self.collector.collect(force, include_runtime=False)
            except (MonitorError, sqlite3.Error, OSError) as error:
                self.error = error.category if isinstance(error, MonitorError) else "armazenamento indisponível"
            refresh.wait(1)

    def close(self):
        self.collector.stop.set()
        self.request()
        for worker in [self.thread, *self.workers]:
            worker.join(timeout=0.2)  # only panel tasks; never interrupt OpenCode
