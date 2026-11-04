import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "protocol/TEST_STRATEGY.md"
SKILLS = ("implement-issue", "openspec-workflow", "apply-issue", "prepare-pr",
          "pr-audit", "post-pr-audit", "address-pr-review", "milestone-orchestrator")
INTEGRATED = ("issue-explore", "implement-issue", "apply-issue", "pr-audit", "magento-review")
FIXTURES = ROOT / "tests/fixtures/preflight/planning"


class PreflightProcedureTests(unittest.TestCase):
    def test_planning_scenarios_and_prerequisites(self):
        text = SOURCE.read_text()
        section = text.split("## Pre-flight for cross-cutting changes and expensive runs\n", 1)[1].split("\n## ", 1)[0].lower()
        regional = json.loads((FIXTURES / "t1-regional-defaults.json").read_text())
        docs = json.loads((FIXTURES / "t4-docs-only.json").read_text())
        for consumer in regional["consumers"]:
            with self.subTest(consumer=consumer):
                self.assertIn(consumer.lower(), section)
        for term in ("pt_br", "brl", "timezone", "consumer path", "fixture assumption",
                     "representative", "existing test", "acceptance criterion", "risk",
                     "discovery", "paths", "rollback", "scope", "mounted checkout", "lockfile",
                     "isolation", "focused", "broad", "hosted", "policy", "commit", "reconciliation",
                     "current", "validated obligations", "baseline", "equivalent environment",
                     "origin", "action", "not passed", "authorized scope", "manually"):
            with self.subTest(term=term):
                self.assertIn(term, section)
        self.assertIn(docs["impact"], section)
        for check in docs["proof"]:
            self.assertIn(check, section)

    def test_skills_reference_preflight(self):
        for name in INTEGRATED:
            with self.subTest(skill=name):
                self.assertIn("pre-flight", (ROOT / "skills" / name / "SKILL.md").read_text().lower())

    def test_distribution_byte_parity(self):
        content = SOURCE.read_bytes()
        for name in SKILLS:
            with self.subTest(skill=name):
                reference = f"skills/{name}/references/TEST_STRATEGY.md"
                self.assertEqual((ROOT / reference).read_bytes(), content)
                self.assertEqual((ROOT / "plugins/my-ai-skills" / reference).read_bytes(), content)
        self.assertEqual((ROOT / "plugins/my-ai-skills/protocol/TEST_STRATEGY.md").read_bytes(), content)
        self.assertEqual((ROOT / "plugins/my-ai-skills/scripts/preflight-check").read_bytes(),
                         (ROOT / "scripts/preflight-check").read_bytes())


if __name__ == "__main__":
    unittest.main()
