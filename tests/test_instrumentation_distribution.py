"""Shared skill references are generated without the personal plugin."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = {
    "contract-handoff": ("templates/github/integration-contract.md",),
    "issue-explore": ("templates/github/question.md",),
    "milestone-orchestrator": ("protocol/AI_WORKFLOW.md", "protocol/WORKTREES.md", "protocol/CI_PERFORMANCE.md", "protocol/TEST_STRATEGY.md"),
    "milestone-progress": ("protocol/AI_WORKFLOW.md", "protocol/WORKTREES.md"),
    "implement-issue": ("protocol/WORKTREES.md", "protocol/CI_PERFORMANCE.md", "protocol/TEST_STRATEGY.md"),
    "apply-issue": ("protocol/WORKTREES.md", "protocol/CI_PERFORMANCE.md", "protocol/TEST_STRATEGY.md"),
    "prepare-pr": ("protocol/WORKTREES.md", "templates/pull-request.md", "protocol/CI_PERFORMANCE.md", "protocol/TEST_STRATEGY.md"),
    "github-resolution": ("protocol/WORKTREES.md", "protocol/CI_PERFORMANCE.md"),
    "address-pr-review": ("protocol/WORKTREES.md", "protocol/TEST_STRATEGY.md"),
    "post-pr-audit": ("protocol/REVIEW_POLICY.md", "protocol/CI_PERFORMANCE.md", "protocol/TEST_STRATEGY.md"),
    "pr-audit": ("protocol/REVIEW_POLICY.md", "protocol/CI_PERFORMANCE.md", "protocol/TEST_STRATEGY.md"),
    "resolve-questions": ("templates/github/decision.md",),
    "chatgpt-web-create-issue": ("protocol/CHATGPT_WEB_ISSUES.md", "protocol/VISUAL_ARTIFACTS.md"),
    "chatgpt-web-refine-issue": ("protocol/CHATGPT_WEB_ISSUES.md", "protocol/VISUAL_ARTIFACTS.md"),
    "issue-audit": ("protocol/CI_PERFORMANCE.md",),
    "kaizen": ("protocol/CI_PERFORMANCE.md",),
    "ci-performance-audit": ("protocol/CI_PERFORMANCE.md",),
    "optimize-ci": ("protocol/CI_PERFORMANCE.md", "skills/ci-performance-audit/references/magento.md"),
    "openspec-workflow": ("protocol/TEST_STRATEGY.md",),
}


def digest_tree(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class DistributionTests(unittest.TestCase):
    def checkout(self, root):
        (root / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts/sync-skill-references", root / "scripts")
        for name in ("skills", "protocol", "templates"):
            shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
        self.assertFalse((root / "plugins").exists())

    def run_sync(self, root):
        return subprocess.run(["bash", str(root / "scripts/sync-skill-references")],
                              capture_output=True, text=True, timeout=30)

    def test_sync_twice_is_idempotent_and_matches_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.checkout(root)
            for skill, sources in REFERENCES.items():
                for source in sources:
                    (root / "skills" / skill / "references" / Path(source).name).unlink(missing_ok=True)
            result = self.run_sync(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            for skill, sources in REFERENCES.items():
                for source in sources:
                    with self.subTest(skill=skill, source=source):
                        self.assertEqual((root / source).read_bytes(),
                                         (root / "skills" / skill / "references" / Path(source).name).read_bytes())
            first = digest_tree(root)
            result = self.run_sync(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(first, digest_tree(root))
            self.assertFalse((root / "plugins").exists())

    def test_missing_source_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.checkout(root)
            (root / "protocol/CHATGPT_WEB_ISSUES.md").unlink()
            result = self.run_sync(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reference source not found:", result.stderr)
            self.assertIn("protocol/CHATGPT_WEB_ISSUES.md", result.stderr)
            self.assertNotIn("Synchronized skill references", result.stdout)

    def test_official_workflow_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            for command in (("workflow-event", "new-run-id"), ("workflow-report", "--help")):
                result = subprocess.run([str(ROOT / "scripts" / command[0]), *command[1:]],
                                        capture_output=True, text=True, timeout=10, cwd=directory)
                self.assertEqual(result.returncode, 0, result.stderr)
