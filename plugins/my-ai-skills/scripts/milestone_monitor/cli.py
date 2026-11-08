"""Comandos públicos do monitor; nenhum comando controla agentes."""
import argparse
import curses
import json
import sqlite3
import sys

from .common import MonitorError, issue_identity, utc_now
from .config import load, state_path
from .store import Store
from .collector import Collector, Background
from .runtime import Runtime, bind, find_incarnation
from .projection import incarnation_key, model
from .tui import dashboard, ascii_locale


def parser():
    root = argparse.ArgumentParser(prog="aew", description="Milestone Monitor: leitura GitHub/workflow/OpenCode; sem alvos não há descoberta.")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("dashboard", "collect", "bind", "unbind"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--config", help="config JSON schema_version 1 (XDG_CONFIG_HOME/aew/config.json)")
        cmd.add_argument("--state-dir", help="cache SQLite (XDG_STATE_HOME/aew)")
        if name == "dashboard":
            cmd.add_argument("--offline", action="store_true")
            cmd.add_argument("--no-color", action="store_true")
            cmd.add_argument("--ascii", action="store_true")
        elif name == "collect":
            cmd.add_argument("--once", action="store_true", required=True)
        else:
            for arg in ("issue", "run-id", "stage", "worker-id", "execution-id"):
                cmd.add_argument("--" + arg, required=True)
            cmd.add_argument("--execution-kind", choices=("worker", "process", "job", "test_run", "ci_run"), required=True)
            if name == "bind":
                cmd.add_argument("--session-id", required=True)
                cmd.add_argument("--worktree", required=True)
                cmd.add_argument("--branch")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        config = load(args.config)
        if args.command == "dashboard" and (not sys.stdin.isatty() or not sys.stdout.isatty()):
            raise MonitorError("dashboard exige TTY; use aew collect --once")
        store, started = Store(args.state_dir or state_path()), utc_now()
        if args.command == "collect":
            Collector(store, config).collect(force=True)
            value = model(store, config, started)
            # Public headless projection is the same metadata shown by the UI.
            print(json.dumps(value, ensure_ascii=False))
            health = value["health"] + [value["runtime_health"]]
            health += [issue[field] for group in value["milestones"] for issue in group["issues"] for field in ("comments_health", "pr_health")]
            return 1 if any(s.get("error") for s in health) else 0
        if args.command == "bind":
            bind(store, Runtime(config["runtime"], timeout=config["timing"]["timeout"]), args)
            print("Vínculo validado e salvo; não é prova de teste/CI.")
        elif args.command == "unbind":
            repo, number = issue_identity(args.issue)
            # Removal also works after the incarnation has ended; match exact
            # binding identity, never require an open run to remove stale links.
            for key, binding in store.bindings().items():
                if (binding["repository"], binding["issue"], binding["run_id"], binding["stage"], binding["worker_id"], binding["execution"]) == (
                    repo, number, args.run_id, args.stage, args.worker_id, {"kind": args.execution_kind, "id": args.execution_id}):
                    store.unbind(key)
            print("Vínculo exato removido; histórico preservado.")
        else:
            background = Background(Collector(store, config), started, args.offline)
            initial = model(store, config, started)
            background.start()
            try:
                curses.wrapper(dashboard, store, config, background, initial, args.no_color, args.ascii or ascii_locale())
            finally:
                background.close()
        return 0
    except (MonitorError, curses.error, sqlite3.Error, OSError) as error:
        category = (error.category if isinstance(error, MonitorError) else "terminal indisponível" if isinstance(error, curses.error)
                    else "armazenamento indisponível")
        print("aew: " + category, file=sys.stderr)
        return 1
