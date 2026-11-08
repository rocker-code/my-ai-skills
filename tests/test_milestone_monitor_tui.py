"""M3/M6/M9/M11: reducer, régua e render sem terminal real."""
import copy
import tempfile
import threading
import time
import unittest

from milestone_monitor_fixtures import *
from milestone_monitor.tui import UIState, render, ruler, cells, fit, detail_lines, expire_samples
from milestone_monitor.projection import issue_view, model
from milestone_monitor.collector import Background, Collector
from milestone_monitor.store import Store


class TUITests(unittest.TestCase):
    def setUp(self):
        issue = issue_view(ISSUE, snapshots(record(event("stage_started"))), {}, {}, NOW, DEFAULTS, STARTED)
        self.value = {"milestones": [{"repository": REPO, "number": n, "title": "Milestone", "issues": [{**issue, "number": n}],
                                      "totals": {"done": 0, "running": 0, "pending": 1, "blocked": 0}, "percent": 0} for n in (1, 2, 3)], "health": []}
        self.state = UIState()

    def test_independent_accordions_identity_selection_and_saved_preferences(self):
        self.state.action("enter", self.value)
        first = self.state.selected
        self.state.action("j", self.value)
        self.state.action("j", self.value)
        self.state.action("enter", self.value)
        self.assertEqual(len(self.state.expanded), 2)
        self.state.selected = first
        self.state.action("enter", self.value)
        self.assertEqual(len(self.state.expanded), 1)
        self.state.action("a", self.value)
        self.state.selected = ("issue", REPO, 2)
        self.value["milestones"][0]["issues"] = []
        self.state.reconcile(self.value)
        self.assertEqual(self.state.selected, ("issue", REPO, 2))
        saved = UIState(self.state.save())
        self.assertEqual(saved.expanded, self.state.expanded)
        self.assertEqual(saved.selected, self.state.selected)

    def test_filters_keep_total_and_empty_milestone_and_stable_fallback(self):
        self.state.action("a", self.value)
        self.state.action("f", self.value)
        self.assertEqual(len(self.state.rows(self.value)), 3)
        text = "\n".join(line for _, line in render(self.value, self.state, 110, 30))
        self.assertIn("(0/1)", text)
        self.assertIn("Nenhuma issue", text)
        self.state.selected = ("issue", REPO, 123)
        self.state.reconcile(self.value)
        self.assertIsNotNone(self.state.selected)

    def test_ruler_apply_without_explore_unknown_stage_rework_parallel_and_no_approval(self):
        issue = self.value["milestones"][0]["issues"][0]
        line = ruler(issue, 1000)
        self.assertIn("[. Explorar]", line)
        self.assertIn("[> Aplicar]", line)
        self.assertNotIn("[+ Explorar]", line)
        self.assertIn("Aplicar", ruler(issue, 30))
        value = record(event("stage_started", stage="custom"), event("stage_started", 1, worker_id="b", execution={"kind": "worker", "id": "b"}, stage="custom"))
        unknown = issue_view(ISSUE, snapshots(value), {}, {}, NOW, DEFAULTS, STARTED)
        self.assertIn("outra: custom", ruler(unknown, 40))
        self.assertEqual(len(unknown["workers"]), 2)
        self.assertIn("referência não implica aprovação", "\n".join(detail_lines(unknown)))

    def test_narrow_unicode_ascii_controls_and_resize(self):
        self.state.action("a", self.value)
        self.state.detailed = True
        for width, height in [(110, 30), (40, 12), (8, 3), (1, 1)]:
            for ascii_only in (True, False):
                lines = render(self.value, self.state, width, height, ascii_only)
                self.assertLessEqual(len(lines), max(0, height-1))
                self.assertTrue(all(cells(line) <= max(0, width-1) for _, line in lines))
                if ascii_only: self.assertTrue(all(line.isascii() for _, line in lines))
        self.assertEqual(cells("界a\u0301"), 3)
        self.assertEqual(fit("\x1b[31m界a\x00", 2), "界")

    def test_selected_issue_ruler_is_not_below_terminal_viewport(self):
        self.state.action("a", self.value)
        self.state.selected = ("issue", REPO, 3)
        lines = render(self.value, self.state, 40, 12, True)
        self.assertTrue(any("Aplicar" in line for key, line in lines if key == self.state.selected))

    def test_history_changes_only_details_not_totals_and_resets_on_issue_switch(self):
        self.state.action("a", self.value)
        self.state.selected = ("issue", REPO, 1)
        self.value["milestones"][0]["issues"][0]["history_count"] = 3
        self.state.action("]", self.value)
        self.assertEqual(self.state.history, 1)
        self.assertEqual(self.value["milestones"][0]["totals"]["pending"], 1)
        self.state.action("j", self.value)
        self.assertEqual(self.state.history, 0)

    def test_background_coalesces_refresh_bounded_models_and_shutdown_panel_only(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            collector = Collector(store, {**CONFIG, "targets": []})
            background = Background(collector, STARTED, offline=True)
            for i in range(100): background.publish({"i": i})
            self.assertEqual(background.models.qsize(), 1)
            self.assertEqual(background.models.get_nowait(), {"i": 99})
            background.start()
            for _ in range(20): background.request()
            background.close()
            self.assertFalse(background.thread.is_alive())
            self.assertTrue(collector.stop.is_set())
            self.assertEqual(store.bindings(), {})

    def test_expiration_during_slow_collection_without_network_or_mutating_model(self):
        issue = issue_view(ISSUE, snapshots(record(event("stage_started"), event("state_observed", 20, state="running", source="runtime_query"))), {}, {}, NOW, DEFAULTS, STARTED)
        value = copy.deepcopy(self.value)
        value["milestones"][0]["issues"] = [issue]
        value["milestones"][0]["totals"] = {"done": 0, "running": 1, "pending": 0, "blocked": 0}
        expired = expire_samples(value, DEFAULTS, NOW + timedelta(seconds=60))
        self.assertEqual(expired["milestones"][0]["issues"][0]["group"], "pending")
        self.assertEqual(value["milestones"][0]["issues"][0]["group"], "running")

    def test_slow_github_does_not_starve_runtime_or_model_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            blocked, release, sampled = threading.Event(), threading.Event(), threading.Event()
            collector = Collector(store, CONFIG)
            def slow(force, include_runtime):
                blocked.set()
                release.wait(3)
            collector.collect = slow
            collector.collect_runtime = lambda force: sampled.set()
            background = Background(collector, STARTED)
            background.start()
            try:
                self.assertTrue(blocked.wait(1))
                self.assertTrue(sampled.wait(1))
                self.assertIn("milestones", background.models.get(timeout=1))
            finally:
                release.set()
                background.close()
