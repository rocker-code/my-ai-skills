"""Conversão conservadora de esperas, nunca de sucesso de turno em conclusão."""
import hashlib
import json
from collections import defaultdict

from workflow_metrics import summarize_run
from workflow_waits import coverage, subtract, union
from .common import MonitorError, parse_time


def reconcile_runtime(coordinator, repository, issue, run_id):
    store = coordinator.store
    states = {}
    for state in store.request_states():
        identity = state["identity"]
        if (identity.get("repository"), identity.get("issue"), identity.get("run_id")) != (repository, issue, run_id):
            continue
        states[(state.get("binding_key"), state.get("binding_revision"))] = state
    report = {"wait_intervals": 0, "deferred": 0, "unmeasured": 0, "results_unverified": 0, "transitions_pending": 0}
    try:
        _raw, _comment, record = coordinator.publisher.current(repository, issue, run_id)
    except MonitorError:
        report.update(deferred=len(states), error="publicação indisponível")
        return [], report
    if not record:
        report.update(deferred=len(states), error="registro canônico ausente")
        return [], report
    if any(op["payload"]["event"] == "wait-intervals" and op["state"] != "published"
           for op in coordinator.journal.operations(repository, issue, run_id)):
        report.update(deferred=len(states), error="publicação de espera pendente")
        return [], report
    details = {}
    summary = summarize_run(record, _details=details)
    report["transitions_pending"] = sum(bool(i["terminal"] and not i["closed_at"]) for i in details["intervals"])
    unverified = {(row["stage"], row["worker_id"], json.dumps(row["execution"], sort_keys=True)) for row in summary["incomplete_evidence"]}
    grouped = defaultdict(list)
    pending = defaultdict(list)
    for state in states.values():
        identity = state["identity"]
        if not identity.get("execution") or not identity.get("stage") or not identity.get("worker_id"):
            continue
        key = identity["stage"], identity["worker_id"], json.dumps(identity["execution"], sort_keys=True)
        signal = store.local(store.observation_key(state["binding_key"]), {})
        if not isinstance(signal, dict):
            signal = {}
        if signal.get("version") == 1 and signal.get("type") == "session.execution.succeeded":
            verified = any(i["stage"] == key[0] and i["worker_id"] == key[1] and i["execution"] == identity["execution"]
                           and i["terminal"] and i["terminal"].get("evidence") for i in details["intervals"])
            if not verified:
                unverified.add(key)
        for request in state["requests"].values():
            left, right = parse_time(request.get("opened_at")), parse_time(request.get("resolved_at"))
            if request["pending"]:
                pending[(key[0], key[1])].append(left)
            elif request.get("complete") and left and right and left < right:
                grouped[key].append((left, right))
            elif not request.get("complete"):
                report["unmeasured"] += 1
    results = []
    for (stage, worker, execution_json), ranges in grouped.items():
        execution = json.loads(execution_json)
        covered, explicit_open = coverage(record, stage, worker, "owner_input")
        candidates = []
        for left, right in union(ranges):
            if any(at is None or at < right for at in pending[(stage, worker)]) or any(at < right for at in explicit_open):
                report["deferred"] += 1
                continue
            owners = [i for i in details["intervals"] if i["stage"] == stage and i["worker_id"] == worker and
                      i["start"] <= left and i["effective_end"] >= right and i["execution"] == execution]
            if len(owners) != 1 or any(i is not owners[0] and i["stage"] == stage and i["worker_id"] == worker and
                                      i["start"] < right and i["effective_end"] > left for i in details["intervals"]):
                report["deferred"] += 1
                continue
            candidates.extend(subtract([(left, right)], covered))
        for index in range(0, len(candidates), 32):
            batch = candidates[index:index + 32]
            intervals = [{"start": left.isoformat().replace("+00:00", "Z"), "end": right.isoformat().replace("+00:00", "Z")} for left, right in batch]
            payload = {"version": 1, "event": "wait-intervals", "issue": f"https://github.com/{repository}/issues/{issue}",
                       "run_id": run_id, "worker_id": worker, "stage": stage, "execution": execution,
                       "at": intervals[0]["start"], "intervals": intervals, "reason": "owner_input",
                       "source": "runtime_event", "coordinator": True}
            payload["operation_id"] = "runtime-wait-" + hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            value = coordinator.transition(payload)
            results.append(value)
            if value["publication"] == "published" and not value["error"]:
                report["wait_intervals"] += len(intervals)
                covered = union(covered + batch)
            else:
                report["deferred"] += len(intervals)
                break
    report["results_unverified"] = len(unverified)
    if not report["deferred"] and not report.get("error"):
        identities = set(states)
        consumed = [fact["event_id"] for fact in store.runtime_facts() if isinstance(fact, dict) and fact.get("version") == 1
                    and (fact.get("binding_key"), fact.get("binding_revision")) in identities and fact.get("projected")]
        store.consume_runtime_facts(consumed)
    return results, report
