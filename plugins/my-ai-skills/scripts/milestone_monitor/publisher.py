"""Publicação exclusiva do coordenador; nenhuma rede sob transação SQLite."""
import copy
import hashlib
import json
import sqlite3

import workflow_events as events
from workflow_lock import PublicationLock, domain
from workflow_waits import build_wait_record
from .common import MonitorError
from .config import state_path
from .store import Store
from .workflow import options


def body_hash(body):
    return hashlib.sha256(body.encode()).hexdigest() if body is not None else None


class Publisher:
    def __init__(self, journal, read=None, save=None):
        self.journal, self.store = journal, journal.store
        self.read = read or events.read_comments
        self.save = save or events.save_record

    def current(self, repository, issue, run_id):
        try:
            comments = self.read(repository, issue)
        except (OSError, RuntimeError, ValueError, TypeError):
            raise MonitorError("publicação indisponível") from None
        matches = [(item, events.parse_run_comment(item.get("body", ""))) for item in comments]
        matches = [(item, value) for item, value in matches if value and value.get("run_id") == run_id]
        if len(matches) > 1:
            raise MonitorError("registro conflitante")
        if not matches:
            return comments, None, None
        comment, record = matches[0]
        if (record.get("schema_version") != 1 or record.get("repository") not in {None, repository} or
                record.get("issue", {}).get("number") not in {None, issue} or
                record.get("issue", {}).get("url") not in {None, f"https://github.com/{repository}/issues/{issue}"}):
            raise MonitorError("registro conflitante")
        return comments, comment, record

    def baseline_key(self, repository, issue, run_id):
        return "workflow-pending:" + domain(repository, issue, run_id)

    def check_baseline(self, key, comment):
        baseline = self.store.local(key)
        if baseline is not None:
            if not isinstance(baseline, dict) or baseline.get("version") != 1:
                raise MonitorError("registro conflitante")
            actual = body_hash(comment["body"] if comment else None)
            if actual not in {baseline.get("base_hash"), baseline.get("expected_hash")}:
                raise MonitorError("registro conflitante")
            if baseline.get("comment_id") and (not comment or comment["id"] != baseline["comment_id"]):
                raise MonitorError("registro conflitante")

    def checkpoint(self, key, comment, expected=None, operation_id=None):
        value = {"version": 1, "base_hash": body_hash(comment["body"] if comment else None),
                 "comment_id": comment["id"] if comment else None, "expected_hash": body_hash(expected),
                 "operation_id": operation_id}
        try:
            with self.store.connect() as db:
                self.store._put_versioned(db, key, value)
        except sqlite3.Error:
            raise MonitorError("armazenamento de publicação indisponível") from None

    def verify_operation(self, operation, record):
        matches = [(index, event) for index, event in enumerate(record["events"])
                   if isinstance(event.get("operation"), dict) and
                   (event["operation"].get("id") == operation["operation_id"] or event["operation"].get("operation_id") == operation["operation_id"])]
        if not matches:
            return False
        expected_count = 2 * len(operation["payload"]["intervals"]) if operation["payload"]["event"] == "wait-intervals" else 1
        if len(matches) != expected_count:
            raise MonitorError("registro conflitante")
        for _index, event in matches:
            metadata = event["operation"]
            if metadata.get("hash") != operation["hash"] or metadata.get("event_hash") != events.event_hash(event):
                raise MonitorError("registro conflitante")
        payload = operation["payload"]
        prefix = copy.deepcopy(record)
        prefix.update(events=prefix["events"][:matches[0][0]], status="running", finished_at=None)
        comments = [] if payload["event"] == "run-start" else [{"id": 1, "body": events.comment_body(prefix)}]
        candidate, _, _ = self.build(operation, comments)
        expected = candidate["events"][-expected_count:]
        for (_, actual), wanted in zip(matches, expected):
            if events.event_hash(wanted) != actual["operation"]["event_hash"] or wanted["operation"]["id"] != actual["operation"]["id"]:
                raise MonitorError("registro conflitante")
        return True

    @staticmethod
    def build(operation, comments):
        metadata = {"id": operation["operation_id"], "hash": operation["hash"]}
        if operation["payload"]["event"] == "wait-intervals":
            return build_wait_record(options(operation["payload"]), comments, operation["payload"]["intervals"], metadata)
        return events.build_record(options(operation["payload"]), comments, operation=metadata)

    def write(self, repository, issue, run_id, comments, comment, record, key, operation_id=None):
        body = events.comment_body(record)
        if len(body.encode()) > 65536:
            raise MonitorError("publicação indisponível")
        # Releitura imediata reduz a janela de corrida; edição GitHub não oferece CAS.
        _, current, _ = self.current(repository, issue, run_id)
        if (body_hash(current["body"] if current else None) != body_hash(comment["body"] if comment else None)
                or (current or {}).get("id") != (comment or {}).get("id")):
            raise MonitorError("registro conflitante")
        self.checkpoint(key, comment, body, operation_id)
        try:
            self.save(repository, issue, record, comment["id"] if comment else None)
        except (OSError, RuntimeError, ValueError, TypeError):
            raise MonitorError("publicação indisponível") from None
        _, confirmed, _ = self.current(repository, issue, run_id)
        if not confirmed or body_hash(confirmed["body"]) != body_hash(body):
            raise MonitorError("registro conflitante")
        self.checkpoint(key, confirmed)
        return confirmed["id"]

    def publish(self, operation_id):
        operation = self.journal.get(operation_id)
        if not operation:
            raise MonitorError("operação ausente")
        repository, issue, run_id = operation["repository"], operation["issue"], operation["run_id"]
        try:
            with PublicationLock(self.store.path.parent, repository, issue, run_id):
                operation = self.journal.get(operation_id)
                if operation["state"] == "conflict":
                    return operation
                for dependency in operation["depends_on"]:
                    if self.journal.get(dependency)["state"] != "published":
                        return self.journal.update(operation_id, error="dependência pendente")
                key = self.baseline_key(repository, issue, run_id)
                comments, comment, record = self.current(repository, issue, run_id)
                self.check_baseline(key, comment)
                if record and self.verify_operation(operation, record):
                    self.checkpoint(key, comment)
                    return self.journal.update(operation_id, state="published", comment_id=comment["id"])
                if operation["state"] == "published":
                    raise MonitorError("registro conflitante")
                payload = operation["payload"]
                if payload["event"] in {"wait-start", "wait-end"} and (not record or not events.opening_for(
                        record, payload["stage"], payload["worker_id"], payload["execution"], payload["at"])):
                    raise MonitorError("registro conflitante")
                built, _, _ = self.build(operation, comments)
                comment_id = self.write(repository, issue, run_id, comments, comment, built, key, operation_id)
                return self.journal.update(operation_id, state="published", comment_id=comment_id)
        except MonitorError as error:
            if error.category == "registro conflitante":
                if operation["state"] == "published":
                    raise  # Nunca reverter uma confirmação já aceita no journal.
                return self.journal.update(operation_id, state="conflict", error="registro conflitante")
            if error.category == "publicação indisponível":
                return self.journal.update(operation_id, error="publicação indisponível")
            raise
        except (RuntimeError, ValueError) as error:
            # Lock ocupado ou fronteira canônica inválida: não sobrescrever nada.
            raise MonitorError("publicação concorrente ou fronteira inválida") from None


def manual_register(args):
    from .journal import Journal
    repository, issue = events.parse_issue_url(args.issue)
    store = Store(args.state_dir or state_path())
    publisher = Publisher(Journal(store))
    try:
        with PublicationLock(store.path.parent, repository, issue, args.run_id):
            key = publisher.baseline_key(repository, issue, args.run_id)
            comments, comment, _ = publisher.current(repository, issue, args.run_id)
            publisher.check_baseline(key, comment)
            record, _, result = events.build_record(args, comments)
            publisher.write(repository, issue, args.run_id, comments, comment, record, key)
            return result
    except RuntimeError:
        raise MonitorError("publicação concorrente no mesmo domínio") from None
