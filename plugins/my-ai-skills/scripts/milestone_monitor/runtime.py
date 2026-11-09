"""Adaptador oficial OpenCode 2.2.5, externo e estritamente read-only."""
import os
import re
import subprocess

from .common import MonitorError, command, identifier, iso_time, issue_identity, parse_time, utc_now
from .projection import analyze, incarnation_key


class Runtime:
    def __init__(self, config, call=command, timeout=10):
        self.config, self.call, self.timeout = config, call, timeout

    def api(self, operation, *params):
        argv = ["opencode"]
        if self.config.get("server"):
            argv += ["--server", self.config["server"]]
        return self.call(argv + ["api", operation, *params], timeout=self.timeout)

    def context(self):
        if self.call(["opencode", "--version"], timeout=self.timeout) != "2.2.5":
            raise MonitorError("contrato OpenCode incompatível")
        raw = self.api("server.info")
        if not isinstance(raw, dict) or raw.get("version") != "2.2.5" or type(raw.get("pid")) is not int:
            raise MonitorError("contrato OpenCode incompatível")
        return {"endpoint": self.config.get("server") or "shared-discovery", "version": raw["version"], "pid": raw["pid"]}

    def location(self, session_id, worktree):
        raw = self.api("session.get", "--param", "sessionID=" + session_id)
        try:
            data = raw["data"]
            directory = data["location"]["directory"]
            if data["id"] != session_id or not isinstance(data["projectID"], str) or not os.path.isabs(directory):
                raise ValueError()
            target = self.api("location.get", "--param", "location[directory]=" + worktree)
            if not isinstance(target.get("project"), dict) or not os.path.isabs(target["directory"]):
                raise ValueError()
            if os.path.realpath(directory) != worktree or os.path.realpath(target["directory"]) != worktree:
                raise MonitorError("localização incompatível")
            return {"directory": worktree, "project_id": data["projectID"]}
        except (KeyError, TypeError, ValueError, AttributeError):
            raise MonitorError("resposta inválida") from None

    def pending(self, session_id):
        result = []
        for kind, operation, prefix in (("permission", "session.permission.list", "per"),
                                        ("form", "session.form.list", "frm_")):
            raw = self.api(operation, "--param", "sessionID=" + session_id)
            if not isinstance(raw, dict) or not isinstance(raw.get("data"), list) or len(raw["data"]) > 1000:
                raise MonitorError("resposta inválida")
            seen = set()
            for item in raw["data"]:
                if not isinstance(item, dict) or item.get("sessionID") != session_id:
                    raise MonitorError("resposta inválida")
                request_id = identifier(item.get("id"))
                if not request_id.startswith(prefix) or request_id in seen:
                    raise MonitorError("resposta inválida")
                seen.add(request_id)
                result.append({"kind": kind, "request_id": request_id})
        return result

    def validate_fact(self, fact, bindings, open_keys, sample=None):
        """Um fato não é resultado semântico; revalida apenas sua correlação."""
        import json
        from .observations import normalize
        key = fact.get("binding_key")
        binding = bindings.get(key) if key in open_keys else None
        if not binding or binding.get("invalidated"):
            return None
        projected = normalize(json.dumps(fact).encode(), binding["context"], {key: binding}, fact.get("collector_epoch"))
        if not projected or projected.get("binding_key") != key:
            return None
        if sample is not None:
            # Prova de consulta oficial iniciada depois do recebimento do fato,
            # com Git/localização validados e a mesma revisão/contexto.
            started, received = parse_time(sample.get("query_started_at")), parse_time(fact.get("received_at"))
            if (sample.get("binding_revision") != binding["revision"] or sample.get("context") != binding["context"]
                    or sample.get("state") not in {"active", "inactive"} or not started or not received or started < received):
                return None
            return projected
        if self.context() != binding["context"]:
            raise MonitorError("contexto alterado")
        self.location(binding["session_id"], binding["worktree"])
        git_identity(binding["worktree"], binding["repository"], binding.get("branch"))
        return projected

    def project_facts(self, store, open_keys, epoch):
        source = store.source("runtime")
        if source.get("error"):
            return
        samples, bindings = source.get("payload") or {}, store.bindings()
        for fact in store.runtime_facts():
            if (not isinstance(fact, dict) or fact.get("version") != 1 or fact.get("projected")
                    or fact.get("collector_epoch") != epoch or fact.get("binding_key") not in open_keys):
                continue
            sample = samples.get(fact["binding_key"], {})
            if sample.get("collector_epoch") != epoch:
                continue
            validated = self.validate_fact(fact, bindings, open_keys, sample)
            if validated:
                store.project_runtime_fact(validated, epoch)

    def collect(self, bindings, open_keys):
        bindings = {key: value for key, value in bindings.items() if key in open_keys}
        if not bindings:
            return {}
        query_started = utc_now().isoformat()
        context = self.context()
        raw = self.api("session.active")
        if not isinstance(raw, dict) or not isinstance(raw.get("data"), dict):
            raise MonitorError("resposta inválida")
        active = raw["data"]
        result = {}
        for key, binding in bindings.items():
            if key not in open_keys:
                continue
            state = "unknown"
            requests = []
            try:
                if binding.get("invalidated"):
                    state = binding["invalidated"]
                elif binding["context"] != context:
                    state = "context_changed"
                else:
                    # Always revalidate location, including a session still running.
                    self.location(binding["session_id"], binding["worktree"])
                    git_identity(binding["worktree"], binding["repository"], binding.get("branch"))
                    item = active.get(binding["session_id"])
                    if item is not None and (not isinstance(item, dict) or item.get("type") != "running"):
                        raise MonitorError("resposta inválida")
                    state = "active" if item else "inactive"
                    requests = self.pending(binding["session_id"])
            except MonitorError as error:
                if error.category == "ausente":
                    state = "absent"
                elif error.category in {"localização incompatível", "worktree incompatível", "branch incompatível"}:
                    state = "incompatible"
                else:
                    raise
            result[key] = {"state": state, "at": utc_now().isoformat(), "binding_revision": binding.get("revision"),
                           "query_started_at": query_started, "requests": requests, "context": context}
        return result


def git_identity(worktree, repo, branch=None):
    def git(*args):
        try:
            p = subprocess.run(["git", "-C", worktree, *args], capture_output=True, text=True, timeout=10,
                               env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
            if p.returncode:
                raise MonitorError("worktree incompatível")
            return p.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            raise MonitorError("worktree incompatível") from None
    if os.path.realpath(git("rev-parse", "--show-toplevel")) != worktree:
        raise MonitorError("worktree incompatível")
    remote = git("remote", "get-url", "origin")
    match = re.fullmatch(r"(?:git@github.com:|https://github.com/)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?", remote)
    if not match or match[1].lower() != repo.lower():
        raise MonitorError("worktree incompatível")
    actual_branch = git("branch", "--show-current")
    if branch is not None and actual_branch != branch:
        raise MonitorError("branch incompatível")
    return actual_branch or None


def find_incarnation(store, repo, number, run_id, stage, worker_id, execution_kind, execution_id):
    snapshots = store.source(f"comments:{repo}:{number}").get("payload") or []
    runs = [s["record"] for s in snapshots if s["record"]["run_id"] == run_id]
    if len(runs) != 1 or runs[0].get("finished_at"):
        raise MonitorError("run ausente, terminal ou ambíguo")
    _summary, details = analyze(runs[0])
    matches = [i for i in details["intervals"] if i["stage"] == stage and i["worker_id"] == worker_id
               and i["execution"] == {"kind": execution_kind, "id": execution_id} and not i["closed_at"] and not i["terminal"]]
    if len(matches) != 1:
        raise MonitorError("incarnação ausente, terminal ou ambígua")
    return matches[0]


def bind(store, runtime, args):
    if not runtime.config.get("enabled"):
        raise MonitorError("runtime desabilitado")
    repo, number = issue_identity(args.issue)
    for key in ("run_id", "stage", "worker_id", "execution_id", "session_id"):
        identifier(getattr(args, key))
    if not args.session_id.startswith("ses"):
        raise MonitorError("sessão inválida")
    inventory_source = store.source("inventory:" + repo)
    comments_source = store.source(f"comments:{repo}:{number}")
    inventory = inventory_source.get("payload") or {}
    if not any(i["number"] == number for i in inventory.get("issues", [])):
        raise MonitorError("issue ausente do inventário")
    interval = find_incarnation(store, repo, number, args.run_id, args.stage, args.worker_id, args.execution_kind, args.execution_id)
    worktree = os.path.realpath(args.worktree)
    branch = git_identity(worktree, repo, args.branch)
    context = runtime.context()
    runtime.location(args.session_id, worktree)
    key = incarnation_key(repo, number, args.run_id, interval)
    store.bind(key, {"repository": repo, "issue": number, "run_id": args.run_id, "stage": args.stage,
                     "worker_id": args.worker_id, "execution": interval["execution"], "session_id": args.session_id,
                      "worktree": worktree, "branch": branch, "context": context, "bound_at": utc_now().isoformat()},
               guards=(("inventory:" + repo, inventory_source.get("accepted")),
                       (f"comments:{repo}:{number}", comments_source.get("accepted"))))
    return key
