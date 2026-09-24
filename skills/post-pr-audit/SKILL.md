---
name: post-pr-audit
description: Verify the final PR state after review fixes and immediately before merge. Use to check approved scope, OpenSpec traceability, CI, reviews, cleanup and outstanding blockers; return READY TO MERGE or CHANGES REQUIRED without merging.
---

# Post PR Audit

Fetch the current PR head SHA, full final diff, issue and decisions, pinned OpenSpec revision, CI/check conclusions, approvals and unresolved review threads. Recheck after a push or CI rerun; previous audit results do not cover a newer head.

Check acceptance criteria and OpenSpec requirement → implementation → test evidence; valid blocker/must-fix findings resolved; required checks green for this head; migration/contract/architecture/documentation obligations satisfied; obsolete code, temporary workarounds and debt assessed. Distinguish missing required evidence from checks that are not configured. Link a follow-up issue for accepted non-blocking debt when appropriate. Never replace repository branch protection or the owner's merge decision.

Report head SHA, CI and review state, evidence matrix summary, unresolved findings, follow-ups and exactly one: `READY TO MERGE`, `CHANGES REQUIRED — <reason>` or `UNVERIFIED — <missing evidence>`. Do not merge or close issues.
