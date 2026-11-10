"""The generated plugin mirrors the maintained scripts and references."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/my-ai-skills"


def digest_tree(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class DistributionTests(unittest.TestCase):
    def test_sync_twice_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("scripts", "skills", "protocol", "templates"):
                shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
            scaffold = root / "plugins/my-ai-skills/.codex-plugin"
            scaffold.mkdir(parents=True)
            shutil.copy2(PLUGIN / ".codex-plugin/plugin.json", scaffold)
            first = None
            for _ in range(2):
                subprocess.run(["bash", str(root / "scripts/sync-plugin")], check=True, capture_output=True, timeout=30)
                current = digest_tree(root / "plugins/my-ai-skills")
                if first is not None:
                    self.assertEqual(first, current)
                first = current
            self.assertFalse(any("milestone_monitor" in path or "opencode-observer" in path or "aew" in path for path in first))

    def test_generated_modules_and_references_match(self):
        for name in ("workflow_events.py",):
            self.assertEqual((ROOT / "scripts" / name).read_bytes(), (PLUGIN / "scripts" / name).read_bytes())
        for skill in (ROOT / "skills").iterdir():
            if (skill / "SKILL.md").exists():
                self.assertEqual((skill / "SKILL.md").read_bytes(), (PLUGIN / "skills" / skill.name / "SKILL.md").read_bytes())
        for file in PLUGIN.rglob("*"):
            self.assertNotIn(file.name, ("node_modules", ".env", "__pycache__"))

    def test_distributed_workflow_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            for command in (("workflow-event", "new-run-id"), ("workflow-report", "--help")):
                result = subprocess.run([str(PLUGIN / "scripts" / command[0]), *command[1:]],
                                        capture_output=True, text=True, timeout=10, cwd=directory)
                self.assertEqual(result.returncode, 0, result.stderr)
