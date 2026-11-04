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

    def test_failing_command_recorded_and_exit_propagated(self):
        result = self.cli("record", "--obligation", "T1", "--", sys.executable, "-c", "exit(7)")
        self.assertEqual(result.returncode, 7)
        evidence_id = json.loads(result.stderr.splitlines()[0])["evidence_id"]
        manifest = load_manifest(record_dir(self.repo, evidence_id))
        self.assertEqual(manifest["exit_code"], 7)
        self.assertEqual(self.verify(evidence_id)[1]["state"], "verified")
        self.assertEqual(self.verify(evidence_id)[1]["result"], "failed")

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

    def test_record_verified_from_other_worktree(self):
        evidence_id, _ = self.record()
        other = Path(self.temp.name) / "other"
        self.git("worktree", "add", "-q", "-b", "other", str(other))
        result = self.cli("verify", evidence_id, "--format", "json", repo=other)
        self.assertEqual(json.loads(result.stdout)["state"], "verified")

    def test_bundle_import_in_other_clone(self):
        evidence_id, _ = self.record()
        package = Path(self.temp.name) / "bundle.tar.gz"
        export_bundle(self.repo, evidence_id, package)
        clone = Path(self.temp.name) / "clone"
        subprocess.run(["git", "clone", "-q", str(self.repo), str(clone)], check=True)
        self.assertEqual(import_bundle(clone, package), evidence_id)
        self.assertEqual(self.cli("verify", evidence_id, "--format", "json", repo=clone).returncode, 0)

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

    def fake_run(self, head=None, conclusion="success", path=".github/workflows/test.yml"):
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
        manifest["hosted"]["clean"] = True
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
                return {"checks": [{"context": "required-job"}]}
            if endpoint.endswith("/jobs"):
                return {"jobs": [{"name": "required-job", "run_id": 123, "status": "completed", "conclusion": "success"}]}
            raise AssertionError(endpoint)

        with patch("workflow_evidence.gh", side_effect=fake_api):
            self.assertEqual(verify_manifest(manifest, self.repo, self.repo)["obligations"][0]["gate"], "pending")
            verified = verify_manifest(manifest, self.repo, self.repo, base_branch="main")
            self.assertEqual(verified["obligations"][0]["gate"], "satisfied")
        with patch("workflow_evidence.gh", side_effect=lambda *args: ({"jobs": [{"name": "unrelated", "run_id": 123,
                       "status": "completed", "conclusion": "success"}]} if args[-1].endswith("/jobs") else fake_api(*args))):
            self.assertEqual(verify_manifest(manifest, self.repo, self.repo, base_branch="main")["obligations"][0]["gate"], "pending")

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
            if "--slurp" in args:
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
