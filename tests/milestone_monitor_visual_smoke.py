#!/usr/bin/env python3
"""Smoke visual curses em servidor tmux próprio, somente dados simulados."""
import argparse
import curses
import os
import queue
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from milestone_monitor_visual_fixtures import visual_model, collapsed_model
from milestone_monitor_fixtures import DEFAULTS
from milestone_monitor.common import utc_now
from milestone_monitor.store import Store
from milestone_monitor.tui import dashboard, UIState


def child(directory, no_color, ascii_only, collapsed=False):
    directory = Path(directory)
    value = collapsed_model() if collapsed else visual_model()
    now = utc_now().isoformat()
    value["health"][0]["fetched_at"] = now
    value["milestones"][0]["title"] += " — DADOS SIMULADOS"
    for group in value["milestones"]:
        for issue in group["issues"]:
            if issue["group"] == "running":
                issue["workers"] = [{"state": "running", "stage": "apply", "worker": "fixture",
                                     "label": "executando (simulado)", "execution": None,
                                     "opened_at": now, "last_observed_at": now}]
    class Background:
        models = queue.Queue()
        session_started = utc_now()
        def request(self): pass
        def close(self): pass
    store = Store(directory/"state")
    state = UIState()
    state.reconcile(value)
    if not collapsed:
        state.action("enter", value)
    store.put_local("ui", state.save())
    curses.wrapper(dashboard, store, {"timing": DEFAULTS}, Background(), value, no_color, ascii_only)
    (directory/"exit").write_text("0")
    # Mantém a pane até o driver ler o resultado, sem processo de painel ativo.
    time.sleep(10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--child", type=Path)
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--ascii", action="store_true")
    parser.add_argument("--collapsed", action="store_true")
    args = parser.parse_args()
    if args.child:
        child(args.child, args.no_color, args.ascii, args.collapsed)
        return
    if not args.output_dir:
        parser.error("--output-dir é obrigatório")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for mode, collapsed in ((mode, collapsed) for mode in ("color", "mono-ascii") for collapsed in (False, True)):
        with tempfile.TemporaryDirectory(prefix="aew-visual-", dir="/tmp/opencode") as directory:
            socket = f"aew-visual-{os.getpid()}-{mode}-{int(collapsed)}"
            def tmux(*argv):
                return subprocess.run(["tmux", "-L", socket, *argv], capture_output=True, text=True,
                                      check=True, timeout=10).stdout
            command = ["env", "TERM=xterm-256color", "PYTHONDONTWRITEBYTECODE=1", sys.executable, "-B", str(Path(__file__).resolve()), "--child", directory]
            if mode == "mono-ascii":
                command += ["--no-color", "--ascii"]
            if collapsed:
                command += ["--collapsed"]
            label = mode + ("-collapsed" if collapsed else "")
            try:
                tmux("new-session", "-d", "-x", "238", "-y", "54", "-s", "visual", shlex.join(command))
                # Espera por frame efetivo, não por um atraso arbitrário de boot.
                # Cada cenário usa socket próprio, inclusive entre dois modos
                # consecutivos, sem disputar o servidor que acabou de sair.
                deadline = time.monotonic()+8
                while "DADOS SIMULADOS" not in tmux("capture-pane", "-p", "-t", "visual"):
                    if time.monotonic() >= deadline:
                        raise AssertionError("curses não apresentou o primeiro frame da fixture")
                    time.sleep(.1)
                for width, height in ((238, 54), (110, 30), (80, 24), (40, 12)):
                    tmux("resize-window", "-t", "visual", "-x", str(width), "-y", str(height))
                    time.sleep(.4)
                    plain = tmux("capture-pane", "-p", "-t", "visual")
                    ansi = tmux("capture-pane", "-p", "-e", "-t", "visual")
                    name = f"{label}-{width}x{height}"
                    (args.output_dir/(name+".txt")).write_text(plain)
                    (args.output_dir/(name+".ansi")).write_text(ansi)
                    if width == 238:
                        expected_values = ("DADOS SIMULADOS", "40 milestones", "0% (0/5)", "concluídas" if mode == "color" else "concluidas") if collapsed else ("DADOS SIMULADOS", "Workflow", "Tempo registrado", "20% (1/5)")
                        for expected in expected_values:
                            if expected not in plain:
                                raise AssertionError(f"{name}: faltou {expected}")
                    if mode == "mono-ascii" and not plain.isascii():
                        raise AssertionError("fallback ASCII produziu Unicode")
                # Vai à issue executando e exerce filtros, sanfonas e detalhes.
                if collapsed:
                    tmux("send-keys", "-t", "visual", "Enter")
                tmux("send-keys", "-t", "visual", "j", "j")
                time.sleep(.3)
                selected = tmux("capture-pane", "-p", "-t", "visual")
                if "Aplicar" not in selected:
                    raise AssertionError("40x12 perdeu etapa atual selecionada")
                (args.output_dir/(label+"-40x12-selected.txt")).write_text(selected)
                tmux("send-keys", "-t", "visual", "Enter", "PageDown", "PageUp", "Enter", "f", "f", "f", "f", "f", "c", "a", "r", "q")
                for _ in range(40):
                    if (Path(directory)/"exit").exists():
                        break
                    time.sleep(.1)
                if not (Path(directory)/"exit").exists():
                    raise AssertionError("curses não confirmou saída normal")
                if not Store(Path(directory)/"state").local("ui"):
                    raise AssertionError("preferências não persistiram")
                print(f"PASS {label}: 238x54 → 110x30 → 80x24 → 40x12, navegação/detalhes/filtro/q; DADOS SIMULADOS")
            finally:
                subprocess.run(["tmux", "-L", socket, "kill-server"], capture_output=True, check=False)


if __name__ == "__main__":
    main()
