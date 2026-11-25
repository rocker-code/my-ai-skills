"""Offline regression for the T7 same-session, pre-native reinventory gate."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import copy
import hashlib
import os
from pathlib import Path
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile
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
                                              STRICT_VALIDATE)


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
        for status in ("completed", "error", "cancelled"):
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
                "directory": str(self.repo), "version": "2.3.2", "session_created": 1,
                "database": str(self.repo.parent / "opencode.db"),
                "database_sha256": "a" * 64, "snapshot_sha256": "b" * 64,
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

    def event(self, command, output):
        return {"type": "tool_use", "sessionID": self.session, "part": {
            "tool": "shell", "state": {"status": "completed",
                "input": {"command": command, "workdir": str(self.repo)},
                "metadata": {"metadata": {"exit": 0, "truncated": False}},
                "output": output}}}

    def proof(self, events=None, invocation=None):
        return t1_proposal_proof(self.events if events is None else events,
                                 self.session, self.repo, self.facts,
                                 self.invocation if invocation is None else invocation)

    def test_correlated_commit_all_artifacts_review_and_strict_observations(self):
        self.assertTrue(self.proof())
        self.assertEqual(len(self.facts["review"]["files"]), 5)
        self.assertNotEqual(self.proposal, self.facts["review_sha"])
        self.assertEqual(self.facts["review"]["kind"], "controlled_fixture_seed")
        self.assertEqual(self.facts["review"]["source_candidate"], "a" * 40)
        self.assertEqual(self.facts["review"]["source_approved_proposal"], "b" * 40)
        self.assertFalse(self.proof(invocation=[]))
        self.assertFalse(self.proof(invocation=[{"event_index": len(self.events)}]))

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
                 "next_action": "apply-issue", "apply_executed": False, "blockers": []}
        value.update(changes)
        return {"type": "text", "sessionID": self.session,
                "part": {"text": json.dumps(value)}}

    def test_t1_successful_probes_may_precede_inspection_but_must_precede_final_handoff(self):
        calls = self.events + [self.apply_event]
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
            events, self.session, self.repo, self.facts, invocation, before=boundary))
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
                                  invocation, before=boundary) and
                t1_apply_gate_proof(moved, self.session, self.repo, self.facts,
                                    invocation, before=boundary))
        self.assertFalse(t1_proposal_proof(
            events, self.session, self.repo, self.facts,
            [{"event_index": len(events)}], before=boundary))

    def test_final_handoff_rejects_blocked_contradictory_wrong_scope_and_substring_claims(self):
        fixture = {"issue": 61, "run": "wf-unit"}
        def check(event):
            return t1_handoff(self.events + [event], self.session, fixture, self.facts)[0]
        self.assertTrue(check(self.handoff_event()))
        for field, value in (
            ("status", "BLOCKED"), ("next_action", "bloquear Apply"),
            ("last_verified_gate", "NÃO comprovado"), ("blockers", ["hash mismatch"]),
            ("proposal_sha", "0" * 40), ("review_sha", "1" * 40),
            ("evidence_scope", "real_candidate"), ("issue", 62), ("run", "other"),
            ("apply_executed", True), ("contradictory_extra", "bloquear Apply"),
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
            with self.subTest(source=index):
                self.assertFalse(self.proof(events=original[:index] + original[index + 1:]))
                for field, value in (("status", "error"), ("status", "cancelled"),
                                     ("output", "declaration only " + self.proposal)):
                    wrong = copy.deepcopy(original)
                    wrong[index]["part"]["state"][field] = value
                    self.assertFalse(self.proof(events=wrong))
                wrong = copy.deepcopy(original)
                wrong[index]["part"]["state"]["metadata"]["metadata"]["exit"] = 1
                self.assertFalse(self.proof(events=wrong))
                wrong = copy.deepcopy(original)
                wrong[index]["sessionID"] = "ses-other"
                self.assertFalse(self.proof(events=wrong))
                for field, value in (("workdir", "/wrong"), ("command", "git show HEAD"),
                                     ("command", original[index]["part"]["state"]["input"]["command"]
                                      + "; true")):
                    wrong = copy.deepcopy(original)
                    wrong[index]["part"]["state"]["input"][field] = value
                    self.assertFalse(self.proof(events=wrong))
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
        self.assertFalse(self.proof(events=wrong))


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
                "output": json.dumps(read["result"])}}} for read in reads]
        self.assertTrue(t5_sources(events, "ses-t5", fixture, github, reads))
        self.assertFalse(t5_sources(events[1:], "ses-t5", fixture, github, reads[1:]))
        self.assertFalse(t5_sources(events[:1], "ses-t5", fixture, github, reads[:1]))
        self.assertFalse(t5_sources(events, "ses-other", fixture, github, reads))
        self.assertFalse(t5_sources([], "ses-t5", fixture, github, reads))
        for field, value in (("headRefOid", "b" * 40), ("statusCheckRollup", []),
                             ("statusCheckRollup", [{"headSha": "b" * 40,
                                 "status": "COMPLETED", "conclusion": "SUCCESS"}]),
                             ("body", "Merge auto"), ("state", "MERGED")):
            wrong = {**pr, field: value}
            self.assertFalse(t5_sources(events, "ses-t5", fixture,
                                       {**github, "pulls": {"12": wrong}}, reads))
        for status in ("error", "cancelled"):
            wrong_events = copy.deepcopy(events)
            wrong_events[0]["part"]["state"]["status"] = status
            self.assertFalse(t5_sources(wrong_events, "ses-t5", fixture, github, reads))
        for exit_code in (1, 77, None):
            wrong_reads = [{**reads[0], "exit_code": exit_code}, reads[1]]
            self.assertFalse(t5_sources(events, "ses-t5", fixture, github, wrong_reads))
        for output in ("I read PR12 " + "a" * 40 + " manual 13",
                       json.dumps(pr) + "\nExit code: 1", "{invalid"):
            wrong_events = copy.deepcopy(events)
            wrong_events[0]["part"]["state"]["output"] = output
            self.assertFalse(t5_sources(wrong_events, "ses-t5", fixture, github, reads))


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
