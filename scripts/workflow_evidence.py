"""Portable, fail-closed evidence for a test execution (stdlib only)."""

from __future__ import annotations

import fnmatch
import gzip
import hashlib
import io
import inspect
import json
import os
import platform
import re
import secrets
import shutil
import socket
import stat
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
MAX_BUNDLE_MEMBERS = 1024
MAX_BUNDLE_BYTES = 256 * 1024 * 1024
MAX_MEMBER_BYTES = 64 * 1024 * 1024
# Include tar framing and extended headers, not just the sizes of returned members.
MAX_ARCHIVE_BYTES = MAX_BUNDLE_BYTES + 16 * 1024 * 1024
PHASE_API = 1
PHASE_MODE = "inprocess-phase"
PHASE_NAMES = {"results.json"} | {
    f"{case}-phase{phase}-{suffix}" for case, phases in (("T1", (1,)), ("T5", (1,)), ("T7", (1, 2)))
    for phase in phases
    for suffix in ("events.jsonl", "terminal.json", "stderr.log")}
PHASE_FIELDS = {"state", "return_kind", "return_code", "result", "finalized", "error_code"}


def execution_mode(manifest, *, projection=False):
    """Discriminate before legacy exit handling. No reserved fields in extensions."""
    mode = manifest.get("execution_mode")
    command = manifest.get("command", {})
    phase_fields = {"phase_identity", "phase_completion"}
    extensions = manifest.get("extensions", {})
    if isinstance(extensions, dict) and (phase_fields | {"execution_mode", "callable"}) & extensions.keys():
        raise ValueError("reserved execution extension")
    if mode is None or mode == "subprocess":
        if (phase_fields & manifest.keys() or "callable" in command or
                manifest.get("kind") == "hosted" and mode is not None):
            raise ValueError("execution mode mismatch")
        return "subprocess"
    if mode != PHASE_MODE or manifest.get("kind") != "local":
        raise ValueError("unknown execution mode")
    if projection:
        return mode
    if any(o.get("required_gate") is not None for o in manifest.get("obligations", [])):
        raise ValueError("phase cannot declare required gates")
    call = command.get("callable", {})
    path = call.get("path")
    ident = manifest.get("phase_identity", {})
    completion = manifest.get("phase_completion", {})
    if ("exit_code" not in manifest or manifest["exit_code"] is not None or command.get("argv", "missing") is not None or
            set(command) != {"argv", "cwd", "callable", "origin"} or
            command["origin"] != "foreground-post-auth" or
            not isinstance(command["cwd"], str) or Path(command["cwd"]).is_absolute() or
            ".." in Path(command["cwd"]).parts or
            set(call) != {"path", "qualname", "sha256"} or not isinstance(path, str) or
            not path or Path(path).suffix != ".py" or Path(path).is_absolute() or ".." in Path(path).parts or
            not re.fullmatch(r"[A-Za-z0-9_.<>]+", str(call.get("qualname", ""))) or
            not re.fullmatch(r"[a-f0-9]{64}", str(call.get("sha256", ""))) or
            set(ident) != {"controller_pid", "controller_start", "execution_id"} or
            any(type(ident.get(k)) is not int or ident[k] <= 0
                for k in ("controller_pid", "controller_start")) or
            not re.fullmatch(r"[a-f0-9]{48}", str(ident.get("execution_id", ""))) or
            set(completion) != PHASE_FIELDS):
        raise ValueError("invalid phase identity")
    state = completion["state"]
    status = manifest.get("status")
    if state == "returned":
        kind, code = completion["return_kind"], completion["return_code"]
        if not ((kind == "none" and code is None) or (kind == "int" and type(code) is int)):
            raise ValueError("invalid phase return")
        result = "passed" if code in (None, 0) else "failed"
        if (completion["result"] != result or status != result or
                completion["finalized"] is not True or completion["error_code"] is not None or
                not manifest.get("finished_at") or not manifest.get("code", {}).get("fingerprint_after")):
            raise ValueError("inconsistent phase return")
    else:
        codes = {"running": {None}, "raised": {None, "phase_exception"},
                 "interrupted": {None, "phase_interrupted"},
                 "finalization_failed": {None, "phase_finalize_failed"},
                 "unknown": {None, "phase_unknown", "unsupported_return"}}
        if (state not in codes or completion["error_code"] not in codes[state] or
                any(completion[k] is not None for k in ("return_kind", "return_code", "result")) or
                completion["finalized"] is not False or
                status != ("running" if state == "running" else "interrupted")):
            raise ValueError("inconsistent phase completion")
    return mode


def phase_descriptor(manifest):
    return {key: manifest[key] for key in ("execution_mode", "evidence_id", "phase_identity")} | {
        "callable": manifest["command"]["callable"]}


def phase_read(path, *, private=True):
    """No-follow, bounded regular file; never traverse a profile or auth database."""
    path = Path(path).absolute()
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise ValueError("unsafe phase file ancestry")
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
        info = os.fstat(stream.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1 or
                private and stat.S_IMODE(info.st_mode) != 0o600 or info.st_size > MAX_MEMBER_BYTES):
            raise ValueError("unsafe phase file")
        data = stream.read(MAX_MEMBER_BYTES + 1)
        after = os.fstat(stream.fileno())
        if len(data) > MAX_MEMBER_BYTES or any(getattr(after, k) != getattr(info, k)
                for k in ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")):
            raise ValueError("phase file changed")
        return data


def phase_payload(name, data):
    """Closed filename/format boundary, before retaining any external payload."""
    if name not in PHASE_NAMES or len(data) > MAX_MEMBER_BYTES:
        raise ValueError("unsupported phase artifact")
    def safe(value, depth=0):
        if depth > 32:
            raise ValueError("phase nesting exceeded")
        if isinstance(value, dict):
            if value.get("type") == "credential" and "id" in value:
                raise ValueError("private phase identity")
            for key, child in value.items():
                if re.sub(r"[^a-z0-9]", "", key.lower()) in {
                    "accountid", "clientid", "devicecode", "authorizationcode", "accesstoken",
                    "refreshtoken", "idtoken", "apikey", "password", "authorization",
                    "credential", "credentials", "authjson"}:
                    raise ValueError("private phase field")
                safe(child, depth + 1)
        elif isinstance(value, list):
            for child in value:
                safe(child, depth + 1)
        elif isinstance(value, str):
            if re.search(r"(?i)Bearer\s+\S+|https?://\S*(?:oauth|authorize|callback)\S*[?&#](?:code|token|state)=", value):
                raise ValueError("private phase text")
            if value.strip().startswith(('"', "{", "[")):
                try:
                    decoded = json.loads(value)
                except ValueError:
                    pass
                else:
                    safe(decoded, depth + 1)
    values = [json.loads(line) for line in data.splitlines() if line.strip()] if name.endswith(".jsonl") else [json.loads(data)]
    for value in values:
        safe(value)
        if name.endswith("-stderr.log") and value not in (
                {"code": "native-stderr-present"}, {"code": "native-stderr-empty"}):
            raise ValueError("raw diagnostic forbidden")
        if name.endswith(".jsonl") and (not isinstance(value, dict) or not value.keys() <= {
                "type", "sessionID", "timestamp", "part", "error"} or
                value.get("type") not in {"text", "reasoning", "tool_use", "step_start", "step_finish", "error"}):
            raise ValueError("unsupported native event")


def phase_members(manifest):
    execution_mode(manifest)
    if manifest.get("schema") != SCHEMA or not isinstance(manifest.get("artifacts"), list):
        raise ValueError("invalid phase manifest")
    phase_payload("results.json", canonical(manifest))
    names = {"manifest.json", "SHA256SUMS"}
    for item in manifest["artifacts"]:
        name = item.get("name")
        if name == "execution.log":
            if item.get("role") != "log":
                raise ValueError("invalid phase log role")
        elif not isinstance(name, str) or not name.startswith("outputs/") or name[8:] not in PHASE_NAMES or item.get("role") != "phase":
            raise ValueError("unsupported phase member")
        if "artifacts/" + name in names or item.get("state") != "present":
            raise ValueError("duplicate/missing phase member")
        names.add("artifacts/" + name)
    if "artifacts/execution.log" not in names:
        raise ValueError("phase log missing")
    return names


def check_phase_files(manifest, directory):
    phase_members(manifest)
    for item in manifest["artifacts"]:
        data = phase_read(directory / "artifacts" / item["name"])
        if hash_bytes(data) != item["sha256"] or len(data) != item["bytes"]:
            raise ValueError("phase artifact changed")
        if item["name"] != "execution.log":
            phase_payload(item["name"][8:], data)
    log = phase_read(directory / "artifacts/execution.log")
    lines = [json.loads(line) for line in log.splitlines()]
    expected = [{"event": "begin", **phase_descriptor(manifest)},
                {"event": "complete", "phase_completion": manifest["phase_completion"]}]
    if lines != expected:
        raise ValueError("phase log marker mismatch")


def phase_support(checkout, callback):
    """Pre-auth capability/destination check. Does not start evidence or call callback."""
    root = checkout_root(checkout)
    if not Path.cwd().resolve().is_relative_to(root):
        raise ValueError("phase cwd must remain inside checkout")
    source = Path(inspect.getsourcefile(callback) or "").absolute()
    if not inspect.isfunction(callback) or not source.is_relative_to(root) or source.is_symlink():
        raise ValueError("phase requires internal tracked callable")
    path = str(source.relative_to(root))
    git(root, "ls-files", "--error-unmatch", "--", path)
    # Probe only the existing common-dir store, not any auth/profile file.
    destination = store(root)
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError("unsafe evidence destination")
    with tempfile.TemporaryFile(dir=destination) as probe:
        probe.write(b"phase-api-1")
        probe.flush()
    start = int(Path(f"/proc/{os.getpid()}/stat").read_text().rsplit(")", 1)[1].split()[19])
    return {"path": path, "qualname": callback.__qualname__, "sha256": hash_file(source)}, start


def record_phase(checkout, callback, *, obligation, artifacts, config=(), required_gate=None,
                 transport=False):
    """Synchronous internal closure only. No stdout/stderr interception or OS exit.

    Checksums are cooperative integrity, not authenticity against a host that
    rewrites every byte. Unknown completion never becomes a passing execution.
    """
    if required_gate is not None:
        raise ValueError("phase cannot declare required gates")
    root = checkout_root(checkout)
    call, start = phase_support(root, callback)
    configs = [safe_relative(p, root) for p in config]
    for path in configs:
        if re.search(r"(?i)(?:\.db(?:-wal|-shm)?|\.sqlite(?:3)?|auth\.json|login\.log)$", path):
            raise ValueError("private storage cannot be phase configuration")
        git(root, "ls-files", "--error-unmatch", "--", path)
    before = code_snapshot(root, configs)
    evidence_id = "ev-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(4)
    directory = record_dir(root, evidence_id)
    directory.mkdir(mode=0o700, exist_ok=False)
    (directory / "artifacts").mkdir(mode=0o700)
    def completion(state, error=None):
        return dict(state=state, return_kind=None, return_code=None, result=None,
                    finalized=False, error_code=error)
    manifest = {"schema": SCHEMA, "evidence_id": evidence_id, "kind": "local", "execution_mode": PHASE_MODE,
                "repository": repository(root), "code": {**before, "fingerprint_after": None},
                "command": {"argv": None, "cwd": str(Path.cwd().resolve().relative_to(root)),
                            "callable": call, "origin": "foreground-post-auth"},
                "phase_identity": {"controller_pid": os.getpid(), "controller_start": start,
                                   "execution_id": secrets.token_hex(24)},
                "phase_completion": completion("running"), "status": "running",
                "selection": "post-auth-native-observation", "obligations": obligations(obligation),
                "runner": runner({}, {}), "started_at": now(), "finished_at": None,
                "exit_code": None, "counts": counts_from_reports([]), "artifacts": [],
                "extensions": {}}
    save_manifest(directory, manifest)
    begin = {"event": "begin", **phase_descriptor(manifest)}
    log = directory / "artifacts/execution.log"
    def write_log():
        log.write_bytes(canonical(begin) + b"\n" + canonical({
            "event": "complete", "phase_completion": manifest["phase_completion"]}) + b"\n")
        log.chmod(0o600)
    log.write_bytes(canonical(begin) + b"\n")
    log.chmod(0o600)
    try:
        value = callback()  # Exactly once, in this PID, with the live closure.
    except (KeyboardInterrupt, SystemExit, InterruptedError):
        manifest["phase_completion"] = completion("interrupted", "phase_interrupted")
    except BaseException:
        manifest["phase_completion"] = completion("raised", "phase_exception")
    else:
        if value is None or type(value) is int:
            outcome = "passed" if value in (None, 0) else "failed"
            manifest["phase_completion"] = dict(state="returned", return_kind="none" if value is None else "int",
                                                return_code=value, result=outcome, finalized=True, error_code=None)
        else:
            manifest["phase_completion"] = completion("unknown", "unsupported_return")
    manifest["status"] = manifest["phase_completion"]["result"] or "interrupted"
    try:
        outputs = artifacts()
        if not isinstance(outputs, dict) or not outputs or not outputs.keys() <= PHASE_NAMES:
            raise ValueError("explicit phase artifact set required")
        total_bytes = 0
        for name, source in outputs.items():
            source = Path(source)
            if source.name != name:
                raise ValueError("phase artifact source mismatch")
            data = phase_read(source)
            phase_payload(name, data)
            total_bytes += len(data)
            if total_bytes > MAX_BUNDLE_BYTES:
                raise ValueError("phase artifacts exceed bundle limit")
            target = directory / "artifacts/outputs" / name
            target.parent.mkdir(mode=0o700, exist_ok=True)
            target.write_bytes(data)
            target.chmod(0o600)
            manifest["artifacts"].append({"name": "outputs/" + name, "role": "phase",
                                          "sha256": hash_bytes(data), "bytes": len(data), "state": "present"})
        after = code_snapshot(root, configs)
        manifest["code"].update(fingerprint_after=after["fingerprint"], state_after=after["state"])
    except BaseException:
        manifest["phase_completion"] = completion("finalization_failed", "phase_finalize_failed")
        manifest["status"] = "interrupted"
    manifest["finished_at"] = now()
    write_log()
    manifest["artifacts"].insert(0, artifact(directory, log, "execution.log", "log"))
    save_manifest(directory, manifest)
    if transport and manifest["phase_completion"]["state"] == "returned":
        bundle = directory / "phase-bundle.tar.gz"
        try:
            verified = verify_manifest(manifest, directory, root)
            if verified["state"] != "verified":
                raise ValueError("phase final verification incomplete")
            export_bundle(root, evidence_id, bundle)
            import_bundle(root, bundle, allow_existing=True)
        except BaseException:
            # This invocation alone allocated this directory/output. Never leave
            # an earlier "passed" transport after its finalization failed.
            if bundle.exists():
                bundle.unlink()
            manifest["phase_completion"] = completion("finalization_failed", "phase_finalize_failed")
            manifest["status"] = "interrupted"
            write_log()
            manifest["artifacts"][0] = artifact(directory, log, "execution.log", "log")
            save_manifest(directory, manifest)
    return evidence_id


class LimitedReader:
    """Bound bytes consumed before tarfile can parse extended headers."""

    def __init__(self, stream, limit):
        self.stream = stream
        self.remaining = limit

    def read(self, size=-1):
        if size < 0:
            size = self.remaining + 1
        chunk = self.stream.read(min(size, self.remaining + 1))
        self.remaining -= len(chunk)
        if self.remaining < 0:
            raise ValueError("bundle exceeds import size limit")
        return chunk


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
    header_value = False
    for arg in argv:
        if redact_next:
            result.append("[REDACTED]")
            redact_next = header_value and arg.lower() == "bearer"
            header_value = False
            continue
        if arg.lower() == "authorization:":
            result.append("Authorization: [REDACTED]")
            redact_next = True
            header_value = True
            continue
        if re.match(r"(?i)^--[^=]*(?:token|password|secret|key|credential)(?:=|$)", arg):
            if "=" in arg:
                result.append(arg.partition("=")[0] + "=[REDACTED]")
            else:
                result.append(arg)
                redact_next = True
            continue
        # A header can be passed as one argv element or as "Authorization: Bearer <token>".
        if re.search(r"(?i)\bauthorization\s*:", arg):
            result.append("Authorization: [REDACTED]")
            redact_next = bool(re.search(r"(?i)\bauthorization\s*:\s*bearer\s*$", arg))
            continue
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


def validate_exclusions(checkout, paths):
    """Outputs may be ignored, but never hide code tracked in HEAD or the index."""
    root = checkout_root(checkout)
    tracked = set()
    for args in (("ls-files", "--cached", "-z"), ("ls-tree", "-r", "--name-only", "-z", "HEAD")):
        result = subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args], capture_output=True)
        if result.returncode:
            raise ValueError("cannot inspect tracked output paths")
        tracked.update(os.fsdecode(p) for p in result.stdout.split(b"\0") if p)
    for path in paths:
        if not isinstance(path, str) or not path or Path(path).is_absolute() or ".." in Path(path).parts:
            raise ValueError("unsafe declared output path")
        # code_state interprets these as fnmatch patterns. Do not validate a
        # literal path here and then exclude a wider set of tracked code there.
        if any(char in path for char in "*?[") and not path.endswith("/**"):
            raise ValueError("glob metacharacters in declared output path")
        if path.endswith("/**") and any(char in path[:-3] for char in "*?["):
            raise ValueError("glob metacharacters in declared output path")
        directory = path[:-3] if path.endswith("/**") else None
        if any(p == path or (directory is not None and (p == directory or p.startswith(directory + "/")))
               for p in tracked):
            raise ValueError(f"output exclusion contains tracked code: {path}")


def save_manifest(directory, manifest):
    directory.mkdir(parents=True, exist_ok=True)
    temp = directory / ".manifest.tmp"
    temp.write_bytes(canonical(manifest) + b"\n")
    if manifest.get("execution_mode") == PHASE_MODE:
        temp.chmod(0o600)
    temp.replace(directory / "manifest.json")


def load_manifest(directory):
    path = directory / "manifest.json"
    if directory.is_symlink() or path.is_symlink():
        raise ValueError("unsafe manifest link")
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > 4 * 1024 * 1024:
            raise ValueError("unsafe manifest file")
        return json.loads(stream.read(4 * 1024 * 1024 + 1))


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
    totals = dict(tests=None, failures=None, errors=None, skipped=None, source="none")
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
                totals[field] = (totals[field] or 0) + int(suite.get(field, "0"))
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
    # Validate raw names before resolve() can normalize a wildcard-containing
    # directory into an apparently harmless path.
    for path in args.report + args.artifact + args.output_dir:
        if any(char in path for char in "*?["):
            raise ValueError("glob metacharacters in declared output path")
    config = [safe_relative(p, root) for p in args.config]
    reports = [safe_relative(p, root) for p in args.report]
    artifacts = [safe_relative(p, root) for p in args.artifact]
    outputs = [safe_relative(p, root).rstrip("/") + "/**" for p in args.output_dir]
    excluded = reports + artifacts + outputs
    validate_exclusions(root, excluded)
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
    if "--paginate" in args:
        decoder = json.JSONDecoder()
        pages, offset = [], 0
        output = result.stdout
        while offset < len(output):
            while offset < len(output) and output[offset].isspace():
                offset += 1
            if offset < len(output):
                page, offset = decoder.raw_decode(output, offset)
                pages.append(page)
        return pages
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
    mode = execution_mode(manifest, projection=manifest.get("schema") == PUBLIC_SCHEMA)
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
    if mode == PHASE_MODE:
        result["execution_mode"] = PHASE_MODE
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
    pages = gh("api", "--paginate", f"repos/{repo}/issues/{number}/comments")
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
        required = [item for item in protection.get("checks", []) if item.get("context") == check]
        if len(required) != 1 or not workflow.startswith(".github/workflows/"):
            return False
        run = confirm_hosted(repo, run_id)
        run_path = run.get("path", "").split("@", 1)[0]
        if run["head_sha"] != head or run_path != workflow:
            return False
        pages = gh("api", "--paginate", f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100")
        jobs = [job for page in pages for job in page["jobs"]]
        matches = [job for job in jobs if job.get("name") == check and job.get("run_id") == int(run_id)
                   and job.get("head_sha") == head and job.get("status") == "completed"
                   and job.get("conclusion") == "success"]
        if len(matches) != 1:
            return False
        # GitHub's required check may be pinned to an app. Confirm the actual
        # check run rather than trusting the job name or the producer manifest.
        check_url = matches[0].get("check_run_url", "")
        match = re.fullmatch(rf"https://api\.github\.com/repos/{re.escape(repo)}/check-runs/([0-9]+)", check_url)
        if not match:
            return False
        check_run = gh("api", f"repos/{repo}/check-runs/{match.group(1)}")
        app_id = required[0].get("app_id")
        return (check_run.get("id") == int(match.group(1)) and check_run.get("name") == check
                and check_run.get("head_sha") == head and check_run.get("status") == "completed"
                and check_run.get("conclusion") == "success" and
                (app_id in (None, -1) or check_run.get("app", {}).get("id") == app_id))
    except (ValueError, KeyError, TypeError, OSError, AttributeError):
        return False


def verify_manifest(manifest, directory, checkout, *, tools=None, env_ids=None, base_branch=None,
                    projection=False, required_obligations=()):
    tools, env_ids = tools or {}, env_ids or {}
    # Public projections deliberately contain no producer-owned obligations.
    # A consumer can request a hosted gate, which only base policy can bind.
    obs = ([{"id": oid, "required_gate": "hosted", "relevant_paths": []} for oid in required_obligations]
           if required_obligations else ([] if projection else manifest.get("obligations", [])))
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
        mode = execution_mode(manifest, projection=projection)
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
                    any(key not in manifest["runner"] for key in required_runner) or
                    not isinstance(code["state"], dict) or
                    not {"head", "digest", "entries"} <= code["state"].keys() or
                    not isinstance(code["config_paths"], list) or
                    not isinstance(code["excluded_paths"], list) or
                    not isinstance(manifest["runner"]["tools"], dict) or
                    not isinstance(manifest["runner"]["env_ids"], dict) or
                    any(not isinstance(item, dict) or "path" not in item for item in code["config_paths"]) or
                    any(not isinstance(item, dict) for item in manifest["artifacts"])):
                raise ValueError("missing local code or runner identity")
            for path in [item["path"] for item in code["config_paths"]] + code["excluded_paths"]:
                if not isinstance(path, str) or not path or Path(path).is_absolute() or ".." in Path(path).parts:
                    raise ValueError("unsafe declared path")
            validate_exclusions(checkout, code["excluded_paths"])
            if mode == PHASE_MODE:
                if code["excluded_paths"]:
                    raise ValueError("phase cannot exclude checkout inputs")
                for path in [manifest["command"]["callable"]["path"]] + [
                        item["path"] for item in code["config_paths"]]:
                    if re.search(r"(?i)(?:\.db(?:-wal|-shm)?|\.sqlite(?:3)?|auth\.json|login\.log)$", path):
                        raise ValueError("private phase input forbidden")
                    git(checkout, "ls-files", "--error-unmatch", "--", path)
        if projection and manifest.get("schema") != PUBLIC_SCHEMA:
            raise ValueError("unknown public schema")
    except (ValueError, TypeError, AttributeError, KeyError):
        return finish("incomplete", "invalid_schema_or_required_fields")

    kind = manifest["kind"]
    code = manifest["code"]
    state = code_state(checkout)
    if kind == "local":
        candidate_repo = repository(checkout)
        recorded_repo = manifest.get("repository")
        if recorded_repo and candidate_repo and recorded_repo != candidate_repo:
            return finish("stale", "repository_changed")
        if any(o.get("required_gate") for o in obs) and (not recorded_repo or not candidate_repo):
            return finish("incomplete", "repository_identity_unavailable", "provide_identifiers")
    bindings = {}
    if kind == "local" and not projection:
        try:
            if mode == PHASE_MODE:
                check_phase_files(manifest, directory)
                if manifest["phase_completion"]["state"] != "returned":
                    return finish("incomplete", "phase_not_terminal")
                call = manifest["command"]["callable"]
                if hash_file(checkout_root(checkout) / call["path"]) != call["sha256"]:
                    return finish("stale", "phase_callable_changed")
            else:
                # A surviving phase marker prevents partial manifest downgrade.
                log = directory / "artifacts/execution.log"
                if log.is_file():
                    with log.open("rb") as stream:
                        first = stream.readline(16384)
                    if b'"execution_mode":"inprocess-phase"' in first:
                        return finish("incomplete", "phase_mode_downgrade")
        except (ValueError, OSError, TypeError, KeyError):
            return finish("incomplete", "phase_artifact_or_marker_invalid")
        if code.get("fingerprint") != code.get("fingerprint_after"):
            return finish("ambiguous", "code_changed_during_execution")
        if mode != PHASE_MODE and (manifest.get("status") in ("running", "interrupted") or manifest.get("exit_code") is None):
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
        if mode == PHASE_MODE and obs:
            return finish("not_applicable", "phase_cannot_satisfy_required_gate")
        if code["head"] != state.head:
            return finish("stale", "head_changed")
        return finish("metadata_only", "local_artifacts_unavailable", "import_bundle")
    else:
        if any(o.get("required_gate") == "local" for o in obs):
            return finish("not_applicable", "hosted_execution_cannot_satisfy_local_gate")
        if (manifest["repository"] != repository(checkout) or code["head"] != state.head or state.entries
                or (not projection and not manifest["hosted"].get("clean"))):
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
        bindings = {o["id"]: result["result"] == "passed" and
                    gate_binding(repo, base_branch, o["id"], run_id, state.head)
                    for o in obs if o.get("required_gate") == "hosted"}
        if bindings and not all(bindings.values()):
            result["reasons"] = ["hosted_gate_binding_unconfirmed"]
    result["state"] = "verified"
    result["result"] = result["result"] or (manifest["phase_completion"]["result"] if mode == PHASE_MODE
                                          else "passed" if manifest.get("exit_code") == 0 else "failed")
    result["obligations"] = [{"id": o["id"], "impact": "unaffected",
                              "gate": "not_required" if o.get("required_gate") is None else
                              ("satisfied" if result["result"] == "passed" and
                               (kind != "hosted" or bindings.get(o["id"], False)) and
                               (o.get("required_gate") != "local" or
                                not code.get("dirty") and not state.entries) else "pending")}
                             for o in obs]
    if not obs:
        result["reasons"] = ["no_obligations_to_verify"]
    elif not any(o.get("required_gate") for o in obs):
        result["reasons"] = ["no_required_gate"]
    elif any(o["gate"] == "pending" for o in result["obligations"]) and not result["reasons"]:
        result["reasons"] = ["required_gate_not_satisfied"]
    if result["result"] == "passed" and result["obligations"] and all(
            o["gate"] in ("satisfied", "not_required") for o in result["obligations"]):
        result["recovery"]["obligations"] = []
    return result


def export_bundle(checkout, evidence_id, destination):
    directory = record_dir(checkout, evidence_id)
    manifest = load_manifest(directory)
    mode = execution_mode(manifest)
    if mode == PHASE_MODE:
        check_phase_files(manifest, directory)
        # Manifest FIRST: importer validates the complete declared set before payload.
        members = [directory / "manifest.json"] + [
            directory / name for name in sorted(phase_members(manifest) - {"manifest.json", "SHA256SUMS"})]
    else:
        log = directory / "artifacts/execution.log"
        if log.is_file():
            with log.open("rb") as stream:
                if b'"execution_mode":"inprocess-phase"' in stream.readline(16384):
                    raise ValueError("phase mode downgrade")
        # An imported directory contains the old checksum file. It describes the
        # previous archive, not a member of the newly generated one.
        members = sorted(p for p in directory.rglob("*")
                         if p.is_file() and p.relative_to(directory).as_posix() != "SHA256SUMS")
        if any(p.is_symlink() for p in directory.rglob("*")):
            raise ValueError("symlink in evidence directory")
    if any(p.is_symlink() for p in members):
        raise ValueError("symlink in evidence directory")
    sums = "".join(f"{hash_file(p)}  {p.relative_to(directory)}\n" for p in members).encode()
    with tarfile.open(destination, "w:gz") as bundle:
        for path in members:
            bundle.add(path, arcname=str(path.relative_to(directory)), recursive=False)
        info = tarfile.TarInfo("SHA256SUMS")
        info.size = len(sums)
        bundle.addfile(info, io.BytesIO(sums))
    return destination


def inspect_bundle(source):
    """Metadata pass only: decide mode/member allowlist BEFORE hashing payloads.

    Legacy member order is preserved. Phase packages have the new manifest-first
    representation; a phase hidden later is refused before copying any payload.
    """
    if source.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("bundle exceeds import size limit")
    names, total, manifest, marker = [], 0, None, False
    with source.open("rb") as compressed, gzip.GzipFile(fileobj=LimitedReader(compressed, MAX_ARCHIVE_BYTES)) as inflated, \
            tarfile.open(fileobj=LimitedReader(inflated, MAX_ARCHIVE_BYTES), mode="r|") as bundle:
        for member in bundle:
            name = member.name
            if (len(names) >= MAX_BUNDLE_MEMBERS or name in names or not member.isfile() or
                    not name or len(name) > 4096 or name.startswith(".") or Path(name).is_absolute() or
                    ".." in Path(name).parts or str(Path(name)) != name):
                raise ValueError("unsafe bundle members")
            names.append(name)
            total += member.size
            if member.size > MAX_MEMBER_BYTES or total > MAX_BUNDLE_BYTES:
                raise ValueError("bundle exceeds import size limit")
            if name == "manifest.json":
                if member.size > 4 * 1024 * 1024:
                    raise ValueError("bundle metadata exceeds import size limit")
                with bundle.extractfile(member) as stream:
                    manifest = json.load(stream)
            elif name == "artifacts/execution.log":
                with bundle.extractfile(member) as stream:
                    marker = b'"execution_mode":"inprocess-phase"' in stream.readline(16384)
    if not isinstance(manifest, dict):
        raise ValueError("bundle manifest missing")
    mode = execution_mode(manifest)
    if mode == PHASE_MODE:
        if names[0] != "manifest.json" or set(names) != phase_members(manifest):
            raise ValueError("phase manifest/member order or set invalid")
    elif marker:
        raise ValueError("phase mode downgrade")


def import_bundle(checkout, source, *, allow_existing=False):
    inspect_bundle(source)
    with tempfile.TemporaryDirectory(dir=store(checkout)) as temp:
        seen = {}
        total = 0
        phase_allowed = None
        first_name = None
        # Tarfile parses PAX extended headers before yielding a member. A size
        # check in the loop below alone cannot bound that allocation. Cap both
        # input and the entire inflated tar stream before it reaches tarfile.
        if source.stat().st_size > MAX_ARCHIVE_BYTES:
            raise ValueError("bundle exceeds import size limit")
        with source.open("rb") as compressed, gzip.GzipFile(fileobj=LimitedReader(compressed, MAX_ARCHIVE_BYTES)) as inflated, \
                tarfile.open(fileobj=LimitedReader(inflated, MAX_ARCHIVE_BYTES), mode="r|") as bundle:
            for member in bundle:
                name = member.name
                if first_name is None:
                    first_name = name
                if phase_allowed is not None and name not in phase_allowed:
                    raise ValueError("undeclared phase member")
                if (name == "manifest.json" and member.size > 4 * 1024 * 1024 or
                        name == "SHA256SUMS" and member.size > 1024 * 1024):
                    raise ValueError("bundle metadata exceeds import size limit")
                if (len(seen) >= MAX_BUNDLE_MEMBERS or name in seen or not member.isfile()
                        or len(name) > 4096 or not name or name.startswith(".") or Path(name).is_absolute()
                        or ".." in Path(name).parts or str(Path(name)) != name):
                    raise ValueError("unsafe bundle members")
                if member.size > MAX_MEMBER_BYTES or total + member.size > MAX_BUNDLE_BYTES:
                    raise ValueError("bundle exceeds import size limit")
                target = Path(temp) / name
                target.parent.mkdir(parents=True, exist_ok=True)
                digest = hashlib.sha256()
                with bundle.extractfile(member) as stream, target.open("xb") as output:
                    remaining = member.size
                    while remaining:
                        chunk = stream.read(min(remaining, 1024 * 1024))
                        if not chunk:
                            raise ValueError("truncated bundle member")
                        output.write(chunk)
                        digest.update(chunk)
                        remaining -= len(chunk)
                seen[name] = digest.hexdigest()
                total += member.size
                target.chmod(0o600)
                if name == "manifest.json":
                    declared = json.loads(target.read_text())
                    if execution_mode(declared) == PHASE_MODE:
                        if first_name != "manifest.json":
                            raise ValueError("phase manifest must precede payload")
                        phase_allowed = phase_members(declared)
                elif name == "artifacts/execution.log" and phase_allowed is None:
                    with target.open("rb") as stream:
                        if b'"execution_mode":"inprocess-phase"' in stream.readline(16384):
                            raise ValueError("phase mode downgrade")
        if "SHA256SUMS" not in seen or "manifest.json" not in seen:
            raise ValueError("unsafe bundle members")
        if (Path(temp, "SHA256SUMS").stat().st_size > 1024 * 1024 or
                Path(temp, "manifest.json").stat().st_size > 4 * 1024 * 1024):
            raise ValueError("bundle metadata exceeds import size limit")
        expected = {}
        for line in Path(temp, "SHA256SUMS").read_text().splitlines():
            match = re.fullmatch(r"([a-f0-9]{64})  (.+)", line)
            if not match or match.group(2) in expected:
                raise ValueError("invalid bundle checksums")
            expected[match.group(2)] = match.group(1)
        if set(expected) != set(seen) - {"SHA256SUMS"} or any(seen[n] != digest for n, digest in expected.items()):
            raise ValueError("bundle checksum mismatch")
        manifest = json.loads(Path(temp, "manifest.json").read_text())
        if manifest.get("schema") != SCHEMA:
            raise ValueError("unknown evidence schema")
        if execution_mode(manifest) == PHASE_MODE:
            if set(seen) != phase_allowed:
                raise ValueError("phase member set mismatch")
            check_phase_files(manifest, Path(temp))
        directory = record_dir(checkout, manifest["evidence_id"])
        if directory.exists():
            if (allow_existing and execution_mode(manifest) == PHASE_MODE and
                    load_manifest(directory) == manifest):
                check_phase_files(manifest, directory)
                return manifest["evidence_id"]  # validated roundtrip; never overwrite
            raise ValueError("evidence ID already exists; refusing overwrite")
        Path(temp).rename(directory)
    return manifest["evidence_id"]
