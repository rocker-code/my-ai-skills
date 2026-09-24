---
name: final-review
description: Perform an independent final PR review after corrections and enforce Review Freeze. Use in ChatGPT/Claude Web to verify only regressions, blockers, contracts, tests, CI and previous feedback, then return a definitive approval or changes-required decision without inventing enhancements.
metadata:
  category: web-supervision
  stage: review
---

# Final Review

Apply Review Freeze. This is not a new implementation review and must not generate feature scope, redesign accepted choices or reopen settled trade-offs.

Refresh the latest PR diff/commits/comments/reviews/CI, linked issue and `[DECISION]` comments, approved OpenSpec artifacts (active or archived), synchronized live specs and previous findings. Verify:

- no unresolved valid `[BLOCKER]` or `[MUST FIX]`;
- prior corrections exist in current code and have appropriate tests;
- acceptance criteria and OpenSpec still match the final diff;
- no regression, security, data-integrity, contract, state, authorization, concurrency or migration blocker;
- required CI/spec validation is successful or explicitly blocking;
- no introduced dead code or weakened tests.

`[NICE TO HAVE]` never blocks. Remaining non-blocking improvements become separate issues. A new finding is appropriate only when it meets blocker/must-fix severity and is supported by current evidence.

When authorized, leave the final decision on the PR. Do not implement, push or merge unless separately requested.

End with exactly one:

```text
FINAL REVIEW: APPROVED
```

or

```text
FINAL REVIEW: CHANGES REQUIRED
```
