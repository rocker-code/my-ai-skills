#!/usr/bin/env python3
"""Read-only disposable GitHub sources, not a workflow persistence protocol."""
import json
import os
from pathlib import Path
import re
import sys


def response(args, state):
    """Small allowlist: unsupported requests and all writes fail closed."""
    if args[:1] == ["api"]:
        endpoint = args[1:] if args[1:2] != ["--paginate"] else args[2:]
        if len(endpoint) != 1:
            raise ValueError("unsupported API arguments")
        match = re.fullmatch(r"repos/disposable/recovery/(issues|pulls)/(\d+)", endpoint[0])
        if match:
            kind, number = match.groups()
            return state["issues" if kind == "issues" else "pulls"][number]
        raise ValueError("unsupported endpoint")
    if args[:2] in (["issue", "view"], ["pr", "view"]):
        if len(args) < 3:
            raise ValueError("missing identifier")
        kind = "issues" if args[0] == "issue" else "pulls"
        number = args[2].rstrip("/").split("/")[-1]
        # JSON selection is accepted, never a shell/filter or write interface.
        if args[3:] and not (len(args) == 5 and args[3] == "--json"):
            raise ValueError("unsupported view arguments")
        return state[kind][number]
    if args[:2] == ["pr", "list"] and len(args) == 2:
        return list(state["pulls"].values())
    if args[:2] == ["issue", "list"] and len(args) == 2:
        return list(state["issues"].values())
    if args[:2] == ["pr", "checks"] and len(args) == 3:
        return state["pulls"][args[2]]["statusCheckRollup"]
    raise ValueError("GitHub fixture refused request")


def main():
    root = Path(os.environ["RESUME_GH_ROOT"])
    args = sys.argv[1:]
    with (root / "calls.jsonl").open("a") as log:
        log.write(json.dumps(args) + "\n")
    try:
        result = response(args, json.loads((root / "state.json").read_text()))
    except (ValueError, KeyError, TypeError):
        print("GitHub fixture refused request", file=sys.stderr)
        return 77
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
