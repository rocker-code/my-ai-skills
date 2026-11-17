"""Contract checks for the M2T consumer guidance (no Docker or M2T execution)."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (ROOT / "protocol/WORKTREES.md").read_text()


def skill(name):
    return (ROOT / f"skills/{name}/SKILL.md").read_text()


class M2TWorktreeGuidanceTests(unittest.TestCase):
    def test_t1_t2_t3_reuse_handoff_and_current_proof(self):
        for phrase in (
            "**issue worktree**", "existing issue handoff", "each known selection",
            "Checkout writer reservation and M2T's execution lock protect different resources",
            "current code/selection", "failed, blocked, interrupted or uncertain",
            "Never impose `down`, `reset`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, PROTOCOL)
        for name in ("implement-issue", "apply-issue", "resume-workflow"):
            with self.subTest(skill=name):
                self.assertIn("M2T", skill(name))
                self.assertIn("handoff", skill(name))
        self.assertIn("Do not `down`/`reset` to resume by default", skill("resume-workflow"))

    def test_t4_t5_t6_exact_owned_cleanup_retains_checkout_on_partial_failure(self):
        # Fixture: integration + two GraphQL tokens owned by A, and one unknown B.
        owned = [("integration", None), ("graphql", "a-1"), ("graphql", "a-2")]
        foreign = ("graphql", "b-1")
        commands = [
            "m2t --worktree <checkout-path> down" if scope == "integration"
            else f"m2t --worktree <checkout-path> down --scope graphql --sandbox-id {token}"
            for scope, token in owned
        ]
        self.assertEqual(len(commands), 3)
        self.assertNotIn(foreign[1], " ".join(commands))
        for command in (
            "m2t --worktree <checkout-path> down",
            "m2t --worktree <checkout-path> down --scope graphql --sandbox-id <exact-owned-token>",
        ):
            self.assertIn(f"`{command}`", PROTOCOL)
        for phrase in (
            "before** Git removes the checkout", "each** proved GraphQL selection",
            "exit 73", "retains the worktree", "Do not use global `gc`",
            "shared vendor/Composer caches", "active owner", "delivery/kaizen",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, PROTOCOL + skill("milestone-orchestrator"))
        for name in ("milestone-orchestrator", "github-resolution", "prepare-pr", "post-pr-audit"):
            with self.subTest(skill=name):
                self.assertIn("M2T", skill(name))
                self.assertRegex(skill(name), r"(?i)retain|retained")
        self.assertIn("per-selection removed/retained", skill("milestone-orchestrator"))

    def test_t7_results_and_internal_cleanup_not_confused_with_retained_sandbox(self):
        self.assertIn("m2t runs show <run-id> --json", PROTOCOL)
        self.assertIn("successful summary does **not** promise a log path", PROTOCOL)
        self.assertIn("`unit`/`exec` return separate execution receipts", PROTOCOL)
        self.assertIn("clean its own disposable `unit`/`exec`", PROTOCOL)
        self.assertIn("only the pertinent private log excerpt", skill("apply-issue"))
        self.assertIn("not unit/exec receipts", skill("resume-workflow"))

    def test_no_per_command_teardown_or_legacy_opsx_instruction(self):
        for name in ("implement-issue", "apply-issue", "resume-workflow"):
            text = skill(name)
            with self.subTest(skill=name):
                self.assertFalse(re.search(r"(?i)(?:must|always|shall)\s+(?:run\s+)?(?:m2t\s+)?down\s+after\s+(?:every|each)\s+(?:test|command)", text))
                self.assertNotIn("/opsx-apply", text)


if __name__ == "__main__":
    unittest.main()
