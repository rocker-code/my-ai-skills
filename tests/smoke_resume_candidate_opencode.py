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
import secrets
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CHANGE = "issue-61-opencode-safe-resume"
MODEL = os.environ.get("RESUME_SMOKE_MODEL", "opencode/glm-5.3-flash-free")
PROMPTS = {
    "T1": (
        "Continue de onde parou nesta issue. Consulte evidências duráveis locais e "
        "OpenSpec; descubra as skills nativas em .agents/skills e invoque a "
        "skill OpenSpec aplicável para conferir o próximo gate. Diga o último "
        "gate comprovado e a próxima ação. Esta prova é "
        "somente leitura: não inicie Apply nem crie branch, worktree ou change."
    ),
    "T5": (
        "Retome este milestone após interrupção. Reconstitua PR, dependência e "
        "merge mode da evidência persistida; descubra as skills OpenSpec nativas "
        "em .agents/skills e consulte a aplicável sem executar mudanças. "
        "Indique a próxima ação sem agendar "
        "o consumidor. Prova somente leitura, sem operações GitHub de escrita."
    ),
    "T7": (
        "Continue de onde parou. Há duas execuções candidatas neste checkout. "
        "Use evidências duráveis; descubra e consulte as skills OpenSpec nativas "
        "em .agents/skills apenas se isso não ultrapassar o gate de "
        "desambiguação. Se ambíguo, faça só a pergunta necessária. "
        "Prova somente leitura, sem escolher pela recência."
    ),
}


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
        if tool in ("glob", "shell") and ".agents/skills" in json.dumps(inp) and name in output:
            discovery.append({"tool": tool, "id": part.get("id"), "event_index": index})
    return discovery, invocation


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
        case_env = {**env, "RESUME_GH_ROOT": str(gh_root)}
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
            checked_json([str(reservation), "reserve", "--path", str(path), "--issue",
                          issue_url, "--branch", branch, "--session", f"seed-{case}",
                          "--run", run_id, "--json"], cwd=repo, env=case_env)
            seed_env = {**case_env, "RESUME_GH_SEED": "1"}
            event = [str(workflow_event), "--issue", issue_url, "--run-id", run_id]
            run([*event, "run-start", *(
                ["--scope", "milestone", "--milestone-url",
                 "https://github.com/disposable/recovery/milestone/3"] if case == "T5" else []
            )], cwd=repo, env=seed_env)
            if case == "T1":
                run([*event, "stage-start", "--stage", "proposal_review",
                     "--worker-id", "reviewer", "--execution-kind", "worker",
                     "--execution-id", "review-61"], cwd=repo, env=seed_env)
                run([*event, "observe", "--stage", "proposal_review", "--worker-id",
                     "reviewer", "--execution-kind", "worker", "--execution-id",
                     "review-61", "--state", "completed", "--source", "runtime_event",
                     "--next", f"Apply at {proposal_sha}"], cwd=repo, env=seed_env)
                run([*event, "stage-end", "--stage", "proposal_review", "--worker-id",
                     "reviewer", "--execution-kind", "worker", "--execution-id",
                     "review-61", "--status", "completed"], cwd=repo, env=seed_env)
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
                                 "--session", f"seed-{case}", "--json"], cwd=repo,
                                env=case_env)["ok"]
        # Exercise the public report reader against the actual seeded ledger.
        report = checked_json([str(workflow_report), issue_url, "--format", "json"],
                              cwd=repo, env=case_env)
        assert report["runs"] and report["runs"][0]["run_id"] == run_id
        before = snapshot(repo, worktrees, gh_root, reservation, case_env, openspec)
        calls_before = (gh_root / "calls.jsonl").read_text().splitlines()
        native_provenance = {"path": str(native), "resolved": str(native.resolve()),
                             "sha256": sha(native), "source_sha256":
                             sha(ROOT / ".agents/skills/openspec-apply-change/SKILL.md"),
                             "symlink": native.is_symlink()}
        assert native_provenance["sha256"] == native_provenance["source_sha256"]
        command = [cli, "run", "--standalone", "--archived", "--model", MODEL,
                   "--format", "json", prompt]
        try:
            execution = subprocess.run(command, cwd=repo, env=case_env,
                                       capture_output=True, text=True, timeout=240)
        except subprocess.TimeoutExpired as error:
            (base / f"{case}-timeout.log").write_bytes(error.stdout or b"")
            raise RuntimeError(f"{case}: model timeout; retained {base}") from error
        transcript = base / f"{case}-events.jsonl"
        transcript.write_text(execution.stdout + "\n")
        (base / f"{case}-stderr.log").write_text(execution.stderr)
        events = []
        for line in execution.stdout.splitlines():
            events.append(json.loads(line))
        texts = [item["part"]["text"] for item in events
                 if item.get("type") == "text" and isinstance(item.get("part", {}).get("text"), str)]
        sessions = sorted({item["sessionID"] for item in events if "sessionID" in item})
        after = snapshot(repo, worktrees, gh_root, reservation, case_env, openspec)
        calls_after = (gh_root / "calls.jsonl").read_text().splitlines()
        new_calls = [json.loads(line) for line in calls_after[len(calls_before):]]
        calls_safe = all(not any(a == "--method" or a.startswith("body=") or
                                 a in ("edit", "create", "merge", "close", "delete")
                                 for a in args) for args in new_calls)
        native_discovery, native_invocation = (
            native_calls(events, sessions[0], native) if len(sessions) == 1 else ([], []))
        resume_invocation = [item["part"]["id"] for item in events
                             if item.get("sessionID") in sessions and
                             item.get("type") == "tool_use" and
                             item["part"].get("tool") == "skill" and
                             item["part"]["state"].get("status") == "completed" and
                             item["part"]["state"].get("input", {}).get("id") == "resume-workflow"]
        response = "\n".join(texts)
        if case == "T1":
            expected = (str(fixture["issue"]), fixture["run"], proposal_sha[:8], "Apply")
        elif case == "T5":
            expected = ("12", fixture["pr_head"], "manual", "13")
        else:
            expected = ("21", "22", "wf-disposable-a", "wf-disposable-b")
        outcome = all(term.lower() in response.lower() for term in expected)
        if case == "T7":
            outcome = outcome and "?" in response
        record = {"prompt": prompt, "session_ids": sessions, "exit": execution.returncode,
                  "response": response, "events": str(transcript),
                  "before": before, "after": after, "unchanged": before == after,
                  "github_calls": new_calls, "github_read_only": calls_safe,
                  "native": native_provenance, "native_discovery": native_discovery,
                  "native_invocation": native_invocation,
                  "resume_invocation": resume_invocation, "outcome": outcome,
                  "model_text_observed": bool(texts)}
        results["scenarios"][case] = record
        (base / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        if (execution.returncode or not texts or len(sessions) != 1 or before != after
                or not calls_safe or not resume_invocation or not native_discovery
                or not native_invocation or not outcome or
                not any(d["event_index"] < i["event_index"] for d in native_discovery
                        for i in native_invocation)):
            raise RuntimeError(f"{case}: recovery proof incomplete; see {base}/results.json")
    results["finished_at"] = datetime.now(timezone.utc).isoformat()
    (base / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"Model-backed observations retained at {base}/results.json; inspect responses "
          "and events against T1/T5/T7 before claiming scenario PASS")


if __name__ == "__main__":
    main()
