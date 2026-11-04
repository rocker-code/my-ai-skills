"""Portable, fail-closed evidence for a test execution (stdlib only)."""

from __future__ import annotations

import fnmatch
import hashlib
import io
import json
import os
import platform
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from worktree_registry import FINGERPRINT_VERSION, code_state, drift_report, identity

SCHEMA = "my-ai-skills.test-evidence/v1"
PUBLIC_SCHEMA = "my-ai-skills.test-evidence-public/v1"
MARKER = "<!-- my-ai-skills-test-evidence:v1 -->"
START = "<!-- my-ai-skills-test-evidence-data:start -->"
END = "<!-- my-ai-skills-test-evidence-data:end -->"
EVIDENCE_ID = re.compile(r"ev-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
NAME = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}")
PROFILE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:+/-]{0,127}")
SENSITIVE = re.compile(r"(?i)(?:token|password|secret|key|credential|ghp_|github_pat_|authorization)")
ENV_NAME = re.compile(r"(?:CI|NODE_ENV|PYTHON[A-Z0-9_]*|[A-Z][A-Z0-9_]*)")


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def hash_bytes(value):
    return hashlib.sha256(value).hexdigest()


def hash_file(path):
    try:
        with path.open("rb") as stream:
            digest = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
            return digest.hexdigest()
    except FileNotFoundError:
        return None


def git(checkout, *args):
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(checkout), *args],
                            text=True, capture_output=True, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Git inspection failed")
    return result.stdout.strip()


def checkout_root(checkout):
    return Path(git(checkout, "rev-parse", "--show-toplevel")).resolve()


def repository(checkout):
    remote = identity(checkout)["remote"]
    match = re.fullmatch(r"(?:git@github\.com:|https://github\.com/)([^?#]+?)(?:\.git)?/?", remote)
    return match.group(1) if match and REPOSITORY.fullmatch(match.group(1)) else None


def store(checkout):
    base = Path(identity(checkout)["common_dir"]) / "ai-workflow" / "evidence"
    base.mkdir(parents=True, exist_ok=True)
    return base


def record_dir(checkout, evidence_id):
    if not EVIDENCE_ID.fullmatch(evidence_id):
        raise ValueError("invalid evidence_id")
    return store(checkout) / evidence_id


def safe_relative(path, checkout):
    root = checkout_root(checkout)
    absolute = (root / path).resolve()
    if not path or Path(path).is_absolute() or ".." in Path(path).parts or not absolute.is_relative_to(root):
        raise ValueError(f"path must remain inside checkout: {path}")
    return str(absolute.relative_to(root))


def parse_pairs(items):
    result = {}
    for pair in items:
        name, sep, value = pair.partition("=")
        if not sep or not NAME.fullmatch(name) or not PROFILE.fullmatch(value) or SENSITIVE.search(value):
            raise ValueError("tool/env identifiers must be non-secret NAME=ID pairs")
        if name in result:
            raise ValueError(f"duplicate identifier: {name}")
        result[name] = value
    return result


def runner(tools, env_ids, env_names=()):
    for name in env_names:
        if not ENV_NAME.fullmatch(name) or name not in env_ids:
            raise ValueError("--env-name requires an allowed name and corresponding --env-id")
    compatibility = {"python": f"{sys.version_info.major}.{sys.version_info.minor}",
                     "platform": sys.platform, "architecture": platform.machine(),
                     "tools": tools, "env_ids": env_ids}
    return {**compatibility, "env_names": sorted(env_names),
            "hostname_hash": hash_bytes(socket.gethostname().encode()),
            "compatibility_digest": "sha256:" + hash_bytes(canonical(compatibility))}


def scrub(argv):
    result = []
    redact_next = False
    for arg in argv:
        if redact_next:
            result.append("[REDACTED]")
            redact_next = False
            continue
        if arg.lower() == "authorization:":
            result.append("Authorization: [REDACTED]")
            redact_next = True
            continue
        if re.match(r"(?i)^--[^=]*(?:token|password|secret|key|credential)(?:=|$)", arg):
            if "=" in arg:
                result.append(arg.partition("=")[0] + "=[REDACTED]")
            else:
                result.append(arg)
                redact_next = True
            continue
        arg = re.sub(r"(?i)authorization:\s*\S+", "Authorization: [REDACTED]", arg)
        arg = re.sub(r"(?i)\b(?:ghp_|github_pat_)[A-Za-z0-9_]+", "[REDACTED]", arg)
        arg = re.sub(r"(://)[^/@\s]+:[^/@\s]+@", r"\1[REDACTED]@", arg)
        result.append(arg)
    return result


def code_snapshot(checkout, config_paths=(), excluded_paths=()):
    root = checkout_root(checkout)
    configs = [{"path": path, "sha256": hash_file(root / path)} for path in sorted(set(config_paths))]
    state = code_state(root, exclude_paths=excluded_paths, include_ignored=config_paths)
    fingerprint = "sha256:" + hash_bytes(canonical({"v": FINGERPRINT_VERSION, "registry_digest": state.digest,
                                                   "configs": configs}))
    return {"head": state.head, "fingerprint": fingerprint, "registry_digest": state.digest,
            "dirty": bool(state.entries), "changed_paths": [entry.__dict__ | {"index": [i.__dict__ for i in entry.index]}
                                                          for entry in state.entries],
            "config_paths": configs, "excluded_paths": list(excluded_paths),
            "state": state.to_json()}


def save_manifest(directory, manifest):
    directory.mkdir(parents=True, exist_ok=True)
    temp = directory / ".manifest.tmp"
    temp.write_bytes(canonical(manifest) + b"\n")
    temp.replace(directory / "manifest.json")


def load_manifest(directory):
    return json.loads((directory / "manifest.json").read_text())


def obligations(items, gate=None):
    if not items:
        raise ValueError("at least one --obligation is required")
    result = []
    for item in items:
        oid, _, globs = item.partition(":")
        if not NAME.fullmatch(oid):
            raise ValueError("invalid obligation id")
        result.append({"id": oid, "required_gate": gate, "relevant_paths": [x for x in globs.split(",") if x]})
    return result


def counts_from_reports(reports):
    totals = dict(tests=0, failures=0, errors=0, skipped=0, source="none")
    for report in reports:
        if not report.is_file():
            continue
        root = ET.parse(report).getroot()
        if root.tag == "testsuite" or (root.tag == "testsuites" and root.get("tests") is not None):
            suites = [root]
        else:
            suites = [suite for suite in root.findall(".//testsuite") if not suite.findall("testsuite")]
        for suite in suites:
            for field in ("tests", "failures", "errors", "skipped"):
                totals[field] += int(suite.get(field, "0"))
        totals["source"] = "junit"
    return totals


def artifact(directory, source, name, role):
    destination = directory / "artifacts" / name
    if not source.is_file():
        return {"name": name, "role": role, "sha256": None, "bytes": None, "state": "missing"}
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source != destination:
        shutil.copyfile(source, destination)
    return {"name": name, "role": role, "sha256": hash_file(destination),
            "bytes": destination.stat().st_size, "state": "present"}


def record(checkout, args):
    root = checkout_root(checkout)
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("record requires -- <command>")
    claimed_obligations = obligations(args.obligation, args.required_gate)
    config = [safe_relative(p, root) for p in args.config]
    reports = [safe_relative(p, root) for p in args.report]
    artifacts = [safe_relative(p, root) for p in args.artifact]
    outputs = [safe_relative(p, root).rstrip("/") + "/**" for p in args.output_dir]
    excluded = reports + artifacts + outputs
    if set(config) & set(reports + artifacts) or any(fnmatch.fnmatchcase(p, pat) for p in config for pat in outputs):
        raise ValueError("configuration cannot be excluded as output")
    tools, env_ids = parse_pairs(args.tool), parse_pairs(args.env_id)
    run = runner(tools, env_ids, args.env_name)
    before = code_snapshot(root, config, excluded)
    evidence_id = "ev-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(4)
    directory = record_dir(root, evidence_id)
    directory.mkdir(exist_ok=False)
    manifest = {"schema": SCHEMA, "evidence_id": evidence_id, "kind": "local",
                "repository": repository(root), "code": {**before, "fingerprint_after": None},
                "command": {"argv": scrub(command), "cwd": str(Path.cwd().resolve().relative_to(root))},
                "selection": args.selection, "obligations": claimed_obligations,
                "openspec_change": args.openspec_change, "runner": run, "started_at": now(),
                "finished_at": None, "exit_code": None, "status": "running", "counts": counts_from_reports([]),
                "artifacts": [], "correlation": {k: getattr(args, "correlation_" + k)
                                              for k in ("run_id", "issue_url", "stage", "worker_id")
                                              if getattr(args, "correlation_" + k)},
                "producer": None, "extensions": {}}
    save_manifest(directory, manifest)
    print(json.dumps({"evidence_id": evidence_id}), file=sys.stderr, flush=True)
    log = directory / "artifacts" / "execution.log"
    log.parent.mkdir(exist_ok=True)
    result = None
    try:
        with log.open("wb") as output:
            process = subprocess.Popen(command, cwd=Path.cwd(), stdout=output, stderr=subprocess.STDOUT)
            try:
                result = process.wait()
            except KeyboardInterrupt:
                process.terminate()
                process.wait()
                raise
    except (KeyboardInterrupt, OSError):
        manifest["status"] = "interrupted"
    else:
        manifest["status"] = "passed" if result == 0 else "failed"
    manifest["finished_at"] = now()
    manifest["exit_code"] = result
    after = code_snapshot(root, config, excluded)
    manifest["code"]["fingerprint_after"] = after["fingerprint"]
    manifest["code"]["state_after"] = after["state"]
    if before["fingerprint"] != after["fingerprint"]:
        manifest["status_note"] = "concurrent_change"
    manifest["artifacts"] = [artifact(directory, log, "execution.log", "log")]
    for path in reports + artifacts:
        manifest["artifacts"].append(artifact(directory, root / path, "outputs/" + path, "report"))
    try:
        manifest["counts"] = counts_from_reports([root / p for p in reports])
    except (ET.ParseError, ValueError):
        manifest["counts"] = counts_from_reports([])
        manifest["status_note"] = "invalid_junit"
    save_manifest(directory, manifest)
    return result if result is not None else 130


def gh(*args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "GitHub API unavailable")
    return json.loads(result.stdout)


def hosted_url(repo, run_id):
    return f"https://github.com/{repo}/actions/runs/{run_id}"


def parse_hosted_url(url):
    match = re.fullmatch(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/actions/runs/([1-9][0-9]*)", url)
    if not match or not REPOSITORY.fullmatch(match.group(1)):
        raise ValueError("expected canonical GitHub Actions run URL")
    return match.group(1), match.group(2)


def confirm_hosted(repo, run_id):
    data = gh("api", f"repos/{repo}/actions/runs/{run_id}")
    if (str(data.get("id")) != str(run_id) or data.get("repository", {}).get("full_name") != repo
            or not SHA.fullmatch(str(data.get("head_sha", ""))) or data.get("status") != "completed"
            or data.get("conclusion") not in {"success", "failure", "timed_out", "cancelled", "action_required"}):
        raise ValueError("run identity, repository, head or terminal conclusion not confirmed")
    return data


def register_hosted(checkout, args):
    claimed_obligations = obligations(args.obligation, args.required_gate)
    repo, run_id = parse_hosted_url(args.url)
    if repo != repository(checkout):
        raise ValueError("hosted repository differs from checkout")
    data = confirm_hosted(repo, run_id)
    state = code_state(checkout)
    evidence_id = "ev-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(4)
    manifest = {"schema": SCHEMA, "evidence_id": evidence_id, "kind": "hosted", "repository": repo,
                "code": {"head": data["head_sha"], "fingerprint": state.digest, "fingerprint_after": state.digest,
                         "dirty": bool(state.entries)},
                "command": {"argv": [], "cwd": ""}, "selection": args.selection,
                "obligations": claimed_obligations, "runner": {},
                "started_at": data.get("created_at"), "finished_at": data.get("updated_at"),
                "exit_code": 0 if data["conclusion"] == "success" else 1,
                "status": "passed" if data["conclusion"] == "success" else "failed",
                "counts": counts_from_reports([]), "artifacts": [],
                "hosted": {"url": args.url, "run_id": run_id, "head": data["head_sha"],
                           "clean": not bool(state.entries)}, "producer": None, "extensions": {}}
    save_manifest(record_dir(checkout, evidence_id), manifest)
    return evidence_id


def public_projection(manifest):
    evidence_id, repo, kind = manifest.get("evidence_id"), manifest.get("repository"), manifest.get("kind")
    code, status = manifest.get("code"), manifest.get("status")
    if (not isinstance(evidence_id, str) or not EVIDENCE_ID.fullmatch(evidence_id)
            or not isinstance(repo, str) or not REPOSITORY.fullmatch(repo)
            or kind not in ("local", "hosted") or not isinstance(code, dict)
            or not isinstance(code.get("head"), str) or not SHA.fullmatch(code["head"])
            or status not in ("running", "interrupted", "passed", "failed")):
        raise ValueError("invalid public projection fields")
    result = {"schema": PUBLIC_SCHEMA, "evidence_id": evidence_id, "kind": kind,
              "repository": repo, "code": {"head": code["head"]}, "status": status}
    if kind == "hosted":
        hosted = manifest.get("hosted")
        if not isinstance(hosted, dict):
            raise ValueError("hosted data missing")
        url = hosted.get("url")
        repo_from_url, run_id = parse_hosted_url(url) if isinstance(url, str) else (None, None)
        if repo_from_url != repo or str(hosted.get("run_id")) != run_id:
            raise ValueError("invalid hosted public fields")
        result["hosted"] = {"run_id": run_id, "url": url}
    if len(canonical(result)) > 60000:
        raise ValueError("projection exceeds 60000 bytes")
    return result


def comment_payload(projection):
    return f"Test evidence {projection['evidence_id']}\n\n{MARKER}\n{START}\n{canonical(projection).decode()}\n{END}"


def parse_comment(body):
    if MARKER not in body or START not in body or END not in body:
        return None
    try:
        value = json.loads(body.split(START, 1)[1].split(END, 1)[0].strip())
        return value if value.get("schema") == PUBLIC_SCHEMA else None
    except (ValueError, AttributeError):
        return None


def target_url(value):
    match = re.fullmatch(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/(issues|pull)/([1-9][0-9]*)", value)
    if not match:
        raise ValueError("expected GitHub issue or PR URL")
    return match.group(1), match.group(2), match.group(3)


def comments(repo, number):
    pages = gh("api", "--paginate", "--slurp", f"repos/{repo}/issues/{number}/comments")
    return [item for page in pages for item in page]


def publish(checkout, evidence_id, target):
    manifest = load_manifest(record_dir(checkout, evidence_id))
    if manifest.get("schema") != SCHEMA:
        raise ValueError("unknown private evidence schema")
    projection = public_projection(manifest)
    repo, _, number = target_url(target)
    if projection["repository"] != repo:
        raise ValueError("target repository differs from evidence")
    matches = [(item, parse_comment(item.get("body", ""))) for item in comments(repo, number)]
    matches = [item for item, value in matches if value and value.get("evidence_id") == evidence_id]
    if len(matches) > 1:
        raise ValueError("duplicate evidence comments; refusing to overwrite")
    body = comment_payload(projection)
    if matches:
        gh("api", "--method", "PATCH", f"repos/{repo}/issues/comments/{matches[0]['id']}", "-f", f"body={body}")
    else:
        gh("api", f"repos/{repo}/issues/{number}/comments", "-f", f"body={body}")
    return projection


def from_github(target, evidence_id):
    repo, _, number = target_url(target)
    values = [parse_comment(item.get("body", "")) for item in comments(repo, number)]
    values = [v for v in values if v and v.get("evidence_id") == evidence_id]
    if len(values) != 1:
        raise ValueError("evidence projection not uniquely available")
    value = values[0]
    if value.get("repository") != repo:
        return {"evidence_id": evidence_id}
    return value


def gate_binding(repo, base_branch, obligation, run_id, head):
    """Only base-branch policy + effective protection + a run job can bind a gate."""
    if not base_branch:
        return False
    try:
        ref = gh("api", f"repos/{repo}/branches/{base_branch}")
        base_sha = ref["commit"]["sha"]
        # Read trusted policy at the branch's immutable base SHA, not the PR.
        policy = gh("api", f"repos/{repo}/contents/.ai-workflow/required-evidence.json?ref={base_sha}")
        import base64
        mapping = json.loads(base64.b64decode(policy["content"]))
        entry = mapping["obligations"][obligation]
        workflow, check = entry["workflow"], entry["check"]
        protection = gh("api", f"repos/{repo}/branches/{base_branch}/protection/required_status_checks")
        required = [item["context"] for item in protection.get("checks", [])] + protection.get("contexts", [])
        if check not in required or not workflow.startswith(".github/workflows/"):
            return False
        run = confirm_hosted(repo, run_id)
        if run["head_sha"] != head or run.get("path") != workflow:
            return False
        jobs = gh("api", "--paginate", f"repos/{repo}/actions/runs/{run_id}/jobs")
        return any(job.get("name") == check and job.get("run_id") == int(run_id)
                   and job.get("head_sha", head) == head and job.get("status") == "completed"
                   and job.get("conclusion") == "success" for job in jobs.get("jobs", []))
    except (ValueError, KeyError, TypeError, OSError):
        return False


def verify_manifest(manifest, directory, checkout, *, tools=None, env_ids=None, base_branch=None, projection=False):
    tools, env_ids = tools or {}, env_ids or {}
    obs = manifest.get("obligations", []) if not projection else []
    result = {"evidence_id": manifest.get("evidence_id"), "state": "incomplete", "result": None,
              "reasons": [], "changed_paths": [], "obligations": [],
              "recovery": {"obligations": [o.get("id") for o in obs if isinstance(o, dict)], "action": "rerun"}}

    def finish(state, reason, action="rerun", impacts=None):
        result.update(state=state, reasons=[reason])
        result["recovery"]["action"] = action
        result["obligations"] = impacts if impacts is not None else [
            {"id": o["id"], "impact": "affected", "gate": "pending"} for o in obs]
        return result

    try:
        if projection or manifest.get("kind") == "hosted":
            projected = public_projection(manifest)
            if projection and projected != manifest:
                raise ValueError("unknown or malformed public fields")
        elif (manifest.get("kind") != "local" or
              (manifest.get("repository") is not None and
               (not isinstance(manifest["repository"], str) or not REPOSITORY.fullmatch(manifest["repository"]))) or
              not EVIDENCE_ID.fullmatch(str(manifest.get("evidence_id", ""))) or
              not SHA.fullmatch(str(manifest.get("code", {}).get("head", "")))):
            raise ValueError("invalid local identity")
        if not projection and (manifest.get("schema") != SCHEMA or not isinstance(obs, list) or not obs
                               or any(not isinstance(o, dict) or not NAME.fullmatch(o.get("id", ""))
                                      or o.get("required_gate") not in (None, "local", "hosted") for o in obs)
                               or not isinstance(manifest.get("artifacts"), list)
                               or not isinstance(manifest.get("runner"), dict)
                               or not isinstance(manifest.get("code"), dict)
                               or not isinstance(manifest.get("command"), dict)
                               or not isinstance(manifest.get("status"), str)
                               or "started_at" not in manifest or "finished_at" not in manifest
                               or "exit_code" not in manifest):
            raise ValueError("missing or invalid private fields")
        if not projection and manifest["kind"] == "local":
            code = manifest["code"]
            required_code = ("fingerprint", "fingerprint_after", "state", "config_paths", "excluded_paths")
            required_runner = ("python", "platform", "architecture", "tools", "env_ids", "compatibility_digest")
            if (any(key not in code for key in required_code) or
                    any(key not in manifest["runner"] for key in required_runner)):
                raise ValueError("missing local code or runner identity")
        if projection and manifest.get("schema") != PUBLIC_SCHEMA:
            raise ValueError("unknown public schema")
    except (ValueError, TypeError, AttributeError):
        return finish("incomplete", "invalid_schema_or_required_fields")

    kind = manifest["kind"]
    code = manifest["code"]
    state = code_state(checkout)
    if kind == "local" and not projection:
        if code.get("fingerprint") != code.get("fingerprint_after"):
            return finish("ambiguous", "code_changed_during_execution")
        if manifest.get("status") in ("running", "interrupted") or manifest.get("exit_code") is None:
            return finish("incomplete", "execution_not_terminal")
        if any(o.get("required_gate") == "hosted" for o in obs):
            return finish("not_applicable", "local_execution_cannot_satisfy_hosted_gate")
        configs = [item["path"] for item in code.get("config_paths", [])]
        current = code_snapshot(checkout, configs, code.get("excluded_paths", []))
        if code.get("fingerprint") != current["fingerprint"]:
            baseline = code.get("state", {})
            drift = drift_report(baseline, code_state(checkout, exclude_paths=code.get("excluded_paths", []),
                                                      include_ignored=configs), checkout=checkout)
            paths = set(drift["changed_paths"] + drift["committed_paths"]) if drift else set()
            paths.update(p["path"] for p, q in zip(code.get("config_paths", []), current["config_paths"])
                         if p.get("sha256") != q.get("sha256"))
            result["changed_paths"] = sorted(paths)
            unknown = code.get("head") != current["head"] and not paths
            impacts = [{"id": o["id"], "impact": "affected" if o.get("required_gate") or unknown
                        or not o.get("relevant_paths") or any(fnmatch.fnmatchcase(p, glob)
                                                               for p in paths for glob in o["relevant_paths"])
                        else "unaffected", "gate": "pending"} for o in obs]
            return finish("stale", "code_changed", impacts=impacts)
        observed = runner(tools, env_ids)
        declared = manifest["runner"]
        if (set(declared.get("tools", {})) - tools.keys() or set(declared.get("env_ids", {})) - env_ids.keys()):
            return finish("incomplete", "missing_environment_identifiers", "provide_identifiers")
        expected = {key: declared.get(key) for key in ("python", "platform", "architecture", "tools", "env_ids")}
        actual = {key: observed.get(key) for key in expected}
        if (expected != actual or declared.get("compatibility_digest") != observed["compatibility_digest"]):
            return finish("stale", "environment_changed")
        for item in manifest["artifacts"]:
            name = item.get("name", "")
            if (not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts
                    or item.get("state") != "present" or hash_file(directory / "artifacts" / name) != item.get("sha256")):
                return finish("incomplete", f"artifact_missing_or_changed:{name}", "restore_artifact")
        if not any(item.get("role") == "log" for item in manifest["artifacts"]):
            return finish("incomplete", "log_missing", "restore_artifact")
    elif kind == "local":
        if code["head"] != state.head:
            return finish("stale", "head_changed")
        return finish("metadata_only", "local_artifacts_unavailable", "import_bundle")
    else:
        if any(o.get("required_gate") == "local" for o in obs):
            return finish("not_applicable", "hosted_execution_cannot_satisfy_local_gate")
        if code["head"] != state.head or state.entries or (not projection and not manifest["hosted"].get("clean")):
            return finish("stale", "hosted_head_or_cleanliness_changed")
        try:
            hosted = manifest["hosted"]
            repo, run_id = parse_hosted_url(hosted["url"])
            if repo != manifest["repository"] or str(hosted["run_id"]) != run_id:
                raise ValueError("hosted identity mismatch")
            confirmed = confirm_hosted(repo, run_id)
            if confirmed["head_sha"] != code["head"]:
                raise ValueError("hosted head mismatch")
        except (ValueError, KeyError, TypeError, OSError):
            return finish("metadata_only", "hosted_origin_unconfirmed", "provide_identifiers")
        result["result"] = "passed" if confirmed["conclusion"] == "success" else "failed"
        if any(o.get("required_gate") == "hosted" for o in obs):
            if result["result"] != "passed" or not all(gate_binding(repo, base_branch, o["id"], run_id, state.head)
                                                         for o in obs if o.get("required_gate") == "hosted"):
                result["state"] = "verified"
                result["reasons"] = ["hosted_gate_binding_unconfirmed"]
                result["obligations"] = [{"id": o["id"], "impact": "affected", "gate": "pending"} for o in obs]
                return result
    result["state"] = "verified"
    result["result"] = result["result"] or ("passed" if manifest.get("exit_code") == 0 else "failed")
    result["obligations"] = [{"id": o["id"], "impact": "unaffected", "gate": "satisfied" if result["result"] == "passed" else "pending"} for o in obs]
    result["recovery"]["obligations"] = [] if result["result"] == "passed" else result["recovery"]["obligations"]
    return result


def export_bundle(checkout, evidence_id, destination):
    directory = record_dir(checkout, evidence_id)
    load_manifest(directory)
    members = sorted(p for p in directory.rglob("*") if p.is_file())
    if any(p.is_symlink() for p in directory.rglob("*")):
        raise ValueError("symlink in evidence directory")
    sums = "".join(f"{hash_file(p)}  {p.relative_to(directory)}\n" for p in members).encode()
    with tarfile.open(destination, "w:gz") as bundle:
        for path in members:
            bundle.add(path, arcname=str(path.relative_to(directory)), recursive=False)
        info = tarfile.TarInfo("SHA256SUMS")
        info.size = len(sums)
        bundle.addfile(info, io.BytesIO(sums))
    return destination


def import_bundle(checkout, source):
    with tarfile.open(source, "r:gz") as bundle:
        members = bundle.getmembers()
        names = [m.name for m in members]
        if (len(names) != len(set(names)) or "SHA256SUMS" not in names or "manifest.json" not in names
                or any(not m.isfile() or Path(m.name).is_absolute() or ".." in Path(m.name).parts
                       or not m.name or m.name.startswith(".") for m in members)):
            raise ValueError("unsafe bundle members")
        sums = bundle.extractfile("SHA256SUMS").read().decode().splitlines()
        expected = {}
        for line in sums:
            match = re.fullmatch(r"([a-f0-9]{64})  (.+)", line)
            if not match or match.group(2) in expected:
                raise ValueError("invalid bundle checksums")
            expected[match.group(2)] = match.group(1)
        if set(expected) != set(names) - {"SHA256SUMS"}:
            raise ValueError("bundle member list mismatch")
        data = {}
        for name in expected:
            content = bundle.extractfile(name).read()
            if hash_bytes(content) != expected[name]:
                raise ValueError("bundle checksum mismatch")
            data[name] = content
    manifest = json.loads(data["manifest.json"])
    if manifest.get("schema") != SCHEMA:
        raise ValueError("unknown evidence schema")
    directory = record_dir(checkout, manifest["evidence_id"])
    if directory.exists():
        raise ValueError("evidence ID already exists; refusing overwrite")
    with tempfile.TemporaryDirectory(dir=store(checkout)) as temp:
        for name, content in data.items():
            target = Path(temp) / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        Path(temp).rename(directory)
    return manifest["evidence_id"]
