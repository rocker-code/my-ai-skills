import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/preflight-check"
FIXTURES = ROOT / "tests/fixtures/preflight/lock"


class PreflightCheckTests(unittest.TestCase):
    def cli(self, root, *args, code=0):
        result = subprocess.run([sys.executable, str(CLI), "--root", str(root), "--format", "json", *args],
                                capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, code, result.stderr + result.stdout)
        return json.loads(result.stdout)

    def test_composer_formats_and_mismatch(self):
        self.assertEqual(self.cli(FIXTURES / "composer-match", "lock")["status"], "ok")
        data = self.cli(FIXTURES / "composer-phpmd-mismatch", "lock", code=1)
        self.assertEqual(data["findings"], [{"ecosystem": "composer", "type": "version-mismatch",
                                             "package": "phpmd/phpmd", "locked": "3.x-dev", "installed": "2.15.0"}])

    def test_not_installed_unsupported_and_npm(self):
        self.assertEqual(self.cli(FIXTURES / "composer-not-installed", "lock", code=1)["findings"][0]["type"], "not-installed")
        self.assertEqual(self.cli(FIXTURES / "none", "lock", code=2)["status"], "unsupported")
        self.assertEqual(self.cli(FIXTURES / "npm-match", "lock")["status"], "ok")
        self.assertEqual(self.cli(FIXTURES / "npm-mismatch", "lock", code=1)["findings"][0]["type"], "version-mismatch")

    def test_invalid_usage(self):
        for args in ([], ["unknown"], ["lock", "--bad"]):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn("usage:", result.stderr)

    def test_options_after_subcommand(self):
        result = subprocess.run([sys.executable, str(CLI), "lock", "--root", str(FIXTURES / "npm-match"),
                                 "--format", "json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "ok")

    def test_missing_package_and_unreadable_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "composer.lock").write_text('{"packages":[{"name":"absent/tool","version":"1.0"}]}')
            installed = root / "vendor/composer/installed.json"
            installed.parent.mkdir(parents=True)
            installed.write_text("[]")
            self.assertEqual(self.cli(root, "lock", code=1)["findings"],
                             [{"ecosystem": "composer", "type": "missing", "package": "absent/tool",
                               "locked": "1.0", "installed": None}])
            (root / "composer.lock").write_text("invalid json")
            self.assertEqual(self.cli(root, "lock", code=2)["status"], "error")

    def test_policy_tracks_commit_worktree_and_untracked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            def git(*args):
                return subprocess.run(["git", "-C", str(root), *args], check=True,
                                      capture_output=True, text=True).stdout.strip()

            git("init", "-q")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.com")
            (root / "AGENTS.md").write_text("old\n")
            git("add", "AGENTS.md")
            git("commit", "-qm", "plan")
            plan = git("rev-parse", "HEAD")
            self.assertEqual(self.cli(root, "policy", "--since", plan)["status"], "ok")
            (root / "AGENTS.md").write_text("new\n")
            git("commit", "-qam", "policy")
            self.assertEqual(self.cli(root, "policy", "--since", plan, code=1)["findings"],
                             [{"path": "AGENTS.md", "type": "M"}])
            (root / "AGENTS.md").write_text("working tree\n")
            self.assertEqual(self.cli(root, "policy", "--since", "HEAD", code=1)["findings"],
                             [{"path": "AGENTS.md", "type": "M"}])
            (root / "CLAUDE.md").write_text("untracked policy\n")
            self.assertIn({"path": "CLAUDE.md", "type": "??"},
                          self.cli(root, "policy", "--since", "HEAD", code=1)["findings"])
            (root / "extra.md").write_text("new\n")
            data = self.cli(root, "policy", "--since", "HEAD", "--path", "extra.md", code=1)
            self.assertIn({"path": "extra.md", "type": "??"}, data["findings"])
            self.assertEqual(self.cli(root, "policy", "--since", "missing-revision", code=2)["status"], "error")

    def test_policy_detects_staged_delta_hidden_by_restored_worktree(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            def git(*args):
                subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

            git("init", "-q")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.com")
            policy = root / "AGENTS.md"
            policy.write_text("original\n")
            git("add", "AGENTS.md")
            git("commit", "-qm", "plan")
            policy.write_text("staged policy\n")
            git("add", "AGENTS.md")
            policy.write_text("original\n")
            self.assertEqual(self.cli(root, "policy", "--since", "HEAD", code=1)["findings"],
                             [{"path": "AGENTS.md", "type": "M"}])

    def test_policy_paths_cannot_exclude_mandatory_defaults(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.name=Test",
                            "-c", "user.email=test@example.com", "commit", "--allow-empty",
                            "-qm", "plan"], check=True)
            (root / "AGENTS.md").write_text("policy\n")
            for path in (":(exclude)AGENTS.md", ":!AGENTS.md"):
                with self.subTest(path=path):
                    self.assertEqual(self.cli(root, "policy", "--since", "HEAD", "--path", path,
                                              code=2)["status"], "error")
            self.assertEqual(self.cli(root, "policy", "--since", "HEAD", "--path", "extra.md",
                                      code=1)["findings"], [{"path": "AGENTS.md", "type": "??"}])

    def test_workspace_and_skipped_optional_cannot_be_reported_ok(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installed = root / "node_modules/.package-lock.json"
            installed.parent.mkdir(parents=True)
            (root / "package-lock.json").write_text(json.dumps({"lockfileVersion": 3, "packages": {
                "": {"version": "1.0.0"}, "node_modules/workspace": {"link": True, "resolved": "packages/workspace"}}}))
            installed.write_text(json.dumps({"packages": {"node_modules/workspace": {"link": True}}}))
            self.assertEqual(self.cli(root, "lock", code=2)["status"], "error")
            (root / "package-lock.json").write_text(json.dumps({"lockfileVersion": 3, "packages": {
                "": {"version": "1.0.0"}, "node_modules/platform-only": {"version": "1.0.0", "optional": True}}}))
            installed.write_text(json.dumps({"packages": {}}))
            self.assertEqual(self.cli(root, "lock", code=1)["findings"],
                             [{"ecosystem": "npm", "type": "missing", "package": "node_modules/platform-only",
                               "locked": "1.0.0", "installed": None}])


if __name__ == "__main__":
    unittest.main()
