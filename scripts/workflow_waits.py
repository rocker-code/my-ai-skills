"""União/subtração e pares v1 atômicos, sem alterar métricas legadas."""
import copy
import hashlib
from collections import defaultdict, deque
from datetime import datetime, timezone

import workflow_events as events
from workflow_metrics import parse_time, summarize_run


def union(intervals):
    result = []
    for start, end in sorted(intervals):
        if start >= end:
            continue
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], end))
        else:
            result.append((start, end))
    return result


def subtract(intervals, covered):
    result = []
    for start, end in union(intervals):
        cursor = start
        for left, right in union(covered):
            if right <= cursor or left >= end:
                continue
            if cursor < left:
                result.append((cursor, min(left, end)))
            cursor = max(cursor, right)
        if cursor < end:
            result.append((cursor, end))
    return result


def pairs(record):
    queues, matches = defaultdict(deque), {}
    for index, event in sorted(enumerate(record["events"]), key=lambda row: parse_time(row[1]["at"])):
        key = event.get("stage"), event.get("worker_id") or "orchestrator", event.get("reason") or "unspecified"
        if event["type"] == "wait_started":
            queues[key].append(index)
            matches[index] = None
        elif event["type"] == "wait_finished" and queues[key]:
            matches[queues[key].popleft()] = index
    return matches


def coverage(record, stage, worker, reason):
    matched = pairs(record)
    closed, opened = [], []
    for start_index, end_index in matched.items():
        start = record["events"][start_index]
        if (start.get("stage"), start.get("worker_id") or "orchestrator", start.get("reason") or "unspecified") != (stage, worker, reason):
            continue
        left = parse_time(start["at"])
        if end_index is None:
            opened.append(left)
        else:
            closed.append((left, parse_time(record["events"][end_index]["at"])))
    return union(closed), opened


def derived_id(operation_id, index):
    return "we-" + hashlib.sha256(f"{operation_id}:{index}".encode()).hexdigest()


def build_wait_record(args, comments, intervals, operation, now=None):
    now = now or datetime.now(timezone.utc)
    matching = [(item, events.parse_run_comment(item.get("body", ""))) for item in comments]
    matching = [(item, record) for item, record in matching if record and record.get("run_id") == args.run_id]
    if len(matching) != 1:
        raise ValueError("wait batch requires one canonical run")
    comment, original = matching[0]
    ranges = [(parse_time(item["start"]), parse_time(item["end"])) for item in intervals]
    covered, opened = coverage(original, args.stage, args.worker_id, args.reason)
    if ranges != union(ranges) or subtract(ranges, covered) != ranges:
        raise ValueError("wait batch overlaps canonical coverage")
    details = {}
    summarize_run(original, now, _details=details)
    for left, right in ranges:
        owners = [i for i in details["intervals"] if i["stage"] == args.stage and i["worker_id"] == args.worker_id
                  and i["start"] <= left and i["effective_end"] >= right]
        if len(owners) != 1 or owners[0]["execution"] != {"kind": args.execution_kind, "id": args.execution_id}:
            raise ValueError("wait batch has ambiguous execution or boundary")
        if any(i is not owners[0] and i["stage"] == args.stage and i["worker_id"] == args.worker_id and
               i["start"] < right and i["effective_end"] > left for i in details["intervals"]):
            raise ValueError("wait batch overlaps another execution of the same worker")
        if any(at < right for at in opened):
            raise ValueError("wait batch would interfere with an open canonical wait")
    record, current_comments = original, comments
    offset = len(original["events"])
    for index, interval in enumerate(intervals):
        for side, command in (("start", "wait-start"), ("end", "wait-end")):
            item = copy.copy(args)
            item.event, item.observed_at = command, interval[side]
            metadata = {"id": derived_id(operation["id"], 2 * index + (side == "end")),
                        "hash": operation["hash"], "operation_id": operation["id"]}
            record, _cid, _result = events.build_record(item, current_comments, now, metadata, atomic_wait=True)
            current_comments = [{"id": comment["id"], "body": events.comment_body(record)}]
    before, after = pairs(original), pairs(record)
    if any(after.get(start) != end for start, end in before.items()):
        raise ValueError("wait batch changes legacy FIFO pairing")
    for index in range(len(intervals)):
        if after.get(offset + 2 * index) != offset + 2 * index + 1:
            raise ValueError("wait batch does not pair its own boundaries")
    return record, comment["id"], {"event": "wait_intervals", "intervals": len(intervals)}
