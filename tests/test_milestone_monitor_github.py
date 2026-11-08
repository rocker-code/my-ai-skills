"""M2/M6/M7/M9: paginação, falhas e vínculos oficiais de fechamento."""
import copy
import json
import subprocess
import tempfile
import unittest
from datetime import timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from milestone_monitor_fixtures import *
from milestone_monitor.common import MonitorError, command
from milestone_monitor.github import GitHub
from milestone_monitor.collector import Collector
from milestone_monitor.projection import model
from milestone_monitor.store import Store


class GitHubTests(unittest.TestCase):
    def test_full_paging_above_500_including_uninstrumented_and_excludes_prs(self):
        def call(argv, timeout):
            endpoint = argv[-1]
            if "/milestones/" in endpoint:
                return {"number": int(endpoint.rsplit("/", 1)[1]), "title": "Vazio"}
            params = parse_qs(urlsplit(endpoint).query)
            page, milestone = int(params["page"][0]), int(params["milestone"][0])
            if milestone == 2:
                return []
            return [{"number": i, "state": "open", "title": "\x1b[31mIssue\x00", "milestone": {"number": 1},
                     "html_url": f"https://github.com/{REPO}/issues/{i}"} for i in range((page-1)*100+1, min(page*100+1, 506))]
        github = GitHub(call)
        values = github.inventory(REPO, [1, 2])
        self.assertEqual(len(values["issues"]), 505)
        self.assertEqual(len(values["milestones"]), 2)
        self.assertEqual(values["issues"][0]["title"], "Issue")
        def prs(argv, timeout):
            if "/milestones/" in argv[-1]: return {"number": 1, "title": "test"}
            return [{"pull_request": {"url": "ignored"}}]
        self.assertEqual(GitHub(prs).inventory(REPO, [1])["issues"], [])

    def test_page_two_failure_preserves_complete_inventory_and_backoff(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            publish(store, "inventory:"+REPO, inventory())
            before = store.source("inventory:"+REPO)["payload"]
            calls = []
            def call(argv, timeout):
                calls.append(argv)
                if "/milestones/" in argv[-1]: return {"number": 1, "title": "test"}
                if "page=2" in argv[-1]: raise MonitorError("rate limit", 120)
                return [{"number": i, "state": "open", "title": "test", "milestone": {"number": 1},
                         "html_url": f"https://github.com/{REPO}/issues/{i}"} for i in range(1, 101)]
            collector = Collector(store, CONFIG, GitHub(call), clock=lambda: NOW)
            operation = lambda: collector.github.inventory(REPO, [1])
            collector.update("inventory:"+REPO, 60, operation, True)
            self.assertEqual(store.source("inventory:"+REPO)["payload"], before)
            self.assertEqual(store.source("inventory:"+REPO)["error"], "rate limit")
            count = len(calls)
            collector.update("inventory:"+REPO, 60, operation, True)
            self.assertEqual(len(calls), count)

    def test_cross_reference_alone_not_delivery_closure_paginated_and_ambiguous(self):
        seen = []
        def call(argv, timeout):
            seen.append(argv)
            if "graphql" not in argv:
                return [{"source": {"issue": {"pull_request": {}, "html_url": f"https://github.com/{REPO}/pull/{n}"}}} for n in (44, 45, 46)]
            n = int(next(a.split("=", 1)[1] for a in argv if a.startswith("number=")))
            second = "cursor=next" in argv
            nodes = [] if n == 44 or not second else [{"number": 7, "repository": {"nameWithOwner": REPO}}]
            return {"data": {"repository": {"pullRequest": {"number": n, "url": f"https://github.com/{REPO}/pull/{n}",
                    "state": "MERGED", "mergedAt": "2026-11-08T12:00:00Z", "mergeCommit": {"oid": "a"*40}, "headRefOid": "b"*40,
                    "closingIssuesReferences": {"nodes": nodes, "pageInfo": {"hasNextPage": n != 44 and not second, "endCursor": "next"}}}}}}
        # A pull_request marker may be an empty object in minimal fixtures.
        values = GitHub(call).pull_requests(REPO, 7)
        self.assertEqual([p["number"] for p in values["candidates"]], [45, 46])
        self.assertTrue(values["ambiguous"])
        self.assertTrue(any("cursor=next" in argv for argv in seen))

    def test_source_health_and_multi_repo_move_reopen_percent_not_merge(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            config = copy.deepcopy(CONFIG)
            config["targets"].append({"repository": "other/repo", "milestones": [1]})
            seed(store)
            publish(store, "inventory:other/repo", {"milestones": [{"repository": "other/repo", "number": 1, "title": "Other"}],
                                                     "issues": [{**ISSUE, "repository": "other/repo", "state": "closed", "url": "https://github.com/other/repo/issues/7"}]})
            publish(store, f"prs:{REPO}:7", {"candidates": [{"number": 1, "state": "MERGED"}], "ambiguous": False})
            value = model(store, config, STARTED, NOW)
            self.assertEqual([g["totals"]["done"] for g in value["milestones"]], [0, 1])
            config["targets"][0]["milestones"] = [1, 2]
            moved = {**ISSUE, "milestone": 2, "state": "closed"}
            groups = [{"repository": REPO, "number": n, "title": str(n)} for n in [1, 2]]
            publish(store, "inventory:"+REPO, inventory([moved], groups))
            self.assertEqual([len(g["issues"]) for g in model(store, config, STARTED, NOW)["milestones"]], [0, 1, 1])
            publish(store, "inventory:"+REPO, inventory([{**moved, "state": "open"}], groups))
            self.assertEqual(model(store, config, STARTED, NOW)["milestones"][1]["percent"], 0)
            self.assertTrue(store.source(f"comments:{REPO}:7")["payload"])

    def test_errors_are_categorized_and_never_store_raw_secrets(self):
        for status, expected in [(401, "não autorizado"), (403, "acesso negado"), (404, "ausente"), (429, "rate limit")]:
            with patch("milestone_monitor.common.subprocess.run", return_value=subprocess.CompletedProcess([], 1, "", f"HTTP {status} secret=PRIVATE\nRetry-After: 99")):
                with self.assertRaises(MonitorError) as raised:
                    command(["gh", "api", "example"])
                self.assertEqual(raised.exception.category, expected)
                self.assertEqual(raised.exception.retry_after, 99)
                self.assertNotIn("PRIVATE", str(raised.exception))
        for failure, expected in [(FileNotFoundError(), "fonte ausente"), (subprocess.TimeoutExpired("gh", 1), "timeout")]:
            with patch("milestone_monitor.common.subprocess.run", side_effect=failure):
                with self.assertRaisesRegex(MonitorError, expected): command(["gh"])
        with patch("milestone_monitor.common.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "{PRIVATE", "")):
            with self.assertRaisesRegex(MonitorError, "resposta inválida"): command(["gh"])

    def test_allowlist_discards_prompts_unknown_metadata_and_controls_before_db(self):
        value = record(event("stage_started", prompt="PRIVATE", metadata={"token": "PRIVATE"}), prompt="PRIVATE")
        cleaned = snapshots(value)
        self.assertNotIn("PRIVATE", json.dumps(cleaned))
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            publish(store, "comments", cleaned)
            self.assertNotIn(b"PRIVATE", store.path.read_bytes())
