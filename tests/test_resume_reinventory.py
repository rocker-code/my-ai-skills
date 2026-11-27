"""Offline regression for the T7 same-session, pre-native reinventory gate."""
from contextlib import closing, contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
import json
import importlib.util
import copy
import hashlib
import fcntl
import os
from pathlib import Path
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile
import termios
import time
import select
import signal
import sqlite3
import unittest
from unittest.mock import patch
from unittest.mock import Mock

from smoke_resume_candidate_opencode import (disposable_opencode_shim,
                                              disposable_path, t7_phase1_proof,
                                              t7_reinventory, t7_visible_question,
                                              native_calls, contract_source, CHANGE,
                                              RUNTIME_READER, inventory, sha,
                                              read_only_permissions, prepared_phase,
                                              execute_model, ModelExecutionError,
                                              model_preflight, t5_sources,
                                              seed_proposal_review, t1_proposal_proof,
                                              t1_apply_gate_proof, t1_inspection_sources,
                                              t1_native_inspection, ROOT,
                                              t1_handoff, catalog_discovery,
                                              delivered_skill_catalog, forbidden_attempts,
                                              read_only_locators, disposable_shell_guard,
                                              artifact_comparison_prerequisites,
                                              STRICT_VALIDATE, t1_inventory_proof,
                                              read_scope_attempts, terminal_receipt,
                                              t1_serialization, t1_ownership_context,
                                              t1_phase_evaluation, t1_offline_projection,
                                              t1_github_source_proof,
                                              native_validation_calls,
                                              input_files, input_digest, effective_input_binding,
                                              effective_input_diff, APPROVED_PROPOSAL, PROMPTS,
                                              VERIFY_SHA256, VERIFY_GENERATOR_VERSION,
                                              t1_handoff_value, t1_serialization_diagnostics,
                                              private_environment, private_inventory,
                                              prepare_private_pause, privatize_new_files,
                                              SupervisedSubscription, public_evidence,
                                              evidence_files, persist, chatgpt_method,
                                              private_binding, private_bytes, native_event_projection,
                                              OwnedMetadataRuntime, native_metadata,
                                               entrypoint, supervise_subscription)
import smoke_resume_candidate_opencode as smoke


@contextmanager
def fixture_cwd(path):
    previous = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(previous)


class PrivatePreparationTest(unittest.TestCase):
    """A1/A2/A3: synthetic metadata/processes only, never login or inference."""
    def setUp(self):
        self.base = Path(self.enterContext(tempfile.TemporaryDirectory(dir="/tmp/opencode")))
        self.cli = self.base / "runtime"
        self.cli.write_text("synthetic runtime")
        self.enterContext(patch("smoke_resume_candidate_opencode.RUNTIME_SHA256", sha(self.cli)))
        self.revision = "a" * 40
        (self.base / "home").mkdir()
        self.env = private_environment(self.base, str(self.cli), {
            "HOME": "/operator", "PATH": "/usr/bin:/bin:/operator/bin",
            "OPENAI_API_KEY": "SECRET", "OPENCODE_CONFIG_CONTENT": "SECRET",
            "OPENCODE_SERVER": "http://operator", "CODEX_HOME": "/operator/codex"})
        self.method = {"id": "chatgpt-token-sharing", "type": "oauth", "label": "Sign in with ChatGPT"}
        self.integration = {"id": "openai", "methods": [self.method], "connections": []}
        self.provider = {"id": "openai", "integrationID": "openai", "activation": "auto"}
        self.model = {"id": "catalog-only", "providerID": "openai", "type": "chat",
                      "enabled": True, "status": "active", "cost": [],
                      "capabilities": {"tools": True, "input": ["text"], "output": ["text"]}}
        self.connection = {"type": "credential", "id": "PRIVATE-CONNECTION-SENTINEL",
                           "label": "PERSONAL-SENTINEL", "method": "oauth"}
        privatize_new_files(self.base)
        runtime = self.enterContext(patch("smoke_resume_candidate_opencode.OwnedMetadataRuntime"))
        runtime.return_value.__enter__.return_value.receipt.return_value = {
            "synthetic": True, "plugin_ready": True, "exit_code": 0}

    def api(self, cli, repo, env, path, **kwargs):
        return {"/api/integration/openai": copy.deepcopy(self.integration),
                "/api/provider/openai": self.provider,
                "/api/model": [self.model]}[path]

    def pause(self, **kwargs):
        with patch("smoke_resume_candidate_opencode.native_metadata", side_effect=self.api):
            return prepare_private_pause(self.base, str(self.cli), self.revision, self.env, **kwargs)

    def controller(self):
        prepared = self.pause()
        with patch("smoke_resume_candidate_opencode.native_metadata", side_effect=self.api):
            controller = SupervisedSubscription(
                self.base, str(self.cli), self.env, self.revision, prepared["receipt_sha256"])
        self.addCleanup(controller.close)
        return controller

    def continuity(self):
        return patch("smoke_resume_candidate_opencode.git",
                     side_effect=lambda root, env, *args: (
                         self.revision if args == ("rev-parse", "HEAD") else
                         "synthetic-code-object" if args[0] in ("rev-parse", "hash-object") else ""))

    def complete(self, controller, *, exit_code=0, real_terminal=False, child_source=None):
        # Fixed harmless OS children ONLY. Never execute the auth argv under test.
        popen = subprocess.Popen
        auth = []
        source = child_source or f"import sys; sys.exit({exit_code})"
        def synthetic_spawn(command, **kwargs):
            if command[1:3] == ["auth", "login"]:
                self.assertEqual(command, [str(self.cli), "auth", "login", "openai",
                                          "--standalone", "--log-level", "none",
                                          "--method", self.method["id"]])
                self.assertEqual({key: kwargs[key] for key in
                                  ("stdin", "stdout", "stderr", "shell", "start_new_session")},
                                 {"stdin": None, "stdout": None, "stderr": None,
                                  "shell": False, "start_new_session": False})
                process = popen([sys.executable, "-I", "-S", "-c", source], **kwargs)
                auth.append(process)
                return process
            self.assertEqual(command, [sys.executable, "-I", "-S", "-c", "pass"])
            return popen(command, **kwargs)
        def api(cli, repo, env, path, **kwargs):
            if path == "/api/integration/openai":
                return {**self.integration, "connections": [self.connection] if auth else []}
            return self.api(cli, repo, env, path)
        from contextlib import nullcontext
        tty = (nullcontext() if real_terminal else patch.object(
            controller, "_terminal_identity", return_value=(((1, 2, 3),) * 3, os.getpgrp())))
        with (self.continuity(), tty,
              patch("smoke_resume_candidate_opencode.native_metadata", side_effect=api),
              patch("smoke_resume_candidate_opencode.subprocess.Popen", side_effect=synthetic_spawn),
              patch("smoke_resume_candidate_opencode.execute_model", side_effect=AssertionError("no inference"))):
            controller.manual_login(self.env, quota_authorized=True,
                                    entitlement_confirmed=True, terminal_privacy_confirmed=True)
        self.assertEqual(len(auth), 1)
        return auth[0]

    def test_metadata_pause_same_profile_resume_no_inference_and_filtered_environment(self):
        with patch("smoke_resume_candidate_opencode.execute_model",
                   side_effect=AssertionError("no inference")):
            prepared = self.pause()
            self.assertEqual(prepared, self.pause(expected=prepared["receipt_sha256"]))
        self.assertFalse(prepared["inference_verified"])
        self.assertFalse(prepared["login_requested"])
        self.assertEqual(prepared["route_proof"], "pending")
        self.assertEqual(prepared["native_proof"], "NOT_RUN")
        self.assertNotIn("SECRET", json.dumps(self.env))
        self.assertNotIn("/operator", self.env["PATH"])
        self.assertTrue(all(Path(self.env[k]).is_relative_to(self.base) for k in
                            ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME",
                             "XDG_STATE_HOME", "CODEX_HOME", "OPENCODE_DB")))
        for bad in ("missing", "0" * 64):
            with self.assertRaises(RuntimeError):
                self.pause(expected=bad)
        receipt = self.base / "private-preparation.json"
        receipt.write_text(receipt.read_text() + " ")
        with self.assertRaises(RuntimeError):
            self.pause(expected=prepared["receipt_sha256"])

    def test_profile_permission_symlink_runtime_config_and_head_mismatch_block(self):
        prepared = self.pause()
        self.cli.chmod(0o644)
        with self.assertRaises(RuntimeError):
            self.pause(expected=prepared["receipt_sha256"])
        self.cli.chmod(0o600)
        link = self.base / "outside"
        link.symlink_to("/etc/passwd")
        with self.assertRaises(RuntimeError):
            private_inventory(self.base)
        link.unlink()
        codex = self.base / "home/.codex"
        codex.mkdir(mode=0o700)
        auth = codex / "auth.json"
        auth.write_text("NEVER-HASH-AUTH-SENTINEL")
        auth.chmod(0o600)
        def nonsecret_hash(path):
            self.assertNotEqual(path, auth)
            return sha(path)
        with patch("smoke_resume_candidate_opencode.sha", side_effect=nonsecret_hash):
            with self.assertRaises(RuntimeError):
                self.pause(expected=prepared["receipt_sha256"])
        auth.unlink()
        self.cli.write_text("changed")
        with self.assertRaises(RuntimeError):
            self.pause(expected=prepared["receipt_sha256"])

    def test_unsupported_schema_method_connections_and_json_proof_block_before_login(self):
        for integration in ({}, {**self.integration, "connections": [self.connection]},
                            {**self.integration, "methods": []},
                            {**self.integration, "methods": [self.method, self.method]},
                            {**self.integration, "methods": [{**self.method, "id": "generic-oauth"}]}):
            with self.subTest(integration=integration):
                with (patch("smoke_resume_candidate_opencode.native_metadata", return_value=integration),
                      patch("smoke_resume_candidate_opencode.subprocess.Popen",
                            side_effect=AssertionError("no login")), self.assertRaises(RuntimeError)):
                    prepare_private_pause(self.base, str(self.cli), self.revision, self.env)
        with self.assertRaises(RuntimeError):
            chatgpt_method({**self.integration, "methods": [{**self.method, "type": "key"}]})
        with (patch("smoke_resume_candidate_opencode.native_metadata",
                    side_effect=[self.integration, {}, [self.model]]), self.assertRaises(RuntimeError)):
            prepare_private_pause(self.base, str(self.cli), self.revision, self.env)

    def test_supervisor_exclusivity_nonterminal_missing_authorization_and_external_callback(self):
        controller = self.controller()
        with self.assertRaises(BlockingIOError):
            SupervisedSubscription(self.base, str(self.cli), self.env,
                                   self.revision, controller.preparation["receipt_sha256"])
        with (self.continuity(), patch("smoke_resume_candidate_opencode.os.isatty", return_value=False),
              patch("smoke_resume_candidate_opencode.subprocess.Popen",
                    side_effect=AssertionError("no login")), self.assertRaises(RuntimeError)):
            controller.manual_login(self.env, quota_authorized=True,
                                    entitlement_confirmed=True, terminal_privacy_confirmed=True)
        for quota, entitlement, privacy in ((False, True, True),
                                            (True, False, True), (True, True, False)):
            with (patch("smoke_resume_candidate_opencode.os.isatty", return_value=True),
                  patch("smoke_resume_candidate_opencode.subprocess.Popen",
                        side_effect=AssertionError("no login")), self.assertRaises(RuntimeError)):
                controller.manual_login(self.env, quota_authorized=quota,
                                        entitlement_confirmed=entitlement,
                                        terminal_privacy_confirmed=privacy)
        for callback in (None, lambda *_: {"completed": True}, {"completed": True}):
            with (patch("smoke_resume_candidate_opencode.subprocess.Popen") as spawn,
                  self.assertRaises(TypeError)):
                controller.manual_login(self.env, quota_authorized=True,
                                        entitlement_confirmed=True, on_terminal=callback)
            spawn.assert_not_called()
        self.assertIsNone(controller.connection)

    def test_cancelled_supervised_process_cannot_prove_authentication(self):
        controller = self.controller()
        with self.assertRaises(RuntimeError):
            self.complete(controller, exit_code=1)
        with self.assertRaises(RuntimeError):
            controller.public_receipt()
        self.assertIsNone(controller.connection)

    def test_local_identity_lease_profile_runtime_head_and_code_fail_before_spawn(self):
        controller = self.controller()
        changes = (
            ("_controller", (-1, 0, 0, 0)),
            ("_lease", (-1, -1)),
            ("_profile_alias", "wrong-profile"),
            ("_execution", "external-execution-id"),
            ("binding", {**controller.binding, "candidate": "other"}),
            ("_attempted", True),
        )
        for name, value in changes:
            with (self.subTest(change=name), self.continuity(),
                  patch.object(controller, name, value),
                  patch("smoke_resume_candidate_opencode.subprocess.Popen") as spawn,
                  self.assertRaises(RuntimeError)):
                controller.manual_login(self.env, quota_authorized=True,
                                        entitlement_confirmed=True, terminal_privacy_confirmed=True)
            spawn.assert_not_called()
        for args in (("rev-parse", "HEAD"), ("hash-object", "tests/smoke_resume_candidate_opencode.py")):
            def changed(root, env, *command):
                if command == args:
                    return "changed"
                return (self.revision if command == ("rev-parse", "HEAD") else
                        "synthetic-code-object" if command[0] in ("rev-parse", "hash-object") else "")
            with (patch("smoke_resume_candidate_opencode.git", side_effect=changed),
                  patch("smoke_resume_candidate_opencode.subprocess.Popen") as spawn,
                  self.assertRaises(RuntimeError)):
                controller.manual_login(self.env, quota_authorized=True,
                                        entitlement_confirmed=True, terminal_privacy_confirmed=True)
            spawn.assert_not_called()
        self.cli.write_text("changed runtime")
        with (self.continuity(), patch("smoke_resume_candidate_opencode.subprocess.Popen") as spawn,
              self.assertRaises(RuntimeError)):
            controller.manual_login(self.env, quota_authorized=True,
                                    entitlement_confirmed=True, terminal_privacy_confirmed=True)
        spawn.assert_not_called()

    def test_failed_capability_probe_cannot_spawn_auth_or_be_replayed(self):
        controller = self.controller()
        popen = subprocess.Popen
        calls = []
        def failed_probe(command, **kwargs):
            calls.append(command)
            self.assertEqual(command, [sys.executable, "-I", "-S", "-c", "pass"])
            return popen([sys.executable, "-I", "-S", "-c", "raise SystemExit(7)"], **kwargs)
        with (self.continuity(),
              patch.object(controller, "_terminal_identity", return_value="synthetic-terminal"),
              patch("smoke_resume_candidate_opencode.subprocess.Popen", side_effect=failed_probe)):
            with self.assertRaises(RuntimeError):
                controller.manual_login(self.env, quota_authorized=True,
                                        entitlement_confirmed=True, terminal_privacy_confirmed=True)
            with self.assertRaises(RuntimeError):
                controller.manual_login(self.env, quota_authorized=True,
                                        entitlement_confirmed=True, terminal_privacy_confirmed=True)
        self.assertEqual(len(calls), 1)
        self.assertIsNone(controller.process)
        self.assertIsNone(controller._completion)

    def test_terminal_descriptor_and_foreground_checks(self):
        good = Mock(st_dev=1, st_ino=2, st_rdev=3)
        with (patch("smoke_resume_candidate_opencode.os.isatty", return_value=True),
              patch("smoke_resume_candidate_opencode.os.get_inheritable", return_value=True),
              patch("smoke_resume_candidate_opencode.os.tcgetpgrp", return_value=os.getpgrp()),
              patch("smoke_resume_candidate_opencode.os.fstat", return_value=good)):
            self.assertIsNotNone(SupervisedSubscription._terminal_identity())
            for target, value in (
                    ("os.get_inheritable", False), ("os.tcgetpgrp", -1),
                    ("os.isatty", False)):
                with (patch("smoke_resume_candidate_opencode." + target, return_value=value),
                      self.assertRaises(RuntimeError)):
                    SupervisedSubscription._terminal_identity()
            with (patch("smoke_resume_candidate_opencode.os.fstat",
                        side_effect=[good, good, Mock(st_dev=1, st_ino=9, st_rdev=8)]),
                  self.assertRaises(RuntimeError)):
                SupervisedSubscription._terminal_identity()

    def test_pty_exact_harmless_child_wait_and_redirect_block_no_auth_or_inference(self):
        """Real owned disposable PTY; all provider metadata synthetic, NO auth."""
        master, slave = os.openpty()
        read_fd, write_fd = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(read_fd)
            os.close(master)
            result = {"ok": False}
            try:
                os.setsid()
                fcntl.ioctl(slave, termios.TIOCSCTTY, 0)
                for fd in (0, 1, 2):
                    os.dup2(slave, fd, inheritable=True)
                if slave > 2:
                    os.close(slave)
                with closing(self.controller()) as controller:
                    saved = os.dup(1)
                    with open(os.devnull, "w") as redirected:
                        os.dup2(redirected.fileno(), 1)
                        with (self.continuity(),
                              patch("smoke_resume_candidate_opencode.subprocess.Popen") as spawn,
                              self.assertRaises(RuntimeError)):
                            controller.manual_login(
                                self.env, quota_authorized=True, entitlement_confirmed=True,
                                terminal_privacy_confirmed=True)
                        spawn.assert_not_called()
                    os.dup2(saved, 1, inheritable=True)
                    os.close(saved)
                    child = self.complete(controller, real_terminal=True, child_source=(
                        "import os; assert all(os.isatty(fd) and os.tcgetpgrp(fd)==os.getpgrp() "
                        "for fd in (0,1,2)); print('OFFLINE-PTY-SENTINEL')"))
                    with self.continuity():
                        receipt = controller.public_receipt()
                    self.assertIs(controller._observed_process, child)
                    self.assertIsNot(child, controller._probe)
                    self.assertEqual(child.returncode, 0)
                    self.assertEqual(receipt["completion"]["completion_source"], "os-wait")
                    self.assertEqual(receipt["completion"]["observer_kind"], "local-controller")
                    self.assertNotIn("worker_id", json.dumps(receipt))
                    self.assertNotIn("OFFLINE-PTY-SENTINEL", json.dumps(receipt))
                    public_evidence(receipt)
                    result = {"ok": True, "child": child.pid, "probe": controller._probe.pid,
                              "observer": receipt["completion"]["observer_kind"]}
            except BaseException as error:
                result = {"ok": False, "error": type(error).__name__}
            os.write(write_fd, json.dumps(result).encode())
            os.close(write_fd)
            os._exit(0 if result["ok"] else 1)
        os.close(write_fd)
        os.close(slave)
        observed, report = b"", b""
        deadline = time.monotonic() + 15
        try:
            while time.monotonic() < deadline:
                ready, _, _ = select.select([read_fd, master], [], [], max(0, deadline-time.monotonic()))
                for fd in ready:
                    try:
                        block = os.read(fd, 8192)
                    except OSError:
                        block = b""
                    if fd == master:
                        observed += block
                    else:
                        report += block
                if report:
                    break
            if not report:
                os.kill(pid, signal.SIGKILL)  # only this fixture-owned child
            _, status = os.waitpid(pid, 0)
            self.assertEqual(status, 0, report)
            self.assertTrue(json.loads(report)["ok"])
            self.assertNotEqual(json.loads(report)["child"], json.loads(report)["probe"])
            # Capture is permitted ONLY for this synthetic fixture, never production login.
            if b"OFFLINE-PTY-SENTINEL" not in observed:
                try:
                    observed += os.read(master, 8192)
                except OSError:
                    pass
            self.assertIn(b"OFFLINE-PTY-SENTINEL", observed)
        finally:
            os.close(read_fd)
            os.close(master)

    def test_os_signal_child_failure_and_restart_or_serialized_receipt_do_not_authorize(self):
        controller = self.controller()
        with self.assertRaises(RuntimeError):
            self.complete(controller, child_source="import os,signal; os.kill(os.getpid(),signal.SIGTERM)")
        self.assertLess(controller.process.returncode, 0)
        with (self.continuity(), self.assertRaises(RuntimeError)):
            controller.public_receipt()
        with (self.continuity(), patch("smoke_resume_candidate_opencode.subprocess.Popen") as spawn,
              self.assertRaises(RuntimeError)):
            controller.manual_login(self.env, quota_authorized=True,
                                    entitlement_confirmed=True, terminal_privacy_confirmed=True)
        spawn.assert_not_called()
        controller.close()
        with self.assertRaises(RuntimeError):
            controller.recheck(str(self.cli), ROOT, self.env, self.model)
        # JSON with favorable fields has no live OS object authority.
        with (patch("smoke_resume_candidate_opencode.checked_json", side_effect=[
                {"location": {"directory": str(ROOT)}, "data": self.model},
                {"location": {"directory": str(ROOT)}, "data": [self.model]}]),
              self.assertRaises(RuntimeError)):
            model_preflight(str(self.cli), ROOT, self.env, {},
                            subscription={"completed": True, "observer_kind": "local-controller"})

    def wait_failure(self, kind):
        controller = self.controller()
        popen = subprocess.Popen
        children = []
        def spawn(command, **kwargs):
            if command[1:3] != ["auth", "login"]:
                return popen(command, **kwargs)  # harmless capability probe
            child = popen([sys.executable, "-I", "-S", "-c",
                           "import time; time.sleep(30)"], **kwargs)
            children.append(child)
            wait = child.wait
            first = True
            def interrupted_wait(timeout=None):
                nonlocal first
                if first:
                    first = False
                    if kind == "signal":
                        os.kill(os.getpid(), signal.SIGTERM)  # handler installed by controller
                    if kind == "timeout":
                        raise subprocess.TimeoutExpired("synthetic-child", timeout)
                    raise KeyboardInterrupt()
                return wait(timeout=timeout)
            child.wait = interrupted_wait
            return child
        with (self.continuity(),
              patch.object(controller, "_terminal_identity", return_value="synthetic-terminal"),
              patch("smoke_resume_candidate_opencode.native_metadata", side_effect=self.api),
              patch("smoke_resume_candidate_opencode.subprocess.Popen", side_effect=spawn),
              self.assertRaises((KeyboardInterrupt, InterruptedError, subprocess.TimeoutExpired))):
            controller.manual_login(self.env, quota_authorized=True,
                                    entitlement_confirmed=True, terminal_privacy_confirmed=True)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())
        self.assertIsNone(controller._completion)
        self.assertIsNone(controller.connection)

    def test_local_wait_timeout_stops_only_owned_child(self):
        self.wait_failure("timeout")

    def test_local_wait_cancellation_stops_only_owned_child(self):
        self.wait_failure("cancel")

    def test_local_controller_signal_stops_only_owned_child(self):
        handler = signal.getsignal(signal.SIGTERM)
        self.wait_failure("signal")
        self.assertEqual(signal.getsignal(signal.SIGTERM), handler)

    def test_probe_wrong_child_receipt_and_restart_cannot_restore_completion(self):
        controller = self.controller()
        self.complete(controller)
        with self.continuity():
            receipt = controller.public_receipt()
            with self.assertRaises(RuntimeError):
                copy.copy(controller).public_receipt()
            for name, value in (("process", controller._probe),
                                ("_completion", json.loads(json.dumps(receipt["completion"]))),
                                ("_execution", "outer-pane-exit"),
                                ("_controller", (-1, 0, 0, 0))):
                with (self.subTest(change=name), patch.object(controller, name, value),
                      self.assertRaises(RuntimeError)):
                    controller.public_receipt()
        controller.close()
        self.integration["connections"] = [self.connection]
        with (patch("smoke_resume_candidate_opencode.native_metadata", side_effect=self.api),
              patch("smoke_resume_candidate_opencode.execute_model",
                    side_effect=AssertionError("no inference")), self.assertRaises(RuntimeError)):
            SupervisedSubscription(self.base, str(self.cli), self.env,
                                   self.revision, controller.preparation["receipt_sha256"])

    def test_changed_method_or_terminal_after_capability_stops_before_auth(self):
        controller = self.controller()
        with (self.continuity(),
              patch.object(controller, "_terminal_identity", return_value="synthetic-terminal")):
            controller._preflight_terminal(self.env)  # harmless OS probe only
            self.assertIsNone(controller.process)
            for name, value in (("_probe_binding", {"completed": True}),
                                ("_terminal", "different-terminal"),
                                ("method", {**self.method, "id": "wrong-method"})):
                with (self.subTest(change=name), patch.object(controller, name, value),
                      patch("smoke_resume_candidate_opencode.subprocess.Popen") as spawn,
                      self.assertRaises(RuntimeError)):
                    controller.manual_login(self.env, quota_authorized=True,
                                            entitlement_confirmed=True, terminal_privacy_confirmed=True)
                spawn.assert_not_called()

    def test_terminal_entrypoint_no_inference_and_technical_failure_before_prompts(self):
        with (patch("smoke_resume_candidate_opencode.supervise_subscription") as local,
              patch("smoke_resume_candidate_opencode.main") as inference):
            entrypoint(["--supervise-subscription", str(self.base), "--receipt-sha256", "a"*64])
        local.assert_called_once_with(self.base, "a"*64, None)
        inference.assert_not_called()
        controller = self.controller()
        with (patch.object(SupervisedSubscription, "_terminal_identity",
                           side_effect=RuntimeError("non-TTY")),
              patch("smoke_resume_candidate_opencode.shutil.which", return_value=str(self.cli)),
              self.continuity(), patch("builtins.input", side_effect=AssertionError("no human prompt")),
              patch("smoke_resume_candidate_opencode.subprocess.Popen") as spawn,
              self.assertRaises(RuntimeError)):
            supervise_subscription(self.base, controller.preparation["receipt_sha256"])
        spawn.assert_not_called()

    def grant(self, controller):
        decision = {
            "decision": "authorized", "issue": 61, "run": smoke.NATIVE_RUN,
            "candidate": controller.revision, "approved_proposal": smoke.APPROVED_PROPOSAL,
            "runtime_sha256": smoke.RUNTIME_SHA256, "profile_alias": controller._profile_alias,
            "receipt_sha256": controller._preparation_sha256, "scope": ["T1", "T5", "T7"],
            "attempts": 1, "economic_route": "chatgpt-subscription-quota",
            "model": "explicit-post-auth-catalog-selection", "fresh_local_confirmation": True,
            "paid_api": False, "fallback": False, "retry": False,
            "coordinator_session": "ses_SYNTHETICCOORDINATOR"}
        body = smoke.GRANT_START + json.dumps(decision) + smoke.GRANT_END
        reference = "sha256:" + hashlib.sha256(smoke.phase_evidence.canonical(decision)).hexdigest()
        return decision, {"body": body}, reference

    def test_specific_canonical_grant_is_not_preparation_consent_flag_or_approval_file(self):
        controller = self.controller()
        decision, issue, reference = self.grant(controller)
        with patch.object(smoke, "canonical_attempt_issue", return_value=issue):
            grant = smoke.attempt_grant(controller, reference)
        self.assertEqual(grant["state"], "consumed")
        for body in ("autorizado", "Plus/Pro authorized; quota allowed",
                     issue["body"] * 2, smoke.GRANT_START + "{}" + smoke.GRANT_END):
            with (patch.object(smoke, "canonical_attempt_issue", return_value={"body": body}),
                  self.assertRaises(RuntimeError)):
                smoke.attempt_grant(controller, reference)
        for key, value in (("decision", "revoked"), ("candidate", "b"*40),
                           ("profile_alias", "other"), ("attempts", True),
                           ("paid_api", True), ("scope", ["T1"]), ("runtime_sha256", "b"*64)):
            changed = {**decision, key: value}
            with (self.subTest(key=key), patch.object(smoke, "canonical_attempt_issue", return_value={
                    "body": smoke.GRANT_START + json.dumps(changed) + smoke.GRANT_END}),
                  self.assertRaises(RuntimeError)):
                smoke.attempt_grant(controller, reference)
        for reference in (None, True, "approval.json", "sha256:"+"0"*64):
            with (patch.object(smoke, "canonical_attempt_issue", return_value=issue),
                  self.assertRaises(RuntimeError)):
                smoke.attempt_grant(controller, reference)

    def test_foreground_grant_recorder_and_consumed_attempt_block_before_auth_or_prompt(self):
        controller = self.controller()
        _, issue, reference = self.grant(controller)
        for boundary in ("grant", "recorder", "consumed"):
            with self.subTest(boundary=boundary):
                if boundary == "consumed":
                    persist(self.base, {"native_attempt": {"state": "consumed"}})
                with (patch.object(smoke.SupervisedSubscription, "_terminal_identity",
                                   return_value="synthetic-terminal"),
                      patch.object(smoke, "SupervisedSubscription", return_value=controller),
                      patch.object(smoke, "canonical_attempt_issue", return_value=(
                          {"body": "no decision"} if boundary == "grant" else issue)),
                      patch.object(smoke.phase_evidence, "phase_support", side_effect=(
                          ValueError("unsupported") if boundary == "recorder" else None)),
                      patch.object(smoke.shutil, "which", return_value=str(self.cli)),
                      self.continuity(),
                      patch.object(controller, "close"), patch.object(controller, "manual_login") as auth,
                      patch("builtins.input", side_effect=AssertionError("no human prompt")),
                      self.assertRaises((RuntimeError, ValueError))):
                    supervise_subscription(self.base, controller.preparation["receipt_sha256"], reference)
                auth.assert_not_called()

    def test_foreground_entry_same_supervisor_real_full_main_and_phase_roundtrip_offline(self):
        """L2/E1 integrated wiring, NOT native auth/Skill/model proof.

        Execute the existing main and its complete T1/T5/T7 loop. Only external
        runtime/model boundaries are synthetic; every recovery oracle, prompt,
        permission, snapshot, fixture Git/receipt and evidence transport is real.
        The synthetic native-schema DB is never an authenticated account DB.
        """
        from types import SimpleNamespace
        source = self.base / "candidate-fixture"
        subprocess.run(["git", "clone", "-q", str(ROOT), str(source)], check=True)
        # An isolated test fixture snapshot, not another implementation worktree.
        for path in ("tests/smoke_resume_candidate_opencode.py", "scripts/workflow_evidence.py"):
            shutil.copyfile(ROOT / path, source / path)
        shutil.copytree(ROOT / ".agents", source / ".agents", dirs_exist_ok=True)
        subprocess.run(["git", "-C", str(source), "add", "tests/smoke_resume_candidate_opencode.py",
                        "scripts/workflow_evidence.py"], check=True)
        subprocess.run(["git", "-C", str(source), "-c", "user.name=Fixture",
                        "-c", "user.email=fixture@localhost", "commit", "-qm",
                        "offline integration snapshot", "--allow-empty"], check=True)
        spec = importlib.util.spec_from_file_location(
            "issue61_offline_full_main", source / "tests/smoke_resume_candidate_opencode.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        self.addCleanup(sys.modules.pop, spec.name, None)
        spec.loader.exec_module(module)
        runtime = self.base / "harmless-runtime"
        runtime.write_text("#!/bin/sh\ncase \"$1\" in\n--version) echo v2.4.2;;\n"
                           "--help) printf 'api\\nrun\\nservice\\n';;\n*) exit 91;;\nesac\n")
        runtime.chmod(0o700)
        module.RUNTIME_SHA256 = sha(runtime)
        profile = self.base / "foreground-profile"
        revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        old_umask = os.umask(0o077)
        self.addCleanup(os.umask, old_umask)
        original_run, original_checked, original_main = module.run, module.checked_json, module.main
        original_which, original_popen = shutil.which, subprocess.Popen
        auth, order, observations, main_objects, fixture_errors, children = [], [], [], [], [], []
        def reap():
            for child in children:
                if child.stdin and not child.stdin.closed:
                    child.stdin.close()
                if child.poll() is None:
                    child.terminate()  # only fixture-owned harmless processes
                    child.wait(timeout=5)
                for stream in (child.stdout, child.stderr):
                    if stream and not stream.closed:
                        stream.close()
        self.addCleanup(reap)
        chosen = "openai/" + self.model["id"]
        connection = dict(self.connection)
        def metadata(cli, repo, env, path, **kwargs):
            if path == "/api/integration/openai":
                return {**self.integration, "connections": [connection] if auth else []}
            return self.api(cli, repo, env, path)
        def checked(command, *, cwd, env, **kwargs):
            if command[:3] == [str(runtime), "api", "--standalone"]:
                return {"location": {"directory": str(cwd)}, "data": (
                    self.model if command[-1] == "/api/model/default" else [self.model])}
            return original_checked(command, cwd=cwd, env=env, **kwargs)
        def run(command, *, cwd, env, **kwargs):
            if command[:2] == ["python3", "-c"]:
                result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
                if result.returncode:
                    raise AssertionError("offline installer fixture: " + result.stderr[-4000:])
                return result.stdout.strip()
            if command[:3] == [str(runtime), "debug", "agents"]:
                # Supported runtime boundary double only; no production guard or
                # oracle is changed. This is not a native plugin activation claim.
                directory = Path(json.loads(env["OPENCODE_CONFIG_CONTENT"])["plugins"][0])
                policy = json.loads((directory / "policy.json").read_text())
                with Path(policy["audit"]).open("a") as stream:
                    stream.write(json.dumps({"boundary": "setup", "decision": "active",
                                             "source": str(directory / "index.mjs")}) + "\n")
                return ""
            return original_run(command, cwd=cwd, env=env, **kwargs)
        def spawn(command, **kwargs):
            if command[1:3] == ["auth", "login"]:
                self.assertEqual(command[0], str(runtime))
                self.assertEqual([kwargs[k] for k in ("stdin", "stdout", "stderr")], [None]*3)
                order.append("synthetic-auth-child")
                child = original_popen([sys.executable, "-I", "-S", "-c", "pass"], **kwargs)
                children.append(child)
                auth.append(child)
                return child  # no auth command is ever executed
            child = original_popen(command, **kwargs)
            children.append(child)
            return child
        def synthetic_model(cli, repo, env, base, case, prompt, session=None, *, model):
            self.assertEqual(model, chosen)
            case_name, phase = case.split("-phase")
            phase = int(phase)
            current = json.loads((base / "results.json").read_text())["scenarios"][case_name][-1]
            fixture = json.loads((repo / "recovery-evidence.json").read_text())
            sid = session or "ses-offline-" + case_name
            message = f"{case_name}-assistant-{phase}"
            timestamp = 4 if phase == 1 else 9
            events = [{"type": "step_start", "sessionID": sid, "timestamp": timestamp,
                       "part": {"messageID": message}}]
            def event(tool, inp, output):
                events.append({"type": "tool_use", "sessionID": sid, "part": {
                    "tool": tool, "id": str(len(events)), "state": {
                        "status": "completed", "input": inp, "output": output,
                        "metadata": {"metadata": {"exit": 0, "truncated": False}}}}})
            policy = json.loads(Path(current["shell_guard"]["policy"]).read_text())
            def shell(command, cwd=repo):
                self.assertIn(command, policy["commands"][str(cwd)])
                output = subprocess.check_output(shlex.split(command), cwd=cwd,
                                                 env=policy["env"], text=True).strip()
                event("shell", {"command": command, "workdir": str(cwd)}, output)
            def skill(name, path):
                event("skill", {"id": name}, f'<skill_content name="{name}">\n' +
                      path.read_text().split("\n---\n", 1)[-1].strip() +
                      f"\nBase directory: {path.parent}\n</skill_content>")
            if phase == 1:
                skill("resume-workflow", base / "home/.local/share/my-ai-skills/active/skills/resume-workflow/SKILL.md")
            if case_name == "T7" and phase == 1:
                for issue in (21, 22):
                    shell(f"gh api repos/disposable/recovery/issues/{issue}")
                response = ("Qual issue e run você escolhe: issue #21 / wf-disposable-a "
                            "ou issue #22 / wf-disposable-b?")
            else:
                locators = current["published_read_only_locators"]
                for locator in locators["inventory_locators"]:
                    shell(locator["command"], Path(locator["cwd"]))
                shell("git rev-parse --show-toplevel")
                shell("git rev-parse HEAD")
                for receipt in current["runtime_receipts"].values():
                    path = receipt["checkout"]
                    for args in ("rev-parse --show-toplevel", "rev-parse HEAD",
                                 "status --porcelain=v1 --untracked-files=all"):
                        shell(f"git -C {shlex.quote(path)} {args}")
                for issue in ([61] if case_name == "T1" else [21, 22] if case_name == "T7" else [11, 13]):
                    shell(f"gh api repos/disposable/recovery/issues/{issue}")
                shell("openspec context --json")
                shell("openspec list --json")
                shell(locators["runtime_receipt_command"])
                if case_name == "T1":
                    for probe in current["fixture_proposal_facts"]["probes"]:
                        shell(probe["command"])
                    shell(locators["apply_instructions_locator"]["command"])
                if case_name == "T5":
                    for locator in locators["github_locators"]:
                        shell(locator["command"], Path(locator["cwd"]))
                event("read", {"path": ".agents/skills"},
                      "Read directory .agents/skills, entries 1-2\n"
                      "openspec-explore/\nopenspec-apply-change/")
                skill("openspec-explore", repo / ".agents/skills/openspec-explore/SKILL.md")
                shell(module.STRICT_VALIDATE)
                if case_name == "T1":
                    receipt = current["runtime_receipts"]["61"]
                    response = json.dumps({
                        "issue": 61, "run": fixture["run"], "evidence_scope": "controlled_fixture",
                        "proposal_sha": current["fixture_proposal_facts"]["proposal_sha"],
                        "review_sha": current["fixture_proposal_facts"]["review_sha"],
                        "status": "BLOCKED", "last_verified_gate": "proposal_review_validated",
                        "next_action": "reconcile-ownership", "apply_executed": False,
                        "blockers": ["Reconcile ownership before write."], "limitations": [],
                        "ownership_condition": module.t1_ownership_context(current["before"], receipt, fixture)})
                elif case_name == "T5":
                    response = f"PR 12 head {fixture['pr_head']} manual; dependent 13 waits."
                else:
                    response = "Issue 21, wf-disposable-a; read-only."
            events.append({"type": "text", "sessionID": sid, "part": {"text": response}})
            # Real supported projection against a SYNTHETIC schema DB. Auth
            # sentinel remains in an unrelated table and is never queried.
            database = base / "opencode.db"
            with closing(sqlite3.connect(database)) as db, db:
                db.executescript("""
                    CREATE TABLE IF NOT EXISTS session_v2(id,directory,version,time_created);
                    CREATE TABLE IF NOT EXISTS instruction_state(session_id,epoch_start,through_seq,initial_values,current_values);
                    CREATE TABLE IF NOT EXISTS instruction_blob(hash,value);
                    CREATE TABLE IF NOT EXISTS session_message(id,seq,time_created,data,session_id,type);
                    CREATE TABLE IF NOT EXISTS credential(secret);
                """)
                if phase == 1:
                    sources = module.t1_inspection_sources(repo, case=case_name)
                    entries = [{"id": Path(s["path"]).parent.name, "name": Path(s["path"]).parent.name,
                                "description": __import__("re").search(
                                    r"^description: (.+)$", Path(s["path"]).read_text(), __import__("re").M)[1]}
                               for s in sources]
                    digest = hashlib.sha256(json.dumps(entries, sort_keys=True,
                        ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
                    state = json.dumps({"core/skill-guidance": digest})
                    db.execute("INSERT INTO session_v2 VALUES(?,?,?,?)", (sid, str(repo), "2.4.2", 1))
                    db.execute("INSERT INTO instruction_state VALUES(?,?,?,?,?)", (sid, 4, 4, state, state))
                    db.execute("INSERT INTO instruction_blob VALUES(?,?)", (digest, json.dumps(entries)))
                    db.execute("INSERT INTO credential VALUES(?)", ("AUTH-SECRET-SENTINEL",))
                for ident, seq, created, role, times in (
                    (f"{case}-user", 5 if phase == 1 else 10, 2 if phase == 1 else 7, "user", {}),
                    (message, 6 if phase == 1 else 11, 3 if phase == 1 else 8, "assistant",
                     {"firstToken": 5 if phase == 1 else 10, "completed": 6 if phase == 1 else 11})):
                    db.execute("INSERT INTO session_message VALUES(?,?,?,?,?,?)",
                               (ident, seq, created, json.dumps({"time": times}), sid, role))
            database.chmod(0o600)
            transcript = base / f"{case}-events.jsonl"
            transcript.write_text("".join(json.dumps(module.native_event_projection(e))+"\n" for e in events))
            (base / f"{case}-stderr.log").write_text('{"code":"native-stderr-empty"}')
            terminal = {"exit_code": 0, "timed_out": False, "candidate": revision,
                        "session_ids": [sid], "malformed_lines": [], "error_events": [],
                        "offline_fixture": True}
            (base / f"{case}-terminal.json").write_text(json.dumps(terminal))
            observations.append((case, sid))
            return events, response, sid, str(transcript)
        def full_main(**kwargs):
            if kwargs.get("subscription") is not None:
                main_objects.append(kwargs["subscription"])
                self.assertEqual(kwargs["selected_model"], chosen)
                order.append("full-main")
            try:
                return original_main(**kwargs)
            except Exception as error:
                fixture_errors.append(type(error).__name__ + ": " + str(error))
                raise
        original_close = module.SupervisedSubscription.close
        def close(controller):
            if auth:
                order.append("close")
                self.assertIs(controller, main_objects[0])
            return original_close(controller)
        evidence = module.phase_evidence
        original_export, original_import = evidence.export_bundle, evidence.import_bundle
        def export(*args, **kwargs):
            self.assertIs(main_objects[0]._identity, main_objects[0])
            order.append("export")
            return original_export(*args, **kwargs)
        def importing(*args, **kwargs):
            self.assertIs(main_objects[0]._identity, main_objects[0])
            order.append("import")
            return original_import(*args, **kwargs)
        with (fixture_cwd(source), patch.object(module.shutil, "which", side_effect=lambda name, **kw: (
                str(runtime) if name == "opencode" and not kw else original_which(name, **kw))),
              patch.object(module, "OwnedMetadataRuntime") as owned,
              patch.object(module, "native_metadata", side_effect=metadata),
              patch.object(module, "checked_json", side_effect=checked),
              patch.object(module, "run", side_effect=run),
              patch.object(module.subprocess, "Popen", side_effect=spawn),
              patch.object(module, "execute_model", side_effect=synthetic_model),
              patch.object(module.SupervisedSubscription, "_terminal_identity", return_value="synthetic-terminal"),
              patch.object(module.SupervisedSubscription, "close", close),
              patch.object(module, "main", side_effect=full_main),
              patch.object(evidence, "export_bundle", side_effect=export),
              patch.object(evidence, "import_bundle", side_effect=importing),
              patch.dict(os.environ, {"RESUME_SMOKE_OUTPUT": str(profile),
                                      "RESUME_SMOKE_MODEL": "wrong-environment-override"}),
              redirect_stdout(StringIO())):
            owned.return_value.__enter__.return_value.receipt.return_value = {
                "synthetic": True, "plugin_ready": True, "exit_code": 0}
            module.main(prepare_only=True)
            prepared = json.loads((profile / "results.json").read_text())["preparation"]
            proxy = SimpleNamespace(revision=revision, _profile_alias=prepared["profile_alias"],
                                    _preparation_sha256=prepared["receipt_sha256"])
            decision, _, _ = self.grant(proxy)
            decision["runtime_sha256"] = module.RUNTIME_SHA256
            issue = {"body": module.GRANT_START + json.dumps(decision) + module.GRANT_END}
            reference = "sha256:" + hashlib.sha256(evidence.canonical(decision)).hexdigest()
            with (patch.object(module, "canonical_attempt_issue", return_value=issue),
                  patch("builtins.input", side_effect=["sim", "sim", "sim", chosen, "sim"])):
                try:
                    eid = module.entrypoint([
                        "--supervise-subscription", str(profile), "--receipt-sha256",
                        prepared["receipt_sha256"], "--grant-reference", reference])
                except RuntimeError as error:
                    self.fail(f"offline fixture: {error}; main={fixture_errors}; observed={observations}")
        self.assertEqual(order, ["synthetic-auth-child", "full-main", "export", "import", "close"])
        self.assertEqual(len(main_objects), 1)
        self.assertEqual([case for case, _ in observations], ["T1-phase1", "T5-phase1", "T7-phase1", "T7-phase2"])
        self.assertEqual(observations[2][1], observations[3][1])
        directory = evidence.record_dir(source, eid)
        manifest = evidence.load_manifest(directory)
        self.assertEqual((manifest["execution_mode"], manifest["exit_code"]), ("inprocess-phase", None))
        self.assertEqual(manifest["phase_identity"]["controller_pid"], os.getpid())
        self.assertEqual(main_objects[0]._controller[0], os.getpid())
        self.assertEqual(manifest["command"]["cwd"], ".")
        self.assertEqual(manifest["phase_completion"]["state"], "returned")
        self.assertEqual(evidence.verify_manifest(manifest, directory, source)["state"], "verified")
        retained = json.loads((profile / "results.json").read_text())
        self.assertTrue(all(r["proof_complete"] for rows in retained["scenarios"].values() for r in rows))
        with __import__("tarfile").open(directory / "phase-bundle.tar.gz") as bundle:
            names = bundle.getnames()
            self.assertNotIn("opencode.db", names)
            self.assertNotIn(b"AUTH-SECRET-SENTINEL", b"".join(
                bundle.extractfile(member).read() for member in bundle.getmembers()))
        # Explicit test-only retention of the already validated allowlisted
        # package. Never retain the fixture HOME/DB or relabel its candidate SHA.
        retained_bundle = os.environ.get("MY_AI_SKILLS_TEST_PHASE_BUNDLE")
        if retained_bundle:
            target = Path(retained_bundle)
            if (target.parent.resolve() != Path("/tmp/opencode").resolve() or
                    not target.name.startswith("issue61-offline-phase-qual-") or
                    not target.name.endswith(".tar.gz")):
                raise ValueError("unsafe offline qualification destination")
            with os.fdopen(os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                                   0o600), "wb") as output:
                output.write((directory / "phase-bundle.tar.gz").read_bytes())
            print(json.dumps({"offline_phase_qualification": eid, "fixture_candidate": revision,
                              "execution_mode": "inprocess-phase", "native_proof": "NOT_RUN",
                              "final_gate": "NOT_RUN"}), file=sys.stderr)

    def test_postauth_invalid_selection_refusal_cancel_or_lost_lease_never_infers(self):
        original_manual = SupervisedSubscription.manual_login
        for boundary in ("empty-model", "unknown-model", "fresh-refusal", "cancel", "lost-lease"):
            with self.subTest(boundary=boundary):
                # Independent harmless profiles; no production retry/reauth path.
                self.base = Path(self.enterContext(tempfile.TemporaryDirectory(dir="/tmp/opencode")))
                (self.base / "home").mkdir()
                self.env = private_environment(self.base, str(self.cli), {
                    "HOME": "/operator", "PATH": "/usr/bin:/bin"})
                self.integration["connections"] = []
                privatize_new_files(self.base)
                prepared = self.pause()
                from types import SimpleNamespace
                proxy = SimpleNamespace(revision=self.revision, _profile_alias=prepared["profile_alias"],
                                        _preparation_sha256=prepared["receipt_sha256"])
                _, issue, reference = self.grant(proxy)
                controllers = []
                def login(controller, env, **kwargs):
                    # The real local observer waits a harmless OS child, not auth.
                    with patch.object(SupervisedSubscription, "manual_login", original_manual):
                        self.complete(controller)
                    self.integration["connections"] = [self.connection]
                    controllers.append(controller)
                replies = iter(["sim", "sim", "sim"])
                def answer(prompt):
                    if prompt.startswith("Informe"):
                        if boundary == "empty-model":
                            return ""
                        if boundary == "unknown-model":
                            return "openai/not-in-catalog"
                        return "openai/" + self.model["id"]
                    if prompt.startswith("Confirma Plus/Pro,"):
                        if boundary == "cancel":
                            raise KeyboardInterrupt()
                        if boundary == "lost-lease":
                            controllers[0].lock.close()
                        return "não" if boundary == "fresh-refusal" else "sim"
                    return next(replies)
                with (self.continuity(),
                      patch.object(SupervisedSubscription, "_terminal_identity",
                                   return_value=(((1, 2, 3),)*3, os.getpgrp())),
                      patch.object(SupervisedSubscription, "manual_login", login),
                      patch.object(smoke, "native_metadata", side_effect=self.api),
                      patch.object(smoke, "private_environment", return_value=self.env),
                      patch.object(smoke.shutil, "which", return_value=str(self.cli)),
                      patch.object(smoke, "canonical_attempt_issue", return_value=issue),
                      patch.object(smoke, "main") as main,
                      patch.object(smoke.phase_evidence, "record_phase") as recorder,
                      patch("builtins.input", side_effect=answer), redirect_stdout(StringIO()),
                      self.assertRaises((RuntimeError, KeyboardInterrupt))):
                    supervise_subscription(self.base, prepared["receipt_sha256"], reference)
                main.assert_not_called()
                recorder.assert_not_called()  # evidence cannot begin before consent/route
                self.assertEqual(len(controllers), 1)
                self.assertIsNone(controllers[0]._identity)
                self.assertEqual(json.loads((self.base / "results.json").read_text())[
                    "native_attempt"]["state"], "consumed")

    def test_interrupted_native_boundary_stops_exact_harmless_child_and_retains_incomplete_facts(self):
        popen = subprocess.Popen
        children = []
        def spawn(command, **kwargs):
            # Test double at the runtime boundary; never execute model argv.
            if command[0] != "unused-fixture-runtime":
                return popen(command, **kwargs)
            child = popen([sys.executable, "-I", "-S", "-c",
                           "import time; time.sleep(30)"], **kwargs)
            communicate = child.communicate
            first = True
            def interrupted(*args, **kw):
                nonlocal first
                if first:
                    first = False
                    raise KeyboardInterrupt("AUTH-SECRET-SENTINEL")
                return communicate(*args, **kw)
            child.communicate = interrupted
            children.append(child)
            return child
        with (patch.object(smoke.subprocess, "Popen", side_effect=spawn),
              self.assertRaises(KeyboardInterrupt)):
            execute_model("unused-fixture-runtime", ROOT, self.env, self.base,
                          "T1-phase1", "offline synthetic cancellation", model="offline/model")
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())
        for stream in (children[0].stdout, children[0].stderr):
            stream.close()
        terminal = json.loads((self.base / "T1-phase1-terminal.json").read_text())
        self.assertTrue(terminal["interrupted"])
        self.assertLess(terminal["exit_code"], 0)
        self.assertNotIn("AUTH-SECRET-SENTINEL", json.dumps(terminal))

    def test_synthetic_os_child_chain_accepts_unknown_subscription_price_not_free(self):
        controller = self.controller()
        self.complete(controller)
        self.integration["connections"] = [self.connection]
        record = {}
        with (self.continuity(),
              patch("smoke_resume_candidate_opencode.native_metadata", side_effect=self.api),
              patch("smoke_resume_candidate_opencode.checked_json", side_effect=[
                  {"location": {"directory": str(ROOT)}, "data": self.model},
                  {"location": {"directory": str(ROOT)}, "data": [self.model]}])):
            self.assertEqual(model_preflight(str(self.cli), ROOT, self.env, record,
                                            subscription=controller), "openai/catalog-only")
        self.assertEqual(record["economic_branch"], "subscription-quota")
        self.assertEqual(record["price_display"], "unknown")
        self.assertFalse(record["inference_verified"])
        self.assertNotIn("SENTINEL", json.dumps(record))
        public_evidence(record)
        paid = {**self.model, "cost": [{"input": 1, "output": 0,
                                       "cache": {"read": 0, "write": 0}}]}
        unknown = {k: v for k, v in self.model.items() if k != "cost"}
        with (self.continuity(),
              patch.object(smoke, "checked_json", side_effect=[
                  {"location": {"directory": str(ROOT)}, "data": unknown},
                  {"location": {"directory": str(ROOT)}, "data": [unknown]}]),
              self.assertRaisesRegex(RuntimeError, "pricing schema")):
            model_preflight(str(self.cli), ROOT, self.env, {},
                            "openai/catalog-only", subscription=controller)
        self.model = paid
        with (self.continuity(),
              patch("smoke_resume_candidate_opencode.native_metadata", side_effect=self.api),
              patch("smoke_resume_candidate_opencode.checked_json", side_effect=[
                  {"location": {"directory": str(ROOT)}, "data": paid},
                  {"location": {"directory": str(ROOT)}, "data": [paid]}]),
              self.assertRaises(RuntimeError)):
            model_preflight(str(self.cli), ROOT, self.env, {}, subscription=controller)
        self.model = {**paid, "cost": []}
        for change in ("quota", "entitlement", "method", "connection", "api", "multiple",
                       "partial", "provider", "environment", "head"):
            with self.subTest(change=change):
                old = copy.deepcopy(self.integration), copy.deepcopy(self.provider)
                controller.quota_authorized = change != "quota"
                controller.entitlement_confirmed = change != "entitlement"
                if change == "method":
                    self.integration["methods"] = [{**self.method, "id": "other"}]
                if change == "connection":
                    self.integration["connections"] = [{**self.connection, "id": "other"}]
                if change == "api":
                    self.integration["connections"] = [{**self.connection, "method": "key"}]
                if change == "multiple":
                    self.integration["connections"] = [self.connection, self.connection]
                if change == "partial":
                    self.integration["connections"] = [{**self.connection, "status": {"status": "needs_auth"}}]
                if change == "provider":
                    self.provider["integrationID"] = "other"
                env = {**self.env, "OPENAI_API_KEY": "SENTINEL"} if change == "environment" else self.env
                with (patch("smoke_resume_candidate_opencode.git",
                            side_effect=lambda root, env, *args: (
                                "changed" if change == "head" else self.revision)
                            if args[0] == "rev-parse" else ""),
                      patch("smoke_resume_candidate_opencode.native_metadata", side_effect=self.api),
                      self.assertRaises(RuntimeError)):
                    controller.recheck(str(self.cli), ROOT, env, self.model)
                self.integration, self.provider = old

    def test_structural_evidence_and_filename_allowlist_never_package_auth_storage(self):
        for name in ("opencode.db", "opencode.db-wal", "opencode.db-shm", "login.log", "auth.json"):
            (self.base / name).write_text("SECRET-SENTINEL")
        persist(self.base, {"status": "metadata_only", "native_proof": "NOT_RUN"})
        self.assertEqual([p.name for p in evidence_files(self.base)], ["results.json"])
        original = (self.base / "results.json").read_bytes()
        for payload in ({"nested": {"account_id": "PERSONAL-SENTINEL"}},
                        {"events": [{"clientId": "PERSONAL-SENTINEL"}]},
                        {"type": "credential", "id": "PRIVATE-SENTINEL", "method": "oauth"},
                        {"unexpected": {"refresh_token": "SECRET-SENTINEL"}}):
            with self.assertRaises(RuntimeError):
                persist(self.base, payload)
            self.assertEqual((self.base / "results.json").read_bytes(), original)

    def test_config_receipt_and_parent_links_to_auth_never_reach_a_read_or_hash(self):
        config = self.base / "home/.config/opencode"
        config.mkdir(parents=True)
        auth = self.base / "opencode.db"
        auth.write_text("NEVER-READ-OR-HASH-SENTINEL")
        privatize_new_files(self.base)
        for name in ("AGENTS.md", "opencode.json", "opencode.jsonc"):
            link = config / name
            link.symlink_to(auth)
            with (patch("smoke_resume_candidate_opencode.sha") as digest,
                  patch("smoke_resume_candidate_opencode.private_bytes") as read,
                  self.assertRaises(RuntimeError)):
                private_binding(self.base, str(self.cli), self.revision)
            digest.assert_not_called()
            read.assert_not_called()
            with self.assertRaises(RuntimeError):
                private_bytes(self.base, link)
            link.unlink()
        receipt = self.base / "private-preparation.json"
        receipt.symlink_to(auth)
        with (patch("smoke_resume_candidate_opencode.sha") as digest,
              self.assertRaises(RuntimeError)):
            self.pause(expected="a" * 64)
        digest.assert_not_called()
        receipt.unlink()
        hardlink = config / "AGENTS.md"
        os.link(auth, hardlink)
        with (patch("smoke_resume_candidate_opencode.os.fdopen") as read,
              self.assertRaises(RuntimeError)):
            private_binding(self.base, str(self.cli), self.revision)
        read.assert_not_called()
        hardlink.unlink()
        with self.assertRaises(RuntimeError):
            private_bytes(self.base, self.base / "home/../opencode.db")
        parent = self.base / "home/.codex"
        parent.symlink_to(config, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            private_bytes(self.base, parent / "AGENTS.md")

    def test_verified_managed_instruction_links_positive_and_retarget_rejected(self):
        package = self.base / "home/.local/share/my-ai-skills"
        version = package / "versions" / self.revision
        instruction = version / "skills/example/SKILL.md"
        instruction.parent.mkdir(parents=True)
        instruction.write_text("canonical instruction")
        (version / "manifest.json").write_text(json.dumps({"revision": self.revision}))
        links = self.base / "home/.config/opencode/skills"
        links.mkdir(parents=True)
        (package / "active").symlink_to("versions/" + self.revision)
        (links / "example").symlink_to(package / "active/skills/example")
        privatize_new_files(self.base)
        binding = private_binding(self.base, str(self.cli), self.revision)
        self.assertIn("home/.config/opencode/skills/example", binding["config"])
        instruction.unlink()
        instruction.symlink_to(self.base / "opencode.db")
        with self.assertRaises(RuntimeError):
            private_binding(self.base, str(self.cli), self.revision)

    def test_native_diagnostics_and_unknown_nested_fields_never_retain_encoded_identity(self):
        sentinel = "SYNTHETIC-IDENTITY-SENTINEL"
        message = json.dumps({"account_id": sentinel})
        base_event = {"type": "error", "timestamp": 1, "sessionID": "ses-synthetic",
                      "error": {"type": "unknown", "message": message}}
        unknown = {"type": "text", "timestamp": 1, "sessionID": "ses-synthetic",
                   "part": {"text": "safe", "time": {"start": 1, "unknown": message}}}
        for number, event in enumerate((base_event, unknown)):
            destination = self.base / str(number)
            destination.mkdir()
            process = Mock(pid=123, returncode=1)
            process.communicate.return_value = (json.dumps(event), message)
            with (patch("smoke_resume_candidate_opencode.subprocess.Popen", return_value=process),
                  patch("smoke_resume_candidate_opencode.git", return_value=self.revision),
                  self.assertRaises(RuntimeError)):
                execute_model("synthetic-cli", self.base, {}, destination,
                              "T1-phase1", "synthetic", model="synthetic/model")
            for artifact in destination.iterdir():
                self.assertNotIn(sentinel, artifact.read_text())
                self.assertNotIn("account_id", artifact.read_text())
            if number == 0:
                self.assertEqual(json.loads((destination / "T1-phase1-stderr.log").read_text()),
                                 {"code": "native-stderr-present"})
                self.assertEqual({p.name for p in evidence_files(destination)},
                                 {"T1-phase1-events.jsonl", "T1-phase1-terminal.json",
                                  "T1-phase1-stderr.log"})
        with self.assertRaises(RuntimeError):
            public_evidence({"encoded": message})
        import smoke_resume_candidate_opencode as harness
        with (patch("smoke_resume_candidate_opencode.subprocess.run",
                    return_value=Mock(returncode=1, stderr=message, stdout=message)),
              self.assertRaises(RuntimeError) as caught):
            harness.run(["synthetic-command"], cwd=self.base, env={})
        self.assertNotIn(sentinel, str(caught.exception))
        self.assertEqual(str(caught.exception), "fixture command exited 1; raw diagnostics omitted")

    def test_supported_tool_projection_preserves_native_body_input_and_execution_facts(self):
        body = "<skill_content>canonical body bytes</skill_content>"
        event = {"type": "tool_use", "timestamp": 3, "sessionID": "ses-synthetic",
                 "part": {"id": "call", "messageID": "assistant", "tool": "skill",
                          "state": {"status": "completed", "input": {"id": "openspec-explore"},
                                    "output": body, "metadata": {
                                        "metadata": {"exit": 0, "truncated": False},
                                        "providerCall": {"executed": True, "state": {"opaque": "excluded"}},
                                        "providerResult": {"executed": True}}}}}
        projected = native_event_projection(event)
        self.assertEqual(projected["part"]["state"]["output"], body)
        self.assertEqual(projected["part"]["state"]["input"], event["part"]["state"]["input"])
        self.assertEqual(projected["part"]["state"]["metadata"]["metadata"],
                         {"exit": 0, "truncated": False})
        self.assertEqual(projected["part"]["state"]["metadata"]["providerCall"], {"executed": True})
        for field in ("metadata", "input"):
            bad = copy.deepcopy(event)
            bad["part"]["state"][field]["unknown"] = {"identity": "SYNTHETIC-IDENTITY-SENTINEL"}
            with self.assertRaises(RuntimeError):
                native_event_projection(bad)

    def owned_process(self, startup=b'{"url":"http://127.0.0.1:12345"}\n'):
        read, write = os.pipe()
        os.write(write, startup)
        os.close(write)
        output = os.fdopen(read, "rb")
        self.addCleanup(output.close)
        process = Mock(pid=123, returncode=None, stdin=Mock(), stdout=output)
        process.poll.side_effect = lambda: process.returncode
        def wait(**kwargs):
            process.returncode = 0
            return 0
        process.wait.side_effect = wait
        return process

    def test_owned_runtime_waits_for_actual_plugin_condition_once_and_observes_terminal(self):
        process = self.owned_process()
        responses = [{"version": "2.4.2", "pid": 123}, [], [{"state": "started"}],
                     self.integration, self.provider]
        with (patch("smoke_resume_candidate_opencode.subprocess.Popen", return_value=process) as spawn,
              patch.object(OwnedMetadataRuntime, "request", side_effect=responses)):
            with OwnedMetadataRuntime(str(self.cli), ROOT, self.env) as runtime:
                self.assertTrue(runtime.ready)
                self.assertEqual(runtime.polls, 2)
                self.assertEqual(native_metadata(str(self.cli), ROOT, self.env,
                                                "/api/integration/openai", runtime=runtime),
                                 self.integration)
                self.assertEqual(native_metadata(str(self.cli), ROOT, self.env,
                                                "/api/provider/openai", runtime=runtime), self.provider)
                with self.assertRaises(RuntimeError):
                    native_metadata(str(self.cli), ROOT / "other", self.env,
                                    "/api/integration/openai", runtime=runtime)
                with self.assertRaises(RuntimeError):
                    native_metadata(str(self.cli), ROOT, {**self.env, "OPENAI_API_KEY": "SENTINEL"},
                                    "/api/integration/openai", runtime=runtime)
            self.assertEqual(runtime.receipt()["exit_code"], 0)
            self.assertEqual(runtime.receipt()["shutdown"], "owned-stdio-eof")
            process.stdin.close.assert_called_once()
            process.wait.assert_called_once()
            self.assertEqual(spawn.call_count, 1)
            self.assertEqual(spawn.call_args.kwargs["stderr"], subprocess.DEVNULL)
            with self.assertRaises(RuntimeError):
                runtime.__enter__()
            self.assertNotIn(self.env["OPENCODE_PASSWORD"], json.dumps(runtime.receipt()))
            original = self.cli.read_text()
            self.cli.write_text("changed synthetic runtime")
            with self.assertRaises(RuntimeError):
                runtime.receipt()
            self.cli.write_text(original)

    def test_owned_runtime_startup_truncation_identity_and_readiness_fail_closed(self):
        for failure in ("truncated", "identity", "pid", "startup-timeout", "startup-exit", "readiness"):
            process = self.owned_process(b'{"url":"PRIVATE-SENTINEL"' if failure == "truncated"
                                         else b'{"url":"http://127.0.0.1:12345"}\n')
            clock = {"now": 0, "calls": 0}
            def now():
                clock["calls"] += 1
                return 16 if failure == "startup-timeout" and clock["calls"] > 1 else clock["now"]
            if failure == "startup-exit":
                process.returncode = 1
            def response(path, **kwargs):
                if path == "/api/info":
                    return {"version": "unknown" if failure == "identity" else "2.4.2",
                            "pid": 999 if failure == "pid" else 123}
                clock["now"] = 6
                return []
            with (patch("smoke_resume_candidate_opencode.subprocess.Popen", return_value=process),
                  patch("smoke_resume_candidate_opencode.time.monotonic", side_effect=now),
                  patch.object(OwnedMetadataRuntime, "request", side_effect=response),
                  self.assertRaises(RuntimeError) as caught):
                with OwnedMetadataRuntime(str(self.cli), ROOT, self.env):
                    self.fail("unsupported preparation must not advance")
            self.assertNotIn("PRIVATE-SENTINEL", str(caught.exception))
            process.stdin.close.assert_called_once()
            self.assertEqual(process.returncode, 0)

    def test_owned_http_error_location_schema_and_uncertain_cleanup_keep_safe_codes(self):
        import urllib.error
        from io import BytesIO
        process = self.owned_process()
        runtime = OwnedMetadataRuntime(str(self.cli), ROOT, self.env)
        runtime.process, runtime.url = process, "http://127.0.0.1:12345"
        error = urllib.error.HTTPError(runtime.url, 404, "PRIVATE-SENTINEL", None,
                                      BytesIO(b'{"account_id":"PRIVATE-SENTINEL"}'))
        with (patch("smoke_resume_candidate_opencode.urllib.request.build_opener") as opener,
              self.assertRaises(RuntimeError) as caught):
            opener.return_value.open.side_effect = error
            runtime.request("/api/integration/openai")
        self.assertEqual(str(caught.exception), "native metadata HTTP 404; payload omitted")
        with (patch("smoke_resume_candidate_opencode.urllib.request.build_opener") as opener,
              self.assertRaises(RuntimeError)):
            response = opener.return_value.open.return_value.__enter__.return_value
            response.read.return_value = b'{"location":{"directory":"/wrong"},"data":[]}'
            runtime.request("/api/plugin")
        process.wait.side_effect = [subprocess.TimeoutExpired("owned-server", 15), 0]
        with self.assertRaises(RuntimeError):
            runtime.close()
        process.terminate.assert_called_once()
        with self.assertRaises(RuntimeError):
            runtime.receipt()


class SmokeArgvSafetyTest(unittest.TestCase):
    def test_help_and_unknown_option_exit_before_discovery_fixture_or_model(self):
        script = Path(__file__).with_name("smoke_resume_candidate_opencode.py")
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
            home = Path(root) / "home"
            home.mkdir()
            for argument, code in (("--help", 0), ("--unexpected", 2)):
                with self.subTest(argument=argument):
                    stdout, stderr = StringIO(), StringIO()
                    with (patch.object(sys, "argv", [str(script), argument]),
                          patch.dict(os.environ, {"HOME": str(home),
                                                   "PATH": str(home),
                                                   "PYTHONDONTWRITEBYTECODE": "1"},
                                     clear=True),
                          patch("shutil.which", side_effect=AssertionError("discovery")),
                          patch("tempfile.mkdtemp", side_effect=AssertionError("fixture")),
                          patch("subprocess.run", side_effect=AssertionError("model")),
                          patch("subprocess.Popen", side_effect=AssertionError("model")),
                          redirect_stdout(stdout), redirect_stderr(stderr)):
                        with self.assertRaises(SystemExit) as exit:
                            runpy.run_path(str(script), run_name="__main__")
                    self.assertEqual(exit.exception.code, code)
                    output = stdout.getvalue() if code == 0 else stderr.getvalue()
                    self.assertIn("usage:", output)
                    if code:
                        self.assertIn("unrecognized arguments: --unexpected", output)
                    self.assertEqual(list(home.iterdir()), [])


class DisposablePathTest(unittest.TestCase):
    def test_launcher_precedes_system_path_without_operator_home(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
            home = Path(root) / "home"
            launcher = home / ".local/bin/worktree-reservation"
            launcher.parent.mkdir(parents=True)
            launcher.write_text("#!/bin/sh\nexit 0\n")
            launcher.chmod(0o755)
            path = disposable_path(home, "/home/operator/.local/bin:/usr/bin:"
                                  "/home/operator/.opencode/bin:/bin",
                                  "/home/operator")
            self.assertEqual(path.split(":"), [str(launcher.parent),
                                              "/usr/bin", "/bin"])
            self.assertEqual(shutil.which("worktree-reservation", path=path),
                             str(launcher))

    def test_similarly_named_directory_is_not_operator_home(self):
        home = Path("/tmp/opencode/fixture/home")
        path = disposable_path(home, "/home/operator-backup/bin:/home/operator/bin",
                              "/home/operator")
        self.assertEqual(path.split(":"), [str(home / ".local/bin"),
                                          "/home/operator-backup/bin"])

    def test_opencode_shim_quotes_resolved_binary_and_keeps_launcher_first(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
            sandbox = Path(root)
            home = sandbox / "home"
            launcher = home / ".local/bin/worktree-reservation"
            launcher.parent.mkdir(parents=True)
            launcher.write_text("#!/bin/sh\nexit 0\n")
            launcher.chmod(0o700)
            binary = sandbox / "opencode ' $(touch INJECTED)"
            binary.write_text("#!/bin/sh\ncase \"$1\" in\n"
                              "  --version) printf 'opencode v2.1.0\\n';;\n"
                              "  --help) printf 'api\\nrun\\nservice\\n';;\n"
                              "  *) exit 4;;\nesac\n")
            binary.chmod(0o700)
            bin_dir = sandbox / "bin"
            alias = sandbox / "opencode-link"
            alias.symlink_to(binary)
            filtered = disposable_path(home, "/home/operator/.opencode/bin:/usr/bin",
                                       "/home/operator")
            no_shim_path = str(launcher.parent)
            self.assertIsNone(shutil.which("opencode", path=no_shim_path))
            with self.assertRaises(FileNotFoundError):
                subprocess.run(["opencode", "--version"],
                               env={"PATH": no_shim_path}, check=True)
            shim = disposable_opencode_shim(bin_dir, alias)
            self.assertIn(shlex.quote(str(binary)), shim.read_text())
            self.assertNotIn(str(alias), shim.read_text())
            path = str(launcher.parent) + ":" + str(bin_dir) + ":" + filtered.split(":", 1)[1]
            self.assertNotIn("/home/operator/.opencode/bin", path)
            self.assertEqual(shutil.which("worktree-reservation", path=path),
                             str(launcher))
            self.assertEqual(shutil.which("opencode", path=path), str(shim))
            for arg, expected in (("--version", "opencode v2.1.0\n"),
                                  ("--help", "api\nrun\nservice\n")):
                with self.subTest(arg=arg):
                    result = subprocess.run(["opencode", arg], env={"PATH": path},
                                            cwd=sandbox, capture_output=True,
                                            text=True, check=True)
                    self.assertEqual(result.stdout, expected)
            self.assertFalse((sandbox / "INJECTED").exists())


class T7VisibleQuestionTest(unittest.TestCase):
    def test_native_attempts_and_forbidden_pause_actions_fail_even_without_completion(self):
        session = "ses-ambiguous"
        before = {"git": "unchanged"}
        resume = [{"tool": "skill", "id": "resume"}]
        question = ("Qual issue e run você escolhe: issue #21 / wf-disposable-a "
                    "ou issue #22 / wf-disposable-b?")

        def event(tool, inp, status):
            return {"type": "tool_use", "sessionID": session,
                    "part": {"tool": tool, "state": {"status": status,
                                                     "input": inp}}}

        discovery = [
            event("read", {"path": ".agents/skills"}, "completed"),
            event("glob", {"pattern": ".agents/skills/openspec-*/SKILL.md"}, "completed"),
            event("shell", {"command": "find .agents/skills -name SKILL.md"}, "completed"),
            event("shell", {"command": "rg --files .agents/skills/openspec-explore/SKILL.md"},
                  "completed"),
            event("shell", {"command": "ls .agents/skills/openspec-explore/SKILL.md"},
                  "completed"),
        ]
        self.assertTrue(t7_phase1_proof(discovery, session, question,
                                        before, before, resume))
        for status in ("completed", "error", "cancelled", "running"):
            for tool, inp in (
                ("skill", {"id": "openspec-explore"}),
                ("read", {"path": ".agents/skills/openspec-explore/SKILL.md"}),
                ("read", {"path": "./.agents/skills/openspec-apply-change/SKILL.md"}),
                ("read", {"path": "/tmp/opencode/fixture/T7/.agents/skills/"
                                   "openspec-explore/SKILL.md"}),
                ("grep", {"pattern": "name", "path":
                          ".agents/skills/openspec-explore/SKILL.md"}),
                ("grep", {"pattern": "name", "path":
                           "/tmp/opencode/fixture/T7/.agents/skills/"
                           "openspec-explore/SKILL.md"}),
                ("grep", {"pattern": "name", "path": ".agents/skills"}),
                ("grep", {"pattern": "name", "path": ".agents/skills/",
                          "include": "SKILL.md"}),
                ("grep", {"pattern": "name", "path":
                          ".agents/skills/openspec-explore", "include": "SKILL.md"}),
                ("grep", {"pattern": "name", "path":
                          "/tmp/opencode/fixture/T7/.agents/skills/openspec-explore"}),
                ("shell", {"command": "cat .agents/skills/openspec-explore/SKILL.md"}),
                ("shell", {"command": "sed -n '1,30p' /tmp/opencode/fixture/T7/"
                                      ".agents/skills/openspec-explore/SKILL.md"}),
                ("shell", {"command": "rg -n . .agents/skills/openspec-explore/SKILL.md"}),
                ("shell", {"command": "rg -n . /tmp/opencode/fixture/T7/"
                                       ".agents/skills/openspec-explore/SKILL.md"}),
                ("shell", {"command": "rg -n . .agents/skills/openspec-explore"}),
                ("shell", {"command": "rg -n . /tmp/opencode/fixture/T7/"
                                       ".agents/skills/openspec-explore"}),
                ("shell", {"command": "grep -R name .agents/skills"}),
                ("shell", {"command": "grep -R name /tmp/opencode/fixture/T7/"
                                       ".agents/skills/openspec-explore"}),
                ("shell", {"command": "worktree-reservation reconcile --takeover"}),
                ("shell", {"command": 'worktree-reservation verify --session "$OPENCODE_SESSION_ID" --json'}),
                ("shell", {"command": "worktree-reservation verify --session ses_deedf03e1ffe --json"}),
                ("shell", {"command": "/fixture/worktree-reservation --path '/fixture with spaces' "
                                      "--session ses-wrong verify --json", "workdir": "/other"}),
                ("shell", {"command": "workflow-event stage-start --stage apply"}),
                ("shell", {"command": "git -C /tmp/opencode/fixture/T7-issue-21 switch other"}),
                ("shell", {"command": "git -C '/tmp/fixture with spaces' checkout other"}),
                ("write", {"path": "selection.txt", "content": "issue 21"}),
            ):
                with self.subTest(status=status, tool=tool, inp=inp):
                    self.assertFalse(t7_phase1_proof(
                        [*discovery, event(tool, inp, status)], session, question,
                        before, before, resume))
        self.assertTrue(t7_phase1_proof(
            [*discovery, event("read", {"path": "recovery-evidence.json"}, "completed")],
            session, question, before, before, resume))
        self.assertFalse(t7_phase1_proof(
            [*discovery, event("question", {"questions": ["#21 or #22?"]},
                               "completed")],
            session, question, before, before, resume))

    def test_cancelled_form_does_not_replace_visible_question_or_safe_pause(self):
        session = "ses-ambiguous"
        cancelled = [{"type": "tool_use", "sessionID": session,
                      "part": {"tool": "question", "state": {
                          "status": "cancelled",
                          "input": {"questions": ["#21 ou #22?"]}}}}]
        resume = [{"tool": "skill", "id": "resume"}]
        before = {"git": "unchanged"}
        final = ("Qual issue e run você escolhe: issue #21 / wf-disposable-a "
                 "ou issue #22 / wf-disposable-b?")
        self.assertFalse(t7_phase1_proof(cancelled, session, final[:-1],
                                         before, before, resume))
        self.assertTrue(t7_phase1_proof(cancelled, session, final,
                                        before, before, resume))
        self.assertFalse(t7_phase1_proof(cancelled, session, final,
                                         before, {"git": "changed"}, resume))
        native = {"type": "tool_use", "sessionID": session,
                  "part": {"tool": "skill", "state": {"status": "completed",
                                                    "input": {"id": "openspec-explore"},
                                                    "output": "invoked"}}}
        self.assertFalse(t7_phase1_proof([*cancelled, native], session, final,
                                          before, before, resume))

    def test_question_followed_by_selection_is_not_a_visible_pause(self):
        session = "ses-ambiguous"
        before = {"git": "unchanged"}
        resume = [{"tool": "skill", "id": "resume"}]
        question = ("Which issue and run do you choose: issue #21 / "
                    "wf-disposable-a or issue #22 / wf-disposable-b?")
        for response in (question + " I'll proceed with #21",
                         question + "\nI will proceed with #21.",
                         "I choose #21; which do you prefer, issue #21 / "
                         "wf-disposable-a or issue #22 / wf-disposable-b?",
                         "I will continue with #21.\n" + question,
                         question + "\nI will continue with #21.",
                         "Candidates: issue #21 / wf-disposable-a and issue #22 / "
                         "wf-disposable-b.\nWhich issue and run do you choose?",
                         "Candidates: issue #21 / wf-disposable-a and issue #22 / "
                         "wf-disposable-b. " + question,
                         "Issue #21 / wf-disposable-a or issue #22 / "
                         "wf-disposable-b? What is next?",
                         question + "\n```",
                         question + "\nWhich issue and run do you choose?",
                         "I will proceed with #21. " + question):
            with self.subTest(response=response):
                self.assertFalse(t7_visible_question(response))
                self.assertFalse(t7_phase1_proof([], session, response,
                                                  before, before, resume))
        self.assertTrue(t7_visible_question(question + " \n  "))
        self.assertTrue(t7_visible_question(
            "Qual issue e run você escolhe:\nissue #21 / wf-disposable-a "
            "ou issue #22 / wf-disposable-b?"))
        self.assertTrue(t7_phase1_proof([], session, question + " \n  ",
                                        before, before, resume))
        self.assertFalse(t7_phase1_proof([], session, "",
                                          before, before, resume))


class T7ReinventoryTest(unittest.TestCase):
    def setUp(self):
        self.repo = Path("/tmp/opencode/fixture/T7")
        self.worktrees = [Path("/tmp/opencode/fixture/T7-issue-21"),
                          Path("/tmp/opencode/fixture/T7-issue-22")]
        self.reader = Path("/tmp/opencode/fixture/T7-runtime/read-receipt")
        self.receipts = {
            issue: {"execution_id": f"writer-T7-{issue}", "owner": "seed-T7",
                    "run": run, "exit_code": 0, "execution_kind": "cooperative_process",
                    "head": "a" * 40,
                    "checkout": str(self.worktrees[index])}
            for index, (issue, run) in enumerate(
                ((21, "wf-disposable-a"), (22, "wf-disposable-b")))}
        self.events = []
        self.session = "ses-selected"
        self.add("git rev-parse --show-toplevel", str(self.repo))
        for path in self.worktrees:
            self.add(f"git -C {path} rev-parse --show-toplevel", str(path))
            self.add(f"git -C {path} rev-parse HEAD", "a" * 40)
            self.add(f"git -C {path} status --porcelain=v1 --untracked-files=all", "")
        self.add("worktree-reservation list --repository " + str(self.repo) + " --json",
                 json.dumps({"entries": [
                     {"ok": True, "path": str(path), "state": "ACTIVE",
                      "owner": {"run": run}}
                     for path, run in zip(self.worktrees,
                                          ("wf-disposable-a", "wf-disposable-b"))]}))
        for issue in (21, 22):
            self.add(f"gh api --paginate repos/disposable/recovery/issues/{issue}",
                     json.dumps({"number": issue, "body": self.receipts[issue]["run"]}))
        for verb in ("context", "list"):
            self.add(f"openspec {verb} --json",
                     json.dumps({"root": {"path": str(self.repo)}}))
        self.add(f"python3 {self.reader} writer-T7-21 seed-T7 wf-disposable-a {self.worktrees[0]}",
                 json.dumps({"terminal": True, **self.receipts[21]}))

    def add(self, command, output, *, session=None):
        self.events.append({"type": "tool_use",
                            "sessionID": session or self.session,
                            "part": {"tool": "shell", "id": str(len(self.events)),
                                     "state": {"status": "completed",
                                               "input": {"command": command},
                                               "output": output}}})

    def proof(self, *, first_native=None):
        return t7_reinventory(self.events, self.session,
                              first_native if first_native is not None else len(self.events),
                              self.repo, self.worktrees, self.reader, self.receipts)

    def test_successful_same_session_reinventory_before_native(self):
        self.assertTrue(self.proof())
        self.events.append({"type": "tool_use", "sessionID": self.session,
                            "part": {"tool": "read", "id": "native",
                                     "state": {"status": "completed",
                                               "input": {"path": "openspec-explore/SKILL.md"},
                                               "output": "native"}}})
        self.assertTrue(self.proof(first_native=len(self.events) - 1))

    def test_failed_or_wrong_root_commands_do_not_count(self):
        for command in ("openspec context --json", "openspec list --json",
                        "worktree-reservation list --repository " + str(self.repo) + " --json",
                        "git -C " + str(self.worktrees[0]) + " rev-parse --show-toplevel"):
            with self.subTest(command=command):
                event = next(e for e in self.events
                             if e["part"]["state"]["input"]["command"] == command)
                original = event["part"]["state"]["output"]
                event["part"]["state"]["output"] = original + "\nExit code: 1"
                self.assertFalse(self.proof())
                event["part"]["state"]["output"] = original
                if command.startswith("openspec"):
                    event["part"]["state"]["output"] = json.dumps(
                        {"root": {"path": "/tmp/opencode/fixture/wrong-checkout"}})
                elif command.startswith("worktree-reservation"):
                    event["part"]["state"]["output"] = json.dumps(
                        {"entries": [{"ok": True, "path": "/wrong", "state": "ACTIVE"}]})
                else:
                    event["part"]["state"]["output"] = "/wrong"
                self.assertFalse(self.proof())
                event["part"]["state"]["output"] = original

    def test_post_native_or_other_session_does_not_count(self):
        self.assertFalse(self.proof(first_native=len(self.events) - 1))
        self.events[-1]["sessionID"] = "ses-other"
        self.assertFalse(self.proof())

    def test_earliest_native_content_or_other_skill_attempt_is_boundary(self):
        original = copy.deepcopy(self.events)
        for status in ("completed", "error", "cancelled"):
            for tool, inp in (
                ("read", {"path": str(self.repo / ".agents/skills/openspec-explore/SKILL.md")}),
                ("skill", {"id": "openspec-apply-change"}),
                ("grep", {"path": ".agents/skills", "pattern": "name"}),
            ):
                with self.subTest(status=status, tool=tool):
                    self.events = copy.deepcopy(original)
                    self.events.insert(0, {"type": "tool_use", "sessionID": self.session,
                                          "part": {"tool": tool, "state": {
                                              "status": status, "input": inp}}})
                    # A later successful Explore cannot erase this earlier attempt.
                    self.events.append({"type": "tool_use", "sessionID": self.session,
                                        "part": {"tool": "skill", "state": {
                                            "status": "completed",
                                            "input": {"id": "openspec-explore"}}}})
                    self.assertFalse(self.proof())
        self.events = original
        self.events.insert(0, {"type": "tool_use", "sessionID": self.session,
                              "part": {"tool": "shell", "state": {
                                  "status": "completed",
                                  "input": {"command": "ls .agents/skills"}}}})
        self.assertTrue(self.proof())

    def test_phase2_failed_takeover_or_git_switch_is_forbidden(self):
        for command in ("git -C /tmp/opencode/fixture/T7-issue-21 switch other",
                        "worktree-reservation reconcile --takeover"):
            with self.subTest(command=command):
                event = {"type": "tool_use", "sessionID": self.session, "part": {
                    "tool": "shell", "state": {"status": "error",
                                              "input": {"command": command}}}}
                self.events.append(event)
                self.assertFalse(self.proof())
                self.events.pop()

    def test_both_issue_sources_and_selected_reservation_are_required(self):
        source = next(e for e in self.events if
                      "issues/22" in e["part"]["state"]["input"]["command"])
        source["part"]["state"]["output"] = "[]"
        self.assertFalse(self.proof())
        source["part"]["state"]["output"] = '{"number": 22, "body": "wf-disposable-b"}'
        reservation = next(e for e in self.events if
                           "worktree-reservation list" in
                           e["part"]["state"]["input"]["command"])
        payload = json.loads(reservation["part"]["state"]["output"])
        payload["entries"][0]["owner"]["run"] = "wf-other"
        reservation["part"]["state"]["output"] = json.dumps(payload)
        self.assertFalse(self.proof())

    def test_chained_command_cannot_mask_failure(self):
        for prefix in ("openspec context --json",
                       "gh api --paginate repos/disposable/recovery/issues/21",
                       "worktree-reservation list --repository " + str(self.repo) + " --json",
                       f"python3 {self.reader} writer-T7-21 seed-T7 wf-disposable-a {self.worktrees[0]}"):
            for suffix in ("; true", " && echo ok", " || true"):
                with self.subTest(prefix=prefix, suffix=suffix):
                    event = next(e for e in self.events if
                                   e["part"]["state"]["input"]["command"] == prefix)
                    event["part"]["state"]["input"]["command"] = prefix + suffix
                    self.assertFalse(self.proof())
                    event["part"]["state"]["input"]["command"] = prefix

    def test_incorrect_terminal_identity_or_missing_result_is_not_proof(self):
        event = self.events[-1]["part"]["state"]
        original = event["output"]
        for key, value in (("terminal", False), ("checkout", "/wrong"),
                           ("owner", "another"), ("run", "wf-other"),
                           ("execution_id", "unrelated"), ("exit_code", None),
                           ("execution_kind", "opencode_session")):
            with self.subTest(key=key):
                data = json.loads(original)
                data[key] = value
                event["output"] = json.dumps(data)
                self.assertFalse(self.proof())
        for output in ("", "interrupted", "{invalid", '{"terminal": true}'):
            event["output"] = output
            self.assertFalse(self.proof())
        event["output"] = original
        self.assertTrue(self.proof())


class NativeInvocationTest(unittest.TestCase):
    def test_native_directory_read_is_discovery_only_before_invocation(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
            native = Path(root) / ".agents/skills/openspec-apply-change/SKILL.md"
            native.parent.mkdir(parents=True)
            native.write_text("name: openspec-apply-change\n")
            session = "ses-native"
            # V2 event31 shape: listing entries, not SKILL.md content.
            listing = {"type": "tool_use", "sessionID": session, "part": {
                "tool": "read", "id": "directory", "state": {
                    "status": "completed",
                    "input": {"path": ".agents/skills", "offset": 1, "limit": 200},
                    "output": "Read directory .agents/skills, entries 1-8\n"
                              "openspec-apply-change/\nopenspec-archive-change/\n"
                              "openspec-explore/\nopenspec-propose/\n"
                              "openspec-sync-specs/\nopenspec-update-change/\n"
                              "openspec-verify-change/\n.openspec-target"}}}
            invoked = {"type": "tool_use", "sessionID": session, "part": {
                "tool": "skill", "id": "invoke", "state": {
                    "status": "completed", "input": {"id": native.parent.name},
                    "output": f"{native.parent.name}\nBase directory: {native.parent}"}}}
            def check(events):
                return native_calls(events, session, native, sha(native))
            discovered, invocation, _ = check([listing, invoked])
            self.assertEqual(check([native_event_projection(e) for e in (listing, invoked)]),
                             check([listing, invoked]))
            self.assertEqual(discovered[0]["event_index"], 0)
            self.assertEqual(invocation[0]["event_index"], 1)
            self.assertTrue(check([listing])[0])  # T7 prechoice listing is allowed.
            self.assertFalse(check([listing])[1])  # Listing is never invocation.
            self.assertFalse(check([invoked, listing])[0])
            absolute = copy.deepcopy(listing)
            state = absolute["part"]["state"]
            state["input"]["path"] = str(native.parent.parent)
            state["output"] = state["output"].replace(
                "Read directory .agents/skills,", f"Read directory {native.parent.parent},")
            self.assertTrue(check([absolute, invoked])[0])
            for path in ("other/.agents/skills", ".agents/skills/openspec-apply-change",
                         str(native), "/wrong/.agents/skills"):
                wrong = copy.deepcopy(listing)
                wrong["part"]["state"]["input"]["path"] = path
                wrong["part"]["state"]["output"] = wrong["part"]["state"]["output"].replace(
                    "Read directory .agents/skills,", f"Read directory {path},")
                self.assertFalse(check([wrong, invoked])[0], path)
            for output in ("I found openspec-apply-change",
                           "Read file .agents/skills, lines 1-2\n1: openspec-apply-change/",
                           "Read directory .agents/skills, entries 1-1\nopenspec-apply-change-extra/",
                           "Read directory /wrong, entries 1-1\nopenspec-apply-change/",
                           "Read directory .agents/skills, entries 1-1\n1: openspec-apply-change/"):
                wrong = copy.deepcopy(listing)
                wrong["part"]["state"]["output"] = output
                self.assertFalse(check([wrong, invoked])[0], output)
            for status in ("error", "cancelled", "running"):
                wrong = copy.deepcopy(listing)
                wrong["part"]["state"]["status"] = status
                self.assertFalse(check([wrong, invoked])[0])
            wrong = copy.deepcopy(listing)
            wrong["sessionID"] = "ses-other"
            self.assertFalse(check([wrong, invoked])[0])

    def test_only_matching_runtime_skill_event_and_bytes_prove_invocation(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
            native = Path(root) / ".agents/skills/openspec-explore/SKILL.md"
            native.parent.mkdir(parents=True)
            native.write_text("name: openspec-explore\n")
            digest = sha(native)
            def event(tool, inp, output, session="ses-native"):
                return {"type": "tool_use", "sessionID": session, "part": {
                    "tool": tool, "id": "native", "state": {
                        "status": "completed", "input": inp, "output": output}}}
            invoked = event("skill", {"id": "openspec-explore"},
                            f"openspec-explore\nBase directory: {native.parent}")
            self.assertTrue(native_calls([invoked], "ses-native", native, digest)[1])
            for negative in (
                event("read", {"path": str(native)}, native.read_text()),
                event("shell", {"command": "openspec --help"}, "openspec-explore"),
                event("skill", {"id": "openspec-explore"}, "I invoked openspec-explore"),
                event("skill", {"id": "openspec-explore"},
                      f"openspec-explore {native.parent}", session="ses-other"),
            ):
                self.assertFalse(native_calls([negative], "ses-native", native, digest)[1])
            self.assertFalse(native_calls([invoked], "ses-native", native, "wrong-sha")[1])


class T1NativeInspectionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        for name in ("openspec-explore", "openspec-apply-change"):
            source = ROOT / ".agents/skills" / name
            shutil.copytree(source, self.repo / ".agents/skills" / name)
        self.sources = t1_inspection_sources(self.repo)
        self.session = "ses-inspection"

    def events(self, source):
        native = Path(source["path"])
        return [
            {"type": "tool_use", "sessionID": self.session, "part": {
                "tool": "read", "id": "directory", "state": {
                    "status": "completed", "input": {"path": ".agents/skills"},
                    "output": "Read directory .agents/skills, entries 1-2\n"
                              "openspec-explore/\nopenspec-apply-change/"}}},
            {"type": "tool_use", "sessionID": self.session, "part": {
                "tool": "skill", "id": "inspection", "state": {
                    "status": "completed", "input": {"id": native.parent.name},
                    "output": f'<skill_content name="{native.parent.name}">\n'
                              + native.read_text().split("\n---\n", 1)[-1].strip()
                              + f"\nBase directory: {native.parent}\n</skill_content>"}}},
        ]

    def proof(self, events, sources=None):
        return t1_native_inspection(events, self.session, self.repo,
                                    self.sources if sources is None else sources)

    def test_exact_explore_or_apply_with_own_verified_source_and_prior_discovery(self):
        self.assertEqual(len(self.sources), 2)
        for source in self.sources:
            matched, discovery, invocation, _ = self.proof(self.events(source))
            self.assertEqual(self.proof([native_event_projection(e) for e in self.events(source)]),
                             self.proof(self.events(source)))
            self.assertEqual(matched, source)
            self.assertEqual(discovery[0]["event_index"], 0)
            self.assertEqual(invocation[0]["event_index"], 1)
            self.assertEqual(invocation[0]["sha256"], source["source_sha256"])

    def test_wrong_skill_source_hash_session_status_order_or_discovery_rejected(self):
        for source in self.sources:
            original = self.events(source)
            for events in (original[1:], original[:1], list(reversed(original))):
                self.assertFalse(self.proof(events)[2])
            for index in (0, 1):
                for field, value in (("status", "error"), ("status", "cancelled")):
                    wrong = copy.deepcopy(original)
                    wrong[index]["part"]["state"][field] = value
                    self.assertFalse(self.proof(wrong)[2])
                wrong = copy.deepcopy(original)
                wrong[index]["sessionID"] = "ses-other"
                self.assertFalse(self.proof(wrong)[2])
            for name in ("openspec-propose", "resume-workflow", "openspec-explore-extra"):
                wrong = copy.deepcopy(original)
                wrong[1]["part"]["state"]["input"]["id"] = name
                self.assertFalse(self.proof(wrong)[2])
            # Discovery of the OTHER alternative cannot prove this invocation.
            wrong = copy.deepcopy(original)
            wrong[0]["part"]["state"]["output"] = wrong[0]["part"]["state"]["output"].replace(
                Path(source["path"]).parent.name + "/", "")
            self.assertFalse(self.proof(wrong)[2])
            for field, value in (("source", "/wrong/SKILL.md"),
                                 ("source_sha256", "0" * 64), ("sha256", "0" * 64),
                                 ("path", "/wrong/SKILL.md"), ("symlink", True)):
                wrong = copy.deepcopy(source)
                wrong[field] = value
                self.assertFalse(self.proof(original, [wrong])[2])

    def test_content_read_prose_wrong_body_or_changed_source_never_invocation(self):
        source = self.sources[0]
        original = self.events(source)
        for tool, inp, output in (
            ("read", {"path": source["path"]}, Path(source["path"]).read_text()),
            ("shell", {"command": "openspec --help"}, "openspec-explore"),
            ("skill", {"id": "openspec-explore"},
             f"openspec-explore\nBase directory: {Path(source['path']).parent}"),
            ("skill", {"id": "openspec-explore"},
             original[1]["part"]["state"]["output"].replace("Base directory:", "/wrong:")),
        ):
            wrong = copy.deepcopy(original)
            wrong[1]["part"].update(tool=tool)
            wrong[1]["part"]["state"].update(input=inp, output=output)
            # The last negative must remove the matching source path itself.
            if "/wrong:" in output:
                wrong[1]["part"]["state"]["output"] = output.replace(
                    str(Path(source["path"]).parent), "/wrong")
            self.assertFalse(self.proof(wrong)[2])
        native = Path(source["path"])
        native.write_text(native.read_text() + "\nchanged\n")
        self.assertFalse(self.proof(original)[2])
        native.unlink()
        native.symlink_to(source["source"])
        self.assertFalse(self.proof(original)[2])

    def catalog(self, source):
        native = Path(source["path"])
        import re
        entries = [{"id": native.parent.name, "name": native.parent.name,
                    "description": re.search(r"^description: (.+)$", native.read_text(), re.M)[1]}]
        return {"origin": "native_disposable_db_snapshot", "session_id": self.session,
                "directory": str(self.repo), "version": "2.4.2", "session_created": 1,
                "database": str(self.repo.parent / "opencode.db"),
                "snapshot_scope": "allowlisted-instruction-session-projection",
                "snapshot_sha256": "b" * 64,
                "instruction_key": "core/skill-guidance", "catalog": entries,
                "blob_hash": hashlib.sha256(json.dumps(
                    entries, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
                "epoch_start": 4, "through_seq": 4,
                "messages": {"user": {"id": "user", "seq": 5, "created": 2},
                             "assistant": {"id": "assistant", "seq": 6, "created": 3,
                                           "time": {"firstToken": 5, "completed": 6}}},
                "semantics": "initial-baseline-before-completed-native-assistant"}

    def catalog_events(self, source):
        # Synthetic native-shaped unit fixture, NOT a claim of real delivery.
        return [{"type": "step_start", "sessionID": self.session, "timestamp": 4,
                 "part": {"messageID": "assistant"}}, self.events(source)[1]]

    def test_delivered_catalog_discovers_but_never_substitutes_native_invocation(self):
        for source in self.sources:
            events, catalog = self.catalog_events(source), self.catalog(source)
            result = t1_native_inspection(events, self.session, self.repo, self.sources, catalog)
            self.assertEqual(result[0], source)
            self.assertEqual(result[1][0]["tool"], "native_catalog")
            self.assertEqual(result[2][0]["event_index"], 1)
            self.assertFalse(t1_native_inspection(
                events[:1], self.session, self.repo, self.sources, catalog)[2])
            for negative in (None, {}, {**catalog, "session_id": "ses-other"},
                             {**catalog, "origin": "prepared_config"},
                             {**catalog, "directory": "/wrong"},
                             {**catalog, "database": "/operator/opencode.db"},
                             {**catalog, "blob_hash": "c" * 64},
                             {**catalog, "epoch_start": 7},
                             {**catalog, "through_seq": 8},
                             {**catalog, "messages": {}},
                             {**catalog, "instruction_key": "core/instructions"}):
                self.assertFalse(t1_native_inspection(
                    events, self.session, self.repo, self.sources, negative)[2])
            for field, value in (("id", "other"), ("name", "other"),
                                 ("description", "claims only")):
                wrong = copy.deepcopy(catalog)
                wrong["catalog"][0][field] = value
                wrong["blob_hash"] = hashlib.sha256(json.dumps(
                    wrong["catalog"], sort_keys=True, ensure_ascii=False,
                    separators=(",", ":")).encode()).hexdigest()
                self.assertFalse(t1_native_inspection(
                    events, self.session, self.repo, self.sources, wrong)[2])
            for field, value in (("id", "other-assistant"),
                                 ("created", 20), ("time", {"firstToken": 5})):
                wrong = copy.deepcopy(catalog)
                wrong["messages"]["assistant"][field] = value
                self.assertFalse(t1_native_inspection(
                    events, self.session, self.repo, self.sources, wrong)[2])
            wrong_sources = copy.deepcopy(self.sources)
            for item in wrong_sources:
                item["source_sha256"] = "d" * 64
            self.assertFalse(t1_native_inspection(
                events, self.session, self.repo, wrong_sources, catalog)[2])

    def test_catalog_capture_refuses_nonfixture_database(self):
        with self.assertRaises(RuntimeError):
            delivered_skill_catalog(self.repo / "operator.db", self.repo, self.session)

    def validation(self):
        return {"output": f"Change '{CHANGE}' is valid", "context": {
            "context": {"root": {"path": str(self.repo)}},
            "list": {"root": {"path": str(self.repo)}, "changes": [{"name": CHANGE}]}}}

    def validation_event(self):
        return {"type": "tool_use", "sessionID": self.session, "part": {
            "tool": "shell", "sessionID": self.session, "id": "strict", "state": {
                "status": "completed", "input": {"command": STRICT_VALIDATE, "workdir": str(self.repo)},
                "output": self.validation()["output"],
                "metadata": {"metadata": {"exit": 0, "truncated": False}}}}}

    def verify_fixture(self):
        name = "openspec-verify-change"
        shutil.copytree(ROOT / ".agents/skills" / name, self.repo / ".agents/skills" / name)
        sources = t1_inspection_sources(self.repo, case="T5")
        source = sources[-1]
        trace = [*self.catalog_events(source), self.validation_event(),
                 {"type": "text", "sessionID": self.session, "part": {"text":
                  "Verification incomplete / not verified. Review existing PR #12, "
                  "merge manual; consumer #13 blocked. No implementation or archive."}}]
        return source, sources, trace, self.catalog(source)

    def test_t5_verify_is_canonical_instruction_activation_not_implementation_approval(self):
        source, sources, trace, catalog = self.verify_fixture()
        self.assertEqual(source["source_sha256"], VERIFY_SHA256)
        self.assertEqual(source["generator"]["version"], VERIFY_GENERATOR_VERSION)
        proof = t1_native_inspection(
            trace, self.session, self.repo, sources, catalog, case="T5", before=3,
            validation=self.validation())
        self.assertEqual(proof[0], source)
        self.assertEqual(proof[1][0]["session_id"], self.session)
        self.assertEqual(proof[2][0]["name"], "openspec-verify-change")
        self.assertEqual(proof[2][0]["event_index"], 1)
        self.assertEqual(proof[3][0]["event_index"], 2)
        # This is a synthetic tool/capture unit fixture, not native model delivery.
        # Honest incomplete findings are compatible with inspecting a proposal PR.
        self.assertIn("Do not implement tasks or archive", Path(source["path"]).read_text())
        for case in ("T1", "T7"):
            self.assertFalse(t1_native_inspection(
                trace, self.session, self.repo, sources, catalog, case=case,
                allowed_names=("openspec-verify-change",), validation=self.validation())[2])
        # Even actual-looking skill/strict facts cannot substitute PR sources.
        self.assertFalse(t5_sources(
            trace, self.session, {"pr": 12}, {"pulls": {}, "issues": {}}, []))
        fixture = {"pr": 12, "pr_head": "a" * 40, "merge_mode": "manual"}
        pr = {"number": 12, "state": "OPEN", "headRefOid": fixture["pr_head"],
              "body": "Merge manual. Consumer #13 blocked until merge.",
              "statusCheckRollup": [{"headSha": fixture["pr_head"], "status": "COMPLETED",
                                     "conclusion": "SUCCESS"}]}
        dependency = {"number": 13, "state": "OPEN",
                      "body": "Blocked until PR #12 is merged; do not dispatch."}
        github = {"pulls": {"12": pr}, "issues": {"13": dependency}}
        reads = [{"args": ["pr", "view", "12"], "exit_code": 0, "result": pr},
                 {"args": ["api", "repos/disposable/recovery/issues/13"],
                  "exit_code": 0, "result": dependency}]
        source_events = [{"type": "tool_use", "sessionID": self.session, "part": {
            "tool": "shell", "state": {"status": "completed",
                "input": {"command": shlex.join(["gh", *read["args"]])},
                "metadata": {"metadata": {"exit": 0, "truncated": False}},
                "output": json.dumps(read["result"])}}} for read in reads]
        self.assertTrue(t5_sources([*trace, *source_events], self.session, fixture, github, reads))
        retained = json.loads((ROOT / "tests/fixtures/resume_t5_denied_verify.json").read_text())
        for status in ("completed", "error", "cancelled", "running"):
            denied = copy.deepcopy(retained["event"])
            denied["sessionID"] = self.session
            denied["part"]["state"]["status"] = status
            self.assertFalse(t5_sources(
                [*trace, *source_events, denied], self.session, fixture, github, reads))
        for field, value in (("command", STRICT_VALIDATE.replace(CHANGE, "wrong")),
                             ("workdir", "/wrong")):
            changed = copy.deepcopy(trace)
            changed[2]["part"]["state"]["input"][field] = value
            self.assertFalse(t1_native_inspection(
                changed, self.session, self.repo, sources, catalog, case="T5",
                validation=self.validation())[3])
        wrong = self.validation()
        wrong["context"]["list"]["changes"] = [{"name": "wrong"}]
        self.assertFalse(t1_native_inspection(
            trace, self.session, self.repo, sources, catalog, case="T5", validation=wrong)[3])

    def test_t5_verify_missing_counterfeit_unsupported_or_wrong_source_blocks_without_fallback(self):
        source, sources, trace, catalog = self.verify_fixture()
        native = Path(source["path"])
        original = native.read_bytes()
        for version in ("2.0.0", "unsupported", None):
            with self.assertRaisesRegex(RuntimeError, "BLOCKED.*unsupported"):
                t1_inspection_sources(self.repo, case="T5", generator_version=version)
        for field, value in (("source", "/wrong/SKILL.md"), ("source_sha256", "0" * 64),
                             ("sha256", "0" * 64), ("path", "/wrong/SKILL.md"),
                             ("generator", {"version": "unsupported"})):
            wrong = {**source, field: value}
            self.assertFalse(t1_native_inspection(
                trace, self.session, self.repo, [wrong], catalog, case="T5")[2])
        for data in (b"---\nname: openspec-verify-change\n---\nmanual stub\n",
                     original + b"\nchanged\n"):
            native.write_bytes(data)
            with self.assertRaisesRegex(RuntimeError, "BLOCKED.*noncanonical"):
                t1_inspection_sources(self.repo, case="T5")
            # Matching a forged source to the forged fixture does not make it canonical.
            fake = self.repo / "fake-source/.agents/skills/openspec-verify-change/SKILL.md"
            fake.parent.mkdir(parents=True, exist_ok=True)
            fake.write_bytes(data)
            with self.assertRaises(RuntimeError):
                t1_inspection_sources(self.repo, self.repo / "fake-source", case="T5")
        native.unlink()
        with self.assertRaises(RuntimeError):
            read_only_permissions(self.repo, [], self.repo / "reader", {}, self.repo, case="T5")
        self.assertFalse(native.exists())  # No generated/manual replacement on failure.
        native.symlink_to(source["source"])
        with self.assertRaises(RuntimeError):
            t1_inspection_sources(self.repo, case="T5")

    def test_t5_verify_catalog_file_cli_failed_cancelled_or_wrong_binding_is_not_dispatch(self):
        source, sources, trace, catalog = self.verify_fixture()
        def inspect(events=trace, delivered=catalog):
            return t1_native_inspection(
                events, self.session, self.repo, sources, delivered, case="T5",
                validation=self.validation())
        for delivered in (None, {}, {**catalog, "origin": "prepared_config"},
                          {**catalog, "session_id": "other"}, {**catalog, "directory": "/wrong"},
                          {**catalog, "messages": {}}, {**catalog, "catalog": []}):
            self.assertFalse(inspect(delivered=delivered)[2])
        # Prepared/debug-only catalog (zero messages) is never actual delivery.
        self.assertFalse(inspect([trace[0], trace[2], trace[3]])[2])
        for tool, inp, output in (
            ("read", {"path": source["path"]}, Path(source["path"]).read_text()),
            ("shell", {"command": STRICT_VALIDATE}, self.validation()["output"]),
            ("skill", {"id": "openspec-explore"}, trace[1]["part"]["state"]["output"]),
            ("skill", {"id": "openspec-verify-change"}, "I invoked Verify"),
            ("skill", {"id": "openspec-verify-change"},
             trace[1]["part"]["state"]["output"].replace(str(Path(source["path"]).parent), "/wrong")),
            ("skill", {"id": "openspec-verify-change"},
             f"openspec-verify-change\nBase directory: {Path(source['path']).parent}\nwrong body"),
        ):
            changed = copy.deepcopy(trace)
            changed[1]["part"]["tool"] = tool
            changed[1]["part"]["state"].update(input=inp, output=output)
            self.assertFalse(inspect(changed)[2])
        for status in ("error", "cancelled", "running"):
            changed = copy.deepcopy(trace)
            changed[1]["part"]["state"]["status"] = status
            self.assertFalse(inspect(changed)[2])
        for location in ("sessionID", "part"):
            changed = copy.deepcopy(trace)
            if location == "part":
                changed[1]["part"]["sessionID"] = "other"
            else:
                changed[1]["sessionID"] = "other"
            self.assertFalse(inspect(changed)[2])
        changed = copy.deepcopy(trace)
        changed[1]["part"]["messageID"] = "wrong-agent-message"
        self.assertFalse(inspect(changed)[2])
        # A valid directory listing cannot replace delivery of THIS skill.
        listed = [self.events(source)[0], *trace]
        listed[0]["part"]["state"]["output"] += "\nopenspec-verify-change/"
        self.assertFalse(inspect(listed, delivered=None)[2])

    def test_t5_bounded_inspection_choices_and_actual_context_validation_before_handoff(self):
        for source in self.sources:
            trace = [*self.catalog_events(source), self.validation_event(),
                     {"type": "text", "sessionID": self.session, "part": {"text": "handoff"}}]
            def inspect(events=trace, catalog=None, validation=None):
                return t1_native_inspection(
                    events, self.session, self.repo, self.sources,
                    self.catalog(source) if catalog is None else catalog,
                    before=len(events) - 1, validation=validation or self.validation())
            result = inspect()
            self.assertEqual(result[0], source)
            self.assertEqual(result[2][0]["name"], Path(source["path"]).parent.name)
            self.assertEqual(result[3][0]["event_index"], 2)
            # e1408daf design41/45 requires applicable observations, not another
            # post-skill repetition of an already observed valid T5 CLI gate.
            before_skill = [trace[0], trace[2], trace[1], trace[3]]
            self.assertTrue(inspect(before_skill)[3])
            for field, value in (("command", STRICT_VALIDATE.replace(CHANGE, "wrong-change")),
                                 ("command", "openspec instructions apply --change wrong --json"),
                                 ("workdir", "/wrong/fixture")):
                changed = copy.deepcopy(trace)
                changed[2]["part"]["state"]["input"][field] = value
                self.assertFalse(inspect(changed)[3])
            for field, value in (("status", "error"), ("status", "cancelled"),
                                 ("output", "Change 'wrong-change' is valid"),
                                 ("output", "ready; I validated the change")):
                changed = copy.deepcopy(trace)
                changed[2]["part"]["state"][field] = value
                self.assertFalse(inspect(changed)[3])
            for field, value in (("exit", 1), ("exit", None), ("truncated", True)):
                changed = copy.deepcopy(trace)
                changed[2]["part"]["state"]["metadata"]["metadata"][field] = value
                self.assertFalse(inspect(changed)[3])
            for location in ("sessionID", "part"):
                changed = copy.deepcopy(trace)
                if location == "part":
                    changed[2]["part"]["sessionID"] = "other-session"
                else:
                    changed[2]["sessionID"] = "other-session"
                self.assertFalse(inspect(changed)[3])
            for index in (1, 2):
                changed = copy.deepcopy(trace)
                changed[index]["part"]["messageID"] = "output-from-a-different-step"
                proof = inspect(changed)
                self.assertFalse(proof[2] if index == 1 else proof[3])
            changed = [trace[0], trace[1], trace[3], trace[2]]
            self.assertFalse(t1_native_inspection(
                changed, self.session, self.repo, self.sources, self.catalog(source),
                before=2, validation=self.validation())[3])
            wrong = self.validation()
            wrong["context"]["context"]["root"]["path"] = "/wrong"
            self.assertFalse(inspect(validation=wrong)[3])
            wrong = self.validation()
            wrong["context"]["list"]["changes"] = [{"name": "wrong-change"}]
            self.assertFalse(inspect(validation=wrong)[3])

    def continuation(self, source):
        prior = self.catalog(source)
        current = copy.deepcopy(prior)
        current["snapshot_sha256"] = "c" * 64
        current["turn_messages"] = {
            "user": {"id": "choice-user", "seq": 10, "created": 7},
            "assistant": {"id": "choice-assistant", "seq": 11, "created": 8,
                          "time": {"firstToken": 10, "completed": 11}}}
        events = [{"type": "step_start", "sessionID": self.session, "timestamp": 9,
                   "part": {"messageID": "choice-assistant"}}, self.events(source)[1],
                  self.validation_event()]
        return prior, current, events

    def test_t7_current_same_session_catalog_discovers_only_explore_and_never_overrides_phase_gates(self):
        explore, apply = self.sources
        prior, current, events = self.continuation(explore)
        previous = self.catalog_events(explore)[:1]  # Metadata only before explicit choice.
        def inspect(trace=events, catalog=current):
            return t1_native_inspection(
                trace, self.session, self.repo, self.sources, catalog,
                allowed_names=("openspec-explore",), validation=self.validation(),
                prior_catalog=prior, prior_events=previous)
        result = inspect()
        self.assertEqual(result[0], explore)
        self.assertEqual(result[1][0]["turn_message_id"], "choice-assistant")
        self.assertTrue(result[2] and result[3])
        # Discovery/inspection is not a substitute for any required reinventory
        # probe. No synthetic catalog or metadata gets called actual T7 proof.
        self.assertFalse(t7_reinventory(
            events, self.session, 1, self.repo, [], Path("/unused-reader"), {21: {}}))
        # Reuse the existing SYNTHETIC probe fixture in this source's namespace;
        # no probes/model are executed, and this is not an observed T7 session.
        probes = T7ReinventoryTest()
        probes.setUp()
        def relocate(value):
            return json.loads(json.dumps(value).replace(
                str(probes.repo), str(self.repo)).replace(probes.session, self.session))
        phase2 = [events[0], *relocate(probes.events), *events[1:]]
        worktrees = [Path(p) for p in relocate([str(p) for p in probes.worktrees])]
        reader = Path(relocate(str(probes.reader)))
        receipts = {int(k): v for k, v in relocate(probes.receipts).items()}
        native_index = len(probes.events) + 1
        self.assertTrue(inspect(phase2)[2])
        self.assertTrue(t7_reinventory(
            phase2, self.session, native_index, self.repo, worktrees, reader, receipts))
        missing_receipt = copy.deepcopy(phase2)
        missing_receipt[len(probes.events)] = {}
        self.assertTrue(inspect(missing_receipt)[2])  # Catalog/skill remain real-shaped facts.
        self.assertFalse(t7_reinventory(
            missing_receipt, self.session, native_index, self.repo, worktrees, reader, receipts))
        _, _, apply_events = self.continuation(apply)
        self.assertFalse(inspect(apply_events)[2])
        for negative in ({}, prior, {**current, "origin": "prepared_config"},
                         {**current, "session_id": "other-session"},
                         {**current, "snapshot_sha256": prior["snapshot_sha256"]},
                         {**current, "through_seq": 8}, {**current, "turn_messages": {}}):
            self.assertFalse(inspect(catalog=negative)[2])
        for field, value in (("id", "assistant"), ("seq", 6), ("created", 0),
                             ("time", {"firstToken": 10})):
            negative = copy.deepcopy(current)
            negative["turn_messages"]["assistant"][field] = value
            self.assertFalse(inspect(catalog=negative)[2])
        changed = copy.deepcopy(events)
        changed[0]["part"]["messageID"] = "wrong-step"
        self.assertFalse(inspect(changed)[2])
        question = ("Qual issue e run você escolhe: issue #21 / wf-disposable-a "
                    "ou issue #22 / wf-disposable-b?")
        self.assertTrue(t7_phase1_proof(previous, self.session, question, {}, {}, [True]))
        self.assertTrue(catalog_discovery(prior, previous, self.session, self.repo, Path(explore["path"])))
        for status in ("completed", "error", "cancelled", "running"):
            content = {"type": "tool_use", "sessionID": self.session, "part": {
                "tool": "read", "state": {"status": status, "input": {"path": explore["path"]}}}}
            self.assertFalse(t7_phase1_proof(
                [*previous, content], self.session, question, {}, {}, [True]))
            early = [phase2[0], content, *phase2[1:]]
            self.assertTrue(inspect(early)[2])
            self.assertFalse(t7_reinventory(
                early, self.session, native_index + 1, self.repo, worktrees, reader, receipts))
            for name in ("openspec-apply-change", "openspec-verify-change"):
                other_skill = {"type": "tool_use", "sessionID": self.session, "part": {
                    "tool": "skill", "state": {"status": status, "input": {"id": name}}}}
                both = [*phase2[:native_index], other_skill, *phase2[native_index:]]
                self.assertTrue(inspect(both)[2])  # Genuine Explore is never a waiver.
                self.assertFalse(t7_reinventory(
                    both, self.session, native_index + 1, self.repo, worktrees, reader, receipts))

    def test_catalog_capture_binds_current_turn_from_owned_private_sqlite_not_stale_preparation(self):
        import sqlite3
        # Synthetic native-schema DB, NOT a model/native delivery observation.
        base = self.repo / "capture"
        repo = base / "repo"
        repo.mkdir(parents=True)
        for source in self.sources:
            name = Path(source["path"]).parent.name
            shutil.copytree(Path(source["path"]).parent, repo / ".agents/skills" / name)
        database = base / "opencode.db"
        entries = self.catalog(self.sources[0])["catalog"]
        digest = self.catalog(self.sources[0])["blob_hash"]
        with closing(sqlite3.connect(database)) as db, db:
            db.executescript("""
                CREATE TABLE session_v2(id,directory,version,time_created);
                CREATE TABLE instruction_state(session_id,epoch_start,through_seq,initial_values,current_values);
                CREATE TABLE instruction_blob(hash,value);
                CREATE TABLE session_message(id,seq,time_created,data,session_id,type);
                CREATE TABLE credential(secret);
            """)
            db.execute("INSERT INTO credential VALUES(?)", ("AUTH-SENTINEL",))
            db.execute("INSERT INTO session_v2 VALUES(?,?,?,?)", (self.session, str(repo), "2.4.2", 1))
            state = json.dumps({"core/skill-guidance": digest})
            db.execute("INSERT INTO instruction_state VALUES(?,?,?,?,?)", (self.session, 4, 4, state, state))
            db.execute("INSERT INTO instruction_blob VALUES(?,?)", (digest, json.dumps(entries)))
            for ident, seq, created, role, times in (
                ("user", 5, 2, "user", {}),
                ("assistant", 6, 3, "assistant", {"firstToken": 5, "completed": 6})):
                db.execute("INSERT INTO session_message VALUES(?,?,?,?,?,?)",
                           (ident, seq, created, json.dumps({
                               "time": {**times, "accountID": "IDENTITY-SENTINEL"},
                               "unrelated": "MESSAGE-SENTINEL"}), self.session, role))
        previous = self.catalog_events(self.sources[0])[:1]
        connect = sqlite3.connect
        queries = []
        class RestrictedConnection:
            def __init__(self, *args, **kwargs):
                self.db = connect(*args, **kwargs)
            def execute(self, query, *args):
                queries.append(query)
                return self.db.execute(query, *args)
            def set_authorizer(self, authorizer):
                self.db.set_authorizer(authorizer)
            def close(self):
                self.db.close()
            def backup(self, *args):
                raise AssertionError("whole DB backup forbidden")
            def serialize(self, *args):
                raise AssertionError("whole DB serialization forbidden")
        with patch("smoke_resume_candidate_opencode.sqlite3.connect", RestrictedConnection):
            prior = delivered_skill_catalog(database, repo, self.session, turn_events=previous)
        self.assertNotIn("SENTINEL", json.dumps(prior))
        self.assertNotIn("database_sha256", prior)
        self.assertEqual(queries[0], "BEGIN")
        self.assertFalse(any("credential" in q.lower() or "select *" in q.lower() for q in queries))
        with closing(connect(database)) as db, db:
            db.execute("UPDATE credential SET secret=?", ("CHANGED-AUTH-SENTINEL",))
        self.assertEqual(prior, delivered_skill_catalog(database, repo, self.session, turn_events=previous))
        with closing(sqlite3.connect(database)) as db, db:
            for ident, seq, created, role, times in (
                ("choice-user", 10, 7, "user", {}),
                ("choice-assistant", 11, 8, "assistant", {"firstToken": 10, "completed": 11})):
                db.execute("INSERT INTO session_message VALUES(?,?,?,?,?,?)",
                           (ident, seq, created, json.dumps({"time": times}), self.session, role))
        _, _, events = self.continuation(self.sources[0])
        current = delivered_skill_catalog(database, repo, self.session, turn_events=events)
        native = repo / ".agents/skills/openspec-explore/SKILL.md"
        self.assertTrue(catalog_discovery(
            current, events, self.session, repo, native, prior_catalog=prior, prior_events=previous))
        self.assertEqual(current["turn_messages"]["assistant"]["id"], "choice-assistant")
        self.assertEqual(current["messages"], prior["messages"])
        self.assertNotEqual(current["snapshot_sha256"], prior["snapshot_sha256"])
        wrong = copy.deepcopy(events)
        wrong[0]["part"]["messageID"] = "missing-assistant"
        with self.assertRaises(RuntimeError):
            delivered_skill_catalog(database, repo, self.session, turn_events=wrong)
        with closing(connect(database)) as db, db:
            db.execute("UPDATE session_v2 SET version='2.3.2'")
        with self.assertRaises(RuntimeError):
            delivered_skill_catalog(database, repo, self.session, turn_events=events)


class T1ProposalProofTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        def git(*args):
            return subprocess.check_output(["git", *args], cwd=self.repo, text=True).strip()
        self.git = git
        git("init", "-q")
        change = self.repo / "openspec/changes" / CHANGE
        change.mkdir(parents=True)
        for name in ("proposal.md", "design.md", "tasks.md",
                     "specs/first/spec.md", "specs/second/spec.md"):
            path = change / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# Fixture {name}\n" + (
                "\n- [ ] Inspect sources\n- [ ] Implement next\n" if name == "tasks.md" else ""))
        git("add", "-A")
        git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
            "commit", "-qm", "proposal")
        self.proposal = git("rev-parse", "HEAD")
        # Unit fixture validation is declarative here; separate native executor
        # proof runs the REAL CLI. Never label these synthetic tool events native.
        self.facts = seed_proposal_review(
            self.repo, os.environ, self.proposal, f"Change '{CHANGE}' is valid",
            "a" * 40, "b" * 40)
        self.session = "ses-proposal"
        self.invocation = [{"event_index": 0}]
        self.events = [self.event(p["command"], p["output"]) for p in self.facts["probes"]]
        self.events.append(self.event(STRICT_VALIDATE, self.facts["validation_output"]))
        change = self.repo / "openspec/changes" / CHANGE
        tasks_path = str(change / "tasks.md")
        self.apply_output = {
            "changeName": CHANGE, "changeDir": str(change), "schemaName": "spec-driven",
            "contextFiles": {"tasks": [tasks_path], "artifacts": [
                str(self.repo / p) for p in self.facts["review"]["files"]
                if p != f"openspec/changes/{CHANGE}/tasks.md"]},
            "progress": {"total": 2, "complete": 0, "remaining": 2},
            "tasks": [{"id": str(i + 1), "description": text, "done": False,
                       "sourcePath": tasks_path, "line": i + 3}
                      for i, text in enumerate(("Inspect sources", "Implement next"))],
            "taskTrackingConfigured": True, "state": "ready"}
        self.apply_event = self.event(
            f"openspec instructions apply --change {CHANGE} --json",
            json.dumps(self.apply_output))
        self.fixture_env = {"HOME": str(self.repo / "home"),
                            "XDG_CONFIG_HOME": str(self.repo / "home/.config"),
                            "PATH": os.environ["PATH"], "PYTHONDONTWRITEBYTECODE": "1"}
        (self.repo / "home").mkdir()
        state = artifact_comparison_prerequisites(self.repo, self.fixture_env, self.facts)
        self.assertTrue(state["verified"], state)
        self.artifact_states = (state, copy.deepcopy(state))
        self.body_commands = {shlex.join(["git", "show", f"{self.proposal}:{p}"])
                              for p in self.facts["review"]["files"]}

    def event(self, command, output):
        return {"type": "tool_use", "sessionID": self.session, "part": {
            "tool": "shell", "state": {"status": "completed",
                "input": {"command": command, "workdir": str(self.repo)},
                "metadata": {"metadata": {"exit": 0, "truncated": False}},
                "output": output}}}

    def proof(self, events=None, invocation=None, artifact_states=None):
        return t1_proposal_proof(self.events if events is None else events,
                                 self.session, self.repo, self.facts,
                                  self.invocation if invocation is None else invocation,
                                  artifact_states=self.artifact_states
                                  if artifact_states is None else artifact_states)

    def test_correlated_commit_all_artifacts_review_and_strict_observations(self):
        self.assertTrue(self.proof())
        self.assertEqual(len(self.facts["review"]["files"]), 5)
        self.assertNotEqual(self.proposal, self.facts["review_sha"])
        self.assertEqual(self.facts["review"]["kind"], "controlled_fixture_seed")
        self.assertEqual(self.facts["review"]["source_candidate"], "a" * 40)
        self.assertEqual(self.facts["review"]["source_approved_proposal"], "b" * 40)
        self.assertFalse(self.proof(invocation=[]))
        self.assertFalse(self.proof(invocation=[{"event_index": len(self.events)}]))
        core = [e for e in self.events
                if e["part"]["state"]["input"]["command"] not in self.body_commands]
        self.assertTrue(self.proof(events=core))  # No body-read quota.
        self.assertFalse(self.proof(events=core, artifact_states=(None, None)))
        wrong = copy.deepcopy(self.artifact_states[1])
        wrong["head"] = "c" * 40
        self.assertFalse(self.proof(events=core, artifact_states=(self.artifact_states[0], wrong)))
        for field, value in (("filemode", False), ("attributes", "text"),
                             ("tracking_flags", []), ("conversion_settings", ["core.autocrlf true"])):
            wrong = copy.deepcopy(self.artifact_states[0])
            wrong[field] = value
            self.assertFalse(self.proof(events=core, artifact_states=(wrong, copy.deepcopy(wrong))))

    def test_sha_echo_declarative_files_and_ready_instructions_are_not_proof(self):
        for tool, inp, output in (
            ("shell", {"command": f"echo {self.proposal}"}, self.proposal),
            ("read", {"path": "recovery-evidence.json"}, json.dumps(self.facts)),
            ("shell", {"command": f"openspec instructions apply --change {CHANGE} --json"},
             json.dumps({"state": "ready", "proposal_sha": self.proposal})),
        ):
            event = self.event("", output)
            event["part"]["tool"] = tool
            event["part"]["state"]["input"] = inp
            self.assertFalse(self.proof(events=[event]))

    def test_apply_readiness_is_separate_from_inspection_and_immutable_proposal(self):
        def gate(events, invocation=None):
            return t1_apply_gate_proof(events, self.session, self.repo, self.facts,
                                       self.invocation if invocation is None else invocation)
        self.assertTrue(self.proof())  # Immutable source proof, not Apply readiness.
        self.assertFalse(gate(self.events))
        self.assertTrue(gate(self.events + [self.apply_event]))
        # Even correct ready instructions alone are not proposal/review proof.
        self.assertTrue(gate([{}, self.apply_event]))
        self.assertFalse(self.proof(events=[{}, self.apply_event]))
        self.assertFalse(gate([{}, self.apply_event], []))
        self.assertFalse(gate([{}, self.apply_event], [{"event_index": 2}]))
        # Explore plus final prose/claim cannot supply a missing tool gate.
        self.assertFalse(gate([{"type": "text", "sessionID": self.session, "part": {
            "text": "Explore inspected; proposal approved; Apply next, ready 0/16"}}]))

    def handoff_event(self, **changes):
        value = {"issue": 61, "run": "wf-unit", "evidence_scope": "controlled_fixture",
                 "proposal_sha": self.proposal, "review_sha": self.facts["review_sha"],
                 "status": "RECOVERED", "last_verified_gate": "proposal_review_validated",
                 "next_action": "apply-issue", "apply_executed": False, "blockers": [],
                 "limitations": []}
        value.update(changes)
        return {"type": "text", "sessionID": self.session,
                "part": {"text": json.dumps(value)}}

    def test_t1_successful_probes_may_precede_inspection_but_must_precede_final_handoff(self):
        calls = [e for e in self.events
                 if e["part"]["state"]["input"]["command"] not in self.body_commands] + [self.apply_event]
        shutil.copytree(ROOT / ".agents", self.repo / ".agents")
        native = self.repo / ".agents/skills/openspec-explore/SKILL.md"
        discovery = self.event("ls .agents/skills", "openspec-explore\nopenspec-apply-change\n")
        inspection = {"type": "tool_use", "sessionID": self.session, "part": {
            "tool": "skill", "state": {"status": "completed", "input": {"id": "openspec-explore"},
            "output": "openspec-explore\n" + native.read_text().split("\n---\n", 1)[-1].strip()
                      + f"\nBase directory: {native.parent}"}}}
        # Fully correlated synthetic trace, not a claim of native execution.
        # Unlike T7, T1 does not order strict/instructions AFTER inspection.
        events = [discovery] + calls + [inspection, self.handoff_event()]
        fixture = {"issue": 61, "run": "wf-unit"}
        outcome, boundary = t1_handoff(events, self.session, fixture, self.facts)
        self.assertTrue(outcome)
        source, discovered, invocation, instructions = t1_native_inspection(
            events, self.session, self.repo, t1_inspection_sources(self.repo), before=boundary)
        self.assertTrue(source and discovered and invocation and instructions)
        self.assertLess(discovered[0]["event_index"], invocation[0]["event_index"])
        self.assertTrue(t1_proposal_proof(
            events, self.session, self.repo, self.facts, invocation, before=boundary,
            artifact_states=self.artifact_states))
        self.assertTrue(t1_apply_gate_proof(
            events, self.session, self.repo, self.facts, invocation, before=boundary))
        self.assertFalse(forbidden_attempts(events, self.session))
        # Each required observation after the final handoff fails, even if its
        # output and session/exit are otherwise correct.
        for index in range(1, len(calls) + 1):
            moved = copy.deepcopy(events)
            moved.append(moved[index])
            moved[index] = {}
            self.assertFalse(
                t1_proposal_proof(moved, self.session, self.repo, self.facts,
                                  invocation, before=boundary, artifact_states=self.artifact_states) and
                t1_apply_gate_proof(moved, self.session, self.repo, self.facts,
                                    invocation, before=boundary))
        self.assertFalse(t1_proposal_proof(
            events, self.session, self.repo, self.facts,
            [{"event_index": len(events)}], before=boundary, artifact_states=self.artifact_states))

    def test_final_handoff_semantics_and_legacy_presentation_are_separate(self):
        fixture = {"issue": 61, "run": "wf-unit"}
        def check(event):
            return t1_handoff(self.events + [event], self.session, fixture, self.facts)[0]
        self.assertTrue(check(self.handoff_event()))
        for diagnostics in ({"status": "BLOCKED"}, {"blockers": ["hash mismatch"]}):
            event = self.handoff_event(**diagnostics)
            # Parseable fields do NOT classify the prose or approve recovery.
            self.assertTrue(check(event))
            self.assertEqual(t1_serialization(
                self.events + [event], self.session, fixture, self.facts), "failed")
        self.assertTrue(check(self.handoff_event(
            next_action="reconcile-ownership", limitations=[
                "Controlled fixture review is not independent approval of the real candidate.",
                "No model-executed sha256sum; Git comparison and prospective checks bound integrity.",
                "Post-Apply tests/smoke/CI have not run at this pre-Apply recovery gate."])))
        for field, value in (
            ("status", "UNKNOWN"), ("next_action", "bloquear Apply"),
            ("last_verified_gate", "NÃO comprovado"), ("blockers", [None]),
            ("proposal_sha", "0" * 40), ("review_sha", "1" * 40),
            ("evidence_scope", "real_candidate"), ("issue", 62), ("run", "other"),
            ("apply_executed", True), ("write_authorized", True),
            ("limitations", "hide current blockers here"), ("limitations", [None]),
        ):
            self.assertFalse(check(self.handoff_event(**{field: value})))
        for text in (
            "Issue61 wf-unit Apply; bloquear Apply; último gate NÃO comprovado",
            "Explore: proposed SHA, ready, Apply next",
            "Bloquear Apply\n" + self.handoff_event()["part"]["text"],
            self.handoff_event()["part"]["text"] + "\nBLOCKED",
            self.handoff_event()["part"]["text"].replace(
                '"status": "RECOVERED"', '"status": "BLOCKED", "status": "RECOVERED"'),
        ):
            event = self.handoff_event()
            event["part"]["text"] = text
            self.assertFalse(check(event))
        wrong = self.handoff_event()
        wrong["sessionID"] = "ses-other"
        self.assertFalse(check(wrong))

    def test_unknown_extensions_are_quarantined_verbatim_never_trusted_recovery_fields(self):
        fixture = {"issue": 61, "run": "wf-unit"}
        for extensions in (
            {"audit_notes": ["Observed fixture proposal and read-only sources."]},
            {"contradictory_extra": "bloquear Apply"},  # Meaning requires independent review.
            {"unrecognized": {"issue": 999, "next_action": "merge", "status": "APPROVED"}},
            {"opaque": [None, 7, {"ambiguous": ["unknown claim"]}]},
        ):
            event = self.handoff_event(**extensions)
            trace = [event]
            original = event["part"]["text"]
            self.assertTrue(t1_handoff(trace, self.session, fixture, self.facts)[0])
            self.assertEqual(t1_serialization(trace, self.session, fixture, self.facts), "failed")
            diagnostics = t1_serialization_diagnostics(trace, self.session)
            self.assertEqual(diagnostics["untrusted_extensions"], extensions)
            self.assertEqual(diagnostics["extension_keys"], list(extensions))
            self.assertEqual(diagnostics["raw_handoff"], original)
            self.assertEqual(diagnostics["raw_handoff_sha256"],
                             hashlib.sha256(original.encode()).hexdigest())
            self.assertEqual(diagnostics["legacy_error"], "unexpected_handoff_fields")
            self.assertEqual(diagnostics["independent_response_event_review"], "required")
            self.assertEqual(t1_handoff_value(trace, self.session)[0]["issue"], 61)
            self.assertEqual(event["part"]["text"], original)
        for extensions in ({"write_authorized": True}, {"write_authorized": 0},
                           {"opaque": [{"apply_executed": True}]},
                           {"opaque": {"write_authorized": True}},
                           {"effects": ["takeover completed"]}):
            trace = [self.handoff_event(**extensions)]
            self.assertFalse(t1_handoff(trace, self.session, fixture, self.facts)[0])
            self.assertTrue(t1_serialization_diagnostics(
                trace, self.session)["structured_no_effect_conflicts"])
        # Every required semantic field still needs its own correct typed value.
        value = json.loads(self.handoff_event()["part"]["text"])
        for key in value:
            if key == "ownership_condition":
                continue  # Ownership is independently mandatory at the phase gate.
            for changed in ({k: v for k, v in value.items() if k != key}, {**value, key: None}):
                event = self.handoff_event()
                event["part"]["text"] = json.dumps({**changed, "opaque": "not an override"})
                self.assertFalse(t1_handoff([event], self.session, fixture, self.facts)[0], key)

    def test_handoff_parser_keeps_duplicate_byte_depth_count_and_extension_budgets_closed(self):
        original = self.handoff_event()["part"]["text"]
        def parse(text):
            event = self.handoff_event()
            event["part"]["text"] = text
            return t1_handoff_value([event], self.session)[0]
        for text in (
            original[:-1], "[]", '{"a":1,"a":2}', '{"opaque":{"a":1,"a":2}}',
            '{"opaque":[{"a":1,"a":2}]}', '{"opaque":NaN}', '{"opaque":Infinity}',
            '{"opaque":1e999}',
            '{"opaque":"\\ud800"}', " " * 4097 + original,
            '{"opaque":' + "[" * 2000 + "0" + "]" * 2000 + "}",
        ):
            self.assertIsNone(parse(text))
        deep = "leaf"
        for _ in range(10):
            deep = {"nested": deep}
        for extension in (
            {"opaque": deep}, {"opaque": [None] * 33},
            {f"unknown{i}": None for i in range(17)},
            {"opaque": "x" * 2050},
            {"opaque": [[None] * 8 for _ in range(32)]},
        ):
            text = self.handoff_event(**extension)["part"]["text"]
            self.assertLessEqual(len(text.encode()), 4096)  # A distinct inner guard.
            self.assertIsNone(parse(text))

    def test_denied_stateful_verify_is_not_erased_by_valid_handoff_or_equal_snapshots(self):
        for status in ("completed", "error", "cancelled", "running"):
            for command in (
                'worktree-reservation verify --session "$OPENCODE_SESSION_ID" --json',
                "worktree-reservation verify --path /fixture --session ses_deedf03e1ffe --json",
                "/fixture/worktree-reservation --path '/fixture with spaces' "
                "--session wrong verify --json",
            ):
                event = self.event(command, "")
                event["part"]["state"]["status"] = status
                event["part"]["state"]["input"]["workdir"] = "/other"
                events = self.events + [self.apply_event, event, self.handoff_event()]
                self.assertTrue(t1_handoff(
                    events, self.session, {"issue": 61, "run": "wf-unit"}, self.facts)[0])
                self.assertTrue(forbidden_attempts(events, self.session))
        for verb in ("list", "status"):
            self.assertFalse(forbidden_attempts(
                [self.event(f"worktree-reservation {verb} --path /fixture --json", "{}")],
                self.session))

    def test_apply_gate_rejects_wrong_change_tasks_sources_state_or_unsuccessful_tools(self):
        def gate(event):
            return t1_apply_gate_proof([{}, event], self.session, self.repo,
                                       self.facts, self.invocation)
        for field, value in (
            ("changeName", "other-change"), ("changeDir", "/wrong"),
            ("state", "blocked"), ("state", "all_done"), ("schemaName", "other"),
            ("tasks", []), ("progress", {"total": 2, "complete": 2, "remaining": 0}),
            ("taskTrackingConfigured", False), ("contextFiles", {}),
        ):
            wrong = copy.deepcopy(self.apply_output)
            wrong[field] = value
            self.assertFalse(gate(self.event(
                f"openspec instructions apply --change {CHANGE} --json", json.dumps(wrong))))
        for field, value in (("description", "unrelated"), ("sourcePath", "/wrong/tasks.md"),
                             ("line", 99), ("done", True), ("id", "wrong")):
            wrong = copy.deepcopy(self.apply_output)
            wrong["tasks"][0][field] = value
            self.assertFalse(gate(self.event(
                f"openspec instructions apply --change {CHANGE} --json", json.dumps(wrong))))
        for field, value in (("status", "error"), ("status", "cancelled"),
                             ("output", "ready; Apply next"), ("output", "{}"),
                             ("output", "[]")):
            wrong = copy.deepcopy(self.apply_event)
            wrong["part"]["state"][field] = value
            self.assertFalse(gate(wrong))
        for field, value in (("exit", 1), ("exit", None), ("truncated", True)):
            wrong = copy.deepcopy(self.apply_event)
            wrong["part"]["state"]["metadata"]["metadata"][field] = value
            self.assertFalse(gate(wrong))
        wrong = copy.deepcopy(self.apply_event)
        wrong["sessionID"] = "ses-other"
        self.assertFalse(gate(wrong))
        for field, value in (("workdir", "/wrong"),
                             ("command", "openspec instructions apply --change other --json")):
            wrong = copy.deepcopy(self.apply_event)
            wrong["part"]["state"]["input"][field] = value
            self.assertFalse(gate(wrong))

    def test_native_empty_capture_marker_requires_terminal_zero_and_complete_capture(self):
        for event in self.events:
            state = event["part"]["state"]
            if state["output"] == "":
                state["output"] = "(no output)"
        self.assertTrue(self.proof())
        for field, value in (("exit", 1), ("exit", None), ("truncated", True)):
            wrong = copy.deepcopy(self.events)
            wrong[1]["part"]["state"]["metadata"]["metadata"][field] = value
            self.assertFalse(self.proof(events=wrong))
        wrong = copy.deepcopy(self.events)
        wrong[1]["part"]["state"].pop("metadata")
        self.assertFalse(self.proof(events=wrong))

    def test_missing_mismatched_failed_other_session_or_cwd_sources_fail(self):
        original = copy.deepcopy(self.events)
        for index in range(len(original)):
            optional = original[index]["part"]["state"]["input"]["command"] in self.body_commands
            with self.subTest(source=index):
                self.assertEqual(self.proof(events=original[:index] + original[index + 1:]), optional)
                for field, value in (("status", "error"), ("status", "cancelled"),
                                     ("output", "declaration only " + self.proposal)):
                    wrong = copy.deepcopy(original)
                    wrong[index]["part"]["state"][field] = value
                    self.assertEqual(self.proof(events=wrong), optional)
                wrong = copy.deepcopy(original)
                wrong[index]["part"]["state"]["metadata"]["metadata"]["exit"] = 1
                self.assertEqual(self.proof(events=wrong), optional)
                wrong = copy.deepcopy(original)
                wrong[index]["sessionID"] = "ses-other"
                self.assertEqual(self.proof(events=wrong), optional)
                for field, value in (("workdir", "/wrong"), ("command", "git show HEAD"),
                                     ("command", original[index]["part"]["state"]["input"]["command"]
                                      + "; true")):
                    wrong = copy.deepcopy(original)
                    wrong[index]["part"]["state"]["input"][field] = value
                    self.assertEqual(self.proof(events=wrong), optional)
        review_index = 3
        for field, value in (("proposal_sha", "c" * 40), ("decision", "pending"),
                             ("files", {}), ("reviewer", "unknown"),
                             ("validation", {"exit_code": 1})):
            wrong = copy.deepcopy(original)
            data = json.loads(wrong[review_index]["part"]["state"]["output"])
            data[field] = value
            wrong[review_index]["part"]["state"]["output"] = json.dumps(data)
            self.assertFalse(self.proof(events=wrong))
        wrong = copy.deepcopy(original)
        wrong[0]["part"]["state"]["output"] = "c" * 40
        self.assertFalse(self.proof(events=wrong))
        wrong = copy.deepcopy(original)
        wrong[4]["part"]["state"]["output"] += "\nchanged artifact"
        # Auxiliary body output is not this predicate's evidence. Actual
        # physical-byte changes are rejected by real repository checks below.
        self.assertTrue(self.proof(events=wrong))

    def test_exact_scope_and_immutable_native_chain_cannot_be_replaced_by_empty_diff(self):
        core = [e for e in self.events
                if e["part"]["state"]["input"]["command"] not in self.body_commands]
        diff_index = next(i for i, e in enumerate(core)
                          if e["part"]["state"]["input"]["command"].startswith("git diff "))
        for scope in ("missing-empty-directory", f"openspec/changes/{CHANGE}/tasks.md", ""):
            wrong = copy.deepcopy(core)
            wrong[diff_index]["part"]["state"]["input"]["command"] = (
                f"git diff --exit-code {self.proposal} -- {scope}").rstrip()
            self.assertFalse(self.proof(events=wrong))
        # Same fixture, real comparison can succeed for a WRONG empty scope.
        self.git("diff", "--exit-code", self.proposal, "--", "missing-empty-directory")
        for field, value in (("proposal_sha", self.facts["review_sha"]),
                             ("review_sha", self.proposal)):
            wrong = copy.deepcopy(self.facts)
            wrong[field] = value
            self.assertFalse(artifact_comparison_prerequisites(
                self.repo, self.fixture_env, wrong)["verified"])
        wrong = copy.deepcopy(self.facts)
        wrong["review"]["files"] = {}
        self.assertFalse(artifact_comparison_prerequisites(
            self.repo, self.fixture_env, wrong)["verified"])

    def test_real_artifact_bytes_index_mode_type_and_flags_are_prerequisites(self):
        relative = f"openspec/changes/{CHANGE}/design.md"
        path = self.repo / relative
        content = path.read_bytes()
        def capture():
            return artifact_comparison_prerequisites(self.repo, self.fixture_env, self.facts)
        def changed_bytes():
            old = path.stat()
            path.write_bytes(b"!" + content[1:])
            os.utime(path, ns=(old.st_atime_ns, old.st_mtime_ns))
        def tracked_delete():
            path.unlink()
            self.git("add", "--update", "--", relative)
        def executable():
            path.chmod(0o755)
            self.git("add", "--", relative)
        def symlink():
            path.unlink()
            path.symlink_to(path.with_name("proposal.md"))
        for mutation in (changed_bytes, path.unlink, tracked_delete, executable, symlink):
            with self.subTest(mutation=mutation.__name__):
                try:
                    mutation()
                    after = capture()
                    self.assertFalse(after["verified"])
                    self.assertFalse(self.proof(artifact_states=(self.artifact_states[0], after)))
                finally:
                    if path.is_symlink():
                        path.unlink()
                    path.write_bytes(content)
                    path.chmod(0o644)
                    self.git("add", "--", relative)
                self.assertTrue(capture()["verified"])
        for flag, clear in (("--assume-unchanged", "--no-assume-unchanged"),
                            ("--skip-worktree", "--no-skip-worktree")):
            with self.subTest(flag=flag):
                try:
                    self.git("update-index", flag, "--", relative)
                    self.git("diff", "--exit-code", self.proposal, "--", f"openspec/changes/{CHANGE}")
                    self.assertFalse(capture()["verified"])
                finally:
                    self.git("update-index", clear, "--", relative)
                self.assertTrue(capture()["verified"])

    def test_conversion_configuration_and_attributes_rejected_inventory_still_separate(self):
        def capture():
            return artifact_comparison_prerequisites(self.repo, self.fixture_env, self.facts)
        for key, value in (("core.filemode", "false"), ("core.autocrlf", "true"),
                           ("filter.fixture.clean", "cat")):
            with self.subTest(config=key):
                try:
                    self.git("config", key, value)
                    self.assertFalse(capture()["verified"])
                finally:
                    if key == "core.filemode":
                        self.git("config", key, "true")
                    else:
                        self.git("config", "--unset", key)
                self.assertTrue(capture()["verified"])
        attributes = self.repo / ".gitattributes"
        try:
            attributes.write_text("openspec/** text eol=crlf\n")
            self.assertFalse(capture()["verified"])
        finally:
            attributes.unlink()
        # Untracked/ignored bytes are NOT covered by scoped Git diff. They are
        # still in the existing inventory and full before/after equality gate.
        (self.repo / ".gitignore").write_text("ignored.data\n")
        for name in ("local.data", "ignored.data"):
            (self.repo / name).write_text("before")
        before = inventory(self.repo, self.fixture_env)
        for name in ("local.data", "ignored.data"):
            (self.repo / name).write_text("after")
        self.git("diff", "--exit-code", self.proposal, "--", f"openspec/changes/{CHANGE}")
        self.assertTrue(capture()["verified"])
        self.assertNotEqual(inventory(self.repo, self.fixture_env), before)


class ReadOnlyGitHubTest(unittest.TestCase):
    def test_sources_and_refusal_of_writes_invalid_output_or_missing_data(self):
        fixture = runpy.run_path(str(Path(__file__).parent / "fixtures/resume_gh.py"))
        response = fixture["response"]
        state = {"issues": {"21": {"number": 21, "body": "run=wf-disposable-a"}},
                 "pulls": {"12": {"number": 12, "headRefOid": "a" * 40,
                                   "statusCheckRollup": []}}}
        self.assertEqual(response(["api", "repos/disposable/recovery/issues/21"],
                                  state), state["issues"]["21"])
        self.assertEqual(response(["pr", "view", "12"], state), state["pulls"]["12"])
        for args in (["api", "--method", "PATCH", "repos/disposable/recovery/issues/21"],
                     ["api", "repos/disposable/recovery/issues/21", "-f", "body=changed"],
                     ["api", "repos/disposable/recovery/issues/21/comments"],
                     ["pr", "merge", "12"], ["issue", "edit", "21"],
                     ["pr", "view", "12", "--jq", ".number"]):
            with self.subTest(args=args), self.assertRaises((ValueError, KeyError)):
                response(args, state)
        # The executable refuses even the obsolete seed switch; source bytes
        # remain unchanged, with an audit record of the attempted write.
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
            path = Path(root) / "state.json"
            path.write_text(json.dumps(state))
            before = path.read_bytes()
            env = {**os.environ, "RESUME_GH_ROOT": root, "RESUME_GH_SEED": "1",
                   "PYTHONDONTWRITEBYTECODE": "1"}
            command = [sys.executable, str(Path(__file__).parent / "fixtures/resume_gh.py")]
            for args in (["issue", "edit", "21"], ["issue", "view", "999"]):
                result = subprocess.run([*command, *args], env=env, capture_output=True)
                self.assertEqual(result.returncode, 77)
                self.assertEqual(path.read_bytes(), before)
            path.write_text("{invalid")
            self.assertNotEqual(subprocess.run([*command, "issue", "view", "21"],
                                              env=env, capture_output=True).returncode, 0)


class ProofBoundaryTest(unittest.TestCase):
    def test_t5_only_adds_one_canonical_skill_rule_without_resource_or_guard_expansion(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            repo = Path(directory)
            name = "openspec-verify-change"
            shutil.copytree(ROOT / ".agents/skills" / name, repo / ".agents/skills" / name)
            args = (repo, [], repo / "runtime/reader", {}, repo / "active")
            baseline = read_only_permissions(*args)
            t5 = read_only_permissions(*args, case="T5")
            addition = {"action": "skill", "resource": name, "effect": "allow"}
            self.assertEqual([r for r in t5 if r not in baseline], [addition])
            self.assertEqual([r for r in t5 if r != addition], baseline)
            self.assertEqual(read_only_permissions(*args, case="T1"), baseline)
            self.assertEqual(read_only_permissions(*args, case="T7"), baseline)
            self.assertEqual(read_only_permissions(*args, case="T7", prechoice=True),
                             read_only_permissions(*args, prechoice=True))
            for case in ("T1", "T7"):
                self.assertNotIn(addition, read_only_permissions(*args, case=case))
            guard = ROOT / "tests/fixtures/resume_shell_guard.mjs"
            self.assertEqual(sha(guard),
                             "b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656")

    def test_t1_github_requires_actual_issue_decisions_read_before_handoff(self):
        repo = Path("/tmp/opencode/unit")
        fixture = {"repository": "disposable/recovery", "issue": 61}
        issue = {"number": 61, "body": "Pinned proposal", "comments": [{"body": "[DECISION] Read only"}]}
        event = {"type": "tool_use", "sessionID": "ses-unit", "part": {
            "tool": "shell", "state": {"status": "completed", "input": {
                "command": "gh api repos/disposable/recovery/issues/61", "workdir": str(repo)},
                "metadata": {"metadata": {"exit": 0, "truncated": False}},
                "output": json.dumps(issue)}}}
        def proof(trace, boundary=1):
            return t1_github_source_proof(
                trace, "ses-unit", repo, fixture, {"issues": {"61": issue}}, before=boundary)
        self.assertTrue(proof([event]))
        self.assertFalse(proof([event], 0))
        for mutation in ("session", "error", "cancelled", "cwd", "output", "exit", "truncated"):
            changed = copy.deepcopy(event)
            state = changed["part"]["state"]
            if mutation == "session":
                changed["sessionID"] = "other"
            elif mutation in ("error", "cancelled"):
                state["status"] = mutation
            elif mutation == "cwd":
                state["input"]["workdir"] = "/other"
            elif mutation == "output":
                state["output"] = json.dumps({**issue, "comments": []})
            else:
                state["metadata"]["metadata"][mutation] = 1 if mutation == "exit" else True
            self.assertFalse(proof([changed]), mutation)

    def test_permissions_deny_search_and_unbounded_shell_or_home_reads(self):
        repo = Path("/tmp/opencode/fixture/T1")
        reader = Path("/tmp/opencode/fixture/T1-runtime/read-receipt")
        active = Path("/tmp/opencode/fixture/home/active")
        rules = read_only_permissions(repo, [], reader, {}, active)
        self.assertEqual(rules[0], {"action": "*", "resource": "*", "effect": "deny"})
        allowed = [r for r in rules if r["effect"] == "allow"]
        self.assertFalse(any(r["action"] in ("grep", "glob") for r in allowed))
        self.assertFalse(any(r["resource"] == "*" for r in allowed))
        self.assertFalse(any(r["action"] == "shell" and "*" in r["resource"] for r in allowed))
        self.assertFalse(any("/home/operator" in r["resource"] for r in allowed))
        self.assertFalse(any(r["resource"] == str(active.parent) + "/*" for r in allowed))

    def test_prepared_failure_records_survive_provider_malformed_and_timeout(self):
        for failure in ("provider", "malformed", "timeout"):
            for after_available in (True, False):
                with self.subTest(failure=failure, after_available=after_available):
                    with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
                        base = Path(root)
                        results = {"scenarios": {}, "candidate": "exact-head"}
                        record = {"before": {"state": "original"}}
                        process = Mock(pid=999999, returncode=1)
                        valid = json.dumps({"type": "error", "sessionID": "ses-failed",
                                            "error": {"message": "HTTP400 Model unavailable"}})
                        process.communicate.return_value = (valid, "provider error")
                        if failure == "malformed":
                            process.returncode = 0
                            process.communicate.return_value = (valid + "\n{invalid", "")
                        if failure == "timeout":
                            process.returncode = -15
                            process.communicate.side_effect = [
                                subprocess.TimeoutExpired("fixture", 360), (valid, "timeout")]
                        def launch():
                            saved = json.loads((base / "results.json").read_text())
                            prepared = saved["scenarios"]["T1"][0]
                            self.assertEqual(prepared["status"], "prepared")
                            self.assertEqual(prepared["before"], record["before"])
                            self.assertIsNone(prepared["unchanged"])
                            return execute_model("opencode", base, {}, base,
                                                 "T1-phase1", "read-only", model="test/free")
                        def after():
                            if not after_available:
                                raise RuntimeError("snapshot unavailable")
                            return record["before"]
                        with (patch("smoke_resume_candidate_opencode.subprocess.Popen",
                                    return_value=process) as popen,
                              patch("smoke_resume_candidate_opencode.os.killpg") as kill,
                              patch("smoke_resume_candidate_opencode.git", return_value="exact-head")):
                            with self.assertRaises(ModelExecutionError):
                                prepared_phase(base, results, "T1", record, launch, after)
                        saved = json.loads((base / "results.json").read_text())
                        phase = saved["scenarios"]["T1"][0]
                        self.assertEqual(saved["status"], "failed")
                        self.assertEqual(phase["status"], "failed")
                        self.assertFalse(phase["outcome"])
                        self.assertEqual(phase["session_id"], "ses-failed")
                        self.assertEqual(phase["after_status"],
                                         "available" if after_available else "unavailable")
                        self.assertEqual(phase["unchanged"], True if after_available else None)
                        self.assertEqual(popen.call_count, 1)
                        self.assertEqual(kill.call_count, int(failure == "timeout"))
                        self.assertEqual(list(saved["scenarios"]), ["T1"])
                        terminal = json.loads((base / "T1-phase1-terminal.json").read_text())
                        self.assertEqual(terminal["session_ids"], ["ses-failed"])
                        self.assertEqual(terminal["candidate"], "exact-head")
                        self.assertEqual(bool(terminal["malformed_lines"]), failure == "malformed")

    def test_native_model_metadata_selects_exact_default_or_explicit_free_override(self):
        # Shape captured from OpenCode 2.3.2 /openapi.json Model.Info/Cost:
        # costs are tier arrays and tools lives under capabilities, not top-level.
        model = {"id": "free-a", "modelID": "upstream-a", "providerID": "test",
                 "type": "chat", "enabled": True, "status": "active",
                 "capabilities": {"tools": True, "input": ["text"], "output": ["text"]},
                 "cost": [{"input": 0, "output": 0, "cache": {"read": 0, "write": 0}}],
                 "settings": {"apiKey": "must-not-be-persisted"}}
        repo = Path("/tmp/opencode/fixture")
        def preflight(default, catalog, override=None):
            record = {}
            responses = [{"location": {"directory": str(repo)}, "data": default},
                         {"location": {"directory": str(repo)}, "data": catalog}]
            with patch("smoke_resume_candidate_opencode.checked_json",
                       side_effect=responses) as calls:
                result = model_preflight("opencode", repo, {"HOME": "/disposable"}, record,
                                         override)
            self.assertEqual(calls.call_count, 2)
            self.assertNotIn("must-not-be-persisted", json.dumps(record))
            self.assertFalse(record["inference_verified"])
            return result, record
        result, record = preflight(model, [model])
        self.assertEqual(result, "test/free-a")
        self.assertEqual(record["source"], "native:/api/model/default")
        other = {**model, "id": "free-b"}
        self.assertEqual(preflight(model, [model, other], "test/free-b")[0], "test/free-b")
        self.assertEqual(preflight(other, [other])[0], "test/free-b")
        for default, catalog, override in (
            (None, [], None), (model, [], None), (model, [model], "test/missing"),
            (model, [{**model, "enabled": False}], None),
            (model, [{**model, "capabilities": {**model["capabilities"], "tools": False}}], None),
            (model, [{**model, "capabilities": {"tools": True, "input": [], "output": []}}], None),
            (model, [{**model, "cost": []}], None),
            (model, [{**model, "cost": [{"input": 0, "output": 0}]}], None),
            (model, [{**model, "cost": [{"input": 0, "output": 1,
                                      "cache": {"read": 0, "write": 0}}]}], None),
            (model, [{**model, "cost": [*model["cost"], {"input": 1, "output": 0,
                                                       "cache": {"read": 0, "write": 0}}]}], None),
        ):
            with self.subTest(default=default, catalog=catalog, override=override):
                with self.assertRaises(RuntimeError):
                    preflight(default, catalog, override)
        with (patch("smoke_resume_candidate_opencode.checked_json",
                    side_effect=RuntimeError("metadata endpoint unavailable")) as api,
              patch("smoke_resume_candidate_opencode.execute_model",
                    side_effect=AssertionError("no inference"))):
            with self.assertRaises(RuntimeError):
                model_preflight("opencode", repo, {}, {})
            self.assertEqual(api.call_count, 1)

    def test_t5_requires_successful_pr_head_checks_manual_and_dependency_reads(self):
        fixture = {"pr": 12, "pr_head": "a" * 40, "merge_mode": "manual"}
        pr = {"number": 12, "state": "OPEN", "headRefOid": "a" * 40,
              "body": "Merge manual. Consumer #13 blocked until merge.",
              "statusCheckRollup": [{"headSha": "a" * 40, "status": "COMPLETED",
                                     "conclusion": "SUCCESS"}]}
        dependency = {"number": 13, "state": "OPEN",
                      "body": "Blocked until PR #12 is merged; do not dispatch."}
        github = {"pulls": {"12": pr}, "issues": {"13": dependency}}
        reads = [{"args": ["pr", "view", "12"], "exit_code": 0, "result": pr},
                 {"args": ["api", "repos/disposable/recovery/issues/13"],
                  "exit_code": 0, "result": dependency}]
        events = [{"type": "tool_use", "sessionID": "ses-t5", "part": {
            "tool": "shell", "state": {"status": "completed",
                "input": {"command": shlex.join(["gh", *read["args"]])},
                "metadata": {"metadata": {"exit": 0, "truncated": False}},
                "output": json.dumps(read["result"])}}} for read in reads]
        self.assertTrue(t5_sources(events, "ses-t5", fixture, github, reads))
        self.assertFalse(t5_sources(events[1:], "ses-t5", fixture, github, reads[1:]))
        self.assertFalse(t5_sources(events[:1], "ses-t5", fixture, github, reads[:1]))
        self.assertFalse(t5_sources(events, "ses-other", fixture, github, reads))
        self.assertFalse(t5_sources([], "ses-t5", fixture, github, reads))
        # Otherwise-valid SYNTHETIC reads, not the original failed trace or a
        # fabricated native PASS. The added negative is verbatim retained event19.
        retained = json.loads((ROOT / "tests/fixtures/resume_t5_denied_verify.json").read_text())
        denied = retained["event"]
        session = denied["sessionID"]
        correlated = [{**event, "sessionID": session} for event in events]
        self.assertTrue(t5_sources(correlated, session, fixture, github, reads))
        self.assertFalse(t5_sources([*correlated, denied], session, fixture, github, reads))
        self.assertFalse(denied["part"]["state"]["metadata"]["providerCall"]["executed"])
        for status in ("completed", "error", "cancelled", "running"):
            changed = copy.deepcopy(denied)
            changed["part"]["state"]["status"] = status
            self.assertFalse(t5_sources([*correlated, changed], session, fixture, github, reads))
        for field, value in (("headRefOid", "b" * 40), ("statusCheckRollup", []),
                             ("statusCheckRollup", [{"headSha": "b" * 40,
                                 "status": "COMPLETED", "conclusion": "SUCCESS"}]),
                             ("body", "Merge auto"), ("state", "MERGED")):
            wrong = {**pr, field: value}
            self.assertFalse(t5_sources(events, "ses-t5", fixture,
                                       {**github, "pulls": {"12": wrong}}, reads))
        self.assertFalse(t5_sources(events, "ses-t5", {**fixture, "merge_mode": "auto"},
                                    github, reads))
        for value in ({}, {**dependency, "number": 14}, {**dependency, "state": "CLOSED"},
                      {**dependency, "body": "Dependency unknown"}):
            self.assertFalse(t5_sources(events, "ses-t5", fixture,
                                        {**github, "issues": {"13": value}}, reads))
        for status in ("error", "cancelled"):
            wrong_events = copy.deepcopy(events)
            wrong_events[0]["part"]["state"]["status"] = status
            self.assertFalse(t5_sources(wrong_events, "ses-t5", fixture, github, reads))
        for field, value in (("exit", 1), ("exit", None), ("truncated", True), ("truncated", None)):
            wrong_events = copy.deepcopy(events)
            wrong_events[0]["part"]["state"]["metadata"]["metadata"][field] = value
            self.assertFalse(t5_sources(wrong_events, "ses-t5", fixture, github, reads))
        for exit_code in (1, 77, None):
            wrong_reads = [{**reads[0], "exit_code": exit_code}, reads[1]]
            self.assertFalse(t5_sources(events, "ses-t5", fixture, github, wrong_reads))
        for output in ("I read PR12 " + "a" * 40 + " manual 13",
                       json.dumps(pr) + "\nExit code: 1", "{invalid"):
            wrong_events = copy.deepcopy(events)
            wrong_events[0]["part"]["state"]["output"] = output
            self.assertFalse(t5_sources(wrong_events, "ses-t5", fixture, github, reads))


class ReadOnlyLocatorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="resume locators ", dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.checkout = self.base / "writer checkout"
        self.checkout.mkdir()
        self.runtime = self.base / "runtime"
        self.runtime.mkdir()
        self.reader = self.runtime / "read-receipt"
        self.reader.write_text(RUNTIME_READER)
        # Synthetic unit input; separate retained native proof exercises a
        # receipt actually observed from a cooperative writer by Popen.wait().
        self.receipt = {"execution_id": "writer-T1-61", "owner": "seed-T1",
                        "run": "wf-disposable-t1", "checkout": str(self.checkout),
                        "execution_kind": "cooperative_process", "terminal": True, "exit_code": 0}

    def publish(self, receipts, *, case="T1", selected_issue=None, fixture=None):
        permissions = read_only_permissions(
            self.repo, [self.checkout], self.reader, receipts, self.repo,
            prechoice=case == "T7" and selected_issue is None)
        original = json.dumps(permissions)
        result = read_only_locators(
            self.repo, [self.checkout], self.reader, receipts, permissions,
            case=case, selected_issue=selected_issue, fixture=fixture)
        self.assertEqual(json.dumps(permissions), original)
        return result, permissions

    def test_published_commands_and_cwds_match_existing_literal_policy(self):
        locator, permissions = self.publish({61: self.receipt})
        guard = disposable_shell_guard(
            self.base / "guard", self.repo, [self.checkout], permissions,
            {"HOME": str(self.base), "PATH": "/usr/bin:/bin"})
        commands = json.loads(Path(guard["policy"]).read_text())["commands"]
        expected = shlex.join(["python3", str(self.reader), *[
            self.receipt[k] for k in ("execution_id", "owner", "run", "checkout")]])
        self.assertEqual(locator["runtime_receipt_command"], expected)
        self.assertEqual(locator["runtime_receipt_identity"],
                         {k: self.receipt[k] for k in ("execution_id", "owner", "run", "checkout")})
        self.assertEqual(locator["runtime_receipt_cwd"], str(self.repo))
        self.assertNotEqual(locator["runtime_receipt_cwd"], self.receipt["checkout"])
        self.assertEqual(set(locator["runtime_receipt_allowed_cwds"]), set(commands))
        for cwd in locator["runtime_receipt_allowed_cwds"]:
            self.assertIn(expected, commands[cwd])
        apply = locator["apply_instructions_locator"]
        self.assertEqual(apply, {
            "command": f"openspec instructions apply --change {CHANGE} --json",
            "cwd": str(self.repo)})
        self.assertIn(apply["command"], commands[apply["cwd"]])
        self.assertNotIn(f'openspec instructions apply --change "{CHANGE}" --json',
                         commands[apply["cwd"]])
        self.assertNotIn("terminal", locator["runtime_receipt_identity"])
        self.assertNotIn("exit_code", locator["runtime_receipt_identity"])
        inventory_locators = locator["inventory_locators"]
        self.assertEqual({item["fact"] for item in inventory_locators},
                         {"branch_checkouts", "registered_owners", "dirty_untracked", "index"})
        for item in inventory_locators:
            self.assertIn(item["command"], commands[item["cwd"]])
            self.assertNotIn("output", item)  # Locators, not a native answer.
        self.assertIn("does NOT enumerate ignored", locator["inventory_scope"])

    def test_t5_shared_locator_and_t7_only_after_explicit_choice(self):
        fixture = {"repository": "disposable/recovery", "milestone": 3, "issue": 11,
                   "pr": 12, "dependent_issue": 13, "run": self.receipt["run"]}
        locator, _ = self.publish({11: self.receipt}, case="T5", fixture=fixture)
        self.assertIn("writer-T1-61", locator["runtime_receipt_command"])
        self.assertNotIn("apply_instructions_locator", locator)
        self.assertEqual(locator["selected_scope"], fixture)
        receipts = {issue: {**self.receipt, "execution_id": f"writer-T7-{issue}",
                            "run": f"wf-disposable-{issue}"} for issue in (21, 22)}
        ambiguous, _ = self.publish(receipts, case="T7")
        self.assertNotIn("runtime_receipt_command", ambiguous)
        self.assertNotIn("runtime_receipt_identity", ambiguous)
        self.assertNotIn("apply_instructions_locator", ambiguous)
        self.assertNotIn("inventory_locators", ambiguous)
        self.assertNotIn("inventory_scope", ambiguous)
        for selected in (21, 22):
            chosen, permissions = self.publish(receipts, case="T7", selected_issue=selected)
            self.assertEqual(chosen["runtime_receipt_identity"]["execution_id"],
                             receipts[selected]["execution_id"])
            self.assertIn(chosen["runtime_receipt_command"],
                           [r["resource"] for r in permissions if r["action"] == "shell"])
            self.assertIn("inventory_locators", chosen)
        with self.assertRaises(ValueError):
            self.publish(receipts, case="T7", selected_issue=99)

    def test_t5_scope_entrypoint_and_existing_raw_github_locators_are_usable_offline(self):
        # No model or network: an actual local Git commit, native /bin/sh and
        # the existing executable GH shim exercise the published commands.
        gh_root = self.base / "github"
        gh_root.mkdir()
        bin_dir = self.base / "bin"
        bin_dir.mkdir()
        shim = bin_dir / "gh"
        shutil.copyfile(ROOT / "tests/fixtures/resume_gh.py", shim)
        shim.chmod(0o755)
        env = {"HOME": str(self.base), "PATH": f"{bin_dir}:/usr/bin:/bin",
               "RESUME_GH_ROOT": str(gh_root), "PYTHONDONTWRITEBYTECODE": "1",
               "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
        def git(*args):
            return subprocess.check_output(["git", *args], cwd=self.repo, env=env,
                                           text=True).strip()
        git("init", "-q")
        plan = self.repo / "openspec/changes" / CHANGE
        plan.mkdir(parents=True)
        shutil.copyfile(ROOT / "openspec/changes" / CHANGE / "proposal.md", plan / "proposal.md")
        self.assertIn("rocker-code/my-ai-skills", (plan / "proposal.md").read_text())
        git("add", ".")
        git("-c", "user.name=Unit", "-c", "user.email=unit@localhost", "commit", "-qm", "producer template")
        head = git("rev-parse", "HEAD")
        fixture = {"repository": "disposable/recovery", "milestone": 3, "issue": 11, "pr": 12,
                   "dependent_issue": 13, "run": "wf-disposable-t5",
                   "pr_head": head, "merge_mode": "manual"}
        receipt = {**self.receipt, "run": fixture["run"], "execution_id": "writer-T5-11"}
        published, permissions = self.publish({11: receipt}, case="T5", fixture=fixture)
        entrypoint = self.repo / "recovery-evidence.json"
        entrypoint.write_text(json.dumps({**fixture, **published}))
        self.assertIn("recovery-evidence.json", PROMPTS["T5"])
        for directed in ("resume-workflow", "openspec-apply-change", ".agents/skills", head):
            self.assertNotIn(directed, PROMPTS["T5"])
        self.assertTrue(any(r == {"action": "read", "resource": entrypoint.name, "effect": "allow"}
                            for r in permissions))
        selected = json.loads(entrypoint.read_text())["selected_scope"]
        self.assertEqual(selected, {k: fixture[k] for k in
                                   ("repository", "milestone", "issue", "pr", "dependent_issue", "run")})
        self.assertNotEqual(selected["repository"], "rocker-code/my-ai-skills")
        self.assertNotEqual(selected["issue"], 61)
        self.assertNotEqual(selected["pr"], 62)
        self.assertIn("template provenance only", published["copied_plan_scope"])
        pr = {"number": 12, "state": "OPEN", "headRefOid": head,
              "statusCheckRollup": [{"headSha": head, "status": "COMPLETED", "conclusion": "SUCCESS"}],
              "body": "Merge manual. Consumer #13 blocked until merge."}
        issues = {"11": {"number": 11, "body": f"Milestone 3; run={fixture['run']}; merge_mode=manual"},
                  "13": {"number": 13, "state": "OPEN",
                         "body": "Blocked until PR #12 is merged; do not dispatch."}}
        state = {"issues": issues, "pulls": {"12": pr}}
        (gh_root / "state.json").write_text(json.dumps(state))
        original = (gh_root / "state.json").read_bytes()
        guard = disposable_shell_guard(
            self.base / "guard-t5", self.repo, [self.checkout], permissions, env)
        allowed = json.loads(Path(guard["policy"]).read_text())["commands"]
        expected = {"issue_inventory": list(issues.values()), "pr_inventory": [pr],
                    "selected_issue": issues["11"], "dependency": issues["13"],
                    "pr_head_checks_mode": pr, "checks": pr["statusCheckRollup"]}
        events = []
        for locator in published["github_locators"]:
            self.assertIn(locator["command"], allowed[locator["cwd"]])
            self.assertNotIn("rocker-code", locator["command"])
            self.assertNotIn("output", locator)  # Locator, not a computed answer.
            result = subprocess.run(["/bin/sh", "-c", locator["command"]], cwd=locator["cwd"],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), expected[locator["fact"]])
            events.append({"type": "tool_use", "sessionID": "ses-unit-t5", "part": {
                "tool": "shell", "state": {"status": "completed", "input": {
                    "command": locator["command"], "workdir": locator["cwd"]},
                    "output": result.stdout,
                    "metadata": {"metadata": {"exit": result.returncode, "truncated": False}}}}})
        reads = [json.loads(line) for line in (gh_root / "reads.jsonl").read_text().splitlines()]
        self.assertEqual([r["args"] for r in reads],
                         [shlex.split(l["command"])[1:] for l in published["github_locators"]])
        self.assertTrue(t5_sources(events, "ses-unit-t5", fixture, state, reads))
        self.assertEqual((gh_root / "state.json").read_bytes(), original)
        for wrong in ({**fixture, "repository": "rocker-code/my-ai-skills"},
                      {**fixture, "pr": 62}, {**fixture, "dependent_issue": 61}):
            with self.assertRaises(AssertionError):
                self.publish({11: receipt}, case="T5", fixture=wrong)
        with self.assertRaises(ValueError):
            self.publish({11: receipt}, case="T5")

    def test_complete_published_reader_and_all_four_identity_arguments(self):
        locator, _ = self.publish({61: self.receipt})
        env = {**os.environ, "RESUME_RUNTIME_ROOT": str(self.runtime)}
        (self.runtime / "receipts.json").write_text(json.dumps([self.receipt]))
        result = subprocess.run(
            ["/bin/sh", "-c", locator["runtime_receipt_command"]],
            cwd=locator["runtime_receipt_cwd"], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), self.receipt)
        args = ["python3", str(self.reader), *[
            self.receipt[k] for k in ("execution_id", "owner", "run", "checkout")]]
        for index in range(2, 6):
            wrong = args[:]
            wrong[index] = "/wrong" if index == 5 else "wrong-identity"
            self.assertEqual(subprocess.run(wrong, env=env, capture_output=True).returncode, 3)
        self.assertEqual(subprocess.run(args[:2], env=env, capture_output=True).returncode, 2)
        (self.runtime / "receipts.json").write_text(json.dumps([{**self.receipt, "terminal": False}]))
        self.assertEqual(subprocess.run(args, env=env, capture_output=True).returncode, 3)


class T1ObservedInventoryTest(unittest.TestCase):
    """Real Git/reservation/receipt readouts in synthetic events, NOT a model run."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="resume inventory ", dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.checkout = self.base / "writer checkout"
        self.runtime = self.base / "runtime"
        self.runtime.mkdir()
        self.reader = self.runtime / "read-receipt"
        self.reader.write_text(RUNTIME_READER)
        self.env = {**os.environ, "HOME": str(self.base), "GIT_CONFIG_GLOBAL": "/dev/null",
                    "GIT_CONFIG_NOSYSTEM": "1", "PYTHONDONTWRITEBYTECODE": "1",
                    "RESUME_RUNTIME_ROOT": str(self.runtime)}
        self.session = "ses-unit-inventory"
        self.reservation = ROOT / "scripts/worktree-reservation"
        self.fixture = {"repository": "disposable/recovery", "issue": 61, "run": "wf-unit"}
        self.invoke(["git", "init", "-q"])
        (self.repo / ".gitignore").write_text("*.cache\n")
        (self.repo / "tracked").write_text("reviewed fixture\n")
        self.invoke(["git", "add", "."])
        self.invoke(["git", "-c", "user.name=Unit", "-c", "user.email=unit@localhost",
                     "commit", "-qm", "fixture"])
        self.invoke([str(self.reservation), "reserve", "--planned", "--path", str(self.checkout),
                     "--repository", str(self.repo), "--issue",
                     "https://github.com/disposable/recovery/issues/61",
                     "--branch", "issue-61-fixture", "--session", "seed-T1", "--run", "wf-unit",
                     "--json"])
        self.invoke(["git", "worktree", "add", "-qb", "issue-61-fixture", str(self.checkout)])
        # Keep the existing cooperative receipt helper unchanged; own/close the
        # real child pipes here so unittest's ResourceWarning mode stays clean.
        children = []
        popen = subprocess.Popen
        def capture(*args, **kwargs):
            child = popen(*args, **kwargs)
            children.append(child)
            return child
        try:
            with patch("subprocess.Popen", side_effect=capture):
                self.receipt = terminal_receipt(
                    self.reservation, self.repo, self.checkout,
                    "https://github.com/disposable/recovery/issues/61",
                    "wf-unit", "T1", self.env, self.runtime)
        finally:
            for child in children:
                if child.stdin and not child.stdin.closed:
                    child.stdin.close()
                child.wait(timeout=20)
                for stream in (child.stdout, child.stderr):
                    if stream:
                        stream.close()
        self.before = self.snapshot()
        self.permissions = read_only_permissions(
            self.repo, [self.checkout], self.reader, {61: self.receipt}, self.repo)
        self.locators = read_only_locators(
            self.repo, [self.checkout], self.reader, {61: self.receipt},
            self.permissions, case="T1")
        self.observe_inventory()

    def observe_inventory(self):
        self.events = []
        for locator in self.locators["inventory_locators"]:
            argv = shlex.split(locator["command"])
            if argv[0] == "worktree-reservation":
                argv[0] = str(self.reservation)
            self.add(locator["command"], self.invoke(argv, Path(locator["cwd"])),
                     cwd=locator["cwd"])
        self.add(self.locators["runtime_receipt_command"],
                 self.invoke(shlex.split(self.locators["runtime_receipt_command"])))

    def invoke(self, args, cwd=None):
        return subprocess.check_output(args, cwd=cwd or self.repo, env=self.env,
                                       text=True).strip()

    def snapshot(self):
        row = json.loads(self.invoke(
            [str(self.reservation), "status", "--path", str(self.checkout), "--json"]))
        return {"git": inventory(self.repo, self.env),
                "checkout_git": {self.checkout.name: inventory(self.checkout, self.env)},
                "reservation": {self.checkout.name: row},
                "runtime": json.loads((self.runtime / "receipts.json").read_text())}

    def add(self, command, output, *, cwd=None):
        self.events.append({"type": "tool_use", "sessionID": self.session, "part": {
            "tool": "shell", "id": str(len(self.events)), "state": {
                "status": "completed", "input": {"command": command,
                                                "workdir": str(cwd or self.repo)},
                "output": output, "metadata": {"metadata": {"exit": 0, "truncated": False}}}}})

    def proof(self, *, events=None, before=None, after=None, receipt=None, boundary=None):
        return t1_inventory_proof(
            self.events if events is None else events, self.session,
            self.repo, [self.checkout], self.reader,
            self.receipt if receipt is None else receipt, self.fixture,
            self.before if before is None else before,
            self.snapshot() if after is None else after,
            handoff_index=len(self.events) if boundary is None else boundary)

    def test_observed_closed_fixture_allows_only_last_gate_recovery_with_limitations(self):
        self.assertTrue(self.proof())
        provenance = {"proposal_sha": "a" * 40, "review_sha": "b" * 40}
        limits = [
            "controlled_fixture_seed is not real independent approval of candidate627/source31c.",
            "No sha256sum66; transformed task bytes differ from source by design.",
            "Post-Apply tests/smoke/CI and 0/16 tasks remain future work, not this read-only gate."]
        handoff = {"issue": 61, "run": "wf-unit", "evidence_scope": "controlled_fixture",
                   **provenance, "status": "RECOVERED",
                   "last_verified_gate": "proposal_review_validated",
                   "next_action": "reconcile-ownership", "apply_executed": False,
                   "blockers": [], "limitations": limits}
        def outcome(value):
            return t1_handoff([*self.events, {"type": "text", "sessionID": self.session,
                                             "part": {"text": json.dumps(value)}}],
                              self.session, self.fixture, provenance)[0]
        self.assertTrue(outcome(handoff))
        # Fourth actual context: inventory was not observed. No JSON label fixes that.
        self.assertFalse(self.proof(events=[]))
        # Prose cannot change the observed facts. Its meaning is NOT automated
        # approval: without corroborated typed context the future phase blocks.
        claimed = {**handoff, "blockers": ["Current inventory not observed."]}
        self.assertTrue(outcome(claimed))
        events = [*self.events, {"type": "text", "sessionID": self.session,
                                "part": {"text": json.dumps(claimed)}}]
        self.assertFalse(t1_phase_evaluation(
            events, self.session, self.fixture, provenance, None, facts={})[
                "read_only_facts_proven"])
        # Last-gate recovery never reserves or authorizes effects.
        self.assertEqual(self.before, self.snapshot())
        self.assertNotEqual(self.before["reservation"][self.checkout.name]["owner"]["session"],
                            self.session)

    def test_each_fact_needs_successful_same_fixture_session_output_before_handoff(self):
        for index in range(len(self.events)):
            for mutation in ("missing", "error", "session", "cwd", "output", "exit", "truncated"):
                with self.subTest(index=index, mutation=mutation):
                    events = copy.deepcopy(self.events)
                    state = events[index]["part"]["state"]
                    if mutation == "missing":
                        events[index] = {}
                    elif mutation == "error":
                        state["status"] = "error"
                    elif mutation == "session":
                        events[index]["sessionID"] = "other-session"
                    elif mutation == "cwd":
                        state["input"]["workdir"] = "/other"
                    elif mutation == "output":
                        state["output"] = "Claimed correct fixture inventory, not a readout."
                    elif mutation == "exit":
                        state["metadata"]["metadata"]["exit"] = 1
                    else:
                        state["metadata"]["metadata"]["truncated"] = True
                    self.assertFalse(self.proof(events=events))
        self.assertFalse(self.proof(boundary=len(self.events) - 1))
        self.assertFalse(self.proof(events=self.events[-1:]))  # Receipt is not inventory.

    def test_equivalent_existing_git_cwd_forms_and_empty_native_marker(self):
        events = copy.deepcopy(self.events)
        for event in events:
            state = event["part"]["state"]
            if state["input"]["workdir"] == str(self.checkout):
                state["input"]["command"] = shlex.join([
                    "git", "-C", str(self.checkout), *shlex.split(state["input"]["command"])[1:]])
                state["input"]["workdir"] = str(self.repo)
            if state["output"] == "":
                state["output"] = "(no output)"
        self.assertTrue(self.proof(events=events))

    def test_publicly_released_waiting_fixture_recovers_read_only_with_prior_receipt(self):
        # Known disposable fixture PRODUCER, explicitly created in setUp; never
        # infer/adopt an operator's session from a registry row.
        producer = "seed-T1"
        self.assertEqual(self.receipt["owner"], producer)
        self.assertTrue(self.proof())  # Existing stopped ACTIVE-owner positive.
        for verb, args in (
            ("checkpoint", ["--note", "fixture producer terminal; ready to release"]),
            ("verify", []),
            ("release", ["--state", "WAITING"]),
        ):
            result = json.loads(self.invoke([
                str(self.reservation), verb, "--path", str(self.checkout),
                "--session", producer, "--run", "wf-unit", *args, "--json"]))
            self.assertTrue(result["ok"])
        self.before = self.snapshot()
        row = self.before["reservation"][self.checkout.name]
        self.assertEqual(row["state"], "WAITING")
        self.assertIsNone(row["owner"])
        self.assertEqual(row["head"], self.receipt["head"])
        self.observe_inventory()  # Fresh real public list/Git/reader readouts AFTER release.
        self.assertTrue(self.proof())
        self.assert_phase_condition("released-unreserved")
        self.assertEqual(self.before, self.snapshot())  # No reservation/writes by recovery.
        self.assertFalse(forbidden_attempts(self.events, self.session))
        self.assertFalse(self.proof(events=self.events[:-1]))  # Ownerless is NOT terminal proof.
        for field in ("execution_id", "owner", "run", "checkout"):
            self.assertFalse(self.proof(receipt={**self.receipt, field: "unrelated"}))
        index = next(i for i, event in enumerate(self.events) if
                     event["part"]["state"]["input"]["command"].startswith("worktree-reservation"))
        for field in ("owner", "issue_url", "branch", "head", "digest", "drift"):
            events = copy.deepcopy(self.events)
            state = events[index]["part"]["state"]
            data = json.loads(state["output"])
            del data["entries"][0][field]
            state["output"] = json.dumps(data)
            self.assertFalse(self.proof(events=events), field)
        for change in ({"digest": "sha256:v1:" + "0" * 64}, {"head": "0" * 40},
                       {"drift": {"changed": True}}, {"state": "RECOVERY_REQUIRED"}):
            events = copy.deepcopy(self.events)
            state = events[index]["part"]["state"]
            data = json.loads(state["output"])
            data["entries"][0].update(change)
            state["output"] = json.dumps(data)
            self.assertFalse(self.proof(events=events), change)

    def assert_phase_condition(self, kind):
        """Real ownership/inventory observations; other gate booleans are unit inputs."""
        provenance = {"proposal_sha": "a" * 40, "review_sha": "b" * 40}
        ownership = t1_ownership_context(self.before, self.receipt, self.fixture)
        self.assertEqual(ownership["kind"], kind)
        value = {"issue": 61, "run": "wf-unit", "evidence_scope": "controlled_fixture",
                 **provenance, "status": "BLOCKED",
                 "last_verified_gate": "proposal_review_validated",
                 "next_action": "reconcile-ownership", "apply_executed": False,
                 "blockers": ["Reconcile ownership before any write."], "limitations": [],
                 "ownership_condition": ownership}
        facts = {key: True for key in (
            "terminal", "proposal", "apply_gate", "inventory", "snapshots",
            "github", "native", "resume", "no_stateful_attempts")}
        def evaluate(body=None, gates=None, events=None, context=ownership):
            trace = [*(self.events if events is None else events), {
                "type": "text", "sessionID": self.session,
                "part": {"text": json.dumps(value if body is None else body)}}]
            actual_facts = {**facts, "inventory": self.proof(
                events=trace, boundary=len(trace) - 1),
                "no_stateful_attempts": not forbidden_attempts(trace, self.session),
                **(gates or {})}
            return t1_phase_evaluation(
                trace, self.session, self.fixture, provenance, context, facts=actual_facts)
        positive = evaluate()
        self.assertTrue(positive["read_only_facts_proven"])
        self.assertFalse(positive["write_authorized"])
        self.assertFalse(positive["scenario_pass"])
        self.assertEqual(positive["serialization_compliance"], "failed")
        self.assertEqual(positive["read_only_acceptance"], "pending_independent_review")
        self.assertTrue(evaluate({**value, "next_action": "apply-issue"})["read_only_facts_proven"])
        for extension in (
            {"audit_notes": ["Read-only fixture observations."]},
            {"unclassified": "Unresolved claim; reviewer must inspect actual response."},
            {"unclassified": {"issue": 999, "next_action": "merge", "status": "APPROVED"}},
            {"scenario_pass": True, "read_only_facts_proven": True},
        ):
            result = evaluate({**value, **extension})
            self.assertTrue(result["read_only_facts_proven"])
            self.assertTrue(result["source_facts_proven"] and result["semantic_fields_proven"])
            self.assertEqual(result["read_only_acceptance"], "pending_independent_review")
            self.assertEqual(result["serialization_compliance"], "failed")
            self.assertEqual(result["serialization_diagnostics"]["untrusted_extensions"], extension)
            self.assertFalse(result["scenario_pass"] or result["write_authorized"])
            self.assertEqual(result["independent_response_event_review"], "required")
            self.assertFalse(evaluate({**value, **extension}, gates={"native": False})[
                "read_only_facts_proven"])
        unsafe = evaluate({**value, "write_authorized": True, "effects": ["takeover completed"]})
        self.assertTrue(unsafe["source_facts_proven"])  # Do not erase actual source facts.
        self.assertFalse(unsafe["semantic_fields_proven"] or unsafe["read_only_facts_proven"])
        self.assertEqual(unsafe["read_only_acceptance"], "blocked")
        for field, wrong in (("phase", "after-write"), ("kind", "unknown"),
                              ("kind", "released-unreserved" if kind == "prior-stopped-owner"
                               else "prior-stopped-owner"),
                              ("owner", "other"), ("checkout", "/other"),
                              ("execution_id", "other"), ("run", "other"),
                              ("write_authorized", True), ("write_authorized", 0),
                              ("effect_claim", "acquired")):
            with self.subTest(field=field, wrong=wrong):
                self.assertFalse(evaluate({**value, "ownership_condition": {
                    **ownership, field: wrong}})["read_only_facts_proven"])
        for changes in ({"ownership_condition": None}, {"next_action": "implement"},
                        {"next_action": "prepare-pr"}, {"apply_executed": True},
                        {"write_authorized": True}, {"effects": ["takeover"]},
                        {"proposal_sha": "0" * 40}, {"run": "other"}):
            self.assertFalse(evaluate({**value, **changes})["read_only_facts_proven"])
        for key in facts:
            self.assertFalse(evaluate(gates={key: False})["read_only_facts_proven"], key)
        self.assertFalse(evaluate(context=None)["read_only_facts_proven"])
        # Arbitrary/contradictory prose has no machine waiver. Even with typed
        # context, no response is accepted until independent event/response review.
        ambiguous = evaluate({**value, "status": "RECOVERED",
                              "blockers": ["Current source missing; owner alive."]})
        self.assertFalse(ambiguous["scenario_pass"])
        self.assertEqual(ambiguous["read_only_acceptance"], "pending_independent_review")
        self.assertFalse(evaluate(body={**value, "status": "RECOVERED", "blockers": []},
                                 events=[])["read_only_facts_proven"])
        for status in ("completed", "error", "cancelled", "running"):
            event = {"type": "tool_use", "sessionID": self.session, "part": {
                "tool": "shell", "state": {"status": status, "input": {
                    "command": "worktree-reservation verify --session observer --json"}}}}
            self.assertFalse(evaluate(events=[*self.events, event])["read_only_facts_proven"])

    def test_active_stopped_owner_condition_requires_all_facts_and_never_grants_writes(self):
        self.assert_phase_condition("prior-stopped-owner")

    def test_unknown_or_live_conflicting_owner_cannot_reuse_old_terminal_receipt(self):
        index = next(i for i, event in enumerate(self.events) if
                     event["part"]["state"]["input"]["command"].startswith("worktree-reservation"))
        for change in (
            {"owner": None},
            {"owner": {**self.before["reservation"][self.checkout.name]["owner"],
                       "session": "other-live-writer", "pid": os.getpid()}},
            {"owner": {**self.before["reservation"][self.checkout.name]["owner"],
                       "pid": os.getpid()}},
            {"state": "RECOVERY_REQUIRED", "owner": None},
            {"drift": {"changed": True}}, {"unknown_untracked_paths": ["local"]},
            {"path": "/unrelated"}, {"head": "0" * 40},
        ):
            with self.subTest(change=change):
                events = copy.deepcopy(self.events)
                state = events[index]["part"]["state"]
                data = json.loads(state["output"])
                data["entries"][0].update(change)
                state["output"] = json.dumps(data)
                # Even a matched snapshot cannot bind an unrelated/live owner to the OLD receipt.
                before = copy.deepcopy(self.before)
                before["reservation"][self.checkout.name].update(change)
                self.assertFalse(self.proof(events=events, before=before, after=before))
        events = copy.deepcopy(self.events)
        state = events[index]["part"]["state"]
        data = json.loads(state["output"])
        data["entries"].append({**data["entries"][0], "path": "/other", "owner": None})
        state["output"] = json.dumps(data)
        self.assertFalse(self.proof(events=events))

    def test_missing_unknown_or_wrong_identity_terminal_receipt_blocks(self):
        for field, value in (("terminal", False), ("exit_code", None),
                             ("exit_code", False), ("pid", None), ("process_start", None),
                             ("running_observed_at", None), ("observed_at", "unknown"),
                             ("running_observed_at", "2099-01-01T00:00:00+00:00"),
                             ("owner", "other"), ("run", "wf-other"),
                             ("execution_id", "other-execution"), ("checkout", "/other"),
                             ("head", "0" * 40), ("execution_kind", "pid_only")):
            with self.subTest(field=field):
                self.assertFalse(self.proof(receipt={**self.receipt, field: value}))
        self.assertFalse(self.proof(receipt={}))
        self.assertFalse(self.proof(events=self.events[:-1]))

    def test_ignored_or_untracked_physical_data_is_not_proved_by_status_or_registry(self):
        for name in ("ignored.cache", "untracked"):
            with self.subTest(name=name):
                path = self.checkout / name
                path.write_text("local data not observed by the model\n")
                before = self.snapshot()
                if name.endswith(".cache"):
                    self.assertEqual(before["checkout_git"][self.checkout.name]["status"], "")
                self.assertFalse(self.proof(before=before, after=before))
                path.unlink()
        changed = copy.deepcopy(self.before)
        changed["checkout_git"][self.checkout.name]["index"] = "changed index"
        self.assertFalse(self.proof(after=changed))

    def test_scope_read_attempts_are_distinct_from_stateful_and_other_denials(self):
        events = copy.deepcopy(self.events)
        def denied(command):
            return {"type": "tool_use", "sessionID": self.session, "part": {
                "tool": "shell", "state": {"status": "error", "input": {"command": command},
                "error": "fixture shell: raw command/cwd denied",
                "metadata": {"providerCall": {"executed": False}}}}}
        # Actual sixth-trace variants: real-repo read61 vs unsupported checksum66.
        events += [denied("gh api repos/rocker-code/my-ai-skills/issues/61"),
                   denied("sha256sum openspec/changes/example/tasks.md"),
                   denied("git status --porcelain=v1 -b && git worktree list --porcelain"),
                   denied("worktree-reservation status --json")]
        result = read_scope_attempts(
            events, self.session, self.repo, self.permissions, self.fixture["repository"])
        self.assertEqual(len(result["out_of_scope_reads"]), 1)
        self.assertFalse(result["out_of_scope_reads"][0]["provider_executed"])
        self.assertEqual(len(result["other_denied_attempts"]), 3)
        self.assertFalse(forbidden_attempts(events, self.session))
        # Labels are diagnostic, not a new rule that every denied read fails.
        self.assertTrue(self.proof(events=events, boundary=len(events)))


class TerminalReceiptTest(unittest.TestCase):
    def test_missing_active_and_wrong_identity_never_prove_stopped_writer(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
            root = Path(root)
            reader = root / "read-receipt"
            reader.write_text(RUNTIME_READER)
            receipt = {"execution_id": "process-21", "execution_kind": "cooperative_process",
                       "owner": "seed", "run": "wf-21", "checkout": str(root),
                       "terminal": True, "exit_code": 0}
            env = {**os.environ, "RESUME_RUNTIME_ROOT": str(root)}
            args = [sys.executable, str(reader), "process-21", "seed", "wf-21", str(root)]
            def check(records, command=args):
                (root / "receipts.json").write_text(json.dumps(records))
                return subprocess.run(command, env=env, capture_output=True)
            self.assertEqual(check([receipt]).returncode, 0)
            self.assertEqual(check([]).returncode, 3)
            for key, value in (("terminal", False), ("exit_code", None),
                               ("checkout", "/wrong"), ("owner", "other"),
                               ("run", "other"), ("execution_id", "other")):
                with self.subTest(key=key):
                    self.assertEqual(check([{**receipt, key: value}]).returncode, 3)


class ArchivedContractTest(unittest.TestCase):
    def test_effective_input_binding_records_consumed_bytes_and_invalidates_uncertain_deltas(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            base = Path(directory)
            source, repo, installed, home = (base / p for p in ("source", "repo", "installed", "home"))
            def write(path, text):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            for path in (
                "tests/smoke_resume_candidate_opencode.py", "tests/fixtures/resume_gh.py",
                "tests/fixtures/resume_shell_guard.mjs", "scripts/install-global",
                "scripts/worktree-reservation", "scripts/worktree_registry.py"):
                write(source / path, "# actual test source\n")
            plan = f"openspec/changes/{CHANGE}"
            for path, text in (
                (f"{plan}/proposal.md", "# Contract\n"),
                (f"{plan}/design.md", "# Design\n"),
                (f"{plan}/tasks.md", "# Tasks\n- [x] Inspect\n"),
                (f"{plan}/specs/one/spec.md", "# Requirement\n"),
                ("openspec/config.yaml", "schema: spec-driven\n"),
                (".agents/skills/openspec-explore/SKILL.md", "# Actual native skill bytes\n")):
                write(source / path, text)
            verify_path = ".agents/skills/openspec-verify-change/SKILL.md"
            write(source / verify_path, (ROOT / verify_path).read_text())
            shutil.copytree(source / "openspec", repo / "openspec")
            shutil.copytree(source / ".agents", repo / ".agents")
            tasks = repo / plan / "tasks.md"
            tasks.write_text(tasks.read_text().replace("- [x]", "- [ ]"))
            write(repo / "recovery-evidence.json", '{"locator":"controlled fixture"}\n')
            write(installed / "skills/resume-workflow/SKILL.md", "# Installed skill\n")
            write(installed / "protocol/WORKTREES.md", "# Consumed canonical policy\n")
            write(installed / "skills/resume-workflow/references/WORKTREES.md", "# Loaded reference\n")
            write(installed / "manifest.json", '{"revision":"candidate"}\n')
            write(installed / verify_path, (ROOT / verify_path).read_text())
            write(home / ".config/opencode/AGENTS.md", "# Loaded rules\n")
            write(base / "bin/gh", "#!/bin/sh\n")
            write(base / "github/state.json", '{"issues":{}}\n')
            write(base / "runtime/read-receipt", RUNTIME_READER)
            write(base / "runtime/receipts.json", "[]\n")
            write(base / "guard/index.mjs", "// guard\n")
            write(base / "guard/policy.json", '{"commands":{}}\n')
            write(base / "runtime-tool", "#!/bin/sh\n# Unit executable bytes; never launched\n")
            env = {"PATH": f"{home}/.local/bin:{base}/bin:/usr/bin",
                   "HOME": str(home), "OPENCODE_PASSWORD": "MUST-NOT-BE-BOUND",
                   "OPENCODE_CONFIG_CONTENT": '{"permissions":[],"plugins":[]}'}
            guard = {"source": str(base / "guard/index.mjs"),
                     "policy": str(base / "guard/policy.json")}
            contract = {"revision": "candidate", "path": plan, "files": {
                f"{plan}/{name}": sha(source / plan / name) for name in
                ("proposal.md", "design.md", "tasks.md", "specs/one/spec.md")}}
            model_profile = {"requested": "known-zero", "status": "metadata_eligible"}
            def binding(candidate="candidate", selected=None, session=None,
                        prompt="Natural request; no computed model answer", permissions=None):
                # Version calls only are stubbed: this test must never launch a
                # native completion, infer from a model answer or need credentials.
                with patch("smoke_resume_candidate_opencode.run", return_value="version-unit"), \
                     patch("smoke_resume_candidate_opencode.shutil.which", return_value="/usr/bin/true"):
                    return effective_input_binding(
                        source, candidate, selected or contract, installed, repo,
                        base / "github", base / "runtime", home, env, phase=1,
                        prompt=prompt, permissions=[] if permissions is None else permissions,
                        guard=guard, model=model_profile, session=session,
                        approved_contract=contract,
                        native_candidates=[{"path": str(repo / ".agents/skills/openspec-explore/SKILL.md"),
                                            "sha256": sha(repo / ".agents/skills/openspec-explore/SKILL.md")}],
                        runtime_paths={name: str(base / "runtime-tool")
                                       for name in ("git", "openspec", "opencode")})
            original = binding()
            self.assertEqual(original["source"]["approved_proposal"], APPROVED_PROPOSAL)
            self.assertNotIn("MUST-NOT-BE-BOUND", json.dumps(original))
            consumed = original["effective"]["prepared_fixture"]["openspec"]["files"]
            self.assertNotEqual(consumed[f"changes/{CHANGE}/tasks.md"]["sha256"],
                                contract["files"][f"{plan}/tasks.md"])
            same = effective_input_diff(original, binding())
            self.assertEqual(same["status"], "byte_identical")
            self.assertFalse(same["reuse_permitted"])  # Never approval of a native run/gate.
            self.assertEqual(same["independent_impact_review"], "required")
            for path in (
                tasks, repo / "recovery-evidence.json", repo / ".agents/skills/openspec-explore/SKILL.md",
                installed / "skills/resume-workflow/SKILL.md",
                repo / verify_path, installed / verify_path,
                installed / "protocol/WORKTREES.md",
                installed / "skills/resume-workflow/references/WORKTREES.md",
                repo / "openspec/config.yaml", base / "guard/index.mjs",
                base / "guard/policy.json", source / "tests/smoke_resume_candidate_opencode.py",
                base / "github/state.json", base / "runtime/receipts.json", base / "runtime-tool"):
                old = path.read_bytes()
                path.write_bytes(old + b"\n# changed effective bytes\n")
                changed = effective_input_diff(original, binding())
                self.assertEqual(changed["status"], "material_or_uncertain", path)
                self.assertTrue(changed["requires_complete_native_smoke"], path)
                self.assertFalse(changed["reuse_permitted"])
                self.assertTrue(any(d["field"].endswith("/sha256") for d in changed["differences"]))
                path.write_bytes(old)
            env["OPENCODE_CONFIG_CONTENT"] = '{"permissions":["different"],"plugins":[]}'
            self.assertTrue(effective_input_diff(original, binding())["requires_complete_native_smoke"])
            env["OPENCODE_CONFIG_CONTENT"] = '{"permissions":[],"plugins":[]}'
            capability_delta = effective_input_diff(original, binding(permissions=[
                {"action": "skill", "resource": "openspec-verify-change", "effect": "allow"}]))
            self.assertTrue(capability_delta["requires_complete_native_smoke"])
            self.assertFalse(capability_delta["reuse_permitted"])
            t5_input = binding(prompt=PROMPTS["T5"])
            prompt_delta = effective_input_diff(original, t5_input)
            self.assertEqual(prompt_delta["status"], "material_or_uncertain")
            self.assertTrue(prompt_delta["requires_complete_native_smoke"])
            self.assertFalse(prompt_delta["reuse_permitted"])
            self.assertEqual(t5_input["effective"]["wire"]["prompt"], PROMPTS["T5"])
            model_profile["requested"] = "different-runtime-model"
            self.assertTrue(effective_input_diff(original, binding())["requires_complete_native_smoke"])
            self.assertEqual(original["effective"]["wire"]["model_preflight"]["requested"], "known-zero")
            model_profile["requested"] = "known-zero"
            continuation = binding(session="ses-same-t7")
            self.assertEqual(continuation["effective"]["wire"]["run_argv"][-2:],
                             ["--session", "ses-same-t7"])
            provenance = effective_input_diff(original, binding(candidate="new-immutable-ref"))
            self.assertEqual(provenance["status"], "provenance_review_required")
            self.assertFalse(provenance["reuse_permitted"])
            self.assertEqual(provenance["differences"], [
                {"field": "/source/candidate", "before": "candidate", "after": "new-immutable-ref"}])
            # Actual archive copies/normalization: prepared bytes can stay the
            # same while SOURCE locators change. Show the delta; don't silently
            # erase it or assume all archive/sync operations are provenance-only.
            archive = "openspec/changes/archive/2026-11-25-" + CHANGE
            archived = {**contract, "path": archive, "files": {
                path.replace(plan, archive): digest for path, digest in contract["files"].items()}}
            archived_binding = binding(selected=archived)
            self.assertEqual(original["effective"], archived_binding["effective"])
            diff = effective_input_diff(original, archived_binding)
            self.assertEqual(diff["status"], "material_or_uncertain")
            self.assertFalse(diff["reuse_permitted"])
            # An absent binding or falsified checksum cannot pass as byte identity.
            self.assertEqual(effective_input_diff({}, original)["status"], "incomplete")
            corrupt = copy.deepcopy(original)
            corrupt["effective"]["wire"]["prompt"] = "unrecorded transformation"
            self.assertEqual(effective_input_diff(original, corrupt)["status"], "incomplete")
            incomplete = copy.deepcopy(original)
            incomplete["source"] = None
            self.assertEqual(effective_input_diff(original, incomplete)["status"], "incomplete")
            missing = copy.deepcopy(original)
            del missing["effective"]["wire"]["child_environment"]["TERM"]
            missing["sha256"] = input_digest({k: v for k, v in missing.items() if k != "sha256"})
            diff = effective_input_diff(original, missing)
            self.assertEqual(diff["status"], "material_or_uncertain")
            self.assertTrue(any(d.get("after_present") is False for d in diff["differences"]))

    def test_active_archived_missing_and_ambiguous_committed_contracts(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
            repo = Path(root)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()
            git("init", "-q")
            active = repo / "openspec/changes" / CHANGE
            active.mkdir(parents=True)
            for name in ("proposal.md", "design.md", "tasks.md"):
                (active / name).write_text(f"# {name}\n")
            def commit():
                git("add", "-A")
                git("-c", "user.name=Test", "-c", "user.email=test@localhost",
                    "commit", "-qm", "fixture")
                return git("rev-parse", "HEAD")
            revision = commit()
            self.assertEqual(contract_source(repo, revision)["path"],
                             f"openspec/changes/{CHANGE}")
            archive = repo / "openspec/changes/archive" / f"2026-11-25-{CHANGE}"
            archive.parent.mkdir()
            active.rename(archive)
            revision = commit()
            source = contract_source(repo, revision)
            self.assertEqual(source["path"], str(archive.relative_to(repo)))
            self.assertEqual(len(source["files"]), 3)
            shutil.copytree(archive, active)
            with self.assertRaises(RuntimeError):
                contract_source(repo, commit())
            # Use a commit with no contract, not a hidden uncommitted fallback.
            empty = git("hash-object", "-t", "tree", "/dev/null")
            missing = subprocess.check_output(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@localhost",
                 "commit-tree", empty, "-m", "lost-local-contract"], cwd=repo,
                text=True).strip()
            with self.assertRaises(RuntimeError):
                contract_source(repo, missing)

    def test_inventory_preserves_staged_unstaged_untracked_and_ignored_bytes(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
            repo = Path(root)
            def git(*args):
                subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)
            git("init", "-q")
            (repo / ".gitignore").write_text("private.data\n")
            (repo / "tracked").write_text("base")
            git("add", "-A")
            git("-c", "user.name=Test", "-c", "user.email=test@localhost",
                "commit", "-qm", "base")
            (repo / "tracked").write_text("staged")
            git("add", "tracked")
            (repo / "tracked").write_text("unstaged")
            (repo / "local-only").write_text("untracked")
            (repo / "private.data").write_text("ignored")
            before = inventory(repo, os.environ)
            self.assertEqual(inventory(repo, os.environ), before)
            (repo / "private.data").write_text("changed ignored")
            self.assertNotEqual(inventory(repo, os.environ), before)
            self.assertIn("tracked", before["index"])
            self.assertEqual(before["files"]["private.data"]["sha256"],
                             __import__("hashlib").sha256(b"ignored").hexdigest())


if __name__ == "__main__":
    unittest.main()
