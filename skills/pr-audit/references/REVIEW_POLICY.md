# Review Policy

## Evidence model

Review the combined system:

```text
issue + latest decisions + OpenSpec + repository architecture + final diff + tests/checks
```

Do not review the diff in isolation and do not treat every reviewer suggestion as authoritative.

## Severity

| Marker | Meaning | Merge policy |
|---|---|---|
| `[BLOCKER]` | Security, data loss, broken core behavior, invalid architecture boundary or unrecoverable migration risk. | Must be resolved. |
| `[MUST FIX]` | Acceptance criterion, correctness, contract, authorization, concurrency or required test defect. | Must be resolved. |
| `[SHOULD FIX]` | Material maintainability, resilience or coverage issue within scope. | Normally resolve; may become a follow-up only with explicit rationale. |
| `[NICE TO HAVE]` | Non-blocking improvement or polish. | Never hold the PR; record a follow-up only if independently valuable, actionable, untracked and qualified by the evolution policy. |

Every finding should include evidence, impact and the smallest acceptable correction. Avoid speculative or style-only findings without project policy support.

## Implementation review

May identify requirement gaps and architectural defects by comparing issue, decisions, OpenSpec, code and tests.

## Final review / Review Freeze

Final review does not invent features, redesign accepted choices or reopen settled trade-offs. It checks only:

- unresolved blocker/must-fix findings;
- regressions, security and data integrity;
- contract and state-transition errors;
- concurrency/transaction defects;
- missing required tests;
- dead/obsolete code introduced by the PR;
- acceptance criteria and earlier review resolution;
- required CI/spec validation.

End with exactly one decision:

```text
FINAL REVIEW: APPROVED
```

or

```text
FINAL REVIEW: CHANGES REQUIRED
```

Once approved, further non-blocking improvements become separate issues.

## One review per immutable candidate

One genuinely independent final-HEAD review satisfies the review gate. Merge eligibility reuses it; no second full audit of unchanged code. After HEAD, base or relevant context changes, independently review invalidated surfaces and rerun affected proofs; keep the final required suite bound to exact clean HEAD. Contributor-controlled policy changes do not approve their own review.
