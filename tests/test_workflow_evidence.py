import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/workflow-evidence"
sys.path.insert(0, str(ROOT / "scripts"))
from workflow_evidence import (code_snapshot, export_bundle, from_github, import_bundle, load_manifest,
                               public_projection, record_dir, runner, scrub, verify_manifest)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        (self.repo / "a.py").write_text("a\n")
        (self.repo / ".gitignore").write_text("config.local\n")
        self.git("add", "a.py", ".gitignore")
        self.git("commit", "-qm", "initial")
        self.git("remote", "add", "origin", "https://github.com/example/repo.git")
        self.env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, text=True).stdout.strip()

    def cli(self, *args, repo=None, env=None):
        return subprocess.run([sys.executable, str(CLI), "--checkout", str(repo or self.repo), *args],
                              cwd=repo or self.repo, env=env or self.env, text=True, capture_output=True)

    def record(self, *opts, command=None):
        result = self.cli("record", "--obligation", "T1:a.py", *opts,
                          "--", *(command or [sys.executable, "-c", "print('ok')"]))
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence_id = json.loads(result.stderr.splitlines()[0])["evidence_id"]
        return evidence_id, load_manifest(record_dir(self.repo, evidence_id))

    def verify(self, evidence_id, *options):
        result = self.cli("verify", evidence_id, "--format", "json", *options)
        return result.returncode, json.loads(result.stdout)

    def test_record_requires_obligation(self):
        result = self.cli("record", "--", "true")
        self.assertEqual(result.returncode, 2)

    def test_local_repository_without_origin_can_verify(self):
        self.git("remote", "remove", "origin")
        evidence_id, manifest = self.record()
        self.assertIsNone(manifest["repository"])
        self.assertEqual(self.verify(evidence_id)[1]["state"], "verified")

    def test_known_local_repository_mismatch_rejected_even_with_same_code(self):
        evidence_id, manifest = self.record()
        self.git("remote", "set-url", "origin", "https://github.com/other/project.git")
        self.assertEqual(self.git("rev-parse", "HEAD"), manifest["code"]["head"])
        result = self.verify(evidence_id)[1]
        self.assertEqual((result["state"], result["reasons"]), ("stale", ["repository_changed"]))

    def test_required_local_gate_needs_repository_identity(self):
        evidence_id, _ = self.record("--required-gate", "local")
        self.git("remote", "remove", "origin")
        result = self.verify(evidence_id)[1]
        self.assertEqual((result["state"], result["reasons"]),
                         ("incomplete", ["repository_identity_unavailable"]))
        path_only, _ = self.record()
        self.assertEqual(self.verify(path_only)[1]["state"], "verified")
        required, _ = self.record("--required-gate", "local")
        self.assertEqual(self.verify(required)[1]["state"], "incomplete")

    def test_failing_command_recorded_and_exit_propagated(self):
        result = self.cli("record", "--obligation", "T1", "--", sys.executable, "-c", "exit(7)")
        self.assertEqual(result.returncode, 7)
        evidence_id = json.loads(result.stderr.splitlines()[0])["evidence_id"]
        manifest = load_manifest(record_dir(self.repo, evidence_id))
        self.assertEqual(manifest["exit_code"], 7)
        self.assertEqual(self.verify(evidence_id)[1]["state"], "verified")
        self.assertEqual(self.verify(evidence_id)[1]["result"], "failed")

    def test_no_report_counts_are_unknown_not_zero(self):
        _, manifest = self.record()
        self.assertEqual(manifest["counts"], {"tests": None, "failures": None, "errors": None,
                                              "skipped": None, "source": "none"})

    def test_same_head_different_diff_is_stale(self):
        (self.repo / "a.py").write_text("before\n")
        evidence_id, _ = self.record()
        (self.repo / "a.py").write_text("after\n")
        _, result = self.verify(evidence_id)
        self.assertEqual(result["state"], "stale")
        self.assertIn("a.py", result["changed_paths"])

    def test_later_commit_is_stale(self):
        evidence_id, _ = self.record()
        (self.repo / "a.py").write_text("commit\n")
        self.git("add", "a.py")
        self.git("commit", "-qm", "later")
        self.assertEqual(self.verify(evidence_id)[1]["state"], "stale")

    def test_ignored_config_change_is_stale(self):
        (self.repo / "config.local").write_text("first")
        evidence_id, _ = self.record("--config", "config.local")
        (self.repo / "config.local").write_text("second")
        self.assertIn("config.local", self.verify(evidence_id)[1]["changed_paths"])

    def test_staged_index_change_is_stale(self):
        (self.repo / "a.py").write_text("staged")
        self.git("add", "a.py")
        evidence_id, _ = self.record()
        (self.repo / "a.py").write_text("another")
        self.git("add", "a.py")
        (self.repo / "a.py").write_text("staged")
        self.assertEqual(self.verify(evidence_id)[1]["state"], "stale")

    def test_concurrent_change_is_ambiguous(self):
        evidence_id, manifest = self.record(command=[sys.executable, "-c", "open('a.py','w').write('during')"])
        self.assertNotEqual(manifest["code"]["fingerprint"], manifest["code"]["fingerprint_after"])
        self.assertEqual(self.verify(evidence_id)[1]["state"], "ambiguous")

    def test_in_tree_report_not_ambiguous(self):
        command = [sys.executable, "-c", "import os; os.makedirs('__pycache__', exist_ok=True); "
                   "open('__pycache__/generated.pyc','wb').write(b'bytecode'); "
                   "open('report.xml','w').write('<testsuite tests=\"1\"/>')"]
        evidence_id, manifest = self.record("--report", "report.xml", command=command)
        self.assertNotIn("status_note", manifest)
        self.assertEqual(manifest["counts"]["tests"], 1)
        self.assertEqual(self.verify(evidence_id)[1]["state"], "verified")

    def test_tracked_output_cannot_hide_code(self):
        for option in ("--report", "--artifact", "--output-dir"):
            with self.subTest(option=option):
                path = "a.py" if option != "--output-dir" else "source"
                if option == "--output-dir":
                    (self.repo / "source").mkdir(exist_ok=True)
                    (self.repo / "source" / "tracked.py").write_text("tracked")
                    self.git("add", "source/tracked.py")
                result = self.cli("record", "--obligation", "T1", option, path, "--", "true")
                self.assertEqual(result.returncode, 2)
                self.assertIn("tracked code", result.stderr)
        evidence_id, manifest = self.record()
        manifest["code"]["excluded_paths"] = ["a.py"]
        self.assertEqual(verify_manifest(manifest, record_dir(self.repo, evidence_id), self.repo)["state"], "incomplete")

    def test_output_glob_cannot_hide_tracked_code(self):
        (self.repo / "source").mkdir()
        (self.repo / "source/a.py").write_text("tracked")
        self.git("add", "source/a.py")
        self.git("commit", "-qm", "source")
        for option, path in (("--output-dir", "s*"), ("--report", "source/*.py"),
                             ("--artifact", "source/a.p?")):
            with self.subTest(option=option):
                result = self.cli("record", "--obligation", "T1", option, path, "--", "true")
                self.assertEqual(result.returncode, 2)
                self.assertIn("glob metacharacters", result.stderr)
        evidence_id, manifest = self.record()
        for exclusion in ("s*/**", "source/*.py", "source/a.p?"):
            with self.subTest(exclusion=exclusion):
                manifest["code"]["excluded_paths"] = [exclusion]
                self.assertEqual(verify_manifest(manifest, record_dir(self.repo, evidence_id), self.repo)["state"],
                                 "incomplete")

    def test_untracked_output_made_tracked_invalidates_evidence(self):
        evidence_id, manifest = self.record("--report", "report.xml")
        (self.repo / "report.xml").write_text("tracked")
        self.git("add", "report.xml")
        self.assertEqual(verify_manifest(manifest, record_dir(self.repo, evidence_id), self.repo)["state"], "incomplete")

    def test_missing_log_incomplete(self):
        evidence_id, _ = self.record()
        (record_dir(self.repo, evidence_id) / "artifacts/execution.log").unlink()
        self.assertEqual(self.verify(evidence_id)[1]["state"], "incomplete")

    def test_missing_report_incomplete(self):
        evidence_id, manifest = self.record("--report", "absent.xml")
        self.assertEqual(manifest["artifacts"][-1]["state"], "missing")
        self.assertEqual(self.verify(evidence_id)[1]["state"], "incomplete")

    def test_interrupted_incomplete(self):
        evidence_id, manifest = self.record()
        manifest["exit_code"] = None
        manifest["status"] = "interrupted"
        self.assertEqual(verify_manifest(manifest, record_dir(self.repo, evidence_id), self.repo)["state"], "incomplete")

    def test_malformed_imported_identity_is_incomplete(self):
        evidence_id, manifest = self.record()
        manifest["code"]["state"].pop("entries")
        (self.repo / "a.py").write_text("different")
        result = verify_manifest(manifest, record_dir(self.repo, evidence_id), self.repo)
        self.assertEqual(result["state"], "incomplete")

    def test_environment_id_drift_is_stale(self):
        evidence_id, _ = self.record("--env-id", "CI=runner-a")
        self.assertEqual(self.verify(evidence_id, "--env-id", "CI=runner-b")[1]["state"], "stale")

    def test_missing_environment_id_is_incomplete(self):
        evidence_id, _ = self.record("--env-id", "CI=runner-a")
        self.assertEqual(self.verify(evidence_id)[1]["state"], "incomplete")

    def test_tool_version_drift_is_stale(self):
        evidence_id, _ = self.record("--tool", "python=3.10")
        self.assertEqual(self.verify(evidence_id, "--tool", "python=3.11")[1]["state"], "stale")

    def test_env_names_alone_do_not_prove_compatibility(self):
        result = self.cli("record", "--obligation", "T1", "--env-name", "CI", "--", "true")
        self.assertEqual(result.returncode, 2)

    def test_environment_values_never_persisted(self):
        env = {**self.env, "CI": "very_private_value"}
        result = self.cli("record", "--obligation", "T1", "--env-name", "CI", "--env-id", "CI=runner-a",
                          "--", "true", env=env)
        evidence_id = json.loads(result.stderr.splitlines()[0])["evidence_id"]
        self.assertNotIn("very_private_value", json.dumps(load_manifest(record_dir(self.repo, evidence_id))))

    def test_secret_argv_masked(self):
        self.assertEqual(scrub(["--token=abc123", "Authorization: Bearer"])[0], "--token=[REDACTED]")
        evidence_id, manifest = self.record(command=[sys.executable, "-c", "print('ok')", "--token=abc123"])
        self.assertNotIn("abc123", json.dumps(manifest))

        for args in (["Authorization: Bearer abc123"], ["Authorization:", "Bearer abc123"],
                     ["Authorization:", "Bearer", "abc123"], ["Authorization: Bearer", "abc123"],
                     ["-H", "Authorization: Bearer abc123"]):
            with self.subTest(args=args):
                self.assertNotIn("abc123", json.dumps(scrub(args)))
        _, manifest = self.record(command=[sys.executable, "-c", "print('ok')", "Authorization: Bearer abc123"])
        package = Path(self.temp.name) / "scrubbed.tar.gz"
        export_bundle(self.repo, manifest["evidence_id"], package)
        with tarfile.open(package, "r:gz") as tar:
            self.assertNotIn("abc123", tar.extractfile("manifest.json").read().decode())

    def test_required_local_gate_needs_clean_candidate_and_execution(self):
        (self.repo / "a.py").write_text("dirty")
        evidence_id, _ = self.record("--required-gate", "local")
        status, result = self.verify(evidence_id)
        self.assertEqual((status, result["state"], result["obligations"][0]["gate"]),
                         (3, "verified", "pending"))
        self.assertEqual(result["recovery"]["obligations"], ["T1"])

    def test_untyped_local_evidence_is_not_a_required_gate_on_dirty_or_clean_head(self):
        for dirty in (True, False):
            with self.subTest(dirty=dirty):
                if dirty:
                    (self.repo / "a.py").write_text("dirty")
                else:
                    (self.repo / "a.py").write_text("a\n")
                evidence_id, _ = self.record()
                status, result = self.verify(evidence_id)
                self.assertEqual((status, result["state"], result["result"]), (3, "verified", "passed"))
                self.assertEqual(result["obligations"][0]["gate"], "not_required")
                self.assertEqual(result["reasons"], ["no_required_gate"])
                self.assertEqual(result["recovery"]["obligations"], [])
                self.assertIn("gates: T1=not_required", self.cli("verify", evidence_id).stdout)

    def test_typed_local_gate_satisfied_only_on_clean_head(self):
        evidence_id, _ = self.record("--required-gate", "local")
        status, result = self.verify(evidence_id)
        self.assertEqual((status, result["state"], result["result"], result["obligations"][0]["gate"]),
                         (0, "verified", "passed", "satisfied"))

    def test_record_verified_from_other_worktree(self):
        evidence_id, _ = self.record()
        other = Path(self.temp.name) / "other"
        self.git("worktree", "add", "-q", "-b", "other", str(other))
        result = self.cli("verify", evidence_id, "--format", "json", repo=other)
        self.assertEqual(json.loads(result.stdout)["state"], "verified")

    def test_bundle_import_in_other_clone(self):
        evidence_id, _ = self.record("--required-gate", "local")
        package = Path(self.temp.name) / "bundle.tar.gz"
        export_bundle(self.repo, evidence_id, package)
        clone = Path(self.temp.name) / "clone"
        subprocess.run(["git", "clone", "-q", str(self.repo), str(clone)], check=True)
        subprocess.run(["git", "-C", str(clone), "remote", "set-url", "origin",
                        "https://github.com/example/repo.git"], check=True)
        self.assertEqual(import_bundle(clone, package), evidence_id)
        self.assertEqual(self.cli("verify", evidence_id, "--format", "json", repo=clone).returncode, 0)

    def test_import_export_import_regenerates_single_checksum_file(self):
        evidence_id, _ = self.record("--required-gate", "local")
        first = Path(self.temp.name) / "first.tar.gz"
        export_bundle(self.repo, evidence_id, first)
        second_clone = Path(self.temp.name) / "second-clone"
        third_clone = Path(self.temp.name) / "third-clone"
        for clone in (second_clone, third_clone):
            subprocess.run(["git", "clone", "-q", str(self.repo), str(clone)], check=True)
            subprocess.run(["git", "-C", str(clone), "remote", "set-url", "origin",
                            "https://github.com/example/repo.git"], check=True)
        self.assertEqual(import_bundle(second_clone, first), evidence_id)
        second = Path(self.temp.name) / "second.tar.gz"
        export_bundle(second_clone, evidence_id, second)
        with tarfile.open(second, "r:gz") as bundle:
            names = bundle.getnames()
            self.assertEqual(names.count("SHA256SUMS"), 1)
            self.assertNotIn("SHA256SUMS", bundle.extractfile("SHA256SUMS").read().decode())
        self.assertEqual(import_bundle(third_clone, second), evidence_id)
        self.assertEqual(self.cli("verify", evidence_id, "--format", "json", repo=third_clone).returncode, 0)

    def test_tampered_bundle_incomplete(self):
        evidence_id, _ = self.record()
        package = Path(self.temp.name) / "bundle.tar.gz"
        export_bundle(self.repo, evidence_id, package)
        tampered = Path(self.temp.name) / "tampered.tar.gz"
        with tarfile.open(package, "r:gz") as source, tarfile.open(tampered, "w:gz") as target:
            for member in source:
                data = source.extractfile(member).read()
                if member.name == "artifacts/execution.log":
                    data = b"tampered"
                member.size = len(data)
                target.addfile(member, io.BytesIO(data))
        clone = Path(self.temp.name) / "clone"
        subprocess.run(["git", "clone", "-q", str(self.repo), str(clone)], check=True)
        with self.assertRaisesRegex(ValueError, "checksum"):
            import_bundle(clone, tampered)

    def test_import_rejects_path_traversal(self):
        package = Path(self.temp.name) / "unsafe.tar.gz"
        with tarfile.open(package, "w:gz") as target:
            for name in ("../escape", "SHA256SUMS", "manifest.json"):
                info = tarfile.TarInfo(name)
                info.size = 0
                target.addfile(info, io.BytesIO(b""))
        with self.assertRaisesRegex(ValueError, "unsafe"):
            import_bundle(self.repo, package)

    def test_import_rejects_oversized_or_too_many_members_without_installing(self):
        from workflow_evidence import MAX_MEMBER_BYTES, MAX_BUNDLE_MEMBERS
        for mode in ("large", "many"):
            with self.subTest(mode=mode):
                package = Path(self.temp.name) / f"{mode}.tar.gz"
                with tarfile.open(package, "w:gz") as target:
                    count = 1 if mode == "large" else MAX_BUNDLE_MEMBERS + 1
                    for index in range(count):
                        info = tarfile.TarInfo(f"member-{index}")
                        info.size = MAX_MEMBER_BYTES + 1 if mode == "large" else 0
                        target.addfile(info, io.BytesIO(b"\0" * info.size))
                with self.assertRaisesRegex(ValueError, "limit|unsafe"):
                    import_bundle(self.repo, package)
        self.assertEqual(list((self.repo / ".git/ai-workflow/evidence").glob("ev-*")), [])

    def test_import_bounds_pax_header_before_member_is_yielded(self):
        package = Path(self.temp.name) / "pax.tar.gz"
        with tarfile.open(package, "w:gz", format=tarfile.PAX_FORMAT) as target:
            info = tarfile.TarInfo("safe")
            info.pax_headers = {"comment": "x" * 8192}
            info.size = 0
            target.addfile(info, io.BytesIO())
        with patch("workflow_evidence.MAX_ARCHIVE_BYTES", 2048):
            with self.assertRaisesRegex(ValueError, "size limit"):
                import_bundle(self.repo, package)
        self.assertEqual(list((self.repo / ".git/ai-workflow/evidence").glob("ev-*")), [])

    def test_unknown_extensions_preserved(self):
        evidence_id, manifest = self.record()
        manifest["extensions"]["example_tool"] = {"unknown": "retained"}
        from workflow_evidence import save_manifest
        save_manifest(record_dir(self.repo, evidence_id), manifest)
        package = Path(self.temp.name) / "bundle.tar.gz"
        export_bundle(self.repo, evidence_id, package)
        with tarfile.open(package, "r:gz") as tar:
            self.assertEqual(json.load(tar.extractfile("manifest.json"))["extensions"], manifest["extensions"])

    def test_public_projection_omits_private_fields(self):
        evidence_id, manifest = self.record("--selection", "private_selection")
        manifest["extensions"] = {"secret": "very_private_value"}
        projection = public_projection(manifest)
        serialized = json.dumps(projection)
        for forbidden in ("private_selection", "very_private_value", "runner", "fingerprint", "config_paths", "obligations"):
            self.assertNotIn(forbidden, serialized)
        manifest["code"]["head"] = "not-a-sha"
        with self.assertRaises(ValueError):
            public_projection(manifest)

    def test_change_affects_only_one_obligation(self):
        evidence_id, manifest = self.record()
        manifest["obligations"].append({"id": "T2", "required_gate": None, "relevant_paths": ["b.py"]})
        (self.repo / "a.py").write_text("new")
        result = verify_manifest(manifest, record_dir(self.repo, evidence_id), self.repo)
        self.assertEqual([o["impact"] for o in result["obligations"]], ["affected", "unaffected"])

    def test_required_gate_always_affected(self):
        evidence_id, manifest = self.record("--required-gate", "local")
        manifest["obligations"][0]["relevant_paths"] = ["b.py"]
        (self.repo / "a.py").write_text("new")
        result = verify_manifest(manifest, record_dir(self.repo, evidence_id), self.repo)
        self.assertEqual(result["obligations"][0]["impact"], "affected")

    def test_hosted_result_not_applicable_for_local_gate(self):
        evidence_id, manifest = self.record()
        manifest["kind"] = "hosted"
        manifest["obligations"][0]["required_gate"] = "local"
        manifest["hosted"] = {"url": "https://github.com/example/repo/actions/runs/123", "run_id": "123"}
        self.assertEqual(verify_manifest(manifest, record_dir(self.repo, evidence_id), self.repo)["state"], "not_applicable")

    def test_register_hosted_confirms_origin_and_does_not_run_ci(self):
        from types import SimpleNamespace
        from workflow_evidence import register_hosted
        options = SimpleNamespace(url="https://github.com/example/repo/actions/runs/123", obligation=["T1"],
                                  required_gate="hosted", selection="ci")
        with patch("workflow_evidence.gh", return_value=self.fake_run()):
            evidence_id = register_hosted(self.repo, options)
        manifest = load_manifest(record_dir(self.repo, evidence_id))
        self.assertEqual(manifest["hosted"]["head"], self.git("rev-parse", "HEAD"))
        self.assertTrue(manifest["hosted"]["clean"])

    def test_final_gate_requires_exact_final_head_after_archive_and_prepare(self):
        evidence_id, _ = self.record("--required-gate", "local")
        self.assertEqual(self.verify(evidence_id)[0], 0)
        (self.repo / "a.py").write_text("archive")
        self.git("add", "a.py")
        self.git("commit", "-qm", "archive and prepare")
        self.assertEqual(self.verify(evidence_id)[1]["state"], "stale")
        current_id, _ = self.record("--required-gate", "local")
        self.assertEqual(self.verify(current_id)[0], 0)
        (self.repo / "a.py").write_text("later")
        self.git("add", "a.py")
        self.git("commit", "-qm", "later")
        self.assertEqual(self.verify(current_id)[1]["state"], "stale")

    def test_later_commit_invalidates_final_gate(self):
        evidence_id, _ = self.record("--required-gate", "local")
        (self.repo / "new-file").write_text("post-gate commit")
        self.git("add", "new-file")
        self.git("commit", "-qm", "post-gate")
        self.assertEqual(self.verify(evidence_id)[1]["state"], "stale")

    def test_list_by_obligation_shows_selection(self):
        self.record("--selection", "tests/")
        result = self.cli("list", "--obligation", "T1")
        self.assertIn("tests/", result.stdout)
        self.assertEqual(self.cli("list", "--obligation", "T2").stdout, "")

    def test_prune_dry_run_by_default(self):
        evidence_id, _ = self.record()
        self.assertIn("would remove", self.cli("prune", "--evidence-id", evidence_id).stdout)
        self.assertTrue(record_dir(self.repo, evidence_id).exists())

    def test_evidence_id_emitted_before_command_runs(self):
        process = subprocess.Popen([sys.executable, str(CLI), "--checkout", str(self.repo), "record", "--obligation", "T1",
                                    "--", sys.executable, "-c", "import time; time.sleep(.5)"],
                                   cwd=self.repo, env=self.env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        line = process.stderr.readline()
        evidence_id = json.loads(line)["evidence_id"]
        self.assertIsNone(process.poll())
        self.assertEqual(load_manifest(record_dir(self.repo, evidence_id))["status"], "running")
        self.assertEqual(process.wait(timeout=5), 0)
        process.stdout.close()
        process.stderr.close()

    def test_public_local_metadata_only_without_logs(self):
        evidence_id, manifest = self.record()
        projection = public_projection(manifest)
        result = verify_manifest(projection, record_dir(self.repo, evidence_id), self.repo, projection=True)
        self.assertEqual(result["state"], "metadata_only")

    def test_invalid_public_projection_incomplete(self):
        evidence_id, manifest = self.record()
        projection = public_projection(manifest)
        projection["unknown"] = "private"
        result = verify_manifest(projection, self.repo, self.repo, projection=True)
        self.assertEqual(result["state"], "incomplete")

    def fake_run(self, head=None, conclusion="success", path=".github/workflows/test.yml@main"):
        return {"id": 123, "repository": {"full_name": "example/repo"},
                "head_sha": head or self.git("rev-parse", "HEAD"), "status": "completed",
                "conclusion": conclusion, "path": path, "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:01:00Z"}

    def hosted_projection(self):
        return {"schema": "my-ai-skills.test-evidence-public/v1", "evidence_id": "ev-20261104T030000Z-1a2b3c4d",
                "kind": "hosted", "repository": "example/repo", "code": {"head": self.git("rev-parse", "HEAD")},
                "status": "passed", "hosted": {"url": "https://github.com/example/repo/actions/runs/123", "run_id": "123"}}

    def test_published_hosted_verified_after_api_confirmation(self):
        projection = self.hosted_projection()
        with patch("workflow_evidence.gh", return_value=self.fake_run()):
            result = verify_manifest(projection, self.repo, self.repo, projection=True)
        self.assertEqual((result["state"], result["result"]), ("verified", "passed"))
        self.assertEqual(result["obligations"], [])

    def test_public_hosted_without_gate_is_not_cli_pass(self):
        projection = self.hosted_projection()
        from workflow_evidence import comment_payload, save_manifest
        script = Path(self.temp.name) / "gh"
        script.write_text("#!/usr/bin/env python3\nimport json,sys\n" +
                           f"print(json.dumps({repr([{'body': comment_payload(projection)}])} " +
                           f"if '--paginate' in sys.argv else {repr(self.fake_run())}))\n")
        script.chmod(0o755)
        env = {**self.env, "PATH": str(script.parent) + os.pathsep + self.env["PATH"]}
        public = self.cli("verify", projection["evidence_id"], "--from-github",
                          "https://github.com/example/repo/pull/12", "--format", "json", env=env)
        self.assertEqual(public.returncode, 3, public.stderr)
        self.assertEqual(json.loads(public.stdout)["state"], "verified")
        self.assertEqual(json.loads(public.stdout)["obligations"], [])
        hosted = {**projection, "schema": "my-ai-skills.test-evidence/v1", "command": {}, "runner": {},
                  "started_at": "x", "finished_at": "y", "artifacts": [], "exit_code": 0,
                  "obligations": [{"id": "T1", "required_gate": None}],
                  "hosted": {**projection["hosted"], "clean": True}}
        save_manifest(record_dir(self.repo, projection["evidence_id"]), hosted)
        cli = self.cli("verify", projection["evidence_id"], "--format", "json", env=env)
        self.assertEqual(cli.returncode, 3, cli.stderr)
        self.assertEqual(json.loads(cli.stdout)["obligations"][0]["gate"], "not_required")
        self.assertEqual(json.loads(cli.stdout)["reasons"], ["no_required_gate"])

    def test_published_hosted_unconfirmed_metadata_only(self):
        with patch("workflow_evidence.gh", side_effect=ValueError("unavailable")):
            result = verify_manifest(self.hosted_projection(), self.repo, self.repo, projection=True)
        self.assertEqual(result["state"], "metadata_only")

    def test_hosted_gate_requires_independent_obligation_binding(self):
        import base64
        projection = self.hosted_projection()
        manifest = {**projection, "schema": "my-ai-skills.test-evidence/v1", "command": {}, "runner": {}, "artifacts": [],
                     "started_at": "2026-01-01T00:00:00Z", "finished_at": "2026-01-01T00:01:00Z",
                     "obligations": [{"id": "T1", "required_gate": "hosted", "relevant_paths": []}], "exit_code": 0}
        manifest["hosted"] = {**projection["hosted"], "clean": True}
        policy = base64.b64encode(json.dumps({"obligations": {"T1": {"workflow": ".github/workflows/test.yml",
                                                                     "check": "required-job"}}}).encode()).decode()

        def fake_api(*args):
            endpoint = args[-1]
            if endpoint.endswith("/actions/runs/123"):
                return self.fake_run()
            if endpoint.endswith("/branches/main"):
                return {"commit": {"sha": self.git("rev-parse", "HEAD")}}
            if "/contents/" in endpoint:
                return {"content": policy}
            if endpoint.endswith("required_status_checks"):
                return {"checks": [{"context": "required-job", "app_id": 15368}]}
            if "/check-runs/" in endpoint:
                return {"id": 456, "name": "required-job", "head_sha": self.git("rev-parse", "HEAD"),
                        "status": "completed", "conclusion": "success", "app": {"id": 15368}}
            if "/jobs?" in endpoint:
                self.assertIn("--paginate", args)
                return [{"jobs": []}, {"jobs": [{"name": "required-job", "run_id": 123,
                         "head_sha": self.git("rev-parse", "HEAD"), "status": "completed", "conclusion": "success",
                         "check_run_url": "https://api.github.com/repos/example/repo/check-runs/456"}]}]
            raise AssertionError(endpoint)

        with patch("workflow_evidence.gh", side_effect=fake_api):
            self.assertEqual(verify_manifest(manifest, self.repo, self.repo)["obligations"][0]["gate"], "pending")
            verified = verify_manifest(manifest, self.repo, self.repo, base_branch="main")
            self.assertEqual(verified["obligations"][0]["gate"], "satisfied")
        with patch("workflow_evidence.gh", side_effect=lambda *args: ([{"jobs": [{"name": "unrelated", "run_id": 123,
                        "status": "completed", "conclusion": "success"}]}] if "/jobs?" in args[-1] else fake_api(*args))):
            self.assertEqual(verify_manifest(manifest, self.repo, self.repo, base_branch="main")["obligations"][0]["gate"], "pending")
        with patch("workflow_evidence.gh", side_effect=lambda *args: (
                {**fake_api(*args), "app": {"id": 99}} if "/check-runs/" in args[-1] else fake_api(*args))):
            self.assertEqual(verify_manifest(manifest, self.repo, self.repo, base_branch="main")["obligations"][0]["gate"], "pending")
        with patch("workflow_evidence.gh", side_effect=fake_api):
            self.assertEqual(verify_manifest(projection, self.repo, self.repo, projection=True,
                             base_branch="main", required_obligations=["T1"])["obligations"][0]["gate"], "satisfied")
            self.assertEqual(verify_manifest(projection, self.repo, self.repo, projection=True)["obligations"], [])
            self.assertEqual(verify_manifest(projection, self.repo, self.repo, projection=True,
                             base_branch="main", required_obligations=["other"])["obligations"][0]["gate"], "pending")
        # Ruleset-only requirements cannot be established by the branch-protection adapter.
        with patch("workflow_evidence.gh", side_effect=lambda *args: (
                (_ for _ in ()).throw(ValueError("no branch protection")) if args[-1].endswith("required_status_checks")
                else fake_api(*args))):
            self.assertEqual(verify_manifest(manifest, self.repo, self.repo,
                             base_branch="main")["obligations"][0]["gate"], "pending")

    def test_hosted_repository_must_match_candidate(self):
        projection = self.hosted_projection()
        projection["repository"] = "elsewhere/repo"
        projection["hosted"] = {"url": "https://github.com/elsewhere/repo/actions/runs/123", "run_id": "123"}
        with patch("workflow_evidence.gh", return_value=self.fake_run()):
            result = verify_manifest(projection, self.repo, self.repo, projection=True)
        self.assertEqual(result["state"], "stale")

    def test_hosted_other_sha_stale_for_hosted_gate(self):
        manifest = {**self.hosted_projection(), "schema": "my-ai-skills.test-evidence/v1", "command": {}, "runner": {},
                    "started_at": "2026-01-01T00:00:00Z", "finished_at": "2026-01-01T00:01:00Z",
                    "artifacts": [], "obligations": [{"id": "T1", "required_gate": "hosted"}], "exit_code": 0}
        manifest["hosted"]["clean"] = True
        manifest["code"]["head"] = "0" * 40
        self.assertEqual(verify_manifest(manifest, self.repo, self.repo)["state"], "stale")

    def test_publish_omits_private_fields_and_updates_comment(self):
        from workflow_evidence import publish, save_manifest, parse_comment
        evidence_id, manifest = self.record("--selection", "private-selection", "--tool", "node=20")
        manifest["extensions"]["private"] = "private-string"
        save_manifest(record_dir(self.repo, evidence_id), manifest)
        state = []

        def fake_api(*args):
            if "--paginate" in args:
                return [state.copy()]
            body = next(a[5:] for a in args if a.startswith("body="))
            if "PATCH" in args:
                state[0]["body"] = body
            else:
                state.append({"id": 1, "body": body})
            return {}

        with patch("workflow_evidence.gh", side_effect=fake_api):
            for _ in range(2):
                publish(self.repo, evidence_id, "https://github.com/example/repo/issues/12")
            projection = from_github("https://github.com/example/repo/issues/12", evidence_id)
        self.assertEqual(len(state), 1)
        self.assertEqual(parse_comment(state[0]["body"]), projection)
        for secret in ("private-selection", "private-string", "node", "fingerprint", "runner", "obligations"):
            self.assertNotIn(secret, state[0]["body"])

    def test_unknown_extension_and_invalid_public_fields(self):
        evidence_id, manifest = self.record()
        manifest["anything"] = {"secret": "private"}
        self.assertNotIn("private", json.dumps(public_projection(manifest)))
        manifest["repository"] = "bad/repo/extra"
        with self.assertRaises(ValueError):
            public_projection(manifest)


if __name__ == "__main__":
    unittest.main()
