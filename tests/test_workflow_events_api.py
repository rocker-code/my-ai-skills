"""API pura compartilhada com CLI manual; não utiliza rede/estado real."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import workflow_events as events
from workflow_metrics import summarize_run


class EventAPITests(unittest.TestCase):
    def test_read_comments_supports_paginated_output_without_slurp(self):
        pages = '[{"id": 1, "body": "first"}]\n[{"id": 2, "body": "second"}]\n'
        with patch.object(events, "gh", return_value=pages) as gh:
            self.assertEqual(events.read_comments("owner/repo", 1), [
                {"id": 1, "body": "first"}, {"id": 2, "body": "second"}])
        gh.assert_called_once_with("api", "--paginate", "repos/owner/repo/issues/1/comments")

    def args(self, event, *extra):
        return events.parse_options([event, "--issue", "https://github.com/owner/repo/issues/1", "--run-id", "wf-api", *extra])

    def test_run_start_uses_validated_effective_time_and_never_calls_network(self):
        now = datetime(2026, 11, 8, 12, tzinfo=timezone.utc)
        args = self.args("run-start", "--observed-at", "2026-11-08T11:00:00Z")
        with patch.object(events, "gh", side_effect=AssertionError("rede proibida")):
            record, comment_id, result = events.build_record(args, [], now)
        self.assertIsNone(comment_id)
        self.assertEqual(record["created_at"], "2026-11-08T11:00:00Z")
        self.assertEqual(record["events"][0]["at"], record["created_at"])
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(result["event"], "run_started")
        for value in ("2099-01-01T00:00:00Z", "2026-11-08T11:00:00", "inválido"):
            args.observed_at = value
            with self.assertRaises(ValueError):
                events.build_record(args, [], now)

    def test_typed_transition_and_legacy_metrics_use_same_builder(self):
        now = datetime(2026, 11, 8, 12, tzinfo=timezone.utc)
        record, _, _ = events.build_record(self.args("run-start", "--observed-at", "2026-11-08T11:00:00Z"), [], now)
        comments = [{"id": 1, "body": events.comment_body(record)}]
        pair = ("--stage", "apply", "--worker-id", "worker-A", "--execution-kind", "worker", "--execution-id", "execution-A")
        record, cid, _ = events.build_record(self.args("dispatch", *pair, "--observed-at", "2026-11-08T11:01:00Z"), comments, now)
        self.assertEqual(cid, 1)
        comments = [{"id": 1, "body": events.comment_body(record)}]
        args = self.args("stage-end", *pair, "--status", "completed", "--observed-at", "2026-11-08T11:02:00Z")
        record, _, _ = events.build_record(args, comments, now)
        self.assertEqual(summarize_run(record, now)["recorded_work_seconds"], 60)
        args.execution_id = "wrong"
        with self.assertRaises(ValueError):
            events.build_record(args, comments, now)

    def test_shared_validation_cannot_bypass_parser_choices_or_worker_identity(self):
        args = self.args("run-start")
        for field, value in (("worker_id", "bad worker"), ("scope", "invalid"), ("event", "invalid")):
            invalid = copy.copy(args)
            setattr(invalid, field, value)
            with self.assertRaises(ValueError):
                events.build_record(invalid, [])
