"""Overlay conservador; métricas canônicas permanecem inalteradas."""
import json
from collections import Counter

from workflow_metrics import summarize_run, parse_time
from .common import fresh, iso_time, utc_now

STAGES = ("issue_audit", "explore", "resolve_questions", "proposal", "proposal_review", "apply", "tests",
          "verify_archive", "prepare_pr", "pr_audit", "ci", "merge", "kaizen")
LABELS = ("Auditoria", "Explorar", "Decisões", "Proposta", "Revisar proposta", "Aplicar", "Testes",
          "Verificar/arquivar", "Preparar PR", "Auditar PR", "CI", "Merge", "Kaizen")
STAGE_LABELS = dict(zip(STAGES, LABELS))
WAIT_LABELS = {"owner_input": "aguardando decisão", "dependency": "aguardando dependência", "ci": "aguardando CI",
               "tests": "aguardando testes", "environment": "aguardando ambiente", "review": "aguardando revisão",
               "runtime_capacity": "aguardando capacidade", "external": "aguardando externo", "other": "outra espera"}


def analyze(record, now=None):
    details = {}
    summary = summarize_run(record, as_of=now or utc_now(), _details=details)
    return summary, details


def incarnation_key(repo, number, run_id, interval):
    return "binding:" + json.dumps([repo, number, run_id, interval["stage"], interval["worker_id"],
                                     interval["execution"], iso_time(interval["start"])], separators=(",", ":"))


def issue_view(issue, snapshots, runtime, bindings, now, timing, session_started, history=0):
    ordered = sorted(snapshots or [], key=lambda s: (parse_time(s["record"]["created_at"]), s["record"]["run_id"], s["comment_id"]), reverse=True)
    view = {**issue, "group": "pending", "label": "nunca iniciada", "warnings": [], "stages": {}, "workers": [],
            "summary": None, "run": None, "history_count": len(ordered), "history": min(history, max(0, len(ordered)-1))}
    if ordered:
        chosen = ordered[view["history"]]
        record = chosen["record"]
        view["run"] = record["run_id"]
        summary, details = analyze(record, now)
        view["summary"] = summary
        if sum(not s["record"].get("finished_at") for s in ordered) > 1:
            view["warnings"].append("runs simultaneamente abertos")
        if sum(s["record"]["created_at"] == record["created_at"] for s in ordered) > 1:
            view["warnings"].append("empate de criação de run")
        if len({s["hash"] for s in ordered if s["record"]["run_id"] == record["run_id"]}) > 1:
            view["warnings"].append("snapshots conflitantes do mesmo run")
        running, failures = False, []
        intervals = details["intervals"]
        latest = {}
        for interval in intervals:
            pair = interval["stage"], interval["worker_id"]
            if pair not in latest or interval["start"] >= latest[pair]["start"]:
                latest[pair] = interval
        for interval in sorted(intervals, key=lambda i: i["start"]):
            key = incarnation_key(issue["repository"], issue["number"], record["run_id"], interval)
            binding = bindings.get(key)
            observation = runtime.get(key) if binding else None
            terminal = interval["terminal"]
            last = interval["last_confirmed"]
            state, label = "unknown", "desconhecida"
            closed = interval["closed_at"] is not None or bool(record.get("finished_at"))
            if terminal:
                state = last["state"]
                label = {"completed": "concluída registrada", "failed": "falha", "interrupted": "interrompida", "unknown": "reconciliação"}[state]
                if observation and observation.get("state") == "active":
                    view["warnings"].append("sessão ativa, execução encerrada")
            elif closed:
                # Administrative closure is not a confirmed test result.
                failed = interval.get("end_event", {}).get("type") == "stage_failed"
                state, label = ("failed", "falha registrada") if failed else ("closed", "encerrada registrada; resultado indisponível")
            else:
                verified = last and last.get("state") == "running" and fresh(last.get("last_seen_at") or last["at"], now, timing["activity_ttl"])
                # A reopened UI never promotes an old cached running sample.
                verified = bool(verified and parse_time(last.get("last_seen_at") or last["at"]) >= session_started)
                worker = (interval["execution"] or {}).get("kind") == "worker"
                if binding and worker:
                    verified = bool(observation and observation.get("state") == "active"
                                    and fresh(observation.get("at"), now, timing["activity_ttl"])
                                    and parse_time(observation["at"]) >= session_started)
                if verified:
                    state, label, running = "running", "executando confirmado", True
                elif observation and observation.get("state") in {"inactive", "absent", "incompatible", "context_changed"}:
                    label = {"inactive": "sessão inativa", "absent": "sessão ausente", "incompatible": "vínculo incompatível", "context_changed": "contexto alterado; refazer vínculo"}[observation["state"]]
            if latest.get((interval["stage"], interval["worker_id"])) is interval and state in {"failed", "interrupted", "unknown"} and terminal:
                failures.append(label)
            if latest.get((interval["stage"], interval["worker_id"])) is interval and state == "failed":
                failures.append(label)
            status = "current" if not closed and not terminal else "completed" if state in {"completed", "closed"} else state
            view["stages"][interval["stage"]] = status
            view["workers"].append({"stage": interval["stage"], "worker": interval["worker_id"], "execution": interval["execution"],
                                    "state": state, "label": label, "opened_at": iso_time(interval["start"]), "key": key,
                                    "last_observed_at": last.get("last_seen_at") or last.get("at") if last else None,
                                    "binding": binding, "runtime": observation, "open": not closed})
        # Legacy waits are available from the same canonical queues, even when
        # its compatibility current_waits field intentionally remains empty.
        waits = details["open_waits"]
        if waits:
            reason = next((w["reason"] for w in waits if w["reason"] == "owner_input"), waits[-1]["reason"])
            view.update(group="blocked", label=WAIT_LABELS.get(reason, "aguardando"))
            for wait in waits:
                view["stages"][wait["stage"]] = "decision" if wait["reason"] == "owner_input" else "blocked"
        elif failures:
            view.update(group="blocked", label=failures[-1])
        elif running:
            view.update(group="running", label="executando confirmado")
        else:
            view["label"] = "reconciliação" if any(w["state"] == "unknown" for w in view["workers"]) else "inativa / sem confirmação recente"
        if view["warnings"] and "snapshots conflitantes do mesmo run" in view["warnings"]:
            view.update(group="pending", label="origem conflitante; reconciliação")
    if issue["state"] == "closed":
        if any(w["open"] for w in view["workers"]):
            view["warnings"].append("GitHub fechado com atividade aberta")
        view.update(group="done", label="fechada no GitHub; entrega separada")
    return view


def model(store, config, session_started, now=None, histories=None):
    now, histories = now or utc_now(), histories or {}
    groups, health = [], []
    bindings = store.bindings()
    runtime_source = store.source("runtime")
    runtime = runtime_source.get("payload") or {}
    if runtime_source.get("error") or not config["runtime"]["enabled"]:
        runtime = {}  # preserve sample on disk, never renew confirmation on error
    for target in config["targets"]:
        repo = target["repository"]
        source = store.source("inventory:" + repo)
        fetched = parse_time(source.get("fetched_at"))
        health.append({**source, "payload": None, "fresh": bool(not source.get("error") and fetched
                       and fetched >= session_started.replace(microsecond=0)
                       and fresh(source.get("fetched_at"), now, config["timing"]["github_ttl"]))})
        payload = source.get("payload") or {"milestones": [{"repository": repo, "number": n, "title": "sem inventário"} for n in target["milestones"]], "issues": []}
        for milestone in payload["milestones"]:
            if milestone["number"] not in target["milestones"]:
                continue
            issues = []
            for issue in payload["issues"]:
                if issue["milestone"] != milestone["number"]:
                    continue
                comments = store.source(f"comments:{repo}:{issue['number']}")
                pr = store.source(f"prs:{repo}:{issue['number']}")
                view = issue_view(issue, comments.get("payload"), runtime, bindings, now, config["timing"], session_started,
                                  histories.get((repo, issue["number"]), 0))
                view.update(comments_health={k: v for k, v in comments.items() if k != "payload"},
                            pr=pr.get("payload"), pr_health={k: v for k, v in pr.items() if k != "payload"},
                            inventory_health={k: v for k, v in source.items() if k != "payload"},
                            runtime_health={k: v for k, v in runtime_source.items() if k != "payload"})
                issues.append(view)
            totals = {key: 0 for key in ("done", "running", "pending", "blocked")}
            totals.update(Counter(i["group"] for i in issues))
            groups.append({**milestone, "issues": sorted(issues, key=lambda i: i["number"]), "totals": totals,
                           "percent": round(100 * totals["done"] / len(issues)) if issues else None})
    return {"milestones": groups, "health": health, "runtime_health": {k: v for k, v in runtime_source.items() if k != "payload"}, "at": iso_time(now)}
