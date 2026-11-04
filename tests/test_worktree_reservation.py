import fcntl
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/worktree-reservation"
sys.path.insert(0, str(ROOT / "scripts"))
import worktree_registry as wr


class ReservationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.primary = self.root / "repo"
        self.path = self.root / "issue"
        self.issue = "https://github.com/owner/repo/issues/35"
        self.git("init", "-q", str(self.primary), cwd=self.root)
        self.git("config", "user.name", "Tester", cwd=self.primary)
        self.git("config", "user.email", "test@example.com", cwd=self.primary)
        self.git("remote", "add", "origin", "https://github.com/owner/repo.git", cwd=self.primary)
        (self.primary / "file.txt").write_text("first")
        self.git("add", "file.txt", cwd=self.primary)
        self.git("commit", "-qm", "first", cwd=self.primary)
        self.git("worktree", "add", "-qb", "issue-35", str(self.path), cwd=self.primary)

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.path, check=True, capture_output=True).stdout.decode().strip()

    def cli(self, command, *args, path=None, session="writer", run="run-1", code=0):
        argv = [str(CLI), command, "--path", str(path or self.path), "--json"]
        if session is not None:
            argv += ["--session", session]
        if run is not None:
            argv += ["--run", run]
        argv += args
        result = subprocess.run(argv, capture_output=True, text=True)
        self.assertEqual(result.returncode, code, f"{argv}\n{result.stdout}\n{result.stderr}")
        return json.loads(result.stdout) if result.stdout.startswith("{") else result

    @property
    def registry(self):
        return Path(wr.identity(self.path)["common_dir"]) / "ai-workflow/worktrees.json"

    def data(self):
        return json.loads(self.registry.read_text())["entries"][0]

    def planned(self):
        # Turn existing checkout into a reviewed recovered entry in the standard fixture.
        inventory = self.cli("reconcile", session=None, run=None)["inventory"]["digest"]
        self.cli("reconcile", "--takeover", "--expected-owner", "unknown", "--stopped-evidence", "worker-ended:fixture",
                 "--inventory-digest", inventory)
        entry = self.data()
        entry["issue_url"] = self.issue
        reg = json.loads(self.registry.read_text())
        reg["entries"][0] = entry
        self.registry.write_text(json.dumps(reg))

    def reserve(self, *args, session="writer", code=0):
        return self.cli("reserve", "--issue", self.issue, "--branch", "issue-35", *args, session=session, code=code)

    def owned(self):
        self.planned()
        self.cli("verify")

    def pyc(self, name, *, content=None):
        file = self.path / "scripts/__pycache__" / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(content if content is not None else importlib.util.MAGIC_NUMBER + b"\0" * 20)
        return file

    def test_concurrent_reserve_grants_single_owner(self):
        target = self.root / "planned"
        base = [str(CLI), "reserve", "--path", str(target), "--repository", str(self.primary),
                "--planned", "--issue", self.issue, "--branch", "feature", "--run", "run-1", "--json"]
        workers = [subprocess.Popen([*base, "--session", f"worker-{i}"], stdout=subprocess.PIPE) for i in range(5)]
        outputs = [p.communicate()[0] for p in workers]
        self.assertEqual([p.returncode for p in workers].count(0), 1)
        self.assertEqual([p.returncode for p in workers].count(3), 4)
        for raw in outputs:
            self.assertTrue(set(("ok", "exit_code", "error", "path", "issue_url", "branch", "state", "owner",
                                 "head", "digest", "drift", "generated_paths", "unknown_untracked_paths", "last_verified_at")) <= set(json.loads(raw)))

    def test_planned_reservation_then_activate_and_single_path_per_issue(self):
        target = self.root / "planned"
        self.cli("reserve", "--planned", "--repository", str(self.primary), "--issue", self.issue,
                 "--branch", "planned", path=target)
        self.assertIsNone(json.loads(self.registry.read_text())["entries"][0]["baseline"])
        self.git("worktree", "add", "-qb", "planned", str(target), cwd=self.primary)
        self.cli("reserve", "--issue", self.issue, "--branch", "planned", path=target)
        self.cli("reserve", "--issue", self.issue, "--branch", "planned", path=target)
        self.cli("reserve", "--planned", "--repository", str(self.primary), "--issue", self.issue,
                 "--branch", "other", path=self.root / "other", code=3)

    def test_planned_idempotency_requires_same_issue_and_branch(self):
        target = self.root / "planned"
        opts = ("--planned", "--repository", str(self.primary))
        self.cli("reserve", *opts, "--issue", self.issue, "--branch", "feature", path=target)
        self.cli("reserve", *opts, "--issue", self.issue, "--branch", "feature", path=target)
        for issue, branch in ((self.issue + "-other", "feature"), (self.issue, "other")):
            self.cli("reserve", *opts, "--issue", issue, "--branch", branch, path=target, code=3)
            self.assertEqual((self.data()["issue_url"], self.data()["branch"]), (self.issue, "feature"))

    def test_planned_checkout_cannot_be_used_before_activation(self):
        target = self.root / "planned"
        self.cli("reserve", "--planned", "--repository", str(self.primary), "--issue", self.issue,
                 "--branch", "feature", path=target)
        self.git("worktree", "add", "-qb", "feature", str(target), cwd=self.primary)
        for command, args, session in (
            ("verify", (), "writer"),
            ("handoff", ("--from-session", "writer", "--to-session", "next"), None),
            ("release", ("--state", "WAITING"), "writer"),
            ("track-generated", ("--", sys.executable, "-c", "print('should not run')"), "writer"),
        ):
            self.cli(command, *args, path=target, session=session, code=3)
            self.assertEqual(self.data()["state"], "RESERVED")
        self.cli("reserve", "--issue", self.issue, "--branch", "feature", path=target)
        self.cli("verify", path=target)

    def test_cancel_planned_requires_same_owner_absent_destination_and_reason(self):
        target = self.root / "not-created"
        opts = ("--repository", str(self.primary))
        self.cli("reserve", "--planned", *opts, "--issue", self.issue, "--branch", "feature", path=target)
        failed_add = subprocess.run(["git", "worktree", "add", "-b", "feature", str(target),
                                     "nonexistent-commit"], cwd=self.primary, capture_output=True)
        self.assertNotEqual(failed_add.returncode, 0)
        self.assertFalse(target.exists())
        self.cli("cancel-planned", *opts, "--reason", "add failed", path=target, session="other", code=3)
        self.cli("cancel-planned", "--reason", "add failed", path=target, code=2)
        target.mkdir()
        self.cli("cancel-planned", *opts, "--reason", "add failed", path=target, code=6)
        target.rmdir()
        self.cli("cancel-planned", *opts, "--reason", "add failed", path=target)
        self.assertEqual(json.loads(self.registry.read_text())["entries"][0]["state"], "REMOVED")

    def test_corrupt_registry_refuses_mutation(self):
        self.registry.parent.mkdir(exist_ok=True)
        self.registry.write_text("{" )
        self.reserve(code=7)
        self.assertEqual(self.registry.read_text(), "{")
        self.registry.write_text('{"schema_version": 99, "entries": []}')
        self.reserve(code=7)
        self.assertEqual(json.loads(self.registry.read_text())["schema_version"], 99)

    def test_lock_timeout_leaves_registry_unchanged(self):
        self.planned()
        prior = self.registry.read_bytes()
        with (self.registry.parent / "worktrees.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            self.cli("verify", "--lock-timeout", "0", code=5)
        self.assertEqual(self.registry.read_bytes(), prior)

    def test_verify_samples_code_after_acquiring_lock(self):
        self.owned()
        with (self.registry.parent / "worktrees.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            worker = subprocess.Popen([str(CLI), "verify", "--path", str(self.path),
                                       "--session", "writer", "--json", "--lock-timeout", "3"],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            time.sleep(.25)
            (self.path / "file.txt").write_text("changed during lock wait")
        output, error = worker.communicate(timeout=5)
        self.assertEqual(worker.returncode, 4, (output, error))
        self.assertIn("file.txt", json.loads(output)["drift"]["changed_paths"])

    def test_identity_mismatch_primary_refusal_and_safe_ids(self):
        self.cli("reserve", "--issue", self.issue, "--branch", self.git("branch", "--show-current", cwd=self.primary),
                 path=self.primary, code=6)
        self.reserve(session="bad space", code=2)
        self.planned()
        self.git("switch", "-qc", "other")
        self.cli("verify", code=6)
        self.git("switch", "issue-35")
        self.git("remote", "set-url", "origin", "https://github.com/other/repo.git")
        self.cli("verify", code=6)

    def test_own_checkpoint_is_not_drift(self):
        self.owned()
        (self.path / "file.txt").write_text("own work")
        self.cli("checkpoint")
        self.assertTrue(self.cli("verify")["ok"])

    def test_detected_drift_cannot_be_checkpointed(self):
        self.owned()
        (self.path / "file.txt").write_text("external")
        self.cli("verify", code=4)
        self.cli("checkpoint", code=4)
        self.assertIsNotNone(self.data()["drift"])
        self.cli("reconcile", "--accept-external", "--reason", "operator reviewed")
        self.cli("verify")

    def test_external_commit_blocks_until_accept_external(self):
        self.owned()
        (self.path / "file.txt").write_text("committed")
        self.git("commit", "-qam", "external")
        result = self.cli("verify", code=4)
        self.assertEqual(len(result["drift"]["commits"]), 1)
        self.assertIn("file.txt", result["drift"]["committed_paths"])
        self.cli("checkpoint", code=4)
        self.cli("reconcile", "--accept-external", "--reason", "reviewed commit")
        self.cli("verify")

    def test_release_requires_checkpoint_after_owner_write(self):
        self.owned()
        (self.path / "file.txt").write_text("own")
        self.cli("release", "--state", "WAITING", code=4)
        self.cli("checkpoint", code=4)

    def test_reserve_after_release_detects_external_change(self):
        self.owned()
        (self.path / "file.txt").write_text("own")
        self.cli("checkpoint")
        self.cli("release", "--state", "WAITING")
        (self.path / "file.txt").write_text("external")
        self.git("commit", "-qam", "external")
        (self.path / "file.txt").write_text("external uncommitted")
        self.reserve(session="next", code=4)
        self.assertIsNone(self.data()["owner"])
        self.assertIn("file.txt", self.data()["drift"]["changed_paths"])
        result = self.reserve("--accept-external", "--reason", "reviewed", session="next")
        self.assertEqual(result["owner"]["session"], "next")
        self.assertIn("accept_external", [e["event"] for e in self.data()["history"]])

    def test_cleanup_eligible_cannot_be_reacquired_by_reserve(self):
        self.owned()
        self.cli("release", "--state", "CLEANUP_ELIGIBLE")
        for args in ((), ("--accept-external", "--reason", "reviewed")):
            result = self.reserve(*args, session="next", code=3)
            self.assertEqual(result["state"], "CLEANUP_ELIGIBLE")
            self.assertIsNone(result["owner"])
        self.assertEqual(self.data()["state"], "CLEANUP_ELIGIBLE")

    def test_handoff_planning_to_apply_keeps_checkout_and_revokes_previous(self):
        self.owned()
        (self.path / "file.txt").write_text("partial")
        self.cli("checkpoint")
        self.cli("handoff", "--from-session", "writer", "--to-session", "apply", "--run", "run-1", session=None)
        self.cli("verify", code=3)
        self.cli("verify", session="apply")
        self.assertEqual((self.path / "file.txt").read_text(), "partial")

    def test_reconcile_recovery_required_blocks_active_worker(self):
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"])
        self.addCleanup(lambda: (child.terminate(), child.wait()))
        self.owned()
        (self.path / "file.txt").write_text("partial")
        self.registry.unlink()  # lost registry, while the worker is still active
        inventory = self.cli("reconcile", session=None, run=None)
        self.assertEqual(inventory["state"], "RECOVERY_REQUIRED")
        self.assertEqual(inventory["owner"], None)
        self.reserve(code=3)
        self.reserve("--accept-external", "--reason", "not enough", code=3)
        self.assertEqual((self.path / "file.txt").read_text(), "partial")

    def test_takeover_requires_expected_owner_evidence_and_inventory_digest(self):
        result = self.cli("reconcile", session=None, run=None)
        digest = result["inventory"]["digest"]
        self.cli("reconcile", "--takeover", "--expected-owner", "wrong", "--stopped-evidence", "operator-note",
                 "--inventory-digest", digest, code=3)
        self.cli("reconcile", "--takeover", "--expected-owner", "unknown", "--stopped-evidence", "operator-note",
                 "--inventory-digest", "stale", code=3)
        self.cli("reconcile", "--takeover", "--expected-owner", "unknown", "--stopped-evidence", "operator-note",
                 "--inventory-digest", digest)

    def test_takeover_refused_when_owner_pid_alive(self):
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"])
        self.addCleanup(lambda: (child.terminate(), child.wait()))
        target = self.root / "planned"
        self.cli("reserve", "--planned", "--repository", str(self.primary), "--issue", self.issue,
                 "--branch", "planned", "--owner-pid", str(child.pid), path=target)
        self.git("worktree", "add", "-qb", "planned", str(target), cwd=self.primary)
        self.cli("reserve", "--issue", self.issue, "--branch", "planned", path=target)
        self.path = target
        digest = self.cli("status", session=None, run=None)["inventory"]["digest"]
        self.cli("reconcile", "--takeover", "--expected-owner", "writer", "--stopped-evidence", "claimed-ended",
                 "--inventory-digest", digest, code=3)

    def test_incomplete_entry_requires_recovery(self):
        self.planned()
        reg = json.loads(self.registry.read_text())
        del reg["entries"][0]["verified_for"]
        self.registry.write_text(json.dumps(reg))
        self.reserve(code=3)
        recovered = self.cli("reconcile", session=None, run=None)
        self.assertEqual(recovered["state"], "RECOVERY_REQUIRED")
        self.assertEqual(self.data()["recovery"]["expected_owner"], "writer")
        self.assertIsNone(self.data()["owner"])
        self.reserve(code=3)

    def test_incomplete_baseline_is_recovered_without_discarding_diff(self):
        self.planned()
        (self.path / "file.txt").write_text("partial")
        reg = json.loads(self.registry.read_text())
        del reg["entries"][0]["baseline"]["digest"]
        self.registry.write_text(json.dumps(reg))
        self.reserve(code=3)
        result = self.cli("reconcile", session=None, run=None)
        self.assertEqual(result["state"], "RECOVERY_REQUIRED")
        self.assertEqual((self.path / "file.txt").read_text(), "partial")

    def test_mark_removed_needs_git_inventory_absence(self):
        self.owned()
        self.cli("release", "--state", "CLEANUP_ELIGIBLE")
        self.cli("mark-removed", "--repository", str(self.primary), session=None, run=None, code=3)
        self.git("worktree", "remove", str(self.path), cwd=self.primary)
        result = self.cli("mark-removed", "--repository", str(self.primary), session=None, run=None)
        self.assertEqual(result["state"], "REMOVED")

    def test_generated_files_do_not_cause_drift(self):
        self.owned()
        self.pyc("manual.pyc")
        result = self.cli("verify")
        self.assertIn("scripts/__pycache__/manual.pyc", result["generated_paths"])
        self.assertIsNone(result["drift"])

    def test_ignored_pycache_is_safe_but_ignored_venv_is_not(self):
        (self.path / ".gitignore").write_text("__pycache__/\n.venv/\n*.pyc\n")
        self.pyc("safe.pyc")
        private = self.path / ".venv/lib/__pycache__/private.pyc"
        private.parent.mkdir(parents=True)
        private.write_bytes(importlib.util.MAGIC_NUMBER + b"0" * 20)
        self.assertIn("scripts/__pycache__/safe.pyc", wr._bytecodes(self.path))
        self.assertNotIn(str(private.relative_to(self.path)), wr._bytecodes(self.path))

    def test_unknown_in_ignored_pycache_is_fingerprinted_and_reported(self):
        (self.path / ".gitignore").write_text("__pycache__/\n.venv/\n*.pyc\n")
        self.git("add", ".gitignore")
        self.git("commit", "-qm", "ignore caches")
        self.owned()
        baseline = wr.code_state(self.path)
        self.pyc("generated.pyc")
        private = self.path / ".venv/lib/private.txt"
        private.parent.mkdir(parents=True)
        private.write_text("not part of checkout fingerprint")
        self.assertEqual(wr.code_state(self.path).digest, baseline.digest)
        unknown = self.path / "scripts/__pycache__/nested/notes.txt"
        unknown.parent.mkdir(parents=True)
        unknown.write_text("user work")
        state = wr.code_state(self.path)
        self.assertNotEqual(state.digest, baseline.digest)
        self.assertIn("scripts/__pycache__/nested/notes.txt", [e.path for e in state.entries])
        self.assertNotIn(".venv/lib/private.txt", [e.path for e in state.entries])
        status = self.cli("status", session=None, run=None)
        self.assertIn("scripts/__pycache__/nested/notes.txt", status["unknown_untracked_paths"])
        self.assertIn("scripts/__pycache__/generated.pyc", status["generated_paths"])
        self.assertIn("scripts/__pycache__/nested/notes.txt", self.cli("verify", code=4)["drift"]["changed_paths"])
        self.assertEqual(unknown.read_text(), "user work")
        (self.path / "scripts/__pycache__/linked").symlink_to(private.parent, target_is_directory=True)
        linked = wr.code_state(self.path)
        self.assertIn("scripts/__pycache__/linked", [e.path for e in linked.entries])
        self.assertNotIn("scripts/__pycache__/linked/private.txt", [e.path for e in linked.entries])

    def test_non_utf8_git_filename_survives_fingerprint_registry_and_json(self):
        raw_name = b"invalid-\xff.txt"
        name = os.fsdecode(raw_name)
        file = self.path / name
        file.write_text("user work")
        initial = wr.code_state(self.path)
        self.assertIn(name, [item.path for item in initial.entries])
        self.assertEqual(wr._canonical({"name": "caf\u00e9"}), b'{"name":"caf\xc3\xa9"}')
        self.planned()
        self.assertEqual(self.cli("status", session=None, run=None)["unknown_untracked_paths"], [name])
        self.assertIn(name, [item["path"] for item in self.data()["baseline"]["entries"]])
        self.cli("verify")
        file.write_text("changed")
        self.assertIn(name, self.cli("verify", code=4)["drift"]["changed_paths"])

    def test_clean_requires_owner_and_post_checkpoint_verify(self):
        self.owned()
        script = "from pathlib import Path; import importlib.util; Path('x.pyc').write_bytes(importlib.util.MAGIC_NUMBER+b'0'*20)"
        self.cli("track-generated", "--", sys.executable, "-c", script)
        self.cli("clean-generated", "--apply", "--paths", "x.pyc", "--reason", "test", code=3)
        self.cli("verify")
        self.cli("clean-generated", "--apply", "--paths", "x.pyc", "--reason", "test", session="other", code=3)
        self.assertTrue((self.path / "x.pyc").exists())

    def test_clean_apply_rechecks_verify_and_drift_under_lock(self):
        self.owned()
        script = "from pathlib import Path; import importlib.util; Path('x.pyc').write_bytes(importlib.util.MAGIC_NUMBER+b'0'*20)"
        self.cli("track-generated", "--", sys.executable, "-c", script)
        self.cli("verify")
        (self.path / "file.txt").write_text("external")
        self.cli("clean-generated", "--apply", "--paths", "x.pyc", "--reason", "test", code=4)
        self.assertTrue((self.path / "x.pyc").exists())

    def test_clean_generated_requires_provenance_selection_and_reason(self):
        self.owned()
        self.pyc("manual.pyc")
        self.pyc("fake.pyc", content=b"fake")
        (self.path / ".gitignore").write_text(".venv/\n__pycache__/\n*.pyc\n")
        ignored = self.path / ".venv/lib/__pycache__/protected.pyc"
        ignored.parent.mkdir(parents=True)
        ignored.write_bytes(importlib.util.MAGIC_NUMBER + b"0" * 20)
        (self.path / "other.txt").write_text("user")
        self.cli("clean-generated", "--apply", "--paths", "scripts/__pycache__/manual.pyc", code=2)
        result = self.cli("clean-generated")
        self.assertTrue(any(not item["eligible"] for item in result["candidates"]))
        self.assertTrue((self.path / "other.txt").exists())
        self.assertTrue(ignored.exists())

    def test_clean_refuses_symlink(self):
        self.owned()
        script = "from pathlib import Path; import importlib.util; Path('x.pyc').write_bytes(importlib.util.MAGIC_NUMBER+b'0'*20)"
        self.cli("track-generated", "--", sys.executable, "-c", script)
        self.cli("verify")
        original = self.path / "x.pyc"
        original.rename(self.path / "keep.pyc")
        original.symlink_to("keep.pyc")
        self.cli("clean-generated", "--apply", "--paths", "x.pyc", "--reason", "test", code=3)
        self.assertTrue(original.is_symlink())

    def test_track_generated_capacity_fails_without_partial_records(self):
        self.owned()
        script = ("from pathlib import Path; import importlib.util; "
                  "[Path(f'{i}.pyc').write_bytes(importlib.util.MAGIC_NUMBER+b'0'*20) for i in range(257)]")
        self.cli("track-generated", "--", sys.executable, "-c", script, code=3)
        self.assertEqual(self.data()["generated_provenance"], [])

    def test_track_generated_pending_child_records_nothing(self):
        self.owned()
        script = ("import subprocess, sys; subprocess.Popen([sys.executable, '-c', "
                  "'import time; time.sleep(2)'])")
        self.cli("track-generated", "--", sys.executable, "-c", script, code=3)
        self.assertEqual(self.data()["generated_provenance"], [])

    def test_code_state_entries_digest_and_options(self):
        start = wr.code_state(self.path)
        (self.path / "file.txt").write_text("changed")
        (self.path / "other.txt").write_text("new")
        state = wr.code_state(self.path)
        self.assertEqual([e.path for e in state.entries], ["file.txt", "other.txt"])
        self.assertTrue(state.digest.startswith("sha256:v1:"))
        self.assertNotEqual(start.digest, state.digest)
        self.assertNotEqual(state.digest, wr.code_state(self.path, exclude_paths=("other.txt",)).digest)
        self.pyc("generated.pyc")
        self.assertEqual(state.digest, wr.code_state(self.path).digest)
        self.assertIn("scripts/__pycache__/generated.pyc", wr.code_state(self.path).generated)
        (self.path / ".gitignore").write_text("env.php\n")
        (self.path / "env.php").write_text("secret")
        ignored = wr.code_state(self.path, include_ignored=("env.php",))
        self.assertIn("env.php", [e.path for e in ignored.entries])

    def test_index_blob_and_mode_change_with_same_xy_and_worktree_changes_digest(self):
        file = self.path / "file.txt"
        file.write_text("stage-one")
        self.git("add", "file.txt")
        file.write_text("working")
        first = wr.code_state(self.path)
        self.git("update-index", "--chmod=+x", "file.txt")
        second = wr.code_state(self.path)
        self.assertEqual(first.entries[0].status, second.entries[0].status)
        self.assertEqual(first.entries[0].sha256, second.entries[0].sha256)
        self.assertNotEqual(first.digest, second.digest)
        self.assertIn("file.txt", wr.drift_report(first, second, checkout=self.path)["changed_paths"])
        file.write_text("stage-two")
        self.git("add", "file.txt")
        file.write_text("working")
        third = wr.code_state(self.path)
        self.assertEqual(second.entries[0].status, third.entries[0].status)
        self.assertNotEqual(second.digest, third.digest)

    def test_git_inspection_uses_no_optional_locks(self):
        original = wr.subprocess.run
        seen = []
        def capture(argv, **kwargs):
            if argv[0] == "git":
                seen.append((argv, kwargs.get("env")))
            return original(argv, **kwargs)
        with patch.object(wr.subprocess, "run", side_effect=capture):
            wr.identity(self.path)
            wr.code_state(self.path)
            wr.drift_report(wr.code_state(self.path), wr.code_state(self.path), checkout=self.path)
        self.assertTrue(seen)
        self.assertTrue(all("--no-optional-locks" in argv and env["GIT_OPTIONAL_LOCKS"] == "0" for argv, env in seen))

    def test_track_generated_only_new_owned_command_output(self):
        (self.path / ".gitignore").write_text("__pycache__/\n*.pyc\n")
        self.git("add", ".gitignore")
        self.git("commit", "-qm", "ignore bytecode")
        self.owned()
        self.pyc("manual.pyc")
        script = "from pathlib import Path; import importlib.util; Path('scripts/__pycache__/new.pyc').write_bytes(importlib.util.MAGIC_NUMBER+b'0'*20); Path('file.txt').write_text('effect')"
        secret = "private-command-argument-12345"
        self.cli("track-generated", "--", sys.executable, "-c", script, secret, session="writer")
        self.assertEqual([e["path"] for e in self.data()["generated_provenance"]], ["scripts/__pycache__/new.pyc"])
        self.assertNotIn("effect", self.registry.read_text())
        self.assertNotIn(secret, self.registry.read_text())
        self.assertEqual(self.data()["baseline"]["entries"][0]["sha256"], hashlib.sha256(b"effect").hexdigest())
        self.cli("verify")
        self.cli("clean-generated", "--apply", "--paths", "scripts/__pycache__/manual.pyc", "--reason", "test", code=3)
        self.cli("clean-generated", "--apply", "--paths", "scripts/__pycache__/new.pyc", "--reason", "test")
        self.assertTrue((self.path / "scripts/__pycache__/manual.pyc").exists())

    def test_track_generated_failure_or_pending_children_records_nothing(self):
        self.owned()
        self.cli("track-generated", "--", sys.executable, "-c", "raise SystemExit(1)", code=3)
        self.assertEqual(self.data()["generated_provenance"], [])

    def test_clean_refuses_changed_content_or_metadata(self):
        self.owned()
        script = "from pathlib import Path; import importlib.util; p=Path('x.pyc'); p.write_bytes(importlib.util.MAGIC_NUMBER+b'0'*20)"
        self.cli("track-generated", "--", sys.executable, "-c", script)
        self.cli("verify")
        (self.path / "x.pyc").write_bytes(importlib.util.MAGIC_NUMBER + b"1" * 20)
        self.cli("clean-generated", "--apply", "--paths", "x.pyc", "--reason", "test", code=3)
        self.assertTrue((self.path / "x.pyc").exists())

    def test_clean_refuses_metadata_change_with_original_bytes(self):
        self.owned()
        script = "from pathlib import Path; import importlib.util; Path('x.pyc').write_bytes(importlib.util.MAGIC_NUMBER+b'0'*20)"
        self.cli("track-generated", "--", sys.executable, "-c", script)
        self.cli("verify")
        file = self.path / "x.pyc"
        file.chmod(0o600)
        self.cli("clean-generated", "--apply", "--paths", "x.pyc", "--reason", "test", code=3)
        self.assertTrue(file.exists())

    def test_helpers_do_not_write_bytecode(self):
        copied = self.root / "helpers"
        shutil.copytree(ROOT / "scripts", copied, ignore=shutil.ignore_patterns("__pycache__"))
        text = (ROOT / "scripts/sync-plugin").read_text()
        import re
        helpers = re.search(r"for helper in ([^;]+); do", text).group(1).split()
        env = os.environ.copy()
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        for name in helpers:
            helper = copied / name
            if helper.read_bytes().startswith(b"#!/usr/bin/env python"):
                subprocess.run([str(helper), "--help"], check=True, capture_output=True, env=env)
        self.assertFalse(list(copied.rglob("__pycache__")))


if __name__ == "__main__":
    unittest.main()
