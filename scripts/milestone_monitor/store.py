"""Snapshots SQLite transacionais; rede nunca ocorre dentro da transação."""
import json
import os
import sqlite3
import fcntl
import socket
import hashlib
from uuid import uuid4
from pathlib import Path
from datetime import timedelta

from .common import MonitorError, iso_time, parse_time, utc_now


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


class CollectorLease:
    """Lock do kernel, nunca removido/recriado para contornar outro dono."""
    def __init__(self, store, fd, owner):
        self.store, self.fd, self.owner = store, fd, owner

    @property
    def epoch(self):
        return self.owner["epoch"]

    def heartbeat(self, now=None):
        self.store.collector_heartbeat(self.epoch, now)

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
            if self.store._collector is self:
                self.store._collector = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class Store:
    def __init__(self, directory):
        self.path = Path(directory) / "monitor.sqlite3"
        self._collector = None
        try:
            Path(directory).mkdir(mode=0o700, parents=True, exist_ok=True)
            # O_EXCL evita alterar permissões de arquivo preexistente.
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.close(fd)
            except FileExistsError:
                pass
            with self.connect() as db:
                version = db.execute("PRAGMA user_version").fetchone()[0]
                if version not in (0, 1):
                    raise MonitorError("schema futuro incompatível")
                if version == 1:
                    # Existing valid snapshots can be read even when new writes
                    # fail (permissions/disk full). Never recreate damaged tables.
                    db.execute("SELECT key FROM sources LIMIT 1").fetchall()
                    db.execute("SELECT key FROM local LIMIT 1").fetchall()
                    return
                db.executescript("""
                    CREATE TABLE IF NOT EXISTS sources (
                      key TEXT PRIMARY KEY, generation INTEGER NOT NULL DEFAULT 0,
                      accepted INTEGER NOT NULL DEFAULT 0, payload TEXT,
                      attempted_at TEXT, fetched_at TEXT, observed_at TEXT,
                      error TEXT, retry_at TEXT, failures INTEGER NOT NULL DEFAULT 0);
                    CREATE TABLE IF NOT EXISTS local (key TEXT PRIMARY KEY, payload TEXT NOT NULL);
                    PRAGMA user_version=1;
                """)
        except (OSError, sqlite3.Error):
            raise MonitorError("armazenamento indisponível") from None

    def connect(self):
        db = sqlite3.connect(self.path, timeout=1, factory=ClosingConnection)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=1000")
        return db

    @staticmethod
    def _owner(raw):
        try:
            owner = json.loads(raw)
            if not isinstance(owner, dict) or owner.get("version") != 1:
                raise MonitorError("versão de posse incompatível")
            if (not isinstance(owner.get("epoch"), str) or len(owner["epoch"]) != 32 or
                    type(owner.get("pid")) is not int or owner["pid"] <= 0 or
                    not isinstance(owner.get("host"), str) or owner.get("kind") not in {"observe", "dashboard", "collect"} or
                    not parse_time(owner.get("started_at")) or not parse_time(owner.get("heartbeat_at"))):
                raise MonitorError("metadados de posse inválidos")
            return owner
        except (ValueError, TypeError):
            raise MonitorError("metadados de posse inválidos") from None

    def acquire_collector(self, kind, now=None):
        if kind not in {"observe", "dashboard", "collect"}:
            raise MonitorError("tipo de coletor inválido")
        fd = None
        try:
            fd = os.open(self.path.parent / "collector.lock", os.O_CREAT | os.O_RDWR | os.O_CLOEXEC, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise MonitorError("coleta já possui dono") from None
            at = now or iso_time()
            owner = {"version": 1, "epoch": uuid4().hex, "pid": os.getpid(), "host": socket.gethostname(),
                     "kind": kind, "started_at": at, "heartbeat_at": at}
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                handoff = db.execute("SELECT payload FROM local WHERE key='collector:handoff'").fetchone()
                if handoff:
                    request = json.loads(handoff[0])
                    if not isinstance(request, dict) or request.get("version") != 1:
                        raise MonitorError("sinal de coleta incompatível")
                    expires = parse_time(request.get("expires_at"))
                    if kind != "observe" and expires and utc_now() < expires:
                        raise MonitorError("coleta reservada ao observador")
                row = db.execute("SELECT payload FROM local WHERE key='collector:owner'").fetchone()
                if row:
                    self._owner(row[0])
                # Uma consulta antiga nunca publica sob a nova posse, inclusive ABA.
                db.execute("UPDATE sources SET generation=generation+1")
                db.execute("INSERT INTO local VALUES ('collector:owner',?) ON CONFLICT(key) DO UPDATE SET payload=excluded.payload",
                           (json.dumps(owner),))
                if handoff:
                    db.execute("DELETE FROM local WHERE key='collector:handoff'")
            lease = CollectorLease(self, fd, owner)
            self._collector = lease
            return lease
        except (OSError, sqlite3.Error, ValueError):
            if fd is not None:
                os.close(fd)
            raise MonitorError("posse de coleta indisponível") from None
        except MonitorError:
            if fd is not None:
                os.close(fd)
            raise

    def collector_status(self):
        owner = self.local("collector:owner")
        if owner is None:
            return None
        owner = self._owner(json.dumps(owner))
        fd = os.open(self.path.parent / "collector.lock", os.O_CREAT | os.O_RDWR | os.O_CLOEXEC, 0o600)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                live = False
            except BlockingIOError:
                live = True
            # Releitura impede confundir um lock recém-adquirido com epoch antigo.
            current = self.local("collector:owner")
            return {**owner, "live": live and current == owner}
        finally:
            os.close(fd)

    def _check_collector(self, db, epoch):
        row = db.execute("SELECT payload FROM local WHERE key='collector:owner'").fetchone()
        if epoch is not None:
            if not self._collector or self._collector.fd is None or self._collector.epoch != epoch or not row:
                raise MonitorError("posse de coleta encerrada")
            owner = self._owner(row[0])
            if owner["epoch"] != epoch:
                raise MonitorError("epoch de coleta antigo")
        elif row:
            # Caminhos legados sem posse não podem competir com um dono vivo.
            status = self.collector_status()
            if status and status["live"]:
                raise MonitorError("coleta já possui dono")

    def collector_heartbeat(self, epoch, now=None):
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                self._check_collector(db, epoch)
                row = db.execute("SELECT payload FROM local WHERE key='collector:owner'").fetchone()
                owner = json.loads(row[0])
                owner["heartbeat_at"] = now or iso_time()
                db.execute("UPDATE local SET payload=? WHERE key='collector:owner'", (json.dumps(owner),))
                self._collector.owner = owner
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def request_collection(self, action="refresh"):
        if action not in {"refresh", "handoff"}:
            raise MonitorError("sinal de coleta inválido")
        owner = self.collector_status()
        if not owner or not owner["live"]:
            return False
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                current = db.execute("SELECT payload FROM local WHERE key='collector:owner'").fetchone()
                if not current or json.loads(current[0]).get("epoch") != owner["epoch"]:
                    return False
                key = "collector:" + action
                previous = db.execute("SELECT payload FROM local WHERE key=?", (key,)).fetchone()
                if previous:
                    value = json.loads(previous[0])
                    if not isinstance(value, dict) or value.get("version") != 1:
                        raise MonitorError("sinal de coleta incompatível")
                    expires = parse_time(value.get("expires_at"))
                    if value.get("collector_epoch") == owner["epoch"] and expires and expires > utc_now():
                        return True
                self._put_versioned(db, key, {"version": 1, "collector_epoch": owner["epoch"],
                                    "expires_at": iso_time(utc_now() + timedelta(seconds=15))})
                return True
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def collection_requested(self, epoch, action="refresh", consume=True):
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                self._check_collector(db, epoch)
                key = "collector:" + action
                row = db.execute("SELECT payload FROM local WHERE key=?", (key,)).fetchone()
                if not row:
                    return False
                value = json.loads(row[0])
                if not isinstance(value, dict) or value.get("version") != 1:
                    raise MonitorError("sinal de coleta incompatível")
                expires = parse_time(value.get("expires_at"))
                valid = value.get("collector_epoch") == epoch and expires and expires > utc_now()
                if consume:
                    db.execute("DELETE FROM local WHERE key=?", (key,))
                return bool(valid)
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    @staticmethod
    def _put_versioned(db, key, value):
        row = db.execute("SELECT payload FROM local WHERE key=?", (key,)).fetchone()
        if row:
            previous = json.loads(row[0])
            if not isinstance(previous, dict) or previous.get("version") != 1:
                raise MonitorError("metadados locais incompatíveis")
        db.execute("INSERT INTO local VALUES (?,?) ON CONFLICT(key) DO UPDATE SET payload=excluded.payload",
                   (key, json.dumps(value, sort_keys=True)))

    def observer_health(self, epoch, state, error=None, now=None):
        if state not in {"starting", "live", "degraded", "stopped"}:
            raise MonitorError("saúde de observador inválida")
        if error not in {None, "fonte de coleta indisponível", "sem vínculos runtime confirmados",
                         "ponte opcional indisponível", "ponte em backoff", "envelope de observação inválido"}:
            raise MonitorError("diagnóstico de observador inválido")
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                self._check_collector(db, epoch)
                self._put_versioned(db, "observer:health", {"version": 1, "collector_epoch": epoch,
                                    "state": state, "at": now or iso_time(), "error": error})
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def _gap(self, db, epoch, reason, now):
        if reason not in {"reinício do observador", "fluxo interrompido", "reconexão do fluxo", "envelope inválido",
                          "saturação de fatos", "vínculo alterado", "contexto alterado"}:
            raise MonitorError("motivo de lacuna inválido")
        self._put_versioned(db, "observer:coverage", {"version": 1, "collector_epoch": epoch,
                            "continuity": uuid4().hex, "gap_at": now, "reason": reason, "complete": False,
                            "connected": reason == "reconexão do fluxo"})

    def observation_gap(self, epoch, reason, now=None):
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                self._check_collector(db, epoch)
                self._gap(db, epoch, reason, now or utc_now().isoformat())
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def append_runtime_fact(self, fact, epoch):
        from .observations import MAX_FACTS, normalize
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                self._check_collector(db, epoch)
                bindings = {row[0]: json.loads(row[1]) for row in db.execute("SELECT key,payload FROM local WHERE key LIKE 'binding:%'")}
                fact = normalize(json.dumps(fact).encode(), fact["context"], bindings, epoch)
                if fact is None:
                    return False
                rows = list(db.execute("SELECT key,payload FROM local WHERE key LIKE 'runtime-event:%' ORDER BY rowid"))
                cutoff = utc_now() - timedelta(days=7)
                retained = []
                for key, payload in rows:
                    value = json.loads(payload)
                    # Nunca remover versão desconhecida nem operação canônica.
                    known = isinstance(value, dict) and value.get("version") == 1
                    at = parse_time(value.get("received_at")) if known else None
                    if known and value.get("consumed") is True and at and at < cutoff:
                        db.execute("DELETE FROM local WHERE key=?", (key,))
                    else:
                        retained.append((key, value, known))
                key = "runtime-event:" + fact["event_id"]
                if any(row[0] == key for row in retained):
                    return False
                if len(retained) >= MAX_FACTS:
                    self._gap(db, epoch, "saturação de fatos", utc_now().isoformat())
                    removable = next((r for r in retained if r[2]), None)
                    if not removable:
                        return False
                    db.execute("DELETE FROM local WHERE key=?", (removable[0],))
                    # Dados antigos acima do limite não são apagados em massa.
                    if len(retained) > MAX_FACTS:
                        return False
                coverage = db.execute("SELECT payload FROM local WHERE key='observer:coverage'").fetchone()
                if coverage:
                    value = json.loads(coverage[0])
                    if not isinstance(value, dict) or value.get("version") != 1 or value.get("collector_epoch") != epoch:
                        raise MonitorError("cobertura de observação incompatível")
                    fact["continuity"] = value["continuity"]
                self._put_versioned(db, key, fact)
                return True
        except (sqlite3.Error, ValueError, KeyError, TypeError):
            raise MonitorError("armazenamento de observação indisponível") from None

    def runtime_facts(self):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute("SELECT payload FROM local WHERE key LIKE 'runtime-event:%' ORDER BY rowid")]

    def request_states(self):
        with self.connect() as db:
            values = [json.loads(row[0]) for row in db.execute("SELECT payload FROM local WHERE key LIKE 'observer:requests:%'")]
        return [value for value in values if isinstance(value, dict) and value.get("version") == 1 and value.get("identity")]

    def consume_runtime_facts(self, event_ids):
        from .common import identifier
        keys = ["runtime-event:" + identifier(value) for value in event_ids]
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                for key in keys:
                    row = db.execute("SELECT payload FROM local WHERE key=?", (key,)).fetchone()
                    if row:
                        value = json.loads(row[0])
                        if not isinstance(value, dict) or value.get("version") != 1:
                            raise MonitorError("fato de observação incompatível")
                        value["consumed"] = True
                        self._put_versioned(db, key, value)
        except sqlite3.Error:
            raise MonitorError("armazenamento de observação indisponível") from None

    @staticmethod
    def observation_key(binding_key, kind="signal"):
        return "observer:" + kind + ":" + hashlib.sha256(binding_key.encode()).hexdigest()

    def project_runtime_fact(self, fact, epoch):
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                self._check_collector(db, epoch)
                key = fact["binding_key"]
                row = db.execute("SELECT payload FROM local WHERE key=?", (key,)).fetchone()
                binding = json.loads(row[0]) if row else {}
                if binding.get("revision") != fact["binding_revision"] or binding.get("invalidated"):
                    return False
                event_key = "runtime-event:" + fact["event_id"]
                row = db.execute("SELECT payload FROM local WHERE key=?", (event_key,)).fetchone()
                if not row:
                    return False
                saved = json.loads(row[0])
                if saved.get("version") != 1 or saved.get("collector_epoch") != epoch or saved.get("binding_revision") != binding["revision"]:
                    return False
                from .requests import event
                coverage_row = db.execute("SELECT payload FROM local WHERE key='observer:coverage'").fetchone()
                coverage = json.loads(coverage_row[0]) if coverage_row else {}
                requests_key = self.observation_key(key, "requests")
                requests_row = db.execute("SELECT payload FROM local WHERE key=?", (requests_key,)).fetchone()
                requests = json.loads(requests_row[0]) if requests_row else None
                state = event(requests, saved, epoch, coverage)
                state.update(binding_key=key, identity={k: binding.get(k) for k in
                             ("repository", "issue", "run_id", "stage", "worker_id", "execution")})
                self._put_versioned(db, requests_key, state)
                signal = {k: saved[k] for k in ("version", "type", "created", "received_at", "binding_revision", "collector_epoch")}
                cache_key = self.observation_key(key)
                previous = db.execute("SELECT payload FROM local WHERE key=?", (cache_key,)).fetchone()
                old = json.loads(previous[0]) if previous else None
                if old is not None and (not isinstance(old, dict) or old.get("version") != 1):
                    raise MonitorError("sinal de observação incompatível")
                if old is None or old.get("created", -1) <= saved["created"]:
                    self._put_versioned(db, cache_key, signal)
                saved["projected"] = True
                self._put_versioned(db, event_key, saved)
                return True
        except sqlite3.Error:
            raise MonitorError("armazenamento de observação indisponível") from None

    def begin(self, key, now=None, epoch=None):
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                self._check_collector(db, epoch)
                db.execute("INSERT OR IGNORE INTO sources(key) VALUES (?)", (key,))
                db.execute("UPDATE sources SET generation=generation+1, attempted_at=? WHERE key=?", (now or iso_time(), key))
                return db.execute("SELECT generation FROM sources WHERE key=?", (key,)).fetchone()[0]
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def publish(self, key, generation, payload, now=None, epoch=None):
        observed = now or iso_time()
        if key.startswith("comments:"):
            times = [event.get("last_seen_at") or event.get("at") for snapshot in payload for event in snapshot["record"]["events"]]
            observed = max((at for at in times if parse_time(at)), key=parse_time, default=None)
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                self._check_collector(db, epoch)
                if key == "runtime":
                    # Bind/unbind and publication share the write transaction:
                    # an in-flight result must still belong to this revision.
                    bindings = {row[0]: json.loads(row[1]) for row in db.execute(
                        "SELECT key,payload FROM local WHERE key LIKE 'binding:%'")}
                    payload = {identity: item for identity, item in payload.items()
                               if item.get("binding_revision") and
                               item["binding_revision"] == bindings.get(identity, {}).get("revision")}
                    observed = max((item["at"] for item in payload.values() if parse_time(item.get("at"))), key=parse_time, default=None)
                encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True)
                result = db.execute("""UPDATE sources SET accepted=?, payload=?, fetched_at=?, observed_at=?,
                    error=NULL, retry_at=NULL, failures=0 WHERE key=? AND generation=?""",
                                    (generation, encoded, now or iso_time(), observed, key, generation))
                if epoch and result.rowcount:
                    self._put_versioned(db, "collector:source:" + hashlib.sha256(key.encode()).hexdigest(),
                                        {"version": 1, "collector_epoch": epoch})
                if key == "runtime" and result.rowcount:
                    for identity, observation in payload.items():
                        if epoch and observation.get("state") in {"active", "inactive"} and "requests" in observation:
                            self._request_snapshot(db, identity, observation, epoch)
                        if observation.get("state") in {"incompatible", "context_changed"}:
                            row = db.execute("SELECT payload FROM local WHERE key=?", (identity,)).fetchone()
                            if row:
                                binding = json.loads(row[0])
                                binding["invalidated"] = observation["state"]
                                db.execute("UPDATE local SET payload=? WHERE key=?", (json.dumps(binding), identity))
                return bool(result.rowcount)
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def _request_snapshot(self, db, identity, sample, epoch):
        from .requests import snapshot
        row = db.execute("SELECT payload FROM local WHERE key='observer:coverage'").fetchone()
        coverage = json.loads(row[0]) if row else {}
        if coverage and (not isinstance(coverage, dict) or coverage.get("version") != 1):
            raise MonitorError("cobertura de observação incompatível")
        started, gap_at = parse_time(sample.get("query_started_at")), parse_time(coverage.get("gap_at"))
        if (coverage.get("collector_epoch") == epoch and coverage.get("connected") and not coverage.get("complete")
                and started and gap_at and started >= gap_at):
            coverage.update(complete=True, reconciled_at=sample["at"])
            self._put_versioned(db, "observer:coverage", coverage)
        key = self.observation_key(identity, "requests")
        previous = db.execute("SELECT payload FROM local WHERE key=?", (key,)).fetchone()
        value = snapshot(json.loads(previous[0]) if previous else None, sample, epoch, coverage)
        binding_row = db.execute("SELECT payload FROM local WHERE key=?", (identity,)).fetchone()
        binding = json.loads(binding_row[0]) if binding_row else {}
        value.update(binding_key=identity, identity={key: binding.get(key) for key in
                     ("repository", "issue", "run_id", "stage", "worker_id", "execution")})
        self._put_versioned(db, key, value)

    def fail(self, key, generation, error, retry_at, epoch=None):
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                self._check_collector(db, epoch)
                db.execute("UPDATE sources SET error=?, retry_at=?, failures=failures+1 WHERE key=? AND generation=?",
                           (error.category, retry_at, key, generation))
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def source(self, key):
        try:
            with self.connect() as db:
                row = db.execute("SELECT * FROM sources WHERE key=?", (key,)).fetchone()
                metadata = db.execute("SELECT payload FROM local WHERE key=?",
                                      ("collector:source:" + hashlib.sha256(key.encode()).hexdigest(),)).fetchone()
            result = dict(row) if row else {"key": key}
            if metadata:
                value = json.loads(metadata[0])
                if isinstance(value, dict) and value.get("version") == 1:
                    result["collector_epoch"] = value.get("collector_epoch")
            result["payload"] = json.loads(result["payload"]) if result.get("payload") else None
            return result
        except (sqlite3.Error, ValueError):
            raise MonitorError("armazenamento ilegível") from None

    def sources(self, prefix):
        with self.connect() as db:
            keys = [row[0] for row in db.execute("SELECT key FROM sources ORDER BY key") if row[0].startswith(prefix)]
        return [self.source(key) for key in keys]

    def local(self, key, default=None):
        with self.connect() as db:
            row = db.execute("SELECT payload FROM local WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def put_local(self, key, value):
        try:
            with self.connect() as db:
                db.execute("INSERT INTO local VALUES (?,?) ON CONFLICT(key) DO UPDATE SET payload=excluded.payload",
                           (key, json.dumps(value, sort_keys=True)))
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def pending_workflow(self):
        with self.connect() as db:
            values = [json.loads(row[0]) for row in db.execute("SELECT payload FROM local WHERE key LIKE 'workflow-operation:%'")]
        return [{key: value.get(key) for key in ("operation_id", "repository", "issue", "run_id", "state", "binding_state")}
                for value in values if isinstance(value, dict) and value.get("version") == 1 and
                (value.get("state") in {"pending", "conflict"} or value.get("binding_state") in {"pending", "failed"})]

    def bind(self, key, value, guards=()):
        """Uma sessão não pode confirmar duas incarnações locais simultaneamente."""
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                for source_key, accepted in guards:
                    row = db.execute("SELECT accepted FROM sources WHERE key=?", (source_key,)).fetchone()
                    if not row or row[0] != accepted:
                        raise MonitorError("cache mudou durante bind; tente novamente")
                for row in db.execute("SELECT key,payload FROM local WHERE key LIKE 'binding:%'"):
                    other = json.loads(row[1])
                    if row[0] != key and other["session_id"] == value["session_id"] and other["context"] == value["context"]:
                        raise MonitorError("sessão já vinculada; remova o vínculo anterior")
                # Fresh even for an identical rebind or unbind/rebind (ABA).
                previous = db.execute("SELECT payload FROM local WHERE key=?", (self.observation_key(key, "requests"),)).fetchone()
                if previous:
                    state = json.loads(previous[0])
                    if isinstance(state, dict) and state.get("version") == 1 and state.get("binding_revision"):
                        self._put_versioned(db, self.observation_key(key, "requests") + ":" + state["binding_revision"], state)
                value = {**value, "revision": uuid4().hex}
                db.execute("INSERT INTO local VALUES (?,?) ON CONFLICT(key) DO UPDATE SET payload=excluded.payload", (key, json.dumps(value)))
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def bindings(self):
        with self.connect() as db:
            return {row[0]: json.loads(row[1]) for row in db.execute("SELECT key,payload FROM local WHERE key LIKE 'binding:%'")}

    def unbind(self, key):
        with self.connect() as db:
            db.execute("DELETE FROM local WHERE key=?", (key,))
