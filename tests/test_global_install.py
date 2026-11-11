"""Offline distribution tests: every installation uses a disposable HOME."""
import hashlib
import errno
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
import importlib.machinery
import types

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
            path.write_text("#!/bin/sh\nif [ \"$1\" = --version ]; then echo 'opencode v2.2.6'; else printf '  api\\n  run\\n  service\\n'; fi\n" if executable == "opencode" else "#!/bin/sh\necho 'test version 1'\n")
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
        # Test-only import injects a disposable Git transport into the internal
        # function; the actual public command has no source override.
        runner = ("import importlib.machinery,sys; "
                  "m=importlib.machinery.SourceFileLoader('installer',sys.argv[1]).load_module(); "
                  "source=sys.argv[2]; sys.argv=[sys.argv[1],*sys.argv[3:]]; "
                  "original=m.install; m.install=lambda args: original(args,source=source); "
                  "sys.exit(m.main())")
        return call("python3", "-c", runner, str(ENTRY), str(self.source),
                    "--revision", revision or self.revision, "--agent", "opencode", *extra,
                    env=env or self.env, timeout=90)

    @property
    def data(self):
        return self.home / ".local/share/my-ai-skills"

    def next_revision(self):
        (self.source / "skills/new-feature").mkdir()
        (self.source / "skills/new-feature/SKILL.md").write_text("---\nname: new-feature\n---\n")
        (self.source / "skills/apply-issue/references/TEST_STRATEGY.md").write_text("updated reference\n")
        (self.source / "scripts/workflow-event").write_text("#!/usr/bin/env python3\nprint('updated helper')\n")
        self.git("add", "-A")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-qm", "next")
        return self.git("rev-parse", "HEAD").stdout.strip()

    def test_update_two_consumers_and_failure_states(self):
        first = self.install()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("state=installed", first.stdout)
        revision = self.next_revision()
        before = (self.home / ".config/opencode/AGENTS.md").read_bytes()
        for phase in ("skills", "guidance", "publish"):
            failed = self.install(revision=revision, env={**self.env, "MY_AI_SKILLS_FAIL_AT": phase})
            self.assertEqual(failed.returncode, 1)
            self.assertIn(f"active={self.revision}", failed.stderr)
            self.assertEqual((self.home / ".config/opencode/AGENTS.md").read_bytes(), before)
            self.assertEqual(json.loads((self.data / "active/manifest.json").read_text())["revision"], self.revision)
            self.assertFalse((self.home / ".config/opencode/skills/new-feature").is_symlink())
        updated = self.install(revision=revision)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertIn("state=updated", updated.stdout)
        self.assertIn(f"previous={self.revision} target={revision} active={revision}", updated.stdout)
        for repo_name in ("consumer-a", "consumer-b"):
            consumer = self.root / repo_name
            consumer.mkdir()
            self.assertEqual((self.home / ".config/opencode/skills/new-feature/SKILL.md").read_bytes(),
                             (self.source / "skills/new-feature/SKILL.md").read_bytes())
            self.assertEqual((self.data / "active/skills/apply-issue/references/TEST_STRATEGY.md").read_text(), "updated reference\n")
            self.assertEqual((self.data / "active/scripts/workflow-event").read_bytes(),
                             (self.source / "scripts/workflow-event").read_bytes())
            self.assertFalse((consumer / ".ai-workflow").exists())
        repeated = self.install(revision=revision)
        self.assertIn("state=already current", repeated.stdout)
        self.assertEqual((self.home / ".config/opencode/AGENTS.md").read_bytes(), before)

    def test_legacy_global_lock_collision_and_authorized_migration(self):
        self.assertEqual(self.install().returncode, 0)
        config = self.home / ".config/opencode"
        link = config / "skills/apply-issue"
        link.unlink()
        legacy = self.home / ".agents/skills/apply-issue"
        legacy.parent.mkdir(parents=True)
        shutil.copytree(self.data / "active/skills/apply-issue", legacy)
        link.symlink_to(legacy)
        lock = self.home / ".agents/.skill-lock.json"
        lock.write_text(json.dumps({"version": 3, "skills": {
            "apply-issue": {"source": "rocker-code/my-ai-skills", "sourceType": "github",
                            "ref": self.revision, "skillPath": "skills/apply-issue/SKILL.md"},
            "unrelated": {"source": "elsewhere/tools", "sourceType": "github"}}}))
        other = config / "skills/unrelated"
        other.mkdir()
        (other / "SKILL.md").write_text("unrelated")
        revision = self.next_revision()
        original_lock = lock.read_bytes()
        for origin in ("elsewhere/tools", None):
            record = json.loads(original_lock)
            if origin is None:
                record["skills"].pop("apply-issue")
            else:
                record["skills"]["apply-issue"]["source"] = origin
            lock.write_text(json.dumps(record))
            blocked = self.install("--migrate-global-skill", "apply-issue", revision=revision)
            self.assertIn("outra origem, alterada ou sem baseline", blocked.stderr)
            self.assertTrue(link.is_symlink())
        lock.write_bytes(original_lock)
        for changed in (False, True):
            if changed:
                (legacy / "SKILL.md").write_text("personalized")
            blocked = self.install(revision=revision)
            self.assertIn("state=blocked", blocked.stderr)
            self.assertIn("--migrate-global-skill" if not changed else "sem baseline", blocked.stderr)
            self.assertEqual(json.loads((self.data / "active/manifest.json").read_text())["revision"], self.revision)
            self.assertTrue(link.is_symlink())
        shutil.rmtree(legacy)
        # The verified active A snapshot, not the B working checkout.
        shutil.copytree(self.data / "versions" / self.revision / "skills/apply-issue", legacy)
        migrated = self.install("--migrate-global-skill", "apply-issue", revision=revision)
        self.assertEqual(migrated.returncode, 0, migrated.stderr)
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(link), str(self.data / "active/skills/apply-issue"))
        self.assertTrue(legacy.is_dir())
        self.assertEqual((other / "SKILL.md").read_text(), "unrelated")
        self.assertIn("migrated:", migrated.stdout)

    def test_only_noncolliding_skills_sh_skill_is_preserved_without_partial_state(self):
        config = self.home / ".config/opencode/skills"
        config.mkdir(parents=True)
        other = config / "unrelated"
        other.mkdir()
        (other / "SKILL.md").write_text("third-party skill\n")
        lock = self.home / ".agents/.skill-lock.json"
        lock.parent.mkdir(parents=True)
        lock.write_text(json.dumps({"version": 3, "skills": {
            "unrelated": {"source": "elsewhere/tools", "sourceType": "github"}}}))
        before = (other / "SKILL.md").read_bytes()
        first = self.install()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("state=installed", first.stdout)
        revision = self.next_revision()
        updated = self.install(revision=revision)
        self.assertEqual(updated.returncode, 0, updated.stderr)
        self.assertIn("state=updated", updated.stdout)
        repeated = self.install(revision=revision)
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertIn("state=already current", repeated.stdout)
        for result in (first, updated, repeated):
            self.assertIn(f"preserved: skill skills.sh sem colisão (intocada): {other}", result.stdout)
            self.assertNotIn("state=partial", result.stdout)
            self.assertNotIn("pending:", result.stdout)
        self.assertFalse(other.is_symlink())
        self.assertEqual((other / "SKILL.md").read_bytes(), before)

    def test_local_diagnostic_requires_scoped_opt_in(self):
        self.assertEqual(self.install().returncode, 0)
        revision = self.next_revision()
        project = self.root / "project"
        other = self.root / "other-project"
        for repo in (project, other):
            local = repo / ".opencode/skills/apply-issue"
            local.parent.mkdir(parents=True)
            shutil.copytree(self.data / "versions" / self.revision / "skills/apply-issue", local)
            rules = repo / "AGENTS.md"
            rules.write_text("# Local custom rules\n")
        result = self.install("--project", str(project), revision=revision)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("state=partial", result.stdout)
        self.assertIn("sombra local idêntica", result.stdout)
        self.assertTrue((project / ".opencode/skills/apply-issue").exists())
        self.assertTrue((other / ".opencode/skills/apply-issue").exists())
        authorized = self.install("--project", str(project), "--reconcile-path",
                                  ".opencode/skills/apply-issue", "--baseline-revision", self.revision,
                                  revision=revision)
        self.assertEqual(authorized.returncode, 0, authorized.stderr)
        self.assertFalse((project / ".opencode/skills/apply-issue").exists())
        self.assertTrue((other / ".opencode/skills/apply-issue").exists())
        self.assertEqual((project / "AGENTS.md").read_text(), "# Local custom rules\n")
        self.assertTrue(list((self.data / "migration-backups").iterdir()))

    def test_local_only_package_collisions_and_custom_precedence(self):
        self.assertEqual(self.install().returncode, 0)
        project = self.root / "project"
        for name in ("openspec-apply-change", "completely-unrelated", "apply-issue"):
            local = project / ".opencode/skills" / name
            local.mkdir(parents=True)
            (local / "SKILL.md").write_text("custom\n")
        result = self.install("--project", str(project))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("state=partial", result.stdout)
        self.assertIn("precedência local sobre global", result.stdout)
        self.assertIn("apply-issue", result.stdout)
        self.assertNotIn("openspec-apply-change", result.stdout)
        self.assertNotIn("completely-unrelated", result.stdout)

    def test_backup_symlink_and_ancestor_are_rejected_without_moves(self):
        self.assertEqual(self.install().returncode, 0)
        project = self.root / "project"
        local = project / ".opencode/skills/apply-issue"
        local.parent.mkdir(parents=True)
        shutil.copytree(self.data / "active/skills/apply-issue", local)
        outside = self.root / "outside"
        outside.mkdir()
        backups = self.data / "migration-backups"
        backups.symlink_to(outside)
        result = self.install("--project", str(project), "--reconcile-path",
                              ".opencode/skills/apply-issue")
        self.assertIn("symlink não confiável", result.stderr)
        self.assertTrue(local.exists())
        self.assertEqual(list(outside.iterdir()), [])
        backups.unlink()
        # A symlink higher in the selected project path is not authorization.
        alias = self.root / "alias"
        alias.symlink_to(project, target_is_directory=True)
        result = self.install("--project", str(alias), "--reconcile-path",
                              ".opencode/skills/apply-issue")
        self.assertIn("symlink", result.stderr)
        self.assertTrue(local.exists())

    def test_project_symlink_parent_and_modified_root_mode(self):
        self.assertEqual(self.install().returncode, 0)
        project = self.root / "project"
        local = project / ".opencode/skills/apply-issue"
        local.parent.mkdir(parents=True)
        shutil.copytree(self.data / "active/skills/apply-issue", local)
        mode = local.stat().st_mode & 0o777
        local.chmod(0o700 if mode != 0o700 else 0o755)
        result = self.install("--project", str(project), "--reconcile-path",
                              ".opencode/skills/apply-issue")
        self.assertIn("sem baseline", result.stderr)
        self.assertTrue(local.exists())
        alias = self.root / "alias"
        alias.symlink_to(project, target_is_directory=True)
        child = project / "child"
        child.mkdir()
        result = self.install("--project", str(alias / "child"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink não confiável", result.stderr)
        self.assertTrue(local.exists())
        ambiguous = self.install("--project", str(alias / "child/../child"))
        self.assertIn("percurso ambíguo", ambiguous.stderr)

    def test_cross_device_preflight_refuses_all_migrations(self):
        self.assertEqual(self.install().returncode, 0)
        project = self.root / "project"
        for name in ("apply-issue", "prepare-pr"):
            local = project / ".opencode/skills" / name
            local.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(self.data / "active/skills" / name, local)
        module = importlib.machinery.SourceFileLoader("installer_cross_device", str(ENTRY)).load_module()
        real_stat = Path.stat
        parent = project / ".opencode/skills"
        def cross_device(path, *args, **kwargs):
            result = real_stat(path, *args, **kwargs)
            if path == parent:
                # Preserve all stat fields except st_dev to simulate a mount.
                values = list(result)
                values[2] += 1
                return os.stat_result(values)
            return result
        args = types.SimpleNamespace(agent=["opencode"], revision=self.revision,
                                     migrate_global_skill=[], project=str(project),
                                     baseline_revision=None,
                                     reconcile_path=[".opencode/skills/apply-issue", ".opencode/skills/prepare-pr"])
        with mock.patch.dict(os.environ, self.env), mock.patch.object(Path, "stat", cross_device):
            with self.assertRaisesRegex(module.InstallError, "entre filesystems"):
                module.install(args, source=str(self.source))
        for name in ("apply-issue", "prepare-pr"):
            self.assertTrue((parent / name).exists())
        self.assertEqual(list((self.data / "migration-backups").iterdir()), [])

    def test_rename_exdev_after_first_move_rolls_back(self):
        self.assertEqual(self.install().returncode, 0)
        project = self.root / "project"
        parent = project / ".opencode/skills"
        parent.mkdir(parents=True)
        for name in ("apply-issue", "prepare-pr"):
            shutil.copytree(self.data / "active/skills" / name, parent / name)
        module = importlib.machinery.SourceFileLoader("installer_exdev", str(ENTRY)).load_module()
        original = Path.rename
        def rename(path, target):
            if path == parent / "prepare-pr":
                raise OSError(errno.EXDEV, "cross-device link")
            return original(path, target)
        args = types.SimpleNamespace(agent=["opencode"], revision=self.revision,
                                     migrate_global_skill=[], project=str(project),
                                     baseline_revision=None,
                                     reconcile_path=[".opencode/skills/apply-issue", ".opencode/skills/prepare-pr"])
        with mock.patch.dict(os.environ, self.env), mock.patch.object(Path, "rename", rename):
            with self.assertRaisesRegex(module.InstallError, "backups anteriores revertidos"):
                module.install(args, source=str(self.source))
        self.assertTrue((parent / "apply-issue").exists())
        self.assertTrue((parent / "prepare-pr").exists())
        self.assertEqual(list((self.data / "migration-backups").iterdir()), [])

    def test_untrusted_test_source_and_local_without_baseline(self):
        forbidden = call("python3", str(ENTRY), "--revision", self.revision,
                         "--agent", "opencode", "--source", str(self.source),
                         env={**self.env, "MY_AI_SKILLS_TEST_SOURCE": "1"})
        self.assertNotEqual(forbidden.returncode, 0)
        self.assertIn("unrecognized arguments: --source", forbidden.stderr)
        self.assertFalse(self.data.exists())
        self.assertEqual(self.install().returncode, 0)
        project = self.root / "project"
        local = project / ".opencode/skills/apply-issue"
        local.mkdir(parents=True)
        (local / "SKILL.md").write_text("custom")
        result = self.install("--project", str(project), "--reconcile-path", ".opencode/skills/apply-issue")
        self.assertIn("sem baseline", result.stderr)
        self.assertEqual((local / "SKILL.md").read_text(), "custom")

    def test_ai_workflow_copy_and_routing_are_explicit_only(self):
        self.assertEqual(self.install().returncode, 0)
        project = self.root / "project"
        shutil.copytree(self.source / "protocol", project / ".ai-workflow/protocol")
        (project / "CLAUDE.md").write_text("keep project rules")
        before = (project / ".ai-workflow/protocol").stat().st_mtime_ns
        diagnostic = self.install("--project", str(project))
        self.assertEqual(diagnostic.returncode, 0, diagnostic.stderr)
        self.assertIn("state=partial", diagnostic.stdout)
        self.assertEqual((project / ".ai-workflow/protocol").stat().st_mtime_ns, before)
        denied = self.install("--project", str(project), "--reconcile-path", ".ai-workflow/scripts")
        self.assertNotEqual(denied.returncode, 0)
        self.assertTrue((project / ".ai-workflow/protocol").exists())
        allowed = self.install("--project", str(project), "--baseline-revision", self.revision,
                               "--reconcile-path", ".ai-workflow/protocol")
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertFalse((project / ".ai-workflow/protocol").exists())
        self.assertEqual((project / "CLAUDE.md").read_text(), "keep project rules")
        routing = (ROOT / "skills/update-ai-workflow/SKILL.md").read_text()
        self.assertIn("ordinary development", routing)
        self.assertIn("Web-only", routing)
        self.assertIn("A separate\n   explicit request", routing)
        self.assertNotIn("npx skills add", routing)

    def test_published_recipe_matches_verified_entry_and_parity(self):
        revision = "c48ac58beadc0a9712f59f60458a5c3df3ed5bfb"
        published = "0e6103f3be6f1797978dba6bf09fd9485acf75346b4e9803ec271cd167cd75ed"
        self.assertEqual(hashlib.sha256(ENTRY.read_bytes()).hexdigest(), published)
        launcher = (ROOT / "scripts/install.sh").read_text()
        self.assertIn(f"entry_revision={revision}", launcher)
        self.assertIn(f"entry_sha256={published}", launcher)
        self.assertIn('python3 "$tmp" --revision "$revision" --agent opencode', launcher)
        updater = (ROOT / "scripts/update.sh").read_text()
        self.assertIn('git ls-remote --exit-code "$origin" "$ref"', updater)
        self.assertIn('sh "$tmp" --revision "$revision"', updater)
        for readme in ("README.md", "README.en.md"):
            text = (ROOT / readme).read_text()
            self.assertIn("/main/scripts/install.sh | sh", text)
            self.assertIn("/main/scripts/update.sh | sh", text)
            self.assertIn("https://github.com/rocker-code/my-ai-skills/wiki/", text)
            self.assertNotIn("8ddd9e60fbe773ca363293b8f0ff3a7b452eed37", text)
        self.assertEqual(revision, re.search(r'ENTRY_REVISION = "([0-9a-f]{40})"',
                                             (ROOT / "tests/smoke_global_opencode.py").read_text()).group(1))

    def test_published_recipe_in_disposable_home(self):
        # The immutable Git object exists locally before the feature branch is
        # published. Substitute only the download and remote transports; run
        # the README command and its launcher's independent digest gate unchanged.
        revision = "c48ac58beadc0a9712f59f60458a5c3df3ed5bfb"
        curl = self.bin / "curl"
        curl.write_text("#!/bin/sh\n"
                        "case \"$2\" in\n"
                        f"  */main/scripts/install.sh) cat {str(ROOT / 'scripts/install.sh')!r} ;;\n"
                        f"  *{revision}/scripts/install-global) /usr/bin/git -C {str(ROOT)!r} show {revision}:scripts/install-global > \"$4\" ;;\n"
                        "  *) exit 2 ;;\n"
                        "esac\n")
        curl.chmod(0o755)
        git = self.bin / "git"
        git.write_text("#!/bin/sh\n"
                       "if [ \"$1\" = ls-remote ] && [ \"$2\" = --exit-code ]; then\n"
                       f"  printf '%s\\trefs/heads/main\\n' {revision}\n"
                       "  exit 0\n"
                       "fi\n"
                       "if [ \"$3\" = remote ] && [ \"$4\" = add ] && [ \"$5\" = origin ]; then\n"
                       f"  exec /usr/bin/git \"$1\" \"$2\" remote add origin {str(ROOT)!r}\n"
                       "fi\nexec /usr/bin/git \"$@\"\n")
        git.chmod(0o755)
        readme = (ROOT / "README.md").read_text()
        snippet = readme.split("## Instalar ou atualizar\n", 1)[1].split("```bash\n", 1)[1].split("\n```", 1)[0]
        result = call("bash", "-c", snippet, cwd=self.root,
                      env={k: v for k, v in self.env.items()
                           if k != "MY_AI_SKILLS_TEST_SOURCE"}, timeout=90)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"active={revision}", result.stdout)
        self.assertEqual(json.loads((self.data / "active/manifest.json").read_text())["revision"], revision)

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

    def test_v1_and_fake_capabilities_rejected_before_writes(self):
        binary = self.bin / "opencode"
        for output in ("opencode v1.9.0 api run service", "opencode v2.2.6 without commands"):
            binary.write_text("#!/bin/sh\necho '" + output + "'\n")
            result = self.install()
            self.assertIn("OpenCode V2", result.stderr)
            self.assertFalse(self.data.exists())

    def test_open_spec_installer_digest_gate(self):
        # Exercise the actual fallback with an intercepted curl and no executable OpenSpec.
        (self.bin / "openspec").unlink()
        marker = self.root / "executed"
        curl = self.bin / "curl"
        curl.write_text("#!/bin/sh\nwhile [ \"$1\" != -o ]; do shift; done\nprintf '#!/bin/sh\\ntouch " + str(marker) + "\\n' > \"$2\"\n")
        curl.chmod(0o755)
        for executable in ("python3", "git", "gh", "jq", "bash"):
            (self.bin / executable).symlink_to(shutil.which(executable))
        result = self.install(env={**self.env, "PATH": str(self.bin)})
        self.assertIn("Digest do instalador OpenSpec divergente", result.stderr)
        self.assertFalse(marker.exists())

    def test_fake_active_manifest_and_extra_tree_rejected(self):
        self.data.mkdir(parents=True)
        version = self.data / "versions" / ("a" * 40)
        version.mkdir(parents=True)
        (version / "manifest.json").write_text(json.dumps({"schema": 1, "origin": "elsewhere", "revision": "a" * 40, "agents": ["opencode"], "files": {}}))
        (self.data / "active").symlink_to(Path("versions") / version.name)
        fail = self.install()
        self.assertNotEqual(fail.returncode, 0)
        self.assertEqual(os.readlink(self.data / "active"), str(Path("versions") / version.name))
        (self.data / "active").unlink()
        shutil.rmtree(version)
        self.assertEqual(self.install().returncode, 0)
        active = self.data / "active"
        (active / "skills/unknown.txt").write_text("unknown")
        self.assertNotEqual(self.install().returncode, 0)
        (active / "skills/unknown.txt").unlink()
        (active / "skills/unknown-link").symlink_to("SKILL.md")
        self.assertNotEqual(self.install().returncode, 0)
        self.assertTrue((active / "skills/unknown-link").is_symlink())
        (active / "skills/unknown-link").unlink()
        (active / "skills/empty-extra").mkdir()
        self.assertNotEqual(self.install().returncode, 0)
        (active / "skills/empty-extra").rmdir()
        directory = active / "skills"
        original_mode = directory.stat().st_mode & 0o777
        directory.chmod(0o700 if original_mode != 0o700 else 0o755)
        self.assertNotEqual(self.install().returncode, 0)
        directory.chmod(original_mode)

    def test_update_preserves_extras_and_ignores_python_cache(self):
        self.assertEqual(self.install().returncode, 0)
        old = (self.data / "active").resolve()
        cache = old / "scripts/__pycache__"
        cache.mkdir()
        (cache / "worktree_registry.cpython-314.pyc").write_bytes(b"cache")
        self.assertEqual(self.install().returncode, 0)
        extra = old / "notes.txt"
        extra.write_text("keep me")
        (old / "empty-extra").mkdir()
        revision = self.next_revision()
        result = self.install(revision=revision)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(extra), result.stdout)
        self.assertIn("preserved:", result.stdout)
        self.assertEqual(extra.read_text(), "keep me")
        self.assertTrue(cache.is_dir())
        self.assertFalse((self.data / "active/notes.txt").exists())
        self.assertEqual((self.data / "active").resolve().name, revision)

    def test_update_rejects_missing_or_modified_managed_file_with_path(self):
        self.assertEqual(self.install().returncode, 0)
        old = (self.data / "active").resolve()
        path = old / "scripts/worktree-reservation"
        original = path.read_bytes()
        revision = self.next_revision()
        for content in (None, b"modified"):
            if content is None:
                path.unlink()
            else:
                path.write_bytes(content)
                path.chmod(0o755)
            result = self.install(revision=revision)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(str(path), result.stderr)
            self.assertEqual((self.data / "active").resolve(), old)
            path.write_bytes(original)
            path.chmod(0o755)

    def test_removed_skill_reconciliation_and_rollback(self):
        self.assertEqual(self.install().returncode, 0)
        name = "apply-issue"
        link = self.home / ".config/opencode/skills" / name
        old = os.readlink(self.data / "active")
        shutil.rmtree(self.source / "skills" / name)
        self.git("add", "-A")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-qm", "remove skill")
        revision = self.git("rev-parse", "HEAD").stdout.strip()
        fail = self.install(revision=revision, env={**self.env, "MY_AI_SKILLS_FAIL_AT": "guidance"})
        self.assertNotEqual(fail.returncode, 0)
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(self.data / "active"), old)
        success = self.install(revision=revision)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertFalse(link.is_symlink())

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

    def test_failure_after_skills_leaves_previous_snapshot(self):
        self.assertEqual(self.install().returncode, 0)
        old = os.readlink(self.data / "active")
        (self.source / "skills/extra").mkdir()
        (self.source / "skills/extra/SKILL.md").write_text("---\nname: extra\ndescription: extra\n---\n")
        self.git("add", "skills/extra")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-qm", "extra")
        next_revision = self.git("rev-parse", "HEAD").stdout.strip()
        fail = self.install(revision=next_revision, env={**self.env, "MY_AI_SKILLS_FAIL_AT": "skills"})
        self.assertIn("Falha simulada", fail.stderr)
        self.assertEqual(os.readlink(self.data / "active"), old)
        self.assertFalse((self.home / ".config/opencode/skills/extra").is_symlink())

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
                planned = call(str(helper), "reserve", "--planned", "--path", str(worktree),
                               "--repository", str(repo), "--issue", "https://github.com/example/one/issues/50",
                               "--branch", "test-branch", "--session", "tester", "--run", "run-50",
                               cwd=repo, env=self.env)
                self.assertEqual(planned.returncode, 0, planned.stderr)
                self.git("worktree", "add", "-qb", "test-branch", str(worktree), cwd=repo)
                common = self.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=worktree).stdout.strip()
                self.assertEqual(common, self.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=repo).stdout.strip())
                owned = call(str(helper), "reserve", "--path", str(worktree),
                             "--issue", "https://github.com/example/one/issues/50", "--branch", "test-branch",
                             "--session", "tester", "--run", "run-50", cwd=worktree, env=self.env)
                self.assertEqual(owned.returncode, 0, owned.stderr)
                verified = call(str(helper), "verify", "--path", str(worktree), "--session", "tester", cwd=worktree, env=self.env)
                self.assertEqual(verified.returncode, 0, verified.stderr)
                self.assertTrue((Path(common) / "ai-workflow/worktrees.json").is_file())
                checkout = worktree
            else:
                self.assertNotEqual(common, self.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=repo).stdout.strip())
                self.assertFalse((Path(self.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=repo).stdout.strip()) / "ai-workflow/worktrees.json").exists())
                checkout = repo
            recorded = call(str(evidence), "--checkout", str(checkout), "record", "--obligation", "T2:file",
                            "--selection", "file", "--", "python3", "-c", "print('ok')", cwd=checkout, env=self.env)
            self.assertEqual(recorded.returncode, 0, recorded.stderr)
            receipt = json.loads(recorded.stderr.splitlines()[0])
            own_common = Path(self.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=checkout).stdout.strip())
            self.assertTrue((own_common / "ai-workflow/evidence" / receipt["evidence_id"]).exists())
            if name == "two":
                self.assertFalse((Path(common) / "ai-workflow/evidence" / receipt["evidence_id"]).exists())

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

    @unittest.skipUnless(shutil.which("openspec"), "official OpenSpec CLI unavailable")
    def test_existing_other_tool_requires_explicit_union_on_first_use(self):
        (self.bin / "openspec").unlink()
        (self.bin / "openspec").symlink_to(shutil.which("openspec"))
        env = {**self.env, "OPENSPEC_TELEMETRY": "0"}
        repo = self.root / "existing-other-tool"
        repo.mkdir()
        initial = call(str(self.bin / "openspec"), "init", "--tools", "codex", str(repo), env=env)
        self.assertEqual(initial.returncode, 0, initial.stderr)
        config = repo / "openspec/config.yaml"
        before = config.read_bytes()
        self.assertEqual(self.install(env=env).returncode, 0)
        self.assertFalse((repo / ".opencode").exists())
        self.assertEqual(config.read_bytes(), before)
        dry = call(str(self.bin / "openspec"), "update", "--dry-run", "--json", str(repo), env=env)
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertTrue((repo / ".agents/skills/openspec-explore/SKILL.md").exists())
        # Explicitly authorized union, never 'init --tools opencode' alone.
        union = call(str(self.bin / "openspec"), "init", "--tools", "codex,opencode", str(repo), env=env)
        self.assertEqual(union.returncode, 0, union.stderr)
        self.assertTrue((repo / ".agents/skills/openspec-explore/SKILL.md").exists())
        self.assertTrue((repo / ".opencode/skills/openspec-apply-change/SKILL.md").exists())
        # CLI success is not a successful chat integration: the migrated
        # custom profile may be skills-only and omit all /opsx-* commands.
        if not (repo / ".opencode/commands/opsx-apply.md").exists():
            self.assertIn("sem essa prova reporte bloqueio", (self.home / ".config/opencode/AGENTS.md").read_text())


if __name__ == "__main__":
    unittest.main()
