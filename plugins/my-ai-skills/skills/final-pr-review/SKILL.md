---
name: final-pr-review
description: Perform the executor-side final self-review of an existing PR after review fixes. Use before returning the PR for independent final approval to verify issue decisions, OpenSpec, final diff, tests, CI and prior comments without adding new feature scope.
metadata:
  category: workflow
  stage: review
---

# Final PR Review

This is a self-review after fixes, not the independent `final-review` approval. Run `post-pr-audit` on the final head before the owner's merge decision.

Refresh the entire PR, newer comments/reviews/commits, linked issue decisions, approved OpenSpec artifacts (active or archived), synchronized live specs and CI. Compare:

```text
issue + [DECISION] + OpenSpec + final diff + tests + previous findings
```

Verify only merge-relevant quality:

- all acceptance criteria and required tasks are implemented;
- every valid `[BLOCKER]` and `[MUST FIX]` is corrected;
- `[SHOULD FIX]` is corrected or explicitly and safely deferred;
- no contract/schema/state/auth/concurrency/migration inconsistency remains;
- required tests cover success and important failures;
- no introduced dead code, debug output, secrets, unrelated churn or weakened assertions;
- required CI and OpenSpec validation pass or have an explicit blocker.

Do not invent features, revisit accepted design preferences or implement `[NICE TO HAVE]` scope. If a material defect is found, fix it only when already authorized and in scope, then rerun relevant checks.

Report remaining findings, validations actually executed, CI/OpenSpec status and end with exactly one:

```text
READY FOR EXTERNAL FINAL REVIEW
```

or

```text
NOT READY — <concrete reason>
```
