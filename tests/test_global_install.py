"""Offline distribution tests: every installation uses a disposable HOME."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "scripts/install-global"


def call(*argv, **kwargs):
    return subprocess.run(argv, text=True, capture_output=True, **kwargs)


class GlobalInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="global-install-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for executable in ("opencode", "openspec"):
            path = self.bin / executable
            path.write_text("#!/bin/sh\necho 'test version 1'\n")
            path.chmod(0o755)
        self.env = {**os.environ, "HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home / ".config"),
                    "XDG_DATA_HOME": str(self.home / ".local/share"),
                    "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
                    "PYTHONDONTWRITEBYTECODE": "1"}
        self.source = self.root / "source with spaces"
        self.source.mkdir()
        for name in ("skills", "scripts", "protocol", "templates"):
            shutil.copytree(ROOT / name, self.source / name, ignore=shutil.ignore_patterns("__pycache__"))
        self.git("init", "-q")
        self.git("add", "skills", "scripts", "protocol", "templates")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-qm", "snapshot")
        self.revision = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args, cwd=None):
        result = call("git", "-C", str(cwd or self.source), *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def install(self, *extra, revision=None, env=None):
        return call("python3", str(ENTRY), "--revision", revision or self.revision,
                    "--agent", "opencode", "--source", str(self.source), *extra,
                    env=env or self.env, timeout=90)

    @property
    def data(self):
        return self.home / ".local/share/my-ai-skills"

    def test_install_complete_idempotent_and_preserves_instructions(self):
        config = self.home / ".config/opencode"
        config.mkdir(parents=True)
        (config / "AGENTS.md").write_text("# Minha regra\n- Não executar ações remotas.\n")
        first = self.install()
        self.assertEqual(first.returncode, 0, first.stderr)
        active = self.data / "active"
        manifest = json.loads((active / "manifest.json").read_text())
        self.assertEqual(manifest["revision"], self.revision)
        self.assertEqual(manifest["origin"], "https://github.com/rocker-code/my-ai-skills.git")
        self.assertEqual(manifest["agents"], ["opencode"])
        for relative, info in manifest["files"].items():
            path = active / relative
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), info["sha256"])
            self.assertEqual(path.stat().st_mode & 0o777, info["mode"])
        self.assertTrue((active / "scripts/worktree_registry.py").exists())
        self.assertFalse((active / "plugins").exists())
        self.assertTrue((config / "skills/apply-issue/SKILL.md").exists())
        self.assertTrue((config / "skills/apply-issue").is_symlink())
        before = (config / "AGENTS.md").read_bytes()
        second = self.install()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(before, (config / "AGENTS.md").read_bytes())
        self.assertTrue(before.startswith(b"# Minha regra\n- N\xc3\xa3o executar a\xc3\xa7\xc3\xb5es remotas."))
        self.assertEqual(before.count(b"my-ai-skills-global:v1 begin"), 1)
        self.assertFalse((self.source / "openspec").exists())

    def test_reject_conflicts_and_rollback_before_pointer_switch(self):
        first = self.install()
        self.assertEqual(first.returncode, 0, first.stderr)
        pointer = os.readlink(self.data / "active")
        config = self.home / ".config/opencode"
        original = (config / "AGENTS.md").read_bytes()
        (config / "AGENTS.md").write_text(original.decode().replace("AI Engineering Workflow global", "Alterado"))
        fail = self.install()
        self.assertNotEqual(fail.returncode, 0)
        self.assertIn("personalizada", fail.stderr)
        self.assertEqual(os.readlink(self.data / "active"), pointer)
        (config / "AGENTS.md").write_bytes(original)
        (config / "skills/new-unknown").mkdir()
        (self.source / "skills/new-unknown").mkdir()
        (self.source / "skills/new-unknown/SKILL.md").write_text("---\nname: unknown\n---\n")
        self.git("add", "skills/new-unknown")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-qm", "next")
        next_rev = self.git("rev-parse", "HEAD").stdout.strip()
        fail = self.install(revision=next_rev)
        self.assertNotEqual(fail.returncode, 0)
        self.assertIn("outra origem", fail.stderr)
        self.assertEqual(os.readlink(self.data / "active"), pointer)
        (config / "skills/new-unknown").rmdir()
        env = {**self.env, "MY_AI_SKILLS_FAIL_AT": "guidance"}
        fail = self.install(revision=next_rev, env=env)
        self.assertNotEqual(fail.returncode, 0)
        self.assertEqual(os.readlink(self.data / "active"), pointer)
        self.assertFalse((config / "skills/new-unknown").exists())
        self.assertEqual(original, (config / "AGENTS.md").read_bytes())
        self.assertEqual(self.install(revision=next_rev).returncode, 0)

    def test_revision_and_agent_and_missing_requirement(self):
        self.assertNotEqual(self.install(revision="a" * 40).returncode, 0)
        result = call("python3", str(ENTRY), "--revision", self.revision, "--agent", "claude",
                      env=self.env)
        self.assertIn("único agente suportado", result.stderr)
        self.assertFalse((self.home / ".config/opencode").exists())
        no_gh = self.root / "without-gh"
        no_gh.mkdir()
        for name in ("git", "jq", "curl", "opencode", "openspec", "python3"):
            (no_gh / name).symlink_to(shutil.which(name, path=self.env["PATH"]))
        result = self.install(env={**self.env, "PATH": str(no_gh)})
        self.assertIn("Falta gh", result.stderr)

    def test_legacy_source_clone_at_data_path_is_not_modified(self):
        self.data.mkdir(parents=True)
        (self.data / ".git").mkdir()
        original = (self.data / "personal.txt")
        original.write_text("custom")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Instalação antiga/clone", result.stderr)
        self.assertEqual(original.read_text(), "custom")
        self.assertFalse((self.data / "active").exists())

    def test_public_download_digest_checked_before_execution(self):
        # Model the published command's download→independent literal digest→execution gate.
        payload = self.root / "entry"
        marker = self.root / "executed"
        payload.write_text(f"#!/usr/bin/env python3\nfrom pathlib import Path\nPath({str(marker)!r}).touch()\n")
        published = hashlib.sha256(ENTRY.read_bytes()).hexdigest()
        # This value comes from the reviewed entry, not from the substituted download.
        verify = "import hashlib,sys; sys.exit(0 if hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()==sys.argv[2] else 1)"
        result = call("sh", "-c", "python3 -c \"$1\" \"$2\" \"$3\" && python3 \"$2\"", "sh",
                      verify, str(payload), published)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(marker.exists())
        # A digest supplied alongside the substituted payload would execute it.
        bad = call("sh", "-c", "python3 -c \"$1\" \"$2\" \"$3\" && python3 \"$2\"", "sh",
                   verify, str(payload), hashlib.sha256(payload.read_bytes()).hexdigest())
        self.assertEqual(bad.returncode, 0, bad.stderr)
        self.assertTrue(marker.exists())

    def test_isolated_repositories_and_worktree_with_spaces(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        helper = self.data / "active/scripts/worktree-reservation"
        evidence = self.data / "active/scripts/workflow-evidence"
        for name in ("one", "two"):
            repo = self.root / f"repo {name}"
            repo.mkdir()
            self.git("init", "-q", str(repo))
            (repo / "file").write_text(name)
            self.git("add", "file", cwd=repo)
            self.git("-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-qm", "base", cwd=repo)
            self.assertFalse((repo / ".ai-workflow").exists())
            self.assertEqual(call(str(helper), "--help", cwd=repo, env=self.env).returncode, 0)
            self.assertEqual(call(str(evidence), "--help", cwd=repo, env=self.env).returncode, 0)
            if name == "one":
                worktree = self.root / "worktree with spaces"
                self.git("worktree", "add", "-qb", "test-branch", str(worktree), cwd=repo)
                common = self.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=worktree).stdout.strip()
                self.assertEqual(common, self.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=repo).stdout.strip())
                self.assertEqual(call(str(helper), "list", "--repository", str(worktree), cwd=worktree, env=self.env).returncode, 0)
            else:
                self.assertNotEqual(common, self.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=repo).stdout.strip())

    @unittest.skipUnless(shutil.which("openspec"), "official OpenSpec CLI unavailable")
    def test_openspec_first_use_new_and_existing_preserves_artifacts(self):
        official = shutil.which("openspec")
        (self.bin / "openspec").unlink()
        (self.bin / "openspec").symlink_to(official)
        env = {**self.env, "OPENSPEC_TELEMETRY": "0"}
        for case in ("new", "existing"):
            repo = self.root / case
            repo.mkdir()
            if case == "existing":
                spec = repo / "openspec/specs/personal/spec.md"
                spec.parent.mkdir(parents=True)
                spec.write_text("# My important specification\n")
                config = repo / "openspec/config.yaml"
                config.write_text("schema: spec-driven\n# custom configuration\n")
                before = (spec.read_bytes(), config.read_bytes())
            self.assertEqual(self.install(env=env).returncode, 0)
            guidance = (self.home / ".config/opencode/AGENTS.md").read_text()
            self.assertIn("openspec-apply-change/SKILL.md", guidance)
            self.assertIn("openspec-archive-change/SKILL.md", guidance)
            # Installation never bootstraps a repository implicitly.
            self.assertFalse((repo / ".opencode").exists())
            context = call(str(self.bin / "openspec"), "context", "--json", cwd=repo, env=env)
            listing = call(str(self.bin / "openspec"), "list", "--json", cwd=repo, env=env)
            if case == "new":
                self.assertNotEqual(context.returncode, 0)
            else:
                self.assertEqual(context.returncode, 0, context.stderr)
            if case == "existing":
                self.assertEqual(listing.returncode, 0, listing.stderr)
                self.assertEqual((spec.read_bytes(), config.read_bytes()), before)
            # Authorized first-use setup in this disposable repo only.
            initialized = call(str(self.bin / "openspec"), "init", "--tools", "opencode", str(repo), env=env)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            for action in ("explore", "propose", "apply", "archive"):
                self.assertTrue((repo / ".opencode/commands" / f"opsx-{action}.md").is_file())
                skill = "openspec-apply-change" if action == "apply" else f"openspec-{action}" + ("-change" if action == "archive" else "")
                self.assertTrue((repo / ".opencode/skills" / skill / "SKILL.md").is_file())
            if case == "existing":
                self.assertEqual(spec.read_bytes(), before[0])
                self.assertIn("# custom configuration", config.read_text())
                dry = call(str(self.bin / "openspec"), "update", "--dry-run", "--json", str(repo), env=env)
                self.assertEqual(dry.returncode, 0, dry.stderr)


if __name__ == "__main__":
    unittest.main()
