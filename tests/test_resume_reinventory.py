"""Offline regression for the T7 same-session, pre-native reinventory gate."""
import json
from pathlib import Path
import unittest

from smoke_resume_candidate_opencode import t7_reinventory


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
        context = next(e for e in self.events if
                       e["part"]["state"]["input"]["command"] ==
                       "openspec context --json")
        context["part"]["state"]["input"]["command"] += "; true"
        self.assertFalse(self.proof())


if __name__ == "__main__":
    unittest.main()
