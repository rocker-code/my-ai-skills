---
name: apply-issue
description: Route a validated issue to native OpenSpec Apply in a fresh context and retain project test, ownership and delivery safeguards.
---

# Apply a validated issue

Use a genuinely fresh implementation context. Read [openspec-workflow](../openspec-workflow/SKILL.md), verify exact proposal SHA, review/validation, decisions and delivered dependencies, then invoke native `openspec-apply-change`. Missing evidence blocks affected implementation; do not simulate independence.

Follow [TEST_STRATEGY.md](references/TEST_STRATEGY.md), including pre-flight, smallest proving layer, safe fixtures/services, failure diagnosis and final required suites. Inspect current source, callers and repository conventions before coding. Use optional `simplify` only for a concrete issue-scoped readability problem or explicit request; preserve behavior/contracts/errors/side effects and rerun relevant tests. Material changes require revised reviewed/validated OpenSpec.

Follow [WORKTREES.md](references/WORKTREES.md): verify reservation before writes and checkpoint own changes, one writer per checkout. Keep M2T selections in the existing handoff across Apply, failures and PR corrections; no post-command down/reset. Record actual exit/run and current-code test proof; `m2t runs show <run-id> --json` applies to test/graphql, with only the pertinent private log excerpt on failure. Unit/exec use separate receipts and clean disposable resources internally. The M2T lock does not transfer checkout ownership; owned integration/GraphQL instances stay until safe delivered closeout.

At a natural checkpoint, capture only qualified untracked evolutions under [incremental delivery](references/INCREMENTAL_DELIVERY.md). Invoke native Verify by default when supported, strict validation and Archive via the adapter, inspect synchronized specs, then `prepare-pr`. Commit archive/distribution/preparation before recording the required final local suite on exact clean HEAD; keep proof outside that commit and rerun after a later commit. Unknown termination/report is incomplete, never PASS. Keep GitHub communication canonical; no progress/event comments.
