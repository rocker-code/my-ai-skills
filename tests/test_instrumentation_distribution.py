"""Shared skill references are generated without the personal plugin."""
import hashlib
import base64
import importlib.machinery
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys
import tarfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = {
    "resume-workflow": ("protocol/WORKTREES.md", "protocol/TEST_STRATEGY.md", "protocol/INCREMENTAL_DELIVERY.md"),
    "contract-handoff": ("templates/github/integration-contract.md",),
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
    "create-issue": ("protocol/CHATGPT_WEB_ISSUES.md", "protocol/VISUAL_ARTIFACTS.md"),
    "refine-issue": ("protocol/CHATGPT_WEB_ISSUES.md", "protocol/VISUAL_ARTIFACTS.md"),
    "kaizen": ("protocol/CI_PERFORMANCE.md",),
    "ci-performance-audit": ("protocol/CI_PERFORMANCE.md",),
    "optimize-ci": ("protocol/CI_PERFORMANCE.md", "skills/ci-performance-audit/references/magento.md"),
    "openspec-workflow": ("protocol/TEST_STRATEGY.md", "protocol/AI_WORKFLOW.md", "protocol/WORKTREES.md"),
}


def digest_tree(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class DistributionTests(unittest.TestCase):
    def installer(self):
        return importlib.machinery.SourceFileLoader(
            "tomli_distribution_installer", str(ROOT / "scripts/install-global")).load_module()

    def test_bundled_tomli_upstream_bytes_license_and_cleanup(self):
        module = self.installer()
        payload = base64.b85decode(module.TOMLI_SDIST_B85)
        self.assertEqual(len(payload), 17662)
        self.assertEqual(hashlib.sha256(payload).hexdigest(),
                         "264507556cd8b8c8e7c6ee037cdf443a463f03f4c958e57195e3d369711b8ff6")
        with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
            for name, (size, digest) in module.TOMLI_MEMBERS.items():
                member = archive.getmember("tomli-2.5.0/" + name)
                self.assertTrue(member.isfile())
                source = archive.extractfile(member).read()
                self.assertEqual(len(source), size)
                self.assertEqual(hashlib.sha256(source).hexdigest(), digest)
                self.assertIn(digest, (ROOT / "scripts/vendor/TOMLI.md").read_text())
            license = archive.extractfile("tomli-2.5.0/LICENSE").read().decode()
        self.assertIn(license.rstrip(), (ROOT / "scripts/vendor/TOMLI.md").read_text())
        self.assertIn("".join(("# " + line).rstrip() + "\n" for line in license.splitlines()),
                      (ROOT / "scripts/install-global").read_text())
        original_path, bytecode = list(sys.path), sys.dont_write_bytecode
        for fail in (False, True):
            try:
                with module.bundled_tomli() as parser:
                    package = Path(parser.__file__).parent
                    namespace = parser.__name__
                    self.assertTrue(package.is_dir())
                    self.assertEqual(parser.loads("a.b = true"), {"a": {"b": True}})
                    self.assertFalse(list(package.rglob("*.pyc")))
                    if fail:
                        raise RuntimeError("caller failure")
            except RuntimeError:
                self.assertTrue(fail)
            self.assertFalse(package.exists())
            self.assertFalse(any(n == namespace or n.startswith(namespace + ".") for n in sys.modules))
            self.assertEqual(sys.path, original_path)
            self.assertEqual(sys.dont_write_bytecode, bytecode)

    def test_tomli_corruption_rejected_before_archive_or_import(self):
        module = self.installer()
        for payload in (b"invalid!", module.TOMLI_SDIST_B85[:-5] + b"00000"):
            with mock.patch.object(module, "TOMLI_SDIST_B85", payload), \
                    mock.patch.object(module.tarfile, "open") as archive, \
                    mock.patch.object(module.importlib.util, "spec_from_file_location") as loader:
                with self.assertRaisesRegex(module.InstallError, "Parser TOML incorporado inválido"):
                    with module.bundled_tomli():
                        self.fail("corrupt payload loaded")
                archive.assert_not_called()
                loader.assert_not_called()

    def test_config_read_error_is_bounded_without_exception_values(self):
        module = self.installer()
        with mock.patch.object(Path, "open", side_effect=OSError("SECRET_READ_ERROR")):
            with self.assertRaisesRegex(module.InstallError, "config.toml: leitura") as raised:
                module.codex_skill_rules(Path("config.toml"))
        self.assertNotIn("SECRET_READ_ERROR", str(raised.exception))

    def test_standalone_tomli_ignores_ambient_packages_and_cleans_on_parse_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = root / "standalone"
            shutil.copyfile(ROOT / "scripts/install-global", entry)
            sentinel = root / "shadow-executed"
            for name in ("tomli", "tomllib"):
                (root / (name + ".py")).write_text(
                    f"from pathlib import Path\nPath({str(sentinel)!r}).touch()\nraise RuntimeError('shadow')\n")
            config = root / "config.toml"
            config.write_text('skills.config = [{name="apply-issue",enabled=false}]\n')
            runner = """
import importlib.machinery, sys
from pathlib import Path
m = importlib.machinery.SourceFileLoader("standalone", sys.argv[1]).load_module()
config = Path(sys.argv[2])
assert m.codex_skill_rules(config)[0]["enabled"] is False
config.write_text('secret="DO_NOT_LEAK"\\na=[')
try:
    m.codex_skill_rules(config)
except m.InstallError as error:
    assert "DO_NOT_LEAK" not in str(error)
else:
    raise AssertionError("malformed config accepted")
assert not any(n.startswith("_my_ai_skills_tomli_") for n in sys.modules)
assert not list(Path(sys.argv[3]).glob("my-ai-skills-tomli-*"))
"""
            result = subprocess.run([sys.executable, "-B", "-c", runner, str(entry), str(config), str(root)],
                                    cwd=root, env={**os.environ, "PYTHONPATH": str(root),
                                                   "TMPDIR": str(root)},
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(sentinel.exists())

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

    def test_distribution_has_no_retired_workflow_collector(self):
        for name in ("workflow-event", "workflow-report", "workflow_events.py", "workflow_metrics.py"):
            with self.subTest(helper=name):
                self.assertFalse((ROOT / "scripts" / name).exists())
        for module in ("workflow_evidence.py", "worktree_registry.py"):
            source = (ROOT / "scripts" / module).read_text()
            self.assertNotIn("import workflow_events", source)
            self.assertNotIn("import workflow_metrics", source)

    def test_official_workflow_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            for command in (("workflow-evidence", "--help"), ("worktree-reservation", "--help")):
                result = subprocess.run([str(ROOT / "scripts" / command[0]), *command[1:]],
                                        capture_output=True, text=True, timeout=10, cwd=directory)
                self.assertEqual(result.returncode, 0, result.stderr)
