"""Redutor de pedidos: estado atual e intervalo medido são coisas distintas."""
import copy
from datetime import datetime, timezone

from .common import MonitorError, parse_time


def state_for(previous, revision, epoch, coverage):
    if previous is not None and (not isinstance(previous, dict) or previous.get("version") != 1):
        raise MonitorError("estado de pedidos incompatível")
    if previous is None or previous.get("binding_revision") != revision:
        previous = {"version": 1, "binding_revision": revision, "requests": {}}
    state = copy.deepcopy(previous)
    continuity = coverage.get("continuity") if coverage.get("collector_epoch") == epoch else None
    changed = state.get("collector_epoch") != epoch or state.get("continuity") != continuity
    if changed:
        for request in state["requests"].values():
            if request["pending"] or not request.get("resolved_at"):
                request.update(start_covered=False, complete=False)
    state.update(collector_epoch=epoch, continuity=continuity,
                 gap=not (coverage.get("collector_epoch") == epoch and coverage.get("complete", False)))
    return state


def empty_request(request_id, kind):
    return {"request_id": request_id, "kind": kind, "pending": False, "status": "unknown",
            "opened_at": None, "resolved_at": None, "start_covered": False, "end_covered": False,
            "complete": False, "continuity": None}


def add_request(state, request_id, kind):
    if request_id not in state["requests"]:
        if len(state["requests"]) >= 1000:
            raise MonitorError("limite de pedidos observados")
        state["requests"][request_id] = empty_request(request_id, kind)
    return state["requests"][request_id]


def snapshot(previous, sample, epoch, coverage):
    state = state_for(previous, sample["binding_revision"], epoch, coverage)
    started, observed = parse_time(sample["query_started_at"]), parse_time(sample["at"])
    if not started or not observed:
        raise MonitorError("horário de consulta inválido")
    present = {item["request_id"]: item["kind"] for item in sample["requests"]}
    for request_id, kind in present.items():
        request = add_request(state, request_id, kind)
        resolved = parse_time(request.get("resolved_at"))
        if resolved and resolved >= started:
            continue  # Resposta nativa posterior ao início da consulta prevalece.
        if resolved:
            # Consulta contraditória não transforma um intervalo em medição confiável.
            request.update(resolved_at=None, start_covered=False, end_covered=False, complete=False)
            state["gap"] = True
        request.update(pending=True, status="pending")
    for request_id, request in state["requests"].items():
        opened = parse_time(request.get("opened_at"))
        if request_id not in present and request["pending"] and (not opened or opened < started):
            request.update(pending=False, status="resolution_unknown", resolved_at=None, complete=False)
    state.update(observed_at=sample["at"], query_started_at=sample["query_started_at"], snapshot_ids=sorted(present))
    return state


def event(previous, fact, epoch, coverage):
    state = state_for(previous, fact["binding_revision"], epoch, coverage)
    if not fact["type"].startswith(("permission.", "form.")):
        return state
    kind = "permission" if fact["type"].startswith("permission.") else "form"
    request = add_request(state, fact["request_id"], kind)
    at = datetime.fromtimestamp(fact["created"] / 1000, timezone.utc)
    reconciled = parse_time(coverage.get("reconciled_at"))
    covered = bool(coverage.get("collector_epoch") == epoch and coverage.get("complete") and reconciled and
                   at >= reconciled and fact.get("continuity") == coverage.get("continuity"))
    if fact["type"] in {"permission.asked", "form.created"}:
        request["opened_at"] = at.isoformat()
        request["start_covered"] = covered
        request["continuity"] = fact.get("continuity")
        queried = parse_time(state.get("query_started_at"))
        absent_after = queried and at < queried and request["request_id"] not in state.get("snapshot_ids", [])
        if not request.get("resolved_at") and not absent_after:
            request.update(pending=True, status="pending")
    else:
        request.update(pending=False, resolved_at=at.isoformat(), end_covered=covered,
                       status="cancelled" if fact["type"] == "form.cancelled" else fact.get("resolution", "answered"))
        request["end_continuity"] = fact.get("continuity")
    opened, resolved = parse_time(request.get("opened_at")), parse_time(request.get("resolved_at"))
    request["complete"] = bool(opened and resolved and resolved >= opened and request["start_covered"] and
                               request["end_covered"] and request.get("continuity") == request.get("end_continuity"))
    # O evento não renova horário de uma consulta nem atividade da sessão.
    return state
