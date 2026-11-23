#!/usr/bin/env python3
"""Real native Codex smoke. No real GitHub writes or user config changes.

Requires --auth-cache (documented headless cache reuse) or a supported token
environment variable, and --controller-session with the caller's native ID.
Private artifacts remain in /tmp/opencode; copied credentials are always removed.
The gh backend alone is a fixture: Codex, OpenSpec, Git, tests and reservations
are real. This is not a production runtime adapter or scheduler.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {"explore": "openspec-explore", "propose": "openspec-propose",
           "apply": "openspec-apply-change", "verify": "openspec-verify-change",
           "archive": "openspec-archive-change"}
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,99}\Z")


def completed_thread(events, exit_code):
    """Unknown/failed/another thread never becomes successful completion."""
    ids = [e.get("thread_id") for e in events if e.get("type") == "thread.started"]
    if (exit_code or len(ids) != 1 or not isinstance(ids[0], str)
            or not SAFE_ID.fullmatch(ids[0])
            or not any(e.get("type") == "turn.completed" for e in events)
            or any(e.get("type") in ("turn.failed", "error") for e in events)):
        raise RuntimeError("BLOCKED: native thread ID or terminal completion unavailable")
    return ids[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auth-cache", type=Path, help="Explicit regular auth.json; never config.toml")
    parser.add_argument("--controller-session", required=True, help="Caller's real native session ID")
    args = parser.parse_args()
    if not SAFE_ID.fullmatch(args.controller_session):
        parser.error("Invalid controller native session ID")
    cli, openspec = shutil.which("codex"), shutil.which("openspec")
    if not cli or not openspec:
        raise RuntimeError("BLOCKED: real Codex and OpenSpec CLIs required; no OpenCode fallback")
    base = Path(tempfile.mkdtemp(prefix="smoke-global-codex-", dir="/tmp/opencode"))
    base.chmod(0o700)
    home = base / "home"
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True, mode=0o700)
    tools = base / "tools"
    tools.mkdir()
    for name in ("git", "gh", "jq", "curl", "python3", "openspec", "codex"):
        executable = shutil.which(name)
        if not executable:
            raise RuntimeError(f"BLOCKED: missing {name}")
        (tools / name).symlink_to(executable)
    env = {key: os.environ[key] for key in ("LANG", "TERM") if key in os.environ}
    env.update(HOME=str(home), CODEX_HOME=str(codex_home),
               XDG_CONFIG_HOME=str(home / ".config"), XDG_DATA_HOME=str(home / ".local/share"),
               XDG_CACHE_HOME=str(home / ".cache"), XDG_STATE_HOME=str(home / ".local/state"),
               PATH=f"{home}/.local/bin:{tools}:/usr/bin:/bin",
               PYTHONDONTWRITEBYTECODE="1", OPENSPEC_TELEMETRY="0")
    auth = codex_home / "auth.json"
    results = {"status": "BLOCKED", "base": str(base), "sessions": [], "locations": {},
               "github_backend": "fixture only; no hosted CI/review/merge proof",
               "controller_session": args.controller_session}
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    results["revision"] = revision

    def run(argv, cwd=ROOT, timeout=120, expected=0):
        result = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                                capture_output=True, text=True, timeout=timeout)
        if result.returncode != expected:
            # argv never contains auth values; don't dump arbitrary runtime logs.
            raise RuntimeError(f"{list(map(str, argv[:4]))}: exit={result.returncode}; expected={expected}; "
                               f"{result.stderr[:500]}")
        return result.stdout

    active = home / ".local/share/my-ai-skills/active"
    helper = active / "scripts/worktree-reservation"
    owners = {}
    thread_ids = set()

    def reservation(command, repo, session, *options):
        return json.loads(run([helper, command, "--path", repo, "--session", session,
                               "--json", *options]))

    def native(label, repo, prompt, *, writable=False):
        index = len(results["sessions"])
        context = base / f"context-{index}.json"
        # Native discovery is inspected, not reconstructed from skill bodies.
        visible = run([cli, "--cd", repo, "debug", "prompt-input", prompt], cwd=repo)
        (base / f"input-{index}.json").write_text(visible)
        command = [cli, "exec", "--json", "--ephemeral", "--ignore-user-config",
                   "--ignore-rules", "--sandbox", "workspace-write" if writable else "read-only",
                   "--cd", str(repo), "--add-dir", str(base / "project-one" / ".git")]
        full_prompt = prompt
        if writable:
            full_prompt += (
                f"\nBefore ANY write, read {context}. This is the real native thread.started ID "
                f"observed by the controller, not an invented identity. Verify your reservation "
                f"using {helper} verify --path {json.dumps(str(repo))} --session <that ID> --json. "
                "Checkpoint your own writes. Do not infer the old owner's ID. "
                "Do not create other worktrees or processes/agents.")
        events = []
        stderr = (base / f"stderr-{index}.log").open("w")
        process = subprocess.Popen(command, cwd=repo, env=env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=stderr, text=True)
        try:
            process.stdin.write(full_prompt)
            process.stdin.close()
            with (base / f"events-{index}.jsonl").open("w") as log, selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                pending = b""
                deadline = time.monotonic() + 600
                while selector.get_map():
                    ready = selector.select(max(0, deadline - time.monotonic()))
                    if not ready:
                        raise RuntimeError("BLOCKED: native execution missing terminal completion (600s)")
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        selector.unregister(process.stdout)
                        break
                    pending += chunk
                    lines = pending.split(b"\n")
                    pending = lines.pop()
                    for raw in lines:
                        line = raw.decode("utf-8")
                        log.write(line + "\n")
                        event = json.loads(line)
                        events.append(event)
                        if event.get("type") != "thread.started":
                            continue
                        thread = event.get("thread_id")
                        if not isinstance(thread, str) or not SAFE_ID.fullmatch(thread) or thread in thread_ids:
                            raise RuntimeError("BLOCKED: wrong/reused native identity")
                        if writable:
                            previous = owners[str(repo)]
                            run([helper, "handoff", "--path", repo, "--from-session", previous,
                                 "--to-session", thread, "--run", "codex-native-smoke", "--json"])
                            owners[str(repo)] = thread
                            context.write_text(json.dumps({"thread_id": thread, "source": "thread.started",
                                                           "issue": current_issue, "checkout": str(repo)}))
                code = process.wait(timeout=30)
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=15)
            stderr.close()
        thread = completed_thread(events, code)
        thread_ids.add(thread)
        if writable:
            reservation("checkpoint", repo, thread)
        response = "\n".join(e.get("item", {}).get("text", "") for e in events
                             if e.get("item", {}).get("type") == "agent_message")
        results["sessions"].append({"label": label, "thread_id": thread, "exit_code": code,
                                    "completed": True, "checkout": str(repo),
                                    "head": run(["git", "rev-parse", "HEAD"], cwd=repo).strip(),
                                    "events": f"events-{index}.jsonl"})
        return response, visible, events

    current_issue = None
    try:
        results["codex"] = run([cli, "--version"]).strip()
        results["openspec"] = run([openspec, "--version"]).strip()
        help_text = run([cli, "exec", "--help"])
        if not all(flag in help_text for flag in ("--json", "--cd", "--ephemeral", "--sandbox")):
            raise RuntimeError("BLOCKED: required native exec flags unavailable")
        if args.auth_cache:
            source = args.auth_cache.absolute()
            if source.is_symlink() or not source.is_file() or source.name != "auth.json":
                raise RuntimeError("BLOCKED: auth cache must be an explicit regular auth.json")
            with auth.open("xb") as output:
                auth.chmod(0o600)
                output.write(source.read_bytes())
        else:
            for variable, option in (("CODEX_ACCESS_TOKEN", "--with-access-token"),
                                     ("OPENAI_API_KEY", "--with-api-key")):
                if os.environ.get(variable):
                    login = subprocess.run([cli, "login", option], input=os.environ[variable],
                                           cwd=base, env=env, capture_output=True, text=True, timeout=60)
                    if login.returncode:
                        raise RuntimeError("BLOCKED: isolated token login failed")
                    break
        login = subprocess.run([cli, "login", "status"], env=env, capture_output=True,
                               text=True, timeout=30)
        results["login_exit"] = login.returncode
        if login.returncode:
            raise RuntimeError("BLOCKED: authenticate disposable CODEX_HOME via supported token login or --auth-cache")
        runner = ("import importlib.machinery,sys;"
                  "m=importlib.machinery.SourceFileLoader('installer',sys.argv[1]).load_module();"
                  "source=sys.argv[2];sys.argv=[sys.argv[1],*sys.argv[3:]];"
                  "original=m.install;m.install=lambda args:original(args,source=source);sys.exit(m.main())")
        run(["python3", "-c", runner, ROOT / "scripts/install-global", ROOT,
             "--agent", "codex", "--revision", revision])
        assert not (home / ".config/opencode").exists()
        manifest = json.loads((active / "manifest.json").read_text())
        assert manifest["revision"] == revision
        profile = json.loads(run([openspec, "config", "list", "--json"]))
        workflows = list(dict.fromkeys([*profile.get("workflows", ["explore", "propose", "apply", "archive"]),
                                       "verify"]))
        run([openspec, "config", "set", "workflows", json.dumps(workflows)])
        run([openspec, "config", "set", "profile", "custom"])
        scope = ["--scope", "project"] if "--scope" in run([openspec, "init", "--help"]) else []
        projects = []
        for name in ("project-one", "project-two"):
            repo = base / name
            repo.mkdir()
            run(["git", "init", "-q", repo])
            run(["git", "config", "user.name", "Smoke"], cwd=repo)
            run(["git", "config", "user.email", "smoke@example.org"], cwd=repo)
            (repo / "README.md").write_text("Disposable Codex native smoke\n")
            if name == "project-two":
                personal = repo / "openspec/specs/personal/spec.md"
                personal.parent.mkdir(parents=True)
                personal.write_text("# personal contract\n")
                (repo / "openspec/config.yaml").write_text("schema: spec-driven\n# custom configuration\n")
            run([openspec, "init", "--tools", "claude,codex" if name == "project-two" else "codex",
                 *scope, repo])
            if name == "project-two":
                assert personal.read_text() == "# personal contract\n"
                assert (repo / "openspec/config.yaml").read_text() == "schema: spec-driven\n# custom configuration\n"
            run(["git", "add", "README.md", "openspec", ".agents"], cwd=repo)
            run(["git", "commit", "-qm", "fixture base"], cwd=repo)
            projects.append(repo)
        worktree = base / "worktree with spaces"
        current_issue = "https://github.com/fixture/native-smoke/issues/1"
        run(["git", "remote", "add", "origin", "https://github.com/fixture/native-smoke.git"], cwd=projects[0])
        run([helper, "reserve", "--planned", "--path", worktree, "--repository", projects[0],
             "--issue", current_issue, "--branch", "smoke-issue", "--session", args.controller_session,
             "--run", "codex-native-smoke", "--json"])
        run(["git", "worktree", "add", "-qb", "smoke-issue", worktree], cwd=projects[0])
        reservation("reserve", worktree, args.controller_session, "--issue", current_issue,
                    "--branch", "smoke-issue", "--run", "codex-native-smoke")
        owners[str(worktree)] = args.controller_session
        for location in (*projects, worktree):
            prompt = (" ".join("$" + skill for skill in ACTIONS.values()) +
                      " $roadmap-status\nNative discovery smoke only: identify the five official skills "
                      "and the global roadmap-status skill, their effective paths and current OpenSpec root. "
                      "Do not create artifacts, implement, archive, initialize or update anything. "
                      "Run only read-only context/list commands. Finish with NATIVE_DISCOVERY_OK.")
            response, visible, _ = native("discovery", location, prompt)
            assert "NATIVE_DISCOVERY_OK" in response
            for skill in (*ACTIONS.values(), "roadmap-status"):
                assert skill in visible, f"Native prompt did not discover {skill}"
            for skill in ACTIONS.values():
                assert str(location / ".agents/skills" / skill / "SKILL.md") in visible
            assert str(home / ".agents/skills/roadmap-status/SKILL.md") in visible
            assert (home / ".agents/skills/roadmap-status").resolve() == (active / "skills/roadmap-status").resolve()
            results["locations"][location.name] = {"discovery": True, "native_skills": list(ACTIONS.values())}
        # A fresh execution has neither resume/fork nor the previous prompt's nonce.
        nonce = str(uuid.uuid4())
        native("fresh-source", projects[1], f"Remember this only in this turn: {nonce}. Reply SOURCE_OK; no tools.")
        response, visible, _ = native("fresh-target", projects[1],
                                     "No tools. If you know a nonce from a prior chat, report it; otherwise reply NO_PRIOR_CONTEXT.")
        assert nonce not in visible and nonce not in response and "NO_PRIOR_CONTEXT" in response
        results["fresh_context"] = True
        # Fixture backend captures all gh invocations, not native execution.
        fixture = base / "github.json"
        calls = base / "github-calls.jsonl"
        fixture.write_text(json.dumps({"prs": [], "issues": [
            {"number": i, "title": f"Add value {i}", "state": "OPEN", "comments": [],
             "url": f"https://github.com/fixture/native-smoke/issues/{i}",
             "body": f"Create value_{i}.py exporting VALUE = {i}, with a unittest. "
                     "No other behavior. Independently valuable later features are not requested."}
            for i in (1, 2)]}))
        backend = tools / "gh"
        backend.unlink()  # Only our disposable symlink.
        backend.write_text("#!/usr/bin/env python3\n"
                           "import json,os,sys\nfrom pathlib import Path\n"
                           "p=Path(os.environ['SMOKE_GH_STATE']);s=json.loads(p.read_text());a=sys.argv[1:]\n"
                           "with open(os.environ['SMOKE_GH_CALLS'],'a') as f:f.write(json.dumps(a)+'\\n')\n"
                           "if a[:2]==['issue','list']:out=s['issues']\n"
                           "elif a[:2]==['issue','view']:out=next(x for x in s['issues'] if str(x['number'])==a[2].split('/')[-1])\n"
                           "elif a[:2]==['pr','list']:out=s['prs']\n"
                           "elif a[:2]==['pr','create']:\n"
                           " n=len(s['prs'])+1;out={'number':n,'url':f'https://github.com/fixture/native-smoke/pull/{n}','state':'OPEN'};s['prs'].append(out);p.write_text(json.dumps(s))\n"
                           "elif a[:2]==['repo','view']:out={'nameWithOwner':'fixture/native-smoke','defaultBranchRef':{'name':'main'}}\n"
                           "else:raise SystemExit('Fixture unsupported: '+repr(a))\n"
                           "print(json.dumps(out))\n")
        backend.chmod(0o755)
        env.update(SMOKE_GH_STATE=str(fixture), SMOKE_GH_CALLS=str(calls))
        for number in (1, 2):
            change = f"fixture-value-{number}"
            current_issue = f"https://github.com/fixture/native-smoke/issues/{number}"
            # Park the completed prior issue before changing the issue binding.
            if number == 2:
                previous = owners[str(worktree)]
                reservation("release", worktree, previous, "--state", "WAITING")
                worktree = base / "second issue worktree"
                run([helper, "reserve", "--planned", "--path", worktree, "--repository", projects[0],
                     "--issue", current_issue, "--branch", "smoke-issue-2", "--session", args.controller_session,
                     "--run", "codex-native-smoke", "--json"])
                run(["git", "worktree", "add", "-qb", "smoke-issue-2", worktree], cwd=projects[0])
                reservation("reserve", worktree, args.controller_session, "--issue", current_issue,
                            "--branch", "smoke-issue-2", "--run", "codex-native-smoke")
                owners[str(worktree)] = args.controller_session
            native(f"explore-{number}", worktree,
                   f"$openspec-explore $milestone-orchestrator\nExplore ONLY issue {current_issue}, "
                   "read its live fixture gh issue view. Selected milestone has issues 1 and 2: "
                   "keep only this issue active. No code, proposal or other writes now. "
                   "Report sufficient scope, tests and blockers. Do not invoke gh comments.")
            native(f"propose-{number}", worktree,
                   f"$openspec-propose\nCreate change {change} ONLY for {current_issue}; "
                   "read gh issue view. Minimal Python constant module and unittest; inspect source. "
                   "Use official CLI artifact instructions and strict validation. Planning ONLY. "
                   "Do not implement, do not touch the other issue, no comments. Keep artifacts concise.",
                   writable=True)
            run([openspec, "validate", change, "--strict", "--no-interactive"], cwd=worktree)
            run(["git", "add", f"openspec/changes/{change}"], cwd=worktree)
            run(["git", "commit", "-qm", f"proposal {number}"], cwd=worktree)
            reservation("checkpoint", worktree, owners[str(worktree)])
            plan = run(["git", "rev-parse", "HEAD"], cwd=worktree).strip()
            review, _, _ = native(f"plan-review-{number}", worktree,
                                  f"Read-only independent planning review of exact HEAD {plan}, "
                                  f"change {change}, live fixture issue {current_issue}. "
                                  "Inspect the immutable artifacts and source. If materially sound reply "
                                  "PLAN_APPROVED; otherwise list blockers. No writes/comments.")
            assert "PLAN_APPROVED" in review
            native(f"apply-{number}", worktree,
                   f"$openspec-apply-change\nExplicitly implement change {change} for {current_issue}. "
                   f"Approved immutable proposal HEAD {plan}; independent native review completed. "
                   "Read artifacts, implement only the constant module/unittest, run unittest discovery, "
                   "mark tasks only when done. No comments, no other issue. "
                   "A cosmetic rename and an already tracked improvement 'Add value 2' are not new issues.",
                   writable=True)
            test = subprocess.run(["python3", "-m", "unittest", "discover", "-s",
                                   "tests" if (worktree / "tests").is_dir() else "."],
                                  cwd=worktree, env=env, capture_output=True, text=True, timeout=60)
            test_output = test.stdout + test.stderr
            (base / f"tests-{number}.log").write_text(test_output)
            count = re.search(r"Ran (\d+) tests?", test_output)
            assert test.returncode == 0 and count and int(count[1]) > 0, test_output
            report, _, _ = native(f"verify-{number}", worktree,
                   f"$openspec-verify-change\nVerify change {change}, actual code and tests. "
                   "Run tests as needed. Read-only report, no archive or implementation.",
                   writable=False)
            results.setdefault("verify_reports", []).append(report)
            native(f"archive-{number}", worktree,
                   f"$openspec-archive-change\nArchive completed change {change}. "
                   "User explicitly selects Sync now (recommended); preserve existing main specs, "
                   "follow official sync instructions and verify all changes. Do not skip validation. "
                   "No GitHub comments. This is explicit authorization for sync and archive.",
                   writable=True)
            archives = list((worktree / "openspec/changes/archive").glob(f"*{change}"))
            assert len(archives) == 1 and not (worktree / f"openspec/changes/{change}").exists()
            native(f"pr-park-{number}", worktree,
                   f"Prepare the fixture-only PR for issue {current_issue}; use gh pr list before gh pr create. "
                   "No real push or merge: the GitHub backend is an explicitly disposable fixture. "
                   "Create at most one fixture PR, then explicitly park this issue awaiting independent review. "
                   "No stage/status/hidden comments. No trivial/duplicate evolution issues. "
                   "Return PARKED_FOR_REVIEW; do not start the next issue.", writable=True)
            assert len(json.loads(fixture.read_text())["prs"]) == number
            if number == 1:
                assert not (worktree / "value_2.py").exists()
                assert not (worktree / "openspec/changes/fixture-value-2").exists()
            results.setdefault("lifecycle", []).append({"issue": current_issue, "proposal": plan,
                                                       "archive": str(archives[0]), "tests_exit": 0,
                                                       "parked_before_next": True})
        commands = [json.loads(line) for line in calls.read_text().splitlines()]
        assert not any(a[:2] in (["issue", "comment"], ["pr", "comment"], ["issue", "create"]) for a in commands)
        results["no_operational_comments_or_duplicate_evolutions"] = True
        results["status"] = "PASS"
        print("PASS: native Codex discovery, fresh contexts and controlled fixture lifecycle")
    except Exception as exc:
        results["error"] = str(exc)
        raise
    finally:
        auth.unlink(missing_ok=True)
        results["copied_auth_removed"] = not auth.exists()
        (base / "results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        print(f"Evidence: {base}/results.json (private; credentials removed)")


if __name__ == "__main__":
    main()
