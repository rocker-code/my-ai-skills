"""Offline checks for the public shell launcher (no user install or network)."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts/install.sh"
UPDATER = ROOT / "scripts/update.sh"
ENTRY = ROOT / "scripts/install-global"
REVISION = "57733e891659174b79c772fb4f16d8b47fe6c93c"


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="install-launcher-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.log = root / "execution.log"
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
        self.env = {**os.environ, "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
                    "ENTRY_SOURCE": str(ENTRY), "LAUNCHER_SOURCE": str(LAUNCHER),
                    "REAL_PYTHON": sys.executable, "FAKE_MAIN_REVISION": "a" * 40,
                    "GIT_FAIL": "0",
                    "EXECUTION_LOG": str(self.log), "CURL_LOG": str(root / "curl.log"),
                    "CURL_FAIL": "0"}

    def run_launcher(self, *args, env=None):
        return subprocess.run(["sh", "-s", "--", *args], input=LAUNCHER.read_text(),
                              text=True, capture_output=True, cwd=self.temp.name, env=env or self.env)

    def run_updater(self, env=None):
        return subprocess.run(["sh", "-s"], input=UPDATER.read_text(),
                              text=True, capture_output=True, cwd=self.temp.name, env=env or self.env)

    def test_default_and_explicit_update(self):
        for revision in (REVISION, "a" * 40):
            args = () if revision == REVISION else ("--revision", revision)
            result = self.run_launcher(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.log.read_text().splitlines()[1:],
                             ["--revision", revision, "--agent", "opencode"])
            self.assertEqual(Path(self.env["CURL_LOG"]).read_text().splitlines()[-1],
                             f"https://raw.githubusercontent.com/rocker-code/my-ai-skills/{REVISION}/scripts/install-global")

    def test_hash_mismatch_and_download_failure_do_not_execute(self):
        wrong = Path(self.temp.name) / "wrong-installer"
        wrong.write_text("not the approved installer\n")
        for changes in ({"ENTRY_SOURCE": str(wrong)}, {"CURL_FAIL": "1"}):
            result = self.run_launcher(env={**self.env, **changes})
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.log.exists())

    def test_invalid_revision_does_not_download(self):
        for args in (("--revision", "main"), ("--revision", "b" * 39),
                     ("--revision", "b" * 40, "--agent", "codex")):
            result = self.run_launcher(*args)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(self.log.exists())
            self.assertFalse(Path(self.env["CURL_LOG"]).exists())

    def test_update_resolves_latest_main_and_uses_verified_entry(self):
        result = self.run_updater()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text().splitlines()[1:],
                         ["--revision", "a" * 40, "--agent", "opencode"])
        self.assertEqual(Path(self.env["CURL_LOG"]).read_text().splitlines(), [
            "https://raw.githubusercontent.com/rocker-code/my-ai-skills/" + "a" * 40 + "/scripts/install.sh",
            f"https://raw.githubusercontent.com/rocker-code/my-ai-skills/{REVISION}/scripts/install-global"])

    def test_update_fails_closed_on_invalid_main_or_download(self):
        for changes in ({"FAKE_MAIN_REVISION": "not-a-sha"}, {"GIT_FAIL": "1"},
                        {"CURL_FAIL": "1"}):
            result = self.run_updater(env={**self.env, **changes})
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
