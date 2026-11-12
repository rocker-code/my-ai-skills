---
name: capture-evolutions
description: At natural planning or implementation checkpoints, process a compact batch of deferred feature scenarios in an isolated child context when available; deduplicate and register qualified linked GitHub evolution issues in future milestones, then return a minimal verified summary without disrupting the main delivery.
metadata:
  category: workflow
  stage: backlog
---

# Capture Evolutions — checkpoint worker

This is a **backlog-only skill**. Read [incremental delivery](references/INCREMENTAL_DELIVERY.md), the live source issue/comments/decisions, and GitHub repository conventions. A separate child session/subagent is preferred; it is **not** a mandatory new orchestration stage or new approval gate.

## Trigger and isolation

The supervising planning agent runs this skill once after its Explore/Propose scope classification, before handing off to Apply. The executing agent **records** discoveries during Apply without GitHub writes and calls the skill once at a natural checkpoint (normally before Prepare PR); Prepare PR reconciles leftovers rather than duplicating issues.

When the agent runtime supports fresh child tasks/subagents with GitHub access, delegate a **compact task payload** only. The child reads the current GitHub issue and relevant evidence independently; never inject the entire planning transcript, source tree, OpenSpec context or test logs. Do not create or claim a fresh child session if the runtime lacks it; perform the same work **sequentially at the checkpoint** with a bounded payload and context.

Do not acquire or mutate implementation worktrees, source code, OpenSpec proposals, approval records, tests or main task state. Only authorized GitHub backlog issue, comment/link and milestone actions are allowed. Do not read or pass secrets. Never run this skill repeatedly per candidate or hold the main coding thread for an optional backlog scan. Preserve the same source issue identity and batch identity on retries.

## Input and existing handoff

Use the existing durable planning/Apply handoff, rather than a new required file or database. Record one short entry per candidate:

```yaml
source: owner/repository#123
checkpoint: planning  # or apply
candidates:
  - key: optimize-balance-list
    title: Improve large-volume balance listing
    value: Reduce latency for growing transaction history
    deferred_because: Not needed for the current safe flow
    boundary: Maintain existing response semantics
    dependency: owner/repository#123
```

The example is illustrative, not a new API schema or required YAML parser. A few sentences per candidate are sufficient; include observed evidence or an approved decision URL when available. Do not copy long logs or speculative internal implementation details into the backlog.

## Processing algorithm

1. Validate source repository/issue, approved scope, current delivery and risk invariants against live GitHub. Reject anything that would undermine the safe flow, existing acceptance criteria or approved public contract. Escalate a truly material change to the supervising agent for the established [QUESTION]/[DECISION] path; do not silently defer it.
2. Qualify actual independently valuable enhancements, consolidate near-duplicates and discard speculative/trivial candidates with a short reason. Search the target repository's open **and closed** issues, linked parents and relevant cross-repository work before any creation. If already tracked, reuse that issue; preserve existing assignees, descriptions, milestone and decisions unless an authorized targeted update is necessary.
3. Resolve the target **future evolution milestone** by reading actual milestones in the **owning repository**. Prefer an appropriate existing future evolution milestone for this capability and phase, not the current delivery milestone. If none exists and the integration supports it, automatically create **one grouped** future evolution milestone, not one per issue. Never guess IDs, due dates, milestone availability, assignment or cross-repository identity.
4. Create only missing qualified evolution issues in the responsible repository. Use the normal create-issue protocol: short what/where/dependencies summary, current vs future behavior, explicit non-goals, concrete criteria, proportionate test cases and architecture/contracts/UI/i18n **only when relevant**. Link the source issue and related dependencies. Assign every evolution issue to a verified future milestone. Do not add future work to current OpenSpec or current delivery acceptance.
5. Update/link the source issue (minimal comment or targeted body edit without overwriting decisions), then read back every created/updated issue, its milestone, and the source link. Do not claim a successful registration based only on a request to GitHub. If issue/milestone writing, reading or link verification is unavailable, return `EVOLUTION BACKLOG BLOCKED` with exact missing actions and unregistered candidates. **Never** leave a new issue without a milestone and describe the batch as complete.
6. Return a compact summary: source issue, checkpoint, created/reused counts, URLs and future milestones, untracked/blocking items and decisions that need owner input. The supervising agent communicates it **after** processing, not as an approval request; consolidate same-checkpoint notifications.

## Idempotency and boundaries

On retry, always re-query GitHub before writes. Match by source link, behavior and owning repository, not solely by title; do not duplicate or rename pre-existing issues just to fit a new naming scheme. If the source issue was closed or the candidate is already delivered, verify first rather than opening a duplicate. For two independent repositories, track and link each responsible issue separately and use that repository's milestone IDs.

Backlog creation does **not** authorize implementation, reprioritization, merging or modifying the current delivery's validated contract. An unavailable milestone creation API is a **capability blocker**, not permission to leave accepted evolutions in the current milestone, assign an arbitrary milestone or report success.

## Output contract

Use one of:

- `EVOLUTIONS TRACKED` — every qualified candidate created/reused, linked and future-milestoned, with verified URLs.
- `NO QUALIFIED EVOLUTIONS` — candidate batch empty, speculative, irrelevant or fully delivered, with a short reason.
- `EVOLUTION BACKLOG BLOCKED — <exact missing capability or decision>` — report what was and was not persisted.

Do not treat a blocked backlog batch as a failed implementation test. Preserve the blocker visibly in the existing handoff and PR summary; only existing workflow gates determine whether the implementation may continue.
