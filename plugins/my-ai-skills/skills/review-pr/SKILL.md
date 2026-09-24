---
name: review-pr
description: Independently review a GitHub pull request against its issue, latest decisions, OpenSpec, repository architecture, final diff and tests. Use for implementation review in ChatGPT/Claude Web; produces evidence-backed severity-tagged findings and does not implement fixes.
metadata:
  category: web-supervision
  stage: review
---

# Review Pull Request

Review the system of intent and implementation, not the diff alone.

Use `pr-audit` for the traceability and evidence pass; this skill manages the independent review findings and PR comments. Invoke `architecture-audit` for material boundary changes.

## Refresh and correlate

Read live PR metadata/diff/commits, issue and all comments, `[DECISION]` entries, approved OpenSpec artifacts (active or archived) and synchronized live specs, repository instructions/architecture, relevant unchanged code, tests, CI and earlier review threads.

Load the applicable domain checklist such as `magento-review` or `expo-mobile-review`.

## Evaluate

Check acceptance coverage, contract/schema consistency, state and authorization, data/migration, concurrency/idempotency, failure behavior, security, regressions, native reuse, tests and removal of obsolete code. Do not expand the issue with unrelated redesign.

Classify findings according to [the review policy](../../protocol/REVIEW_POLICY.md):

- `[BLOCKER]`;
- `[MUST FIX]`;
- `[SHOULD FIX]`;
- `[NICE TO HAVE]`.

Every actionable finding needs evidence, impact and the smallest acceptable outcome. Verify it against current code before commenting. Avoid duplicate or stale findings.

When authorized, add findings to the PR in the most precise location; otherwise provide copy-ready comments. Do not implement, push, resolve threads or merge.

Conclude with counts by severity and `CHANGES REQUIRED`, `APPROVED WITH NON-BLOCKING FOLLOW-UPS`, or `READY FOR FINAL REVIEW`.
