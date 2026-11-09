"""Contrato sintético offline; verificação de proveniência remota é opt-in."""
import hashlib
import json
import os
from pathlib import Path
import unittest


FIXTURES = Path(__file__).parent / "fixtures"


class ObserverContractTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((FIXTURES / "opencode-observer-2.2.5.json").read_text())

    def test_provenance_matches_existing_runtime_contract(self):
        previous = json.loads((FIXTURES / "milestone-monitor-opencode-2.2.5.json").read_text())
        for field in ("producer", "schema_sha256"):
            self.assertEqual(self.fixture[field], previous[field])

    def test_envelopes_and_identities(self):
        events = self.fixture["events"]
        self.assertEqual(len({e["id"] for e in events}), len(events))
        for event in events:
            self.assertTrue(event["id"].startswith("evt_"))
            self.assertIs(type(event["created"]), int)  # UTC epoch, milissegundos
            if event["type"].startswith("session.execution."):
                self.assertEqual(event["durable"]["aggregateID"], event["data"]["sessionID"])
                self.assertEqual(event["durable"]["version"], 1)
            else:
                self.assertNotIn("durable", event)
        by_type = {e["type"]: e for e in events}
        self.assertIn("requestID", by_type["permission.replied"]["data"])
        self.assertIn("form", by_type["form.created"]["data"])
        self.assertIn("id", by_type["form.replied"]["data"])
        self.assertNotIn("executionID", json.dumps(events))

    def test_minimal_synthetic_content(self):
        raw = json.dumps(self.fixture)
        for forbidden in ("authorization", "password", "prompt", "reasoning", "tool.input", "transcript"):
            self.assertNotIn(forbidden, raw.lower())
        for query in self.fixture["queries"].values():
            self.assertEqual(query["data"][0]["sessionID"], "ses_fixture")

    @unittest.skipUnless(os.environ.get("OPENCODE_CONTRACT_SOURCE"), "proveniência remota opt-in")
    def test_pinned_producer(self):
        # Diretório temporário contendo somente fontes públicas do commit fixado.
        root = Path(os.environ["OPENCODE_CONTRACT_SOURCE"])
        schema = (root / "packages/protocol/openapi.json").read_bytes()
        self.assertEqual(hashlib.sha256(schema).hexdigest(), self.fixture["schema_sha256"])
        sources = {key: (root / path).read_text() for key, path in self.fixture["definitions"].items()}
        for event in self.fixture["events"]:
            kind = event["type"]
            category = ("execution" if kind.startswith("session.execution.") else
                        "connected" if kind == "server.connected" else
                        "context" if kind == "location.shutdown" else kind.split(".")[0])
            self.assertIn('type: "' + kind + '"', sources[category])
        self.assertIn("created: Schema.Finite", sources["envelope"])
        paths = json.loads(schema)["paths"]
        operations = {op.get("operationId") for path in paths.values() for op in path.values()}
        self.assertTrue(set(self.fixture["queries"]).issubset(operations))
