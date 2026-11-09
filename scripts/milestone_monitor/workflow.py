"""Contrato estruturado opt-in; configuração de leitura nunca autoriza publicação."""
import argparse
import copy
import json
import os
import re
from datetime import datetime, timedelta, timezone

import workflow_events as events
from .common import MonitorError, identifier, issue_identity, parse_time, utc_now
from .projection import STAGES

MAX_OPERATION_BYTES = 16 * 1024
EVENTS = {"run-start", "run-end", "stage-start", "stage-end", "wait-start", "wait-end", "dispatch", "observe", "rework", "wait-intervals"}
FIELDS = {"version", "operation_id", "event", "issue", "run_id", "at", "worker_id", "stage", "execution",
          "depends_on", "binding", "coordinator", "scope", "milestone_url", "agent", "model", "reason", "status",
          "evidence", "source", "state", "exit_code", "report", "log_ref", "next", "intervals"}


def options(payload):
    args = events.parser().parse_args(["wait-start" if payload["event"] == "wait-intervals" else payload["event"]])
    for key in ("issue", "run_id", "stage", "worker_id", "scope", "milestone_url", "agent", "model", "reason",
                "status", "evidence", "source", "state", "exit_code", "report", "log_ref"):
        if key in payload:
            setattr(args, key, copy.deepcopy(payload[key]))
    args.observed_at = payload["at"]
    args.next_action = payload.get("next")
    if payload.get("execution"):
        args.execution_kind, args.execution_id = payload["execution"]["kind"], payload["execution"]["id"]
    return args


def normalize_operation(value, now=None):
    try:
        encoded = json.dumps(value, allow_nan=False).encode()
        if len(encoded) > MAX_OPERATION_BYTES or not isinstance(value, dict) or set(value) - FIELDS:
            raise ValueError()
        if type(value.get("version")) is not int or value["version"] != 1 or value.get("event") not in EVENTS:
            raise ValueError()
        if value.get("coordinator") is not True:
            raise MonitorError("publicação exige contexto explícito do coordenador autorizado")
        result = copy.deepcopy(value)
        identifier(result["operation_id"])
        identifier(result["run_id"])
        identifier(result["worker_id"])
        if not isinstance(result["issue"], str) or len(result["issue"]) > 512:
            raise ValueError()
        issue_identity(result["issue"])
        at = result["at"]
        parsed = datetime.fromisoformat(at.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None or parsed > (now or utc_now()) + timedelta(seconds=120):
            raise ValueError()
        result["at"] = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        dependencies = result.setdefault("depends_on", [])
        if not isinstance(dependencies, list) or len(dependencies) > 1000 or len(set(dependencies)) != len(dependencies):
            raise ValueError()
        for dependency in dependencies:
            identifier(dependency)
        if result["operation_id"] in dependencies:
            raise ValueError()
        result["depends_on"] = sorted(dependencies)
        result.setdefault("scope", "single_issue")
        result.setdefault("evidence", [])
        if result["event"] == "wait-intervals":
            intervals = result.get("intervals")
            if not isinstance(intervals, list) or not 1 <= len(intervals) <= 32 or result.get("source") != "runtime_event":
                raise ValueError()
            for interval in intervals:
                if not isinstance(interval, dict) or set(interval) != {"start", "end"}:
                    raise ValueError()
                for side in ("start", "end"):
                    stamp = datetime.fromisoformat(interval[side].replace("Z", "+00:00"))
                    if stamp.tzinfo is None or stamp.utcoffset() is None:
                        raise ValueError()
                    interval[side] = stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
                if parse_time(interval["start"]) >= parse_time(interval["end"]) or parse_time(interval["end"]) > (now or utc_now()):
                    raise ValueError()
            if result["at"] != intervals[0]["start"]:
                raise ValueError()
        elif "intervals" in result:
            raise ValueError()
        if result["event"] not in {"run-start", "run-end"}:
            if result.get("stage") not in STAGES or set(result.get("execution", {})) != {"kind", "id"}:
                raise ValueError()
        if "execution" in result:
            identifier(result["execution"]["id"])
            if result["execution"]["kind"] not in events.EXECUTION_KINDS:
                raise ValueError()
        for field in ("agent", "model"):
            if field in result and (not isinstance(result[field], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/#-]{0,199}", result[field])):
                raise ValueError()
        if "exit_code" in result and (type(result["exit_code"]) is not int or not -(2**31) <= result["exit_code"] < 2**31):
            raise ValueError()
        evidence = result.get("evidence", [])
        if not isinstance(evidence, list) or len(evidence) > 32:
            raise ValueError()
        for reference in evidence:
            if not isinstance(reference, str) or not (events.EVIDENCE_REF_PATTERN.fullmatch(reference) or
                                                     events.validate_log_ref(reference) and not events.TYPED_REF.fullmatch(reference)):
                raise ValueError()
        if result["event"] == "observe" and result.get("state") in {"completed", "failed", "interrupted"} and result.get("source") in events.CONFIRMING:
            execution = result["execution"]
            if not evidence:
                raise MonitorError("resultado terminal exige evidência correlacionada do coordenador")
            if execution["kind"] == "worker" and result.get("source") in {"runtime_event", "runtime_query"}:
                if result.get("log_ref") != "worker-result:" + execution["id"]:
                    raise MonitorError("sinal de sessão não é resultado do worker")
            if execution["kind"] == "test_run" and (result.get("report") != "present" or
                    result.get("source") not in {"test_report", "process_exit"} or "evidence:" + execution["id"] not in evidence):
                raise MonitorError("resultado de teste exige relatório e evidência próprios")
        binding = result.get("binding")
        if binding is not None:
            if result["event"] not in {"dispatch", "stage-start"} or not isinstance(binding, dict) or set(binding) - {"session_id", "worktree", "branch"}:
                raise ValueError()
            if (not isinstance(binding.get("worktree"), str) or not os.path.isabs(binding["worktree"]) or
                    len(binding["worktree"]) > 4096 or any(ord(c) < 32 for c in binding["worktree"])):
                raise ValueError()
            if binding.get("session_id") is not None:
                if not identifier(binding["session_id"]).startswith("ses"):
                    raise ValueError()
            if binding.get("branch") is not None and (not isinstance(binding["branch"], str) or
                    len(binding["branch"]) > 200 or any(ord(c) < 32 for c in binding["branch"])):
                raise ValueError()
        events.validate_options(options(result))
        return result
    except MonitorError:
        raise
    except (ValueError, KeyError, TypeError, AttributeError, OverflowError):
        raise MonitorError("operação de workflow inválida") from None
