---
name: milestone-orchestrator
description: Carry one issue, an exact milestone or an authorized repository queue through delivery sequentially, respecting dependencies, ownership and verified recovery.
---

# Sequential issue coordinator

Read [AI_WORKFLOW.md](references/AI_WORKFLOW.md). This is a control plane for scope, dependency order, one active issue, worker ownership, blockers and delivery; native OpenSpec owns planning/implementation. Do not mirror OpenSpec tasks, implement or certify review in the parent context when independent workers are required.

## Scope and inventory

Accept natural requests: "cuide da issue URL", "cuide deste milestone URL", "cuide da fila deste projeto". Establish exact repository and scope from explicit URL or unique evidence; ask only for missing/ambiguous identity. A single issue never authorizes siblings/prerequisites. A closed issue requires delivery verification, not reopening. Add "sem merge(s)" to select manual; otherwise preserve authorized auto-if-green for this scope. Never widen scope on recovery.

Inventory scoped issues/PRs and Git/OpenSpec/worktrees read-only; paginate complete scope. Detect existing PR/change and hard dependencies, including effective producer/consumer contracts. No duplicate branch/change/PR. An unmerged prerequisite or unverified contract blocks its consumer. Detect dependency cycles; do not invent an ordering for unknown edges. Related issues outside scope are read-only evidence.

## One active issue

1. Reconstruct existing verified progress before selecting new work. Select the interrupted active issue first when safe; otherwise one eligible issue ordered by real dependencies. **At most one active issue**, including planning. Independent issues must not be planned or implemented concurrently.
2. Reserve/reuse the issue checkout under [WORKTREES.md](references/WORKTREES.md). With real runtime support, delegate only inside the active issue: Planning uses native Explore/Propose through `implement-issue`; fresh Apply receives the exact reviewed/validated proposal after stopped-writer ownership handoff; independent `pr-audit` reviews the final candidate. Use runtime callbacks/queries and exact Git/test evidence, never prose or dispatch acknowledgement as completion. Missing capability blocks its affected action; never simulate independence.
3. Check worker identity, repository/issue, input/output SHAs, actual outcome, ownership, accessible proofs and next action. Return stale or materially changed proposals to native planning. Hard producer dependencies require `contract-handoff` design review and final frozen effective contract before consumer integration. Use [TEST_STRATEGY.md](references/TEST_STRATEGY.md), project tests/M2T/CI and existing evidence helpers; never waive mandatory proofs.
4. For an existing PR, route directly to `github-resolution`, reusing valid independent review and verifying current HEAD/checks. It owns only feedback and merge loop. Preserve authorized mode and actual GitHub protections; unknown required evidence never means approved.
5. Finish confirmed merge/closure, or explicitly park the issue before selecting another. Parking retains branch/change/PR, ownership-safe checkpoint, last verified state, blocker/reason and next action in existing canonical artifacts/content; stop all its active writers before advancing. A pending check may be awaited or explicitly parked, not silently executed alongside another issue. A material owner decision blocks only affected work after safe parking.
6. Perform eligible housekeeping after delivery without waiting for Kaizen, then select the next eligible scoped issue. Continue until all delivered, explicitly parked/blocked or a real capability/resource limit; one invocation authorizes continuation, not one user command per stage. Subagents never start another issue in the queue.

Keep only useful states queued, planning, implementing, reviewing, blocked, delivered, backed by authoritative refs. Show a compact table with issue/PR, current SHA/state, blocker and next action. Do not create a database, redundant ledger or operational GitHub comments. Requirements/decisions stay in issue body/OpenSpec, proof in commits/PR/checks/reviews. Comments only for material questions, owner-action blockers or actionable review discussion. Capture only qualified untracked evolutions under [INCREMENTAL_DELIVERY.md](references/INCREMENTAL_DELIVERY.md), at natural checkpoints; no cosmetic issue or mandatory backlog gate when no candidate exists.

## Recovery and housekeeping

Use `resume-workflow` for interrupted work: reconcile Git/GitHub/OpenSpec, native runtime status, accessible test proof and one-writer reservation. An unknown worker, test without termination/report, ambiguous ownership or missing capability remains unknown/blocked. Reuse valid completed work; do not treat a changed session as reason to restart planning or duplicate PR. Honor manual mode; unknown earlier authorization holds merge pending resolution.

Global helpers resolve at `${XDG_DATA_HOME:-$HOME/.local/share}/my-ai-skills/active/scripts/<helper>`; run with explicit checkout and quoted paths. `worktree-reservation` verifies before writes, checkpoints own changes and transfers only after prior writer stops. Preserve unrelated work, no force/blanket cleanup. Inventory eligible leftovers at startup/resume/end under WORKTREES; no owner/test/process/data/unique undelivered commit may remain. For M2T keep exact owned selections through PR/failure; close safe owned instances through public commands before non-forced Git removal. Any unknown selection or partial failure retains checkout and handoff. Report per-selection removed/retained results. Kaizen is on demand, never on the critical path. CI optimization follows [CI_PERFORMANCE.md](references/CI_PERFORMANCE.md) only where relevant, not workflow analytics.

Read-only status requests route to `milestone-progress` or `roadmap-status`; do not start execution as a reporting side effect.
