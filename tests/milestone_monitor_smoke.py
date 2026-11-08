#!/usr/bin/env python3
"""Smoke curses/tmux isolado; cache artificial explicitamente identificado.

Não consulta GitHub/OpenCode e não prova integração de fontes externas.
"""
import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from datetime import timedelta
from pathlib import Path

from milestone_monitor_fixtures import CONFIG, ISSUE, ROOT, inventory, record, event, snapshots, publish, STARTED
from milestone_monitor.store import Store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="aew43-smoke-", dir="/tmp/opencode") as directory:
        directory = Path(directory)
        config = json.loads(json.dumps(CONFIG))
        config["targets"] = [{"repository": "owner/repo", "milestones": [1, 2]}, {"repository": "other/repo", "milestones": [1]}]
        cfg = directory/"config.json"
        cfg.write_text(json.dumps(config))
        store = Store(directory/"state")
        groups = [{"repository": "owner/repo", "number": n, "title": "FIXTURE DE TESTE"} for n in [1, 2]]
        publish(store, "inventory:owner/repo", inventory([ISSUE], groups))
        publish(store, "comments:owner/repo:7", snapshots(record(event("stage_started"), event("wait_started", 10, reason="owner_input"))))
        publish(store, "inventory:other/repo", {"milestones": [{"repository": "other/repo", "number": 1, "title": "FIXTURE DE TESTE"}],
                                                   "issues": [{**ISSUE, "repository": "other/repo", "url": "https://github.com/other/repo/issues/7"}]})
        # Wrapper records actual exit status while leaving the pane available.
        wrapper = directory/"run.py"
        wrapper.write_text("import subprocess,pathlib,time\n" +
                           f"p=subprocess.run({[str(ROOT/'scripts/aew'), 'dashboard', '--offline', '--no-color', '--ascii', '--config', str(cfg), '--state-dir', str(directory/'state')]!r})\n" +
                           f"pathlib.Path({str(directory/'exit')!r}).write_text(str(p.returncode))\ntime.sleep(30)\n")
        socket = "aew43-" + str(os.getpid())
        def tmux(*argv):
            return subprocess.run(["tmux", "-L", socket, *argv], capture_output=True, text=True, check=True, timeout=10).stdout
        try:
            tmux("new-session", "-d", "-x", "110", "-y", "30", "-s", "monitor", shlex.join([sys.executable, "-B", str(wrapper)]))
            time.sleep(0.5)
            tmux("send-keys", "-t", "monitor", "a")
            time.sleep(0.3)
            wide = tmux("capture-pane", "-p", "-t", "monitor")
            if "FIXTURE DE TESTE" not in wide or "Aplicar" not in wide:
                raise AssertionError("curses não apresentou inventário/régua fixture")
            (args.output_dir/"tmux-110x30.txt").write_text(wide)
            tmux("send-keys", "-t", "monitor", "f", "f", "f", "f", "f", *(["k"]*20), "j", "j", "j", "Enter", "]", "[", "PageDown", "PageUp")
            tmux("resize-window", "-t", "monitor", "-x", "40", "-y", "12")
            time.sleep(0.5)
            narrow = tmux("capture-pane", "-p", "-t", "monitor")
            (args.output_dir/"tmux-40x12.txt").write_text(narrow)
            if "Aplicar" not in narrow:
                raise AssertionError("terminal estreito perdeu etapa atual")
            tmux("send-keys", "-t", "monitor", "q")
            for _ in range(30):
                if (directory/"exit").exists():
                    break
                time.sleep(0.1)
            if (directory/"exit").read_text() != "0":
                raise AssertionError("dashboard não terminou normalmente")
            if not Store(directory/"state").local("ui"):
                raise AssertionError("preferências não persistiram")
            print("PASS: curses/tmux 110x30 -> 40x12, navegação/detalhes/filtro/histórico/q; cache fixture, sem fontes reais")
        finally:
            subprocess.run(["tmux", "-L", socket, "kill-server"], capture_output=True, check=False)


if __name__ == "__main__":
    main()
