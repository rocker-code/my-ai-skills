"""Artefato gerado executável, referências resolvidas e sem dependências vendidas."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/my-ai-skills"


def digest_tree(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class DistributionTests(unittest.TestCase):
    def test_sync_twice_is_idempotent_and_never_copies_installed_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("scripts", "skills", "protocol", "templates", "integrations", "examples"):
                shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("node_modules", "__pycache__"))
            fixture = root / "tests/fixtures"
            fixture.mkdir(parents=True)
            shutil.copy2(ROOT / "tests/fixtures/opencode-observer-2.2.5.json", fixture)
            (root / "docs").mkdir()
            for name in ("milestone-monitor.md", "milestone-monitor.en.md"):
                shutil.copy2(ROOT / "docs" / name, root / "docs" / name)
            scaffold = root / "plugins/my-ai-skills/.codex-plugin"
            scaffold.mkdir(parents=True)
            shutil.copy2(PLUGIN / ".codex-plugin/plugin.json", scaffold)
            # Armadilha sintética que jamais pode aparecer na distribuição.
            dependencies = root / "integrations/opencode-observer/node_modules"
            dependencies.mkdir()
            (dependencies / "SEGREDO_FIXTURE").write_text("SEGREDO_FIXTURE")
            first = None
            for _ in range(2):
                subprocess.run(["bash", str(root / "scripts/sync-plugin")], check=True, capture_output=True, timeout=30)
                current = digest_tree(root / "plugins/my-ai-skills")
                if first is not None:
                    self.assertEqual(first, current)
                first = current
            self.assertFalse(any("node_modules" in path or "SEGREDO_FIXTURE" in path for path in first))

    def test_generated_modules_bridge_fixture_guides_and_references_match(self):
        for module in (ROOT / "scripts/milestone_monitor").glob("*.py"):
            self.assertEqual(module.read_bytes(), (PLUGIN / module.relative_to(ROOT)).read_bytes(), str(module))
        for name in ("workflow_events.py", "workflow_lock.py", "workflow_waits.py"):
            self.assertEqual((ROOT / "scripts" / name).read_bytes(), (PLUGIN / "scripts" / name).read_bytes())
        source = ROOT / "integrations/opencode-observer"
        for file in source.rglob("*"):
            if file.is_file() and "node_modules" not in file.parts:
                self.assertEqual(file.read_bytes(), (PLUGIN / file.relative_to(ROOT)).read_bytes(), str(file))
        self.assertEqual((ROOT / "tests/fixtures/opencode-observer-2.2.5.json").read_bytes(),
                         (PLUGIN / "tests/fixtures/opencode-observer-2.2.5.json").read_bytes())
        for language in ("", ".en"):
            name = f"docs/milestone-monitor{language}.md"
            self.assertEqual((ROOT / name).read_bytes(), (PLUGIN / name).read_bytes())
        for skill in (ROOT / "skills").iterdir():
            body = (skill / "SKILL.md").read_text() if (skill / "SKILL.md").exists() else ""
            if "references/WORKFLOW_INSTRUMENTATION.md" in body:
                for base in (ROOT, PLUGIN):
                    self.assertEqual((base / "skills" / skill.name / "references/WORKFLOW_INSTRUMENTATION.md").read_bytes(),
                                     (ROOT / "protocol/WORKFLOW_INSTRUMENTATION.md").read_bytes())
        for file in PLUGIN.rglob("*"):
            self.assertNotIn(file.name, ("node_modules", ".env", "__pycache__"))

    def test_distributed_commands_without_node_and_demo_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "python3").symlink_to(sys.executable)
            env = {"PATH": str(path), "HOME": directory, "PYTHONDONTWRITEBYTECODE": "1",
                   "XDG_CONFIG_HOME": directory, "XDG_STATE_HOME": directory}
            commands = (("aew", "workflow", "transition", "--help"), ("aew", "workflow", "reconcile", "--help"),
                        ("aew", "observe", "--help"), ("aew", "collect", "--once"),
                        ("workflow-event", "new-run-id"), ("workflow-report", "--help"))
            for command in commands:
                result = subprocess.run([str(PLUGIN / "scripts" / command[0]), *command[1:]],
                    capture_output=True, text=True, timeout=10, env=env, cwd=directory)
                self.assertEqual(result.returncode, 0, result.stderr)
                if command == ("aew", "collect", "--once"):
                    self.assertEqual(json.loads(result.stdout)["milestones"], [])
        self.assertIn("DADOS SIMULADOS", (ROOT / "examples/milestone-monitor/dashboard.py").read_text().upper())
        for name in ("dashboard.py", "README.md"):
            relative = "examples/milestone-monitor/" + name
            self.assertEqual((ROOT / relative).read_bytes(), (PLUGIN / relative).read_bytes())
