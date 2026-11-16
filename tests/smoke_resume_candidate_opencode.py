#!/usr/bin/env python3
"""Model-backed recovery probe against a candidate snapshot, in disposable homes.

Run from a clean candidate commit: python3 tests/smoke_resume_candidate_opencode.py
This is a separate check from smoke_global_opencode.py (published-revision discovery).
It never uses real GitHub resources or the operator's OpenCode configuration.
The retained results are observations, not an automatic claim of agent correctness.
"""
import hashlib
import json
import os
from pathlib import Path
import re
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
        "OpenSpec; diga o último gate comprovado e a próxima ação. Esta prova é "
        "somente leitura: não inicie Apply nem crie branch, worktree ou change."
    ),
    "T5": (
        "Retome este milestone após interrupção. Reconstitua PR, dependência e "
        "merge mode da evidência persistida; indique a próxima ação sem agendar "
        "o consumidor. Prova somente leitura, sem operações GitHub de escrita."
    ),
    "T7": (
        "Continue de onde parou. Há duas execuções candidatas neste checkout. "
        "Use evidências duráveis e, se ambíguo, faça só a pergunta necessária. "
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

    # No external GitHub requests: fixture metadata stands in for read-only
    # GitHub evidence; a shim refuses *every* write request.
    bin_dir = base / "bin"
    bin_dir.mkdir()
    shim = bin_dir / "gh"
    shim.write_text("#!/usr/bin/env python3\n"
                    "import json,os,sys\n"
                    "from pathlib import Path\n"
                    "args=sys.argv[1:]\n"
                    "if len(args)>=2 and args[0] in ('issue','pr') and args[1] in ('view','list'):\n"
                    " print(Path(os.environ['RESUME_FIXTURE']).read_text()); sys.exit(0)\n"
                    "print('GitHub fixture is read-only; request refused',file=sys.stderr)\n"
                    "sys.exit(77)\n")
    shim.chmod(0o755)
    env["PATH"] = str(bin_dir) + os.pathsep + env["PATH"]

    for case, prompt in PROMPTS.items():
        repo = base / case
        repo.mkdir()
        git(repo, env, "init", "-q")
        git(repo, env, "-c", "user.name=Smoke", "-c",
            "user.email=smoke@example.org", "commit", "--allow-empty", "-qm", "base")
        fixture = {
            "T1": {"repository": "disposable/recovery", "issue": 61,
                   "run": "wf-disposable-t1", "scope": "single_issue",
                   "stage": "proposal_review", "result": "verified",
                   "next": "apply-issue on the pinned validated OpenSpec revision",
                   "writer": "stopped (disposable fixture)"},
            "T5": {"repository": "disposable/recovery", "milestone": 3,
                   "run": "wf-disposable-t5", "merge_mode": "manual",
                   "issue": 11, "pr": 12, "pr_head": "disposable-pr-head",
                   "dependent_issue": 13, "dependency": "issue 13 waits for PR 12 merge",
                   "stage": "pr_audit", "result": "pending"},
            "T7": {"repository": "disposable/recovery", "candidates": [
                {"run": "wf-disposable-a", "issue": 21, "stage": "apply"},
                {"run": "wf-disposable-b", "issue": 22, "stage": "apply"}],
                "result": "ambiguous"},
        }[case]
        if case == "T1":
            run([openspec, "init", "--tools", "opencode", str(repo)], cwd=base,
                env=env, timeout=90)
            shutil.copytree(ROOT / "openspec/changes" / CHANGE,
                            repo / "openspec/changes" / CHANGE)
            fixture["proposal_sha"] = git(
                repo, env, "hash-object", f"openspec/changes/{CHANGE}/proposal.md")
            fixture["strict_validation"] = run(
                [openspec, "validate", CHANGE, "--strict"], cwd=repo, env=env)
        evidence = repo / "recovery-evidence.json"
        evidence.write_text(json.dumps(fixture, indent=2) + "\n")
        git(repo, env, "add", "-A")
        git(repo, env, "-c", "user.name=Smoke", "-c",
            "user.email=smoke@example.org", "commit", "-qm", "interrupted state")
        # Untracked GitHub fixture lives outside the repo; the model can inspect
        # committed recovery-evidence.json, and gh read calls return these bytes.
        github_fixture = base / f"{case}-github.json"
        github_fixture.write_text(json.dumps(fixture, indent=2) + "\n")
        case_env = {**env, "RESUME_FIXTURE": str(github_fixture)}
        before = inventory(repo, case_env)
        command = [cli, "run", "--standalone", "--archived", "--model", MODEL,
                   "--format", "json", prompt]
        execution = subprocess.run(command, cwd=repo, env=case_env,
                                   capture_output=True, text=True, timeout=240)
        transcript = base / f"{case}-events.jsonl"
        transcript.write_text(execution.stdout + "\n")
        (base / f"{case}-stderr.log").write_text(execution.stderr)
        events = []
        for line in execution.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        texts = [item["part"]["text"] for item in events
                 if item.get("type") == "text" and isinstance(item.get("part", {}).get("text"), str)]
        sessions = sorted(set(re.findall(r"ses_[A-Za-z0-9]+", execution.stdout)))
        after = inventory(repo, case_env)
        record = {"prompt": prompt, "session_ids": sessions, "exit": execution.returncode,
                  "response": "\n".join(texts), "events": str(transcript),
                  "before": before, "after": after, "unchanged": before == after,
                  "model_text_observed": bool(texts)}
        results["scenarios"][case] = record
        (base / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        if execution.returncode or not texts or before != after:
            raise RuntimeError(f"{case}: model failed or modified the fixture; see {base}")
    results["finished_at"] = datetime.now(timezone.utc).isoformat()
    (base / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"Model-backed observations retained at {base}/results.json; inspect responses "
          "and events against T1/T5/T7 before claiming scenario PASS")


if __name__ == "__main__":
    main()
