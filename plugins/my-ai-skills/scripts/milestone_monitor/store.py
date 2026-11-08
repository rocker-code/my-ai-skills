"""Snapshots SQLite transacionais; rede nunca ocorre dentro da transação."""
import json
import os
import sqlite3
from pathlib import Path

from .common import MonitorError, iso_time, parse_time


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


class Store:
    def __init__(self, directory):
        self.path = Path(directory) / "monitor.sqlite3"
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

    def begin(self, key, now=None):
        try:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute("INSERT OR IGNORE INTO sources(key) VALUES (?)", (key,))
                db.execute("UPDATE sources SET generation=generation+1, attempted_at=? WHERE key=?", (now or iso_time(), key))
                return db.execute("SELECT generation FROM sources WHERE key=?", (key,)).fetchone()[0]
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def publish(self, key, generation, payload, now=None):
        encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True)
        observed = now or iso_time()
        if key.startswith("comments:"):
            times = [event.get("last_seen_at") or event.get("at") for snapshot in payload for event in snapshot["record"]["events"]]
            observed = max((at for at in times if parse_time(at)), key=parse_time, default=None)
        elif key == "runtime":
            observed = max((item["at"] for item in payload.values() if parse_time(item.get("at"))), key=parse_time, default=None)
        try:
            with self.connect() as db:
                result = db.execute("""UPDATE sources SET accepted=?, payload=?, fetched_at=?, observed_at=?,
                    error=NULL, retry_at=NULL, failures=0 WHERE key=? AND generation=?""",
                                    (generation, encoded, now or iso_time(), observed, key, generation))
                if key == "runtime" and result.rowcount:
                    for identity, observation in payload.items():
                        if observation.get("state") in {"incompatible", "context_changed"}:
                            row = db.execute("SELECT payload FROM local WHERE key=?", (identity,)).fetchone()
                            if row:
                                binding = json.loads(row[0])
                                binding["invalidated"] = observation["state"]
                                db.execute("UPDATE local SET payload=? WHERE key=?", (json.dumps(binding), identity))
                return bool(result.rowcount)
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def fail(self, key, generation, error, retry_at):
        try:
            with self.connect() as db:
                db.execute("UPDATE sources SET error=?, retry_at=?, failures=failures+1 WHERE key=? AND generation=?",
                           (error.category, retry_at, key, generation))
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def source(self, key):
        try:
            with self.connect() as db:
                row = db.execute("SELECT * FROM sources WHERE key=?", (key,)).fetchone()
            result = dict(row) if row else {"key": key}
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
                db.execute("INSERT INTO local VALUES (?,?) ON CONFLICT(key) DO UPDATE SET payload=excluded.payload", (key, json.dumps(value)))
        except sqlite3.Error:
            raise MonitorError("armazenamento ocupado ou indisponível") from None

    def bindings(self):
        with self.connect() as db:
            return {row[0]: json.loads(row[1]) for row in db.execute("SELECT key,payload FROM local WHERE key LIKE 'binding:%'")}

    def unbind(self, key):
        with self.connect() as db:
            db.execute("DELETE FROM local WHERE key=?", (key,))
