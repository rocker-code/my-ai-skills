#!/usr/bin/env python3
"""Smoke real opt-in de uma sessão própria explicitamente informada.

Não publica ID/payload, não persiste dados e não lê mensagens. O caller deve
fornecer AEW_SMOKE_SESSION_ID de sua própria sessão autorizada.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from milestone_monitor.common import MonitorError, identifier
from milestone_monitor.runtime import Runtime, git_identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()
    sid = identifier(os.environ.get("AEW_SMOKE_SESSION_ID"))
    cli = subprocess.run(["opencode", "--version"], capture_output=True, text=True, timeout=10, check=True)
    assert cli.stdout.strip() == "opencode v2.2.5", "CLI fora do freeze"
    runtime = Runtime({"enabled": True, "expected_version": "2.2.5", "server": None})
    context = runtime.context()
    directory = os.path.realpath(args.worktree)
    branch = git_identity(directory, args.repository)
    runtime.location(sid, directory)
    observation = runtime.collect({"binding:smoke": {"session_id": sid, "worktree": directory, "repository": args.repository,
                                                     "branch": branch, "context": context}}, {"binding:smoke"})
    assert observation["binding:smoke"]["state"] == "active", "própria sessão não observada ativa"
    try:
        runtime.location("ses_aew_deliberately_absent_43", directory)
    except MonitorError as error:
        assert error.category == "ausente", "ausência não categorizada"
    else:
        raise AssertionError("ID deliberadamente ausente encontrado")
    print("PASS: CLI/servidor 2.2.5, envelopes oficiais, localização própria, foreground ativo, ausência categorizada.")
    print("Sem mensagens, payload persistido, IDs publicados ou controle de agentes. 401 real NOT RUN (fixture negativa cobre consumidor).")


if __name__ == "__main__":
    main()
