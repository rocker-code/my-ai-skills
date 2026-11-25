#!/usr/bin/env python3
"""Fail-closed model-backed recovery probe against disposable Git/GitHub fixtures.

Run from a clean candidate commit: python3 tests/smoke_resume_candidate_opencode.py
This is a separate check from smoke_global_opencode.py (published-revision discovery).
It never uses real GitHub resources or the operator's OpenCode configuration.
Only an exact clean candidate HEAD is eligible; retained results are audited evidence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import shutil
import signal
import subprocess
import tempfile
from datetime import datetime, timezone
import time

ROOT = Path(__file__).resolve().parents[1]
CHANGE = "issue-61-opencode-safe-resume"
APPROVED_PROPOSAL = "31cdb42b2d0e409e8820fa71d97177316c07f94a"
STRICT_VALIDATE = f"openspec validate {CHANGE} --strict --no-interactive"
PROMPTS = {
    "T1": (
        "Continue de onde parou nesta issue. Consulte evidências duráveis locais e "
        "a issue e suas decisões via gh api (fixture somente leitura). Antes de afirmar "
        "que o antigo writer parou, consulte o comando runtime_receipt_command "
        "em recovery-evidence.json para obter confirmação terminal independente "
        "pelo harness; sem ela bloqueie Apply. "
        "OpenSpec; descubra as skills nativas em .agents/skills e invoque a "
        "skill OpenSpec aplicável para conferir o próximo gate. Diga o último "
        "gate comprovado e a próxima ação. Esta prova é "
        "somente leitura: não inicie Apply nem crie branch, worktree ou change. "
        "Confronte o commit da proposta, seus artefatos, validação estrita e "
        "revisão imutável nas fontes disponíveis, não apenas declarações de estado. "
        "Os comandos somente leitura publicados pela fixture têm argv e diretório "
        "restritos; use-os sem composição. Relate fontes verificadas e lacunas."
    ),
    "T5": (
        "Retome este milestone após interrupção. Reconstitua PR, dependência e "
        "merge mode da evidência persistida, incluindo issues via gh api e PR "
        "via gh pr view (fixture somente leitura); descubra as skills OpenSpec nativas "
        "em .agents/skills, invoque a aplicável e execute `openspec validate "
        "issue-61-opencode-safe-resume --strict --no-interactive` somente leitura "
        "depois de consultá-la, sem executar mudanças. "
        "Indique a próxima ação sem agendar "
        "o consumidor. Prova somente leitura, sem operações GitHub de escrita."
    ),
    "T7": (
        "Continue de onde parou. Há duas execuções candidatas neste checkout. "
        "Use evidências duráveis, incluindo issues via gh api (fixture somente "
        "leitura); pode descobrir arquivos das skills OpenSpec nativas "
        "em .agents/skills, mas NÃO invoque nenhuma skill OpenSpec antes da escolha. "
        "Não selecione candidato nem faça takeover ou dispatch. Respeite o gate de "
        "desambiguação. Se ambíguo, identifique os dois candidatos por issue e run "
        "obtidos da evidência, e responda SOMENTE com uma pergunta de escolha "
        "sem preâmbulo, no formato 'Qual issue e run você escolhe: issue "
        "#<primeira> / <run> ou issue #<segunda> / <run>?' Use os identificadores "
        "confirmados pela evidência, não escolha por conta própria. Depois pause. "
        "Se a ferramenta "
        "interativa de pergunta estiver indisponível ou for cancelada neste run, "
        "faça a mesma pergunta na resposta comum visível ao usuário, sem tratar "
        "o cancelamento como uma escolha. "
        "Prova somente leitura, sem escolher pela recência."
    ),
}

RUNTIME_READER = '''#!/usr/bin/env python3
"""Fixture-only terminal observation; never derives liveness from a PID alone."""
import json
import os
from pathlib import Path
import sys
if len(sys.argv) != 5:
    sys.exit(2)
execution, owner, run, checkout = sys.argv[1:]
records = json.loads((Path(os.environ["RESUME_RUNTIME_ROOT"]) / "receipts.json").read_text())
matching = [r for r in records if r["execution_id"] == execution and
             r["owner"] == owner and r["run"] == run and
             r["checkout"] == str(Path(checkout).resolve()) and
             r["terminal"] is True and r["execution_kind"] == "cooperative_process" and
             r["exit_code"] == 0]
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
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()
print(json.dumps({"pid":os.getpid(),"start":start,"head":head}), flush=True)
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
               "execution_kind": "cooperative_process", "terminal": True,
               "checkout": str(path.resolve()), "head": identity["head"],
               "pid": identity["pid"], "process_start": identity["start"],
               "exit_code": code, "observed_at": datetime.now(timezone.utc).isoformat(),
               "running_observed_at": observed_at}
    (root / "receipts.json").write_text(json.dumps([receipt]))
    assert subprocess.run(["python3", str(root / "read-receipt"), execution_id,
                           owner, run_id, str(path)], cwd=repo, env=case_env,
                          capture_output=True).returncode == 0
    assert subprocess.run(["python3", str(root / "read-receipt"), execution_id,
                            "wrong-owner", run_id, str(path)], cwd=repo, env=case_env,
                          capture_output=True).returncode == 3
    assert subprocess.run(["python3", str(root / "read-receipt"), "absent",
                            owner, run_id, str(path)], cwd=repo, env=case_env,
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
        "index": git(repo, env, "ls-files", "--stage"),
        # Include local-only and ignored bytes; .git is administrative, captured
        # separately by refs/index/reservation. Symlinks are never followed.
        "files": {str(p.relative_to(repo)): (
            {"symlink": os.readlink(p)} if p.is_symlink() else {"sha256": sha(p)})
            for p in sorted(repo.rglob("*"))
            if ".git" not in p.relative_to(repo).parts and (p.is_file() or p.is_symlink())},
        "change": sorted(str(p.relative_to(repo)) for p in
                         (repo / "openspec/changes").rglob("*") if p.is_file())
                  if (repo / "openspec/changes").is_dir() else [],
    }


def checked_json(args, *, cwd, env):
    return json.loads(run(args, cwd=cwd, env=env))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contract_source(root, revision):
    """Resolve exactly one committed active/archive contract, never a fallback."""
    paths = git(root, os.environ, "ls-tree", "-r", "--name-only", revision,
                "--", "openspec/changes").splitlines()
    roots = sorted({str(Path(p).parent) for p in paths
                    if p == f"openspec/changes/{CHANGE}/proposal.md" or re.fullmatch(
                        rf"openspec/changes/archive/\d{{4}}-\d{{2}}-\d{{2}}-{CHANGE}/proposal\.md", p)})
    if len(roots) != 1:
        raise RuntimeError(f"Expected one committed active/archive contract, found {roots}")
    selected = roots[0]
    files = {p: hashlib.sha256(subprocess.check_output(
        ["git", "show", f"{revision}:{p}"], cwd=root)).hexdigest()
        for p in paths if p.startswith(selected + "/")}
    for name in ("proposal.md", "design.md", "tasks.md"):
        if f"{selected}/{name}" not in files:
            raise RuntimeError(f"Incomplete committed contract: {name}")
    return {"revision": revision, "path": selected, "files": files}


def seed_proposal_review(repo, env, proposal_sha, validation, candidate, source_proposal):
    """Controlled fixture seed, NOT an independent review of the real candidate.

    Pin all proposal bytes and the successful strict result to an immutable Git
    review record. Keep candidate/source approval/fixture SHAs distinct.
    """
    contract = contract_source(repo, proposal_sha)
    review_path = ".fixture/proposal-review.json"
    review = {
        "kind": "controlled_fixture_seed", "reviewer": "fixture-reviewer",
        "decision": "approved", "proposal_sha": proposal_sha,
        "files": contract["files"],
        "validation": {"command": STRICT_VALIDATE, "exit_code": 0, "output": validation},
        "source_candidate": candidate, "source_approved_proposal": source_proposal,
        "limit": "Seeded test input; not real independent approval of the candidate.",
    }
    path = repo / review_path
    path.parent.mkdir()
    path.write_text(json.dumps(review, indent=2) + "\n")
    git(repo, env, "add", review_path)
    git(repo, env, "-c", "user.name=Smoke", "-c", "user.email=smoke@example.org",
        "commit", "-qm", "controlled fixture proposal review")
    review_sha = git(repo, env, "rev-parse", "HEAD")
    # Facts independently read by the harness; model observations are checked
    # separately below. The declarative recovery file is only a locator.
    probes = [
        (["git", "show", "--format=%H", "--no-patch", proposal_sha], proposal_sha),
        (["git", "merge-base", "--is-ancestor", proposal_sha, review_sha], ""),
        (["git", "merge-base", "--is-ancestor", review_sha, "HEAD"], ""),
        (["git", "show", f"{review_sha}:{review_path}"], path.read_text()),
    ]
    for name, digest in contract["files"].items():
        content = git(repo, env, "show", f"{proposal_sha}:{name}")
        # git() strips output; hash the unstripped committed bytes instead.
        assert hashlib.sha256(subprocess.check_output(
            ["git", "show", f"{proposal_sha}:{name}"], cwd=repo, env=env)).hexdigest() == digest
        assert sha(repo / name) == digest
        probes.append((["git", "show", f"{proposal_sha}:{name}"], content))
    probes.append((["git", "diff", "--exit-code", proposal_sha, "--", contract["path"]], ""))
    for argv, expected in probes:
        assert run(argv, cwd=repo, env=env) == expected.strip()
    return {"proposal_sha": proposal_sha, "review_sha": review_sha,
            "review_path": review_path, "review": review,
            "probes": [{"command": shlex.join(argv), "output": expected.strip()}
                       for argv, expected in probes],
            "validation_command": STRICT_VALIDATE, "validation_output": validation.strip()}


def shell_output_matches(output, expected):
    # V2's native shell capture renders a successful empty stream this way.
    # Callers must ALSO prove exit=0; this marker never proves success alone.
    return isinstance(output, str) and (
        output.strip() == expected or (expected == "" and output.strip() == "(no output)"))


def t1_proposal_proof(events, session, repo, provenance, native_invocation):
    """Require actual successful same-session tool observations, never SHA echo."""
    calls = tool_events(events, session, tool="shell")
    def observed(command, expected, *, after=-1):
        return any(e["input"].get("command") == command and
                   e["input"].get("workdir", str(repo)) == str(repo) and
                   e["exit_code"] == 0 and e["truncated"] is False and
                   e["index"] > after and shell_output_matches(e["output"], expected)
                   for e in calls)
    return bool(
        provenance and native_invocation and
        all(observed(p["command"], p["output"]) for p in provenance["probes"]) and
        observed(provenance["validation_command"], provenance["validation_output"],
                 after=min(i["event_index"] for i in native_invocation)))


def read_only_permissions(repo, worktrees, reader, receipts, active, *, prechoice=False,
                          provenance=None):
    """V2 ordered rules (last match wins), not a shell sandbox.

    grep authorizes the regexp and glob the pattern, NOT the target directory.
    Keep both denied; exact shell listings provide discovery instead. External
    boundaries and content reads are independently constrained.
    """
    rules = [{"action": "*", "resource": "*", "effect": "deny"}]
    roots = [repo, *worktrees, reader.parent, active.resolve()]
    for root in roots:
        rules.append({"action": "external_directory", "resource": str(root) + "/*",
                      "effect": "allow"})
        rules.append({"action": "read", "resource": str(root) + "/*", "effect": "allow"})
    # Internal reads use Location-relative paths; don't grant ../ or all HOME.
    for path in ("recovery-evidence.json", ".agents/*", "openspec/*",
                 ".git/ai-workflow/*"):
        rules.append({"action": "read", "resource": path, "effect": "allow"})
    for name in ("resume-workflow", "openspec-apply-change", "openspec-explore"):
        rules.append({"action": "skill", "resource": name, "effect": "allow"})
    commands = ["git rev-parse --show-toplevel", "git rev-parse HEAD",
                "git rev-parse --path-format=absolute --git-common-dir",
                "git status --short", "git status --porcelain",
                "git status --porcelain=v1 --untracked-files=all",
                "git diff", "git diff --cached", "git log -5 --oneline",
                "git show --stat HEAD", "git branch --list", "git worktree list --porcelain",
                 "git ls-files", "git ls-files --stage",
                 shlex.join(["worktree-reservation", "list", "--repository", str(repo), "--json"]),
                 "openspec context --json", "openspec list --json",
                 f"openspec status --change {CHANGE} --json",
                 f"openspec show {CHANGE} --json",
                 f"openspec instructions apply --change {CHANGE} --json",
                 STRICT_VALIDATE,
                 "gh issue list", "gh pr list",
                 "ls .agents/skills", "find .agents/skills -name SKILL.md", "pwd"]
    for issue in receipts:
        commands.extend([f"gh api repos/disposable/recovery/issues/{issue}",
                         f"gh api --paginate repos/disposable/recovery/issues/{issue}",
                         f"gh issue view {issue}"])
    if 11 in receipts:
        commands.extend(["gh api repos/disposable/recovery/issues/13",
                         "gh api --paginate repos/disposable/recovery/issues/13",
                         "gh issue view 13", "gh pr view 12", "gh pr checks 12",
                         "gh pr view 12 --json number,headRefOid,state,statusCheckRollup,body"])
    for path in sorted((repo / ".agents/skills").glob("openspec-*/SKILL.md")):
        commands.append("ls " + shlex.quote(str(path.relative_to(repo))))
    for path in worktrees:
        for args in ("rev-parse --show-toplevel", "rev-parse HEAD", "status --short",
                     "status --porcelain=v1 --untracked-files=all", "diff", "diff --cached",
                     "log -5 --oneline", "ls-files --stage"):
            commands.append(f"git -C {shlex.quote(str(path))} {args}")
    for receipt in receipts.values():
        commands.append(shlex.join(["python3", str(reader), receipt["execution_id"],
                                    receipt["owner"], receipt["run"], receipt["checkout"]]))
    if provenance:
        commands.extend(p["command"] for p in provenance["probes"])
    rules.extend({"action": "shell", "resource": c, "effect": "allow"} for c in commands)
    if prechoice:
        rules.extend([
            {"action": "skill", "resource": "openspec-*", "effect": "deny"},
        ])
        for root in [repo, *worktrees]:
            rules.append({"action": "read", "resource": str(root / ".agents/skills/openspec-*"),
                          "effect": "deny"})
        rules.append({"action": "read", "resource": ".agents/skills/openspec-*",
                      "effect": "deny"})
    return rules


def disposable_path(home, inherited_path, operator_home):
    """Expose the fixture launcher, not executables from the operator's HOME."""
    source_home = Path(operator_home).resolve()
    system_paths = [
        entry for entry in inherited_path.split(os.pathsep)
        if entry and not Path(entry).resolve().is_relative_to(source_home)
    ]
    return os.pathsep.join([str(home / ".local/bin"), *system_paths])


def disposable_shell_guard(directory, repo, worktrees, permissions, env, *, repo_only_commands=()):
    """Materialize a temporary native V2 guard, not a distributed plugin.

    Shell permissions operate on scanner output and cannot constrain raw input.
    The native pre-spawn hook instead checks exact raw commands and cwd, and
    replaces the child environment with fixture-owned constants.
    """
    directory.mkdir(parents=True, exist_ok=False)
    commands = [r["resource"] for r in permissions
                if r["action"] == "shell" and r["effect"] == "allow"]
    if not commands or any(re.search(r'[$`\\\n\r;&|<>!*?{}()]', c) for c in commands):
        raise RuntimeError("fixture shell allowlist must contain only literal simple commands")
    safe_env = {key: env[key] for key in (
        "HOME", "PATH", "LANG", "TERM", "XDG_CONFIG_HOME", "XDG_DATA_HOME",
        "XDG_CACHE_HOME", "XDG_STATE_HOME", "RESUME_GH_ROOT", "RESUME_RUNTIME_ROOT",
        "OPENSPEC_TELEMETRY", "PYTHONDONTWRITEBYTECODE") if key in env}
    safe_env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
                    GIT_OPTIONAL_LOCKS="0", GIT_PAGER="cat", PAGER="cat",
                    GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.fsmonitor",
                    GIT_CONFIG_VALUE_0="false")
    roots = [str(p.resolve(strict=True)) for p in (repo, *worktrees)]
    policy = {"commands": {root: [c for c in commands if root == roots[0] or
                                  c not in repo_only_commands] for root in roots}, "env": safe_env,
              "audit": str(directory / "audit.jsonl")}
    policy_path = directory / "policy.json"
    policy_path.write_text(json.dumps(policy, indent=2) + "\n")
    plugin = directory / "index.mjs"
    shutil.copyfile(ROOT / "tests/fixtures/resume_shell_guard.mjs", plugin)
    return {"plugin": str(directory), "source": str(plugin), "plugin_sha256": sha(plugin),
            "policy": str(policy_path), "policy_sha256": sha(policy_path),
            "audit": policy["audit"], "cwd": roots,
            "mechanism": "native tool.execute.before + shell.create.before"}


def shell_guard_preflight(cli, repo, env, guard):
    """Use debug agents' activation barrier, not an early config snapshot."""
    audit = Path(guard["audit"])
    previous = audit.read_text().splitlines() if audit.exists() else []
    run([cli, "debug", "agents", "--standalone"], cwd=repo, env=env)
    events = [json.loads(line) for line in audit.read_text().splitlines()[len(previous):]]
    if not any(e == {"boundary": "setup", "decision": "active", "source": guard["source"]}
               for e in events):
        raise RuntimeError("native fixture shell guard not activated; no inference")
    guard["preflight"] = {"status": "active", "events": events,
                          "limit": "separate standalone; prompt admission also awaits plugins"}


def disposable_opencode_shim(bin_dir, cli):
    """Expose only the discovered executable, not the operator's HOME."""
    if not Path(cli).is_absolute():
        raise RuntimeError("OpenCode executable must be an absolute executable file")
    binary = Path(cli).resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise RuntimeError("OpenCode executable must be an absolute executable file")
    bin_dir.mkdir()
    shim = bin_dir / "opencode"
    shim.write_text("#!/bin/sh\nexec " + shlex.quote(str(binary)) + ' "$@"\n')
    shim.chmod(0o700)
    return shim


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
            "github": json.loads((gh_root / "state.json").read_text()),
            "registry": json.loads((repo / ".git/ai-workflow/worktrees.json").read_text()),
            "runtime": json.loads((Path(env["RESUME_RUNTIME_ROOT"]) / "receipts.json").read_text()),
            "openspec": {"context": context, "list": changes},
            }


def native_calls(events, session, native, expected_sha256=None):
    """Match a real model tool call and its successful output, not prose/CLI alone."""
    path = str(native.resolve())
    name = native.parent.name
    if not native.is_file() or (expected_sha256 and sha(native) != expected_sha256):
        return [], [], []
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
        # Only the runtime's skill tool is invocation. Direct reads/CLI/prose
        # are auxiliary evidence, never native invocation.
        if (tool == "skill" and inp.get("id") == name and name in output and
                str(native.parent) in output):
            invocation.append({"tool": tool, "id": part.get("id"), "name": name,
                               "path": path, "sha256": sha(native), "event_index": index})
        if tool in ("glob", "shell") and ".agents" in json.dumps(inp) and name in output:
            discovery.append({"tool": tool, "id": part.get("id"), "event_index": index})
        if tool == "read" and isinstance(inp.get("path"), str) and isinstance(output, str):
            requested = inp["path"]
            directory = native.parent.parent
            # Actual V2 directory-read format. A file containing the skill name,
            # a different listing, or prose about discovery is not discovery.
            target = Path(requested)
            canonical = (target if target.is_absolute() else directory.parent.parent / target)
            lines = output.splitlines()
            if (canonical == directory and lines and re.fullmatch(
                    rf"Read directory {re.escape(requested)}, entries \d+-\d+", lines[0]) and
                    name + "/" in lines[1:]):
                discovery.append({"tool": tool, "id": part.get("id"), "event_index": index})
        if tool == "shell" and (
            "openspec instructions " in inp.get("command", "") or
            "openspec validate " in inp.get("command", "")
        ) and output:
            instructions.append({"tool": tool, "id": part.get("id"), "event_index": index})
    # A later directory read cannot retroactively discover an invoked skill.
    # With no invocation yet (T7 ambiguity turn), retain listing-only discovery.
    if invocation:
        discovery = [d for d in discovery if d["event_index"] < min(
            i["event_index"] for i in invocation)]
    return discovery, invocation, instructions


def tool_events(events, session, *, tool=None, contains=None, completed_only=True):
    found = []
    for index, event in enumerate(events):
        if event.get("sessionID") != session or event.get("type") != "tool_use":
            continue
        part = event.get("part", {})
        state = part.get("state", {})
        if (completed_only and state.get("status") != "completed") or (
            tool and part.get("tool") != tool
        ):
            continue
        if contains and contains not in json.dumps(state.get("input", {})):
            continue
        found.append({"index": index, "input": state.get("input", {}),
                      "output": state.get("output", ""), "tool": part.get("tool"),
                      "id": part.get("id"),
                      "exit_code": state.get("metadata", {}).get("metadata", {}).get("exit"),
                      "truncated": state.get("metadata", {}).get("metadata", {}).get("truncated")})
    return found


def t7_visible_question(response):
    """Accept only a single neutral choice question with both issue/run pairs."""
    text = response.strip()
    # Full-match a bounded interrogative shape rather than searching for
    # selection verbs: declarative choices anywhere in the turn fail closed.
    return bool(re.fullmatch(
        r"(?:Qual\s+issue\s+e\s+run\s+você\s+escolhe|"
        r"Which\s+issue\s+and\s+run\s+do\s+you\s+choose)"
        r"\s*:\s*issue\s+#21\s*/\s*wf-disposable-a"
        r"\s+(?:ou|or)\s+issue\s+#22\s*/\s*wf-disposable-b\s*\?",
        text, re.IGNORECASE))


def native_attempts(events, session):
    """Every content/invocation attempt is a boundary, including failed tools."""
    attempts = tool_events(events, session, completed_only=False)
    def native_skill_path(path):
        return isinstance(path, str) and bool(re.search(
            r"(?:^|/)\.agents/skills/openspec-[^/]+/SKILL\.md$",
            os.path.normpath(path)))

    def native_content_target(path):
        """Content searches on a skill directory can expose SKILL.md too."""
        return isinstance(path, str) and bool(re.search(
            r"(?:^|/)\.agents/skills(?:/openspec-[^/]+(?:/SKILL\.md)?)?$",
            os.path.normpath(path)))

    def shell_native_read(event):
        if event["tool"] != "shell":
            return False
        command = event["input"].get("command")
        if not isinstance(command, str):
            return False
        try:
            tokens = shlex.split(command)
        except ValueError:
            return False
        return any(
            (Path(token).name in ("cat", "sed", "head", "tail", "less", "more",
                                  "grep", "rg") and
              # `rg --files` lists paths, but grep/rg content-mode can read
              # SKILL.md via a directory target, including on failed calls.
              not (Path(token).name == "rg" and "--files" in tokens[index + 1:]) and
              any((native_content_target(arg) if Path(token).name in ("grep", "rg")
                   else native_skill_path(arg)) for arg in tokens[index + 1:]))
            for index, token in enumerate(tokens))

    return [
        e for e in attempts
        if (e["tool"] == "skill" and
            str(e["input"].get("id", "")).startswith("openspec-")) or
             (e["tool"] == "read" and
              native_skill_path(e["input"].get("path"))) or
              (e["tool"] == "grep" and
               native_content_target(e["input"].get("path"))) or shell_native_read(e)]


def git_mutation(command):
    """Recognize Git's global -C/options before its verb, even on denied calls."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return True
    for index, token in enumerate(tokens):
        if Path(token).name != "git":
            continue
        tail = tokens[index + 1:]
        while tail and tail[0].startswith("-"):
            option = tail.pop(0)
            if option in ("-C", "-c", "--git-dir", "--work-tree"):
                tail = tail[1:]
        if tail and (tail[0] in ("add", "commit", "push", "checkout", "switch",
                                "reset", "clean", "stash", "merge", "rebase") or
                     tail[:2] == ["worktree", "add"]):
            return True
    return False


def forbidden_attempts(events, session):
    """Read-only recovery forbids attempts, not just successful mutations."""
    attempts = tool_events(events, session, completed_only=False)
    # Snapshot equality proves no effects, not that a forbidden attempt was
    # never made. Only actual tool calls count: listing or globbing skill paths
    # is discovery, not reading their SKILL.md contents.
    return [
        e for e in attempts
        if (e["tool"] == "question" and
            events[e["index"]].get("part", {}).get("state", {}).get("status") ==
            "completed") or
        e["tool"] in ("write", "edit", "patch", "apply_patch", "subagent") or
        "reconcile" in json.dumps(e["input"]) or
        (e["tool"] == "shell" and isinstance(e["input"].get("command"), str) and
          (git_mutation(e["input"]["command"]) or
           re.search(r"\b(?:worktree-reservation\s+(?:reserve|handoff|release|checkpoint)"
                    r"|workflow-event\s+(?:stage-start|dispatch|observe)"
                    r")\b", e["input"]["command"])))]


def t7_phase1_proof(events, session, response, before, after, resume_invocation):
    """A cancelled interactive form is not a user-visible disambiguation."""
    visible_question = t7_visible_question(response)
    return (visible_question and before == after and bool(resume_invocation)
             and not native_attempts(events, session)
             and not forbidden_attempts(events, session))


def t7_reinventory(events, session, first_native, repo, worktrees, reader, receipts):
    """Require successful phase-2 observations of this fixture before native use."""
    if forbidden_attempts(events, session):
        return False
    boundaries = native_attempts(events, session)
    if boundaries:
        first_native = min(first_native, min(e["index"] for e in boundaries))
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
    for path, issue in zip(worktrees, (21, 22)):
        roots_ok &= any(out == receipts[issue]["head"] for out in commands(
            ["git", "-C", str(path), "rev-parse", "HEAD"]))
        roots_ok &= any(out == "" for out in commands(
            ["git", "-C", str(path), "status", "--porcelain=v1", "--untracked-files=all"]))
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
        for data in json_outputs(["worktree-reservation", "list", "--repository", root, "--json"]))
    # Resolve the terminal receipt to the explicitly chosen run, not merely
    # to a command that mentions the receipt reader.
    receipt_ok = any(
        isinstance(data, dict) and data.get("terminal") is True and
        all(data.get(key) == chosen[key] for key in
             ("execution_id", "owner", "run", "checkout", "exit_code", "execution_kind"))
        for event in calls
        if (tokens := shlex.split(event["input"]["command"])) and
         tokens == ["python3", str(reader), chosen["execution_id"],
                    chosen["owner"], chosen["run"], chosen["checkout"]]
        for data in [parse_json_output(event["output"])])
    sources_ok = all(any(
        isinstance(data, dict) and data.get("number") == issue and
        isinstance(data.get("body"), str) and receipts[issue]["run"] in data["body"]
        for argv in (["gh", "api", "--paginate",
                      f"repos/disposable/recovery/issues/{issue}"],
                     ["gh", "api",
                       f"repos/disposable/recovery/issues/{issue}"])
        for data in json_outputs(argv)) for issue in (21, 22))
    return bool(roots_ok and openspec_ok and reservation_ok and receipt_ok and sources_ok)


def t5_sources(events, session, fixture, github, reads):
    """Successful fixture reads, not response substrings or attempted argv."""
    def observed(argv, expected):
        if not any(r.get("args") == argv and r.get("exit_code") == 0 and
                   r.get("result") == expected for r in reads):
            return False
        for event in tool_events(events, session, tool="shell"):
            command = event["input"].get("command", "")
            try:
                tokens = shlex.split(command)
                output = json.loads(event["output"])
            except (ValueError, TypeError):
                continue
            if tokens == ["gh", *argv] and output == expected:
                return True
        return False

    pr = github["pulls"].get(str(fixture["pr"]), {})
    checks = pr.get("statusCheckRollup", [])
    bound = (pr.get("number") == fixture["pr"] and pr.get("state") == "OPEN" and
             pr.get("headRefOid") == fixture["pr_head"] and checks and
             all(c.get("headSha") == fixture["pr_head"] and
                 c.get("status") == "COMPLETED" and c.get("conclusion") == "SUCCESS"
                 for c in checks) and fixture["merge_mode"] == "manual" and
             "manual" in pr.get("body", "").lower() and
             "13" in pr.get("body", "") and "blocked" in pr.get("body", "").lower())
    pr_read = any(observed(argv, pr) for argv in (
        ["pr", "view", "12"],
        ["pr", "view", "12", "--json", "number,headRefOid,state,statusCheckRollup,body"]))
    dependency = github["issues"].get("13", {})
    dependency_read = (
        dependency.get("number") == 13 and dependency.get("state") == "OPEN" and
        "PR #12" in dependency.get("body", "") and
        "do not dispatch" in dependency.get("body", "") and
        any(observed(argv, dependency) for argv in (
            ["api", "repos/disposable/recovery/issues/13"],
            ["api", "--paginate", "repos/disposable/recovery/issues/13"],
            ["issue", "view", "13"])))
    return bool(bound and pr_read and dependency_read)


def redact(text, env):
    for key, value in env.items():
        if value and re.search(r"PASSWORD|TOKEN|SECRET|API_KEY", key, re.I):
            text = text.replace(value, "[REDACTED]")
    return re.sub(r'(?i)((?:authorization|api[_-]?key|password|token)'
                  r'["\s:=]+)(?:Bearer\s+)?[^\s",}]+', r'\1[REDACTED]', text)


def persist(base, results):
    path = base / "results.json"
    temporary = base / "results.json.new"
    temporary.write_text(json.dumps(results, indent=2) + "\n")
    temporary.replace(path)


def model_preflight(cli, repo, env, record, override=None):
    """Native metadata only, same isolated env/location; never generate or retry."""
    record.update(source="RESUME_SMOKE_MODEL" if override else "native:/api/model/default",
                  requested=override, status="metadata_unavailable", inference_verified=False)
    def api(path):
        data = checked_json([cli, "api", "--standalone", "get", path], cwd=repo, env=env)
        if data.get("location", {}).get("directory") != str(repo):
            raise RuntimeError("model metadata belongs to a different Location")
        return data["data"]

    def summary(model):
        # Never retain provider settings, headers or credentials from the catalog.
        return {key: model.get(key) for key in
                ("id", "modelID", "providerID", "type", "enabled", "status",
                 "capabilities", "cost")}

    default = api("/api/model/default")
    catalog = api("/api/model")
    requested = override or (f"{default['providerID']}/{default['id']}" if default else None)
    matches = [m for m in catalog if f"{m['providerID']}/{m['id']}" == requested]
    record.update({"source": "RESUME_SMOKE_MODEL" if override else "native:/api/model/default",
                   "requested": requested, "default": summary(default) if default else None,
                   "catalog_matches": [summary(m) for m in matches],
                   "inference_verified": False, "status": "rejected"})
    if len(matches) != 1:
        raise RuntimeError("selected model absent/ambiguous in native catalog")
    model = matches[0]
    caps, costs = model.get("capabilities", {}), model.get("cost", [])
    if (model.get("enabled") is not True or model.get("status") == "deprecated" or
            model.get("type") != "chat" or caps.get("tools") is not True or
            "text" not in caps.get("input", []) or "text" not in caps.get("output", [])):
        raise RuntimeError("selected model lacks enabled chat/tools/text capability")
    if not costs or not all(
        all(type(value) in (int, float) and value == 0 for value in
            (cost.get("input"), cost.get("output"), cost.get("cache", {}).get("read"),
             cost.get("cache", {}).get("write"))) for cost in costs):
        raise RuntimeError("selected model pricing unknown or paid; no fallback")
    record["status"] = "metadata_eligible"
    return requested


class ModelExecutionError(RuntimeError):
    def __init__(self, metadata):
        self.metadata = metadata
        super().__init__(metadata["error"])


def execute_model(cli, repo, env, base, case, prompt, session=None, *, model):
    command = [cli, "run", "--standalone", "--archived", "--model", model,
               "--format", "json"]
    if session:
        command.extend(["--session", session])
    process = subprocess.Popen([*command, prompt], cwd=repo, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=360)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate(timeout=20)
    terminal = {
        "pid": process.pid, "exit_code": process.returncode, "timed_out": timed_out,
        "candidate": git(ROOT, os.environ, "rev-parse", "HEAD"),
        "finished_at": datetime.now(timezone.utc).isoformat()}
    (base / f"{case}-terminal.json").write_text(json.dumps(terminal))
    stdout, stderr = redact(stdout, env), redact(stderr, env)
    transcript = base / f"{case}-events.jsonl"
    transcript.write_text(stdout + "\n")
    (base / f"{case}-stderr.log").write_text(stderr)
    events, malformed = [], []
    for number, line in enumerate(stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if (not isinstance(event, dict) or not isinstance(event.get("type"), str) or
                    ("sessionID" in event and not isinstance(event["sessionID"], str)) or
                    ("part" in event and not isinstance(event["part"], dict))):
                raise ValueError("malformed event shape")
            if event.get("type") == "tool_use" and (
                    not isinstance(event.get("part", {}).get("state"), dict) or
                    not isinstance(event["part"]["state"].get("input"), dict)):
                raise ValueError("malformed tool state")
            events.append(event)
        except ValueError:
            malformed.append(number)
    texts = [item["part"]["text"] for item in events
             if item.get("type") == "text" and isinstance(item.get("part", {}).get("text"), str)]
    sessions = sorted({item["sessionID"] for item in events if item.get("sessionID")})
    metadata = {"exit_code": process.returncode, "timed_out": timed_out,
                "session_ids": sessions, "events": str(transcript),
                "terminal": str(base / f"{case}-terminal.json"),
                "stderr": str(base / f"{case}-stderr.log"), "malformed_lines": malformed,
                "error_events": [e for e in events if e.get("type") == "error"]}
    (base / f"{case}-terminal.json").write_text(json.dumps({**terminal, **metadata}))
    if (timed_out or process.returncode != 0 or malformed or metadata["error_events"] or
            not texts or len(sessions) != 1 or (session and sessions != [session])):
        metadata["error"] = (f"{case}: terminal/events incomplete; exit={process.returncode}, "
                             f"timeout={timed_out}, malformed={malformed} (not PASS)")
        raise ModelExecutionError(metadata)
    return events, "\n".join(texts), sessions[0], str(transcript)


def prepared_phase(base, results, case, record, launch, take_snapshot):
    """Write preparation BEFORE launch and finalize failures without advancing."""
    results["scenarios"].setdefault(case, []).append(record)
    record.update(status="prepared", outcome=False, unchanged=None, after=None,
                  after_status="unavailable", session_id=None)
    persist(base, results)
    try:
        value = launch()
    except Exception as error:
        record.update(status="failed", error=redact(str(error), os.environ))
        results.update(status="failed", finished_at=datetime.now(timezone.utc).isoformat())
        if isinstance(error, ModelExecutionError):
            record["execution"] = error.metadata
            ids = error.metadata["session_ids"]
            record["session_id"] = ids[0] if len(ids) == 1 else None
        raise
    finally:
        try:
            record["after"] = take_snapshot()
            record["after_status"] = "available"
            record["unchanged"] = record["before"] == record["after"]
        except Exception as error:
            record["after_error"] = redact(str(error), os.environ)
            record["after_status"] = "unavailable"
            record["unchanged"] = None
        persist(base, results)
    if record["after_status"] != "available":
        record.update(status="failed", error="after snapshot unavailable (not PASS)")
        results.update(status="failed", finished_at=datetime.now(timezone.utc).isoformat())
        persist(base, results)
        raise RuntimeError(record["error"])
    return value


def main():
    cli = shutil.which("opencode")
    openspec = shutil.which("openspec")
    if not cli or not openspec:
        raise RuntimeError("OpenCode V2 and OpenSpec are required")
    revision = run(["git", "rev-parse", "HEAD"], cwd=ROOT, env=os.environ)
    if run(["git", "status", "--porcelain"], cwd=ROOT, env=os.environ):
        raise RuntimeError("Commit the candidate before installing its exact revision")
    selected_contract = contract_source(ROOT, revision)
    output = os.environ.get("RESUME_SMOKE_OUTPUT")
    base = Path(output) if output else Path(tempfile.mkdtemp(
        prefix="resume-candidate-", dir="/tmp/opencode"))
    if output:
        base.mkdir(exist_ok=False)
    home = base / "home"
    home.mkdir()
    bin_dir = base / "bin"
    opencode_shim = disposable_opencode_shim(bin_dir, cli)
    # The installer checks gh on PATH. Expose the read-only fixture before that
    # preflight, never the operator's HOME or real authenticated GitHub CLI.
    shim = bin_dir / "gh"
    shutil.copy2(ROOT / "tests/fixtures/resume_gh.py", shim)
    shim.chmod(0o755)
    env = {key: os.environ[key] for key in ("PATH", "LANG", "TERM") if key in os.environ}
    path_entries = disposable_path(home, os.environ.get("PATH", os.defpath),
                                   os.environ["HOME"]).split(os.pathsep)
    env["PATH"] = os.pathsep.join([path_entries[0], str(bin_dir), *path_entries[1:]])
    env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"),
               XDG_DATA_HOME=str(home / ".local/share"),
               XDG_CACHE_HOME=str(home / ".cache"),
                XDG_STATE_HOME=str(home / ".local/state"),
                CODEX_HOME=str(home / ".codex"),
               OPENCODE_DB=str(base / "opencode.db"),
               OPENCODE_PASSWORD=secrets.token_hex(24),
               OPENSPEC_TELEMETRY="0", PYTHONDONTWRITEBYTECODE="1")
    assert shutil.which("opencode", path=env["PATH"]) == str(opencode_shim)
    assert run(["opencode", "--version"], cwd=ROOT, env=env) == run(
        [cli, "--version"], cwd=ROOT, env=env)
    assert run(["opencode", "--help"], cwd=ROOT, env=env) == run(
        [cli, "--help"], cwd=ROOT, env=env)
    assert run([openspec, "--version"], cwd=ROOT, env=env).startswith("2.")
    results = {"started_at": datetime.now(timezone.utc).isoformat(),
               "candidate": revision, "approved_proposal": APPROVED_PROPOSAL,
               "contract": selected_contract, "model": None,
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
    assert reservation.is_file()
    assert not (active / "scripts/workflow-event").exists()
    assert not (active / "scripts/workflow-report").exists()
    assert shutil.which("worktree-reservation", path=env["PATH"]) == str(
        home / ".local/bin/worktree-reservation")
    assert os.access(home / ".local/bin/worktree-reservation", os.X_OK)

    # No external GitHub requests or write endpoints, even during preparation.
    for case, prompt in PROMPTS.items():
        repo = base / case
        repo.mkdir()
        git(repo, env, "init", "-q")
        git(repo, env, "remote", "add", "origin", "https://github.com/disposable/recovery.git")
        # Copy the already-generated OpenSpec 2 native contract rather than
        # initializing/updating global or project configuration in the test.
        shutil.copytree(ROOT / ".agents", repo / ".agents")
        shutil.copytree(ROOT / "openspec", repo / "openspec")
        source = repo / selected_contract["path"]
        active_change = repo / "openspec/changes" / CHANGE
        if source != active_change:
            source.rename(active_change)
        # This fixture models interruption at the reviewed proposal, regardless
        # of whether the candidate has already completed/archived its own work.
        tasks = active_change / "tasks.md"
        tasks.write_text(tasks.read_text().replace("- [x]", "- [ ]"))
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
        provenance = (seed_proposal_review(repo, env, proposal_sha, validation, revision,
                                           APPROVED_PROPOSAL) if case == "T1" else None)
        fixture = {
            "T1": {"repository": "disposable/recovery", "issue": 61,
                   "run": "wf-disposable-t1", "scope": "single_issue",
                   "next": "apply-issue on the pinned validated OpenSpec revision",
                   "proposal_sha": proposal_sha},
            "T5": {"repository": "disposable/recovery", "milestone": 3,
                   "run": "wf-disposable-t5", "merge_mode": "manual",
                    "issue": 11, "pr": 12, "pr_head": proposal_sha,
                   "dependent_issue": 13, "dependency": "issue 13 waits for PR 12 merge"},
            "T7": {"repository": "disposable/recovery", "candidates": [
                {"run": "wf-disposable-a", "issue": 21, "stage": "apply"},
                {"run": "wf-disposable-b", "issue": 22, "stage": "apply"}],
                "result": "ambiguous"},
        }[case]
        evidence = repo / "recovery-evidence.json"
        fixture["strict_validation"] = validation
        fixture["candidate_sha"] = revision
        fixture["approved_source_proposal_sha"] = APPROVED_PROPOSAL
        fixture["contract_source"] = selected_contract
        if provenance:
            fixture["proposal_sources"] = {
                key: provenance[key] for key in
                ("proposal_sha", "review_sha", "review_path", "validation_command")}
            fixture["proposal_sources"]["commands"] = [
                p["command"] for p in provenance["probes"]]
        evidence.write_text(json.dumps(fixture, indent=2) + "\n")
        git(repo, env, "add", "-A")
        git(repo, env, "-c", "user.name=Smoke", "-c",
            "user.email=smoke@example.org", "commit", "-qm", "interrupted state")
        gh_root = base / f"{case}-github"
        gh_root.mkdir()
        issue_runs = [(fixture["issue"], fixture["run"])] if case != "T7" else [
            (candidate["issue"], candidate["run"]) for candidate in fixture["candidates"]]
        issues = {str(issue): {
            "number": issue, "url": f"https://github.com/disposable/recovery/issues/{issue}",
            "title": f"Read-only recovery fixture #{issue}", "state": "OPEN",
            "body": (f"Scope={'milestone:3' if case == 'T5' else 'single_issue'}; "
                     f"run={run_id}; merge_mode=manual. "
                     f"Validated proposal {proposal_sha}; next action "
                     f"{'review existing PR 12; consumer 13 waits for merge' if case == 'T5' else 'Apply, not executed in this read-only probe'}."),
            "comments": [{"body": "[DECISION] Read-only recovery. No merge or dispatch."}],
        } for issue, run_id in issue_runs}
        if case == "T5":
            issues["13"] = {"number": 13, "state": "OPEN",
                            "body": "Blocked until PR #12 is merged; do not dispatch."}
        pulls = {"12": {"number": 12, "headRefOid": fixture["pr_head"],
                         "state": "OPEN", "url": "https://github.com/disposable/recovery/pull/12",
                         "baseRefOid": proposal_sha, "isDraft": False,
                         "statusCheckRollup": [{"headSha": proposal_sha, "name": "fixture-check",
                                                "status": "COMPLETED", "conclusion": "SUCCESS"}],
                         "reviews": [], "body": "Merge manual. Consumer #13 blocked until merge."}
                 } if case == "T5" else {}
        (gh_root / "state.json").write_text(json.dumps({"issues": issues, "pulls": pulls}))
        (gh_root / "calls.jsonl").write_text("")
        (gh_root / "reads.jsonl").write_text("")
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
        before = snapshot(repo, worktrees, gh_root, reservation, case_env, openspec)
        calls_before = (gh_root / "calls.jsonl").read_text().splitlines()
        reads_before = (gh_root / "reads.jsonl").read_text().splitlines()
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
                "NESTA MESMA sessão somente leitura. Antes da skill, faça chamadas "
                "de ferramenta SEPARADAS, cada uma com um único comando, saída "
                "integral não modificada e status de saída próprio; não use "
                "echo, redirecionamento, `;`, `&&`, `||`, pipe nem agrupe probes. "
                "Confira `git rev-parse --show-toplevel` na raiz principal e "
                 "`git -C <checkout> rev-parse --show-toplevel` separadamente "
                 "para CADA um dos dois checkouts, e também `git -C <checkout> "
                 "rev-parse HEAD` e `git -C <checkout> status --porcelain=v1 "
                 "--untracked-files=all`, cada comando separado; `worktree-reservation list "
                 "--repository <raiz> --json` (launcher no PATH desta fixture); "
                "`gh api --paginate repos/disposable/recovery/issues/21` "
                "e `gh api --paginate repos/disposable/recovery/issues/22` "
                "em chamadas separadas; `openspec context --json` e "
                "`openspec list --json` em chamadas separadas. Confirme o writer "
                "anterior com um único comando independente `python3 <caminho de "
                "runtime_receipt_command> <execution_id> <owner> <run> <checkout>` usando "
                f"{selected['execution_id']}, {selected['owner']}, {selected['run']}; "
                "a variável de ambiente da fixture já está definida. Se qualquer "
                "probe falhar ou faltar, bloqueie; não substitua por resposta textual. "
                "Depois da escolha descubra .agents/skills e invoque explicitamente "
                "openspec-explore nativa pela ferramenta skill em modo somente leitura, "
                "depois execute openspec validate somente "
                "leitura para conferir o change no contexto da issue. "
                "Não invoque Apply, faça takeover, dispatch ou escrita.")
        for phase, message in enumerate(prompts, 1):
            permissions = read_only_permissions(repo, worktrees, reader, receipts,
                                                active,
                                                prechoice=case == "T7" and phase == 1,
                                                provenance=provenance)
            guard = disposable_shell_guard(
                runtime_root / f"shell-guard-phase{phase}", repo, worktrees, permissions, case_env,
                repo_only_commands=[p["command"] for p in provenance["probes"]]
                if provenance else [])
            case_env["OPENCODE_CONFIG_CONTENT"] = json.dumps({
                "$schema": "https://opencode.ai/config.json", "permissions": permissions,
                "plugins": [guard["plugin"]]})
            record = {"phase": phase, "prompt": message, "before": before,
                      "native": native_provenance, "runtime_receipts": receipts,
                      "shell_guard": guard,
                      "fixture_proposal_facts": provenance,
                      "permissions": permissions, "previous_session_id": session,
                      "model_preflight": {}}

            def launch():
                shell_guard_preflight(cli, repo, case_env, guard)
                persist(base, results)
                model = model_preflight(cli, repo, case_env, record["model_preflight"],
                                        os.environ.get("RESUME_SMOKE_MODEL"))
                results["model"] = model
                # Persist selected capabilities/source/pricing BEFORE inference.
                persist(base, results)
                return execute_model(cli, repo, case_env, base, f"{case}-phase{phase}",
                                     message, session, model=model)

            events, response, session, transcript = prepared_phase(
                base, results, case, record, launch,
                lambda: snapshot(repo, worktrees, gh_root, reservation, case_env, openspec))
            after = record["after"]
            calls_after = (gh_root / "calls.jsonl").read_text().splitlines()
            reads_after = (gh_root / "reads.jsonl").read_text().splitlines()
            new_reads = [json.loads(line) for line in reads_after[len(reads_before):]]
            new_calls = [json.loads(line) for line in calls_after[len(calls_before):]]
            calls_safe = all(not any(a == "--method" or a.startswith("body=") or
                                     a in ("edit", "create", "merge", "close", "delete")
                                     for a in args) for args in new_calls)
            native_discovery, native_invocation, native_instructions = (
                 native_calls(events, session, native, native_provenance["sha256"]))
            resume_invocation = tool_events(events, session, tool="skill",
                                            contains="resume-workflow") + [
                e for e in tool_events(events, session, tool="read",
                                       contains=str(skill)) if "resume-workflow" in e["output"]]
            receipt_reads = [e for e in tool_events(events, session, contains=str(reader))
                             if '"terminal": true' in e["output"] or
                                '"terminal":true' in e["output"]]
            if case == "T1":
                expected = (str(fixture["issue"]), fixture["run"], "Apply")
            elif case == "T5":
                expected = ("12", fixture["pr_head"], "manual", "13")
            elif phase == 1:
                expected = ("21", "22", "wf-disposable-a", "wf-disposable-b", "?")
            else:
                expected = ("21", "wf-disposable-a")
            outcome = (t7_visible_question(response) if case == "T7" and phase == 1
                       else all(term.lower() in response.lower() for term in expected))
            proposal_proved = (t1_proposal_proof(events, session, repo, provenance,
                                                native_invocation) if case == "T1" else None)
            record.update({"phase": phase, "prompt": message, "session_id": session,
                      "response": response, "events": transcript, "before": before,
                      "after": after, "unchanged": before == after,
                      "github_calls": new_calls, "github_read_only": calls_safe,
                      "native": native_provenance, "native_discovery": native_discovery,
                      "native_invocation": native_invocation,
                      "native_instructions": native_instructions,
                      "resume_invocation": resume_invocation, "runtime_receipts": receipts,
                       "runtime_reads": receipt_reads, "outcome": outcome,
                       "github_reads": new_reads, "status": "observed"})
            record["model_proposal_proved"] = proposal_proved
            phases.append(record)
            persist(base, results)
            required = before == after and calls_safe and new_calls and outcome
            required &= any(args[:1] == ["api"] for args in new_calls)
            if case == "T1":
                required &= proposal_proved
            if case == "T5":
                required &= t5_sources(events, session, fixture, before["github"], new_reads)
            if case == "T7" and phase == 1:
                # Any native invocation before explicit user choice fails closed.
                required &= t7_phase1_proof(events, session, response, before, after,
                                            resume_invocation)
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
                record.update(status="failed", proof_complete=False)
                persist(base, results)
                raise RuntimeError(f"{case} phase {phase}: recovery proof incomplete; "
                                    f"see {base}/results.json")
            record.update(status="proof_complete", proof_complete=True)
            persist(base, results)
            before, calls_before = after, calls_after
            reads_before = reads_after
        if case == "T7":
            assert phases[0]["session_id"] == phases[1]["session_id"]
    results["finished_at"] = datetime.now(timezone.utc).isoformat()
    (base / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"Model-backed observations retained at {base}/results.json; inspect responses "
          "and events against T1/T5/T7 before claiming scenario PASS")


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    main()
