"""Offline allowlist tests; native execution is a SEPARATE explicit proof."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from smoke_resume_candidate_opencode import (
    disposable_shell_guard, read_only_permissions, shell_guard_preflight)


class RawShellGuardTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.worktree = self.base / "worktree with spaces"
        self.worktree.mkdir()
        self.permissions = read_only_permissions(
            self.repo, [self.worktree], self.base / "reader", {}, self.repo)
        self.guard = disposable_shell_guard(
            self.base / "guard", self.repo, [self.worktree], self.permissions,
            {"HOME": str(self.base), "PATH": "/usr/bin:/bin",
             "BASH_ENV": "/untrusted", "LD_PRELOAD": "/untrusted",
             "GIT_CONFIG_COUNT": "5", "SECRET": "not-for-child"})

    def evaluate(self, commands):
        # Unit-only direct function evaluation, NOT evidence of runtime hooking.
        source = """
import fs from 'node:fs';
import {authorize} from './tests/fixtures/resume_shell_guard.mjs';
const [policy, location, cases] = JSON.parse(fs.readFileSync(0, 'utf8'));
console.log(JSON.stringify(cases.map(([command,cwd]) => {
  try { authorize(policy, location, command, cwd === null ? undefined : cwd); return true; }
  catch { return false; }
})));
"""
        policy = json.loads(Path(self.guard["policy"]).read_text())
        result = subprocess.run(["node", "--input-type=module", "-e", source],
                                cwd=Path(__file__).resolve().parents[1], check=True,
                                input=json.dumps([policy, str(self.repo), commands]),
                                capture_output=True, text=True)
        return json.loads(result.stdout)

    def test_exact_simple_commands_in_exact_fixture_cwds(self):
        self.assertEqual(self.evaluate([
            ["git status --short", None], ["git rev-parse HEAD", str(self.worktree)],
            ["find .agents/skills -name SKILL.md", str(self.repo)],
            ["openspec context --json", str(self.repo)]]), [True] * 4)

    def test_equivalent_injection_classes_are_not_prefix_exceptions(self):
        hook = str(self.base / "harmless-fsmonitor")
        prefixes = [
            f"export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0={hook}; ",
            f"GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0={hook} ",
            f"env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0={hook} ",
            "declare -x GIT_CONFIG_COUNT=1; ", "readonly GIT_CONFIG_COUNT=1; ",
            "typeset -x GIT_CONFIG_COUNT=1; ", "set -a; GIT_CONFIG_COUNT=1; ",
            "function git() { printf harmless; }; ", "command ", "builtin ",
            "eval ", "exec ", "$(printf git) ", "`printf git` ", "( ", "{ ",
        ]
        commands = [p + "git status --short" for p in prefixes] + [
            "git status --short; pwd", "git status --short && pwd",
            "git status --short | cat", "git status --short > marker",
            "git status --short\npwd", "git status --short # comment",
            "git -c core.fsmonitor=" + hook + " status --short",
            "git status --short --ignored", " git status --short",
            "git status ${OPTION}", "git status --short &", "git status --short\t",
        ]
        self.assertEqual(self.evaluate([[c, None] for c in commands]), [False] * len(commands))

    def test_untrusted_cwd_symlink_and_argv_types_fail_closed(self):
        alias = self.base / "alias"
        alias.symlink_to(self.repo, target_is_directory=True)
        self.assertEqual(self.evaluate([
            ["git status --short", str(self.base)],
            ["git status --short", str(alias)],
            ["git status --short", ".agents"],
            ["git status --short", 3], [None, None], [[], None]]), [False] * 6)

    def test_child_environment_is_fixture_only_and_policy_is_digest_bound(self):
        policy = json.loads(Path(self.guard["policy"]).read_text())
        self.assertEqual(policy["env"]["GIT_CONFIG_COUNT"], "1")
        self.assertEqual(policy["env"]["GIT_CONFIG_VALUE_0"], "false")
        self.assertTrue({"BASH_ENV", "LD_PRELOAD", "SECRET"}.isdisjoint(policy["env"]))
        self.assertEqual(len(self.guard["plugin_sha256"]), 64)
        self.assertEqual(len(self.guard["policy_sha256"]), 64)
        self.assertEqual(set(policy["commands"]), {str(self.repo), str(self.worktree)})
        self.assertNotIn("export", " ".join(policy["commands"][str(self.repo)]))

    def test_unsafe_generated_allowlist_blocks_before_plugin_creation(self):
        with self.assertRaisesRegex(RuntimeError, "literal simple"):
            disposable_shell_guard(self.base / "unsafe", self.repo, [],
                                   [{"action": "shell", "effect": "allow",
                                     "resource": "git status; pwd"}], os.environ)
        self.assertFalse((self.base / "unsafe/index.mjs").exists())

    def test_missing_or_wrong_native_activation_blocks_preflight(self):
        with patch("smoke_resume_candidate_opencode.run", return_value="[]"):
            with self.assertRaises(FileNotFoundError):
                shell_guard_preflight("opencode", self.repo, {}, self.guard)
            Path(self.guard["audit"]).write_text(json.dumps({
                "boundary": "setup", "decision": "active", "source": "/wrong/source"}) + "\n")
            with self.assertRaisesRegex(RuntimeError, "not activated"):
                shell_guard_preflight("opencode", self.repo, {}, self.guard)
        self.assertNotIn("preflight", self.guard)

    def test_preflight_requires_fresh_activation_not_old_audit(self):
        audit = Path(self.guard["audit"])
        event = {"boundary": "setup", "decision": "active", "source": self.guard["source"]}
        audit.write_text(json.dumps(event) + "\n")
        with patch("smoke_resume_candidate_opencode.run", return_value="[]"):
            with self.assertRaisesRegex(RuntimeError, "not activated"):
                shell_guard_preflight("opencode", self.repo, {}, self.guard)

        def native_debug(_args, **_kwargs):
            with audit.open("a") as stream:
                stream.write(json.dumps(event) + "\n")
        with patch("smoke_resume_candidate_opencode.run", side_effect=native_debug):
            shell_guard_preflight("opencode", self.repo, {}, self.guard)
        self.assertEqual(self.guard["preflight"]["status"], "active")


if __name__ == "__main__":
    unittest.main()
