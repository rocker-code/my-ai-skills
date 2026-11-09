"""Aceitação durável, idempotência e limites sem qualquer chamada remota."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from milestone_monitor_fixtures import ROOT
from milestone_monitor.common import MonitorError, iso_time
from milestone_monitor.journal import Journal
from milestone_monitor.store import Store


def operation(operation_id="op-start", **extra):
    return {"version": 1, "operation_id": operation_id, "event": "run-start", "issue": "https://github.com/owner/repo/issues/7",
            "run_id": "wf-fixture", "worker_id": "orchestrator", "at": "2026-11-08T00:00:00Z", "coordinator": True, **extra}


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        self.journal = Journal(self.store)

    def test_same_operation_replays_and_other_payload_cannot_replace(self):
        with patch("workflow_events.gh", side_effect=AssertionError("rede sob aceitação")):
            first = self.journal.accept(operation())
            self.assertEqual(self.journal.accept(operation()), first)
        self.assertEqual(first["state"], "pending")
        self.assertEqual(first["binding_state"], "not_requested")
        with self.assertRaisesRegex(MonitorError, "outro payload"):
            self.journal.accept(operation(at="2026-11-08T00:01:00Z"))
        self.assertEqual(self.journal.get("op-start"), first)

    def test_dependencies_are_scoped_and_bind_state_is_independent(self):
        self.journal.accept(operation())
        payload = operation("op-dispatch", event="dispatch", stage="apply", worker_id="worker-A",
                            execution={"kind": "worker", "id": "execution-A"}, depends_on=["op-start"],
                            binding={"worktree": "/fixture/worktree"})
        self.assertEqual(self.journal.accept(payload)["binding_state"], "pending")
        updated = self.journal.update("op-dispatch", state="published", binding_state="failed", error="vínculo indisponível")
        self.assertEqual(updated["state"], "published")
        self.assertEqual(updated["binding_state"], "failed")
        self.assertEqual(self.journal.accept(payload), updated)
        with self.assertRaises(MonitorError):
            self.journal.update("op-dispatch", state="pending")
        with self.assertRaises(MonitorError):
            self.journal.accept(operation("other", issue="https://github.com/owner/repo/issues/8", depends_on=["op-start"]))

    def test_full_outbox_rejects_new_but_never_discards_or_rejects_replay(self):
        first = self.journal.accept(operation())
        with self.store.connect() as db:
            for index in range(999):
                value = {**first, "operation_id": f"op-{index}"}
                db.execute("INSERT INTO local VALUES (?,?)", (f"workflow-operation:op-{index}", json.dumps(value)))
        with self.assertRaisesRegex(MonitorError, "outbox cheia"):
            self.journal.accept(operation("new"))
        self.assertEqual(len(self.journal.operations("owner/repo", 7, "wf-fixture")), 1000)
        self.assertEqual(self.journal.accept(operation()), first)

    def test_disk_full_no_false_acceptance_and_existing_operation_preserved(self):
        first = self.journal.accept(operation())
        with self.store.connect() as db:
            db.execute("CREATE TRIGGER full BEFORE INSERT ON local BEGIN SELECT RAISE(ABORT,'disk full'); END")
        with self.assertRaises(MonitorError):
            self.journal.accept(operation("second"))
        self.assertIsNone(self.journal.get("second"))
        self.assertEqual(self.journal.get("op-start"), first)

    def test_process_crash_before_and_after_local_acceptance(self):
        script = '''import sys,os,json
sys.path.insert(0,sys.argv[1])
from milestone_monitor.store import Store
from milestone_monitor.journal import Journal
s=Store(sys.argv[2]);Journal(s).accept(json.loads(sys.argv[3]));os._exit(0)
'''
        subprocess.run([sys.executable, "-B", "-c", script, str(ROOT / "scripts"), self.temp.name, json.dumps(operation())], check=True)
        self.assertEqual(Journal(Store(self.temp.name)).get("op-start")["state"], "pending")
        script = '''import sqlite3,sys,os
db=sqlite3.connect(sys.argv[1]);db.execute('BEGIN IMMEDIATE')
db.execute("INSERT INTO local VALUES ('workflow-operation:uncommitted','{}')")
os._exit(0)
'''
        subprocess.run([sys.executable, "-c", script, str(self.store.path)], check=True)
        self.assertIsNone(self.journal.get("uncommitted"))
        self.assertIsNotNone(self.journal.get("op-start"))
