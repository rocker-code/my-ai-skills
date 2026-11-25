"""Deterministic negatives are not native Codex execution proof."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

PATH = Path(__file__).with_name("smoke_global_codex.py")
spec = importlib.util.spec_from_file_location("codex_smoke", PATH)
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


class NativeCodexSmokeTests(unittest.TestCase):
    def test_native_profile_uses_explicit_git_metadata_and_reader_parent(self):
        for writable, parent, access in ((True, ":workspace", "write"),
                                         (False, ":read-only", "read")):
            args = smoke.native_permissions(Path("/fixture"), Path("/fixture/worktree with spaces"),
                                            Path("/fixture/repo/.git"),
                                            Path("/fixture/repo/.git/worktrees/wt"), writable)
            config = args[-1]
            self.assertIn(f'extends="{parent}"', config)
            self.assertIn("network={enabled=false}", config)
            for path in ("/fixture/worktree with spaces", "/fixture/repo/.git",
                         "/fixture/repo/.git/worktrees/wt"):
                self.assertIn(f"{json.dumps(path)}={json.dumps(access)}", config)
            self.assertIn('"/fixture/home/.codex/auth.json"="deny"', config)

    def test_source_snapshot_preserves_deleted_indexed_artifacts_and_broken_links(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            def run(argv, cwd):
                return subprocess.check_output(argv, cwd=cwd, text=True)
            run(["git", "init", "-q"], repo)
            path = repo / "planning.md"
            path.write_text("approved artifact\n")
            run(["git", "add", "planning.md"], repo)
            run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.org",
                 "commit", "-qm", "fixture"], repo)
            present = smoke.source_snapshot(repo, run)
            path.unlink()
            missing = smoke.source_snapshot(repo, run)
            self.assertNotEqual(present, missing)
            self.assertEqual(missing, smoke.source_snapshot(repo, run))
            path.symlink_to("absent-target")
            self.assertNotEqual(missing, smoke.source_snapshot(repo, run))
            path.unlink()
            path.write_text("approved artifact\n")
            self.assertEqual(present, smoke.source_snapshot(repo, run))

    def test_interrupted_shell_requires_own_terminal_signal_not_missing_exit(self):
        receipt = {"id": "sh_fixture", "cwd": "/fixture", "status": "exited", "signal": "SIGINT"}
        smoke.require_interrupted_shell(receipt, "sh_fixture", Path("/fixture"))
        smoke.require_interrupted_shell({**receipt, "signal": None, "exit": 130}, "sh_fixture", Path("/fixture"))
        for wrong in ({**receipt, "signal": None}, {**receipt, "status": "running"},
                      {**receipt, "id": "sh_other"}, {**receipt, "cwd": "/other"},
                      {**receipt, "signal": None, "exit": 1}):
            with self.subTest(receipt=wrong):
                with self.assertRaisesRegex(RuntimeError, "BLOCKED"):
                    smoke.require_interrupted_shell(wrong, "sh_fixture", Path("/fixture"))

    def test_native_schema_graph_cannot_hide_unfinished_design(self):
        smoke.require_planning_complete({"artifacts": [{"status": "done"}, {"status": "skipped"}]})
        for status in ({}, {"artifacts": []}, {"artifacts": [{"status": "ready"}]},
                       {"artifacts": [{"status": "done"}, {"status": "blocked"}]}):
            with self.subTest(status=status):
                with self.assertRaisesRegex(RuntimeError, "unfinished schema artifacts"):
                    smoke.require_planning_complete(status)

    def test_native_compact_roots_are_resolved_not_assumed(self):
        text = ("### Skill roots\n- `r7` = `/tmp/project with spaces/.agents/skills`\n"
                "### Available skills\n- openspec-explore: Explore things. "
                "(file: r7/openspec-explore/SKILL.md)\n")
        visible = json.dumps([{"content": [{"text": text}]}])
        self.assertEqual(smoke.discovered_paths(visible)["openspec-explore"],
                         Path("/tmp/project with spaces/.agents/skills/openspec-explore/SKILL.md"))
        with self.assertRaisesRegex(RuntimeError, "root r7"):
            smoke.discovered_paths(json.dumps([{"text": text.replace("- `r7` = ", "- `r8` = ")}]))

    def test_real_shaped_identity_and_terminal_completion_required(self):
        thread = "019ad8a1-0ee1-7b81-a98d-125216541ffd"
        events = [{"type": "thread.started", "thread_id": thread}, {"type": "turn.completed"}]
        self.assertEqual(smoke.completed_thread(events, 0), thread)
        for invalid, code in ((events, 1), (events[:1], 0), (events[1:], 0),
                              (events + [events[0]], 0),
                              ([{"type": "thread.started", "thread_id": "../owner"},
                                {"type": "turn.completed"}], 0),
                              (events + [{"type": "turn.failed"}], 0),
                              (events + [{"type": "error"}], 0)):
            with self.subTest(events=invalid, exit=code):
                with self.assertRaisesRegex(RuntimeError, "BLOCKED"):
                    smoke.completed_thread(invalid, code)

    def test_shared_runtime_policy_has_no_cross_agent_fallback(self):
        policy = (PATH.parents[1] / "protocol/AI_WORKFLOW.md").read_text()
        for phrase in ("without `resume`, `fork`", "thread/session ID",
                       "Reject another worker's callback", "same selected CLI",
                       "never\nlive chat history", "At most one active issue"):
            self.assertIn(phrase, policy)


if __name__ == "__main__":
    unittest.main()
