#!/usr/bin/env python3
"""Real OpenCode V2/OpenSpec smoke in an isolated HOME; no model credentials.

Run: python3 tests/smoke_global_opencode.py
Prints the retained disposable evidence directory. Never writes to the real HOME.
"""
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile
import time
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
ENTRY_REVISION = "8ddd9e60fbe773ca363293b8f0ff3a7b452eed37"
ACTIONS = {"explore": "openspec-explore", "propose": "openspec-propose",
           "apply": "openspec-apply-change", "archive": "openspec-archive-change"}


def main():
    cli = shutil.which("opencode")
    openspec = shutil.which("openspec")
    if not cli or not openspec:
        raise RuntimeError("Real opencode V2 and openspec CLIs required")
    base = Path(tempfile.mkdtemp(prefix="smoke-global-opencode-", dir="/tmp/opencode"))
    home = base / "home"
    home.mkdir()
    env = {key: os.environ[key] for key in ("PATH", "LANG", "TERM") if key in os.environ}
    env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"),
               XDG_DATA_HOME=str(home / ".local/share"), XDG_CACHE_HOME=str(home / ".cache"),
               XDG_STATE_HOME=str(home / ".local/state"), OPENSPEC_TELEMETRY="0",
               PYTHONDONTWRITEBYTECODE="1", OPENCODE_PASSWORD=secrets.token_hex(24))
    results = {"base": str(base), "installer_revision": ENTRY_REVISION, "locations": {}}
    server = None

    def run(args, cwd=ROOT, timeout=90):
        result = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                                text=True, timeout=timeout)
        if result.returncode:
            raise RuntimeError(f"{args[:4]} returned {result.returncode}: {result.stderr[:400]}")
        return result.stdout

    try:
        results["opencode"] = run([cli, "--version"]).strip()
        results["openspec"] = run([openspec, "--version"]).strip()
        run(["python3", str(ROOT / "scripts/install-global"), "--agent", "opencode",
             "--revision", ENTRY_REVISION, "--source", str(ROOT)])
        active = home / ".local/share/my-ai-skills/active"
        assert json.loads((active / "manifest.json").read_text())["revision"] == ENTRY_REVISION

        projects = []
        for name in ("project-one", "project-two"):
            repo = base / name
            repo.mkdir()
            run(["git", "init", "-q", str(repo)])
            (repo / "README.md").write_text("Disposable smoke project\n")
            run(["git", "add", "README.md"], cwd=repo)
            run(["git", "-c", "user.name=Smoke", "-c", "user.email=smoke@example.org",
                 "commit", "-qm", "base"], cwd=repo)
            run([openspec, "init", "--tools", "opencode", str(repo)])
            projects.append(repo)
        worktree = base / "worktree with spaces"
        run(["git", "worktree", "add", "-qb", "smoke-worktree", str(worktree)], cwd=projects[0])
        # OpenSpec's generated integration was untracked in the source repo;
        # this independent disposable worktree needs its own authorized init.
        run([openspec, "init", "--tools", "opencode", str(worktree)])
        locations = (*projects, worktree)
        for location in locations:
            for action, skill in ACTIONS.items():
                assert (location / ".opencode/commands" / f"opsx-{action}.md").is_file()
                assert (location / ".opencode/skills" / skill / "SKILL.md").is_file()

        server = subprocess.Popen([cli, "serve", "--hostname", "127.0.0.1", "--port", "0"],
                                  cwd=projects[0], env=env, stdout=subprocess.PIPE,
                                  stderr=(base / "server-stderr.log").open("w"), text=True)
        line = server.stdout.readline()
        match = re.search(r"http://127\.0\.0\.1:\d+", line)
        if not match:
            raise RuntimeError("No private OpenCode server URL")
        url = match.group()

        def api(method, endpoint, cwd, body=None):
            if endpoint in ("/api/command", "/api/skill"):
                endpoint += "?" + urlencode({"location[directory]": str(cwd)})
            args = [cli, "--server", url, "api", method, endpoint]
            if body is not None:
                args += ["--data", json.dumps(body)]
            output = run(args, cwd=cwd)
            return json.loads(output) if output.strip() else None

        for location in locations:
            # Registry loading is asynchronous; the first location-scoped GET
            # often lists only built-ins. Do not use that as negative evidence.
            deadline = time.monotonic() + 25
            while True:
                commands = api("get", "/api/command", location)
                skills = api("get", "/api/skill", location)
                assert commands["location"]["directory"] == str(location), commands["location"]
                assert skills["location"]["directory"] == str(location), skills["location"]
                command_names = {item["name"] for item in commands["data"]}
                skill_map = {item["id"]: item for item in skills["data"]}
                if all(f"opsx-{action}" in command_names and skill in skill_map
                       for action, skill in ACTIONS.items()) and "apply-issue" in skill_map:
                    break
                if time.monotonic() > deadline:
                    raise RuntimeError(f"Discovery timeout in {location}: {command_names}, {set(skill_map)}")
                time.sleep(0.5)
            assert Path(skill_map["apply-issue"]["path"]).resolve() == (
                active / "skills/apply-issue/SKILL.md").resolve()
            record = {"directory": str(location), "commands": sorted(command_names),
                      "skills": {skill: skill_map[skill]["path"] for skill in ACTIONS.values()},
                      "global_skill": skill_map["apply-issue"]["path"], "invoked": {}}
            for action, skill in ACTIONS.items():
                session = api("post", "/api/session", location,
                              {"location": {"directory": str(location)}})["data"]
                assert session["location"]["directory"] == str(location)
                session_id = session["id"]
                api("post", f"/api/experimental/session/{session_id}/skill", location,
                    {"id": skill, "resume": False})
                messages = api("get", f"/api/session/{session_id}/message", location)["data"]
                assert any(msg.get("type") == "skill" and msg.get("skill") == skill
                           and msg.get("text") for msg in messages)
                api("post", f"/api/session/{session_id}/command", location,
                    {"name": f"opsx-{action}", "text": "smoke (no model credentials)"})
                deadline = time.monotonic() + 10
                while True:
                    messages = api("get", f"/api/session/{session_id}/message", location)["data"]
                    if any(msg.get("type") == "user" and msg.get("text") and
                           msg.get("text") != "smoke (no model credentials)" for msg in messages):
                        break
                    if time.monotonic() > deadline:
                        raise RuntimeError(f"Command did not expand in {session_id}")
                    time.sleep(0.2)
                record["invoked"][action] = {"session_id": session_id,
                                              "skill_message": True, "expanded_command": True}
            results["locations"][location.name] = record
        print("PASS: real OpenCode/OpenSpec discovery and invocation in two projects + worktree")
    finally:
        if server is not None:
            server.terminate()
            server.wait(timeout=10)
        (base / "results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        print(f"Evidence: {base}/results.json and disposable server log under {home}")


if __name__ == "__main__":
    main()
