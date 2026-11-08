"""Fixtures mínimas artificiais; nunca sessões/dados privados reais."""
import copy
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from milestone_monitor.config import DEFAULTS
from milestone_monitor.ingest import comments_snapshot

NOW = datetime(2026, 11, 8, 12, 0, 30, tzinfo=timezone.utc)
STARTED = NOW - timedelta(seconds=30)
REPO = "owner/repo"
ISSUE = {"repository": REPO, "number": 7, "milestone": 1, "title": "Uma issue", "state": "open",
         "url": f"https://github.com/{REPO}/issues/7"}
CONFIG = {"schema_version": 1, "targets": [{"repository": REPO, "milestones": [1]}],
          "runtime": {"enabled": False, "expected_version": "2.2.5", "server": None}, "timing": DEFAULTS.copy()}
EXECUTION = {"kind": "worker", "id": "worker-a"}


def event(kind, second=0, **extra):
    return {"type": kind, "at": (STARTED + timedelta(seconds=second)).isoformat().replace("+00:00", "Z"),
            "stage": "apply", "worker_id": "a", "execution": EXECUTION.copy(), **extra}


def record(*events, **extra):
    return {"schema_version": 1, "run_id": "wf-test", "repository": REPO, "scope": "single_issue",
            "issue": {"number": ISSUE["number"], "url": ISSUE["url"]}, "status": "running",
            "created_at": STARTED.isoformat(), "finished_at": None, "events": list(events), "evidence": [], **extra}


def comment(value, cid=1):
    return {"id": cid, "body": "<!-- my-ai-skills-workflow-run:v1 -->\n<!-- my-ai-skills-workflow-data:start -->\n" +
            json.dumps(value) + "\n<!-- my-ai-skills-workflow-data:end -->"}


def snapshots(value, cid=1):
    return comments_snapshot([comment(value, cid)], REPO, ISSUE["number"])


def inventory(issues=None, milestones=None):
    return {"milestones": milestones or [{"repository": REPO, "number": 1, "title": "Milestone"}],
            "issues": copy.deepcopy([ISSUE] if issues is None else issues)}


def publish(store, key, value, at=None):
    generation = store.begin(key, at or NOW.isoformat())
    store.publish(key, generation, value, at or NOW.isoformat())


def seed(store, value=None):
    publish(store, "inventory:" + REPO, inventory())
    publish(store, f"comments:{REPO}:7", snapshots(value or record(event("stage_started"))))
