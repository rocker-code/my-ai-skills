import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from workflow_metrics import parse_run_comment, percentile, summarize_run


class WorkflowMetricsTest(unittest.TestCase):
    def test_parse_hidden_run_record(self):
        payload = {"schema_version": 1, "run_id": "wf-test", "events": []}
        body = (
            "Run summary\n<!-- my-ai-skills-workflow-run:v1 -->\n"
            "<!-- my-ai-skills-workflow-data:start -->\n"
            + json.dumps(payload)
            + "\n<!-- my-ai-skills-workflow-data:end -->"
        )
        self.assertEqual(parse_run_comment(body), payload)
        self.assertIsNone(parse_run_comment("ordinary issue comment"))

    def test_stage_work_excludes_explicit_wait_and_cycle_includes_it(self):
        record = {
            "schema_version": 1, "run_id": "wf-test", "repository": "owner/repo",
            "scope": "single_issue", "issue": {"number": 12, "url": "https://github.com/owner/repo/issues/12"},
            "status": "completed", "created_at": "2026-01-01T00:00:00Z",
            "finished_at": "2026-01-01T00:40:00Z",
            "events": [
                {"type": "run_started", "at": "2026-01-01T00:00:00Z"},
                {"type": "stage_started", "at": "2026-01-01T00:10:00Z", "stage": "apply", "worker_id": "worker-1"},
                {"type": "wait_started", "at": "2026-01-01T00:20:00Z", "stage": "apply", "worker_id": "worker-1", "reason": "ci"},
                {"type": "wait_finished", "at": "2026-01-01T00:30:00Z", "stage": "apply", "worker_id": "worker-1", "reason": "ci"},
                {"type": "stage_finished", "at": "2026-01-01T00:40:00Z", "stage": "apply", "worker_id": "worker-1"},
                {"type": "run_finished", "at": "2026-01-01T00:40:00Z"},
            ],
        }
        summary = summarize_run(record, datetime(2026, 1, 1, 1, tzinfo=timezone.utc))
        stage = summary["stages"][0]
        self.assertEqual(stage["elapsed_seconds"], 1800)
        self.assertEqual(stage["recorded_work_seconds"], 1200)
        self.assertEqual(stage["wait_seconds_by_reason"]["ci"], 600)
        self.assertEqual(summary["cycle_elapsed_seconds"], 2400)

    def test_parallel_workers_report_calendar_and_aggregated_work_separately(self):
        record = {
            "run_id": "wf-parallel", "created_at": "2026-01-01T00:00:00Z",
            "finished_at": "2026-01-01T00:40:00Z", "events": [
                {"type": "stage_started", "at": "2026-01-01T00:00:00Z", "stage": "apply", "worker_id": "a"},
                {"type": "stage_started", "at": "2026-01-01T00:10:00Z", "stage": "apply", "worker_id": "b"},
                {"type": "stage_finished", "at": "2026-01-01T00:30:00Z", "stage": "apply", "worker_id": "a"},
                {"type": "stage_finished", "at": "2026-01-01T00:40:00Z", "stage": "apply", "worker_id": "b"},
            ],
        }
        stage = summarize_run(record, datetime(2026, 1, 1, 1, tzinfo=timezone.utc))["stages"][0]
        self.assertEqual(stage["elapsed_seconds"], 2400)
        self.assertEqual(stage["recorded_work_seconds"], 3600)

    def test_open_stage_is_measured_until_report_time(self):
        record = {"run_id": "wf-open", "created_at": "2026-01-01T00:00:00Z", "events": [
            {"type": "stage_started", "at": "2026-01-01T00:00:00Z", "stage": "audit", "worker_id": "orchestrator"},
        ]}
        summary = summarize_run(record, datetime(2026, 1, 1, 0, 5, tzinfo=timezone.utc))
        self.assertEqual(summary["stages"][0]["elapsed_seconds"], 300)
        self.assertEqual(summary["stages"][0]["recorded_work_seconds"], 300)
        self.assertEqual(summary["status"], "running")

    def test_percentile_returns_none_for_empty_sample(self):
        self.assertIsNone(percentile([], 0.5))
        self.assertEqual(percentile([10, 20, 100], 0.5), 20)



    def test_event_cli_updates_one_github_comment_for_a_run(self):
        import os
        import subprocess
        import tempfile

        root = Path(__file__).resolve().parents[1]
        event_cli = root / "scripts" / "workflow-event"
        issue_url = "https://github.com/owner/repo/issues/42"
        fake_gh = """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
path = os.environ["FAKE_GH_STATE"]
try:
    state = json.load(open(path))
except FileNotFoundError:
    state = {"comments": [], "next_id": 1}
if args[0] == "api":
    method = "POST" if any(arg.startswith("body=") for arg in args) else "GET"
    if "--method" in args:
        method = args[args.index("--method") + 1]
    endpoint = next(arg for arg in args if arg.startswith("repos/"))
    body_arg = next((arg[5:] for arg in args if arg.startswith("body=")), None)
    if method == "GET" and "--paginate" in args:
        print(json.dumps([state["comments"]]))
    elif method == "POST":
        state["comments"].append({"id": state["next_id"], "body": body_arg})
        state["next_id"] += 1
        json.dump(state, open(path, "w"))
        print("{}")
    elif method == "PATCH":
        comment_id = int(endpoint.rsplit("/", 1)[1])
        for comment in state["comments"]:
            if comment["id"] == comment_id:
                comment["body"] = body_arg
        json.dump(state, open(path, "w"))
        print("{}")
elif args[0] == "issue":
    print(json.dumps({"number": 42, "title": "Metrics test", "state": "OPEN", "url": "https://github.com/owner/repo/issues/42"}))
elif args[0] == "pr":
    print("[]")
"""
        with tempfile.TemporaryDirectory() as temp:
            fake_bin = Path(temp) / "bin"
            fake_bin.mkdir()
            fake_path = fake_bin / "gh"
            fake_path.write_text(fake_gh)
            fake_path.chmod(0o755)
            state_path = Path(temp) / "state.json"
            env = dict(os.environ, PATH=f"{fake_bin}:{os.environ['PATH']}", FAKE_GH_STATE=str(state_path))

            def invoke(*args):
                return subprocess.run([str(event_cli), *args], env=env, text=True, capture_output=True, check=True)

            invoke("run-start", "--issue", issue_url, "--run-id", "wf-test", "--scope", "single_issue")
            invoke("stage-start", "--issue", issue_url, "--run-id", "wf-test", "--stage", "apply")
            invoke("wait-start", "--issue", issue_url, "--run-id", "wf-test", "--stage", "apply", "--reason", "ci")
            invoke("wait-end", "--issue", issue_url, "--run-id", "wf-test", "--stage", "apply", "--reason", "ci")
            invoke("stage-end", "--issue", issue_url, "--run-id", "wf-test", "--stage", "apply", "--status", "completed")
            invoke("rework", "--issue", issue_url, "--run-id", "wf-test", "--stage", "apply", "--reason", "review")
            invoke("run-end", "--issue", issue_url, "--run-id", "wf-test", "--status", "completed")

            state = json.loads(state_path.read_text())
            self.assertEqual(len(state["comments"]), 1)
            record = parse_run_comment(state["comments"][0]["body"])
            self.assertEqual(record["run_id"], "wf-test")
            self.assertEqual(record["status"], "completed")
            self.assertEqual(len(record["events"]), 7)
            self.assertEqual(summarize_run(record)["rework_count"], 1)
            report_result = subprocess.run(
                [str(root / "scripts" / "workflow-report"), issue_url, "--format", "json"],
                env=env, text=True, capture_output=True, check=True,
            )
            report = json.loads(report_result.stdout)
            self.assertEqual(report["tracked_issue_count"], 1)
            self.assertEqual(report["runs"][0]["rework_count"], 1)
            self.assertEqual(report["runs"][0]["stages"][0]["stage"], "apply")

if __name__ == "__main__":
    unittest.main()
