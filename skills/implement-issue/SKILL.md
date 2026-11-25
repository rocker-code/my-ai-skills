---
name: implement-issue
description: Plan or resume a GitHub issue with native OpenSpec Explore and Propose; route existing PRs to review.
---

# Plan an issue

This public entry routes to [openspec-workflow](../openspec-workflow/SKILL.md); it is not another planner. Resume matching change/PR, inspect live issue/code/decisions in native Explore, then native Propose only when needed. Pin the officially validated and reviewed proposal; continue automatically to a fresh Apply context via `apply-issue` when evidence is complete. Escalate only material unresolved decisions. An existing PR routes to `github-resolution`.

Use [TEST_STRATEGY.md](references/TEST_STRATEGY.md) for the existing acceptance/risk matrix and pre-flight; inspect current fixtures, rollback, mounted checkout, toolchain, service isolation and required commands before expensive tests. No code implementation in planning. Apply [incremental delivery](references/INCREMENTAL_DELIVERY.md) to qualified evolution candidates only.

Follow [WORKTREES.md](references/WORKTREES.md): reuse the verified issue checkout, transfer one-writer reservation only after the planning context stops, and carry M2T checkout, exact owned selections and current-code proof in the existing handoff. No session-boundary teardown; the M2T execution lock does not grant checkout ownership. Return pinned proposal/review/validation, dependency refs and next action, not a new record service.
