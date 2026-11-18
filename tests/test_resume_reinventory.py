"""Offline regression for the T7 same-session, pre-native reinventory gate."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
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

from smoke_resume_candidate_opencode import (disposable_opencode_shim,
                                              disposable_path, t7_phase1_proof,
                                              t7_reinventory, t7_visible_question)


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
            event("glob", {"pattern": ".agents/skills/openspec-*/SKILL.md"}, "completed"),
            event("shell", {"command": "find .agents/skills -name SKILL.md"}, "completed"),
            event("grep", {"pattern": "openspec", "path": ".agents/skills"}, "completed"),
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
                ("shell", {"command": "cat .agents/skills/openspec-explore/SKILL.md"}),
                ("shell", {"command": "sed -n '1,30p' /tmp/opencode/fixture/T7/"
                                      ".agents/skills/openspec-explore/SKILL.md"}),
                ("shell", {"command": "rg -n . .agents/skills/openspec-explore/SKILL.md"}),
                ("shell", {"command": "rg -n . /tmp/opencode/fixture/T7/"
                                      ".agents/skills/openspec-explore/SKILL.md"}),
                ("shell", {"command": "worktree-reservation reconcile --takeover"}),
                ("shell", {"command": "workflow-event stage-start --stage apply"}),
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
                    "run": run, "exit_code": 0}
            for issue, run in ((21, "wf-disposable-a"), (22, "wf-disposable-b"))}
        self.events = []
        self.session = "ses-selected"
        self.add("git rev-parse --show-toplevel", str(self.repo))
        for path in self.worktrees:
            self.add(f"git -C {path} rev-parse --show-toplevel", str(path))
        self.add("worktree-reservation list --repository " + str(self.repo),
                 json.dumps({"entries": [
                     {"ok": True, "path": str(path), "state": "ACTIVE",
                      "owner": {"run": run}}
                     for path, run in zip(self.worktrees,
                                          ("wf-disposable-a", "wf-disposable-b"))]}))
        for issue in (21, 22):
            self.add(f"gh api --paginate repos/disposable/recovery/issues/{issue}/comments",
                     json.dumps([{"body": self.receipts[issue]["run"]}]))
        for verb in ("context", "list"):
            self.add(f"openspec {verb} --json",
                     json.dumps({"root": {"path": str(self.repo)}}))
        self.add(f"python3 {self.reader} writer-T7-21 seed-T7 wf-disposable-a",
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
                        "worktree-reservation list --repository " + str(self.repo),
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

    def test_both_ledgers_and_selected_reservation_are_required(self):
        ledger = next(e for e in self.events if
                      "issues/22/comments" in e["part"]["state"]["input"]["command"])
        ledger["part"]["state"]["output"] = "[]"
        self.assertFalse(self.proof())
        ledger["part"]["state"]["output"] = '[{"body": "wf-disposable-b"}]'
        reservation = next(e for e in self.events if
                           "worktree-reservation list" in
                           e["part"]["state"]["input"]["command"])
        payload = json.loads(reservation["part"]["state"]["output"])
        payload["entries"][0]["owner"]["run"] = "wf-other"
        reservation["part"]["state"]["output"] = json.dumps(payload)
        self.assertFalse(self.proof())

    def test_chained_command_cannot_mask_failure(self):
        for prefix in ("openspec context --json",
                       "gh api --paginate repos/disposable/recovery/issues/21/comments",
                       "worktree-reservation list --repository " + str(self.repo),
                       f"python3 {self.reader} writer-T7-21 seed-T7 wf-disposable-a"):
            for suffix in ("; true", " && echo ok", " || true"):
                with self.subTest(prefix=prefix, suffix=suffix):
                    event = next(e for e in self.events if
                                   e["part"]["state"]["input"]["command"] == prefix)
                    event["part"]["state"]["input"]["command"] = prefix + suffix
                    self.assertFalse(self.proof())
                    event["part"]["state"]["input"]["command"] = prefix


if __name__ == "__main__":
    unittest.main()
