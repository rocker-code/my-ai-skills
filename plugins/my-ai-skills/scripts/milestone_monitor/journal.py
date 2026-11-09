"""Outbox local durável; nenhuma chamada remota ocorre em transação SQLite."""
import hashlib
import json
import sqlite3

from .common import MonitorError, identifier, iso_time, issue_identity
from .workflow import normalize_operation


class Journal:
    def __init__(self, store):
        self.store = store

    @staticmethod
    def key(operation_id):
        return "workflow-operation:" + identifier(operation_id)

    @staticmethod
    def decode(raw):
        value = json.loads(raw)
        if not isinstance(value, dict) or value.get("version") != 1:
            raise MonitorError("versão de operação incompatível")
        return value

    def accept(self, payload):
        payload = normalize_operation(payload)
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        digest = hashlib.sha256(encoded.encode()).hexdigest()
        repository, issue = issue_identity(payload["issue"])
        key = self.key(payload["operation_id"])
        try:
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                previous = db.execute("SELECT payload FROM local WHERE key=?", (key,)).fetchone()
                if previous:
                    value = self.decode(previous[0])
                    if value["hash"] != digest:
                        raise MonitorError("operation_id reutilizado com outro payload")
                    return value
                existing = [self.decode(row[0]) for row in db.execute("SELECT payload FROM local WHERE key LIKE 'workflow-operation:%'")]
                pending = [op for op in existing if op["state"] != "published" or op.get("binding_state") in {"pending", "failed"}]
                if len(pending) >= 1000:
                    raise MonitorError("outbox cheia; operação não aceita")
                by_id = {op["operation_id"]: op for op in existing}
                for dependency in payload["depends_on"]:
                    op = by_id.get(dependency)
                    if not op or (op["repository"], op["issue"], op["run_id"]) != (repository, issue, payload["run_id"]):
                        raise MonitorError("dependência ausente ou fora do escopo")
                value = {"version": 1, "operation_id": payload["operation_id"], "hash": digest, "payload": payload,
                         "repository": repository, "issue": issue, "run_id": payload["run_id"], "depends_on": payload["depends_on"],
                         "accepted_at": iso_time(), "state": "pending", "binding_state": "pending" if payload.get("binding") else "not_requested"}
                self.store._put_versioned(db, key, value)
                return value
        except sqlite3.Error:
            raise MonitorError("operação não aceita; armazenamento indisponível") from None

    def get(self, operation_id):
        value = self.store.local(self.key(operation_id))
        return self.decode(json.dumps(value)) if value is not None else None

    def operations(self, repository, issue, run_id):
        with self.store.connect() as db:
            values = [self.decode(row[0]) for row in db.execute("SELECT payload FROM local WHERE key LIKE 'workflow-operation:%' ORDER BY rowid")]
        return [op for op in values if (op["repository"], op["issue"], op["run_id"]) == (repository, issue, run_id)]

    def accept_binding(self, operation_id, session_id):
        identifier(session_id)
        if not session_id.startswith("ses"):
            raise MonitorError("sessão executora inválida")
        try:
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT payload FROM local WHERE key=?", (self.key(operation_id),)).fetchone()
                if not row:
                    raise MonitorError("operação ausente")
                operation = self.decode(row[0])
                binding = operation["payload"].get("binding")
                if not binding or binding.get("session_id") not in {None, session_id}:
                    raise MonitorError("vínculo fora da intenção de abertura")
                value = {"version": 1, "operation_id": operation_id, "operation_hash": operation["hash"], "session_id": session_id}
                key = "workflow-binding:" + operation_id
                previous = db.execute("SELECT payload FROM local WHERE key=?", (key,)).fetchone()
                if previous and self.decode(previous[0]) != value:
                    raise MonitorError("intenção de vínculo já registrada com outros dados")
                self.store._put_versioned(db, key, value)
                return value
        except sqlite3.Error:
            raise MonitorError("intenção de vínculo não aceita; armazenamento indisponível") from None

    def binding_intent(self, operation):
        value = self.store.local("workflow-binding:" + operation["operation_id"])
        if value is not None:
            value = self.decode(json.dumps(value))
            if value.get("operation_hash") != operation["hash"]:
                raise MonitorError("intenção de vínculo incompatível")
        return value

    def update(self, operation_id, *, state=None, binding_state=None, binding_reason=None, comment_id=None, error=None):
        if state not in {None, "pending", "published", "conflict"} or binding_state not in {None, "pending", "bound", "failed", "not_requested"}:
            raise MonitorError("estado de operação inválido")
        if error not in {None, "publicação indisponível", "registro conflitante", "vínculo indisponível", "dependência pendente"}:
            raise MonitorError("diagnóstico de operação inválido")
        if binding_reason not in {None, "session_unavailable", "runtime_disabled", "cache_pending", "conflict", "validation_failed", "bound"}:
            raise MonitorError("diagnóstico de vínculo inválido")
        try:
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT payload FROM local WHERE key=?", (self.key(operation_id),)).fetchone()
                if not row:
                    raise MonitorError("operação ausente")
                value = self.decode(row[0])
                if value["state"] == "published" and state not in {None, "published"}:
                    raise MonitorError("publicação confirmada não pode ser revertida")
                if state is not None:
                    value["state"] = state
                if binding_state is not None:
                    value["binding_state"] = binding_state
                if binding_reason is not None:
                    value["binding_reason"] = binding_reason
                if comment_id is not None:
                    if type(comment_id) is not int or comment_id <= 0:
                        raise MonitorError("comentário inválido")
                    value["comment_id"] = comment_id
                value.update(error=error, updated_at=iso_time())
                self.store._put_versioned(db, self.key(operation_id), value)
                return value
        except sqlite3.Error:
            raise MonitorError("estado de operação não confirmado; armazenamento indisponível") from None
