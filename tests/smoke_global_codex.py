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
import secrets
import selectors
import shlex
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


def discovered_paths(visible):
    """Resolve Codex's native compact rN skill paths, not guessed root order."""
    def strings(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "text" and isinstance(child, str):
                    yield child
                else:
                    yield from strings(child)
        elif isinstance(value, list):
            for child in value:
                yield from strings(child)
    text = "\n".join(strings(json.loads(visible)))
    roots = dict(re.findall(r"- `(r\d+)` = `([^`]+)`", text))
    paths = {}
    for name, root, relative in re.findall(
            r"(?m)^- ([\w-]+):[^\n]*\(file: (r\d+)/([^)\n]+/SKILL\.md)\)", text):
        if root not in roots:
            raise RuntimeError(f"BLOCKED: native skill root {root} unavailable")
        paths[name] = Path(roots[root]) / relative
    return paths


def require_planning_complete(status):
    artifacts = status.get("artifacts")
    if (not isinstance(artifacts, list) or not artifacts
            or any(item.get("status") not in ("done", "skipped") for item in artifacts)):
        raise RuntimeError("BLOCKED: native proposal has unfinished schema artifacts")


def require_interrupted_shell(detail, shell_id, cwd):
    if (detail.get("id") != shell_id or detail.get("cwd") != str(cwd)
            or detail.get("status") not in ("exited", "killed")
            or not (detail.get("signal") == "SIGINT" or detail.get("exit") in (-2, 130))):
        raise RuntimeError("BLOCKED: native interrupted shell receipt is missing or belongs to another execution")


def source_snapshot(repo, run):
    paths = run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                cwd=repo).split("\0")
    digest = hashlib.sha256(run(["git", "rev-parse", "HEAD"], cwd=repo).encode())
    for name in sorted(set(filter(None, paths))):
        path = repo / name
        digest.update(name.encode())
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            # Archive legitimately removes still-indexed planning files.
            # Their absence remains part of the before/after source identity.
            digest.update(b"\0MISSING\0")
            continue
        digest.update(str(mode).encode())
        digest.update(os.readlink(path).encode() if path.is_symlink() else path.read_bytes())
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auth-cache", type=Path, help="Explicit regular auth.json; never config.toml")
    parser.add_argument("--controller-session", required=True, help="Caller's real native session ID")
    parser.add_argument("--cross-agent-opencode", action="store_true",
                        help="Also exercise native OpenCode API/shell recovery; requires that CLI explicitly")
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
    opencode = shutil.which("opencode") if args.cross_agent_opencode else None
    if args.cross_agent_opencode:
        if not opencode:
            raise RuntimeError("BLOCKED: explicit cross-agent scenario requires OpenCode")
        (tools / "opencode").symlink_to(opencode)
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
    # Supported per-invocation restrictions: keep all GitHub traffic inside
    # the fixture. ChatGPT apps are otherwise enabled even in an empty HOME.
    native_config = ["--disable", "apps", "--disable", "browser_use",
                     "--disable", "browser_use_external", "--disable", "computer_use",
                     "--disable", "remote_plugin", "-c", 'web_search="disabled"',
                     "-c", "agents.enabled=false"]

    def reservation(command, repo, session, *options):
        return json.loads(run([helper, command, "--path", repo, "--session", session,
                               "--json", *options]))

    def snapshot(repo):
        return source_snapshot(repo, run)

    def native(label, repo, prompt, *, writable=False):
        index = len(results["sessions"])
        before = snapshot(repo)
        context = base / f"context-{index}.json"
        # Native discovery is inspected, not reconstructed from skill bodies.
        visible = run([cli, *native_config, "--cd", repo, "debug", "prompt-input", prompt], cwd=repo)
        (base / f"input-{index}.json").write_text(visible)
        # Even source-read-only reviews call the captured gh backend, which
        # appends its audit receipt outside the checkout. Source immutability
        # is checked independently below, not inferred from a sandbox label.
        command = [cli, "exec", *native_config, "--json", "--ephemeral", "--ignore-user-config",
                   "--ignore-rules", "--sandbox", "workspace-write",
                   "--cd", str(repo), "--add-dir", str(base)]
        full_prompt = prompt + ("\nAll GitHub access MUST use the local gh fixture only; "
                                "no apps/connectors/web/network access or real GitHub mutations. "
                                 "This is the explicitly authorized fixture/native-smoke namespace; "
                                 "Git origin is a disposable local bare fixture representing it. "
                                 "The gh backend must append its captured call receipt; do not redirect "
                                 "or override that capture. Temporary metadata may live under the fixture root. "
                                 "Do not read credentials/auth files. No subagents in this controlled smoke.")
        if writable:
            full_prompt += (
                f"\nBefore ANY write, read {context}. This is the real native thread.started ID "
                f"observed by the controller, not an invented identity. Verify your reservation "
                f"using {helper} verify --path {json.dumps(str(repo))} --session <that ID> --json. "
                "Checkpoint your own writes AND verify again after checkpoint before finishing. "
                 "Do not infer the old owner's ID. "
                 "Do not create other worktrees or processes/agents.")
        else:
            full_prompt += (
                "\nThis execution has SOURCE-READ-ONLY scope: no source/Git/OpenSpec changes, "
                "ownership transfer, checkpoint or reservation verify as another writer. "
                "The controller retains the writer reservation; you are not its owner. "
                "Only the gh fixture may append its call metadata. The controller checks exact "
                "source bytes/modes/HEAD before and after you return. Do not claim a sandbox "
                "denial unless an actual command attempted it and returned that denial.")
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
        assert not any(e.get("item", {}).get("type") in ("mcp_tool_call", "web_search")
                       for e in events), "Native fixture escaped into external connectors/search"
        thread_ids.add(thread)
        if writable:
            reservation("checkpoint", repo, thread)
            reservation("verify", repo, thread)
        else:
            assert snapshot(repo) == before, "Read-only native execution changed the checkout"
        response = "\n".join(e.get("item", {}).get("text", "") for e in events
                             if e.get("item", {}).get("type") == "agent_message")
        results["sessions"].append({"label": label, "thread_id": thread, "exit_code": code,
                                    "completed": True, "checkout": str(repo),
                                    "issue": current_issue,
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
            run(["git", "init", "-q", "--initial-branch", "main", repo])
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
        remote = base / "github-origin.git"
        run(["git", "init", "--bare", "-q", "--initial-branch", "main", remote])
        run(["git", "remote", "add", "origin", remote], cwd=projects[0])
        run(["git", "push", "-qu", "origin", "main"], cwd=projects[0])
        run([helper, "reserve", "--planned", "--path", worktree, "--repository", projects[0],
             "--issue", current_issue, "--branch", "smoke-issue", "--session", args.controller_session,
             "--run", "codex-native-smoke", "--json"])
        run(["git", "worktree", "add", "-qb", "smoke-issue", worktree], cwd=projects[0])
        run(["git", "push", "-q", "origin", "smoke-issue"], cwd=projects[0])
        reservation("reserve", worktree, args.controller_session, "--issue", current_issue,
                    "--branch", "smoke-issue", "--run", "codex-native-smoke")
        owners[str(worktree)] = args.controller_session
        for location in (*projects, worktree):
            prompt = (" ".join("$" + skill for skill in ACTIONS.values()) +
                      " $roadmap-status\nNative discovery smoke only: identify the five official skills "
                      "and the global roadmap-status skill, their effective paths and current OpenSpec root. "
                      "Invoke the native skills named by $ mentions: load their FULL SKILL.md instructions "
                      "from the native discovered paths, not just frontmatter. Apply only their read-only "
                      "project/context checks in this invocation and explain the remaining lifecycle steps. "
                      "Do not create artifacts, implement, archive, initialize or update anything. "
                      "Run only read-only context/list commands. Finish with NATIVE_DISCOVERY_OK.")
            response, visible, events = native("discovery", location, prompt)
            assert "NATIVE_DISCOVERY_OK" in response
            discovered = discovered_paths(visible)
            for skill in (*ACTIONS.values(), "roadmap-status"):
                assert skill in discovered, f"Native prompt did not discover {skill}"
            for skill in ACTIONS.values():
                assert discovered[skill] == location / ".agents/skills" / skill / "SKILL.md"
            assert discovered["roadmap-status"] == home / ".agents/skills/roadmap-status/SKILL.md"
            output = "\n".join(e.get("item", {}).get("aggregated_output", "") for e in events
                               if e.get("type") == "item.completed"
                               and e.get("item", {}).get("type") == "command_execution"
                               and e.get("item", {}).get("exit_code") == 0)
            for skill in (*ACTIONS.values(), "roadmap-status"):
                assert f"name: {skill}" in output, f"No runtime loading evidence for {skill}"
            assert "Verify that an implementation" in output and "Planning boundary" in output
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
        fixture.write_text(json.dumps({"prs": ([{
            "number": 1, "url": "https://github.com/fixture/native-smoke/pull/1",
            "state": "OPEN", "isDraft": True, "issue_number": 1,
            "headRefName": "smoke-issue", "baseRefName": "main",
            "body": "Closes #1; interrupted draft; tests NOT RUN", "reviews": [],
            "statusCheckRollup": [], "headRefOid": run(["git", "rev-parse", "HEAD"], cwd=worktree).strip()
        }] if args.cross_agent_opencode else []), "issues": [
            {"number": i, "title": f"Add value {i}", "state": "OPEN", "comments": [],
             "url": f"https://github.com/fixture/native-smoke/issues/{i}",
             "body": f"Create value_{i}.py exporting VALUE = {i}, with a unittest. "
                     "No other behavior. Independently valuable later features are not requested."}
            for i in (1, 2)]}))
        backend = tools / "gh"
        backend.unlink()  # Only our disposable symlink.
        backend.write_text("#!/usr/bin/env python3\n"
                           "import json,os,sys,subprocess\nfrom pathlib import Path\n"
                           "p=Path(os.environ['SMOKE_GH_STATE']);s=json.loads(p.read_text());a=sys.argv[1:]\n"
                           f"with open({str(calls)!r},'a') as f:f.write(json.dumps(a)+'\\n')\n"
                           "def target_pr():\n"
                           " target=a[2].split('/')[-1] if len(a)>2 and not a[2].startswith('-') else None\n"
                           " return next(x for x in s['prs'] if (str(x['number'])==target if target else x.get('issue_number')==int(os.environ['SMOKE_ISSUE_NUMBER'])))\n"
                           "def fields(out):\n"
                           " for option,key in (('--title','title'),('--body','body')):\n"
                           "  if option in a:out[key]=a[a.index(option)+1]\n"
                           " if '--body-file' in a:\n"
                           "  file=a[a.index('--body-file')+1];out['body']=sys.stdin.read() if file=='-' else Path(file).read_text()\n"
                           "for pr in s['prs']:\n"
                           " ref=pr.get('headRefName','');g=subprocess.run(['git','--git-dir',os.environ['SMOKE_GIT_REMOTE'],'rev-parse','--verify','refs/heads/'+ref],capture_output=True,text=True)\n"
                           " if g.returncode==0:pr['headRefOid']=g.stdout.strip()\n"
                           "if a[:2]==['issue','list']:out=s['issues']\n"
                           "elif a[:2]==['issue','view']:out=next(x for x in s['issues'] if str(x['number'])==a[2].split('/')[-1])\n"
                           "elif a[:2]==['pr','list']:out=[x for x in s['prs'] if x.get('issue_number')==int(os.environ['SMOKE_ISSUE_NUMBER'])]\n"
                           "elif a[:2]==['pr','view']:out=target_pr()\n"
                           "elif a[:2]==['pr','create']:\n"
                           " n=len(s['prs'])+1;head=a[a.index('--head')+1] if '--head' in a else subprocess.check_output(['git','branch','--show-current'],text=True).strip()\n"
                           " out={'number':n,'url':f'https://github.com/fixture/native-smoke/pull/{n}','state':'OPEN','isDraft':'--draft' in a,'headRefName':head,'baseRefName':'main','issue_number':int(os.environ['SMOKE_ISSUE_NUMBER'])};fields(out);s['prs'].append(out);p.write_text(json.dumps(s))\n"
                           "elif a[:2] in (['pr','edit'],['pr','ready']):\n"
                           " out=target_pr()\n"
                           " if a[1]=='ready':out['isDraft']=False\n"
                           " fields(out);p.write_text(json.dumps(s))\n"
                           "elif a[:2]==['repo','view']:out={'nameWithOwner':'fixture/native-smoke','defaultBranchRef':{'name':'main'}}\n"
                           "else:raise SystemExit('Fixture unsupported: '+repr(a))\n"
                           "print(json.dumps(out))\n")
        backend.chmod(0o755)
        env.update(SMOKE_GH_STATE=str(fixture), SMOKE_GH_CALLS=str(calls), SMOKE_GIT_REMOTE=str(remote))
        for number in (1, 2):
            env["SMOKE_ISSUE_NUMBER"] = str(number)
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
                   "For this fixture explicitly create ALL schema planning artifacts, including design.md "
                   "even though the implementation is simple; do not leave any CLI artifact ready/blocked. "
                   "Use python3 (not python) in all documented fixture test commands. "
                   "Use official CLI artifact instructions and strict validation. Planning ONLY. "
                   "Do not implement, do not touch the other issue, no comments. Keep artifacts concise.",
                   writable=True)
            require_planning_complete(json.loads(run(
                [openspec, "status", "--change", change, "--json"], cwd=worktree)))
            run([openspec, "validate", change, "--strict", "--no-interactive"], cwd=worktree)
            run(["git", "add", f"openspec/changes/{change}"], cwd=worktree)
            run(["git", "commit", "-qm", f"proposal {number}"], cwd=worktree)
            reservation("checkpoint", worktree, owners[str(worktree)])
            reservation("verify", worktree, owners[str(worktree)])
            plan = run(["git", "rev-parse", "HEAD"], cwd=worktree).strip()
            review, _, _ = native(f"plan-review-{number}", worktree,
                                  f"Read-only independent planning review of exact HEAD {plan}, "
                                  f"change {change}, live fixture issue {current_issue}. "
                                  "Inspect the immutable artifacts and source. If materially sound reply "
                                  "with the standalone line PLAN_APPROVED (no formatting); otherwise list blockers. No writes/comments.")
            assert re.search(r"(?m)^PLAN_APPROVED\s*$", review), review
            if number == 1 and args.cross_agent_opencode:
                # Supported native session tools suffice for identity and shell
                # completion here; this does NOT claim OpenCode model execution.
                run(["python3", "-c", runner, ROOT / "scripts/install-global", ROOT,
                     "--agent", "opencode", "--revision", revision])
                env["OPENCODE_PASSWORD"] = secrets.token_hex(24)
                server = subprocess.Popen([opencode, "serve", "--hostname", "127.0.0.1", "--port", "0"],
                                          cwd=worktree, env=env, stdout=subprocess.PIPE,
                                          stderr=(base / "recovery-server.log").open("w"), text=True)
                try:
                    match = re.search(r"http://127\.0\.0\.1:\d+", server.stdout.readline())
                    if not match:
                        raise RuntimeError("BLOCKED: private recovery OpenCode server unavailable")
                    url = match[0]

                    def api(method, path, body=None):
                        command = [opencode, "--server", url, "api", method, path]
                        if body is not None:
                            command += ["--data", json.dumps(body)]
                        output = run(command, cwd=worktree)
                        return json.loads(output) if output.strip() else None

                    def native_shell(session_id, command):
                        api("post", f"/api/session/{session_id}/shell", {"command": command})
                        deadline = time.monotonic() + 90
                        while True:
                            messages = api("get", f"/api/session/{session_id}/message")["data"]
                            matches = [message for message in messages
                                       if message.get("type") == "shell" and message.get("command") == command]
                            if matches and matches[-1]["status"] != "running":
                                return matches[-1], messages
                            if time.monotonic() >= deadline:
                                raise RuntimeError("BLOCKED: native OpenCode shell terminal result unavailable")
                            time.sleep(0.25)

                    session = api("post", "/api/session", {"location": {"directory": str(worktree)}})["data"]
                    session_id = session["id"]
                    assert session["location"]["directory"] == str(worktree)
                    blocked = subprocess.run([helper, "verify", "--path", worktree, "--session", session_id, "--json"],
                                             env=env, capture_output=True, text=True, timeout=30)
                    assert blocked.returncode == 3, "Unknown/new writer must not take over implicitly"
                    previous = owners[str(worktree)]
                    run([helper, "handoff", "--path", worktree, "--from-session", previous,
                         "--to-session", session_id, "--run", "codex-native-smoke", "--json"])
                    owners[str(worktree)] = session_id
                    before_status = snapshot(worktree)
                    for skill in ("resume-workflow", "pr-status"):
                        api("post", f"/api/experimental/session/{session_id}/skill", {"id": skill, "resume": False})
                    query = ("set -e\n" + shlex.join([str(helper), "verify", "--path", str(worktree),
                                                       "--session", session_id, "--json"]) +
                             f"\nopenspec instructions apply --change {change} --json\n"
                             "gh pr list --json number,url,state\n")
                    shell, messages = native_shell(session_id, query)
                    assert shell["status"] == "exited" and shell["exit"] == 0
                    assert snapshot(worktree) == before_status
                    interrupted, messages = native_shell(
                        session_id, "python3 -c 'import os,signal; os.kill(os.getpid(),signal.SIGINT)'")
                    detail = api("get", f"/api/shell/{interrupted['shellID']}")["data"]
                    require_interrupted_shell(detail, interrupted["shellID"], worktree)
                    (base / "opencode-recovery-messages.json").write_text(json.dumps(messages, indent=2))
                    recovery = {"opencode_session": session_id, "previous_codex_thread": previous,
                                "checkout": str(worktree), "change": change,
                                "pr": "https://github.com/fixture/native-smoke/pull/1",
                                "test_result": "incomplete/interrupted; NOT PASSED",
                                "interrupted_shell": {key: detail.get(key) for key in ("id", "status", "exit", "signal")},
                                "history_portable": False, "status_readonly": True,
                                "opencode_model_execution": False}
                    (base / "recovery.json").write_text(json.dumps(recovery, indent=2))
                    response, _, _ = native("cross-agent-recovery-status", worktree,
                        f"$resume-workflow $pr-status\nRead-only recovery inspection for {current_issue}. "
                        f"The previous native OpenCode writer returned; inspect {base / 'recovery.json'} "
                        f"and actual Git/OpenSpec/fixture gh issue view/pr list evidence. Existing change is {change}, "
                        "existing draft PR is #1. Do not write, transfer ownership, create a change/worktree/PR, "
                        "or start workers. Only gh issue view/list and pr view/list are supported by this backend; "
                        "hosted checks/review are NOT RUN. Report incomplete tests and next safe action, "
                        "no timing analytics or comments. Finish INCOMPLETE_NOT_PASSED.")
                    assert "INCOMPLETE_NOT_PASSED" in response
                    assert len(json.loads(fixture.read_text())["prs"]) == 1
                    results["cross_agent_recovery"] = recovery
                finally:
                    server.terminate()
                    server.wait(timeout=15)
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
            assert (test.returncode == 0 and count and int(count[1]) > 0
                    and not re.search(r"(?:skipped|expected failures|unexpected successes)\s*=", test_output)), test_output
            run(["python3", "-c", f"import value_{number}; assert type(value_{number}.VALUE) is int and value_{number}.VALUE == {number}"],
                cwd=worktree)
            report, _, _ = native(f"verify-{number}", worktree,
                   f"$openspec-verify-change\nVerify change {change}, actual code and tests. "
                   "Run tests as needed. Read-only report, no archive or implementation. "
                   "Finish with a standalone VERIFY_CLEAN only if no critical/warning findings "
                   "and no applicable check is unverified; otherwise report the findings.",
                   writable=False)
            results.setdefault("verify_reports", []).append(report)
            assert re.search(r"(?m)^VERIFY_CLEAN\s*$", report), report
            native(f"archive-{number}", worktree,
                   f"$openspec-archive-change\nArchive completed change {change}. "
                   "User explicitly selects Sync now (recommended); preserve existing main specs, "
                   "follow official sync instructions and verify all changes. Do not skip validation. "
                   "No GitHub comments. This is explicit authorization for sync and archive.",
                   writable=True)
            archives = list((worktree / "openspec/changes/archive").glob(f"*{change}"))
            assert len(archives) == 1 and not (worktree / f"openspec/changes/{change}").exists()
            pr_response, _, _ = native(f"pr-park-{number}", worktree,
                   f"$prepare-pr\nPrepare the fixture-only PR for issue {current_issue}; use gh pr list before gh pr create. "
                   "Git origin is the disposable local bare fixture, not GitHub: scoped commit and "
                   "non-force push ONLY to that local origin are authorized. No external push or merge. "
                   "Create at most one fixture PR, then explicitly park this issue awaiting independent review. "
                   "No stage/status/hidden comments. No trivial/duplicate evolution issues. "
                   f"Keep any temporary PR body under {base}, outside the checkout. "
                   "Finish with clean Git source and current HEAD pushed to the local bare origin. "
                   "Return the standalone line PARKED_FOR_REVIEW exactly (no formatting); do not start the next issue.",
                   writable=True)
            assert re.search(r"(?m)^PARKED_FOR_REVIEW\s*$", pr_response), pr_response
            assert len(json.loads(fixture.read_text())["prs"]) == number
            assert not run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=worktree)
            assert run(["git", "rev-parse", "HEAD"], cwd=worktree).strip() == run([
                "git", "--git-dir", remote, "rev-parse",
                "refs/heads/" + ("smoke-issue" if number == 1 else "smoke-issue-2")]).strip()
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
