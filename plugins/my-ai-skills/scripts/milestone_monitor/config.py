"""Configuração explícita e versionada, sem descoberta de projetos."""
import json
import os
from pathlib import Path

from .common import MonitorError, REPO, server_url

DEFAULTS = {"github_interval": 60, "runtime_interval": 15, "github_ttl": 180,
            "activity_ttl": 45, "timeout": 10}


def config_path():
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "aew/config.json"


def state_path():
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "aew"


def load(path=None):
    path = Path(path) if path else config_path()
    try:
        data = json.loads(path.read_text()) if path.exists() else {"schema_version": 1, "targets": []}
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            raise ValueError()
        targets = {}
        if not isinstance(data.get("targets", []), list):
            raise ValueError()
        for target in data.get("targets", []):
            repo, numbers = target["repository"], target["milestones"]
            if not isinstance(repo, str) or not REPO.fullmatch(repo) or not isinstance(numbers, list):
                raise ValueError()
            if any(type(n) is not int or n <= 0 for n in numbers):
                raise ValueError()
            targets.setdefault(repo, set()).update(numbers)
        runtime = data.get("runtime", {"enabled": False})
        if not isinstance(runtime, dict) or type(runtime.get("enabled", False)) is not bool:
            raise ValueError()
        if runtime.get("expected_version", "2.2.5") != "2.2.5":
            raise MonitorError("contrato OpenCode incompatível")
        if runtime.get("server") is not None:
            runtime["server"] = server_url(runtime["server"])
        timing = {**DEFAULTS, **data.get("timing", {})}
        if set(timing) != set(DEFAULTS) or any(type(v) not in (float, int) or not 0 < v <= 86400 for v in timing.values()):
            raise ValueError()
        return {"schema_version": 1, "targets": [{"repository": r, "milestones": sorted(ns)} for r, ns in sorted(targets.items())],
                "runtime": {"enabled": runtime.get("enabled", False), "expected_version": "2.2.5", "server": runtime.get("server")},
                "timing": timing}
    except MonitorError:
        raise
    except (OSError, ValueError, TypeError, KeyError):
        raise MonitorError("configuração inválida") from None
