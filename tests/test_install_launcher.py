"""Offline checks for the public shell launcher (no user install or network)."""
import os
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts/install.sh"
UPDATER = ROOT / "scripts/update.sh"
ENTRY = ROOT / "scripts/install-global"
REVISION = "d06b4dc7e1d25d80515903544dcb0eb1ce8ace7b"


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="install-launcher-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.log = root / "execution.log"
        # Fetch the immutable installer in ancestor commit A.
        pinned = subprocess.run(["git", "show", f"{REVISION}:scripts/install-global"],
                                cwd=ROOT, capture_output=True, check=True).stdout
        self.assertEqual(hashlib.sha256(pinned).hexdigest(),
                          "36c733d268da960ddb3f468589ab210058d91c6b5c80e9b0177e9ed2f9f84001")
        self.assertEqual(pinned, ENTRY.read_bytes())
        self.assertEqual(subprocess.run(["git", "merge-base", "--is-ancestor", REVISION, "HEAD"],
                                        cwd=ROOT).returncode, 0)
        entry_source = root / "pinned-install-global"
        entry_source.write_bytes(pinned)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        curl = bin_dir / "curl"
        curl.write_text(
            "#!/bin/sh\n"
            "[ \"$CURL_FAIL\" != 1 ] || exit 22\n"
            "[ \"$1\" = -fsSL ] || exit 2\n"
            "[ \"$3\" = -o ] || exit 2\n"
            "printf '%s\\n' \"$2\" >> \"$CURL_LOG\"\n"
            "case \"$2\" in\n"
            "  */scripts/install.sh) cp \"$LAUNCHER_SOURCE\" \"$4\" ;;\n"
            "  */scripts/install-global) cp \"$ENTRY_SOURCE\" \"$4\" ;;\n"
            "  *) exit 2 ;;\n"
            "esac\n"
        )
        curl.chmod(0o755)
        python = bin_dir / "python3"
        python.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = -c ]; then exec \"$REAL_PYTHON\" \"$@\"; fi\n"
            "printf '%s\\n' \"$@\" > \"$EXECUTION_LOG\"\n"
        )
        python.chmod(0o755)
        git = bin_dir / "git"
        git.write_text(
            "#!/bin/sh\n"
            "[ \"$1\" = ls-remote ] && [ \"$2\" = --exit-code ] || exit 2\n"
            "[ \"$3\" = https://github.com/rocker-code/my-ai-skills.git ] || exit 2\n"
            "[ \"$4\" = refs/heads/main ] || exit 2\n"
            "[ \"$GIT_FAIL\" != 1 ] || exit 2\n"
            "printf '%s\\trefs/heads/main\\n' \"$FAKE_MAIN_REVISION\"\n"
        )
        git.chmod(0o755)
        openspec = bin_dir / "openspec"
        openspec.write_text("#!/bin/sh\n[ \"$FAIL_OPENSPEC\" != 1 ] || exit 1\necho 'OpenSpec test version'\n")
        openspec.chmod(0o755)
        data = root / "data/my-ai-skills/active"
        (data / "scripts").mkdir(parents=True)
        (data / "manifest.json").write_text("{}\n")
        worktree = data / "scripts/worktree-reservation"
        worktree.write_text("#!/bin/sh\n")
        worktree.chmod(0o755)
        global_bin = root / ".local/bin"
        global_bin.mkdir(parents=True)
        global_launcher = global_bin / "worktree-reservation"
        global_launcher.write_text("#!/bin/sh\nexec \"${XDG_DATA_HOME}/my-ai-skills/active/scripts/worktree-reservation\" \"$@\"\n")
        global_launcher.chmod(0o755)
        self.skill = data / "skills/apply-issue/SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text("test skill\n")
        link = root / "config/opencode/skills/apply-issue"
        link.parent.mkdir(parents=True)
        link.symlink_to(self.skill.parent)
        instructions = root / "config/opencode/AGENTS.md"
        instructions.write_text("fixture instructions")
        (data.parent / "guidance.json").write_text(json.dumps({
            "schema": 2, "agents": {"opencode": {"skills": str(link.parent),
                                                "instructions": str(instructions)}}}))
        self.env = {**os.environ, "PATH": str(bin_dir) + os.pathsep + str(global_bin) + os.pathsep + os.environ["PATH"],
                    "HOME": str(root), "XDG_DATA_HOME": str(root / "data"),
                    "XDG_CONFIG_HOME": str(root / "config"), "FAIL_OPENSPEC": "0",
                    "ENTRY_SOURCE": str(entry_source), "LAUNCHER_SOURCE": str(LAUNCHER),
                    "REAL_PYTHON": sys.executable, "FAKE_MAIN_REVISION": "a" * 40,
                    "GIT_FAIL": "0",
                    "EXECUTION_LOG": str(self.log), "CURL_LOG": str(root / "curl.log"),
                    "CURL_FAIL": "0"}

    def run_launcher(self, *args, env=None):
        return subprocess.run(["sh", "-s", "--", *args], input=LAUNCHER.read_text(),
                              text=True, capture_output=True, cwd=self.temp.name, env=env or self.env)

    def run_updater(self, *args, env=None):
        return subprocess.run(["sh", "-s", "--", *args], input=UPDATER.read_text(),
                              text=True, capture_output=True, cwd=self.temp.name, env=env or self.env)

    def test_default_and_explicit_update(self):
        for revision, args in (("a" * 40, ()), (REVISION, ("--revision", REVISION))):
            result = self.run_launcher(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Post-install verification passed", result.stdout)
            self.assertEqual(self.log.read_text().splitlines()[1:],
                             ["--revision", revision])
            self.assertEqual(Path(self.env["CURL_LOG"]).read_text().splitlines()[-1],
                             f"https://raw.githubusercontent.com/rocker-code/my-ai-skills/{REVISION}/scripts/install-global")

    def test_hash_mismatch_and_download_failure_do_not_execute(self):
        wrong = Path(self.temp.name) / "wrong-installer"
        wrong.write_text("not the approved installer\n")
        for changes in ({"ENTRY_SOURCE": str(wrong)}, {"CURL_FAIL": "1"}):
            result = self.run_launcher(env={**self.env, **changes})
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.log.exists())

    def test_agent_arguments_are_forwarded_without_implicit_default(self):
        args = ("--agent", "codex", "--agent", "opencode")
        result = self.run_launcher(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text().splitlines()[1:],
                         [*args, "--revision", "a" * 40])
        result = self.run_updater(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text().splitlines()[1:],
                         ["--revision", "a" * 40, *args])

    def test_install_requires_a_valid_latest_main(self):
        for changes in ({"FAKE_MAIN_REVISION": "not-a-sha"}, {"GIT_FAIL": "1"}):
            result = self.run_launcher(env={**self.env, **changes})
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.log.exists())
            self.assertFalse(Path(self.env["CURL_LOG"]).exists())

    def test_invalid_revision_does_not_download(self):
        for args in (("--revision", "main"), ("--revision", "b" * 39),
                     ("--revision", "b" * 40, "--agent", "claude"),
                     ("--agent", "codex;touch pwned"), ("--agent",),
                     ("--revision", ""), ("--revision", "b" * 40, "--revision", "a" * 40)):
            result = self.run_launcher(*args)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(self.log.exists())
            self.assertFalse(Path(self.env["CURL_LOG"]).exists())

    def test_update_resolves_latest_main_and_uses_verified_entry(self):
        result = self.run_updater()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Post-install verification passed", result.stdout)
        self.assertEqual(self.log.read_text().splitlines()[1:],
                         ["--revision", "a" * 40])
        self.assertEqual(Path(self.env["CURL_LOG"]).read_text().splitlines(), [
            "https://raw.githubusercontent.com/rocker-code/my-ai-skills/" + "a" * 40 + "/scripts/install.sh",
            f"https://raw.githubusercontent.com/rocker-code/my-ai-skills/{REVISION}/scripts/install-global"])

    def test_update_fails_closed_on_invalid_main_or_download(self):
        for changes in ({"FAKE_MAIN_REVISION": "not-a-sha"}, {"GIT_FAIL": "1"},
                        {"CURL_FAIL": "1"}):
            result = self.run_updater(env={**self.env, **changes})
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.log.exists())

    def test_missing_skill_or_openspec_fails_install_and_update(self):
        self.skill.unlink()
        for run in (self.run_launcher, self.run_updater):
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Post-install verification failed", result.stderr)
        self.skill.write_text("test skill\n")
        for run in (self.run_launcher, self.run_updater):
            result = run(env={**self.env, "FAIL_OPENSPEC": "1"})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Post-install verification failed", result.stderr)


if __name__ == "__main__":
    unittest.main()
