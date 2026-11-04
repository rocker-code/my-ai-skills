"""Structural checks for the retry reasoning block in an existing validation handoff.

Evidence references are deliberately opaque: this module never reads execution
manifests, configuration files, or the cited contract definition.
"""

import json
import re


EXECUTION_REF = re.compile(r"(?:evidence:ev-\d{8}T\d{6}Z-[0-9a-f]{8}|https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_./#-]+)?|[0-9a-fA-F]{7,64})\Z")
CODE_REF = re.compile(r"(?!/|\.\./)(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+#L[1-9]\d*\Z")
CLASSES = {"environment/bootstrap", "fixture/isolation", "implementation", "assertion/contract", "intermittent"}
TARGETS = {"application", "test", "fixture", "environment", "plan", "none"}
BLOCKER_REASONS = {
    "technical": ("BLOCKED", {"environment", "dependency", "external"}),
    "capacity": ("RESOURCE_QUEUED", {"runtime_capacity"}),
    "business_decision": ("NEEDS_INPUT", {"owner_input"}),
}


class MalformedLog(ValueError):
    """Input cannot be parsed as one attempt-log document."""


def normalize(value):
    return " ".join(value.lower().split()) if isinstance(value, str) else ""


def present(value):
    return isinstance(value, str) and bool(value.strip())


def parse(text):
    fences = re.findall(r"^```attempt-log\s*\n(.*?)^```\s*$", text, re.MULTILINE | re.DOTALL)
    if "```attempt-log" in text and len(fences) != 1:
        raise MalformedLog("expected exactly one closed attempt-log fence")
    if fences:
        text = fences[0]
    try:
        data = json.loads(text)
    except (ValueError, TypeError) as exc:
        raise MalformedLog(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict) or type(data.get("attempt_log")) is not int or data["attempt_log"] != 1 or not isinstance(data.get("entries"), list):
        raise MalformedLog("expected attempt_log: 1 and entries: array")
    if any(not isinstance(entry, dict) for entry in data["entries"]):
        raise MalformedLog("each entry must be an object")
    return data


def check(data, *, final=False):
    """Validate a parsed document; valid concerns rules, ready concerns final approval."""
    violations = []
    groups = {}
    claims = {}
    blockers = {}
    seen_refs = set()
    last_seq = 0
    replan_required = False

    def violation(code, seq, message):
        violations.append({"code": code, "seq": seq, "message": message})

    def required(entry, seq, *keys):
        for key in keys:
            if not present(entry.get(key)):
                violation("E_FIELD", seq, f"missing {key}")

    def refs(value, seq, *, citation=False, required_refs=False):
        if not isinstance(value, list) or (required_refs and not value):
            violation("E_FIELD", seq, "missing evidence references")
            return []
        good = []
        for ref in value:
            if not isinstance(ref, str) or not (EXECUTION_REF.fullmatch(ref) or (citation and CODE_REF.fullmatch(ref))):
                violation("E_EVIDENCE_REF", seq, f"invalid reference: {ref!r}")
            else:
                good.append(ref)
        return good

    def group_for(entry, seq):
        group = entry.get("group")
        if not isinstance(group, dict):
            violation("E_FIELD", seq, "missing group")
            return None
        required(group, seq, "obligation", "signature")
        if not present(group.get("obligation")) or not present(group.get("signature")):
            return None
        key = (group["obligation"], normalize(group["signature"]))
        if key not in groups:
            violation("E_FIELD", seq, "group has no attempt")
            return None
        return key

    for entry in data["entries"]:
        kind = entry.get("kind")
        seq = entry.get("seq")
        if not isinstance(kind, str) or kind not in {"attempt", "diagnosis", "contract_claim", "replan", "blocker", "resolution"}:
            violation("E_FIELD", seq, "unknown kind")
            continue
        if kind != "resolution":
            if type(seq) is not int or seq <= last_seq:
                violation("E_FIELD", seq, "seq must increase")
                continue
            last_seq = seq
        if kind == "attempt":
            required(entry, seq, "obligation", "signature", "target", "class", "hypothesis", "change", "observed_effect", "result", "change_target")
            if not all(isinstance(entry.get(k), str) for k in ("class", "result", "change_target")) or entry.get("class") not in CLASSES or entry.get("result") not in {"pass", "fail"} or entry.get("change_target") not in TARGETS:
                violation("E_FIELD", seq, "invalid class, result or change_target")
            evidence = refs(entry.get("evidence"), seq, required_refs=True)
            if not present(entry.get("obligation")) or not present(entry.get("signature")):
                continue
            key = (entry["obligation"], normalize(entry["signature"]))
            state = groups.setdefault(key, {"attempts": [], "diagnoses": [], "blockers": [], "resolution": None, "seen_refs": set()})
            attempts = state["attempts"]
            state["resolution"] = None  # a later execution invalidates any earlier approval
            previous = next((item for item in reversed(attempts) if normalize(item.get("hypothesis")) == normalize(entry.get("hypothesis"))), None)
            if previous is not None:
                changed = present(entry.get("observed_change")) and normalize(entry["observed_change"]) not in {"n/a", "none", "unchanged", "sem mudança"}
                if not changed or normalize(entry.get("observed_effect")) == normalize(previous.get("observed_effect")) or not set(evidence) - state["seen_refs"]:
                    violation("E_NO_NEW_EVIDENCE", seq, "repeated hypothesis requires changed observed effect, concrete summary and a new cited reference")
            # A pass is progress; only the current uninterrupted failure streak counts.
            pending_failures = []
            for item in reversed(attempts):
                if item.get("result") != "fail":
                    break
                pending_failures.append(item["seq"])
            if len(pending_failures) >= 2:
                second_failure = pending_failures[-2]
                if not any(second_failure < diag["seq"] < seq and diag["complete"] for diag in state["diagnoses"]):
                    violation("E_RETRY_LIMIT", seq, "diagnose after the second failure and before any next attempt")
            if attempts and attempts[-1].get("class") == "environment/bootstrap" and entry.get("change_target") == "application":
                if not any(attempts[-1]["seq"] < diag["seq"] < seq and diag.get("class") != "environment/bootstrap" and diag["complete"] for diag in state["diagnoses"]):
                    violation("E_FOCUS", seq, "environment failure cannot trigger application edit without reclassification")
            attempts.append(entry)
            state["seen_refs"].update(evidence)
            seen_refs.update(evidence)
        elif kind == "diagnosis":
            key = group_for(entry, seq)
            checked = entry.get("checked")
            complete = isinstance(entry.get("class"), str) and entry["class"] in CLASSES and isinstance(checked, dict) and all(present(checked.get(k)) for k in ("phase", "scope", "lifecycle", "consumers"))
            proof = entry.get("runtime_proof")
            if isinstance(proof, list):
                complete = complete and bool(proof)
                refs(proof, seq, citation=True, required_refs=True)
            else:
                complete = complete and present(proof) and proof.startswith("not_applicable: ") and present(proof[16:])
            complete = complete and all(present(entry.get(k)) for k in ("simplest_alternative", "choice_rationale", "next_hypothesis"))
            if not complete:
                violation("E_DIAG_INCOMPLETE", seq, "classification, effective checks, runtime proof, alternative, rationale and next hypothesis required")
            if key:
                groups[key]["diagnoses"].append({"seq": seq, "complete": complete, "class": entry.get("class")})
        elif kind == "contract_claim":
            required(entry, seq, "definition_ref", "cited_path", "field_path", "scope", "observation", "inference", "confirmation")
            definition = entry.get("definition_ref")
            if present(definition):
                refs([definition], seq, citation=True)
            path, field = entry.get("cited_path"), entry.get("field_path")
            ancestor = present(path) and present(field) and field.startswith(path.rstrip("/") + "/")
            inheritance = entry.get("inheritance_proof")
            if ancestor and not present(inheritance):
                violation("E_CLAIM_ANCESTOR", seq, "ancestor is not proof of the field's attribute")
            if present(inheritance):
                refs([inheritance], seq, citation=True)
            if not all(present(entry.get(k)) for k in ("definition_ref", "cited_path", "field_path", "scope", "observation", "inference", "confirmation")):
                violation("E_CLAIM_INCOMPLETE", seq, "exact definition, field, scope, observation, inference and confirmation required")
            claims[seq] = (not ancestor or present(inheritance)) and (not present(definition) or bool(EXECUTION_REF.fullmatch(definition) or CODE_REF.fullmatch(definition)))
            claims[seq] &= all(present(entry.get(k)) for k in ("definition_ref", "cited_path", "field_path", "scope", "observation", "inference", "confirmation"))
        elif kind == "replan":
            basis = entry.get("basis")
            if not isinstance(basis, list) or not basis or not present(entry.get("openspec_revision")):
                violation("E_REPLAN_BASIS", seq, "material replan requires a basis and OpenSpec revision")
            else:
                accepted = any(isinstance(ref, str) and ((ref.startswith("claim:") and ref[6:].isdigit() and claims.get(int(ref[6:]), False)) or (EXECUTION_REF.fullmatch(ref) and ref not in seen_refs)) for ref in basis)
                if not accepted:
                    violation("E_REPLAN_BASIS", seq, "basis must cite an accepted claim or new execution evidence")
                else:
                    replan_required = True
            if isinstance(basis, list):
                seen_refs.update(ref for ref in basis if isinstance(ref, str) and EXECUTION_REF.fullmatch(ref))
        elif kind == "blocker":
            key = group_for(entry, seq)
            typ = entry.get("type")
            mapped = BLOCKER_REASONS.get(typ) if isinstance(typ, str) else None
            valid = mapped is not None and isinstance(entry.get("wait_reason"), str) and entry["wait_reason"] in mapped[1] and isinstance(entry.get("evidence"), list) and bool(entry["evidence"])
            refs(entry.get("evidence"), seq, required_refs=True)
            if typ == "technical":
                valid = valid and present(entry.get("diagnosis")) and any(entry["diagnosis"] == f"seq:{d['seq']}" and d["complete"] for d in groups.get(key, {}).get("diagnoses", []))
            elif typ == "capacity":
                valid = valid and present(entry.get("missing_capability"))
            elif typ == "business_decision":
                valid = valid and isinstance(entry.get("options"), list) and len([x for x in entry["options"] if present(x)]) >= 2 and present(entry.get("impact")) and entry.get("researchable") is False
            if not valid:
                violation("E_BLOCKER", seq, "invalid blocker type, wait reason, evidence or type-specific explanation")
            if key:
                blockers[seq] = {"key": key, "valid": valid, "state": mapped[0] if mapped else None, "wait_reason": entry.get("wait_reason")}
        elif kind == "resolution":
            key = group_for(entry, seq)
            if key:
                if not isinstance(entry.get("via_seq"), int) or entry["via_seq"] > last_seq:
                    violation("E_WEAKENED", entry.get("via_seq"), "resolution must refer to an earlier event")
                groups[key]["resolution"] = entry

    output_groups = []
    blocker_state = "NEEDS_REPLAN" if replan_required else None
    blocker_wait_reason = None
    ready = not replan_required
    for key, state in groups.items():
        attempts = state["attempts"]
        if not attempts:
            continue
        last = attempts[-1]
        resolution = state["resolution"]
        status = "open"
        if resolution:
            outcome, via = resolution.get("outcome"), resolution.get("via_seq")
            if outcome == "passed" and last.get("result") == "pass" and via == last.get("seq"):
                status = "resolved"
            elif outcome == "blocked" and type(via) is int and via in blockers and blockers[via]["valid"] and blockers[via]["key"] == key and last.get("result") == "fail" and via > last["seq"]:
                status = "blocked"
                blocker_state = blockers[via]["state"]
                blocker_wait_reason = blockers[via]["wait_reason"]
            else:
                violation("E_WEAKENED", via, "resolution must cite latest passing attempt or valid same-group blocker after failure")
        if status != "resolved":
            ready = False
            if final and last.get("result") == "fail" and status != "blocked":
                violation("E_UNRESOLVED", last.get("seq"), "last failed attempt remains unresolved")
        output_groups.append({"key": {"obligation": key[0], "signature": key[1]}, "attempts": len(attempts), "status": status, "replan_required": replan_required})

    valid = not violations
    return {"valid": valid, "ready": (valid and ready) if final else None, "groups": output_groups, "violations": violations, "blocker_state": blocker_state, "wait_reason": blocker_wait_reason}
