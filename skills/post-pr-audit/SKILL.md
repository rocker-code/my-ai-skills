---
name: post-pr-audit
description: Check merge eligibility using an existing independent final-HEAD review; request pr-audit only for missing or invalidated evidence. This is not a second full audit.
---

# Merge eligibility (compatibility entry)

This retained public entry supplies merge eligibility formerly attached to a second full audit. Reuse the current independent `pr-audit` verdict under [REVIEW_POLICY.md](references/REVIEW_POLICY.md). Do not demand a second reviewer or repeat a full audit of the same immutable HEAD and context. If review is missing, request it; a changed HEAD/base/policy invalidates affected evidence and requires independent focused re-review. Never let implementation self-certify independent review.

Refresh issue/decisions, current base/head, archived/synchronized OpenSpec, findings, required checks and human approvals. Confirm required local suite on the exact clean HEAD and accessible proof via `workflow-evidence verify` where installed; metadata_only/incomplete/ambiguous/stale is not PASS. Hosted gates require trusted base-policy/check mapping and API confirmation for the exact SHA. Unknown or missing required proof blocks merge; hosted results do not replace local gates. Follow [TEST_STRATEGY.md](references/TEST_STRATEGY.md).

## Merge mode

Default to `merge_mode=auto-if-green` under the owner's standing instruction for the PR/run being reviewed, whether invoked directly or through a verified `github-resolution` handoff. A direct "do not merge" or `merge_mode=manual` request overrides this default and returns `READY TO MERGE` for the owner. The default authorizes completion without another confirmation only after every gate below passes. Never infer merge eligibility from a green CI result alone. Do not merge a draft, wrong-target PR, unresolved blocking review, unvalidated changed scope, failed or unknown required gate. Verify the target branch and permitted merge method from repository policy; do not bypass protections or use administrator privileges to override them.

After a valid independent pr-audit approves the exact current head, all non-CI gates clear and the final audit finds no blocker:

- If applicable required CI checks are already green, refresh head/base, approvals and mergeability immediately before a direct merge; supply the expected head SHA so a concurrent push rejects the operation. Verify returned merged state and merge SHA.
- If CI is still pending, enable native GitHub auto-merge only when repository rules enforce every applicable required check and review on the target branch, auto-merge is enabled, the expected head is still current and no blocking audit finding remains. GitHub will merge once its requirements pass. Report `AUTO-MERGE ENABLED` as pending, never as merged. If protections do not enforce the necessary gates, keep observing in the current run and merge only after the exact head turns green; if observation cannot continue, report `AWAITING CHECKS` and the next action without falsely claiming automation is active.
- If GitHub rejects enabling auto-merge or a merge queue/branch policy requires another path, stop at the accurate blocker. Never bypass checks. If the head/base changes before landing, independently review the invalidated surfaces and do not rely on the old verdict.

After a confirmed merge, verify the merge SHA and linked issue state. Check merge-commit CI when the repository requires it; a green PR head does not establish the result of a different merged tree. If GitHub queued auto-merge and the run ends before landing, do not claim verification of a future merge.

For an M2T-backed issue, the final audit does not close the sandbox. After confirmed delivery, the closeout owner follows WORKTREES' liveness/ownership checks and M2T-before-Git cleanup for exact owned selections; pending CI, open PR, active worker or uncertain ownership retains checkout and sandbox. Report partial cleanup rather than implying the merge alone authorized `down`.

Report base/head SHA, trust gate, CI and review state, evidence matrix summary, reused/not-run validations with reasons, unresolved findings and accepted follow-ups. End with the precise state: `READY TO MERGE`, `AUTO-MERGE ENABLED`, `MERGED — <sha>`, `AWAITING CHECKS`, `CHANGES REQUIRED — <reason>` or `UNVERIFIED — <missing evidence>`. Do not merge or close issues in manual mode.
