"""Publicação fake com resposta perdida, deriva e concorrência cooperativa."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from milestone_monitor_fixtures import ROOT
from milestone_monitor.common import MonitorError
from milestone_monitor.journal import Journal
from milestone_monitor.publisher import Publisher, manual_register
from milestone_monitor.store import Store
from test_milestone_monitor_journal import operation
import workflow_events as events
from workflow_lock import PublicationLock
from workflow_metrics import summarize_run


class FakeGitHub:
    def __init__(self, store):
        self.store, self.comments, self.writes = store, [], 0
        self.lose_response = False
        self.read_hook = self.save_hook = None

    def outside_transaction(self):
        # Falha caso o publicador mantenha uma transação SQLite durante rede.
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.rollback()

    def read(self, repository, issue):
        self.outside_transaction()
        if self.read_hook:
            self.read_hook()
        return copy.deepcopy([comment for comment in self.comments
                              if comment.get("resource_repository", repository) == repository and comment.get("resource_issue", issue) == issue])

    def save(self, repository, issue, record, comment_id):
        self.outside_transaction()
        if self.save_hook:
            self.save_hook()
        body = events.comment_body(record)
        if comment_id is None:
            self.comments.append({"id": len(self.comments) + 1, "body": body, "resource_repository": repository, "resource_issue": issue})
        else:
            next(c for c in self.comments if c["id"] == comment_id)["body"] = body
        self.writes += 1
        if self.lose_response:
            self.lose_response = False
            raise RuntimeError("SEGREDO_FIXTURE resposta perdida")


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        self.journal = Journal(self.store)
        self.github = FakeGitHub(self.store)
        self.publisher = Publisher(self.journal, self.github.read, self.github.save)

    def publish(self, payload):
        self.journal.accept(payload)
        return self.publisher.publish(payload["operation_id"])

    def start(self):
        return self.publish(operation())

    def record(self):
        return events.parse_run_comment(self.github.comments[0]["body"])

    def dispatch(self, operation_id="op-dispatch", **extra):
        return operation(operation_id, event="dispatch", stage="apply", worker_id="worker-A",
                         execution={"kind": "worker", "id": "execution-A"}, depends_on=["op-start"],
                         at="2026-11-08T00:01:00Z", **extra)

    def test_lost_response_after_save_retries_without_duplicate_events_or_evidence(self):
        self.github.lose_response = True
        self.assertEqual(self.start()["state"], "pending")
        self.assertEqual(self.github.writes, 1)
        self.assertEqual(self.publisher.publish("op-start")["state"], "published")
        self.assertEqual(self.github.writes, 1)
        self.assertEqual(len(self.record()["events"]), 1)
        payload = self.dispatch(evidence=["abcdef0"])
        self.github.lose_response = True
        self.assertEqual(self.publish(payload)["state"], "pending")
        self.assertEqual(self.publisher.publish("op-dispatch")["state"], "published")
        self.assertEqual(self.record()["evidence"], ["abcdef0"])
        self.assertEqual(len(self.record()["events"]), 2)
        self.assertNotIn("SEGREDO_FIXTURE", json.dumps(self.journal.get("op-dispatch")))

    def test_duplicate_comment_or_unexpected_drift_causes_conflict_without_write(self):
        self.start()
        original = copy.deepcopy(self.github.comments)
        self.github.comments.append({**original[0], "id": 2})
        self.assertEqual(self.publish(self.dispatch())["state"], "conflict")
        self.assertEqual(self.github.writes, 1)
        self.github.comments = original
        self.github.comments[0]["body"] = "Alteração externa\n" + self.github.comments[0]["body"]
        self.assertEqual(self.publish(self.dispatch("op-other"))["state"], "conflict")
        self.assertTrue(self.github.comments[0]["body"].startswith("Alteração externa"))

    def test_drift_between_first_and_final_read_is_detected(self):
        self.start()
        reads = []
        def drift():
            reads.append(True)
            if len(reads) == 2:
                self.github.comments[0]["body"] += "\nAlteração externa"
        self.github.read_hook = drift
        self.assertEqual(self.publish(self.dispatch())["state"], "conflict")
        self.assertEqual(self.github.writes, 1)

    def test_operation_metadata_cannot_hide_changed_canonical_payload(self):
        self.start()
        self.publish(self.dispatch())
        changed = self.record()
        changed["events"][-1]["execution"]["id"] = "different"
        changed["events"][-1]["operation"]["event_hash"] = events.event_hash(changed["events"][-1])
        self.github.comments[0]["body"] = events.comment_body(changed)
        key = self.publisher.baseline_key("owner/repo", 7, "wf-fixture")
        self.publisher.checkpoint(key, self.github.comments[0])
        with self.assertRaisesRegex(MonitorError, "conflitante"):
            self.publisher.publish("op-dispatch")

    def test_causal_order_and_wait_duration_are_not_duplicated(self):
        self.journal.accept(operation())
        dispatch = self.dispatch()
        self.journal.accept(dispatch)
        self.assertEqual(self.publisher.publish("op-dispatch")["state"], "pending")
        self.assertEqual(self.github.writes, 0)
        self.publisher.publish("op-start")
        self.publisher.publish("op-dispatch")
        previous = "op-dispatch"
        for name, event, at, fields in (("wait-A", "wait-start", "00:02:00", {"reason": "owner_input"}),
                                         ("wait-B", "wait-end", "00:04:00", {"reason": "owner_input"}),
                                         ("end", "stage-end", "00:05:00", {"status": "completed"})):
            payload = {**dispatch, "operation_id": name, "event": event, "at": "2026-11-08T" + at + "Z",
                       "depends_on": [previous], **fields}
            self.publish(payload)
            self.publisher.publish(name)
            previous = name
        self.assertEqual(len(self.record()["events"]), 5)
        self.assertEqual(summarize_run(self.record())["wait_seconds_by_reason"], {"owner_input": 120})

    def test_manual_and_structured_paths_share_lock_and_baseline(self):
        self.start()
        self.journal.accept(self.dispatch())
        with PublicationLock(self.temp.name, "owner/repo", 7, "wf-fixture"):
            with self.assertRaisesRegex(MonitorError, "concorrente"):
                self.publisher.publish("op-dispatch")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/workflow-event"), "stage-start",
                                     "--issue", "https://github.com/owner/repo/issues/7", "--run-id", "wf-fixture",
                                     "--stage", "explore", "--state-dir", self.temp.name],
                                    env={**os.environ, "PATH": "/caminho-inexistente"}, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("concorrente", result.stderr)
        with patch.object(events, "read_comments", self.github.read), patch.object(events, "save_record", self.github.save):
            args = events.parse_options(["stage-start", "--issue", "https://github.com/owner/repo/issues/7", "--run-id", "wf-fixture",
                                         "--stage", "explore", "--state-dir", self.temp.name])
            manual_register(args)
        self.assertEqual(self.publisher.publish("op-dispatch")["state"], "published")

    def test_known_noncooperative_window_after_last_read_has_no_cas_guarantee(self):
        self.start()
        external = []
        def noncooperative():
            # Apenas fake: documenta a janela inevitável, não um gate aprovado.
            self.github.comments[0]["body"] += "\nEscrita externa após última leitura"
            external.append(True)
        self.github.save_hook = noncooperative
        self.publish(self.dispatch())
        self.assertEqual(external, [True])
        self.assertNotIn("Escrita externa", self.github.comments[0]["body"])
