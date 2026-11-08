"""Leitura allowlist dos comentários v1; nunca escreve no GitHub."""
import hashlib
import json
import re
from datetime import datetime

from workflow_metrics import RUN_MARKER, parse_run_comment, parse_time
from .common import MonitorError, identifier, text

KINDS = {"worker", "process", "job", "test_run", "ci_run"}
STATES = {"running", "completed", "failed", "interrupted", "unknown"}
SOURCES = {"runtime_event", "runtime_query", "ci_api", "process_exit", "test_report", "agent_prose", "container_state"}
REASONS = {"owner_input", "dependency", "ci", "tests", "environment", "review", "runtime_capacity", "external", "other", "replan", "reopened"}


def timestamp(value):
    if not isinstance(value, str):
        raise MonitorError("registro workflow inválido")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError()
    except ValueError:
        raise MonitorError("registro workflow inválido") from None
    return value


def refs(values):
    if not isinstance(values, list):
        raise MonitorError("registro workflow inválido")
    return [v for v in values if isinstance(v, str) and (
        re.fullmatch(r"evidence:ev-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}|[a-fA-F0-9]{7,64}", v)
        or re.fullmatch(r"https://github.com/[A-Za-z0-9_./:#-]+", v))]


def record_of(body, repo, number):
    if not isinstance(body, str) or RUN_MARKER not in body:
        return None
    try:
        raw = parse_run_comment(body)
    except (AttributeError, TypeError):
        raw = None
    if not isinstance(raw, dict):
        raise MonitorError("registro workflow inválido")
    url = f"https://github.com/{repo}/issues/{number}"
    if raw.get("repository") != repo or raw.get("issue") != {"number": number, "url": url}:
        raise MonitorError("identidade workflow incompatível")
    result = {"schema_version": 1, "run_id": identifier(raw["run_id"]), "repository": repo,
              "issue": {"number": number, "url": url}, "created_at": timestamp(raw.get("created_at")),
              "finished_at": timestamp(raw["finished_at"]) if raw.get("finished_at") else None,
              "status": raw.get("status", "running"), "scope": raw.get("scope", "single_issue"),
              "events": [], "evidence": refs(raw.get("evidence", []))}
    if result["status"] not in {"running", "completed", "failed"} or result["scope"] not in {"single_issue", "milestone", "project_queue"}:
        raise MonitorError("registro workflow inválido")
    milestone = raw.get("milestone_url")
    if milestone and not re.fullmatch(rf"https://github.com/{re.escape(repo)}/milestone/[1-9][0-9]*/?", milestone):
        raise MonitorError("identidade workflow incompatível")
    result["milestone_url"] = milestone
    if not isinstance(raw.get("events"), list):
        raise MonitorError("registro workflow inválido")
    for event in raw["events"]:
        if not isinstance(event, dict):
            raise MonitorError("registro workflow inválido")
        clean = {"type": identifier(event.get("type")), "at": timestamp(event.get("at"))}
        for key in ("stage", "worker_id"):
            if event.get(key) is not None:
                clean[key] = identifier(event[key])
        for key in ("recorded_at", "last_seen_at"):
            if event.get(key) is not None:
                clean[key] = timestamp(event[key])
        for key, choices in (("state", STATES), ("source", SOURCES), ("reason", REASONS),
                             ("status", {"completed", "failed"}), ("report", {"present", "absent", "unknown"})):
            if key in event:
                if event[key] not in choices:
                    raise MonitorError("registro workflow inválido")
                clean[key] = event[key]
        execution = event.get("execution")
        if execution is not None:
            if not isinstance(execution, dict) or execution.get("kind") not in KINDS:
                raise MonitorError("registro workflow inválido")
            clean["execution"] = {"kind": execution["kind"], "id": identifier(execution.get("id"))}
        for key in ("agent", "model", "next"):
            if isinstance(event.get(key), str):
                clean[key] = text(event[key], 160)
        if "exit_code" in event and type(event["exit_code"]) is int:
            clean["exit_code"] = event["exit_code"]
        if "evidence" in event:
            clean["evidence"] = refs(event["evidence"])
        # log_ref is a reference only, never the contents of a log.
        ref = event.get("log_ref")
        if isinstance(ref, str) and (refs([ref]) or re.fullmatch(r"[a-z][a-z0-9-]{1,30}:[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}", ref)):
            clean["log_ref"] = ref
        result["events"].append(clean)
    return result


def comments_snapshot(comments, repo, number):
    snapshots = {}
    for comment in comments:
        if not isinstance(comment, dict) or type(comment.get("id")) is not int:
            raise MonitorError("resposta inválida")
        try:
            record = record_of(comment.get("body"), repo, number)
        except (TypeError, ValueError, AttributeError, KeyError):
            raise MonitorError("registro workflow inválido") from None
        if record:
            canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
            snapshots[comment["id"]] = {"comment_id": comment["id"], "hash": hashlib.sha256(canonical.encode()).hexdigest(), "record": record}
    return sorted(snapshots.values(), key=lambda s: (parse_time(s["record"]["created_at"]), s["record"]["run_id"], s["comment_id"]), reverse=True)
