"""M3/M6/M9/M11: reducer, régua e render sem terminal real."""
import copy
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import curses

from milestone_monitor_fixtures import *
from milestone_monitor.tui import UIState, render, render_frame, stage_tokens, ruler, cells, fit, detail_lines, expire_samples
from milestone_monitor.projection import issue_view, model
from milestone_monitor.collector import Background, Collector
from milestone_monitor.store import Store
from milestone_monitor_visual_fixtures import visual_model, collapsed_model
from milestone_monitor.tui import distribution, duration, init_styles, draw_frame, Span, Line, content_lines, counts_spans


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

    def test_frame_adapter_and_semantic_stage_tokens(self):
        self.state.action("a", self.value)
        frame = render_frame(self.value, self.state, 110, 30)
        self.assertEqual([(line.identity, line.text) for line in frame], render(self.value, self.state, 110, 30))
        tokens, index = stage_tokens(self.value["milestones"][0]["issues"][0])
        self.assertEqual(len(tokens), 13)
        self.assertEqual(tokens[index].role, "current")
        self.assertEqual(tokens[0].role, "muted")

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


class VisualTUITests(unittest.TestCase):
    def test_multidigit_counters_keep_semantic_column_positions(self):
        digits = {"done": 3, "running": 2, "pending": 4, "blocked": 2}
        totals = ({"done": 1, "running": 2, "pending": 3, "blocked": 4},
                  {"done": 123, "running": 45, "pending": 1234, "blocked": 99})
        for compact in (False, True):
            starts = []
            for value in totals:
                x, positions = 0, []
                for span in counts_spans(value, compact, False, digits):
                    if span.role != "text": positions.append(x)
                    x += cells(span.text)
                starts.append(positions)
            self.assertEqual(*starts)

    def test_cards_context_order_identity_and_no_decorative_navigation(self):
        value, state = visual_model(), UIState()
        state.action("a", value)
        keys = [key for key, _ in state.rows(value)]
        lines = content_lines(value, state, 237, 100, False, None)
        milestones = [line for line in lines if line.kind == "milestone"]
        self.assertEqual([line.identity[1:] for line in milestones], [(m["repository"], m["number"]) for m in value["milestones"]])
        self.assertTrue(all(line.identity is None for line in lines if line.kind in {"border", "space"}))
        self.assertTrue(any("╭" in line.text for line in lines))
        state.selected = ("issue", "fixture/loja", 119)
        frame = render_frame(value, state, 110, 30)
        self.assertTrue(any("fixture/loja" in line.text for line in frame if line.kind in {"context", "repository"}))
        self.assertIn(state.selected, keys)
        saved = state.save()
        value["milestones"].reverse()
        state.reconcile(value)
        self.assertEqual(state.save(), saved)

    def test_global_totals_coverage_filters_and_expansion(self):
        value, state = visual_model(), UIState()
        baseline = [line.text for line in render_frame(value, state, 238, 54) if line.kind == "header"]
        for _ in range(5):
            state.action("f", value)
            state.action("a", value)
            rows = [line.text for line in render_frame(value, state, 238, 54) if line.kind == "header"]
            self.assertEqual(rows[3:6], baseline[3:6])
        self.assertTrue(any("4 milestones" in row and "20 issues" in row for row in baseline))
        value["milestones"][0].update(title="sem inventário", issues=[], percent=None, totals=dict.fromkeys(("done", "running", "pending", "blocked"), 0))
        frame = render_frame(value, state, 238, 54)
        self.assertIn("parcial", "\n".join(line.text for line in frame))
        self.assertTrue(any("cobertura parcial" in line.text for line in frame if line.kind == "health"))
        value["health"][0]["fresh"] = False
        value["milestones"][0]["title"] = "vazio conhecido"
        text = "\n".join(line.text for line in render_frame(value, state, 238, 54))
        self.assertIn("cache desatualizado", text)
        self.assertIn("--% vazio (0/0)", text)

    def test_distribution_exact_width_no_mutation_and_no_activity_completion(self):
        totals = {"done": 1, "running": 2, "pending": 1, "blocked": 1}
        for width in (1, 3, 10, 37):
            spans = distribution(totals, width)
            self.assertEqual(sum(cells(s.text) for s in spans), width)
        self.assertEqual([(s.role, cells(s.text)) for s in distribution(totals, 10)], [("done", 2), ("running", 4), ("bar_pending", 2), ("blocked", 2)])
        self.assertEqual(distribution(dict.fromkeys(totals, 0), 20), ())
        value = visual_model(1)
        original = copy.deepcopy(value)
        state = UIState()
        state.action("f", value)
        self.assertIn("20% (1/5)", "\n".join(s for _, s in render(value, state, 238, 54)))
        self.assertEqual(original, value)

    def test_table_columns_stage_roles_and_protocol_not_implicit(self):
        value, state = visual_model(1), UIState()
        state.action("a", value)
        frame = render_frame(value, state, 238, 54)
        issues = [line for line in frame if line.kind == "issue"]
        self.assertEqual(len(issues), 5)
        # Separadores da tabela são spans estruturais, não análise de títulos.
        positions = []
        for line in issues:
            x, dividers = 0, []
            for span in line.spans:
                if span.text == " │ ":
                    dividers.append(x)
                x += cells(span.text)
            positions.append(dividers)
        self.assertTrue(all(p == positions[0] for p in positions))
        self.assertEqual(len(positions[0]), 3)
        current = issues[1]
        self.assertTrue(any(s.role == "pill_current" and "Aplicar" in s.text for s in current.spans))
        self.assertNotIn("[+ Proposta]", current.text)
        self.assertIn("...", current.text)
        self.assertIn("Tempo registrado", "\n".join(line.text for line in frame))
        self.assertEqual(len(stage_tokens(value["milestones"][0]["issues"][0])[0]), 13)

    def test_responsive_boundaries_scroll_unicode_ascii_and_model_preserved(self):
        value, state = visual_model(40), UIState()
        value["milestones"][0]["title"] = "界á"*100
        value["milestones"][0]["issues"][0]["title"] = "界á"*100
        original = copy.deepcopy(value)
        state.action("a", value)
        for width, height in ((238, 54), (180, 30), (179, 30), (120, 30), (110, 30), (80, 24), (40, 12), (8, 3), (1, 1)):
            for ascii_only in (False, True):
                for group in (value["milestones"][0], value["milestones"][-1]):
                    state.selected = ("issue", group["repository"], group["issues"][1]["number"])
                    frame = render_frame(value, state, width, height, ascii_only)
                    self.assertLessEqual(len(frame), height-1)
                    self.assertTrue(all(cells(line.text) <= width-1 for line in frame))
                    if ascii_only:
                        self.assertTrue(all(line.text.isascii() for line in frame))
                    if width >= 40:
                        self.assertTrue(any(line.identity == state.selected and "Aplicar" in line.text for line in frame))
            state.scrolling = True
            state.offset += 12
            render_frame(value, state, width, height)
            state.scrolling = False
        self.assertEqual(value, original)
        for width, expected_rulers in ((179, 5), (180, 0)):
            state = UIState(); state.action("a", visual_model(1))
            frame = render_frame(visual_model(1), state, width, 54)
            self.assertEqual(sum(line.kind == "ruler" for line in frame), expected_rulers)

    def test_registered_time_zero_missing_history_and_parallel(self):
        value, state = visual_model(1), UIState()
        issue = value["milestones"][0]["issues"][0]
        self.assertEqual(duration(issue), "2min")
        issue["summary"]["recorded_work_seconds"] = 0
        self.assertEqual(duration(issue), "0s")
        issue["summary"]["recorded_work_seconds"] = 3661
        self.assertEqual(duration(issue), "1h 01min 1s")
        issue["summary"]["cycle_elapsed_seconds"] = 30
        self.assertEqual(duration(issue), "1h 01min 1s")
        state.action("a", value)
        state.selected = ("issue", issue["repository"], issue["number"])
        before = [line.text for line in render_frame(value, state, 238, 54) if line.kind == "issue"]
        state.history = 1
        historical = copy.deepcopy(issue); historical["summary"]["recorded_work_seconds"] = 50
        after = [line.text for line in render_frame(value, state, 238, 54, detail=historical) if line.kind == "issue"]
        self.assertEqual(before, after)
        self.assertEqual(duration({"summary": None}), "indisponível")

    def test_details_sections_full_data_and_wrapping(self):
        value, state = visual_model(1), UIState()
        issue = value["milestones"][0]["issues"][0]
        issue["url"] += "x"*200
        issue["warnings"] = ["aviso de teste"]
        state.action("a", value); state.detailed = True
        lines = detail_lines(issue)
        self.assertTrue(all(section in lines for section in ("Execução", "Entrega", "Fontes")))
        self.assertIn("calendário=600", "\n".join(lines))
        content = content_lines(value, state, 39, 12, False, None)
        wrapped = "".join(line.text.strip() for line in content if line.kind == "detail")
        self.assertIn(issue["url"], wrapped)
        self.assertIn("referência não implica aprovação", wrapped)

    def test_colors_fallback_and_draw_per_span(self):
        for colors in (8, 256):
            with patch.multiple(curses, has_colors=lambda: True, start_color=lambda: None, use_default_colors=lambda: None,
                                init_pair=lambda *args: None, color_pair=lambda i: i << 8), \
                    patch.object(curses, "COLORS", colors, create=True), patch.object(curses, "COLOR_PAIRS", 256, create=True):
                styles = init_styles()
                self.assertNotEqual(styles["done"], styles["current"])
                self.assertFalse(styles["focus"] & curses.A_REVERSE)
                class Screen:
                    def __init__(self): self.calls = []
                    def bkgd(self, *args): pass
                    def erase(self): pass
                    def addstr(self, *args): self.calls.append(args)
                screen = Screen()
                draw_frame(screen, [Line(None, (Span("界", "done"), Span("x", "current")))], styles)
                self.assertEqual(screen.calls, [(0, 0, "界", styles["done"]), (0, 2, "x", styles["current"])])
        mono = init_styles(True)
        for failing in ("start_color", "use_default_colors", "init_pair"):
            with patch.multiple(curses, has_colors=lambda: True, start_color=lambda: None, use_default_colors=lambda: None,
                                init_pair=lambda *args: None), patch.object(curses, "COLORS", 256, create=True), \
                    patch.object(curses, "COLOR_PAIRS", 256, create=True), patch.object(curses, failing, side_effect=curses.error):
                self.assertEqual(init_styles(), mono)

    def test_collapsed_navigation_frames_complete_cards_and_no_duplicate_context(self):
        value, state = collapsed_model(), UIState()
        original = copy.deepcopy(value)
        # Começa deliberadamente no título: reproduz o offset da captura real.
        state.offset = 1
        for direction in ("j", "k"):
            for _ in range(40):
                frame = render_frame(value, state, 238, 54)
                card = [line for line in frame if line.context and line.kind != "context"]
                self.assertEqual(card[0].kind, "card_top")
                self.assertEqual(card[-1].kind, "card_bottom")
                self.assertFalse(any(line.kind == "context" for line in frame))
                selected = next(line for line in frame if line.kind == "milestone" and line.identity == state.selected)
                block = [line for line in frame if line.context == selected.context]
                self.assertEqual([line.kind for line in block], ["card_top", "milestone", "repository", "card_bottom"])
                self.assertTrue(any("concluídas" in line.text and "executando" in line.text for line in block))
                state.action(direction, value)
        self.assertEqual(value, original)

    def test_context_only_after_both_card_headers_are_hidden(self):
        value, state = visual_model(1), UIState()
        state.action("a", value)
        state.detailed = True
        lines = content_lines(value, state, 109, 30, False, None)
        for kind, expected in (("milestone", False), ("repository", False), ("detail", True)):
            state.offset = next(i for i, line in enumerate(lines) if line.kind == kind)
            state.scrolling = True
            frame = render_frame(value, state, 110, 30)
            self.assertEqual(any(line.kind == "context" for line in frame), expected)

    def test_navigation_skips_orphan_bottom_of_large_previous_card(self):
        value, state = visual_model(2), UIState()
        state.action("enter", value)
        state.detailed = True
        lines = content_lines(value, state, 237, 54, False, None)
        state.offset = next(i for i, line in enumerate(lines) if line.kind == "card_bottom")
        group = value["milestones"][1]
        state.selected = ("milestone", group["repository"], group["number"])
        frame = render_frame(value, state, 238, 54)
        content = [line for line in frame if line.context]
        self.assertEqual(content[0].kind, "card_top")
        self.assertTrue(content[0].context.startswith(group["repository"]))
        self.assertFalse(any(line.kind == "context" for line in frame))

    def test_neutral_zero_pending_bar_and_focus_not_accordion(self):
        value, state = collapsed_model(), UIState()
        state.action("j", value)
        frame = render_frame(value, state, 238, 54)
        selected = next(line for line in frame if line.identity == state.selected)
        self.assertIn("● ▶", selected.text)
        self.assertTrue(any(s.role == "focus" for s in selected.spans))
        zero = next(s for s in selected.spans if "0% (0/5)" in s.text)
        self.assertEqual(zero.role, "muted")
        self.assertTrue(any(s.role == "bar_pending" for s in selected.spans))
        self.assertTrue(all(line.kind != "space" for line in frame if line.context))
        ascii_frame = render_frame(value, state, 238, 54, True)
        self.assertTrue(any("* >" in line.text for line in ascii_frame if line.identity == state.selected))
        styles = init_styles(True)
        self.assertTrue(styles["focus_border"] & curses.A_BOLD)
        self.assertFalse(styles["border"] & curses.A_BOLD)
