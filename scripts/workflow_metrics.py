#!/usr/bin/env python3
"""Shared parsing and duration calculations for My AI Skills workflow metrics."""

from __future__ import annotations

import json
import re
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any

RUN_MARKER = "<!-- my-ai-skills-workflow-run:v1 -->"
CONFIRMING_SOURCES = {"runtime_event", "runtime_query", "ci_api", "process_exit", "test_report"}
TERMINAL_STATES = {"completed", "failed", "interrupted", "unknown"}
DATA_PATTERN = re.compile(
    r"<!-- my-ai-skills-workflow-run:v1 -->\s*"
    r"<!-- my-ai-skills-workflow-data:start -->(.*?)"
    r"<!-- my-ai-skills-workflow-data:end -->",
    re.DOTALL,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_time(value: datetime | None = None) -> str:
    value = value or utc_now()
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_run_comment(body: str) -> dict[str, Any] | None:
    match = DATA_PATTERN.search(body or "")
    if not match:
        return None
    try:
        record = json.loads(match.group(1).strip())
    except json.JSONDecodeError:
        return None
    if record.get("schema_version") != 1 or not record.get("run_id"):
        return None
    return record


def overlap_seconds(start: datetime, end: datetime, other_start: datetime, other_end: datetime) -> float:
    return max(0.0, (min(end, other_end) - max(start, other_start)).total_seconds())


def correlate_observations(intervals: list[dict[str, Any]], events: list[dict[str, Any]]) -> None:
    """Attach observations to exactly one incarnation using effective time and identity."""
    opening_order = {id(event): index for index, event in enumerate(events) if event.get("type") == "stage_started"}
    for event in events:
        if event.get("type") != "state_observed":
            continue
        at = parse_time(event.get("at"))
        if at is None:
            continue
        stage, worker = event.get("stage") or "workflow", event.get("worker_id") or "orchestrator"
        pair = sorted((item for item in intervals if item["stage"] == stage and item["worker_id"] == worker),
                      key=lambda item: opening_order[id(item["start_event"])])
        candidates = []
        for index, interval in enumerate(pair):
            if interval["execution"] != event.get("execution") or at < interval["start"]:
                continue
            if interval["execution"] and (interval["closed_at"] is None or at <= interval["closed_at"]):
                # Typed IDs remain unique, but a callback outside the execution's
                # effective-time window cannot confirm it after administrative close.
                candidates.append(interval)
            else:
                # At equal effective timestamps, the next opening still owns
                # the boundary. The writer uses this stable opening order too.
                boundary = pair[index + 1]["start"] if index + 1 < len(pair) else None
                if (interval["closed_at"] is None or at <= interval["closed_at"]) and (boundary is None or at < boundary):
                    candidates.append(interval)
        if len(candidates) == 1:
            candidates[0]["observations"].append(event)


def summarize_run(record: dict[str, Any], as_of: datetime | None = None) -> dict[str, Any]:
    as_of = as_of or utc_now()
    events = sorted(
        (event for event in record.get("events", []) if parse_time(event.get("at"))),
        key=lambda event: parse_time(event["at"]),
    )
    stage_starts: dict[tuple[str, str], deque[dict[str, Any]]] = defaultdict(deque)
    wait_starts: dict[tuple[str, str, str], deque[datetime]] = defaultdict(deque)
    intervals: list[dict[str, Any]] = []
    waits: list[dict[str, Any]] = []
    run_started = parse_time(record.get("created_at"))
    run_finished = parse_time(record.get("finished_at"))
    legacy = not any(event.get("type") == "state_observed" for event in events)
    current_stage = None

    for event in events:
        at = parse_time(event.get("at"))
        kind = event.get("type")
        worker = event.get("worker_id") or "orchestrator"
        stage = event.get("stage") or "workflow"
        if kind == "run_started":
            run_started = run_started or at
        elif kind == "run_finished":
            run_finished = at
        elif kind == "stage_started":
            current_stage = stage
            stage_starts[(stage, worker)].append({
                "stage": stage, "worker_id": worker, "start": at, "end": as_of, "closed_at": None,
                "agent": event.get("agent"), "model": event.get("model"), "execution": event.get("execution"),
                "observations": [], "start_event": event,
            })
        elif kind in ("stage_finished", "stage_failed"):
            queue = stage_starts[(stage, worker)]
            match = next((item for item in queue if item["execution"] == event.get("execution")), None)
            if match:
                queue.remove(match)
                match["end"] = at
                match["closed_at"] = at
                match["end_event"] = event
                intervals.append(match)
        elif kind == "wait_started":
            wait_starts[(stage, worker, event.get("reason") or "unspecified")].append(at)
        elif kind == "wait_finished":
            key = (stage, worker, event.get("reason") or "unspecified")
            queue = wait_starts[key]
            if queue:
                waits.append({"stage": stage, "worker_id": worker, "reason": key[2], "start": queue.popleft(), "end": at})

    for (stage, worker), queue in stage_starts.items():
        intervals.extend(queue)
    open_waits = ([{"stage": stage, "worker_id": worker, "reason": reason}
                   for (stage, worker, reason), queue in wait_starts.items() if queue]
                   if legacy or not run_finished else [])
    for (stage, worker, reason), queue in wait_starts.items():
        while queue:
            waits.append({"stage": stage, "worker_id": worker, "reason": reason, "start": queue.popleft(),
                          "end": as_of})

    open_stages = [(items[-1]["start"], stage) for (stage, _worker), items in stage_starts.items() if items]
    current_stage = max(open_stages, default=(None, None))[1] if legacy or not run_finished else None

    correlate_observations(intervals, events)
    for interval in intervals:
        # An observation affects only its incarnation. A separate unobserved
        # worker retains pre-#32 accounting, including future closed endpoints.
        if interval["observations"] and run_finished:
            interval["end"] = max(interval["start"], min(interval["end"], as_of, run_finished))
        observations = sorted(interval["observations"], key=lambda e: parse_time(e["at"]))
        confirmed = [e for e in observations if e.get("source") in CONFIRMING_SOURCES]
        terminals = [e for e in confirmed if e.get("state") in TERMINAL_STATES]
        interval["terminal"] = terminals[0] if terminals else None
        # Once terminal, a later running signal cannot revive this incarnation.
        interval["last_confirmed"] = terminals[-1] if terminals else (confirmed[-1] if confirmed else None)
        interval["effective_end"] = min(interval["end"], parse_time(terminals[0]["at"])) if terminals else interval["end"]
        interval["verified_state"] = (
            "needs_reconciliation" if terminals and interval["closed_at"] is None
            else terminals[-1]["state"] if terminals
            else "working" if confirmed
            else "unconfirmed" if observations
            else "unobserved"
        )

    opening_order = {id(event): index for index, event in enumerate(events) if event.get("type") == "stage_started"}
    for wait in waits:
        # Charge a wait to the incarnation active when it began. An earlier
        # observed incarnation of the same pair must not cap a later B's
        # unobserved wait (or its legacy work subtraction).
        candidates = [item for item in intervals if item["stage"] == wait["stage"]
                      and item["worker_id"] == wait["worker_id"] and item["start"] <= wait["start"]
                      and (item["closed_at"] is None or wait["start"] <= item["closed_at"])]
        owner = (max(candidates, key=lambda item: (item["start"], opening_order[id(item["start_event"])]))
                 if candidates else None)
        if run_finished and owner and owner["observations"]:
            wait["end"] = max(wait["start"], min(wait["end"], as_of, run_finished))

    rework_count = sum(1 for event in events if event.get("type") in {"stage_failed", "rework"})
    stage_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for interval in intervals:
        stage_groups[interval["stage"]].append(interval)

    stage_metrics = []
    total_work = 0.0
    for stage, group in sorted(stage_groups.items()):
        wall_start = min(item["start"] for item in group)
        wall_end = max(item["end"] for item in group)
        elapsed = max(0.0, (wall_end - wall_start).total_seconds())
        work = 0.0
        for interval in group:
            duration = max(0.0, (interval["effective_end"] - interval["start"]).total_seconds())
            blocked = sum(
                overlap_seconds(interval["start"], interval["effective_end"], wait["start"], wait["end"])
                for wait in waits
                if wait["stage"] == stage and wait["worker_id"] == interval["worker_id"]
            )
            work += max(0.0, duration - blocked)
        stage_waits: dict[str, float] = defaultdict(float)
        for wait in waits:
            if wait["stage"] == stage:
                stage_waits[wait["reason"]] += max(0.0, (wait["end"] - wait["start"]).total_seconds())
        total_work += work
        latest = max(group, key=lambda item: item["start"])
        stage_metrics.append({
            "stage": stage,
            "elapsed_seconds": round(elapsed, 3),
            "recorded_work_seconds": round(work, 3),
            "wait_seconds_by_reason": {reason: round(seconds, 3) for reason, seconds in sorted(stage_waits.items())},
            "workers": sorted({item["worker_id"] for item in group}),
            "verified_state": latest["verified_state"],
            "executions": [
                {"worker_id": item["worker_id"], "execution": item["execution"],
                 "verified_state": item["verified_state"], "last_observed_at": item["last_confirmed"].get("at") if item["last_confirmed"] else None}
                for item in sorted(group, key=lambda value: value["start"])
            ],
        })

    wait_totals: dict[str, float] = defaultdict(float)
    for wait in waits:
        wait_totals[wait["reason"]] += max(0.0, (wait["end"] - wait["start"]).total_seconds())

    cycle_end = run_finished or as_of
    cycle = max(0.0, (cycle_end - run_started).total_seconds()) if run_started else None
    active = sorted((item for item in intervals if item["closed_at"] is None and not run_finished), key=lambda i: i["start"])
    current = active[-1] if active else None
    # The accounting horizon may give several intervals the same capped end.
    # The latest opening identifies the relevant incarnation, not that tie.
    historical = max(enumerate(intervals),
                     key=lambda pair: (pair[1]["start"], pair[1]["closed_at"] or pair[1]["start"], pair[0]))[1] if intervals else None
    relevant = current or historical
    last = relevant["last_confirmed"] if relevant else None
    incomplete = []
    for item in intervals:
        if (item["execution"] or {}).get("kind") == "test_run":
            # Work ends at the first terminal observation, but completeness
            # follows the last confirmed terminal outcome of this incarnation.
            outcomes = sorted((e for e in item["observations"] if e.get("source") in CONFIRMING_SOURCES
                               and e.get("state") in TERMINAL_STATES), key=lambda e: parse_time(e["at"]))
            outcome = outcomes[-1] if outcomes else None
            if not outcome or outcome["state"] not in {"completed", "failed"} or outcome.get("report") != "present":
                incomplete.append({"stage": item["stage"], "worker_id": item["worker_id"],
                                    "execution": item["execution"],
                                    "reason": "missing_terminal" if outcome is None or outcome["state"] in {"unknown", "interrupted"} else "missing_report"})
    if record.get("finished_at"):
        activity = record.get("status", "completed")
    elif open_waits:
        activity = f"waiting:{open_waits[-1]['reason']}"
    elif current:
        activity = (current["last_confirmed"]["state"] if current["terminal"] and current["last_confirmed"]["state"] in {"unknown", "interrupted"}
                    else current["verified_state"])
    else:
        activity = "unobserved"
    linked_events = ([relevant["start_event"], *relevant["observations"], relevant.get("end_event")]
                     if relevant else [])
    evidence = next((ref for e in reversed(linked_events) if e
                     for ref in reversed(e.get("evidence", [])) if isinstance(ref, str) and ref.startswith("evidence:")), None)
    proof = ({"state": last.get("state"), "source": last.get("source"), "stage": relevant["stage"],
              "worker_id": relevant["worker_id"], "execution": relevant["execution"],
              "log_ref": last.get("log_ref"), "evidence": evidence or ("não verificada" if (relevant["execution"] or {}).get("kind") == "test_run" else None),
              "at": last.get("at")} if last else None)
    weak = next((e for e in reversed(relevant["observations"]) if e.get("source") not in CONFIRMING_SOURCES), None) if relevant else None
    next_action = next((e["next"] for e in reversed(linked_events) if e and e.get("next")), None)
    blocker = (None if record.get("finished_at") else
               open_waits[-1]["reason"] if open_waits else
               "needs_reconciliation" if current and current["terminal"] else None)
    verification_times = (parse_time(e.get("last_seen_at")) or parse_time(e["at"])
                          for e in relevant["observations"] if e.get("source") in CONFIRMING_SOURCES) if relevant else ()
    verified_at = max(verification_times, default=None)
    status_summary = {"current_stage": current_stage, "activity_state": activity, "last_confirmed": proof,
                      "insufficient_signal": {"state": weak.get("state"), "source": weak.get("source"), "at": weak.get("at")} if weak else None,
                      "blocker": blocker, "next_action": next_action,
                      "verified_at": iso_time(verified_at) if verified_at else None}
    return {
        "run_id": record["run_id"],
        "repository": record.get("repository"),
        "scope": record.get("scope"),
        "milestone_url": record.get("milestone_url"),
        "issue": record.get("issue"),
        "status": record.get("status", "running"),
        "current_stage": current_stage,
        # The pre-observation reader consumed its wait queues before emitting
        # this legacy field (always []). Keep that field byte-for-byte compatible.
        "current_waits": [] if legacy else open_waits,
        "status_summary": status_summary,
        "incomplete_evidence": incomplete,
        "created_at": record.get("created_at"),
        "finished_at": record.get("finished_at"),
        "cycle_elapsed_seconds": round(cycle, 3) if cycle is not None else None,
        "recorded_work_seconds": round(total_work, 3),
        "wait_seconds_by_reason": {reason: round(seconds, 3) for reason, seconds in sorted(wait_totals.items())},
        "stages": stage_metrics,
        "rework_count": rework_count,
        "events": record.get("events", []),
        "evidence": record.get("evidence", []),
    }


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * fraction + 0.5)))
    return ordered[index]
