"""Caminhos antigos não dependem de Node, npm ou pacote instalado."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class OptionalBridgeTests(unittest.TestCase):
    def test_legacy_commands_without_node_on_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            (bin_dir / "python3").symlink_to(sys.executable)
            env = {**os.environ, "PATH": str(bin_dir), "PYTHONDONTWRITEBYTECODE": "1",
                   "XDG_CONFIG_HOME": str(root / "config"), "XDG_STATE_HOME": str(root / "state")}
            result = subprocess.run([str(ROOT / "scripts/aew"), "collect", "--once"],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["milestones"], [])
            result = subprocess.run([str(ROOT / "scripts/aew"), "dashboard", "--offline"],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertIn("TTY", result.stderr)
            self.assertNotIn("Node", result.stderr)

    def test_documented_example_matches_bridge_contract(self):
        readme = (ROOT / "integrations/opencode-observer/README.md").read_text()
        example = json.loads(readme.split("```json\n", 1)[1].split("```", 1)[0])
        self.assertEqual(example["version"], 1)
        self.assertEqual(example["context"]["version"], "2.2.5")
        self.assertEqual(example["bindings"][0]["session_id"], "ses_fixture")
        for language in ("", ".en"):
            guide = (ROOT / f"docs/milestone-monitor{language}.md").read_text()
            self.assertIn("npm ci --ignore-scripts --no-audit --no-fund", guide)
            self.assertIn("16 KiB", guide)

    def test_operational_labels_and_synthetic_ids_in_both_guides(self):
        fixture = json.loads((ROOT / "tests/fixtures/opencode-observer-2.2.5.json").read_text())
        for language in ("", ".en"):
            guide = (ROOT / f"docs/milestone-monitor{language}.md").read_text()
            for label in ("aguardando autorização (observada)", "aguardando resposta (observada)",
                          "aguardando decisão", "Publicação/vínculo pendente", "owner_input"):
                self.assertIn(label, guide)
            for name in ("session.permission.list", "session.form.list"):
                self.assertIn(fixture["queries"][name]["data"][0]["id"], guide)

    def test_readme_parity_optin_degraded_mode_and_copied_helper_dependencies(self):
        for language in ("", ".en"):
            readme = (ROOT / f"README{language}.md").read_text()
            for token in ("aew observe", "aew workflow transition", "aew workflow reconcile", "@opencode/client@2.2.5",
                          "npm ci --ignore-scripts --no-audit --no-fund", "GitHub-only/Codex", "NOT RUN",
                          "scripts/workflow_events.py", "scripts/workflow_lock.py", "scripts/workflow_waits.py",
                          'cp -R "$MY_AI_SKILLS_SOURCE"/scripts/milestone_monitor'):
                self.assertIn(token, readme)
        installer = (ROOT / "scripts/install-aew").read_text()
        for forbidden in ("npm install", "npm ci", "systemctl", "launchctl", "opencode service", "aew observe"):
            self.assertNotIn(forbidden, installer)
