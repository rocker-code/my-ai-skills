"""Cooperative checkout reservation and canonical code-state fingerprint (v1).

Public API: FINGERPRINT_VERSION, SAFE_ID, KNOWN_GENERATED_PATTERNS,
is_known_generated, code_state, drift_report, IndexEntry, PathEntry, CodeState.
Changing the digest's canonical payload requires a new fingerprint version.
"""

from __future__ import annotations

import contextlib
import fnmatch
import hashlib
import importlib.util
import json
import os
import re
import secrets
import socket
import stat
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - POSIX is required for mutations
    fcntl = None

FINGERPRINT_VERSION = "v1"
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
KNOWN_GENERATED_PATTERNS = ("__pycache__/", "*.pyc", "*.pyo")
STATES = {"RESERVED", "ACTIVE", "WAITING", "HANDOFF", "RETAINED", "CLEANUP_ELIGIBLE", "RECOVERY_REQUIRED", "REMOVED"}
PROVENANCE_LIMIT = 256


class ReservationError(Exception):
    def __init__(self, code: int, message: str, *, entry=None, drift=None, inventory=None):
        super().__init__(message)
        self.code, self.entry, self.drift, self.inventory = code, entry, drift, inventory


def _git(checkout, *args: str, check=True, return_code=False) -> bytes | int:
    """All Git inspection goes through this read-only, no-optional-locks gate."""
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(checkout), *args],
                            capture_output=True, env=env)
    if check and result.returncode:
        raise ReservationError(6, result.stderr.decode(errors="replace").strip() or "Git inspection failed")
    if return_code:
        return result.returncode
    return result.stdout if result.returncode == 0 else b""


def _is_ancestor(checkout, old, new):
    return _git(checkout, "merge-base", "--is-ancestor", old, new, check=False, return_code=True) == 0


def _text(checkout, *args, check=True):
    return _git(checkout, *args, check=check).decode("utf-8", "surrogateescape").strip()


def identity(checkout):
    checkout = Path(checkout).resolve(strict=True)
    common = Path(_text(checkout, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    git_dir = Path(_text(checkout, "rev-parse", "--path-format=absolute", "--git-dir")).resolve()
    remote = _text(checkout, "remote", "get-url", "origin", check=False)
    branch = _text(checkout, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    return {"path": str(checkout), "common_dir": str(common), "remote": remote,
            "branch": branch, "primary": common == git_dir}


def is_known_generated(rel_path: str) -> bool:
    # A cache directory can contain user files; only bytecode is generated.
    return rel_path.endswith((".pyc", ".pyo"))


@dataclass(frozen=True)
class IndexEntry:
    stage: int
    mode: str
    oid: str


@dataclass(frozen=True)
class PathEntry:
    path: str
    status: str
    sha256: str | None
    deleted: bool
    index: tuple[IndexEntry, ...]


@dataclass(frozen=True)
class CodeState:
    head: str | None
    digest: str
    entries: tuple[PathEntry, ...]
    generated: tuple[str, ...]

    def to_json(self):
        return asdict(self)


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value) -> bytes:
    # Preserve the existing UTF-8 payload for normal names while retaining
    # Git's undecodable filename bytes represented by surrogateescape.
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8", "surrogateescape")


def _matching(path, patterns):
    return any(fnmatch.fnmatchcase(path, pattern) or path == pattern for pattern in patterns)


def _file_hash(path: Path):
    try:
        if path.is_symlink():
            return _hash(os.readlink(path).encode("utf-8", "surrogateescape"))
        with path.open("rb") as stream:
            digest = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
            return digest.hexdigest()
    except FileNotFoundError:
        return None


def _status(checkout):
    raw = _git(checkout, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored=matching")
    items = raw.split(b"\0")
    result = {}
    n = 0
    while n < len(items) and items[n]:
        record = items[n]
        status = record[:2].decode("ascii")
        path = record[3:].decode("utf-8", "surrogateescape")
        # Git coalesces ignored __pycache__/ directories even with
        # --ignored=matching. Inspect only this directory, including unknown
        # files; never recurse into unrelated ignored trees such as .venv/.
        if status == "!!" and path.rstrip("/").split("/")[-1] == "__pycache__":
            directory = Path(checkout) / path
            if directory.is_dir() and not directory.is_symlink():
                for child in directory.rglob("*"):
                    if not (child.is_file() or child.is_symlink()):
                        continue
                    rel = str(child.relative_to(checkout))
                    if not is_known_generated(rel) or _safe_file(checkout, rel):
                        result[rel] = "!!"
        else:
            result[path] = status
        n += 2 if "R" in status or "C" in status else 1
    return result


def code_state(checkout, *, exclude_paths=(), include_ignored=()) -> CodeState:
    checkout = Path(checkout)
    head = _text(checkout, "rev-parse", "--verify", "HEAD", check=False) or None
    index = {}
    for row in _git(checkout, "ls-files", "--stage", "-z").split(b"\0"):
        if not row:
            continue
        meta, path = row.split(b"\t", 1)
        mode, oid, stage = meta.decode().split()
        index.setdefault(path.decode("utf-8", "surrogateescape"), []).append(IndexEntry(int(stage), mode, oid))
    statuses = _status(checkout)
    for declared in include_ignored:
        if Path(declared).is_absolute() or ".." in Path(declared).parts:
            raise ValueError("include_ignored requires relative checkout paths")
        paths = checkout.glob(declared) if any(ch in declared for ch in "*?[") else (checkout / declared,)
        for candidate in paths:
            relative = str(candidate.relative_to(checkout))
            if relative not in statuses and candidate.is_file() and _git(checkout, "check-ignore", "-v", "--", relative, check=False):
                statuses[relative] = "!!"
    generated = []
    entries = []
    for path, xy in sorted(statuses.items()):
        if (xy == "!!" and not _matching(path, include_ignored) and
                not is_known_generated(path) and "__pycache__" not in Path(path).parts):
            continue
        if is_known_generated(path) and xy in ("??", "!!"):
            generated.append(path)
            continue
        if _matching(path, exclude_paths):
            continue
        file_path = checkout / path
        if file_path.is_dir() and not file_path.is_symlink():  # never hash directories
            continue
        sha = _file_hash(file_path)
        entries.append(PathEntry(path, xy, sha, sha is None,
                                 tuple(sorted(index.get(path, ()), key=lambda item: item.stage))))
    payload = {"v": FINGERPRINT_VERSION, "head": head,
               "entries": [asdict(item) for item in entries]}
    return CodeState(head, "sha256:v1:" + _hash(_canonical(payload)), tuple(entries), tuple(generated))


def drift_report(baseline: CodeState | dict, current: CodeState, *, checkout) -> dict | None:
    old = baseline.to_json() if isinstance(baseline, CodeState) else baseline
    if old["head"] == current.head and old["digest"] == current.digest:
        return None
    before = {item["path"]: item for item in old["entries"]}
    after = {item.path: asdict(item) for item in current.entries}
    old_head, new_head = old["head"], current.head
    commits, committed, diverged = [], [], False
    if old_head and new_head:
        commits = _text(checkout, "log", "--format=%H", f"{old_head}..{new_head}", check=False).splitlines()
        committed = _git(checkout, "diff", "--name-only", "-z", old_head, new_head, check=False)
        committed = [p.decode("utf-8", "surrogateescape") for p in committed.split(b"\0") if p]
        diverged = not _is_ancestor(checkout, old_head, new_head)
    return {"head_before": old_head, "head_after": new_head, "commits": commits,
            "diverged": diverged, "committed_paths": committed,
            "changed_paths": sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p)),
            "detected_at": datetime.now(timezone.utc).isoformat()}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _invalid(label):
    raise ReservationError(7, f"Invalid registry {label}; preserve it for review")


def _fields(obj, types, label):
    """Missing fields are recoverable; present fields must have their declared shape."""
    if not isinstance(obj, dict):
        _invalid(label)
    for key, valid in types.items():
        if key in obj and not valid(obj[key]):
            _invalid(f"{label} {key}")


def _optional(valid):
    return lambda value: value is None or valid(value)


def _string(value):
    return isinstance(value, str)


def _number(value):
    return type(value) is int and value >= 0


def _hex(value):
    return _string(value) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _digest(value):
    return _string(value) and re.fullmatch(r"sha256:v1:[0-9a-f]{64}", value) is not None


def _oid(value):
    return _string(value) and re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value) is not None


def _owner_shape(owner):
    _fields(owner, {"session": _string, "run": _string, "stage": _string,
                    "host": _string, "pid": _optional(lambda v: _number(v) and v > 0)}, "owner")


def _baseline_shape(baseline):
    _fields(baseline, {"head": _optional(_oid), "digest": _digest,
                       "entries": lambda v: isinstance(v, list),
                       "generated": lambda v: isinstance(v, list) and all(_string(p) for p in v)}, "baseline")
    seen = set()
    for item in baseline.get("entries", []):
        _fields(item, {"path": lambda v: _string(v) and bool(v) and not Path(v).is_absolute() and
                       not any(part in (".", "..") for part in Path(v).parts),
                       "status": lambda v: _string(v) and len(v) == 2,
                       "sha256": _optional(_hex), "deleted": lambda v: type(v) is bool,
                       "index": lambda v: isinstance(v, list)}, "baseline entry")
        if "path" in item:
            if item["path"] in seen:
                _invalid("duplicate baseline path")
            seen.add(item["path"])
        for index in item.get("index", []):
            _fields(index, {"stage": lambda v: _number(v) and v <= 3,
                            "mode": lambda v: _string(v) and re.fullmatch(r"[0-7]{6}", v) is not None,
                            "oid": _oid}, "baseline index entry")
    # The digest is the canonical v1 payload, not a claim supplied by the registry.
    if _baseline_complete(baseline):
        payload = {"v": FINGERPRINT_VERSION, "head": baseline["head"], "entries": baseline["entries"]}
        if baseline["digest"] != "sha256:v1:" + _hash(_canonical(payload)):
            _invalid("baseline digest")


def _baseline_complete(baseline):
    return ({"head", "digest", "entries"} <= baseline.keys() and
            all(isinstance(item, dict) and {"path", "status", "sha256", "deleted", "index"} <= item.keys()
                and all(isinstance(index, dict) and {"stage", "mode", "oid"} <= index.keys()
                        for index in item["index"]) for item in baseline["entries"]))


def _owner_complete(owner):
    return owner is None or {"session", "run", "stage", "host", "pid"} <= owner.keys()


def _drift_complete(report):
    return report is None or {"head_before", "head_after", "commits", "diverged", "committed_paths", "changed_paths", "detected_at"} <= report.keys()


def _validate_registry(reg, repo):
    if (not isinstance(reg, dict) or type(reg.get("schema_version")) is not int or
            reg["schema_version"] != 1 or not isinstance(reg.get("entries"), list)):
        raise ReservationError(7, "Invalid registry schema; review and reconstruct ownership explicitly")
    if "repository" in reg:
        _fields(reg["repository"], {"remote": _string, "common_dir": _string}, "repository identity")
    if reg.get("repository") != repo:
        raise ReservationError(6, "Registry repository identity differs")
    active_paths = set()
    active_issues = set()
    for entry in reg["entries"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ReservationError(7, "Invalid registry entry")
        if not Path(entry["path"]).is_absolute():
            raise ReservationError(7, "Registry path must be absolute")
        _fields(entry, {"issue_url": _optional(_string), "branch": _string,
                        "base_sha": _optional(_string), "proposal_sha": _optional(_string),
                        "pr_url": _optional(_string), "pr_head": _optional(_string),
                        "sandbox": _optional(_string), "state": lambda v: _string(v) and v in STATES,
                        "last_verified_at": _optional(_string), "owner": _optional(lambda v: isinstance(v, dict)),
                        "baseline": _optional(lambda v: isinstance(v, dict)),
                        "drift": _optional(lambda v: isinstance(v, dict)),
                        "recovery": _optional(lambda v: isinstance(v, dict)),
                        "verified_for": _optional(lambda v: isinstance(v, dict)),
                        "history": lambda v: isinstance(v, list)}, "entry")
        if isinstance(entry.get("owner"), dict):
            _owner_shape(entry["owner"])
        if isinstance(entry.get("baseline"), dict):
            _baseline_shape(entry["baseline"])
        if isinstance(entry.get("verified_for"), dict):
            _fields(entry["verified_for"], {"session": _string, "digest": _digest}, "verification receipt")
        if isinstance(entry.get("drift"), dict):
            _fields(entry["drift"], {"head_before": _optional(_string), "head_after": _optional(_string),
                                     "commits": lambda v: isinstance(v, list) and all(_string(p) for p in v),
                                     "diverged": lambda v: type(v) is bool,
                                     "committed_paths": lambda v: isinstance(v, list) and all(_string(p) for p in v),
                                     "changed_paths": lambda v: isinstance(v, list) and all(_string(p) for p in v),
                                     "detected_at": _string}, "drift report")
        if isinstance(entry.get("recovery"), dict):
            recovery = entry["recovery"]
            _fields(recovery, {"reason": _string, "expected_owner": _string,
                               "prior_owner": _optional(lambda v: isinstance(v, dict)),
                               "inventory_digest": _digest}, "recovery record")
            if isinstance(recovery.get("prior_owner"), dict):
                _owner_shape(recovery["prior_owner"])
        for record in entry.get("history", []):
            _fields(record, {"at": _string, "event": _string, "session": _optional(_string),
                             "detail": lambda v: isinstance(v, dict)}, "entry history record")
        if entry.get("state") != "REMOVED":
            if entry["path"] in active_paths:
                raise ReservationError(7, "Duplicate active checkout entries in registry")
            active_paths.add(entry["path"])
            issue = entry.get("issue_url")
            if issue is not None:
                if issue in active_issues:
                    raise ReservationError(7, "Duplicate active issue entries in registry")
                active_issues.add(issue)
        if "generated_provenance" in entry:
            provenance = entry["generated_provenance"]
            if not isinstance(provenance, list) or len(provenance) > PROVENANCE_LIMIT or any(
                not isinstance(item, dict) or set(item) != {"path", "sha256", "dev", "ino", "uid", "mode", "size", "mtime_ns", "ctime_ns", "execution_ref", "session", "run"}
                or not isinstance(item.get("path"), str) or not item["path"]
                or Path(item["path"]).is_absolute() or ".." in Path(item["path"]).parts
                or not _hex(item.get("sha256"))
                or any(not _number(item[key]) for key in ("dev", "ino", "uid", "mode", "size", "mtime_ns", "ctime_ns"))
                or any(not isinstance(item[key], str) for key in ("execution_ref", "session", "run"))
                for item in provenance
            ):
                raise ReservationError(7, "Invalid generated provenance")
    return reg


def _complete(entry):
    keys = {"path", "issue_url", "branch", "base_sha", "owner", "state", "baseline", "drift", "recovery", "last_verified_at", "verified_for", "history"}
    if not keys <= entry.keys() or entry["state"] not in STATES or not isinstance(entry["history"], list):
        return False
    if entry["state"] == "RESERVED" and (entry["baseline"] is not None or
        not isinstance(entry["owner"], dict)):
        return False
    if entry["state"] not in ("RESERVED", "REMOVED") and not isinstance(entry["baseline"], dict):
        return False
    if entry["baseline"] is not None and not _baseline_complete(entry["baseline"]):
        return False
    if entry["state"] == "RECOVERY_REQUIRED" and entry.get("recovery") is None:
        return False
    if entry.get("recovery") is not None and (
        not {"reason", "expected_owner", "prior_owner", "inventory_digest"} <= entry["recovery"].keys()):
        return False
    if not _drift_complete(entry["drift"]):
        return False
    if entry.get("verified_for") is not None and not {"session", "digest"} <= entry["verified_for"].keys():
        return False
    owner = entry["owner"]
    return _owner_complete(owner)


@contextlib.contextmanager
def locked(common, remote, timeout=10):
    if fcntl is None:
        raise ReservationError(5, "fcntl unavailable; no reservation granted")
    directory = Path(common) / "ai-workflow"
    directory.mkdir(exist_ok=True)
    with (directory / "worktrees.lock").open("a+b") as lock:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise ReservationError(5, "Reservation lock timed out")
                time.sleep(.05)
        try:
            path = directory / "worktrees.json"
            repo = {"remote": remote, "common_dir": str(common)}
            try:
                reg = _validate_registry(json.loads(path.read_text()), repo)
            except FileNotFoundError:
                reg = {"schema_version": 1, "repository": repo, "entries": []}
            except (ValueError, TypeError) as exc:
                raise ReservationError(7, "Invalid registry JSON; preserve it and reconstruct verified ownership") from exc
            yield reg, path
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def save(reg, path):
    fd, temp = tempfile.mkstemp(prefix=".worktrees-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(reg, stream, sort_keys=True, ensure_ascii=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def _history(entry, event, session=None, **detail):
    entry.setdefault("history", []).append({"at": _now(), "event": event,
                                            "session": session, "detail": detail})
    entry["history"] = entry["history"][-50:]


def _owner(session, run, stage="apply", pid=None):
    return {"session": session, "run": run, "stage": stage, "host": socket.gethostname(), "pid": pid}


def _entry(path, issue, branch, base, owner, state, baseline):
    return {"path": path, "issue_url": issue, "branch": branch, "base_sha": base,
            "proposal_sha": None, "pr_url": None, "pr_head": None, "owner": owner,
            "state": state, "sandbox": None, "baseline": baseline, "drift": None,
            "recovery": None, "last_verified_at": None, "verified_for": None,
            "generated_provenance": [], "history": []}


def _inventory(anchor, target, ident=None, state=None):
    listing = _text(anchor, "worktree", "list", "--porcelain")
    payload = {"worktrees": listing, "path": str(target), "identity": ident,
               "code_state": state.to_json() if state else None,
               "unknown_untracked_paths": [e.path for e in state.entries if e.status in ("??", "!!")] if state else []}
    payload["digest"] = "sha256:v1:" + _hash(_canonical(payload))
    return payload


def _recover(reg, path, ident, current, previous=None, anchor=None):
    entry = previous or _entry(path, None, ident["branch"], current.head, None, "RECOVERY_REQUIRED", current.to_json())
    prior = entry.get("owner")
    inventory = _inventory(anchor or path, path, ident, current)
    entry.update(state="RECOVERY_REQUIRED", owner=None, baseline=current.to_json(),
                 drift=None, verified_for=None, generated_provenance=[],
                 recovery={"reason": "incomplete entry" if previous else "registry/entry absent",
                           "expected_owner": prior["session"] if isinstance(prior, dict) and prior.get("session") else "unknown",
                           "prior_owner": prior, "inventory_digest": inventory["digest"]})
    entry["branch"] = ident["branch"]
    _history(entry, "recovery_required", inventory_digest=inventory["digest"])
    if previous is None:
        reg["entries"].append(entry)
    return entry, inventory


def _check_identity(entry, ident, path):
    if ident["path"] != path or ident["branch"] != entry["branch"]:
        raise ReservationError(6, "Checkout path or branch differs from reservation", entry=entry)


def _check_owner(entry, session):
    if entry["state"] == "RECOVERY_REQUIRED":
        raise ReservationError(3, "Recovery required: review inventory and stopped-writer evidence", entry=entry)
    if entry["state"] == "RESERVED":
        raise ReservationError(3, "Activate the planned checkout before writing", entry=entry)
    if not entry["owner"] or entry["owner"]["session"] != session:
        raise ReservationError(3, "Checkout owned by another session", entry=entry)


def _drift(entry, current, checkout, persist=True):
    report = entry.get("drift") or drift_report(entry["baseline"], current, checkout=checkout)
    if report:
        if persist:
            entry["drift"] = report
            entry["verified_for"] = None
        raise ReservationError(4, "Code state differs from checkpoint; explicit acceptance required", entry=entry, drift=report)


def _receipt(entry, session):
    if entry.get("verified_for") != {"session": session, "digest": entry["baseline"]["digest"]}:
        raise ReservationError(3, "Verify the current baseline before writing/checkpointing", entry=entry)


def _safe_file(checkout, rel):
    p = Path(rel)
    if p.is_absolute() or not p.parts or any(part in ("..", ".") for part in p.parts):
        return None
    path = Path(checkout)
    for part in p.parts[:-1]:
        path /= part
        if path.is_symlink() or not path.is_dir():
            return None
    path /= p.parts[-1]
    if path.is_symlink() or not path.is_file():
        return None
    # Never traverse an ignored ancestor (for example .venv or node_modules).
    for i in range(1, len(p.parts)):
        prefix = str(Path(*p.parts[:i]))
        if p.parts[i - 1] != "__pycache__" and _git(checkout, "check-ignore", "-v", prefix, check=False):
            return None
    return path


def _metadata(path):
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode):
        raise ValueError("not a regular file")
    return {"sha256": _file_hash(path), "dev": st.st_dev, "ino": st.st_ino,
            "uid": st.st_uid, "mode": st.st_mode, "size": st.st_size,
            "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns}


def _fd_metadata(fd):
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode):
        raise ValueError("not a regular file")
    digest = hashlib.sha256()
    os.lseek(fd, 0, os.SEEK_SET)
    for chunk in iter(lambda: os.read(fd, 1024 * 1024), b""):
        digest.update(chunk)
    return {"sha256": digest.hexdigest(), "dev": st.st_dev, "ino": st.st_ino,
            "uid": st.st_uid, "mode": st.st_mode, "size": st.st_size,
            "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns}


def _magic(path):
    with path.open("rb") as stream:
        return stream.read(4) == importlib.util.MAGIC_NUMBER


def _bytecodes(checkout):
    result = {}
    for path, xy in _status(checkout).items():
        if xy not in ("??", "!!") or not path.endswith((".pyc", ".pyo")):
            continue
        file = _safe_file(checkout, path)
        if file:
            result[path] = _metadata(file)
    return result


def _pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
