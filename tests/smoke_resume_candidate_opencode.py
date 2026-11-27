#!/usr/bin/env python3
"""Fail-closed model-backed recovery probe against disposable Git/GitHub fixtures.

Run from a clean candidate commit: python3 tests/smoke_resume_candidate_opencode.py
This is a separate check from smoke_global_opencode.py (published-revision discovery).
It never uses real GitHub resources or the operator's OpenCode configuration.
Only an exact clean candidate HEAD is eligible; retained results are audited evidence.
"""
import argparse
import base64
import copy
import fcntl
from contextlib import closing
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import selectors
import shlex
import shutil
import signal
import sqlite3
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
CHANGE = "issue-61-opencode-safe-resume"
APPROVED_PROPOSAL = "c0224e1e8825def93c2d72e1e78685b22cfd8e29"
RUNTIME_VERSION = "2.4.2"
RUNTIME_SHA256 = "523b1502d1d556998b0904235cef65eb1d8cf8362b4e2faa7ae7a170c9a44cd4"
RUNTIME_SOURCE = "fc31a485317970bcf6be7b431a9830aaef875731"
VERIFY_SHA256 = "3b86fbb9734fdb6b942dd12d0afa4247457aa7f212bb48832eae133f5e66880a"
VERIFY_GENERATOR_VERSION = "2.1.1"
T1_HANDOFF_FIELDS = frozenset((
    "issue", "run", "evidence_scope", "proposal_sha", "review_sha", "last_verified_gate",
    "apply_executed", "status", "blockers", "limitations", "ownership_condition", "next_action"))
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
        "Use os comandos completos e cwd publicados pela fixture verbatim: a "
        "restrição compara bytes brutos, inclusive aspas/espaços, não só argv. "
        "Não componha nem reformule comandos. Relate fontes verificadas e lacunas."
        " Distinga fingerprints de origem e da fixture transformada; o seed só "
        "comprova o estado controlado da fixture, não aprovação real da candidata. "
        "Na última resposta retorne SOMENTE um objeto JSON de handoff com: "
        "issue (número), run, evidence_scope, proposal_sha, review_sha, "
        "status (RECOVERED ou BLOCKED), last_verified_gate, next_action, "
        "apply_executed (booleano), blockers (somente impedimentos ATUAIS ao "
        "handoff) e limitations (limites honestos de escopo/método/estágio futuro). "
        "Escopo de seed, checksum não recalculado pelo modelo e testes pós-Apply "
        "ainda futuros não são por si blockers da retomada anterior. Inventário "
        "atual não observado, owner conflitante/vivo ou término inconclusivo SÃO "
        "impedimentos da ação dependente, não podem ser ocultados em limitations. "
        "RECOVERED identifica o último gate; não concede posse nem permissão de "
        "escrever. A próxima ação segura pode ser reconcile-ownership antes de "
        "apply-issue. Inclua ownership_condition como objeto com phase, kind, "
        "checkout, execution_id, owner, run e write_authorized. phase deve ser "
        "before-write; kind é prior-stopped-owner para ACTIVE do mesmo writer "
        "comprovadamente parado, ou released-unreserved para WAITING sem owner "
        "com receipt correto. Copie as identidades das fontes observadas, não "
        "infira término/posse. write_authorized deve ser false: esta prova nunca "
        "concede escrita. Uma condição ausente, desconhecida ou incompatível "
        "não pode ser convertida em pré-escrita por texto. Use os locators "
        "de inventário e confronte o owner atual com o receipt real. Use "
        "evidence_scope=controlled_fixture para esta prova; só use RECOVERED "
        "com last_verified_gate=proposal_review_validated e next_action=apply-issue "
        "(ou reconcile-ownership como condição anterior a efeitos) "
        "se esses gates foram realmente comprovados. Não execute essa ação."
    ),
    "T5": (
        "Retome este milestone após interrupção. Comece lendo recovery-evidence.json "
        "neste checkout: é o entrypoint legível do escopo selecionado e dos locators "
        "somente leitura. Confronte esse escopo com as fontes publicadas; referências "
        "de repositório/issue/PR no plano OpenSpec copiado são proveniência do "
        "template produtor, não seleção de alvo nem autorização para consultá-lo. "
        "Reconstitua PR, dependência e merge mode das fontes GitHub da fixture, "
        "usando os comandos completos e cwd publicados verbatim, sem reformulação "
        "de aspas/argumentos/composição. Descubra e invoque a skill OpenSpec nativa "
        "aplicável para conferir o gate, e execute `openspec validate "
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
        raise RuntimeError(f"fixture command exited {result.returncode}; raw diagnostics omitted")
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


def input_files(root):
    """Byte inventory of the supplied consumed tree, with paths/modes/symlinks.

    No path-name based 'docs are irrelevant' exemption. The caller chooses an
    actual source/installed/prepared input root, never a transient DB or secrets.
    """
    root = Path(root)
    if not root.exists():
        raise RuntimeError(f"Missing effective input root: {root}")
    files = {}
    for path in sorted(root.rglob("*")) if root.is_dir() else [root]:
        if path.is_file() or path.is_symlink():
            files[str(path.relative_to(root)) if root.is_dir() else path.name] = {
                "sha256": sha(path), "mode": stat.S_IMODE(path.lstat().st_mode),
                "symlink": os.readlink(path) if path.is_symlink() else None,
                "resolved": str(path.resolve())}
    return {"root": str(root), "files": files}


def input_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":")).encode()).hexdigest()


def effective_input_binding(source, revision, contract, active, repo, gh_root, runtime_root,
                            home, env, *, phase, prompt, permissions, guard, model,
                            runtime_paths, approved_contract, native_candidates, session=None):
    """Record actual source AND transformed inputs, not a blanket source-path claim.

    Written before inference. No credential values, DB bytes or model answer are
    included. Delivered catalog/session/events/terminal are bound separately after
    execution; this preparation by itself never proves native behavior.
    """
    source_paths = (
        "tests/smoke_resume_candidate_opencode.py", "tests/fixtures/resume_gh.py",
        "tests/fixtures/resume_shell_guard.mjs",
        "scripts/install-global", "scripts/worktree-reservation", "scripts/worktree_registry.py")
    source_files = {p: input_files(source / p) for p in source_paths}
    prepared = {p: input_files(repo / p) for p in
                (".agents", "openspec", "recovery-evidence.json")}
    installed = input_files(active)
    rules = input_files(home / ".config/opencode/AGENTS.md")
    wire = {
        "phase": phase, "prompt": prompt, "permissions": permissions,
        "native_inspection_candidates": native_candidates,
        "config": json.loads(env["OPENCODE_CONFIG_CONTENT"]),
        "guard": {key: input_files(guard[key]) for key in ("source", "policy")},
        "github_shim": input_files(Path(env["PATH"].split(os.pathsep)[1]) / "gh"),
        "github_state": input_files(gh_root / "state.json"),
        "runtime_reader": input_files(runtime_root / "read-receipt"),
        "runtime_receipts": input_files(runtime_root / "receipts.json"),
        # An allowlist, not an environment dump. OPENCODE_PASSWORD is excluded.
        "child_environment": {k: env.get(k) for k in (
            "PATH", "HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME",
            "XDG_STATE_HOME", "CODEX_HOME", "OPENCODE_DB", "OPENSPEC_TELEMETRY",
            "PYTHONDONTWRITEBYTECODE", "RESUME_GH_ROOT", "RESUME_RUNTIME_ROOT", "LANG", "TERM")},
        "authentication": "Disposable generated password; credential value intentionally excluded.",
        "runtime": {name: {"path": shutil.which(name, path=env["PATH"]),
                            "resolved": str(Path(shutil.which(name, path=env["PATH"])).resolve()),
                            "version": run([name, "--version"], cwd=repo, env=env),
                            "executable": input_files(runtime_paths[name])}
                    for name in ("git", "openspec", "opencode")},
        "python": {"path": sys.executable, "version": sys.version,
                   "executable": input_files(sys.executable)},
        "model_preflight": model,
        "run_argv": [runtime_paths["opencode"], "run", "--standalone", "--archived", "--model",
                     model["requested"], "--format", "json",
                     *(["--session", session] if session else [])],
    }
    value = {"format": "resume-effective-inputs-v1",
             "source": {"candidate": revision, "approved_proposal": APPROVED_PROPOSAL,
                        "approved_contract": approved_contract,
                        "contract": contract, "files": source_files},
             "effective": {"installed_snapshot": installed, "loaded_rules": rules,
                           "prepared_fixture": prepared, "wire": wire},
             "limit": "Preparation binding only; independent impact review and complete "
                      "actual T1/T5/T7 observations remain mandatory."}
    # Freeze metadata against later caller mutation; file/input bytes are NOT normalized.
    value = copy.deepcopy(value)
    return {**value, "sha256": input_digest(value)}


def effective_input_diff(previous, current):
    """Exact changed leaves for independent impact review, NEVER an approval.

    Do not strip hashes, normalize text, or automatically bless relocated paths.
    Even provenance-only mappings require the reviewer to cite immutable refs and
    explain every difference. Material/uncertain deltas require a complete smoke.
    """
    def leaves(value, prefix=""):
        if isinstance(value, dict) and value:
            return {p: v for k, child in value.items()
                    for p, v in leaves(child, f"{prefix}/{k}").items()}
        return {prefix: value}
    valid = all(isinstance(v, dict) and v.get("format") == "resume-effective-inputs-v1" and
                isinstance(v.get("source"), dict) and
                isinstance(v["source"].get("files"), dict) and
                isinstance(v.get("effective"), dict) and set(v["effective"]) == {
                    "installed_snapshot", "loaded_rules", "prepared_fixture", "wire"} and
                v.get("sha256") == input_digest({k: x for k, x in v.items() if k != "sha256"})
                for v in (previous, current))
    if not valid:
        return {"status": "incomplete", "reuse_permitted": False,
                "requires_complete_native_smoke": True, "differences": []}
    old, new = (leaves({k: v for k, v in x.items() if k != "sha256"})
                for x in (previous, current))
    differences = [{"field": p, "before": old.get(p), "after": new.get(p),
                    **({"before_present": p in old, "after_present": p in new}
                       if p not in old or p not in new else {})}
                   for p in sorted(set(old) | set(new))
                   if p not in old or p not in new or old[p] != new[p]]
    changed_effective = any(d["field"].startswith("/effective/") for d in differences)
    # Harness/oracle, shim, installer/reservation sources affect behavior too.
    changed_source = any(d["field"].startswith((
        "/source/files/", "/source/contract/files/", "/source/approved_contract/files/"))
                         for d in differences)
    return {"status": ("material_or_uncertain" if changed_effective or changed_source else
                       "provenance_review_required" if differences else "byte_identical"),
            "previous": previous["sha256"], "current": current["sha256"],
            "differences": differences, "reuse_permitted": False,
            "independent_impact_review": "required",
            "requires_complete_native_smoke": changed_effective or changed_source,
            "limit": "Only independent byte-identity/relevance review may justify behavioral "
                     "reuse; never exact-HEAD local approval or replacement native PASS."}


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


def artifact_comparison_prerequisites(repo, env, provenance):
    """Bounded fixture conditions for native Git diff, NOT universal diff proof.

    Harness-owned Git/physical observations, captured before AND after the turn.
    Model-observed commit/review/comparison/strict are independently required.
    Use the existing native child Git environment; never inspect operator config.
    """
    env = {key: env[key] for key in (
        "HOME", "PATH", "LANG", "TERM", "XDG_CONFIG_HOME", "XDG_DATA_HOME",
        "XDG_CACHE_HOME", "XDG_STATE_HOME", "RESUME_GH_ROOT", "RESUME_RUNTIME_ROOT",
        "OPENSPEC_TELEMETRY", "PYTHONDONTWRITEBYTECODE") if key in env}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
               GIT_OPTIONAL_LOCKS="0", GIT_PAGER="cat", PAGER="cat",
               GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.fsmonitor",
               GIT_CONFIG_VALUE_0="false")
    result = {"verified": False, "repo": str(repo)}
    try:
        proposal, review = provenance["proposal_sha"], provenance["review_sha"]
        scope = f"openspec/changes/{CHANGE}"
        contract = {"files": provenance["review"]["files"]}
        paths = sorted(contract["files"])
        if "HOME" not in env or not all(
                Path(env[key]).resolve().is_relative_to(repo.parent.resolve())
                for key in ("HOME", "XDG_CONFIG_HOME") if key in env):
            raise ValueError("private fixture Git HOME/config required")
        if (not {scope + "/" + name for name in ("proposal.md", "design.md", "tasks.md")} <=
                set(paths) or not all(p.startswith(scope + "/") for p in paths) or
                not any(p.startswith(scope + "/specs/") and p.endswith("/spec.md") for p in paths)):
            raise ValueError("required reviewed artifact set/scope mismatch")
        review_output = git(repo, env, "show", f"{review}:{provenance['review_path']}")
        if (json.loads(review_output) != provenance["review"] or
                provenance["review"]["proposal_sha"] != proposal or
                provenance["review"]["decision"] != "approved"):
            raise ValueError("immutable review/proposal binding mismatch")
        git(repo, env, "merge-base", "--is-ancestor", proposal, review)
        git(repo, env, "merge-base", "--is-ancestor", review, "HEAD")
        if git(repo, env, "config", "--bool", "--get", "core.filemode") != "true":
            raise ValueError("core.filemode must be true")
        conversion = subprocess.run(
            ["git", "config", "--get-regexp",
             r"^(core\.(autocrlf|eol|attributesfile)|filter\..*|diff\..*\.(textconv|command)|diff\.external)$"],
            cwd=repo, env=env, capture_output=True, text=True)
        if conversion.returncode not in (0, 1):
            raise ValueError("conversion config query failed")
        # The fixture has no conversion setup; do not infer arbitrary filter or
        # attribute semantics. An explicit false autocrlf is equivalent to none.
        settings = conversion.stdout.splitlines()
        if any(line.lower() != "core.autocrlf false" for line in settings):
            raise ValueError("conversion config outside bounded fixture conditions")
        attributes = git(repo, env, "check-attr", "--all", "-z", "--", *paths)
        if attributes:
            raise ValueError("applicable attributes outside bounded fixture conditions")
        tree = {}
        for entry in git(repo, env, "ls-tree", "-r", "-z", proposal, "--", scope).split("\0"):
            if entry:
                header, path = entry.split("\t")
                mode, kind, blob = header.split()
                if mode != "100644" or kind != "blob":
                    raise ValueError("reviewed artifacts must be regular 100644 blobs")
                tree[path] = (mode, blob)
        index = {}
        for entry in git(repo, env, "ls-files", "--stage", "-z", "--", *paths).split("\0"):
            if entry:
                header, path = entry.split("\t")
                mode, blob, stage = header.split()
                if stage != "0" or path in index:
                    raise ValueError("unmerged/duplicate artifact index entry")
                index[path] = (mode, blob)
        flags = git(repo, env, "ls-files", "-v", "-z", "--", *paths).split("\0")
        if (set(tree) != set(paths) or index != tree or
                {entry for entry in flags if entry} != {"H " + p for p in paths}):
            raise ValueError("artifact tracking/blob/mode/skip-or-assume flag mismatch")
        artifacts = {}
        for path in paths:
            physical = repo / path
            mode = physical.lstat().st_mode
            if (not stat.S_ISREG(mode) or mode & 0o111 or physical.resolve() != physical):
                raise ValueError("physical artifact type/mode mismatch")
            committed = subprocess.check_output(
                ["git", "show", f"{proposal}:{path}"], cwd=repo, env=env)
            digest = hashlib.sha256(committed).hexdigest()
            if digest != contract["files"][path] or sha(physical) != digest:
                raise ValueError("physical/proposal/review artifact hash mismatch")
            artifacts[path] = {"mode": tree[path][0], "blob": tree[path][1], "sha256": digest}
        result.update(verified=True, proposal_sha=proposal, review_sha=review,
                      head=git(repo, env, "rev-parse", "HEAD"), scope=scope,
                      artifacts=artifacts, review_output=review_output,
                      tracking_flags=sorted(e for e in flags if e),
                      filemode=True, conversion_settings=settings, attributes=attributes)
    except (KeyError, TypeError, ValueError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        result["error"] = str(error)
    return result


def t1_proposal_proof(events, session, repo, provenance, native_invocation, *, before=None,
                      artifact_states=None):
    """Native scoped comparison under verified conditions; body reads optional."""
    if (not provenance or not artifact_states or len(artifact_states) != 2 or
            not artifact_states[0] or artifact_states[0] != artifact_states[1]):
        return False
    state = artifact_states[0]
    if (state.get("verified") is not True or state.get("repo") != str(repo) or
            state.get("scope") != f"openspec/changes/{CHANGE}" or
            state.get("proposal_sha") != provenance["proposal_sha"] or
            state.get("review_sha") != provenance["review_sha"] or
            state.get("filemode") is not True or state.get("attributes") != "" or
            not isinstance(state.get("conversion_settings"), list) or
            any(line.lower() != "core.autocrlf false" for line in state["conversion_settings"]) or
            state.get("tracking_flags") != sorted("H " + p for p in provenance["review"]["files"]) or
            any(a.get("mode") != "100644" for a in state.get("artifacts", {}).values()) or
            {p: a["sha256"] for p, a in state.get("artifacts", {}).items()} !=
            provenance["review"]["files"]):
        return False
    calls = tool_events(events, session, tool="shell")
    before = len(events) if before is None else before
    def observed(command, expected):
        return any(e["input"].get("command") == command and
                   e["input"].get("workdir", str(repo)) == str(repo) and
                   e["exit_code"] == 0 and e["truncated"] is False and
                    e["index"] < before and shell_output_matches(e["output"], expected)
                   for e in calls)
    # These are roles in the native provenance chain, not a quota of body
    # locators. Keep every body command available for optional inspection.
    proposal, review = provenance["proposal_sha"], provenance["review_sha"]
    required = [
        (["git", "show", "--format=%H", "--no-patch", proposal], proposal),
        (["git", "merge-base", "--is-ancestor", proposal, review], ""),
        (["git", "merge-base", "--is-ancestor", review, "HEAD"], ""),
        (["git", "show", f"{review}:{provenance['review_path']}"], state["review_output"]),
        (["git", "diff", "--exit-code", proposal, "--", state["scope"]], ""),
    ]
    return bool(
        provenance and any(i["event_index"] < before for i in native_invocation) and
        all(observed(shlex.join(command), output) for command, output in required) and
        observed(provenance["validation_command"], provenance["validation_output"]))


def t1_apply_gate_proof(events, session, repo, provenance, native_invocation, *, before=None):
    """Apply NEXT is a CLI/source fact, separate from the native inspection ID."""
    before = len(events) if before is None else before
    if not provenance or not any(i["event_index"] < before for i in native_invocation):
        return False
    change = repo / "openspec/changes" / CHANGE
    tasks_path = change / "tasks.md"
    task_command = shlex.join(["git", "show", f"{provenance['proposal_sha']}:"
                               f"openspec/changes/{CHANGE}/tasks.md"])
    task_source = next((p["output"] for p in provenance["probes"]
                        if p["command"] == task_command), "")
    tasks = []
    for line, text in enumerate(task_source.splitlines(), 1):
        match = re.fullmatch(r"\s*-\s+\[([ xX])\]\s+(.+)", text)
        if match:
            tasks.append({"id": str(len(tasks) + 1), "description": match[2],
                          "done": match[1].lower() == "x",
                          "sourcePath": str(tasks_path), "line": line})
    complete = sum(t["done"] for t in tasks)
    if not tasks or complete == len(tasks):
        return False
    expected_files = {str(repo / p) for p in provenance["review"]["files"]}
    for event in tool_events(events, session, tool="shell"):
        if not (event["input"].get("command") ==
                f"openspec instructions apply --change {CHANGE} --json" and
                event["input"].get("workdir", str(repo)) == str(repo) and
                event["exit_code"] == 0 and event["truncated"] is False and
                event["index"] < before):
            continue
        try:
            output = json.loads(event["output"])
        except (ValueError, TypeError):
            continue
        if not isinstance(output, dict):
            continue
        context = output.get("contextFiles")
        if not (isinstance(context, dict) and all(
                isinstance(paths, list) and all(isinstance(p, str) for p in paths)
                for paths in context.values())):
            continue
        if (output.get("changeName") == CHANGE and output.get("changeDir") == str(change) and
                output.get("schemaName") == "spec-driven" and output.get("state") == "ready" and
                output.get("taskTrackingConfigured") is True and
                {p for paths in context.values() for p in paths} == expected_files and
                context.get("tasks") == [str(tasks_path)] and
                output.get("tasks") == tasks and output.get("progress") == {
                    "total": len(tasks), "complete": complete,
                    "remaining": len(tasks) - complete}):
            return True
    return False


def t1_handoff_value(events, session):
    """Parse only the bounded last same-session handoff; never rewrite its bytes."""

    texts = [(i, e["part"]["text"]) for i, e in enumerate(events)
             if e.get("sessionID") == session and e.get("type") == "text" and
             isinstance(e.get("part", {}).get("text"), str)]
    if not texts:
        return None, 0
    index, text = texts[-1]
    def unique_object(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError("duplicate handoff field")
        return result
    def reject_constant(value):
        raise ValueError("non-finite handoff value")
    try:
        if len(text.encode()) > 4096:
            return None, index
        value = json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)
        if not isinstance(value, dict):
            return None, index
        # Bound unknown data as well as known fields. Iteration avoids recursion
        # in the checker; the decoder's own recursion failure is also closed.
        pending, count = [(value, 1)], 0
        while pending:
            item, depth = pending.pop()
            count += 1
            if depth > 8 or count > 256:
                return None, index
            if isinstance(item, (dict, list)):
                if len(item) > 32:
                    return None, index
                children = [*item.keys(), *item.values()] if isinstance(item, dict) else item
                pending.extend((child, depth + 1) for child in children)
            elif isinstance(item, str):
                item.encode("utf-8")  # Reject unpaired surrogates, including object keys.
            elif isinstance(item, float) and not math.isfinite(item):
                return None, index
        extensions = {k: v for k, v in value.items() if k not in T1_HANDOFF_FIELDS}
        if (len(extensions) > 16 or
                len(json.dumps(extensions, ensure_ascii=False).encode()) > 2048):
            return None, index
    except (ValueError, TypeError, RecursionError, UnicodeError):
        return None, index
    return value, index


def t1_no_effect_conflicts(value):
    """Only explicit structured no-effect constraints; never classify free text."""
    pending, conflicts = [(value, [])], []
    while pending:
        item, path = pending.pop()
        if isinstance(item, dict):
            for key, child in item.items():
                if ((key in ("write_authorized", "apply_executed") and child is not False) or
                        (key == "effects" and (not isinstance(child, list) or child != []))):
                    conflicts.append([*path, key])
                pending.append((child, [*path, key]))
        elif isinstance(item, list):
            pending.extend((child, [*path, i]) for i, child in enumerate(item))
    return conflicts


def t1_serialization_diagnostics(events, session):
    """Quarantine bounded extensions verbatim, outside all trusted recovery fields.

    No value here authorizes effects or supplies facts/tool inputs. Meaning of
    unknown/free-text claims remains the EXISTING independent response/event review.
    """
    value, index = t1_handoff_value(events, session)
    extensions = {k: v for k, v in value.items() if k not in T1_HANDOFF_FIELDS} if value else {}
    text = events[index].get("part", {}).get("text") if value is not None else None
    return {"parse_compliance": "bounded" if value is not None else "failed",
            "legacy_error": "unexpected_handoff_fields" if extensions else None,
            "untrusted_extensions": extensions, "extension_keys": list(extensions),
            "raw_handoff": text,
            "raw_handoff_sha256": hashlib.sha256(text.encode()).hexdigest() if text else None,
            "structured_no_effect_conflicts": t1_no_effect_conflicts(value),
            "independent_response_event_review": "required"}


def t1_handoff(events, session, fixture, provenance):
    """Semantic fields only, NOT acceptance, blocker classification or write proof.

    Ownership corroboration and every native gate are checked separately. Textual
    diagnostics (including contradictory prose) MUST still be reviewed independently.
    Unknown fields are quarantined by serialization diagnostics, never merged
    into trusted fields. Their meaning cannot receive automatic approval.
    """
    value, index = t1_handoff_value(events, session)
    if value is None:
        return False, index
    expected = {"issue": fixture["issue"], "run": fixture["run"],
                 "evidence_scope": "controlled_fixture",
                 "proposal_sha": provenance["proposal_sha"], "review_sha": provenance["review_sha"],
                 "last_verified_gate": "proposal_review_validated", "apply_executed": False}
    return (not t1_no_effect_conflicts(value) and
             all(value.get(key) == item for key, item in expected.items()) and
             value.get("next_action") in ("apply-issue", "reconcile-ownership") and
             value.get("status") in ("RECOVERED", "BLOCKED") and
             all(isinstance(value.get(key), list) and len(value[key]) <= 8 and
                 all(isinstance(item, str) and 0 < len(item) <= 1024 for item in value[key])
                 for key in ("blockers", "limitations")) and
             type(value.get("issue")) is int and value.get("apply_executed") is False), index


def t1_serialization(events, session, fixture, provenance):
    """Keep the OLD strict convention visible; it no longer judges recovery."""
    value, _ = t1_handoff_value(events, session)
    if value is None:
        return "failed"
    expected = {"issue": fixture["issue"], "run": fixture["run"],
                "evidence_scope": "controlled_fixture",
                "proposal_sha": provenance["proposal_sha"], "review_sha": provenance["review_sha"],
                "status": "RECOVERED", "last_verified_gate": "proposal_review_validated",
                "next_action": value.get("next_action"), "apply_executed": False, "blockers": []}
    # The new typed condition is not part of the legacy presentation convention.
    body = {k: v for k, v in value.items() if k not in ("limitations", "ownership_condition")}
    valid, _ = t1_handoff(events, session, fixture, provenance)
    return "passed" if valid and body == expected else "failed"


def t1_ownership_context(before, receipt, fixture):
    """Bounded native snapshot condition, never a grant or a liveness inference.

    Callers must ALSO prove actual inventory/receipt observations before handoff.
    A declarative snapshot alone cannot satisfy t1_inventory_proof.
    """
    if not isinstance(receipt, dict):
        return None
    try:
        running = datetime.fromisoformat(receipt["running_observed_at"])
        stopped = datetime.fromisoformat(receipt["observed_at"])
        if (not running.tzinfo or not stopped.tzinfo or running > stopped or
                any(type(receipt.get(k)) is not int or receipt[k] <= 0
                    for k in ("pid", "process_start"))):
            return None
    except (KeyError, TypeError, ValueError):
        return None
    rows = before.get("reservation", {})
    selected = [(name, r) for name, r in rows.items() if r.get("path") == receipt.get("checkout") or
                r.get("issue_url") == (
                    f"https://github.com/{fixture['repository']}/issues/{fixture['issue']}")]
    if len(selected) != 1:
        return None
    name, row = selected[0]
    if not {"issue_url", "branch", "state", "owner", "head", "digest", "drift",
            "unknown_untracked_paths"} <= set(row):
        return None
    owner = row.get("owner")
    if (receipt.get("terminal") is not True or type(receipt.get("exit_code")) is not int or
            receipt["exit_code"] != 0 or receipt.get("execution_kind") != "cooperative_process" or
            receipt.get("run") != fixture["run"] or not all(isinstance(receipt.get(k), str) and
            receipt[k] for k in ("execution_id", "owner", "run", "checkout", "head")) or
            name != Path(receipt["checkout"]).name or name not in before.get("checkout_git", {}) or
            ("path" in row and row["path"] != receipt["checkout"]) or
            row.get("head") != receipt["head"] or
            row.get("issue_url") != (
                f"https://github.com/{fixture['repository']}/issues/{fixture['issue']}") or
            row.get("drift") is not None or row.get("unknown_untracked_paths") != [] or
            ("ok" in row and row["ok"] is not True) or
            ("exit_code" in row and row["exit_code"] != 0)):
        return None
    if (row.get("state") == "ACTIVE" and isinstance(owner, dict) and
            owner.get("session") == receipt["owner"] and owner.get("run") == receipt["run"] and
            owner.get("pid") in (None, receipt.get("pid"))):
        kind = "prior-stopped-owner"
    elif row.get("state") == "WAITING" and owner is None:
        kind = "released-unreserved"
    else:
        return None
    return {"phase": "before-write", "kind": kind, "write_authorized": False,
            **{k: receipt[k] for k in ("checkout", "execution_id", "owner", "run")}}


def t1_phase_evaluation(events, session, fixture, provenance, ownership, *, facts):
    """Technical conjunction, not a prose judge or final scenario approval.

    All listed facts are independently established by the existing native gates.
    Nonempty textual blockers are NEVER waived: even corroborated structured
    conditions leave response/event interpretation pending independent review.
    """
    semantic, _ = t1_handoff(events, session, fixture, provenance)
    value, _ = t1_handoff_value(events, session)
    required = {"terminal", "proposal", "apply_gate", "inventory", "snapshots",
                "github", "native", "resume", "no_stateful_attempts"}
    sources = set(facts) == required and all(v is True for v in facts.values())
    condition = value.get("ownership_condition") if value else None
    condition_proved = bool(ownership and isinstance(condition, dict) and
                            condition == ownership and condition.get("write_authorized") is False)
    proved = bool(semantic and sources and condition_proved)
    return {"read_only_facts_proven": proved,
            "source_facts_proven": sources, "semantic_fields_proven": semantic,
            "read_only_acceptance": "pending_independent_review" if proved else "blocked",
            "ownership_condition_proven": condition_proved,
            "write_authorized": False,
            "serialization_compliance": t1_serialization(events, session, fixture, provenance),
            "serialization_diagnostics": t1_serialization_diagnostics(events, session),
            "independent_response_event_review": "required",
            "scenario_pass": False, "facts": facts}


def delivered_skill_catalog(database, repo, session, *, turn_events=None):
    """Bounded native-owned DB projection, never operator DB/config or prompt text.

    Initial state alone can be merely prepared. Require its baseline to precede
    the first user and a completed native assistant. InstructionState.initial and
    SessionModelRequest.baseTranscript render that baseline for the model request
    in the audited V2.4.2 source. This is delivery, not skill-body invocation.
    """
    database = Path(database)
    if (database != repo.parent / "opencode.db" or not database.is_file() or
            database.resolve() != database):
        raise RuntimeError("catalog capture requires this disposable fixture database")
    # No backup, serialize, whole-file hash, credential queries or broad SELECT.
    # BEGIN pins a consistent WAL-aware read transaction. The authorizer makes
    # the column allowlist enforceable even if a later query is accidentally added.
    columns = {
        "session_v2": {"id", "directory", "version", "time_created"},
        "instruction_state": {"session_id", "epoch_start", "through_seq",
                              "initial_values", "current_values"},
        "instruction_blob": {"hash", "value"},
        "session_message": {"id", "seq", "time_created", "data", "session_id", "type"},
    }
    def authorize(action, table, column, *_):
        if action == sqlite3.SQLITE_READ:
            return (sqlite3.SQLITE_OK if column in columns.get(table, set())
                    else sqlite3.SQLITE_DENY)
        if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_TRANSACTION):
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_FUNCTION and column == "json_extract":
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    def times(raw):
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise RuntimeError("unsupported native message time schema")
        return {k: value[k] for k in ("firstToken", "completed") if k in value
                and type(value[k]) in (int, float)}
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as db:
        db.set_authorizer(authorize)
        db.execute("BEGIN")
        identity = db.execute(
            "SELECT id,directory,version,time_created FROM session_v2 WHERE id=?", (session,)).fetchone()
        state = db.execute(
            "SELECT epoch_start,through_seq,initial_values,current_values FROM instruction_state "
            "WHERE session_id=?", (session,)).fetchone()
        if not identity or identity[1:3] != (str(repo), RUNTIME_VERSION) or not state:
            raise RuntimeError("catalog session/root/version/baseline unavailable")
        key = "core/skill-guidance"
        initial, current = json.loads(state[2]), json.loads(state[3])
        digest = initial.get(key)
        if not digest or current.get(key) != digest:
            raise RuntimeError("initial catalog missing or changed")
        blob = db.execute("SELECT value FROM instruction_blob WHERE hash=?", (digest,)).fetchone()
        if not blob or len(blob[0].encode()) > 32768:
            raise RuntimeError("bounded catalog blob unavailable")
        messages = {}
        for role in ("user", "assistant"):
            row = db.execute(
                "SELECT id,seq,time_created,json_extract(data,'$.time') FROM session_message "
                "WHERE session_id=? AND type=? ORDER BY seq LIMIT 1", (session, role)).fetchone()
            if not row:
                raise RuntimeError("prepared baseline is not delivered assistant evidence")
            messages[role] = {"id": row[0], "seq": row[1], "created": row[2],
                              "time": times(row[3])}
        turn = {}
        if turn_events is not None:
            first = next((e for e in turn_events if e.get("sessionID") == session), {})
            if first.get("type") != "step_start":
                raise RuntimeError("native turn start unavailable for catalog delivery")
            assistant = db.execute(
                "SELECT id,seq,time_created,json_extract(data,'$.time') FROM session_message "
                "WHERE session_id=? AND type='assistant' AND id=?",
                (session, first.get("part", {}).get("messageID"))).fetchone()
            user = db.execute(
                "SELECT id,seq,time_created,json_extract(data,'$.time') FROM session_message "
                "WHERE session_id=? AND type='user' AND seq<? ORDER BY seq DESC LIMIT 1",
                (session, assistant[1] if assistant else -1)).fetchone()
            if not assistant or not user:
                raise RuntimeError("current native turn messages unavailable in fixture DB")
            turn["turn_messages"] = {
                role: {"id": row[0], "seq": row[1], "created": row[2], "time": times(row[3])}
                for role, row in (("user", user), ("assistant", assistant))}
        projection = {"origin": "native_disposable_db_snapshot", "session_id": identity[0],
                "directory": identity[1], "version": identity[2], "session_created": identity[3],
                "database": str(database), "snapshot_scope": "allowlisted-instruction-session-projection",
                "instruction_key": key, "blob_hash": digest, "catalog": json.loads(blob[0]),
                "epoch_start": state[0], "through_seq": state[1],
                "messages": messages,
                "semantics": "initial-baseline-before-completed-native-assistant", **turn}
        projection["snapshot_sha256"] = input_digest(projection)
        return projection


def catalog_discovery(catalog, events, session, repo, native, *, prior_catalog=None, prior_events=None):
    """Verify delivered IDs independently of the selected canonical skill body."""
    if not isinstance(catalog, dict):
        return []
    if prior_catalog is not None or prior_events is not None:
        # Same-session T7 continuation: recapture the CURRENT private DB, prove
        # the unchanged delivered baseline against the original turn, and bind
        # its new native assistant to this turn. Never relabel old metadata as
        # a new delivery, invocation, user choice or reinventory.
        try:
            baseline = ("origin", "session_id", "directory", "version", "session_created",
                        "database", "instruction_key", "blob_hash", "catalog",
                        "epoch_start", "through_seq", "messages", "semantics")
            if (not isinstance(prior_catalog, dict) or not prior_events or
                    any(catalog[k] != prior_catalog[k] for k in baseline) or
                    catalog["snapshot_sha256"] == prior_catalog["snapshot_sha256"] or
                    not catalog_discovery(prior_catalog, prior_events, session, repo, native) or
                    not catalog_discovery(catalog, prior_events, session, repo, native)):
                return []
            first = next(e for e in events if e.get("sessionID") == session)
            user, assistant = (catalog["turn_messages"][role] for role in ("user", "assistant"))
            previous = prior_catalog["messages"]["assistant"]
            if (first["type"] != "step_start" or first["part"]["messageID"] != assistant["id"] or
                    assistant["id"] == previous["id"] or
                    not previous["seq"] < user["seq"] < assistant["seq"] or
                    not (previous["time"]["completed"] <= user["created"] <= assistant["created"] <=
                         first["timestamp"] <= assistant["time"]["firstToken"] <=
                         assistant["time"]["completed"])):
                return []
        except (KeyError, TypeError, ValueError, StopIteration):
            return []
        return [{"tool": "native_catalog", "event_index": -1, "session_id": session,
                 "message_id": previous["id"], "turn_message_id": assistant["id"],
                 "blob_hash": catalog["blob_hash"], "scope": "unchanged-baseline-current-turn"}]
    try:
        entries = catalog["catalog"]
        digest = hashlib.sha256(json.dumps(
            entries, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        user, assistant = (catalog["messages"][role] for role in ("user", "assistant"))
        first = next(e for e in events if e.get("sessionID") == session)
        description = re.search(r"^description: (.+)$", native.read_text(), re.MULTILINE)[1]
        selected = {"id": native.parent.name, "name": native.parent.name, "description": description}
        if (catalog["origin"] != "native_disposable_db_snapshot" or
                catalog["semantics"] != "initial-baseline-before-completed-native-assistant" or
                catalog["session_id"] != session or catalog["directory"] != str(repo) or
                catalog["version"] != RUNTIME_VERSION or catalog["instruction_key"] != "core/skill-guidance" or
                catalog["database"] != str(repo.parent / "opencode.db") or
                catalog["blob_hash"] != digest or not isinstance(entries, list) or
                len(entries) > 16 or entries.count(selected) != 1 or
                any(set(e) != {"id", "name", "description"} for e in entries) or
                catalog["snapshot_scope"] != "allowlisted-instruction-session-projection" or
                not re.fullmatch(r"[a-f0-9]{64}", catalog["snapshot_sha256"]) or
                not (catalog["epoch_start"] == catalog["through_seq"] < user["seq"] < assistant["seq"]) or
                not (catalog["session_created"] <= user["created"] <= assistant["created"] <=
                     first["timestamp"] <= assistant["time"]["firstToken"] <=
                     assistant["time"]["completed"]) or
                first["type"] != "step_start" or first["part"]["messageID"] != assistant["id"]):
            return []
    except (KeyError, TypeError, ValueError, StopIteration):
        return []
    return [{"tool": "native_catalog", "event_index": -1, "session_id": session,
             "message_id": assistant["id"], "blob_hash": digest}]


def read_only_permissions(repo, worktrees, reader, receipts, active, *, prechoice=False,
                          provenance=None, case="T1"):
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
    if case == "T5":
        # Instruction loading only. Fail closed before advertising a missing or
        # counterfeit source; no shell/resource rule is added by this capability.
        t1_inspection_sources(repo, case=case)
        rules.append({"action": "skill", "resource": "openspec-verify-change", "effect": "allow"})
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


def read_only_locators(repo, worktrees, reader, receipts, permissions, *, case,
                       selected_issue=None, fixture=None):
    """Publish existing literal permissions, not a new source of authorization."""
    allowed = {r["resource"] for r in permissions
               if r["action"] == "shell" and r["effect"] == "allow"}
    result = {"raw_command_contract": (
        "Use the complete published command verbatim in its published cwd. "
        "Authorization compares raw bytes, including quotes and spaces, not merely argv. "
        "Do not add quotes, arguments, prefixes, redirection or composition.")}
    if case == "T1":
        command = f"openspec instructions apply --change {CHANGE} --json"
        assert command in allowed
        result["apply_instructions_locator"] = {"command": command, "cwd": str(repo)}
    if case == "T7" and selected_issue is None:
        result["runtime_receipt_note"] = (
            "No candidate is selected. The chosen writer's complete locator is "
            "published only after explicit issue/run choice.")
        return result
    if case == "T5":
        if (not fixture or fixture["issue"] not in receipts or
                fixture["run"] != receipts[fixture["issue"]]["run"]):
            raise ValueError("T5 locators require the selected fixture and matching writer")
        result["selected_scope"] = {key: fixture[key] for key in
                                   ("repository", "milestone", "issue", "pr",
                                    "dependent_issue", "run")}
        result["copied_plan_scope"] = (
            "The copied OpenSpec contract and its producer repository/issue/PR references "
            "are template provenance only, NOT the selected GitHub target. Consult the "
            "selected_scope through these fixture-only sources, never the producer or "
            "operator resources. Metadata and locators do not prove a successful read, "
            "a verified gate, ownership or permission to write.")
        github_locators = [
            ("issue_inventory", ["gh", "issue", "list"]),
            ("pr_inventory", ["gh", "pr", "list"]),
            ("selected_issue", ["gh", "api",
                                f"repos/{fixture['repository']}/issues/{fixture['issue']}"]),
            ("dependency", ["gh", "api",
                            f"repos/{fixture['repository']}/issues/{fixture['dependent_issue']}"]),
            ("pr_head_checks_mode", ["gh", "pr", "view", str(fixture["pr"])]),
            ("checks", ["gh", "pr", "checks", str(fixture["pr"])]),
        ]
        result["github_locators"] = [
            {"fact": fact, "command": shlex.join(argv), "cwd": str(repo)}
            for fact, argv in github_locators]
        # Publish a subset of the ALREADY allowed raw strings. A wrong fixture
        # identity must fail, not widen policy or silently fall back to producer IDs.
        assert all(item["command"] in allowed for item in result["github_locators"])
    inventory_locators = [
        {"fact": "branch_checkouts", "command": "git worktree list --porcelain", "cwd": str(repo)},
        {"fact": "registered_owners", "command": shlex.join(
            ["worktree-reservation", "list", "--repository", str(repo), "--json"]), "cwd": str(repo)},
    ]
    for path in (repo, *worktrees):
        inventory_locators.extend([
            {"fact": "dirty_untracked", "command": "git status --porcelain=v1 --untracked-files=all",
             "cwd": str(path)},
            {"fact": "index", "command": "git ls-files --stage", "cwd": str(path)},
        ])
    assert all(item["command"] in allowed for item in inventory_locators)
    result["inventory_locators"] = inventory_locators
    result["inventory_scope"] = (
        "Observe the actual branch/checkouts/index/status and registered owner, not an answer "
        "from metadata. This closed fixture is seeded from tracked files; the harness separately "
        "checks its full physical inventory before/after. Git status does NOT enumerate ignored "
        "files; do not claim an ignored scan. Unobserved extra local data or unknown/conflicting "
        "owner blocks the dependent action. A stopped prior writer is not ownership transfer; "
        "reconcile/reserve under the existing workflow before ANY effects. Candidate/source IDs "
        "are producer traceability, NOT permission to read operator files or the real repository.")
    if selected_issue is None:
        assert len(receipts) == 1
        selected_issue = next(iter(receipts))
    if selected_issue not in receipts:
        raise ValueError("receipt locator requires an explicitly identified fixture writer")
    receipt = receipts[selected_issue]
    identity = {key: receipt[key] for key in ("execution_id", "owner", "run", "checkout")}
    # Same primitive, fields and ordering as read_only_permissions; preserve that
    # function and the raw guard byte-for-byte, and check exact policy membership.
    command = shlex.join(["python3", str(reader), identity["execution_id"],
                          identity["owner"], identity["run"], identity["checkout"]])
    assert command in allowed
    result.update(runtime_receipt_command=command, runtime_receipt_cwd=str(repo),
                  runtime_receipt_allowed_cwds=[str(p) for p in (repo, *worktrees)],
                  runtime_receipt_identity=identity,
                  runtime_receipt_identity_scope=(
                      "Cooperative WRITER identity from the actual receipt, not the "
                      "model/observer session. Command cwd is not receipt checkout. "
                      "These locators do not prove terminal state; run the reader."))
    return result


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


def snapshot(repo, worktrees, gh_root, reservation, env, openspec, *, provenance=None):
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
    result = {"git": inventory(repo, env),
            "checkout_git": {path.name: inventory(path, env) for path in worktrees},
            "reservation": statuses,
            "github": json.loads((gh_root / "state.json").read_text()),
            "registry": json.loads((repo / ".git/ai-workflow/worktrees.json").read_text()),
            "runtime": json.loads((Path(env["RESUME_RUNTIME_ROOT"]) / "receipts.json").read_text()),
             "openspec": {"context": context, "list": changes},
             }
    if provenance is not None:
        result["artifact_comparison"] = artifact_comparison_prerequisites(repo, env, provenance)
    return result


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
        if part.get("sessionID", session) != session:
            continue
        if "messageID" in part and not any(
                e.get("type") == "step_start" and e.get("sessionID") == session and
                e.get("part", {}).get("messageID") == part["messageID"] for e in events[:index]):
            continue
        state = part.get("state", {})
        if state.get("status") != "completed":
            continue
        tool = part.get("tool")
        inp = state.get("input", {})
        output = state.get("output", "")
        if not isinstance(output, str):
            continue
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


def t1_inspection_sources(repo, source_root=ROOT, *, case="T1",
                          generator_version=VERIFY_GENERATOR_VERSION):
    """Bounded canonical sources; only T5 may add the approved Verify bytes.

    VERIFY_SHA256 pins the official 2.1.1 generator's published content with its
    supported skill-reference conversion, not a manually synthesized fallback.
    The actual installed CLI version is checked before any model run.
    """
    sources = []
    names = (("openspec-explore",) if case == "T7" else
             ("openspec-explore", "openspec-apply-change"))
    if case == "T5":
        if generator_version != VERIFY_GENERATOR_VERSION:
            raise RuntimeError("T5 Verify capability BLOCKED: unsupported canonical generator version")
        names += ("openspec-verify-change",)
    for name in names:
        native = repo / ".agents/skills" / name / "SKILL.md"
        source = source_root / ".agents/skills" / name / "SKILL.md"
        if (not native.is_file() or not source.is_file() or
                native.resolve() != native or source.resolve() != source or
                sha(native) != sha(source) or
                (name == "openspec-verify-change" and sha(source) != VERIFY_SHA256)):
            if name == "openspec-verify-change":
                raise RuntimeError("T5 Verify capability BLOCKED: missing/noncanonical source/path/hash")
            continue
        sources.append({"path": str(native), "resolved": str(native.resolve()),
                        "sha256": sha(native), "source": str(source),
                        "source_sha256": sha(source), "symlink": False})
        if name == "openspec-verify-change":
            sources[-1]["generator"] = {"package": "@fission-ai/openspec",
                                       "version": VERIFY_GENERATOR_VERSION,
                                       "published_sha256": VERIFY_SHA256}
    return sources


def t1_native_inspection(events, session, repo, sources, catalog=None, *, before=None,
                         allowed_names=None, case="T1", validation=None,
                         prior_catalog=None, prior_events=None):
    """Bind discovery and real skill invocation to ONE verified official source.

    Do not combine discovery of one alternative with invocation of the other.
    T5 alone additionally admits Verify; T7 restricts to Explore. This proves inspection
    only; immutable proposal/Apply, PR facts, choice and reinventory stay separate.
    """
    try:
        canonical = t1_inspection_sources(repo, case=case)
    except RuntimeError:
        return None, [], [], []
    names = {Path(s["path"]).parent.name for s in canonical}
    for source in sources:
        native = Path(source["path"])
        if (native != repo / ".agents/skills" / native.parent.name / "SKILL.md" or
                native.parent.name not in names or
                (allowed_names is not None and native.parent.name not in allowed_names) or
                source not in canonical):
            continue
        discovery, invocation, instructions = native_calls(
            events, session, native, source["source_sha256"])
        delivered = catalog_discovery(
            catalog, events, session, repo, native,
            prior_catalog=prior_catalog, prior_events=prior_events)
        if native.parent.name == "openspec-verify-change" and not delivered:
            continue  # Prepared/debug catalog or listing alone is not delivery.
        discovery += delivered
        # Native output contains the official body (without YAML frontmatter).
        # A same-name/path claim or different skill content is not invocation.
        body = native.read_text().split("\n---\n", 1)[-1].strip()
        invocation = [i for i in invocation if body in events[i["event_index"]][
            "part"]["state"]["output"] and i["event_index"] < (
                len(events) if before is None else before) and any(
                d["event_index"] < i["event_index"] for d in discovery)]
        if invocation:
            if validation is not None:
                instructions = native_validation_calls(
                    events, session, repo, validation, before=before)
            return source, discovery, invocation, instructions
    return None, [], [], []


def native_validation_calls(events, session, repo, validation, *, before=None):
    """Actual applicable strict validation in the known fixture context.

    Do not accept help, an unrelated change, arbitrary instructions prose or a
    successful-looking output from a failed/truncated/wrong-cwd tool event.
    This is not an Apply-specific command or a post-skill repetition quota.
    """
    try:
        context = validation["context"]
        if (any(context[key]["root"]["path"] != str(repo) for key in ("context", "list")) or
                len([c for c in context["list"]["changes"] if c["name"] == CHANGE]) != 1 or
                not isinstance(validation["output"], str) or not validation["output"].strip()):
            return []
    except (KeyError, TypeError):
        return []
    boundary = len(events) if before is None else before
    return [{"tool": "shell", "id": e["id"], "event_index": e["index"]}
            for e in tool_events(events, session, tool="shell")
            if e["index"] < boundary and e["input"].get("command") == STRICT_VALIDATE and
            e["input"].get("workdir", str(repo)) == str(repo) and
            events[e["index"]]["part"].get("sessionID", session) == session and
            ("messageID" not in events[e["index"]]["part"] or any(
                prior.get("type") == "step_start" and prior.get("sessionID") == session and
                prior.get("part", {}).get("messageID") ==
                events[e["index"]]["part"]["messageID"] for prior in events[:e["index"]])) and
            e["exit_code"] == 0 and e["truncated"] is False and
            shell_output_matches(e["output"], validation["output"].strip())]


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


def reservation_mutation(command):
    """Recognize stateful reservation verbs with native argv/global cwd flags."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return True
    for index, token in enumerate(tokens):
        if Path(token).name != "worktree-reservation":
            continue
        tail = tokens[index + 1:]
        while tail and tail[0].startswith("-"):
            option = tail.pop(0)
            if option in ("--path", "--repository", "--session", "--run", "--lock-timeout"):
                tail = tail[1:]
        if tail and tail[0] in (
                "verify", "reserve", "handoff", "release", "checkpoint", "reconcile",
                "cancel-planned", "mark-removed", "track-generated", "clean-generated"):
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
           reservation_mutation(e["input"]["command"]) or
           re.search(r"\b(?:worktree-reservation\s+(?:reserve|handoff|release|checkpoint)"
                     r"|workflow-event\s+(?:stage-start|dispatch|observe)"
                     r")\b", e["input"]["command"])))]


def read_scope_attempts(events, session, repo, permissions, repository):
    """Diagnostic resource-boundary labels, NOT a language judge or deny policy."""
    roots = [Path(r["resource"][:-2]) for r in permissions
             if r["action"] == "external_directory" and r["effect"] == "allow" and
             r["resource"].endswith("/*")]
    result = {"out_of_scope_reads": [], "other_denied_attempts": []}
    for event in tool_events(events, session, completed_only=False):
        status = events[event["index"]]["part"]["state"].get("status")
        resource = None
        if event["tool"] in ("read", "grep", "glob"):
            path = event["input"].get("path")
            if isinstance(path, str):
                target = Path(os.path.normpath(path if Path(path).is_absolute() else str(repo / path)))
                if not any(target.is_relative_to(root) for root in roots):
                    resource = path
        elif event["tool"] == "shell":
            try:
                tokens = shlex.split(event["input"].get("command", ""))
            except (ValueError, TypeError):
                tokens = []
            if tokens[:2] == ["gh", "api"]:
                resource = next((p for p in tokens[2:] if p.startswith("repos/") and
                                 not p.startswith(f"repos/{repository}/")), None)
        entry = {"event_index": event["index"], "tool": event["tool"],
                 "id": event["id"], "status": status,
                 "provider_executed": events[event["index"]]["part"]["state"].get(
                     "metadata", {}).get("providerCall", {}).get("executed")}
        if resource:
            result["out_of_scope_reads"].append({
                **entry, "resource": resource,
                "resource_kind": "repository" if event["tool"] == "shell" else "filesystem"})
        elif status in ("error", "cancelled"):
            result["other_denied_attempts"].append(entry)
    return result


def t1_inventory_proof(events, session, repo, worktrees, reader, receipt,
                       fixture, before, after, *, handoff_index):
    """Observed inventory for read-only last-gate recovery, NEVER a write grant.

    Four existing source kinds cover this tracked-only fixture. Status/list do
    not enumerate ignored bytes: the full physical inventories must contain no
    extra paths and remain unchanged. Other local-only data needs more evidence.
    """
    if (before != after or not worktrees or not isinstance(receipt, dict) or
            not all(receipt.get(key) for key in
                    ("execution_id", "owner", "run", "checkout", "head"))):
        return False
    if (t1_ownership_context(before, receipt, fixture) is None or
            before.get("runtime") != [receipt]):
        return False
    calls = [e for e in tool_events(events, session, tool="shell")
             if e["index"] < handoff_index and e["exit_code"] == 0 and e["truncated"] is False]
    def outputs(command, cwd):
        return [e["output"] for e in calls if e["input"].get("command") == command and
                e["input"].get("workdir", str(repo)) == str(cwd)]
    def observed(args, path, expected):
        candidates = [(shlex.join(["git", *args]), path)]
        if path != repo:
            candidates.append((shlex.join(["git", "-C", str(path), *args]), repo))
        return any(shell_output_matches(out, expected)
                   for command, cwd in candidates for out in outputs(command, cwd))
    def json_value(output):
        try:
            return json.loads(output)
        except (ValueError, TypeError):
            return None
    roots = {repo: before["git"],
             **{path: before["checkout_git"][path.name] for path in worktrees}}
    # Closed-world precondition, NOT an assertion that status scans ignored.
    if any(set(g["files"]) - set(g["tracked"].splitlines()) for g in roots.values()):
        return False
    if not any(shell_output_matches(out, before["git"]["worktrees"])
               for cwd in roots for out in outputs("git worktree list --porcelain", cwd)):
        return False
    for path, state in roots.items():
        if not observed(["ls-files", "--stage"], path, state["index"]):
            return False
        if not any(observed(["status", *flags], path, state["status"]) for flags in (
                ["--porcelain=v1", "--untracked-files=all"], ["--short"], ["--porcelain"])):
            return False
    if (receipt.get("terminal") is not True or receipt.get("exit_code") != 0 or
            receipt.get("execution_kind") != "cooperative_process" or
            receipt.get("run") != fixture["run"] or
            receipt.get("checkout") not in {str(path) for path in worktrees}):
        return False
    receipt_command = shlex.join(["python3", str(reader), *[
        receipt[key] for key in ("execution_id", "owner", "run", "checkout")]])
    if not any(json_value(out) == receipt for cwd in roots
               for out in outputs(receipt_command, cwd)):
        return False
    command = shlex.join(["worktree-reservation", "list", "--repository", str(repo), "--json"])
    for output in outputs(command, repo):
        data = json_value(output)
        if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
            continue
        selected = [r for r in data["entries"] if isinstance(r, dict) and (
            r.get("path") == receipt["checkout"] or
            r.get("issue_url") == f"https://github.com/{fixture['repository']}/issues/{fixture['issue']}")]
        if len(selected) != 1:
            continue
        row = selected[0]
        path = Path(receipt["checkout"])
        expected = before["reservation"][path.name]
        owner = row.get("owner")
        stopped_owner = (row.get("state") == "ACTIVE" and isinstance(owner, dict) and
                         owner.get("session") == receipt["owner"] and
                         owner.get("run") == receipt["run"] and
                         owner.get("pid") in (None, receipt.get("pid")))
        released = row.get("state") == "WAITING" and owner is None
        if (row.get("ok") is True and row.get("exit_code") == 0 and
                row.get("path") == receipt["checkout"] and row.get("head") == receipt["head"] and
                row.get("issue_url") == (
                    f"https://github.com/{fixture['repository']}/issues/{fixture['issue']}") and
                row.get("drift") is None and (stopped_owner or released) and
                row.get("unknown_untracked_paths") == [] and all(
                    k in row and k in expected and row[k] == expected[k] for k in
                    ("issue_url", "branch", "state", "owner", "head", "digest", "drift"))):
            # Both states still require the independently observed prior-writer
            # receipt above. Neither transfers ownership or authorizes effects.
            return True
    return False


def t1_github_source_proof(events, session, repo, fixture, github, *, before):
    """Successful same-session native issue/decisions read, not a claim or audit alone."""
    expected = github.get("issues", {}).get(str(fixture["issue"]))
    endpoint = f"repos/{fixture['repository']}/issues/{fixture['issue']}"
    if not isinstance(expected, dict):
        return False
    commands = {shlex.join(["gh", "api", *flags, endpoint]) for flags in ([], ["--paginate"])}
    for event in tool_events(events, session, tool="shell"):
        if (event["index"] >= before or event["exit_code"] != 0 or event["truncated"] is not False or
                event["input"].get("workdir", str(repo)) != str(repo) or
                event["input"].get("command") not in commands):
            continue
        try:
            if json.loads(event["output"]) == expected:
                return True
        except (ValueError, TypeError):
            pass
    return False


def t1_offline_projection(record, events, terminal, fixture):
    """Diagnose retained original observations, never synthesize a future field.

    Caller retains/hashes original files and records this separately. Recompute
    the gates from actual events/prospective snapshots, not recorded booleans.
    Text interpretation still requires independent response/event review.
    """
    session, before, after = record["session_id"], record["before"], record["after"]
    provenance = record["fixture_proposal_facts"]
    repo = Path(before["artifact_comparison"]["repo"])
    worktrees = [Path(row["path"]) for row in before["registry"]["entries"]]
    receipt = record["runtime_receipts"][str(fixture["issue"])]
    reader = Path(shlex.split(fixture["runtime_receipt_command"])[1])
    semantic, boundary = t1_handoff(events, session, fixture, provenance)
    source, discovery, invocation, instructions = t1_native_inspection(
        events, session, repo, record["native_inspection_candidates"],
        record["delivered_skill_catalog"], before=boundary)
    calls = record["github_calls"]
    resume = tool_events(events, session, tool="skill", contains="resume-workflow")
    facts = {
        "terminal": terminal.get("exit_code") == 0 and terminal.get("timed_out") is False and
                    terminal.get("session_ids") == [session] and
                    terminal.get("candidate") == fixture.get("candidate_sha") ==
                    provenance["review"].get("source_candidate") and
                    fixture.get("approved_source_proposal_sha") ==
                    provenance["review"].get("source_approved_proposal") and
                    terminal.get("malformed_lines") == [] and terminal.get("error_events") == [] and
                    {e["sessionID"] for e in events if e.get("sessionID")} == {session},
        "proposal": t1_proposal_proof(
            events, session, repo, provenance, invocation, before=boundary,
            artifact_states=(before.get("artifact_comparison"), after.get("artifact_comparison"))),
        "apply_gate": t1_apply_gate_proof(events, session, repo, provenance, invocation, before=boundary),
        "inventory": t1_inventory_proof(events, session, repo, worktrees, reader, receipt,
                                        fixture, before, after, handoff_index=boundary),
        "snapshots": before == after,
        "github": bool(t1_github_source_proof(
            events, session, repo, fixture, before["github"], before=boundary) and
            calls and any(args[:1] == ["api"] for args in calls) and all(
            not any(a == "--method" or a.startswith("body=") or
                    a in ("edit", "create", "merge", "close", "delete") for a in args)
            for args in calls)),
        "native": bool(source and discovery and invocation and instructions and any(
            d["event_index"] < i["event_index"] for d in discovery for i in invocation)),
        "resume": bool(resume and any(e["index"] < boundary for e in resume)),
        "no_stateful_attempts": not forbidden_attempts(events, session)}
    ownership = t1_ownership_context(before, receipt, fixture)
    value, _ = t1_handoff_value(events, session)
    future = t1_phase_evaluation(events, session, fixture, provenance, ownership, facts=facts)
    return {"kind": "offline_projection", "session_id": session,
            "original_status": record["status"], "original_outcome": record["outcome"],
            "original_proof_complete": record["proof_complete"],
            "last_handoff_index": boundary, "facts": facts,
            "semantic_fields_proven": semantic,
            "read_only_facts_proven": bool(semantic and ownership and all(facts.values())),
            "observed_ownership_context": ownership,
            "future_typed_condition_observed": bool(value and "ownership_condition" in value),
            "future_fixture_evaluation": future,
            "serialization_compliance": t1_serialization(events, session, fixture, provenance),
            "write_authorized": False, "native_pass": False,
            "independent_response_event_review": "required",
            "limit": "No retroactive typed condition, native PASS, failure resolution, T5/T7 "
                     "observation or replacement of the original manifest."}


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
    if any(e["tool"] == "skill" and e["input"].get("id") != "openspec-explore"
           for e in boundaries):
        return False  # T7 prohibits Apply even after reinventory or beside valid Explore.
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
    """Read-only source acceptance: actual reads AND no stateful attempt, at any status."""
    if forbidden_attempts(events, session):
        return False
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
            if (tokens == ["gh", *argv] and output == expected and
                    event["exit_code"] == 0 and event["truncated"] is False):
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


def public_evidence(value, _depth=0):
    """Reject structured secrets/identities BEFORE persistence, not regex-only."""
    if _depth > 32:
        raise RuntimeError("evidence nesting unsupported")
    forbidden = {"accountid", "clientid", "devicecode", "authorizationcode",
                 "accesstoken", "refreshtoken", "idtoken", "apikey", "password",
                 "authorization", "credential", "credentials", "authjson"}
    if isinstance(value, dict):
        if value.get("type") == "credential" and "id" in value:
            raise RuntimeError("private connection mapping cannot enter evidence")
        for key, child in value.items():
            if re.sub(r"[^a-z0-9]", "", key.lower()) in forbidden:
                raise RuntimeError("private structured field cannot enter evidence")
            public_evidence(child, _depth + 1)
    elif isinstance(value, (list, tuple)):
        for child in value:
            public_evidence(child, _depth + 1)
    elif isinstance(value, str) and re.search(
            r"(?i)(Bearer\s+[A-Za-z0-9._-]+|https?://[^\s]*(?:oauth|authorize|callback)"
            r"[^\s]*[?&#](?:code|token|state)=)", value):
        raise RuntimeError("private authentication material cannot enter evidence")
    elif isinstance(value, str):
        # Encoded JSON is still structured input, not an escape hatch through a
        # string field. This does NOT normalize or repair the model's response.
        candidate = value.strip()
        if candidate.startswith(("\"", "{", "[")):
            try:
                decoded = json.loads(candidate)
            except ValueError:
                pass
            else:
                public_evidence(decoded, _depth + 1)
    return value


def native_event_projection(event):
    """Supported V2 event schemas only; opaque provider/error diagnostics omitted.

    Tool input/output and skill body remain exact for downstream native proof.
    Error messages, stderr and provider-native opaque state are NOT proof inputs
    and never enter retained artifacts. Unknown nested fields fail closed.
    """
    def shape(value, allowed, required=()):
        if (not isinstance(value, dict) or not set(required) <= value.keys() or
                not value.keys() <= set(allowed)):
            raise RuntimeError("unsupported native evidence schema")
        return value
    def numeric(value):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise RuntimeError("unsupported native numeric evidence")
    if len(json.dumps(event)) > 1_000_000:
        raise RuntimeError("native evidence exceeds bound")
    shape(event, ("type", "sessionID", "timestamp", "part", "error"), ("type", "sessionID"))
    if not isinstance(event["sessionID"], str):
        raise RuntimeError("unsupported native session identity")
    if "timestamp" in event:
        numeric(event["timestamp"])
    result = copy.deepcopy(event)
    kind = event["type"]
    if kind == "error":
        shape(event, ("type", "sessionID", "timestamp", "error"), ("error",))
        error = shape(event.get("error"), ("type", "message"), ("message",))
        if (not isinstance(error["message"], str) or
                "type" in error and not isinstance(error["type"], str)):
            raise RuntimeError("unsupported native error schema")
        result["error"] = {"code": "native-runtime-error"}
        result.pop("part", None)
        return result
    part = event.get("part")
    common = ("id", "partID", "sessionID", "messageID", "type")
    if not isinstance(part, dict) or any(
            key in part and not isinstance(part[key], str) for key in common):
        raise RuntimeError("unsupported native part identity")
    if kind in ("text", "reasoning"):
        shape(part, (*common, "text", "time", "metadata"), ("text",))
        if not isinstance(part["text"], str):
            raise RuntimeError("unsupported native text evidence")
        result["part"].pop("metadata", None)  # provider-native opaque state
    elif kind in ("step_start", "step_finish"):
        shape(part, (*common, "reason", "snapshot", "cost", "tokens"))
        if any(key in part and part[key] is not None and not isinstance(part[key], str)
               for key in ("reason", "snapshot")):
            raise RuntimeError("unsupported native step evidence")
        if "cost" in part:
            numeric(part["cost"])
        if "tokens" in part:
            tokens = shape(part["tokens"], ("input", "output", "reasoning", "cache", "total"))
            for key, value in tokens.items():
                if key == "cache":
                    for number in shape(value, ("read", "write")).values():
                        numeric(number)
                else:
                    numeric(value)
    elif kind == "tool_use":
        shape(part, (*common, "tool", "state"), ("tool", "state"))
        state = shape(part["state"], ("status", "input", "output", "title", "metadata",
                                     "time", "error"), ("status", "input"))
        if state["status"] not in ("pending", "running", "completed", "error", "failed", "cancelled"):
            raise RuntimeError("unsupported native tool status")
        inputs = {"shell": ("command", "workdir", "timeout", "description"),
                  "skill": ("id", "name"),
                  "read": ("path", "offset", "limit"),
                  "glob": ("pattern", "path", "hidden", "limit"),
                  "grep": ("pattern", "path", "include", "literal", "caseSensitive", "limit"),
                  "question": ("questions",)}
        if part["tool"] not in inputs:
            raise RuntimeError("unsupported native tool evidence; proof blocked")
        shape(state["input"], inputs[part["tool"]])
        if part["tool"] != "question":
            for key, value in state["input"].items():
                if key in ("timeout", "offset", "limit"):
                    numeric(value)
                elif key in ("hidden", "literal", "caseSensitive"):
                    if type(value) is not bool:
                        raise RuntimeError("unsupported native input flag")
                elif not isinstance(value, str):
                    raise RuntimeError("unsupported native input scalar")
        if part["tool"] == "question":
            questions = state["input"].get("questions", [])
            if not isinstance(questions, list) or len(questions) > 16:
                raise RuntimeError("unsupported native question evidence")
            for question in questions:
                shape(question, ("question", "header", "options", "multiple", "custom"))
                if (not isinstance(question.get("options", []), list) or
                        len(question.get("options", [])) > 32 or any(
                            key in question and type(question[key]) is not bool
                            for key in ("multiple", "custom"))):
                    raise RuntimeError("unsupported native question structure")
                for option in question.get("options", []):
                    shape(option, ("label", "description"))
                    if any(not isinstance(v, str) for v in option.values()):
                        raise RuntimeError("unsupported native question option")
                if any(key in question and not isinstance(question[key], str)
                       for key in ("question", "header")):
                    raise RuntimeError("unsupported native question text")
        if "error" in state:
            if not isinstance(state["error"], str):
                raise RuntimeError("unsupported native tool error schema")
            result["part"]["state"]["error"] = "native-tool-error"
        metadata = shape(state.get("metadata", {}), ("metadata", "providerCall", "providerResult",
                                                    "rawInput"))
        projected = {}
        if "metadata" in metadata:
            inner = shape(metadata["metadata"], ("exit", "truncated", "output", "title",
                                                 "description"))
            projected["metadata"] = {k: inner[k] for k in ("exit", "truncated") if k in inner}
            if ("exit" in inner and type(inner["exit"]) is not int or
                    "truncated" in inner and type(inner["truncated"]) is not bool):
                raise RuntimeError("unsupported native tool execution metadata")
        for key in ("providerCall", "providerResult"):
            if key in metadata:
                native = shape(metadata[key], ("executed", "state"), ("executed",))
                if type(native["executed"]) is not bool:
                    raise RuntimeError("unsupported native provider execution flag")
                projected[key] = {"executed": native["executed"]}
        result["part"]["state"]["metadata"] = projected
        for key in ("output", "title"):
            if key in state and not isinstance(state[key], str):
                raise RuntimeError("unsupported native tool text evidence")
    else:
        raise RuntimeError("unsupported native event type")
    if "time" in part:
        for number in shape(part["time"], ("start", "end")).values():
            numeric(number)
    if kind == "tool_use" and "time" in part["state"]:
        for number in shape(part["state"]["time"], ("start", "end")).values():
            numeric(number)
    public_evidence(result)
    return result


def evidence_files(base):
    """Positive filename allowlist; never recursively package an auth profile."""
    names = ["results.json"]
    names += [f"{case}-phase{phase}-{suffix}" for case in ("T1", "T5", "T7")
              for phase in (1, 2) for suffix in ("events.jsonl", "terminal.json", "stderr.log")]
    files = []
    for name in names:
        path = base / name
        if not path.exists():
            continue
        if path.is_symlink() or not path.is_file() or path.resolve().parent != base.resolve():
            raise RuntimeError("unsafe evidence artifact")
        text = path.read_text()
        if path.suffix == ".json":
            public_evidence(json.loads(text))
        elif path.suffix == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    value = json.loads(line)
                    if value.get("type") == "error":
                        if (not set(value) <= {"type", "sessionID", "timestamp", "error"} or
                                value.get("error") != {"code": "native-runtime-error"}):
                            raise RuntimeError("unprojected native error artifact")
                        public_evidence(value)
                    elif native_event_projection(value) != value:
                        raise RuntimeError("unprojected native evidence artifact")
        else:
            if json.loads(text) not in ({"code": "native-stderr-present"},
                                       {"code": "native-stderr-empty"}):
                raise RuntimeError("unprojected native stderr artifact")
        files.append(path)
    return files


def persist(base, results):
    public_evidence(results)
    path = base / "results.json"
    temporary = base / "results.json.new"
    temporary.write_text(json.dumps(results, indent=2) + "\n")
    temporary.replace(path)


def private_environment(base, cli, inherited):
    """Explicit new profile; no ambient config, credentials, headers or endpoint."""
    home, bin_dir = base / "home", base / "bin"
    env = {key: inherited[key] for key in ("LANG", "TERM") if key in inherited}
    entries = disposable_path(home, inherited.get("PATH", os.defpath),
                              inherited["HOME"]).split(os.pathsep)
    env["PATH"] = os.pathsep.join([entries[0], str(bin_dir), *entries[1:]])
    env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"),
               XDG_DATA_HOME=str(home / ".local/share"),
               XDG_CACHE_HOME=str(home / ".cache"),
               XDG_STATE_HOME=str(home / ".local/state"), CODEX_HOME=str(home / ".codex"),
               OPENCODE_DB=str(base / "opencode.db"),
               OPENCODE_PASSWORD=secrets.token_hex(24),
               OPENSPEC_TELEMETRY="0", PYTHONDONTWRITEBYTECODE="1")
    return env


def validate_private_environment(base, env):
    expected = {"HOME": base / "home", "XDG_CONFIG_HOME": base / "home/.config",
                "XDG_DATA_HOME": base / "home/.local/share",
                "XDG_CACHE_HOME": base / "home/.cache",
                "XDG_STATE_HOME": base / "home/.local/state",
                "CODEX_HOME": base / "home/.codex", "OPENCODE_DB": base / "opencode.db"}
    allowed = {*expected, "PATH", "LANG", "TERM", "OPENCODE_PASSWORD",
               "OPENSPEC_TELEMETRY", "PYTHONDONTWRITEBYTECODE"}
    if (not set(env) <= allowed or any(env.get(k) != str(v) for k, v in expected.items()) or
            not env.get("OPENCODE_PASSWORD") or env.get("OPENSPEC_TELEMETRY") != "0" or
            env.get("PYTHONDONTWRITEBYTECODE") != "1"):
        raise RuntimeError("private environment contains unapproved source/auth/config")
    entries = env.get("PATH", "").split(os.pathsep)
    if (entries[:2] != [str(base / "home/.local/bin"), str(base / "bin")] or
            any(not Path(p).is_absolute() or (
                Path(p).is_relative_to(Path.home()) and not Path(p).is_relative_to(base))
                for p in entries)):
        raise RuntimeError("private PATH contains ambient operator paths")


def private_inventory(base):
    """Validate privately, never publish paths/contents of native auth storage."""
    if base != base.resolve() or not base.is_dir():
        raise RuntimeError("private profile path/symlink mismatch")
    for parent in (base, *base.parents):
        if parent.is_symlink() or parent.stat().st_uid not in (0, os.getuid()):
            raise RuntimeError("private profile ancestor ownership mismatch")
    for item in (base, *base.rglob("*")):
        mode = item.lstat()
        if mode.st_uid != os.getuid():
            raise RuntimeError("private profile ownership mismatch")
        if item.is_symlink():
            relative = item.relative_to(base).as_posix()
            package = base / "home/.local/share/my-ai-skills"
            target = os.readlink(item)
            allowed = (relative == "home/.local/share/my-ai-skills/active" and
                       bool(re.fullmatch(r"versions/[a-f0-9]{40}", target)))
            name = item.name
            if re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
                allowed |= (relative == f"home/.config/opencode/skills/{name}" and
                            target == str(package / "active/skills" / name))
                allowed |= (relative == f"home/.local/bin/{name}" and
                            target == str(package / "bin" / name))
            if not allowed:
                raise RuntimeError("private profile unverified symlink")
        elif not (stat.S_ISDIR(mode.st_mode) or stat.S_ISREG(mode.st_mode)):
            raise RuntimeError("private profile special file")
        elif stat.S_IMODE(mode.st_mode) & 0o077:
            raise RuntimeError("private profile permissions must exclude group/other")


def privatize_new_files(directory):
    """Only freshly created known fixtures/install snapshots, NEVER auth state."""
    for item in (directory, *directory.rglob("*")):
        if not item.is_symlink():
            item.chmod(0o700 if item.is_dir() or os.access(item, os.X_OK) else 0o600)


def private_bytes(base, path):
    """Open each component relative to held dirfds; never follow links.

    Only use on named configuration/receipts or a separately verified managed
    instruction target, never auth storage. A path replacement after open cannot
    redirect this read. Same-user interference outside the observation is not
    cryptographically excluded.
    """
    try:
        parts = path.relative_to(base).parts
    except ValueError:
        raise RuntimeError("unsafe private file scope") from None
    if not parts or any(part in (".", "..") for part in parts):
        raise RuntimeError("unsafe private file traversal")
    descriptors = []
    try:
        fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(fd)
        for part in (*base.parts[1:], *parts[:-1]):
            fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            descriptors.append(fd)
            if os.fstat(fd).st_uid not in (0, os.getuid()):
                raise RuntimeError("unsafe private parent ownership")
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        descriptors.append(fd)
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid() or
                before.st_nlink != 1 or before.st_mode & 0o077 or before.st_size > 2_000_000):
            raise RuntimeError("unsafe private regular file")
        with os.fdopen(os.dup(fd), "rb") as stream:
            data = stream.read(2_000_001)
        after = os.fstat(fd)
        fields = ("st_dev", "st_ino", "st_mode", "st_uid", "st_nlink", "st_size",
                  "st_mtime_ns", "st_ctime_ns")
        if (any(getattr(before, k) != getattr(after, k) for k in fields) or
                len(data) != before.st_size):
            raise RuntimeError("private file changed during bounded read")
        return data
    except (OSError, ValueError):
        raise RuntimeError("unsafe private file target") from None
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def private_binding(base, cli, revision):
    private_inventory(base)
    if sha(Path(cli)) != RUNTIME_SHA256:
        raise RuntimeError("unsupported runtime provenance; stop before login")
    # Only explicit configuration/instructions, never DB, auth, cache or logs.
    config = {}
    for directory in (base / "home/.config/opencode", base / "home/.codex"):
        if directory.exists():
            for item in directory.rglob("*"):
                if item.is_file():
                    relative = item.relative_to(directory)
                    allowed = relative.as_posix() in ("AGENTS.md", "opencode.json", "opencode.jsonc")
                    allowed |= (relative.parts[0] == "skills" and item.suffix == ".md" and
                                item.resolve().is_relative_to(
                                    base / "home/.local/share/my-ai-skills"))
                    if directory.name == ".codex" or not allowed:
                        raise RuntimeError("unexpected private configuration artifact")
                    config[str(item.relative_to(base))] = hashlib.sha256(
                        private_bytes(base, item)).hexdigest()
    package = base / "home/.local/share/my-ai-skills"
    active = package / "active"
    if active.is_symlink():
        target = "versions/" + revision
        if os.readlink(active) != target:
            raise RuntimeError("managed snapshot pointer mismatch")
        version = package / target
        manifest = json.loads(private_bytes(base, version / "manifest.json"))
        if manifest.get("revision") != revision:
            raise RuntimeError("managed snapshot revision mismatch")
        links = base / "home/.config/opencode/skills"
        for link in links.iterdir():
            name = link.name
            if (not link.is_symlink() or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) or
                    os.readlink(link) != str(active / "skills" / name)):
                raise RuntimeError("unverified managed instruction link")
            # Construct the permitted source, never resolve the link's target.
            canonical = version / "skills" / name / "SKILL.md"
            config[str(link.relative_to(base))] = hashlib.sha256(
                private_bytes(base, canonical)).hexdigest()
            if os.readlink(active) != target or os.readlink(link) != str(active / "skills" / name):
                raise RuntimeError("managed instruction link changed during read")
    return {"candidate": revision, "approved_proposal": APPROVED_PROPOSAL,
            "runtime_sha256": RUNTIME_SHA256, "runtime_source": RUNTIME_SOURCE,
            "profile": str(base), "config": config}


class OwnedMetadataRuntime:
    """One private stdio server/Location, supported bounded plugin activation.

    v2.4.2 server-process.ts owns lifetime through stdin EOF. api.ts performs no
    plugin wait; plugin-startup.ts polls GET plugin until nonempty for <=5s.
    No shared service, auth attempt, provider request or inference is performed.
    """
    def __init__(self, cli, repo, env):
        self.cli, self.repo, self.env = cli, repo, dict(env)
        self.process = None
        self.url = None
        self.ready = False
        self.closed = False
        self.polls = 0
        self.alias = secrets.token_hex(16)

    def __enter__(self):
        if self.process is not None or self.closed:
            raise RuntimeError("owned metadata runtime cannot be replayed")
        if sha(Path(self.cli)) != RUNTIME_SHA256:
            raise RuntimeError("unsupported metadata runtime provenance")
        try:
            self.process = subprocess.Popen(
                [self.cli, "serve", "--stdio", "--hostname", "127.0.0.1",
                 "--port", "0", "--log-level", "none"],
                cwd=self.repo, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, start_new_session=True)
            data = b""
            deadline = time.monotonic() + 15
            with selectors.DefaultSelector() as watcher:
                watcher.register(self.process.stdout, selectors.EVENT_READ)
                while b"\n" not in data:
                    if self.process.poll() is not None:
                        raise RuntimeError("owned metadata runtime startup exited")
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise RuntimeError("owned metadata runtime startup timeout")
                    if not watcher.select(min(remaining, 0.1)):
                        continue
                    block = os.read(self.process.stdout.fileno(), 4097 - len(data))
                    if not block or len(data) + len(block) > 4096:
                        raise RuntimeError("owned metadata runtime startup truncated/oversized")
                    data += block
            endpoint = json.loads(data.split(b"\n", 1)[0])
            url = urllib.parse.urlsplit(endpoint.get("url", ""))
            if (set(endpoint) != {"url"} or url.scheme != "http" or
                    url.hostname != "127.0.0.1" or not url.port or
                    url.username or url.password or url.path not in ("", "/") or
                    url.query or url.fragment):
                raise RuntimeError("owned metadata runtime endpoint unsupported")
            self.url = endpoint["url"].rstrip("/")
            info = self.request("/api/info")
            if info.get("version") != RUNTIME_VERSION or info.get("pid") != self.process.pid:
                raise RuntimeError("owned metadata runtime identity mismatch")
            # Actual native condition, not a fixed sleep or model-availability retry.
            deadline = time.monotonic() + 5
            while True:
                plugins = self.request("/api/plugin", timeout=max(0.01, deadline - time.monotonic()))
                self.polls += 1
                if not isinstance(plugins, list):
                    raise RuntimeError("owned metadata plugin schema unsupported")
                if plugins:
                    self.ready = True
                    return self
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError("owned metadata plugin readiness timeout")
                time.sleep(min(0.025, remaining))
        except RuntimeError:
            self.close()
            raise
        except Exception:
            self.close()
            raise RuntimeError("owned metadata startup/readiness failed; payload omitted") from None

    def request(self, path, *, timeout=5):
        if (self.closed or not self.process or self.process.poll() is not None or not self.url or
                path not in ("/api/info", "/api/plugin", "/api/integration/openai",
                             "/api/provider/openai", "/api/model")):
            raise RuntimeError("owned metadata request unavailable/not allowlisted")
        query = urllib.parse.urlencode({"location[directory]": str(self.repo)})
        credential = base64.b64encode(("opencode:" + self.env["OPENCODE_PASSWORD"]).encode()).decode()
        request = urllib.request.Request(self.url + path + "?" + query,
                                         headers={"Authorization": "Basic " + credential})
        try:
            # Never inherit the controller's proxy settings or credentials.
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(request, timeout=timeout) as response:
                raw = response.read(1_000_001)
                if len(raw) > 1_000_000:
                    raise RuntimeError("owned metadata response exceeds bound")
                value = json.loads(raw)
        except urllib.error.HTTPError as error:
            code = error.code
            error.close()
            raise RuntimeError(f"native metadata HTTP {code}; payload omitted") from None
        except Exception:
            raise RuntimeError("native metadata transport/schema failure; payload omitted") from None
        if path == "/api/info":
            return value
        if (not isinstance(value, dict) or set(value) != {"location", "data"} or
                value.get("location") != {"directory": str(self.repo)}):
            raise RuntimeError("metadata Location/schema mismatch")
        return value["data"]

    def close(self):
        if self.closed:
            return
        self.closed = True
        if self.process is None:
            return
        if self.process.stdin:
            self.process.stdin.close()  # supported graceful stdio lifetime
        forced = False
        try:
            self.process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            forced = True
            self.process.terminate()  # ONLY this Popen-owned process
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        finally:
            if self.process.stdout:
                self.process.stdout.close()
        if forced or self.process.returncode != 0:
            raise RuntimeError("owned metadata shutdown not graceful; preparation blocked")

    def __exit__(self, *_):
        self.close()

    def receipt(self):
        if (not self.ready or not self.closed or self.process.returncode != 0 or
                sha(Path(self.cli)) != RUNTIME_SHA256):
            raise RuntimeError("owned metadata terminal receipt unavailable")
        return {"execution_alias": self.alias, "pid": self.process.pid,
                "runtime_sha256": RUNTIME_SHA256, "version": RUNTIME_VERSION,
                "location": str(self.repo), "plugin_ready": True,
                "readiness_polls": self.polls, "exit_code": self.process.returncode,
                "shutdown": "owned-stdio-eof", "inference_verified": False}


def native_metadata(cli, repo, env, path, *, runtime=None):
    if runtime is None:
        with OwnedMetadataRuntime(cli, repo, env) as owned:
            return owned.request(path)
    if (runtime.cli != cli or runtime.repo != repo or runtime.env != env or not runtime.ready):
        raise RuntimeError("metadata runtime/profile/Location binding mismatch")
    return runtime.request(path)


def chatgpt_method(integration):
    """Public integration projection, never assume a public post-login methodID."""
    if integration.get("id") != "openai" or not isinstance(integration.get("connections"), list):
        raise RuntimeError("unsupported integration schema; stop before login")
    methods = [m for m in integration.get("methods", [])
               if m.get("type") == "oauth" and m.get("label") == "Sign in with ChatGPT"]
    if (len(methods) != 1 or not isinstance(methods[0].get("id"), str) or
            methods[0]["id"] != "chatgpt-token-sharing"):
        raise RuntimeError("ChatGPT method absent/ambiguous; stop before login")
    return {key: methods[0][key] for key in ("id", "type", "label")}


def prepare_private_pause(base, cli, revision, env, *, expected=None):
    """Metadata-only pause. A checksum validates continuity, NOT authentication."""
    validate_private_environment(base, env)
    binding = private_binding(base, cli, revision)
    receipt_path = base / "private-preparation.json"
    if expected:
        raw_receipt = private_bytes(base, receipt_path)
        if hashlib.sha256(raw_receipt).hexdigest() != expected:
            raise RuntimeError("private preparation receipt missing/tampered")
        receipt = json.loads(raw_receipt)
        if receipt["binding"] != binding or receipt["state"] != "metadata_only":
            raise RuntimeError("private preparation HEAD/runtime/config/profile mismatch")
    else:
        if receipt_path.exists():
            raise RuntimeError("private preparation already exists")
        receipt = {"binding": binding, "nonce": secrets.token_hex(24), "state": "metadata_only"}
    with OwnedMetadataRuntime(cli, ROOT, env) as runtime:
        integration = native_metadata(cli, ROOT, env, "/api/integration/openai", runtime=runtime)
        method = chatgpt_method(integration)
        if integration["connections"]:
            raise RuntimeError("offline pause requires zero connections; supervised controller required")
        provider = native_metadata(cli, ROOT, env, "/api/provider/openai", runtime=runtime)
        catalog = native_metadata(cli, ROOT, env, "/api/model", runtime=runtime)
    if expected and receipt["method"] != method:
        raise RuntimeError("private preparation method mismatch")
    receipt["method"] = method
    # Check the supported non-secret Provider/Model schema without selecting
    # a model or inspecting any actual account. Missing/changed API blocks here.
    if (provider.get("id") != "openai" or provider.get("integrationID") != "openai" or
            provider.get("activation") not in ("auto", "enabled", "disabled") or
            not isinstance(catalog, list) or any(
                not isinstance(m, dict) or not {"id", "providerID", "type", "cost",
                                                "capabilities", "enabled"} <= m.keys()
                for m in catalog)):
        raise RuntimeError("native provider/catalog schema unsupported; stop before login")
    if not expected:
        receipt["metadata_runtime"] = runtime.receipt()
        with os.fdopen(os.open(receipt_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                               os.O_NOFOLLOW, 0o600), "w") as stream:
            stream.write(json.dumps(receipt, sort_keys=True))
    return {"state": "metadata_only", "inference_verified": False,
            "profile_alias": hashlib.sha256(receipt["nonce"].encode()).hexdigest(),
            "candidate": revision, "approved_proposal": APPROVED_PROPOSAL,
            "runtime_sha256": RUNTIME_SHA256, "runtime_source": RUNTIME_SOURCE,
            "metadata_runtime": runtime.receipt(),
            "receipt_sha256": hashlib.sha256(private_bytes(base, receipt_path)).hexdigest(),
            "method": method,
            "auth_availability": "pending_manual", "route_proof": "pending",
            "economic_eligibility": "pending", "native_proof": "NOT_RUN",
            "login_requested": False}


def model_preflight(cli, repo, env, record, override=None, *, subscription=None):
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
        value = {key: model.get(key) for key in
                 ("id", "modelID", "providerID", "type", "enabled", "status")}
        caps = model.get("capabilities", {})
        value["capabilities"] = {k: caps.get(k) for k in ("tools", "input", "output")}
        if (type(value["capabilities"]["tools"]) is not bool or any(
                not isinstance(caps.get(k), list) or
                any(not isinstance(item, str) for item in caps[k]) for k in ("input", "output"))):
            raise RuntimeError("unsupported model capability schema")
        prices = []
        for cost in model.get("cost", []):
            cache = cost.get("cache", {})
            numbers = (cost.get("input"), cost.get("output"), cache.get("read"), cache.get("write"))
            if any(number is not None and (
                    type(number) not in (int, float) or not math.isfinite(number)) for number in numbers):
                raise RuntimeError("unsupported model price schema")
            price = {"input": numbers[0], "output": numbers[1],
                     "cache": {"read": numbers[2], "write": numbers[3]}}
            if "tier" in cost:
                tier = cost["tier"]
                if (not isinstance(tier, dict) or set(tier) != {"type", "size"} or
                        tier["type"] != "context" or type(tier["size"]) is not int):
                    raise RuntimeError("unsupported model price tier")
                price["tier"] = dict(tier)
            prices.append(price)
        value["cost"] = prices
        return value

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
    zero = bool(costs) and all(
        all(type(value) in (int, float) and value == 0 for value in
            (cost.get("input"), cost.get("output"), cost.get("cache", {}).get("read"),
             cost.get("cache", {}).get("write"))) for cost in costs)
    if subscription is not None:
        if not isinstance(subscription, SupervisedSubscription):
            raise RuntimeError("subscription requires live trusted supervisor, not JSON")
        subscription.recheck(cli, repo, env, model)
        # Empty means display unknown only in this separately authorized route.
        if costs != [] and not zero:
            raise RuntimeError("subscription metadata conflicts with API pricing; no fallback")
        record.update(economic_branch="subscription-quota",
                      price_display="unknown" if costs == [] else "numerical-zero",
                      route_proof=subscription.public_receipt(),
                      quota_available="UNKNOWN", final_settlement="UNKNOWN")
    elif not zero:
        raise RuntimeError("selected model pricing unknown or paid; no fallback")
    else:
        record["economic_branch"] = "credential-free-all-zero"
    record["status"] = "metadata_eligible"
    return requested


class SupervisedSubscription:
    """Trusted controller only, outside model tools; never load a proof from JSON.

    The exact child is observed by OS wait here, not by an external callback.
    Keep this object alive through all phases. Restart/transfer without the
    authentic controller is blocked, not recovered from a checkbox/checksum.
    0700/flock are cooperative controls, not hostile-same-user isolation.
    """
    def __init__(self, base, cli, env, revision, receipt_sha256):
        self.base, self.cli, self.revision = base, cli, revision
        self.env = {k: v for k, v in env.items() if k != "OPENCODE_PASSWORD"}
        private_inventory(base)
        validate_private_environment(base, env)
        self.lock = os.fdopen(os.open(base / "supervisor.lock",
                                     os.O_CREAT | os.O_APPEND | os.O_WRONLY | os.O_NOFOLLOW,
                                     0o600), "a")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.preparation = prepare_private_pause(
                base, cli, revision, env, expected=receipt_sha256)
        except Exception:
            self.lock.close()
            raise
        self.binding = private_binding(base, cli, revision)
        self.method = self.preparation["method"]
        self._preparation_sha256 = receipt_sha256
        self._profile_alias = self.preparation["profile_alias"]
        self.connection = None  # private runtime credential ID, never evidence
        self.process = None
        self._auth_child = None
        self._observed_process = None
        self._completion = None
        self._attempted = False
        self._controller = self._process_identity(os.getpid())
        self._execution = secrets.token_hex(24)  # local harness ID, NOT an agent session
        self._lease = self._lease_identity()
        self._identity = self
        self._identity_binding = self._local_identity()
        self._terminal = None
        self._probe = None
        self._probe_binding = None
        self.quota_authorized = self.entitlement_confirmed = False

    def close(self):
        self._identity = None
        self._completion = None
        self.connection = None
        self._stop_child()
        self.lock.close()

    def _local_identity(self):
        return (self._controller, self._execution, self._lease, self._profile_alias,
                self.revision, str(self.base), self.cli, APPROVED_PROPOSAL, CONTROLLER_SHA256,
                tuple(sorted(self.method.items())))

    @staticmethod
    def _process_identity(pid):
        # Linux /proc process-start ticks distinguish PID reuse; no auth storage.
        try:
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            return (pid, int(fields[19]), os.getsid(pid), os.getpgid(pid))
        except (OSError, ValueError, IndexError):
            raise RuntimeError("local controller/process identity unavailable") from None

    def _lease_identity(self):
        if self.lock.closed:
            raise RuntimeError("local controller lease closed")
        fd = os.fstat(self.lock.fileno())
        path = (self.base / "supervisor.lock").lstat()
        if (not stat.S_ISREG(path.st_mode) or path.st_nlink != 1 or
                path.st_uid != os.getuid() or stat.S_IMODE(path.st_mode) != 0o600 or
                (fd.st_dev, fd.st_ino) != (path.st_dev, path.st_ino)):
            raise RuntimeError("local controller lease replaced")
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd.st_dev, fd.st_ino

    def _code_identity(self):
        path = "tests/smoke_resume_candidate_opencode.py"
        if (sha(Path(__file__)) != CONTROLLER_SHA256 or
                git(ROOT, os.environ, "rev-parse", f"{self.revision}:{path}") !=
                git(ROOT, os.environ, "hash-object", path)):
            raise RuntimeError("local controller source differs from loaded clean candidate")
        git(ROOT, os.environ, "merge-base", "--is-ancestor", APPROVED_PROPOSAL, self.revision)

    @staticmethod
    def _terminal_identity():
        try:
            identities = []
            for fd in (0, 1, 2):
                if (not os.isatty(fd) or not os.get_inheritable(fd) or
                        os.tcgetpgrp(fd) != os.getpgrp()):
                    raise RuntimeError("direct inherited foreground terminal required")
                info = os.fstat(fd)
                identities.append((info.st_dev, info.st_ino, info.st_rdev))
            if len(set(identities)) != 1:
                raise RuntimeError("stdin/stdout/stderr must share the same terminal")
            return tuple(identities), os.getpgrp()
        except OSError:
            raise RuntimeError("direct inherited foreground terminal unavailable") from None

    def _preflight_terminal(self, env):
        if type(self) is not SupervisedSubscription or self._attempted:
            raise RuntimeError("local controller absent/injected or attempt already consumed")
        self._continuity(self.cli, env)
        terminal = self._terminal_identity()
        if self._terminal is not None and terminal != self._terminal:
            raise RuntimeError("local controller terminal changed")
        self._terminal = terminal
        if self._probe is None:
            # Fixed harmless child, no provider command/output. Never an auth receipt.
            self._probe = subprocess.Popen(
                [sys.executable, "-I", "-S", "-c", "pass"], cwd=ROOT, env=env,
                shell=False, stdin=None, stdout=None, stderr=None, start_new_session=False)
            try:
                identity = self._process_identity(self._probe.pid)
                code = self._probe.wait(timeout=5)
                if code != 0:
                    raise RuntimeError("local OS wait capability probe failed")
                self._probe_binding = (self._probe, identity, self._controller,
                                       self._execution, self._lease, self._terminal)
            finally:
                self._stop_child(self._probe)
        if (type(self._probe_binding) is not tuple or
                self._probe_binding[0] is not self._probe or self._probe.poll() != 0 or
                self._probe_binding[2:] != (self._controller, self._execution,
                                            self._lease, self._terminal)):
            raise RuntimeError("local OS wait capability unavailable/unbound")
        self._continuity(self.cli, env)

    def _stop_child(self, process=None):
        process = self._auth_child if process is None else process
        # Never signal a process group: auth shares the person's foreground group.
        if process is not None and process.poll() is None:
            process.terminate()  # ONLY the Popen object created by this controller
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

    def manual_login(self, env, *, quota_authorized, entitlement_confirmed,
                     terminal_privacy_confirmed):
        # ONLY the person's own terminal after independent review; no callback,
        # stream capture, auth export, token/URL parsing, or auth database access.
        if (quota_authorized is not True or entitlement_confirmed is not True or
                terminal_privacy_confirmed is not True):
            raise RuntimeError("manual quota/entitlement/terminal privacy confirmation required")
        self._preflight_terminal(env)
        before = native_metadata(self.cli, ROOT, env, "/api/integration/openai")
        if before["connections"] or chatgpt_method(before) != self.method:
            raise RuntimeError("fresh method/inventory changed; stop before login")
        command = [self.cli, "auth", "login", "openai", "--standalone",
                   "--log-level", "none", "--method", self.method["id"]]
        self._preflight_terminal(env)  # recheck FD/lease/HEAD after metadata, before spawn
        self._attempted = True  # failed/cancelled attempts cannot retry on this object
        previous = {}
        def interrupted(signum, frame):
            raise InterruptedError("local authentication interrupted")
        try:
            for signum in (signal.SIGTERM, signal.SIGHUP):
                previous[signum] = signal.signal(signum, interrupted)
            self.process = subprocess.Popen(
                command, cwd=ROOT, env=env, shell=False,
                stdin=None, stdout=None, stderr=None, start_new_session=False)
            self._auth_child = self.process
            identity = self._process_identity(self.process.pid)
            code = self.process.wait(timeout=300)
            if code != 0 or self.process is self._probe:
                raise RuntimeError("manual authentication incomplete/cancelled")
            self._continuity(self.cli, env)
            if self._terminal_identity() != self._terminal:
                raise RuntimeError("local terminal continuity lost")
        except BaseException:
            self._completion = None
            self._stop_child()
            raise
        finally:
            for signum, handler in previous.items():
                signal.signal(signum, handler)
        after = native_metadata(self.cli, ROOT, env, "/api/integration/openai")
        connections = after.get("connections", [])
        if (chatgpt_method(after) != self.method or len(connections) != 1 or
                connections[0].get("type") != "credential" or
                connections[0].get("method") != "oauth" or connections[0].get("status") or
                not isinstance(connections[0].get("id"), str)):
            raise RuntimeError("manual authentication route/inventory inconclusive")
        self.connection = connections[0]["id"]
        self._observed_process = self.process
        self._completion = (identity, code, self._execution, self._controller,
                            copy.deepcopy(self.binding), copy.deepcopy(self.method), self._lease)
        self.quota_authorized = quota_authorized
        self.entitlement_confirmed = entitlement_confirmed

    def _continuity(self, cli, env):
        dynamic = {"OPENCODE_PASSWORD", "RESUME_GH_ROOT", "RESUME_RUNTIME_ROOT",
                   "OPENCODE_CONFIG_CONTENT"}
        if (self._identity is not self or self._local_identity() != self._identity_binding or
                self._controller != self._process_identity(os.getpid()) or
                self._lease_identity() != self._lease or cli != self.cli or
                self.preparation["profile_alias"] != self._profile_alias or
                hashlib.sha256(private_bytes(
                    self.base, self.base / "private-preparation.json")).hexdigest() !=
                self._preparation_sha256 or
                {k: v for k, v in env.items() if k not in dynamic} != self.env or
                private_binding(self.base, cli, self.revision) != self.binding or
                git(ROOT, os.environ, "rev-parse", "HEAD") != self.revision or
                git(ROOT, os.environ, "status", "--porcelain")):
            raise RuntimeError("supervised profile/runtime/HEAD/config/environment continuity lost")
        self._code_identity()

    def _require_completion(self):
        if (self._identity is not self or self._controller != self._process_identity(os.getpid()) or
                self._lease_identity() != self._lease or
                type(self._completion) is not tuple or not self._attempted or
                self._observed_process is not self.process or self.process is not self._auth_child or
                self.process is self._probe or
                self.process.poll() != 0 or self._completion[0][0] != self.process.pid or
                self._completion[1:] != (0, self._execution, self._controller,
                                        self.binding, self.method, self._lease)):
            raise RuntimeError("live local-controller OS completion unavailable")

    def recheck(self, cli, repo, env, model):
        self._continuity(cli, env)
        self._require_completion()
        if (not self.connection or self.quota_authorized is not True or
                self.entitlement_confirmed is not True):
            raise RuntimeError("subscription method/completion/consent proof pending")
        with OwnedMetadataRuntime(cli, repo, env) as runtime:
            integration = native_metadata(cli, repo, env, "/api/integration/openai", runtime=runtime)
            provider = native_metadata(cli, repo, env, "/api/provider/openai", runtime=runtime)
            catalog = native_metadata(cli, repo, env, "/api/model", runtime=runtime)
        connections = integration.get("connections", [])
        if (chatgpt_method(integration) != self.method or len(connections) != 1 or
                connections[0].get("id") != self.connection or
                connections[0].get("method") != "oauth" or
                connections[0].get("type") != "credential" or connections[0].get("status")):
            raise RuntimeError("subscription connection/method mismatch")
        if (provider.get("id") != "openai" or provider.get("integrationID") != "openai" or
                provider.get("activation") not in ("auto", "enabled") or
                model.get("providerID") != "openai" or
                len([m for m in catalog if m == model]) != 1):
            raise RuntimeError("subscription provider/catalog mismatch")

    def public_receipt(self):
        self._continuity(self.cli, self.env)
        self._require_completion()
        if (not self.connection or self.quota_authorized is not True or
                self.entitlement_confirmed is not True):
            raise RuntimeError("subscription completion not observed")
        return {key: self.preparation[key] for key in
                ("profile_alias", "candidate", "approved_proposal", "runtime_sha256",
                 "runtime_source", "method", "receipt_sha256")} | {
                    "connection_alias": "sole-new-oauth", "before_count": 0, "after_count": 1,
                    "completion": {
                        "observer_kind": "local-controller", "completion_source": "os-wait",
                        "execution_id": self._execution,
                        "controller_pid": self._controller[0],
                        "controller_start": self._controller[1],
                        "controller_os_session": self._controller[2],
                        "controller_process_group": self._controller[3],
                        "controller_sha256": CONTROLLER_SHA256,
                        "pid": self.process.pid, "process_start": self._completion[0][1],
                        "exit_code": self._completion[1]},
                    "quota_authorized": True, "entitlement_confirmed": True}


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
        "event_projection": "supported-native-proof-fields-v1",
        "stderr_policy": "diagnostic-code-only",
        "candidate": git(ROOT, os.environ, "rev-parse", "HEAD"),
        "finished_at": datetime.now(timezone.utc).isoformat()}
    (base / f"{case}-terminal.json").write_text(json.dumps(terminal))
    stdout, stderr = redact(stdout, env), redact(stderr, env)
    transcript = base / f"{case}-events.jsonl"
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
            events.append(native_event_projection(event))
        except ValueError:
            malformed.append(number)
    # Only parsed native events, with a positive outer schema; malformed/raw
    # streams are never copied into evidence. Denied tool attempts stay visible.
    for event in events:
        if not set(event) <= {"type", "sessionID", "timestamp", "part", "error"}:
            raise RuntimeError("unexpected native event fields; publication blocked")
        public_evidence(event)
    transcript.write_text("".join(json.dumps(event) + "\n" for event in events))
    # Never publish untrusted stderr, even if it looks like innocent text.
    (base / f"{case}-stderr.log").write_text(json.dumps({
        "code": "native-stderr-present" if stderr else "native-stderr-empty"}))
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


def main(*, prepare_only=False, private_base=None, receipt_sha256=None, subscription=None):
    os.umask(0o077)
    cli = shutil.which("opencode")
    openspec = shutil.which("openspec")
    if not cli or not openspec:
        raise RuntimeError("OpenCode V2 and OpenSpec are required")
    if sha(Path(cli)) != RUNTIME_SHA256:
        raise RuntimeError("unsupported runtime provenance; no login or inference")
    revision = run(["git", "rev-parse", "HEAD"], cwd=ROOT, env=os.environ)
    if run(["git", "status", "--porcelain"], cwd=ROOT, env=os.environ):
        raise RuntimeError("Commit the candidate before installing its exact revision")
    selected_contract = contract_source(ROOT, revision)
    git(ROOT, os.environ, "merge-base", "--is-ancestor", APPROVED_PROPOSAL, revision)
    approved_contract = contract_source(ROOT, APPROVED_PROPOSAL)
    output = os.environ.get("RESUME_SMOKE_OUTPUT")
    if subscription is not None:
        if not isinstance(subscription, SupervisedSubscription):
            raise RuntimeError("live supervised subscription required")
        private_base = subscription.base
        receipt_sha256 = subscription.preparation["receipt_sha256"]
    base = Path(private_base) if private_base else (
        Path(output) if output else Path(tempfile.mkdtemp(
            prefix="resume-candidate-", dir="/tmp/opencode")))
    if private_base:
        if not receipt_sha256:
            raise RuntimeError("resume requires independently retained preparation checksum")
        private_inventory(base)
        receipt = base / "private-preparation.json"
        raw_receipt = private_bytes(base, receipt)
        if hashlib.sha256(raw_receipt).hexdigest() != receipt_sha256:
            raise RuntimeError("resume preparation missing/tampered")
        if json.loads(raw_receipt)["binding"] != private_binding(base, cli, revision):
            raise RuntimeError("resume profile/runtime/HEAD/config mismatch")
    elif output:
        base.mkdir(mode=0o700, exist_ok=False)
    home = base / "home"
    if not private_base:
        home.mkdir(mode=0o700)
    bin_dir = base / "bin"
    opencode_shim = bin_dir / "opencode"
    if not private_base:
        opencode_shim = disposable_opencode_shim(bin_dir, cli)
    # The installer checks gh on PATH. Expose the read-only fixture before that
    # preflight, never the operator's HOME or real authenticated GitHub CLI.
    shim = bin_dir / "gh"
    if not private_base:
        shutil.copy2(ROOT / "tests/fixtures/resume_gh.py", shim)
        shim.chmod(0o700)
    env = private_environment(base, cli, os.environ)
    assert shutil.which("opencode", path=env["PATH"]) == str(opencode_shim)
    assert run(["opencode", "--version"], cwd=ROOT, env=env) == run(
        [cli, "--version"], cwd=ROOT, env=env)
    assert run(["opencode", "--help"], cwd=ROOT, env=env) == run(
        [cli, "--help"], cwd=ROOT, env=env)
    assert run([openspec, "--version"], cwd=ROOT, env=env).startswith("2.")
    results = {"started_at": datetime.now(timezone.utc).isoformat(),
               "candidate": revision, "approved_proposal": APPROVED_PROPOSAL,
               "contract": selected_contract, "approved_contract": approved_contract, "model": None,
               "opencode": run([cli, "--version"], cwd=ROOT, env=env),
               "openspec": run([openspec, "--version"], cwd=ROOT, env=env),
               "scenarios": {}}
    # No model if the pinned canonical Verify or its supported CLI is unavailable.
    t1_inspection_sources(ROOT, case="T5", generator_version=results["openspec"])
    # The public installer has no source override. Inject the local Git transport
    # only in this disposable test process; no global install is performed.
    loader = ("import importlib.machinery,sys; "
              "m=importlib.machinery.SourceFileLoader('installer',sys.argv[1]).load_module(); "
              "source=sys.argv[2]; sys.argv=[sys.argv[1],*sys.argv[3:]]; "
              "original=m.install; m.install=lambda args: original(args,source=source); "
              "sys.exit(m.main())")
    if not private_base:
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

    if not private_base:
        privatize_new_files(base)
    if prepare_only or (private_base and subscription is None):
        # This command NEVER logs in, selects a model, or starts a model phase.
        # Serializes only metadata, not profile, database or authentication I/O.
        with os.fdopen(os.open(base / "supervisor.lock",
                               os.O_CREAT | os.O_APPEND | os.O_WRONLY | os.O_NOFOLLOW,
                               0o600), "a") as lease:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                results["preparation"] = prepare_private_pause(
                    base, cli, revision, env, expected=receipt_sha256)
            except Exception as error:
                results.update(status="blocked", inference_verified=False,
                               preparation={"state": "blocked", "inference_verified": False,
                                            "login_requested": False, "native_proof": "NOT_RUN",
                                            "auth_availability": "technical_blocked",
                                            "route_proof": "pending", "economic_eligibility": "blocked",
                                            "error": str(error)})
                persist(base, results)
                raise
        results.update(status="metadata_only", inference_verified=False)
        persist(base, results)
        print(json.dumps(results["preparation"], sort_keys=True))
        return

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
        inspection_sources = t1_inspection_sources(repo, case=case)
        native_names = (("openspec-explore",) if case == "T7" else
                        ("openspec-explore", "openspec-apply-change") +
                        (("openspec-verify-change",) if case == "T5" else ()))
        assert len(inspection_sources) == len(native_names)
        for name in native_names:
            native = repo / ".agents/skills" / name / "SKILL.md"
            if name != "openspec-verify-change":
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
            fixture["fingerprint_scopes"] = {
                "candidate_source": selected_contract,
                "transformed_fixture": {
                    "proposal_sha": proposal_sha, "files": provenance["review"]["files"],
                    "transformation": "Normalize active/archive source to the active fixture path; "
                                      "reset completed task checkboxes BEFORE fixture proposal/review.",
                    "purpose": "Model an interruption at the reviewed fixture proposal.",
                    "review_scope": "controlled_fixture_seed",
                    "limit": "Proves this fixture state only, NOT independent approval of the real candidate.",
                },
                "comparison": "Compare fixture review/current artifacts to transformed_fixture, "
                              "not to candidate_source; their tasks hashes intentionally differ.",
            }
            fixture["read_only_boundary"] = (
                "Published list commands inspect ownership only. verify mutates verified_for/"
                "last_verified_at and is NOT read-only, even with --json or a session ID. "
                "Do not invoke verify/reserve/checkpoint/handoff/release/takeover in this observation. "
                "Status/reconcile inspection in the real workflow does not authorize unpublished "
                "commands here; reconcile --accept-external changes state. No ownership transition "
                "or writer dispatch is authorized by a stopped-writer receipt.")
            fixture["handoff_scope"] = (
                "Controlled fixture recovery of the last verified pre-Apply gate only. "
                "Not production approval of candidate/source IDs, and not post-Apply tests/CI. "
                "Native Git comparison and fixture review are integrity evidence; there is no "
                "extra model-executed SHA256 command requirement. Report scope/method/future "
                "limits in limitations, not as current blockers unless they actually prevent "
                "this recovery. Missing current inventory/receipt or conflicting owner remains "
                "a blocker. No output label grants ownership or authorizes effects.")
            fixture["proposal_sources"] = {
                key: provenance[key] for key in
                ("proposal_sha", "review_sha", "review_path", "validation_command")}
            fixture["proposal_sources"]["commands"] = [
                p["command"] for p in provenance["probes"]]
            fixture["proposal_sources"]["inspection_note"] = (
                "Artifact body reads are optional inspection locators. Native commit/"
                "ancestry/immutable-review/full-change comparison and strict/Apply gates "
                "remain mandatory; no body-read command quota.")
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
        locator_permissions = read_only_permissions(
            repo, worktrees, reader, receipts, active, prechoice=case == "T7",
            provenance=provenance, case=case)
        locators = read_only_locators(
            repo, worktrees, reader, receipts, locator_permissions, case=case, fixture=fixture)
        fixture.update(locators)
        fixture["writer_execution_ids"] = {str(issue): receipts[issue]["execution_id"]
                                           for issue, _ in issue_runs}
        # The evidence file is committed before model invocation, while runtime
        # receipts live outside every checkout and are independently observed.
        evidence.write_text(json.dumps(fixture, indent=2) + "\n")
        git(repo, env, "add", "-A")
        git(repo, env, "-c", "user.name=Smoke", "-c",
            "user.email=smoke@example.org", "commit", "-qm", "runtime reader locator")
        before = snapshot(repo, worktrees, gh_root, reservation, case_env, openspec,
                          provenance=provenance)
        calls_before = (gh_root / "calls.jsonl").read_text().splitlines()
        reads_before = (gh_root / "reads.jsonl").read_text().splitlines()
        inspection_sources = [s for s in t1_inspection_sources(repo, case=case)
                              if Path(s["path"]).parent.name in native_names]
        assert len(inspection_sources) == len(native_names)
        native_provenance = None  # Selected source is an observation, not a factory placeholder.
        phases = []
        previous_events = None
        session = None
        prompts = [prompt]
        phase_locators = [locators]
        if case == "T7":
            chosen_locators = read_only_locators(
                repo, worktrees, reader, receipts,
                read_only_permissions(repo, worktrees, reader, receipts, active),
                case=case, selected_issue=21)
            phase_locators.append(chosen_locators)
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
                "anterior executando o comando completo deste locator, verbatim, no "
                "cwd publicado; os argumentos são do writer escolhido, não da sessão "
                "do modelo/observer. A variável de ambiente da fixture já está definida. "
                "Locator publicado somente após esta escolha explícita: "
                + json.dumps(chosen_locators) + ". Se qualquer "
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
                                                provenance=provenance, case=case)
            guard = disposable_shell_guard(
                runtime_root / f"shell-guard-phase{phase}", repo, worktrees, permissions, case_env,
                repo_only_commands=[p["command"] for p in provenance["probes"]]
                if provenance else [])
            case_env["OPENCODE_CONFIG_CONTENT"] = json.dumps({
                "$schema": "https://opencode.ai/config.json", "permissions": permissions,
                "plugins": [guard["plugin"]]})
            # Only newly created disposable fixture files, not HOME/DB/auth.
            for directory in (repo, runtime_root, gh_root, *worktrees):
                privatize_new_files(directory)
            record = {"phase": phase, "prompt": message, "before": before,
                      "published_read_only_locators": phase_locators[phase - 1],
                      "native": None, "runtime_receipts": receipts,
                      "shell_guard": guard,
                      "fixture_proposal_facts": provenance,
                      "permissions": permissions, "previous_session_id": session,
                      "model_preflight": {}}
            record["native_inspection_candidates"] = inspection_sources

            def launch():
                if case == "T1" and not before["artifact_comparison"]["verified"]:
                    raise RuntimeError("artifact comparison prerequisites not verified; no inference")
                shell_guard_preflight(cli, repo, case_env, guard)
                persist(base, results)
                model = model_preflight(cli, repo, case_env, record["model_preflight"],
                                        os.environ.get("RESUME_SMOKE_MODEL"),
                                        subscription=subscription)
                results["model"] = model
                # Persist selected capabilities/source/pricing BEFORE inference.
                record["effective_inputs"] = effective_input_binding(
                    ROOT, revision, selected_contract, active, repo, gh_root, runtime_root,
                    home, case_env, phase=phase, prompt=message, permissions=permissions,
                    guard=guard, model=record["model_preflight"], session=session,
                    approved_contract=approved_contract,
                    native_candidates=inspection_sources,
                    runtime_paths={"opencode": cli, "openspec": openspec,
                                   "git": shutil.which("git", path=case_env["PATH"])})
                persist(base, results)
                return execute_model(cli, repo, case_env, base, f"{case}-phase{phase}",
                                     message, session, model=model)

            events, response, session, transcript = prepared_phase(
                base, results, case, record, launch,
                lambda: snapshot(repo, worktrees, gh_root, reservation, case_env, openspec,
                                 provenance=provenance))
            after = record["after"]
            calls_after = (gh_root / "calls.jsonl").read_text().splitlines()
            reads_after = (gh_root / "reads.jsonl").read_text().splitlines()
            new_reads = [json.loads(line) for line in reads_after[len(reads_before):]]
            new_calls = [json.loads(line) for line in calls_after[len(calls_before):]]
            calls_safe = all(not any(a == "--method" or a.startswith("body=") or
                                     a in ("edit", "create", "merge", "close", "delete")
                                     for a in args) for args in new_calls)
            try:
                record["delivered_skill_catalog"] = delivered_skill_catalog(
                    Path(case_env["OPENCODE_DB"]), repo, session, turn_events=events)
            except (RuntimeError, sqlite3.Error, ValueError, TypeError) as error:
                record["delivered_skill_catalog"] = None
                record["catalog_capture_error"] = str(error)
            handoff_index = max((i for i, e in enumerate(events) if e.get("type") == "text" and
                                 e.get("sessionID") == session), default=0)
            if case == "T1":
                outcome, handoff_index = t1_handoff(events, session, fixture, provenance)
                native_provenance, native_discovery, native_invocation, native_instructions = (
                    t1_native_inspection(events, session, repo, inspection_sources,
                                         record["delivered_skill_catalog"], before=handoff_index))
            elif case == "T7" and phase == 1:
                native = Path(inspection_sources[0]["path"])
                native_discovery, native_invocation, native_instructions = (
                    native_calls(events, session, native, inspection_sources[0]["sha256"]))
                native_discovery += catalog_discovery(
                    record["delivered_skill_catalog"], events, session, repo, native)
            else:
                native_provenance, native_discovery, native_invocation, native_instructions = (
                    t1_native_inspection(
                        events, session, repo, inspection_sources, record["delivered_skill_catalog"],
                        before=handoff_index, allowed_names=native_names, case=case,
                        validation={"output": fixture["strict_validation"], "context": before["openspec"]},
                        prior_catalog=phases[-1]["delivered_skill_catalog"] if previous_events else None,
                        prior_events=previous_events))
            resume_invocation = tool_events(events, session, tool="skill",
                                            contains="resume-workflow") + [
                e for e in tool_events(events, session, tool="read",
                                       contains=str(skill)) if "resume-workflow" in e["output"]]
            receipt_reads = [e for e in tool_events(events, session, contains=str(reader))
                             if '"terminal": true' in e["output"] or
                                '"terminal":true' in e["output"]]
            if case == "T5":
                expected = ("12", fixture["pr_head"], "manual", "13")
            elif phase == 1:
                expected = ("21", "22", "wf-disposable-a", "wf-disposable-b", "?")
            else:
                expected = ("21", "wf-disposable-a")
            if case != "T1":
                outcome = (t7_visible_question(response) if case == "T7" and phase == 1
                           else all(term.lower() in response.lower() for term in expected))
            proposal_proved = (t1_proposal_proof(events, session, repo, provenance,
                                                native_invocation, before=handoff_index,
                                                artifact_states=(before.get("artifact_comparison"),
                                                                 after.get("artifact_comparison")))
                               if case == "T1" else None)
            record.update({"phase": phase, "prompt": message, "session_id": session,
                      "response": response, "events": transcript, "before": before,
                      "handoff_index": handoff_index,
                      "after": after, "unchanged": before == after,
                      "github_calls": new_calls, "github_read_only": calls_safe,
                      "native": native_provenance, "native_discovery": native_discovery,
                      "native_invocation": native_invocation,
                      "native_instructions": native_instructions,
                      "resume_invocation": resume_invocation, "runtime_receipts": receipts,
                       "runtime_reads": receipt_reads, "outcome": outcome,
                       "github_reads": new_reads, "status": "observed"})
            record["model_proposal_proved"] = proposal_proved
            apply_gate_proved = (t1_apply_gate_proof(
                events, session, repo, provenance, native_invocation, before=handoff_index)
                                if case == "T1" else None)
            record["model_apply_gate_proved"] = apply_gate_proved
            phases.append(record)
            persist(base, results)
            required = (before == after and calls_safe and new_calls and outcome and
                        bool(record["delivered_skill_catalog"]))
            required &= any(args[:1] == ["api"] for args in new_calls)
            if case == "T1":
                record["forbidden_attempts"] = forbidden_attempts(events, session)
                record["forbidden_attempts_scope"] = "Stateful/tool-action attempts, not all read boundaries."
                record["read_scope_attempts"] = read_scope_attempts(
                    events, session, repo, permissions, fixture["repository"])
                record["model_inventory_proved"] = t1_inventory_proof(
                    events, session, repo, worktrees, reader, receipts[61],
                    fixture, before, after, handoff_index=handoff_index)
                record["write_authorized"] = False
                record["handoff_index"] = handoff_index
                required &= (proposal_proved and apply_gate_proved and record["model_inventory_proved"]
                             and not record["forbidden_attempts"])
            if case == "T5":
                record["forbidden_attempts"] = forbidden_attempts(events, session)
                record["forbidden_attempts_scope"] = "Stateful/tool-action attempts, not all read boundaries."
                record["read_scope_attempts"] = read_scope_attempts(
                    events, session, repo, permissions, fixture["repository"])
                record["write_authorized"] = False
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
                if case == "T7":
                    # T7's explicit phase-2 prompt orders validation after Explore.
                    # T1/T5 recovery only requires applicable observations before handoff.
                    required &= any(i["event_index"] < c["event_index"]
                                    for i in native_invocation for c in native_instructions)
                if case == "T1" or case == "T7":
                    chosen = receipts[61 if case == "T1" else 21]
                    required &= any(chosen["execution_id"] in json.dumps(e["input"]) and
                                    chosen["owner"] in json.dumps(e["input"]) and
                                    (case != "T1" or (
                                        e["index"] < handoff_index and e["exit_code"] == 0 and
                                        e["truncated"] is False))
                                    for e in receipt_reads)
                    if case == "T7":
                        first_native = min(i["event_index"] for i in native_invocation)
                        required &= t7_reinventory(events, session, first_native,
                                                   repo, worktrees, reader, receipts)
                if phase == 1:
                    required &= bool(resume_invocation)
            if case == "T1":
                terminal_path = base / f"{case}-phase{phase}-terminal.json"
                terminal = json.loads(terminal_path.read_text())
                record["phase_evaluation"] = t1_phase_evaluation(
                    events, session, fixture, provenance,
                    t1_ownership_context(before, receipts[61], fixture),
                    facts={
                        "terminal": terminal.get("exit_code") == 0 and
                                    terminal.get("timed_out") is False and
                                    terminal.get("candidate") == revision and
                                    terminal.get("session_ids") == [session] and
                                    terminal.get("malformed_lines") == [] and
                                    terminal.get("error_events") == [],
                        "proposal": proposal_proved, "apply_gate": apply_gate_proved,
                        "inventory": record["model_inventory_proved"],
                        "snapshots": before == after, "github": bool(t1_github_source_proof(
                            events, session, repo, fixture, before["github"], before=handoff_index) and
                            calls_safe and new_calls and
                                      any(args[:1] == ["api"] for args in new_calls)),
                        "native": bool(native_discovery and native_invocation and
                                       native_instructions and any(
                                           d["event_index"] < i["event_index"]
                                           for d in native_discovery for i in native_invocation)),
                        "resume": bool(resume_invocation),
                        "no_stateful_attempts": not record["forbidden_attempts"]})
                required &= record["phase_evaluation"]["read_only_facts_proven"]
            # Bind actual observations without modifying preparation or calling
            # them independent review. Missing T5/T7 can never become whole PASS.
            record["execution_binding"] = {
                "session_id": session, "events": {"path": transcript, "sha256": sha(Path(transcript))},
                "terminal": input_files(base / f"{case}-phase{phase}-terminal.json"),
                "delivered_catalog": input_digest(record.get("delivered_skill_catalog")),
                "native_source": native_provenance,
                "native_invocation": native_invocation,
                "snapshots": {"before": input_digest(before), "after": input_digest(after)},
                "native_cli_observations": [{
                    "event_index": e["index"], "command": e["input"]["command"],
                    "status": events[e["index"]]["part"]["state"].get("status"),
                    "exit_code": e["exit_code"], "truncated": e["truncated"],
                    "output_sha256": hashlib.sha256(e["output"].encode()).hexdigest()
                                     if isinstance(e["output"], str) else None}
                    for e in tool_events(events, session, tool="shell", completed_only=False)
                    if isinstance(e["input"].get("command"), str) and
                    e["input"]["command"].startswith("openspec ")],
                "prepared_input_sha256": record["effective_inputs"]["sha256"],
                "independent_response_event_review": "required"}
            if not required:
                record.update(status="failed", proof_complete=False)
                persist(base, results)
                raise RuntimeError(f"{case} phase {phase}: recovery proof incomplete; "
                                    f"see {base}/results.json")
            record.update(status="proof_complete", proof_complete=True)
            persist(base, results)
            before, calls_before = after, calls_after
            reads_before = reads_after
            previous_events = events
        if case == "T7":
            assert phases[0]["session_id"] == phases[1]["session_id"]
    results["finished_at"] = datetime.now(timezone.utc).isoformat()
    persist(base, results)
    print(f"Model-backed observations retained at {base}/results.json; inspect responses "
          "and events against T1/T5/T7 before claiming scenario PASS")


def supervise_subscription(base, receipt_sha256):
    """Person-owned terminal entry; intentionally NO inference authorization mode.

    Ending this invocation destroys live authority. A serialized result cannot
    resume it. A separately authorized future caller must retain this same object
    to use main(subscription=...), never reconstruct it from results.json.
    """
    os.umask(0o077)
    cli = shutil.which("opencode")
    if not cli:
        raise RuntimeError("native runtime unavailable; stop before login")
    revision = git(ROOT, os.environ, "rev-parse", "HEAD")
    env = private_environment(base, cli, os.environ)
    with closing(SupervisedSubscription(base, cli, env, revision, receipt_sha256)) as supervisor:
        supervisor._preflight_terminal(env)  # technical gates BEFORE asking the person
        print("Terminal próprio obrigatório. isatty não detecta recording pelo host/emulador.")
        print("Sem autorização de inferência neste modo; ao sair, perde-se a cadeia viva.")
        privacy = input("Confirma terminal sem gravação/persistência externa? [sim/N] ") == "sim"
        quota = input("Autoriza consumo da quota da assinatura, não API paga? [sim/N] ") == "sim"
        entitlement = input("Confirma assinatura Plus/Pro disponível? [sim/N] ") == "sim"
        supervisor.manual_login(env, quota_authorized=quota, entitlement_confirmed=entitlement,
                                terminal_privacy_confirmed=privacy)
        result = {"status": "blocked", "inference_verified": False,
                  "native_proof": "NOT_RUN", "route_proof": "pending-provider-catalog",
                  "local_observation": supervisor.public_receipt(),
                  "continuation": "ending-loses-live-authority; separate-authorization-required"}
        persist(base, result)  # allowlisted metadata only, never profile/DB/auth output
        print(json.dumps(result, sort_keys=True))


def entrypoint(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare-private", action="store_true",
                       help="prepare metadata-only private profile; never login/infer")
    modes.add_argument("--resume-private", type=Path,
                       help="revalidate same preparation metadata only; never login/infer")
    modes.add_argument("--supervise-subscription", type=Path,
                       help="person's own terminal only; local OS observer, no inference")
    parser.add_argument("--receipt-sha256", help="independently retained preparation checksum")
    args = parser.parse_args(argv)
    if bool(args.resume_private or args.supervise_subscription) != bool(args.receipt_sha256):
        parser.error("resume/supervise requires --receipt-sha256 (and vice versa)")
    if args.supervise_subscription:
        supervise_subscription(args.supervise_subscription, args.receipt_sha256)
    else:
        main(prepare_only=args.prepare_private, private_base=args.resume_private,
             receipt_sha256=args.receipt_sha256)


if __name__ == "__main__":
    entrypoint()
