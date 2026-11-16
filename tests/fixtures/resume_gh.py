#!/usr/bin/env python3
"""Disposable GitHub API for the recovery smoke; every request is audited."""
import json
import os
from pathlib import Path
import sys

root = Path(os.environ["RESUME_GH_ROOT"])
args = sys.argv[1:]
with (root / "calls.jsonl").open("a") as log:
    log.write(json.dumps(args) + "\n")
state = json.loads((root / "state.json").read_text())

if args[:2] == ["api", "--paginate"] and len(args) == 3 and args[2].startswith("repos/disposable/recovery/issues/") and args[2].endswith("/comments"):
    number = int(args[2].split("/")[4])
    print(json.dumps([c for c in state["comments"] if c["issue"] == number]))
elif args[:2] == ["api", "--method"] and len(args) >= 4 and args[2] == "PATCH" and args[3].startswith("repos/disposable/recovery/issues/comments/"):
    number = int(args[3].split("/")[-1])
    body = next((a[5:] for a in args if a.startswith("body=")), None)
    if not os.environ.get("RESUME_GH_SEED") or body is None:
        sys.exit(77)
    next(c for c in state["comments"] if c["id"] == number)["body"] = body
    (root / "state.json").write_text(json.dumps(state))
    print("{}")
elif args and args[0] == "api" and len(args) >= 2 and args[1].startswith("repos/disposable/recovery/issues/") and args[1].endswith("/comments") and any(a.startswith("body=") for a in args):
    if not os.environ.get("RESUME_GH_SEED"):
        sys.exit(77)
    number = int(args[1].split("/")[4])
    state["comments"].append({"id": len(state["comments"]) + 1, "issue": number,
                              "body": next(a[5:] for a in args if a.startswith("body="))})
    (root / "state.json").write_text(json.dumps(state))
    print("{}")
elif args[:2] == ["issue", "view"] and len(args) >= 3:
    number = int(args[2].split("/")[-1])
    print(json.dumps({"number": number, "url": args[2], "title": f"Fixture #{number}", "state": "OPEN"}))
elif args[:2] == ["pr", "view"] and len(args) >= 3:
    print(json.dumps(state["pr"]))
elif args[:2] == ["pr", "list"]:
    print(json.dumps([state["pr"]] if state.get("pr") else []))
else:
    print("GitHub fixture refused request", file=sys.stderr)
    sys.exit(77)
