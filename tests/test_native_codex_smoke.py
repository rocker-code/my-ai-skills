"""Deterministic negatives are not native Codex execution proof."""
import importlib.util
import json
from pathlib import Path
import unittest

PATH = Path(__file__).with_name("smoke_global_codex.py")
spec = importlib.util.spec_from_file_location("codex_smoke", PATH)
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


class NativeCodexSmokeTests(unittest.TestCase):
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
