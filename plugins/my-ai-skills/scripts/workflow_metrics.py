#!/usr/bin/env python3
"""Shared parsing and duration calculations for My AI Skills workflow metrics."""

from __future__ import annotations

import json
import re
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any

RUN_MARKER = "<!-- my-ai-skills-workflow-run:v1 -->"
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


def summarize_run(record: dict[str, Any], as_of: datetime | None = None) -> dict[str, Any]:
    as_of = as_of or utc_now()
    events = sorted(
        (event for event in record.get("events", []) if parse_time(event.get("at"))),
        key=lambda event: parse_time(event["at"]),
    )
    stage_starts: dict[tuple[str, str], deque[tuple[datetime, dict[str, Any]]]] = defaultdict(deque)
    wait_starts: dict[tuple[str, str, str], deque[datetime]] = defaultdict(deque)
    intervals: list[dict[str, Any]] = []
    waits: list[dict[str, Any]] = []
    run_started = parse_time(record.get("created_at"))
    run_finished = parse_time(record.get("finished_at"))
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
            stage_starts[(stage, worker)].append((at, event))
        elif kind in ("stage_finished", "stage_failed"):
            queue = stage_starts[(stage, worker)]
            if queue:
                started, start_event = queue.popleft()
                intervals.append({
                    "stage": stage, "worker_id": worker, "start": started, "end": at,
                    "agent": start_event.get("agent"), "model": start_event.get("model"),
                })
        elif kind == "wait_started":
            wait_starts[(stage, worker, event.get("reason") or "unspecified")].append(at)
        elif kind == "wait_finished":
            key = (stage, worker, event.get("reason") or "unspecified")
            queue = wait_starts[key]
            if queue:
                waits.append({"stage": stage, "worker_id": worker, "reason": key[2], "start": queue.popleft(), "end": at})

    open_stages = [
        (items[-1][0], stage) for (stage, _worker), items in stage_starts.items() if items
    ]
    current_stage = max(open_stages, default=(None, None))[1]

    for (stage, worker), queue in stage_starts.items():
        while queue:
            started, start_event = queue.popleft()
            intervals.append({
                "stage": stage, "worker_id": worker, "start": started, "end": as_of,
                "agent": start_event.get("agent"), "model": start_event.get("model"),
            })
    for (stage, worker, reason), queue in wait_starts.items():
        while queue:
            waits.append({"stage": stage, "worker_id": worker, "reason": reason, "start": queue.popleft(), "end": as_of})

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
            duration = max(0.0, (interval["end"] - interval["start"]).total_seconds())
            blocked = sum(
                overlap_seconds(interval["start"], interval["end"], wait["start"], wait["end"])
                for wait in waits
                if wait["stage"] == stage and wait["worker_id"] == interval["worker_id"]
            )
            work += max(0.0, duration - blocked)
        stage_waits: dict[str, float] = defaultdict(float)
        for wait in waits:
            if wait["stage"] == stage:
                stage_waits[wait["reason"]] += max(0.0, (wait["end"] - wait["start"]).total_seconds())
        total_work += work
        stage_metrics.append({
            "stage": stage,
            "elapsed_seconds": round(elapsed, 3),
            "recorded_work_seconds": round(work, 3),
            "wait_seconds_by_reason": {reason: round(seconds, 3) for reason, seconds in sorted(stage_waits.items())},
            "workers": sorted({item["worker_id"] for item in group}),
        })

    wait_totals: dict[str, float] = defaultdict(float)
    for wait in waits:
        wait_totals[wait["reason"]] += max(0.0, (wait["end"] - wait["start"]).total_seconds())

    cycle_end = run_finished or as_of
    cycle = max(0.0, (cycle_end - run_started).total_seconds()) if run_started else None
    return {
        "run_id": record["run_id"],
        "repository": record.get("repository"),
        "scope": record.get("scope"),
        "milestone_url": record.get("milestone_url"),
        "issue": record.get("issue"),
        "status": record.get("status", "running"),
        "current_stage": current_stage,
        "current_waits": [
            {"stage": stage, "worker_id": worker, "reason": reason}
            for (stage, worker, reason), queue in wait_starts.items() if queue
        ],
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
