"""Ponta a ponta sintético com cliente instalado; nunca inicia OpenCode real.

OPENCODE_OBSERVER_BRIDGE aponta para main.js de uma cópia com npm ci executado.
Sem essa opção explícita, a suíte stdlib continua independente de Node.
"""
import base64
import copy
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen

from milestone_monitor_fixtures import CONFIG, inventory, ROOT
from milestone_monitor.collector import Background, Collector
from milestone_monitor.common import MonitorError, utc_now
from milestone_monitor.coordinator import Coordinator
from milestone_monitor.ingest import comments_snapshot
from milestone_monitor.journal import Journal
from milestone_monitor.observer import Bridge, Observer
from milestone_monitor.projection import model
from milestone_monitor.publisher import Publisher
from milestone_monitor.runtime import Runtime
from milestone_monitor.store import Store
from test_milestone_monitor_journal import operation
from test_milestone_monitor_observer import wait_for
from test_milestone_monitor_publisher import FakeGitHub
from workflow_metrics import parse_run_comment, summarize_run


class Transport:
    """Servidor apenas loopback, senha sintética e feeds distintos por conexão."""
    def __init__(self, worktree):
        self.worktree, self.feeds, self.queries = str(worktree), [], []
        self.active, self.permissions, self.forms = True, [], []
        self.sequence = 0
        self.stopping = threading.Event()
        fixture = self
        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *_args):
                pass

            def do_GET(self):
                parsed = urlparse(self.path)
                expected = "Basic " + base64.b64encode(b"opencode:SEGREDO_FIXTURE").decode()
                if self.headers.get("Authorization") != expected:
                    self.send_response(401)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                fixture.queries.append(parsed.path)  # nunca salvar headers/credenciais
                if parsed.path == "/api/event":
                    types = parse_qs(parsed.query).get("types", [])
                    fixture.types = types
                    feed = queue.Queue()
                    fixture.feeds.append(feed)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    connected = {"id": "evt_connected_" + str(len(fixture.feeds)), "created": int(time.time() * 1000),
                                 "type": "server.connected", "data": {}}
                    feed.put(connected)
                    while not fixture.stopping.is_set():
                        try:
                            event = feed.get(timeout=0.1)
                        except queue.Empty:
                            continue
                        if event is None:
                            break
                        try:
                            self.wfile.write(("data: " + json.dumps(event) + "\n\n").encode())
                            self.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError):
                            break
                    self.close_connection = True
                    return
                values = {
                    "/api/info": {"version": "2.2.5", "pid": 1234},
                    "/api/session/active": {"data": {"ses_fixture": {"type": "running"}} if fixture.active else {}},
                    "/api/session/ses_fixture": {"data": {"id": "ses_fixture", "projectID": "prj_fixture",
                                                          "location": {"directory": fixture.worktree}}},
                    "/api/location": {"directory": fixture.worktree, "project": {"id": "prj_fixture"}},
                    "/api/session/ses_fixture/permission": {"data": copy.deepcopy(fixture.permissions)},
                    "/api/session/ses_fixture/form": {"data": copy.deepcopy(fixture.forms)},
                }
                body = json.dumps(values.get(parsed.path, {})).encode()
                self.send_response(200 if parsed.path in values else 404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.url = "http://127.0.0.1:" + str(self.server.server_port)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def call(self, argv, timeout):
        if argv == ["opencode", "--version"]:
            return "2.2.5"
        operation = argv[argv.index("api") + 1]
        path = {"server.info": "/api/info", "session.active": "/api/session/active", "location.get": "/api/location",
                "session.get": "/api/session/ses_fixture", "session.permission.list": "/api/session/ses_fixture/permission",
                "session.form.list": "/api/session/ses_fixture/form"}[operation]
        request = Request(self.url + path, headers={"Authorization": "Basic " + base64.b64encode(b"opencode:SEGREDO_FIXTURE").decode()})
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)

    def send(self, kind, data):
        at = int(time.time() * 1000)
        self.sequence += 1
        event = {"id": "evt_" + str(self.sequence), "created": at,
                 "type": kind, "location": {"directory": self.worktree}, "data": data}
        if kind.startswith("session.execution."):
            event["durable"] = {"aggregateID": "ses_fixture", "version": 1, "seq": self.sequence}
        self.feeds[-1].put(event)
        return at

    def close(self):
        self.stopping.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(3)


@unittest.skipUnless(os.environ.get("OPENCODE_OBSERVER_BRIDGE"), "cliente instalado opt-in")
class InstrumentationE2ETests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="instrumentation-e2e-", dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.worktree = self.path / "checkout"
        self.worktree.mkdir()
        # Checkout local descartável; nenhum fetch/remote real é executado.
        for args in (("init", "-b", "fixture"), ("remote", "add", "origin", "https://github.com/owner/repo.git")):
            subprocess.run(["git", "-C", str(self.worktree), *args], check=True, capture_output=True)
        self.transport = Transport(self.worktree)
        self.addCleanup(self.transport.close)
        self.store = Store(self.path / "state")
        self.github = FakeGitHub(self.store)
        outer = self
        class GitHub:
            def inventory(self, *_args):
                return inventory()
            def comments(self, repo, issue):
                return comments_snapshot(outer.github.read(repo, issue), repo, issue)
            def pull_requests(self, *_args):
                return []
        self.reader = GitHub()
        self.config = copy.deepcopy(CONFIG)
        self.config["runtime"].update(enabled=True, server=self.transport.url)
        self.runtime = Runtime(self.config["runtime"], self.transport.call)
        self.publisher = Publisher(Journal(self.store), self.github.read, self.github.save)
        self.coordinator = Coordinator(self.store, self.config, self.publisher, self.runtime, self.reader)
        self.start = utc_now() - timedelta(seconds=2)
        self.assertEqual(self.coordinator.transition(operation(at=self.start.isoformat()))["publication"], "published")
        self.opening = operation("op-open", event="dispatch", stage="apply", worker_id="worker-A",
            execution={"kind": "worker", "id": "execution-A"}, at=(self.start + timedelta(seconds=1)).isoformat(),
            depends_on=["op-start"], binding={"worktree": str(self.worktree), "branch": "fixture", "session_id": "ses_fixture"})
        self.assertEqual(self.coordinator.transition(self.opening)["binding"], "bound")
        self.key, self.binding = next(iter(self.store.bindings().items()))
        # Ambiente allowlist: nem senha herdada, nem registro de serviço do usuário.
        self.env = {"PATH": os.environ.get("PATH", ""), "HOME": str(self.path), "OPENCODE_PASSWORD": "SEGREDO_FIXTURE",
                    **{name: str(self.path / name) for name in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME")}}
        self.observer = None
        self.addCleanup(lambda: self.observer.close() if self.observer else None)

    def observe(self):
        collector = Collector(self.store, self.config, self.reader, self.runtime)
        self.observer = Observer(self.store, self.config, collector=collector,
            bridge_factory=lambda config: Bridge(config, script=os.environ["OPENCODE_OBSERVER_BRIDGE"], env=self.env))
        self.observer.start()
        self.observer.runtime_refresh.set()
        self.pump(lambda: self.store.local("observer:coverage", {}).get("complete"))

    def pump(self, predicate):
        def tick():
            self.observer.step()
            return predicate()
        wait_for(tick, seconds=10)

    def requests(self):
        return self.store.local(self.store.observation_key(self.key, "requests"), {}).get("requests", {})

    def record(self):
        return parse_run_comment(self.github.comments[0]["body"])

    def reconcile(self):
        return self.coordinator.reconcile(self.opening["issue"], self.opening["run_id"], authorized=True)

    def test_official_stream_wait_retry_gap_restart_and_closed_panels(self):
        self.observe()
        self.assertTrue(all(not any(word in kind for word in ("text", "tool", "reasoning")) for kind in self.transport.types))
        # Consumidor real do painel, sem curses/TTY; fechar não toma a posse.
        panel = Background(Collector(self.store, self.config, self.reader, self.runtime), utc_now())
        panel.start()
        wait_for(lambda: not panel.models.empty())
        panel.close()
        self.assertTrue(self.store.collector_status()["live"])
        self.assertEqual(self.store.collector_status()["kind"], "observe")
        self.transport.send("session.execution.started", {"sessionID": "ses_fixture"})
        self.pump(lambda: any(f.get("projected") and f["type"] == "session.execution.started" for f in self.store.runtime_facts()))
        value = model(self.store, self.config, utc_now())
        self.assertEqual(value["milestones"][0]["issues"][0]["group"], "running")
        writes = self.github.writes
        self.transport.permissions = [{"id": "per_fixture", "sessionID": "ses_fixture", "action": "SEGREDO_FIXTURE"}]
        opened = self.transport.send("permission.asked", self.transport.permissions[0])
        self.pump(lambda: self.requests().get("per_fixture", {}).get("pending"))
        self.transport.forms = [{"id": "frm_fixture", "sessionID": "ses_fixture", "title": "SEGREDO_FIXTURE", "fields": []}]
        self.transport.send("form.created", {"form": self.transport.forms[0]})
        self.pump(lambda: self.requests().get("frm_fixture", {}).get("pending"))
        self.assertEqual(self.github.writes, writes)
        issue = model(self.store, self.config, utc_now())["milestones"][0]["issues"][0]
        self.assertEqual(issue["group"], "blocked")
        self.assertEqual(issue["summary"]["wait_seconds_by_reason"], {})
        self.transport.permissions = []
        self.transport.send("permission.replied", {"requestID": "per_fixture", "sessionID": "ses_fixture", "reply": "once"})
        self.pump(lambda: self.requests().get("per_fixture", {}).get("complete"))
        self.assertTrue(self.requests()["frm_fixture"]["pending"])
        self.transport.forms = []
        closed = self.transport.send("form.replied", {"id": "frm_fixture", "sessionID": "ses_fixture", "answer": {"text": "SEGREDO_FIXTURE"}})
        self.pump(lambda: self.requests().get("frm_fixture", {}).get("complete"))
        self.github.lose_response = True
        self.assertGreater(self.reconcile()["remaining"], 0)
        self.assertEqual(self.reconcile()["remaining"], 0)
        self.assertEqual(self.github.writes, writes + 1)
        expected = (closed - opened) / 1000
        self.assertAlmostEqual(summarize_run(self.record())["wait_seconds_by_reason"]["owner_input"], expected, places=6)
        # Resposta perdida durante desconexão: estado recupera, duração não.
        self.transport.forms = [{"id": "frm_lost", "sessionID": "ses_fixture", "title": "SEGREDO_FIXTURE", "fields": []}]
        self.transport.send("form.created", {"form": self.transport.forms[0]})
        self.pump(lambda: self.requests().get("frm_lost", {}).get("pending"))
        self.transport.feeds[-1].put(None)
        self.pump(lambda: self.observer.bridge is None)
        self.transport.forms = []
        self.observer.runtime_refresh.set()
        self.pump(lambda: not self.requests()["frm_lost"]["pending"])
        self.observer.retry_at = 0  # relógio de backoff avançado somente no teste
        feeds = len(self.transport.feeds)
        self.pump(lambda: len(self.transport.feeds) > feeds and self.store.local("observer:coverage", {}).get("complete"))
        self.assertIsNone(self.requests()["frm_lost"]["resolved_at"])
        self.assertGreater(self.reconcile()["runtime"]["unmeasured"], 0)
        self.transport.active = False
        self.transport.send("session.execution.succeeded", {"sessionID": "ses_fixture"})
        self.pump(lambda: self.store.local(self.store.observation_key(self.key), {}).get("type") == "session.execution.succeeded")
        self.assertGreater(self.reconcile()["runtime"]["results_unverified"], 0)
        self.assertFalse(any(e["type"] in {"stage_finished", "state_observed"} for e in self.record()["events"]))
        old_epoch = self.observer.lease.epoch
        self.observer.close()
        self.assertFalse(self.store.collector_status()["live"])
        self.observe()
        self.assertNotEqual(self.observer.lease.epoch, old_epoch)
        self.assertEqual(self.store.source("runtime")["payload"][self.key]["collector_epoch"], self.observer.lease.epoch)
        self.assertEqual(self.store.bindings()[self.key]["revision"], self.binding["revision"])
        self.assertAlmostEqual(summarize_run(self.record())["wait_seconds_by_reason"]["owner_input"], expected, places=6)
        self.assertEqual(self.record()["schema_version"], 1)
        self.assertNotIn("SEGREDO_FIXTURE", json.dumps(self.github.comments))
        for path in (self.path / "state").iterdir():
            if path.is_file():
                self.assertNotIn(b"SEGREDO_FIXTURE", path.read_bytes())
        self.assertTrue(all(path.startswith("/api/") for path in self.transport.queries))
