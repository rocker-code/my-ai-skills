---
name: address-pr-review
description: Refresh and resolve GitHub PR feedback on the existing branch. Use after an independent review to evaluate severity-tagged findings, fix valid items, update OpenSpec for contract changes, run tests, reply with evidence and avoid blindly following stale or incorrect comments.
metadata:
  category: workflow
  stage: review
---

# Address PR Review

Correct the implementation, not merely the comment count.

## Refresh live state

Fetch PR metadata, latest diff/commits, top-level comments, reviews, inline threads, CI, linked issues and all newer comments since the last execution. Read latest `[DECISION]` comments and relevant OpenSpec. Stay on the existing PR branch; never create a replacement PR.

## Build and classify findings

Record source, severity, affected behavior/file, evidence and applicability. Preserve reviewer severity (`[BLOCKER]`, `[MUST FIX]`, `[SHOULD FIX]`, `[NICE TO HAVE]`) and classify each:

- `VALID`;
- `VALID WITH ADAPTATION` (concern is correct; proposed solution conflicts with project/framework design);
- `ALREADY RESOLVED`;
- `OBSOLETE`;
- `CONFLICTS WITH REQUIREMENTS`;
- `INVALID`;
- `AMBIGUOUS`.

Fix all valid blockers and must-fix items. Normally fix valid should-fix items within scope; if deferred, explain and propose a follow-up. Ignore nice-to-have unless trivial and scope-neutral. Do not implement obsolete/invalid/conflicting feedback just to close a thread. For ambiguity that materially changes behavior, ask rather than guess.

## OpenSpec rule

Implementation defects that preserve the contract change only code/tests. Behavioral or architectural review changes must first update and validate the active OpenSpec change via `openspec-workflow`, then update code/tests.

## Correct and validate

Trace the full affected path, use existing/native mechanisms, implement the smallest coherent correction, remove code made obsolete by the fix and add/update relevant tests. Run targeted checks first, then broader permitted validation.

Review the resulting diff against every finding, issue, decisions and OpenSpec. Do not expand the PR into unrelated improvements.

## Push and respond

When authorized by the workflow, commit/push to the same branch without force. Reply to material threads after code is available, citing the correction/test. Explain rejected findings with evidence. Resolve threads only when actually addressed and when authorized.

## Completion

Report counts by classification, changes, OpenSpec impact, actual checks, remaining material items and branch/push state. End with `READY FOR FINAL PR REVIEW` or `NOT READY — <reason>`.
