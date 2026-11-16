#!/usr/bin/env python3
"""Fail-closed model-backed recovery probe against disposable Git/ledger fixtures.

Run from a clean candidate commit: python3 tests/smoke_resume_candidate_opencode.py
This is a separate check from smoke_global_opencode.py (published-revision discovery).
It never uses real GitHub resources or the operator's OpenCode configuration.
Only an exact clean candidate HEAD is eligible; retained results are audited evidence.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
import time

ROOT = Path(__file__).resolve().parents[1]
CHANGE = "issue-61-opencode-safe-resume"
MODEL = os.environ.get("RESUME_SMOKE_MODEL", "opencode/glm-5.3-flash-free")
PROMPTS = {
    "T1": (
        "Continue de onde parou nesta issue. Consulte evidências duráveis locais e "
        "o ledger da issue via gh api (fixture somente leitura). Antes de afirmar "
        "que o antigo writer parou, consulte o comando runtime_receipt_command "
        "em recovery-evidence.json para obter confirmação terminal independente "
        "pelo harness; sem ela bloqueie Apply. "
        "OpenSpec; descubra as skills nativas em .agents/skills e invoque a "
        "skill OpenSpec aplicável para conferir o próximo gate. Diga o último "
        "gate comprovado e a próxima ação. Esta prova é "
        "somente leitura: não inicie Apply nem crie branch, worktree ou change."
    ),
    "T5": (
        "Retome este milestone após interrupção. Reconstitua PR, dependência e "
        "merge mode da evidência persistida, incluindo ledger via gh api e PR "
        "via gh pr view (fixture somente leitura); descubra as skills OpenSpec nativas "
        "em .agents/skills, invoque a aplicável e execute `openspec validate "
        "issue-61-opencode-safe-resume --strict --no-interactive` somente leitura "
        "depois de consultá-la, sem executar mudanças. "
        "Indique a próxima ação sem agendar "
        "o consumidor. Prova somente leitura, sem operações GitHub de escrita."
    ),
    "T7": (
        "Continue de onde parou. Há duas execuções candidatas neste checkout. "
        "Use evidências duráveis, incluindo ledgers via gh api (fixture somente "
        "leitura); pode descobrir arquivos das skills OpenSpec nativas "
        "em .agents/skills, mas NÃO invoque nenhuma skill OpenSpec antes da escolha. "
        "Não selecione candidato nem faça takeover ou dispatch. Respeite o gate de "
        "desambiguação. Se ambíguo, faça só a pergunta necessária. "
        "Prova somente leitura, sem escolher pela recência."
    ),
}

RUNTIME_READER = '''#!/usr/bin/env python3
"""Fixture-only terminal observation; never derives liveness from a PID alone."""
import json
import os
from pathlib import Path
import sys
if len(sys.argv) != 4:
    sys.exit(2)
execution, owner, run = sys.argv[1:]
records = json.loads((Path(os.environ["RESUME_RUNTIME_ROOT"]) / "receipts.json").read_text())
matching = [r for r in records if r["execution_id"] == execution and
            r["owner"] == owner and r["run"] == run and r["exit_code"] == 0]
if len(matching) != 1:
    print(json.dumps({"terminal": False, "execution_id": execution}))
    sys.exit(3)
print(json.dumps({"terminal": True, **matching[0]}))
'''


def process_start(pid):
    # Field 22 of /proc/<pid>/stat; skip the parenthesized executable safely.
    return int(Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()[19])


def terminal_receipt(reservation, repo, path, issue, run_id, case, case_env, root):
    """Observe a real cooperative fixture writer's exit via Popen.wait()."""
    owner = f"seed-{case}"
    execution_id = f"writer-{case}-{issue.split('/')[-1]}"
    child = '''import json, os, subprocess, sys
reservation, path, issue, branch, owner, run_id = sys.argv[1:]
start = int(open(f"/proc/{os.getpid()}/stat").read().rsplit(") ",1)[1].split()[19])
subprocess.run([reservation,"reserve","--path",path,"--issue",issue,
    "--branch",branch,"--session",owner,"--run",run_id,
    "--owner-pid",str(os.getpid()),"--json"],check=True,capture_output=True,text=True)
v = subprocess.run([reservation,"verify","--path",path,"--session",owner,
    "--run",run_id,"--json"],check=True,capture_output=True,text=True)
assert json.loads(v.stdout)["ok"]
print(json.dumps({"pid":os.getpid(),"start":start}), flush=True)
sys.stdin.read()
'''
    process = subprocess.Popen(
        ["python3", "-c", child, str(reservation), str(path), issue,
         f"issue-{issue.split('/')[-1]}-fixture", owner, run_id],
        cwd=repo, env=case_env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True)
    ready = process.stdout.readline()
    if not ready:
        raise RuntimeError(f"fixture writer did not reserve: {process.stderr.read()[:2000]}")
    identity = json.loads(ready)
    assert process.pid == identity["pid"] and process_start(process.pid) == identity["start"]
    observed_at = datetime.now(timezone.utc).isoformat()
    process.stdin.close()
    code = process.wait(timeout=20)
    assert code == 0, process.stderr.read()[:500]
    proc_path = Path(f"/proc/{identity['pid']}/stat")
    assert not proc_path.exists() or process_start(identity["pid"]) != identity["start"]
    receipt = {"execution_id": execution_id, "owner": owner, "run": run_id,
               "pid": identity["pid"], "process_start": identity["start"],
               "exit_code": code, "observed_at": datetime.now(timezone.utc).isoformat(),
               "running_observed_at": observed_at}
    (root / "receipts.json").write_text(json.dumps([receipt]))
    assert subprocess.run(["python3", str(root / "read-receipt"), execution_id,
                           owner, run_id], cwd=repo, env=case_env,
                          capture_output=True).returncode == 0
    assert subprocess.run(["python3", str(root / "read-receipt"), execution_id,
                           "wrong-owner", run_id], cwd=repo, env=case_env,
                          capture_output=True).returncode == 3
    assert subprocess.run(["python3", str(root / "read-receipt"), "absent",
                           owner, run_id], cwd=repo, env=case_env,
                          capture_output=True).returncode == 3
    return receipt


def run(args, *, cwd, env, timeout=90):
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"{args[:4]} exited {result.returncode}: {result.stderr[:500]}")
    return result.stdout.strip()


def git(repo, env, *args):
    return run(["git", *args], cwd=repo, env=env)


def inventory(repo, env):
    return {
        "head": git(repo, env, "rev-parse", "HEAD"),
        "branches": git(repo, env, "branch", "--list"),
        "worktrees": git(repo, env, "worktree", "list", "--porcelain"),
        "status": git(repo, env, "status", "--porcelain=v1", "--untracked-files=all"),
        "tracked": git(repo, env, "ls-files"),
        "change": sorted(str(p.relative_to(repo)) for p in
                         (repo / "openspec/changes").rglob("*") if p.is_file())
                  if (repo / "openspec/changes").is_dir() else [],
    }


def checked_json(args, *, cwd, env):
    return json.loads(run(args, cwd=cwd, env=env))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(repo, worktrees, gh_root, reservation, env, openspec):
    statuses = {}
    for path in worktrees:
        state = checked_json([str(reservation), "status", "--path", str(path), "--json"],
                             cwd=repo, env=env)
        assert state["ok"] and state["issue_url"] and state["state"] == "ACTIVE"
        statuses[path.name] = {key: state[key] for key in
                               ("issue_url", "branch", "state", "owner", "head",
                                "digest", "drift", "unknown_untracked_paths")}
    context = checked_json([openspec, "context", "--json"], cwd=repo, env=env)
    changes = checked_json([openspec, "list", "--json"], cwd=repo, env=env)
    assert context["root"]["path"] == str(repo) and changes["root"]["path"] == str(repo)
    return {"git": inventory(repo, env),
            "checkout_git": {path.name: inventory(path, env) for path in worktrees},
            "reservation": statuses,
            "ledger": json.loads((gh_root / "state.json").read_text()),
            "openspec": {"context": context, "list": changes},
            "pr": json.loads((gh_root / "state.json").read_text())["pr"]}


def native_calls(events, session, native):
    """Match a real model tool call and its successful output, not prose/CLI alone."""
    path = str(native.resolve())
    name = native.parent.name
    discovery = []
    invocation = []
    instructions = []
    for index, event in enumerate(events):
        if event.get("sessionID") != session or event.get("type") != "tool_use":
            continue
        part = event.get("part", {})
        state = part.get("state", {})
        if state.get("status") != "completed":
            continue
        tool = part.get("tool")
        inp = state.get("input", {})
        output = state.get("output", "")
        if tool == "skill" and inp.get("id") == name and name in output:
            invocation.append({"tool": tool, "id": part.get("id"), "name": name,
                               "event_index": index})
        elif tool == "read" and inp.get("path") in (path, str(native)) and name in output:
            invocation.append({"tool": tool, "id": part.get("id"),
                               "path": inp["path"], "event_index": index})
        if tool in ("glob", "shell") and ".agents" in json.dumps(inp) and name in output:
            discovery.append({"tool": tool, "id": part.get("id"), "event_index": index})
        if tool == "shell" and (
            "openspec instructions " in inp.get("command", "") or
            "openspec validate " in inp.get("command", "")
        ) and output:
            instructions.append({"tool": tool, "id": part.get("id"), "event_index": index})
    return discovery, invocation, instructions


def tool_events(events, session, *, tool=None, contains=None):
    found = []
    for index, event in enumerate(events):
        if event.get("sessionID") != session or event.get("type") != "tool_use":
            continue
        part = event.get("part", {})
        state = part.get("state", {})
        if state.get("status") != "completed" or (tool and part.get("tool") != tool):
            continue
        if contains and contains not in json.dumps(state.get("input", {})):
            continue
        found.append({"index": index, "input": state.get("input", {}),
                      "output": state.get("output", ""), "tool": part.get("tool"),
                      "id": part.get("id")})
    return found


def t7_reinventory(events, session, first_native, repo, worktrees, reader, receipts):
    """Require successful phase-2 observations of this fixture before native use."""
    chosen = receipts[21]
    def parse_json_output(output):
        try:
            return json.loads(output.strip())
        except (ValueError, TypeError):
            return None

    calls = [e for e in tool_events(events, session, tool="shell")
             if e["index"] < first_native and
             isinstance(e["input"].get("command"), str) and
             isinstance(e["output"], str) and
             not re.search(r"[;&|`]|\n", e["input"]["command"]) and
             not re.search(r"(?:^|\n)Exit code: [1-9]\d*\s*$", e["output"])]

    def commands(argv, *, cwd=repo):
        for event in calls:
            if event["input"].get("workdir", str(repo)) != str(cwd):
                continue
            try:
                tokens = shlex.split(event["input"]["command"])
            except ValueError:
                continue
            # A compound command can mask a failed earlier command with the
            # exit status of its last command; only standalone probes count.
            if tokens and Path(tokens[0]).name == argv[0] and tokens[1:] == argv[1:]:
                yield event["output"].strip()

    def json_outputs(argv):
        for output in commands(argv):
            yield parse_json_output(output)

    root = str(repo)
    roots_ok = any(out == root for out in commands(["git", "rev-parse", "--show-toplevel"]))
    roots_ok &= all(any(out == str(path) for out in commands(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"]))
                    for path in worktrees)
    openspec_ok = all(any(
        isinstance(data, dict) and data.get("root", {}).get("path") == root
        for data in json_outputs(["openspec", subcommand, "--json"]))
        for subcommand in ("context", "list"))
    expected_runs = {str(path): receipts[issue]["run"]
                     for path, issue in zip(worktrees, (21, 22))}
    reservation_ok = any(
        isinstance(data, dict) and
        all(any(isinstance(row, dict) and row.get("path") == str(path) and
                row.get("state") == "ACTIVE" and row.get("ok") is True
                and (str(path) not in expected_runs or
                     row.get("owner", {}).get("run") == expected_runs[str(path)])
                for row in data.get("entries", [])) for path in worktrees)
        for data in json_outputs(["worktree-reservation", "list", "--repository", root]))
    # Resolve the terminal receipt to the explicitly chosen run, not merely
    # to a command that mentions the receipt reader.
    receipt_ok = any(
        isinstance(data, dict) and data.get("terminal") is True and
        all(data.get(key) == chosen[key] for key in
            ("execution_id", "owner", "run", "exit_code"))
        for event in calls
        if (tokens := shlex.split(event["input"]["command"])) and
        tokens[-5:] == ["python3", str(reader), chosen["execution_id"],
                        chosen["owner"], chosen["run"]] and
        len(tokens) in (5, 6) and
        (len(tokens) == 5 or tokens[0].startswith("RESUME_RUNTIME_ROOT="))
        for data in [parse_json_output(event["output"])])
    ledger_ok = all(any(
        isinstance(data, list) and any(
            isinstance(comment, dict) and
            isinstance(comment.get("body"), str) and
            receipts[issue]["run"] in comment["body"]
            for comment in data)
        for argv in (["gh", "api", "--paginate",
                      f"repos/disposable/recovery/issues/{issue}/comments"],
                     ["gh", "api",
                      f"repos/disposable/recovery/issues/{issue}/comments"])
        for data in json_outputs(argv)) for issue in (21, 22))
    return bool(roots_ok and openspec_ok and reservation_ok and receipt_ok and ledger_ok)


def execute_model(cli, repo, env, base, case, prompt, session=None):
    command = [cli, "run", "--standalone", "--archived", "--model", MODEL,
               "--format", "json"]
    if session:
        command.extend(["--session", session])
    try:
        execution = subprocess.run([*command, prompt], cwd=repo, env=env,
                                   capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired as error:
        (base / f"{case}-timeout.log").write_bytes(error.stdout or b"")
        raise RuntimeError(f"{case}: model timeout; retained {base}") from error
    transcript = base / f"{case}-events.jsonl"
    transcript.write_text(execution.stdout + "\n")
    (base / f"{case}-stderr.log").write_text(execution.stderr)
    events = [json.loads(line) for line in execution.stdout.splitlines()]
    texts = [item["part"]["text"] for item in events
             if item.get("type") == "text" and isinstance(item.get("part", {}).get("text"), str)]
    sessions = sorted({item["sessionID"] for item in events if "sessionID" in item})
    assert execution.returncode == 0 and texts and len(sessions) == 1
    if session:
        assert sessions == [session], f"{case}: OpenCode changed session"
    return events, "\n".join(texts), sessions[0], str(transcript)


def main():
    cli = shutil.which("opencode")
    openspec = shutil.which("openspec")
    if not cli or not openspec:
        raise RuntimeError("OpenCode V2 and OpenSpec are required")
    revision = run(["git", "rev-parse", "HEAD"], cwd=ROOT, env=os.environ)
    if run(["git", "status", "--porcelain"], cwd=ROOT, env=os.environ):
        raise RuntimeError("Commit the candidate before installing its exact revision")
    base = Path(tempfile.mkdtemp(prefix="resume-candidate-", dir="/tmp/opencode"))
    home = base / "home"
    home.mkdir()
    env = {key: os.environ[key] for key in ("PATH", "LANG", "TERM") if key in os.environ}
    env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"),
               XDG_DATA_HOME=str(home / ".local/share"),
               XDG_CACHE_HOME=str(home / ".cache"),
               XDG_STATE_HOME=str(home / ".local/state"),
               OPENCODE_DB=str(base / "opencode.db"),
               OPENCODE_PASSWORD=secrets.token_hex(24),
               OPENSPEC_TELEMETRY="0", PYTHONDONTWRITEBYTECODE="1")
    assert run([openspec, "--version"], cwd=ROOT, env=env).startswith("2.")
    results = {"started_at": datetime.now(timezone.utc).isoformat(),
               "candidate": revision, "model": MODEL,
               "opencode": run([cli, "--version"], cwd=ROOT, env=env),
               "openspec": run([openspec, "--version"], cwd=ROOT, env=env),
               "scenarios": {}}
    # The public installer has no source override. Inject the local Git transport
    # only in this disposable test process; no global install is performed.
    loader = ("import importlib.machinery,sys; "
              "m=importlib.machinery.SourceFileLoader('installer',sys.argv[1]).load_module(); "
              "source=sys.argv[2]; sys.argv=[sys.argv[1],*sys.argv[3:]]; "
              "original=m.install; m.install=lambda args: original(args,source=source); "
              "sys.exit(m.main())")
    run(["python3", "-c", loader, str(ROOT / "scripts/install-global"),
         str(ROOT), "--agent", "opencode", "--revision", revision], cwd=base, env=env,
        timeout=180)
    active = home / ".local/share/my-ai-skills/active"
    manifest = json.loads((active / "manifest.json").read_text())
    skill = active / "skills/resume-workflow/SKILL.md"
    assert manifest["revision"] == revision and skill.is_file()
    results["skill_sha256"] = hashlib.sha256(skill.read_bytes()).hexdigest()
    results["installed_revision"] = manifest["revision"]
    assert skill.read_bytes() == (ROOT / "skills/resume-workflow/SKILL.md").read_bytes()
    reservation = active / "scripts/worktree-reservation"
    workflow_event = active / "scripts/workflow-event"
    workflow_report = active / "scripts/workflow-report"
    assert all(p.is_file() for p in (reservation, workflow_event, workflow_report))

    # No external GitHub requests. Writes are permitted only while SEED is set;
    # the model's environment never receives that switch.
    bin_dir = base / "bin"
    bin_dir.mkdir()
    shim = bin_dir / "gh"
    shutil.copy2(ROOT / "tests/fixtures/resume_gh.py", shim)
    shim.chmod(0o755)
    env["PATH"] = str(bin_dir) + os.pathsep + env["PATH"]

    for case, prompt in PROMPTS.items():
        repo = base / case
        repo.mkdir()
        git(repo, env, "init", "-q")
        git(repo, env, "remote", "add", "origin", "https://github.com/disposable/recovery.git")
        # Copy the already-generated OpenSpec 2 native contract rather than
        # initializing/updating global or project configuration in the test.
        shutil.copytree(ROOT / ".agents", repo / ".agents")
        shutil.copytree(ROOT / "openspec", repo / "openspec")
        assert "opencode" in (repo / ".agents/skills/.openspec-target").read_text().splitlines()
        assert not (repo / ".opencode/commands").exists()
        native = repo / ".agents/skills/openspec-apply-change/SKILL.md"
        assert native.is_file() and "generatedBy: \"2.0.0\"" in native.read_text()
        validation = run([openspec, "validate", CHANGE, "--strict", "--no-interactive"],
                         cwd=repo, env=env)
        git(repo, env, "add", "-A")
        git(repo, env, "-c", "user.name=Smoke", "-c",
            "user.email=smoke@example.org", "commit", "-qm", "validated proposal")
        proposal_sha = git(repo, env, "rev-parse", "HEAD")
        fixture = {
            "T1": {"repository": "disposable/recovery", "issue": 61,
                   "run": "wf-disposable-t1", "scope": "single_issue",
                   "next": "apply-issue on the pinned validated OpenSpec revision",
                   "proposal_sha": proposal_sha},
            "T5": {"repository": "disposable/recovery", "milestone": 3,
                   "run": "wf-disposable-t5", "merge_mode": "manual",
                   "issue": 11, "pr": 12, "pr_head": "disposable-pr-head",
                   "dependent_issue": 13, "dependency": "issue 13 waits for PR 12 merge"},
            "T7": {"repository": "disposable/recovery", "candidates": [
                {"run": "wf-disposable-a", "issue": 21, "stage": "apply"},
                {"run": "wf-disposable-b", "issue": 22, "stage": "apply"}],
                "result": "ambiguous"},
        }[case]
        evidence = repo / "recovery-evidence.json"
        fixture["strict_validation"] = validation
        evidence.write_text(json.dumps(fixture, indent=2) + "\n")
        git(repo, env, "add", "-A")
        git(repo, env, "-c", "user.name=Smoke", "-c",
            "user.email=smoke@example.org", "commit", "-qm", "interrupted state")
        gh_root = base / f"{case}-github"
        gh_root.mkdir()
        (gh_root / "state.json").write_text(json.dumps({
            "comments": [], "pr": ({"number": 12, "headRefOid": fixture["pr_head"],
                                      "state": "OPEN", "url": "https://github.com/disposable/recovery/pull/12"}
                                     if case == "T5" else None)}))
        (gh_root / "calls.jsonl").write_text("")
        runtime_root = base / f"{case}-runtime"
        runtime_root.mkdir()
        reader = runtime_root / "read-receipt"
        reader.write_text(RUNTIME_READER)
        reader.chmod(0o755)
        (runtime_root / "receipts.json").write_text("[]")
        case_env = {**env, "RESUME_GH_ROOT": str(gh_root),
                    "RESUME_RUNTIME_ROOT": str(runtime_root)}
        receipts = {}
        worktrees = []
        issue_runs = [(fixture["issue"], fixture["run"])] if case != "T7" else [
            (candidate["issue"], candidate["run"]) for candidate in fixture["candidates"]]
        for issue, run_id in issue_runs:
            branch = f"issue-{issue}-fixture"
            path = base / f"{case}-issue-{issue}"
            issue_url = f"https://github.com/disposable/recovery/issues/{issue}"
            checked_json([str(reservation), "reserve", "--planned", "--path", str(path),
                          "--repository", str(repo), "--issue", issue_url, "--branch",
                          branch, "--session", f"seed-{case}", "--run", run_id,
                          "--json"], cwd=repo, env=case_env)
            git(repo, env, "worktree", "add", "-qb", branch, str(path), "HEAD")
            worktrees.append(path)
            receipt = terminal_receipt(reservation, repo, path, issue_url, run_id,
                                       case, case_env, runtime_root)
            receipts[issue] = receipt
            (runtime_root / "receipts.json").write_text(json.dumps(list(receipts.values())))
            seed_env = {**case_env, "RESUME_GH_SEED": "1"}
            event = [str(workflow_event), "--issue", issue_url, "--run-id", run_id]
            run([*event, "run-start", *(
                ["--scope", "milestone", "--milestone-url",
                 "https://github.com/disposable/recovery/milestone/3"] if case == "T5" else []
            )], cwd=repo, env=seed_env)
            if case == "T1":
                run([*event, "stage-start", "--stage", "proposal_review",
                     "--worker-id", receipt["owner"], "--execution-kind", "worker",
                     "--execution-id", receipt["execution_id"]], cwd=repo, env=seed_env)
                run([*event, "observe", "--stage", "proposal_review", "--worker-id",
                     receipt["owner"], "--execution-kind", "worker", "--execution-id",
                     receipt["execution_id"], "--state", "completed", "--source", "runtime_event",
                     "--next", f"Apply at {proposal_sha}"], cwd=repo, env=seed_env)
                run([*event, "stage-end", "--stage", "proposal_review", "--worker-id",
                     receipt["owner"], "--execution-kind", "worker", "--execution-id",
                     receipt["execution_id"], "--status", "completed"], cwd=repo, env=seed_env)
            elif case == "T5" and issue == 11:
                run([*event, "stage-start", "--stage", "pr_audit", "--worker-id",
                     "reviewer", "--execution-kind", "worker", "--execution-id",
                     "pr-12"], cwd=repo, env=seed_env)
                run([*event, "wait-start", "--stage", "pr_audit", "--reason",
                     "dependency", "--next", "issue 13 waits for PR 12; merge_mode=manual"],
                    cwd=repo, env=seed_env)
            else:
                run([*event, "stage-start", "--stage", "apply", "--worker-id",
                     "reviewer", "--execution-kind", "worker", "--execution-id",
                     f"apply-{issue}"], cwd=repo, env=seed_env)
            # The fixture writer has stopped; it is not evidence authorizing
            # takeover. Read-only recovery must leave the owner untouched.
            assert checked_json([str(reservation), "verify", "--path", str(path),
                                 "--session", receipt["owner"], "--json"], cwd=repo,
                                env=case_env)["ok"]
        fixture["runtime_receipt_command"] = f"python3 {reader}"
        fixture["writer_execution_ids"] = {str(issue): receipts[issue]["execution_id"]
                                           for issue, _ in issue_runs}
        # The evidence file is committed before model invocation, while runtime
        # receipts live outside every checkout and are independently observed.
        evidence.write_text(json.dumps(fixture, indent=2) + "\n")
        git(repo, env, "add", "-A")
        git(repo, env, "-c", "user.name=Smoke", "-c",
            "user.email=smoke@example.org", "commit", "-qm", "runtime reader locator")
        # Exercise the public report reader against the actual seeded ledger.
        report = checked_json([str(workflow_report), issue_url, "--format", "json"],
                              cwd=repo, env=case_env)
        assert report["runs"] and report["runs"][0]["run_id"] == run_id
        before = snapshot(repo, worktrees, gh_root, reservation, case_env, openspec)
        calls_before = (gh_root / "calls.jsonl").read_text().splitlines()
        if case == "T7":
            native = repo / ".agents/skills/openspec-explore/SKILL.md"
        native_provenance = {"path": str(native), "resolved": str(native.resolve()),
                             "sha256": sha(native), "source_sha256":
                             sha(ROOT / ".agents/skills" / native.parent.name / "SKILL.md"),
                             "symlink": native.is_symlink()}
        assert native_provenance["sha256"] == native_provenance["source_sha256"]
        phases = []
        session = None
        prompts = [prompt]
        if case == "T7":
            selected = receipts[21]
            prompts.append(
                "Escolho explicitamente a issue #21, run wf-disposable-a. Continue "
                "NESTA MESMA sessão somente leitura: reinventarie ambos os checkouts, "
                "reservas, ledgers via gh api, Git/OpenSpec/GitHub (execute "
                "`openspec context --json` e `openspec list --json` antes da skill); "
                "confirme o writer "
                "anterior pelo runtime_receipt_command de recovery-evidence.json "
                f"com execução {selected['execution_id']}, owner {selected['owner']} "
                f"e run {selected['run']}. Sem prova terminal bloqueie. "
                "Depois da escolha descubra .agents/skills e invoque explicitamente "
                "openspec-explore nativa em modo somente leitura (arquivo canônico "
                "ou ferramenta skill), depois execute openspec validate somente "
                "leitura para conferir o change no contexto da issue. "
                "Não invoque Apply, faça takeover, dispatch ou escrita.")
        for phase, message in enumerate(prompts, 1):
            events, response, session, transcript = execute_model(
                cli, repo, case_env, base, f"{case}-phase{phase}", message, session)
            after = snapshot(repo, worktrees, gh_root, reservation, case_env, openspec)
            calls_after = (gh_root / "calls.jsonl").read_text().splitlines()
            new_calls = [json.loads(line) for line in calls_after[len(calls_before):]]
            calls_safe = all(not any(a == "--method" or a.startswith("body=") or
                                     a in ("edit", "create", "merge", "close", "delete")
                                     for a in args) for args in new_calls)
            native_discovery, native_invocation, native_instructions = (
                native_calls(events, session, native))
            resume_invocation = tool_events(events, session, tool="skill",
                                            contains="resume-workflow") + [
                e for e in tool_events(events, session, tool="read",
                                       contains=str(skill)) if "resume-workflow" in e["output"]]
            receipt_reads = [e for e in tool_events(events, session, contains=str(reader))
                             if '"terminal": true' in e["output"] or
                                '"terminal":true' in e["output"]]
            if case == "T1":
                expected = (str(fixture["issue"]), fixture["run"], proposal_sha[:7], "Apply")
            elif case == "T5":
                expected = ("12", fixture["pr_head"], "manual", "13")
            elif phase == 1:
                expected = ("21", "22", "wf-disposable-a", "wf-disposable-b", "?")
            else:
                expected = ("21", "wf-disposable-a")
            outcome = all(term.lower() in response.lower() for term in expected)
            record = {"phase": phase, "prompt": message, "session_id": session,
                      "response": response, "events": transcript, "before": before,
                      "after": after, "unchanged": before == after,
                      "github_calls": new_calls, "github_read_only": calls_safe,
                      "native": native_provenance, "native_discovery": native_discovery,
                      "native_invocation": native_invocation,
                      "native_instructions": native_instructions,
                      "resume_invocation": resume_invocation, "runtime_receipts": receipts,
                      "runtime_reads": receipt_reads, "outcome": outcome}
            phases.append(record)
            results["scenarios"][case] = phases
            (base / "results.json").write_text(json.dumps(results, indent=2) + "\n")
            required = before == after and calls_safe and new_calls and outcome
            required &= any(args[:1] == ["api"] for args in new_calls)
            if case == "T7" and phase == 1:
                # Any native invocation before explicit user choice fails closed.
                all_native_invocations = [
                    e for e in tool_events(events, session)
                    if (e["tool"] == "skill" and
                        str(e["input"].get("id", "")).startswith("openspec-")) or
                       (e["tool"] == "read" and
                        "/.agents/skills/openspec-" in str(e["input"].get("path", "")))]
                required &= bool(resume_invocation) and not all_native_invocations
                required &= not tool_events(events, session, contains="reconcile")
            else:
                # Discovery may occur in the ambiguity turn, but invocation
                # must happen only after explicit choice in this same session.
                previous_discovery = (phases[0]["native_discovery"]
                                      if case == "T7" and phase == 2 else [])
                required &= bool((native_discovery or previous_discovery) and
                                 native_invocation and native_instructions)
                required &= bool(previous_discovery) or any(
                    d["event_index"] < i["event_index"] for d in native_discovery
                    for i in native_invocation)
                required &= any(i["event_index"] < c["event_index"]
                                for i in native_invocation for c in native_instructions)
                if case == "T1" or case == "T7":
                    chosen = receipts[61 if case == "T1" else 21]
                    required &= any(chosen["execution_id"] in json.dumps(e["input"]) and
                                    chosen["owner"] in json.dumps(e["input"])
                                    for e in receipt_reads)
                    if case == "T7":
                        first_native = min(i["event_index"] for i in native_invocation)
                        required &= t7_reinventory(events, session, first_native,
                                                   repo, worktrees, reader, receipts)
                if phase == 1:
                    required &= bool(resume_invocation)
            if not required:
                raise RuntimeError(f"{case} phase {phase}: recovery proof incomplete; "
                                   f"see {base}/results.json")
            before, calls_before = after, calls_after
        if case == "T7":
            assert phases[0]["session_id"] == phases[1]["session_id"]
    results["finished_at"] = datetime.now(timezone.utc).isoformat()
    (base / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"Model-backed observations retained at {base}/results.json; inspect responses "
          "and events against T1/T5/T7 before claiming scenario PASS")


if __name__ == "__main__":
    main()
