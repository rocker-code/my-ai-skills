#!/usr/bin/env python3
"""Explicit OFFLINE native V2 shell-executor proof. Never submits a model prompt.

Run: python3 -B tests/smoke_resume_shell_guard_native.py
The temporary command bridge invokes the real built-in shell executor returned
by the documented ctx.tool.list() API, not a mock or a Python authorization
function. It bypasses the generic tool dispatcher; the shell.create.before hook
is exercised INSIDE that native executor before scanner/permission/spawn.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile

from smoke_resume_candidate_opencode import (
    disposable_shell_guard, read_only_permissions, sha, shell_guard_preflight, redact)


BRIDGE = r'''
import fs from "node:fs";
export default {
  id: "issue61.offline-executor-proof",
  async setup(ctx) {
    // Unexpected generation fails before dispatch. No prompt is ever submitted.
    for (const name of ["context", "generate", "title", "compaction"]) {
      await ctx.session.hook(name, () => { throw new Error("offline proof: no inference"); });
    }
    await ctx.command.transform((editor) => editor.add({
      name: "fixture-shell-proof",
      execute: async ({sessionID}) => {
        const inputs = JSON.parse(fs.readFileSync(ctx.options.inputs, "utf8"));
        const audit = fs.readFileSync(ctx.options.audit, "utf8").trim().split("\n").map(JSON.parse);
        if (!audit.some((e) => e.boundary === "setup" && e.decision === "active")) {
          throw new Error("native guard missing; no shell invocation");
        }
        const session = await ctx.session.get({sessionID});
        const tools = await ctx.tool.list();
        const shell = tools.find((tool) => tool.id === "shell");
        if (!shell || typeof shell.execute !== "function") throw new Error("native shell absent");
        const results = [];
        for (const [index, input] of inputs.entries()) {
          const progress = [];
          try {
            const result = await shell.execute(input, {
              sessionID, agent: session.agent ?? "build", messageID: "msg_offline_fixture",
              id: `fixture-${index}`, signal: new AbortController().signal,
              progress: async (update) => { progress.push(update); },
            });
            results.push({input, result, progress, status: "completed"});
          } catch (error) {
            results.push({input, progress, status: "rejected", error: String(error)});
          }
        }
        fs.writeFileSync(ctx.options.output, JSON.stringify({
          sessionID, toolID: shell.id, results,
        }, null, 2));
      },
    }));
  },
};
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="new disposable directory to retain proof")
    args = parser.parse_args()
    cli = shutil.which("opencode")
    if not cli:
        raise RuntimeError("installed OpenCode V2 required; no inference fallback")
    base = args.output_dir
    if base is None:
        base = Path(tempfile.mkdtemp(prefix="issue61-native-rawguard-", dir="/tmp/opencode"))
    else:
        base = base.resolve()
        if not base.is_relative_to(Path("/tmp/opencode")):
            raise RuntimeError("native proof must remain under /tmp/opencode")
        base.mkdir(exist_ok=False)
    print(f"disposable proof directory: {base}", flush=True)
    home, repo = base / "home", base / "repo"
    home.mkdir()
    repo.mkdir()
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8",
           "XDG_CONFIG_HOME": str(home / ".config"),
           "XDG_DATA_HOME": str(home / ".local/share"),
           "XDG_CACHE_HOME": str(home / ".cache"),
           "XDG_STATE_HOME": str(home / ".local/state"),
           "OPENCODE_DB": str(base / "opencode.db"), "OPENCODE_PASSWORD": secrets.token_hex(24),
           "PYTHONDONTWRITEBYTECODE": "1"}
    operator_env_before = dict(os.environ)

    def command(args, cwd=repo):
        result = subprocess.run([str(a) for a in args], cwd=cwd, env=env,
                                capture_output=True, text=True, timeout=120)
        # Retain every native response locally, but never print/store credentials.
        return result

    def checked(args):
        result = command(args)
        if result.returncode:
            raise RuntimeError(f"{args[:4]}: {result.stderr[:2000]}")
        return result.stdout

    checked(["git", "init", "-q"])
    (repo / "tracked").write_text("unchanged\n")
    checked(["git", "add", "tracked"])
    checked(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
             "commit", "-qm", "fixture"])
    marker, hook = base / "hook-executed", base / "harmless-fsmonitor"
    hook.write_text(f"#!/bin/sh\nprintf 'harmless hook executed\\n' >> '{marker}'\nprintf '\\n'\n")
    hook.chmod(0o700)
    exploit = ("export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor "
               f"GIT_CONFIG_VALUE_0={hook}; git status --short")
    control = command(["/bin/sh", "-c", exploit])
    assert control.returncode == 0 and marker.read_text() == "harmless hook executed\n"
    marker.rename(base / "positive-control-hook-executed")
    (base / "positive-control.json").write_text(json.dumps({
        "command": exploit, "exit": control.returncode, "stdout": control.stdout,
        "stderr": control.stderr, "hook_sha256": sha(hook)}))

    permissions = read_only_permissions(repo, [], base / "read-receipt", {}, repo)
    guard = disposable_shell_guard(base / "guard", repo, [], permissions, env)
    bridge = base / "bridge"
    bridge.mkdir()
    (bridge / "index.mjs").write_text(BRIDGE)
    inputs = [
        {"command": "git status --short", "workdir": str(repo)},
        {"command": exploit, "workdir": str(repo)},
        {"command": f"GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0={hook} git status --short"},
        {"command": f"env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0={hook} git status --short"},
        {"command": "declare -x GIT_CONFIG_COUNT=1; git status --short"},
        {"command": "readonly GIT_CONFIG_COUNT=1; git status --short"},
        {"command": "set -a; GIT_CONFIG_COUNT=1; git status --short"},
        {"command": "git status --short; pwd"},
        {"command": "$(printf git) status --short"},
        {"command": "git status --short", "workdir": str(base)},
        {"command": "git status --short --ignored", "workdir": str(repo)},
    ]
    input_path, output = base / "inputs.json", base / "native-results.json"
    input_path.write_text(json.dumps(inputs))
    env["OPENCODE_CONFIG_CONTENT"] = json.dumps({
        "$schema": "https://opencode.ai/config.json", "permissions": permissions,
        "plugins": [guard["plugin"], {"package": str(bridge),
                                    "options": {"inputs": str(input_path), "output": str(output),
                                                "audit": guard["audit"]}}]})
    version = checked([cli, "--version"]).strip()
    assert version == "opencode v2.3.2", f"review native API/source before using another runtime: {version}"
    shell_guard_preflight(cli, repo, env, guard)

    def api(method, path, data=None):
        args = [cli, "api", "--standalone", method, path]
        if data is not None:
            args += ["--data", json.dumps(data)]
        result = command(args)
        index = len(list(base.glob("api-*-terminal.json")))
        (base / f"api-{index}-terminal.json").write_text(json.dumps({
            "method": method, "path": path, "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}))
        if result.returncode:
            raise RuntimeError(f"native API {path}: {result.stderr[:2000]}")
        value = json.loads(result.stdout) if result.stdout.strip() else None
        return value["data"] if isinstance(value, dict) and set(value) == {"data"} else value

    openapi = api("get", "/openapi.json")
    assert "/api/session/{sessionID}/command" in openapi["paths"]
    created = api("post", "/api/session", {"title": "Offline native shell guard proof",
                  "agent": "build", "location": {"directory": str(repo)}, "permissions": permissions})
    session = created["id"]
    before = {str(p.relative_to(repo)): sha(p) for p in repo.rglob("*") if p.is_file()}
    api("post", f"/api/session/{session}/command", {"name": "fixture-shell-proof", "text": ""})
    result = json.loads(output.read_text())
    assert result["sessionID"] == session and result["toolID"] == "shell"
    results = result["results"]
    assert results[0]["status"] == "completed", results[0]
    assert results[0]["result"]["output"]["exitCode"] == 0, results[0]
    assert all(r["status"] == "rejected" and not r["progress"] for r in results[1:]), results
    assert not marker.exists(), "rejected raw command executed the fsmonitor hook"
    assert before == {str(p.relative_to(repo)): sha(p) for p in repo.rglob("*") if p.is_file()}
    assert operator_env_before == dict(os.environ)
    audit = [json.loads(line) for line in Path(guard["audit"]).read_text().splitlines()]
    checks = [a for a in audit if a["boundary"] == "shell.create.before"]
    assert len(checks) == len(inputs), checks
    assert checks[0]["decision"] == "allow"
    assert all(a["decision"] == "deny" for a in checks[1:])
    assert checks[1]["command"] == exploit
    state = api("get", f"/api/session/{session}")
    assert state["cost"] == 0
    messages = api("get", f"/api/session/{session}/message")
    assert messages["data"] == []
    assert all(value == 0 for key, value in state["tokens"].items() if key != "cache")
    assert all(value == 0 for value in state["tokens"]["cache"].values())
    proof = {
        "runtime": version, "session": session, "guard": guard,
        "native_executor": "ctx.tool.list().find(id=shell).execute",
        "bridge_sha256": sha(bridge / "index.mjs"), "allowed": 1, "rejected": len(inputs) - 1,
        "hook_calls": len(checks), "hook_marker_absent": True, "repo_bytes_unchanged": True,
        "operator_env_unchanged": True, "cost": state["cost"], "messages": messages,
        "limitation": "native executor via command bridge, not model-driven tool dispatcher",
    }
    (base / "proof.json").write_text(json.dumps(proof, indent=2))
    # workflow-evidence keeps stdout checksum-bound in the Git common dir.
    # Do not bypass its checkout-only artifact policy to attach /tmp files.
    print(json.dumps({"proof_metadata": proof, "native_results": result, "audit": audit,
                      "positive_control": json.loads((base / "positive-control.json").read_text()),
                      "guard_source": Path(guard["source"]).read_text(),
                      "bridge_source": (bridge / "index.mjs").read_text(),
                      "policy": json.loads(Path(guard["policy"]).read_text()),
                      "native_log": redact((home / ".local/share/opencode/log/opencode.log").read_text(), env)}))
    print(json.dumps({"proof": str(base / "proof.json"), "native_allowed": 1,
                      "native_rejected": len(inputs) - 1, "inference": "NOT RUN"}))


if __name__ == "__main__":
    main()
