"""Entrada explícita do coordenador; não é acionada por observador/dashboard."""
import json
import sqlite3
import sys
import argparse
import os

from .common import MonitorError, identifier, issue_identity
from .config import state_path
from .journal import Journal
from .publisher import Publisher
from .store import Store
from .workflow import MAX_OPERATION_BYTES, normalize_operation
from .collector import Collector
from .runtime import Runtime, bind, find_incarnation, git_identity
from .github import GitHub
from .ingest import comments_snapshot
from .projection import incarnation_key


def read_input(path, stream=None):
    try:
        if path == "-":
            data = (stream or sys.stdin.buffer).read(MAX_OPERATION_BYTES + 1)
        else:
            with open(path, "rb") as source:
                data = source.read(MAX_OPERATION_BYTES + 1)
        if len(data) > MAX_OPERATION_BYTES:
            raise MonitorError("entrada de workflow excedida")
        def unique(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise ValueError()
                value[key] = item
            return value
        return json.loads(data, object_pairs_hook=unique)
    except MonitorError:
        raise
    except (OSError, ValueError, TypeError):
        raise MonitorError("entrada de workflow inválida ou indisponível") from None


def result(operation, error=None):
    return {"version": 1, "operation_id": operation["operation_id"], "accepted": True,
            "publication": operation["state"], "binding": operation["binding_state"],
            "binding_reason": operation.get("binding_reason"),
            "error": error or operation.get("error")}


class Coordinator:
    def __init__(self, store, config, publisher=None, runtime=None, github=None):
        self.store, self.config = store, config
        self.journal = Journal(store)
        self.publisher = publisher or Publisher(self.journal)
        self.runtime = runtime or Runtime(config["runtime"], timeout=config["timing"]["timeout"])
        self.github = github or GitHub(timeout=config["timing"]["timeout"])

    def transition(self, payload):
        operation = self.journal.accept(payload)
        try:
            operation = self.publisher.publish(operation["operation_id"])
            if operation["state"] == "published" and not operation.get("error") and operation["payload"].get("binding"):
                operation = self.attempt_binding(operation)
            return result(operation)
        except (MonitorError, OSError, sqlite3.Error) as error:
            try:
                current = self.journal.get(operation["operation_id"]) or operation
            except (MonitorError, OSError, sqlite3.Error):
                current = operation  # A aceitação anterior já foi confirmada duravelmente.
            return result(current, error.category if isinstance(error, MonitorError) else "instrumentação indisponível")

    def refresh_for_binding(self, operation):
        repository, issue = operation["repository"], operation["issue"]
        targets = [target for target in self.config["targets"] if target["repository"] == repository]
        if not targets:
            raise MonitorError("vínculo fora dos alvos autorizados")
        try:
            lease = self.store.acquire_collector("collect")
        except MonitorError as error:
            if error.category not in {"coleta já possui dono", "coleta reservada ao observador"}:
                raise
            self.store.request_collection()
            return
        with lease:
            collector = Collector(self.store, self.config, github=self.github, runtime=self.runtime, epoch=lease.epoch)
            collector.update("inventory:" + repository, self.config["timing"]["github_interval"],
                             lambda: self.github.inventory(repository, targets[0]["milestones"]), force=True)
            def comments():
                raw, _comment, record = self.publisher.current(repository, issue, operation["run_id"])
                if not record or not self.publisher.verify_operation(operation, record):
                    raise MonitorError("abertura publicada não confirmada")
                return comments_snapshot(raw, repository, issue)
            collector.update(f"comments:{repository}:{issue}", self.config["timing"]["github_interval"], comments, force=True)

    def attempt_binding(self, operation):
        op_id, payload = operation["operation_id"], operation["payload"]
        binding = payload["binding"]
        intent = self.journal.binding_intent(operation)
        session_id = binding.get("session_id") or (intent or {}).get("session_id")
        if not session_id:
            return self.journal.update(op_id, binding_state="pending", binding_reason="session_unavailable", error="vínculo indisponível")
        if not self.config["runtime"]["enabled"]:
            return self.journal.update(op_id, binding_state="failed", binding_reason="runtime_disabled", error="vínculo indisponível")
        try:
            self.refresh_for_binding(operation)
            inventory_source = self.store.source("inventory:" + operation["repository"])
            comments_source = self.store.source(f"comments:{operation['repository']}:{operation['issue']}")
            if inventory_source.get("error") or comments_source.get("error"):
                raise MonitorError("cache aguarda atualização")
            inventory = inventory_source.get("payload") or {}
            allowed = {number for target in self.config["targets"] if target["repository"] == operation["repository"] for number in target["milestones"]}
            if not any(item["number"] == operation["issue"] and item["milestone"] in allowed and item["state"] == "open"
                       for item in inventory.get("issues", [])):
                raise MonitorError("vínculo fora dos alvos autorizados")
            execution = payload["execution"]
            interval = find_incarnation(self.store, operation["repository"], operation["issue"], operation["run_id"],
                                        payload["stage"], payload["worker_id"], execution["kind"], execution["id"])
            key = incarnation_key(operation["repository"], operation["issue"], operation["run_id"], interval)
            existing = self.store.bindings().get(key)
            if existing:
                if (existing.get("invalidated") or existing["session_id"] != session_id or existing["worktree"] != os.path.realpath(binding["worktree"])
                        or existing["context"] != self.runtime.context()):
                    raise MonitorError("vínculo anterior exige remoção explícita")
                self.runtime.location(session_id, existing["worktree"])
                git_identity(existing["worktree"], existing["repository"], existing.get("branch"))
                if binding.get("branch") is not None and binding["branch"] != existing.get("branch"):
                    raise MonitorError("vínculo anterior exige remoção explícita")
            else:
                args = argparse.Namespace(issue=payload["issue"], run_id=payload["run_id"], stage=payload["stage"],
                    worker_id=payload["worker_id"], execution_kind=execution["kind"], execution_id=execution["id"],
                    session_id=session_id, worktree=binding["worktree"], branch=binding.get("branch"))
                bind(self.store, self.runtime, args)
            return self.journal.update(op_id, binding_state="bound", binding_reason="bound")
        except MonitorError as error:
            pending = error.category in {"incarnação ausente, terminal ou ambígua", "issue ausente do inventário", "cache mudou durante bind; tente novamente", "cache aguarda atualização"}
            return self.journal.update(op_id, binding_state="pending" if pending else "failed",
                                       binding_reason="cache_pending" if pending else "validation_failed", error="vínculo indisponível")

    def reconcile(self, issue_url, run_id, authorized=False, binding_input=None):
        if authorized is not True:
            raise MonitorError("reconciliação exige coordenador autorizado explícito")
        if not isinstance(issue_url, str) or len(issue_url) > 512:
            raise MonitorError("escopo de workflow inválido")
        repository, issue = issue_identity(issue_url)
        identifier(run_id)
        selected = None
        if binding_input is not None:
            if (not isinstance(binding_input, dict) or set(binding_input) != {"version", "operation_id", "session_id"}
                    or type(binding_input["version"]) is not int or binding_input["version"] != 1):
                raise MonitorError("entrada de vínculo inválida")
            selected = self.journal.get(binding_input["operation_id"])
            if not selected or (selected["repository"], selected["issue"], selected["run_id"]) != (repository, issue, run_id):
                raise MonitorError("intenção de vínculo fora do escopo")
            self.journal.accept_binding(selected["operation_id"], binding_input["session_id"])
        operations = self.journal.operations(repository, issue, run_id)
        pending = [op for op in operations if op["state"] != "published" or op["binding_state"] in {"pending", "failed"}]
        if selected and all(op["operation_id"] != selected["operation_id"] for op in pending):
            pending.append(selected)
        results = []
        for operation in pending:
            results.append(self.transition(operation["payload"]))
        from .reconciliation import reconcile_runtime
        generated, runtime_report = reconcile_runtime(self, repository, issue, run_id)
        results.extend(generated)
        return {"version": 1, "issue": issue_url, "run_id": run_id, "operations": results[:20],
                "total": len(results), "truncated": len(results) > 20,
                "runtime": runtime_report,
                "remaining": sum(r["publication"] != "published" or r["binding"] in {"pending", "failed"} or bool(r["error"]) for r in results)
                             + runtime_report["deferred"] + runtime_report["results_unverified"] + runtime_report["unmeasured"]
                             + runtime_report["transitions_pending"]
                             + bool(runtime_report.get("error"))}


def workflow_cli(args, config):
    try:
        if args.workflow_action == "transition":
            payload = normalize_operation(read_input(args.input))
        else:
            if not args.coordinator:
                raise MonitorError("reconciliação exige coordenador autorizado explícito")
            issue_identity(args.issue)
            identifier(args.run_id)
        coordinator = Coordinator(Store(args.state_dir or state_path()), config)
        if args.workflow_action == "transition":
            value = coordinator.transition(payload)
            success = value["publication"] == "published" and value["binding"] not in {"pending", "failed"} and not value["error"]
        else:
            value = coordinator.reconcile(args.issue, args.run_id, authorized=args.coordinator,
                                          binding_input=read_input(args.binding_input) if args.binding_input else None)
            success = value["remaining"] == 0
        print(json.dumps(value, ensure_ascii=False))
        return 0 if success else 1
    except (MonitorError, OSError, sqlite3.Error) as error:
        category = error.category if isinstance(error, MonitorError) else "instrumentação indisponível"
        print(json.dumps({"version": 1, "accepted": False, "publication": "not_attempted", "binding": "not_attempted", "error": category}, ensure_ascii=False))
        return 1
