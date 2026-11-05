"""Simulation fixtures for retry diagnosis (issue #34)."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from attempt_log import MalformedLog, check, parse  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "attempt_log"


def fixture(name):
    return parse((FIXTURES / f"{name}.json").read_text())


def codes(data, final=False):
    return [item["code"] for item in check(data, final=final)["violations"]]


def attempt(seq, signature="A", *, obligation="R1", result="fail", cls="implementation", target="test", change_target="none"):
    return {"kind": "attempt", "seq": seq, "obligation": obligation, "signature": signature,
            "target": target, "class": cls, "hypothesis": f"hypothesis {seq}", "change": f"change {seq}",
            "change_target": change_target, "observed_effect": f"effect {seq}", "result": result,
            "evidence": [f"abcdef{seq}"]}


def passed(signature, via, obligation="R1"):
    return {"kind": "resolution", "group": {"obligation": obligation, "signature": signature},
            "outcome": "passed", "via_seq": via}


def diagnosis(seq, signature="A", *, obligation="R1", cls="implementation", proof=None):
    return {"kind": "diagnosis", "seq": seq, "group": {"obligation": obligation, "signature": signature},
            "class": cls, "checked": {"phase": "runner", "scope": "sandbox", "lifecycle": "started", "consumers": "test"},
            "runtime_proof": ["abcdef9"] if proof is None else proof,
            "simplest_alternative": "repair sandbox", "choice_rationale": "observed runtime cause",
            "next_hypothesis": "new cause"}


class AttemptLogTests(unittest.TestCase):
    def test_progressed_history_final_ready(self):
        data = {"attempt_log": 1, "entries": [attempt(1), attempt(2, "B"), attempt(3, "B", result="pass"), passed("B", 3)]}
        result = check(data, final=True)
        self.assertEqual((True, True, [], None), (result["valid"], result["ready"], result["violations"], result["blocker_state"]))
        self.assertEqual([("progressed", 1), ("resolved", 2)], [(g["status"], g["attempts"]) for g in result["groups"]])
        self.assertEqual([[1], [2, 3]], [g["attempt_seqs"] for g in result["groups"]])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "attempts.json"
            path.write_text(json.dumps(data))
            proc = subprocess.run([str(ROOT / "scripts" / "attempt-log"), "check", str(path), "--final"], capture_output=True, text=True)
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertTrue(json.loads(proc.stdout)["ready"])

    def test_progressed_history_active_failure_not_ready(self):
        data = {"attempt_log": 1, "entries": [attempt(1), attempt(2, "B")]}
        result = check(data, final=True)
        self.assertEqual((False, ["progressed", "open"], ["E_UNRESOLVED"], None),
                         (result["ready"], [g["status"] for g in result["groups"]], [v["code"] for v in result["violations"]], result["blocker_state"]))

    def test_signature_return_starts_new_episode(self):
        entries = [attempt(1), attempt(2), attempt(3, "B"), attempt(4)]
        data = {"attempt_log": 1, "entries": entries}
        self.assertNotIn("E_RETRY_LIMIT", codes(data))
        entries.append(attempt(5))
        self.assertNotIn("E_RETRY_LIMIT", codes(data))
        entries.append(attempt(6))
        self.assertIn("E_RETRY_LIMIT", codes(data))
        result = check(data, final=True)
        self.assertEqual([("progressed", 1, 2), ("progressed", 3, 1), ("open", 4, 3)],
                         [(g["status"], g["first_seq"], g["attempts"]) for g in result["groups"]])

    def test_old_approval_and_blocker_do_not_hide_active_failure(self):
        data = {"attempt_log": 1, "entries": [attempt(1, result="pass"), passed("A", 1), attempt(2)]}
        self.assertIn("E_UNRESOLVED", codes(data, final=True))
        self.assertFalse(check(data, final=True)["ready"])
        data = fixture("blockers")
        data["entries"].insert(-1, attempt(4, "B"))
        result = check(data, final=True)
        self.assertEqual(["progressed", "open"], [g["status"] for g in result["groups"]])
        self.assertIsNone(result["blocker_state"])
        self.assertFalse(result["ready"])

    def test_environment_focus_cleared_by_pass(self):
        data = {"attempt_log": 1, "entries": [attempt(1, cls="environment/bootstrap"), attempt(2, "B", result="pass"), attempt(3, "C", change_target="application")]}
        self.assertNotIn("E_FOCUS", codes(data))

    def test_environment_focus_intermediate_does_not_bypass(self):
        data = {"attempt_log": 1, "entries": [attempt(1, cls="environment/bootstrap"), attempt(2, "B"), attempt(3, "C", change_target="application")]}
        self.assertIn("E_FOCUS", codes(data))
        data["entries"].insert(2, attempt(3, "X", obligation="R2"))
        data["entries"][3]["seq"] = 4
        self.assertIn("E_FOCUS", codes(data))

    def test_other_obligation_pass_and_blocker_do_not_clear_focus(self):
        data = {"attempt_log": 1, "entries": [attempt(1, cls="environment/bootstrap"),
                {"kind": "blocker", "seq": 2, "group": {"obligation": "R1", "signature": "A"},
                 "type": "capacity", "wait_reason": "runtime_capacity", "missing_capability": "runner", "evidence": ["abcdef2"]},
                attempt(3, "other", obligation="R2", result="pass"), attempt(4, "B", change_target="application")]}
        result = check(data)
        self.assertIn("E_FOCUS", [v["code"] for v in result["violations"]])
        self.assertNotIn("E_BLOCKER", [v["code"] for v in result["violations"]])

    def test_environment_reclassification_requires_new_runtime_proof(self):
        first = attempt(1, cls="environment/bootstrap")
        edit = attempt(3, "B", change_target="application")
        data = {"attempt_log": 1, "entries": [first, diagnosis(2), edit]}
        self.assertNotIn("E_FOCUS", codes(data))
        for proof in (["abcdef1"], ["src/config.py#L2"], ["abcdef1", "src/config.py#L2"], "not_applicable: source inspected"):
            with self.subTest(proof=proof):
                data["entries"][1] = diagnosis(2, proof=proof)
                self.assertIn("E_FOCUS", codes(data))
        data["entries"][1] = diagnosis(2)
        data["entries"][1]["checked"].pop("lifecycle")
        self.assertIn("E_FOCUS", codes(data))
        data["entries"][1] = diagnosis(2, cls="environment/bootstrap")
        self.assertIn("E_FOCUS", codes(data))
        data["entries"][1] = diagnosis(2, obligation="R2")
        self.assertIn("E_FOCUS", codes(data))

    def test_environment_reclassification_after_intervening_failure(self):
        data = {"attempt_log": 1, "entries": [attempt(1, cls="environment/bootstrap"), attempt(2, "B"), diagnosis(3), attempt(4, "C", change_target="application")]}
        self.assertNotIn("E_FOCUS", codes(data))
        data["entries"][2]["runtime_proof"] = ["abcdef2"]
        self.assertIn("E_FOCUS", codes(data))

    def test_new_environment_failure_reactivates_focus(self):
        data = {"attempt_log": 1, "entries": [attempt(1, cls="environment/bootstrap"), diagnosis(2), attempt(3, "B", cls="environment/bootstrap"), attempt(4, "C", change_target="application")]}
        self.assertIn("E_FOCUS", codes(data))

    def test_t1_retry_limit_requires_diagnosis(self):
        data = fixture("t1_override_no_effect")
        self.assertIn("E_RETRY_LIMIT", codes(data, final=True))
        data["entries"][2]["result"] = "fail"
        self.assertIn("E_RETRY_LIMIT", codes(data))

    def test_third_pass_still_requires_diagnosis(self):
        self.assertIn("E_RETRY_LIMIT", codes(fixture("t1_override_no_effect")))
        self.assertTrue(check(fixture("t1_diagnosed_alternative"), final=True)["ready"])

    def test_two_failures_are_valid_history_not_next_attempt_approval(self):
        data = fixture("t1_override_no_effect")
        third = data["entries"].pop(2)
        resolution = data["entries"].pop()
        self.assertTrue(check(data)["valid"])
        self.assertIsNone(check(data)["ready"])
        data["entries"].extend((third, resolution))
        self.assertIn("E_RETRY_LIMIT", codes(data))

    def test_t1_diagnosed_alternative_accepted(self):
        self.assertEqual([], codes(fixture("t1_diagnosed_alternative")))

    def test_grouping_ignores_command_and_target(self):
        data = fixture("t1_override_no_effect")
        data["entries"][1]["signature"] = "  VALIDATOR   read country=US "
        self.assertEqual(1, len(check(data)["groups"]))
        data["entries"][1]["signature"] = "validator read country=BR"
        self.assertEqual(3, len(check(data)["groups"]))  # A, B, then a fresh A episode
        self.assertEqual(["progressed", "progressed", "resolved"], [g["status"] for g in check(data)["groups"]])

    def test_pass_resets_failure_streak(self):
        data = fixture("t1_override_no_effect")
        data["entries"][1]["result"] = "pass"
        data["entries"][2]["result"] = "fail"
        self.assertNotIn("E_RETRY_LIMIT", codes(data))

    def test_repeated_hypothesis_rejected(self):
        data = fixture("t1_diagnosed_alternative")
        data["entries"][1]["hypothesis"] = "default override"
        self.assertIn("E_NO_NEW_EVIDENCE", codes(data))

    def test_new_id_same_effect_rejected(self):
        data = fixture("t1_diagnosed_alternative")
        data["entries"][1].update(hypothesis="default override", observed_change="read moved to store scope")
        self.assertIn("E_NO_NEW_EVIDENCE", codes(data))

    def test_repeated_hypothesis_changed_effect_accepted(self):
        data = fixture("t1_diagnosed_alternative")
        data["entries"][1].update(hypothesis="default override", observed_change="validator now reads store scope", observed_effect="US in store scope")
        self.assertEqual([], codes(data))

    def test_observed_change_missing_or_uncited_rejected(self):
        data = fixture("t1_diagnosed_alternative")
        data["entries"][1].update(hypothesis="default override", observed_effect="US in store scope")
        self.assertIn("E_NO_NEW_EVIDENCE", codes(data))
        data["entries"][1]["observed_change"] = "validator now reads store scope"
        data["entries"][1]["evidence"] = ["abcdef1"]
        self.assertIn("E_NO_NEW_EVIDENCE", codes(data))

    def test_t4_environment_focus(self):
        data = fixture("t4_service_before_phpunit")
        self.assertIn("E_FOCUS", codes(data))
        data["entries"][1]["change_target"] = "environment"
        self.assertNotIn("E_FOCUS", codes(data))

    def test_environment_focus_survives_signature_change(self):
        data = fixture("t4_service_before_phpunit")
        first, second = data["entries"][:2]
        second["signature"] = "phpunit assertion failed"
        self.assertEqual(2, len(check(data)["groups"]))
        self.assertIn("E_FOCUS", codes(data))
        diagnosis = {
            "kind": "diagnosis", "seq": first["seq"] + 1,
            "group": {"obligation": first["obligation"], "signature": first["signature"]},
            "class": "implementation",
            "checked": {"phase": "after bootstrap", "scope": "sandbox", "lifecycle": "runner started", "consumers": "PHPUnit"},
            "runtime_proof": ["abcdef3"], "simplest_alternative": "repair service",
            "choice_rationale": "runtime evidence shows application failure", "next_hypothesis": "fix application",
        }
        second["seq"] = diagnosis["seq"] + 1
        data["entries"].insert(1, diagnosis)
        self.assertNotIn("E_FOCUS", codes(data))
        diagnosis["checked"].pop("phase")
        self.assertIn("E_FOCUS", codes(data))

    def test_t2_group_vs_field_claim_rejected(self):
        data = fixture("t2_group_vs_field")
        self.assertIn("E_CLAIM_ANCESTOR", codes(data))
        data["entries"][0]["inheritance_proof"] = "etc/adminhtml/system.xml#L44"
        self.assertEqual([], codes(data))
        del data["entries"][0]["confirmation"]
        self.assertIn("E_CLAIM_INCOMPLETE", codes(data))

    def test_t3_replan_with_basis(self):
        result = check(fixture("t3_replan_with_basis"), final=True)
        self.assertTrue(result["valid"])
        self.assertFalse(result["ready"])
        self.assertEqual("NEEDS_REPLAN", result["blocker_state"])

    def test_replan_without_basis_rejected(self):
        data = fixture("t3_replan_with_basis")
        data["entries"][1]["basis"] = ["claim:99"]
        self.assertIn("E_REPLAN_BASIS", codes(data))
        data["entries"][0]["cited_path"] = "section/general/group/locale"
        data["entries"][1]["basis"] = ["claim:1"]
        self.assertIn("E_REPLAN_BASIS", codes(data))

    def test_accepted_replan_precedes_blocked_group_state(self):
        data = fixture("blockers")
        replan = fixture("t3_replan_with_basis")["entries"]
        replan[0]["seq"] = 4
        replan[1]["seq"] = 5
        replan[1]["basis"] = ["claim:4"]
        data["entries"][3:3] = replan
        result = check(data, final=True)
        self.assertEqual((True, False, "blocked", "NEEDS_REPLAN", None),
                         (result["valid"], result["ready"], result["groups"][0]["status"], result["blocker_state"], result["wait_reason"]))

    def test_final_unresolved_not_approval(self):
        self.assertIn("E_UNRESOLVED", codes(fixture("final_unresolved"), final=True))

    def test_weakened_resolution_rejected(self):
        data = fixture("final_unresolved")
        data["entries"].append({"kind": "resolution", "group": {"obligation": "R1", "signature": "assertion failed"}, "outcome": "skipped", "via_seq": 1})
        self.assertIn("E_WEAKENED", codes(data, final=True))

    def test_boolean_via_seq_does_not_resolve_attempt_or_blocker(self):
        passed = fixture("final_unresolved")
        passed["entries"][0]["result"] = "pass"
        passed["entries"].append({"kind": "resolution", "group": {"obligation": "R1", "signature": "assertion failed"}, "outcome": "passed", "via_seq": True})
        for data, outcome in ((passed, "passed"), (fixture("blockers"), "blocked")):
            with self.subTest(outcome=outcome):
                data["entries"][-1]["via_seq"] = True
                result = check(data, final=True)
                self.assertIn("E_WEAKENED", [v["code"] for v in result["violations"]])
                self.assertFalse(result["ready"])

    def test_old_pass_cannot_resolve_last_fail(self):
        data = fixture("t1_diagnosed_alternative")
        old_pass = copy.deepcopy(data["entries"][3])
        data["entries"].insert(4, {**old_pass, "seq": 5, "hypothesis": "another hypothesis", "result": "fail", "evidence": ["abcdef5"]})
        self.assertIn("E_WEAKENED", codes(data, final=True))

    def test_approval_before_later_execution_is_stale(self):
        data = fixture("t1_diagnosed_alternative")
        data["entries"].append({**data["entries"][3], "seq": 5, "hypothesis": "new hypothesis", "evidence": ["abcdef5"], "result": "fail"})
        self.assertIn("E_UNRESOLVED", codes(data, final=True))

    def test_valid_blocked_final_not_ready_exit_one(self):
        data = fixture("blockers")
        result = check(data, final=True)
        self.assertEqual((True, False, [], "blocked", "BLOCKED", "environment"), (result["valid"], result["ready"], result["violations"], result["groups"][0]["status"], result["blocker_state"], result["wait_reason"]))
        proc = subprocess.run([str(ROOT / "scripts" / "attempt-log"), "check", str(FIXTURES / "blockers.json"), "--final"], capture_output=True, text=True)
        self.assertEqual(1, proc.returncode, proc.stderr)
        self.assertEqual([], json.loads(proc.stdout)["violations"])

    def test_blocker_classification(self):
        data = fixture("blockers")
        blocker = data["entries"][2]
        for typ, reason, state in (("technical", "dependency", "BLOCKED"), ("technical", "external", "BLOCKED"), ("capacity", "runtime_capacity", "RESOURCE_QUEUED"), ("business_decision", "owner_input", "NEEDS_INPUT")):
            with self.subTest(typ=typ, reason=reason):
                blocker.update(type=typ, wait_reason=reason, missing_capability="test runner", options=["defer", "provide access"], impact="suite cannot run", researchable=False)
                result = check(data, final=True)
                self.assertTrue(result["valid"], result["violations"])
                self.assertEqual(state, result["blocker_state"])
        blocker["researchable"] = True
        self.assertIn("E_BLOCKER", codes(data))
        blocker.update(type="capacity", wait_reason="owner_input")
        self.assertIn("E_BLOCKER", codes(data))

    def test_blocker_other_group_not_resolution(self):
        data = fixture("blockers")
        data["entries"].insert(3, {"kind": "attempt", "seq": 4, "obligation": "R2", "signature": "other", "target": "suite", "class": "implementation", "hypothesis": "first", "change": "first", "change_target": "application", "observed_effect": "error", "result": "fail", "evidence": ["abcdef4"]})
        data["entries"].append({"kind": "resolution", "group": {"obligation": "R2", "signature": "other"}, "outcome": "blocked", "via_seq": 3})
        self.assertIn("E_WEAKENED", codes(data, final=True))

    def test_evidence_ref_rejects_paths(self):
        for ref in ("/tmp/run.log", "/home/user/run.log", "etc/config.xml#L8"):
            data = fixture("final_unresolved")
            data["entries"][0]["evidence"] = [ref]
            self.assertIn("E_EVIDENCE_REF", codes(data))

    def test_missing_fields_and_malformed(self):
        data = fixture("final_unresolved")
        del data["entries"][0]["hypothesis"]
        self.assertIn("E_FIELD", codes(data))
        with self.assertRaises(MalformedLog):
            parse("not json")
        self.assertEqual(data, parse("```attempt-log\n" + json.dumps(data) + "\n```"))

    def test_wrong_json_field_types_are_violations_not_tracebacks(self):
        for field, value in (("kind", {}), ("class", []), ("result", {}), ("change_target", [])):
            data = fixture("final_unresolved")
            data["entries"][0][field] = value
            self.assertIn("E_FIELD", codes(data), field)
        data = fixture("blockers")
        data["entries"][2]["type"] = {}
        self.assertIn("E_BLOCKER", codes(data))
        data = fixture("blockers")
        data["entries"][3]["via_seq"] = []
        self.assertIn("E_WEAKENED", codes(data, final=True))

    def test_cli_check_exit_codes(self):
        script = str(ROOT / "scripts" / "attempt-log")
        for name, final, expected in (("t1_diagnosed_alternative", True, 0), ("t1_override_no_effect", False, 1), ("blockers", False, 0)):
            proc = subprocess.run([script, "check", str(FIXTURES / f"{name}.json")] + (["--final"] if final else []), capture_output=True, text=True)
            self.assertEqual(expected, proc.returncode, proc.stderr)
        with self.subTest("malformed"):
            proc = subprocess.run([script, "check", str(FIXTURES / "missing.json")], capture_output=True, text=True)
            self.assertEqual(2, proc.returncode)


if __name__ == "__main__":
    unittest.main()
