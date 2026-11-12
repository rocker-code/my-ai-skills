# Incremental Delivery and Evolution Backlog

Apply this policy to **new capabilities** during issue creation/refinement, audit, OpenSpec Explore/Propose, Apply, and PR preparation. Existing capabilities and bug fixes still follow approved acceptance criteria; this policy is not a shortcut around contractual obligations.

## Goal and decision rule

Deliver the smallest **complete, useful and safe vertical slice** first. The happy path is the primary product journey, **not** permission to omit essential validation, business invariants, authorization/ownership, integrity, persistence, reliable error handling or explicitly approved acceptance criteria.

For each scenario, classify it as:

| Class | Action |
| --- | --- |
| **Current delivery — essential** | Needed for an end-to-end usable outcome, approved behavior or existing dependency; implement and prove now. |
| **Current delivery — risk boundary** | Required to keep money, points, stock, privacy, authorization, data integrity or irreversible effects safe; implement a proportionate safe baseline now. |
| **Future evolution** | Independently valuable enhancement, exceptional UX, speculative edge case, scale optimization or nonessential sophistication; defer, with traceability. |
| **Not planned** | Out of product intent, obsolete or no demonstrated value; record as non-goal, not an automatic issue. |

Do not defer a scenario merely because it is difficult, costly to test or technically inconvenient. Do not turn every possible case into an evolution. Prefer a simpler safe solution over unsafe deferral. Keep mandatory repository tests and explicit validated proof obligations. A scenario needed to fulfill a public contract or approved design stays in the current delivery unless that contract/decision is legitimately revised.

## During planning

1. Identify the concrete first user/business journey, its completion condition and essential failure/authorization boundaries. Review related issues, PRs, code and decisions; avoid duplicate implementation.
2. In the existing issue and OpenSpec artifacts, separate **current delivery**, **future evolutions** and **non-goals**, with the reason for every material deferral. Ensure diagrams, contracts, acceptance criteria and tests describe only the agreed current scope; avoid fake future fields or assumed implementation.
3. For any change to already approved scope, obtain the required material decision and update the issue and pinned/revalidated OpenSpec contract before implementation. Routine candidate evolutions need no new approval gate. For clearly optional, independently valuable work, the established product direction authorizes **automatic backlog registration**, not automatic implementation or prioritization.

## During Apply

If a new complex scenario emerges, first determine whether it violates the approved behavior or safety baseline. Implement and test current-delivery scenarios; for nonessential enhancements record a compact candidate with parent issue, business value, reason for deferral, dependency, and proposed acceptance boundaries in the **existing handoff**. Do not silently change the approved contract or add unrequested sophistication. Replan through existing OpenSpec revision gates when necessary. Candidate discovery must not stop unrelated eligible work. **Do not perform GitHub backlog research/writes inline with an active implementation step**; hand candidates to `capture-evolutions` at a natural checkpoint.

## Persist and schedule evolutions

**Register first, notify afterward, at natural checkpoints.** During planning (after Explore/Propose, before handoff) and Apply (existing checkpoint/Prepare PR), call `capture-evolutions` once per accumulated batch. Keep only compact candidate records in the **existing** durable handoff; the worker reads GitHub evidence itself. When the runtime offers fresh subagents, give the worker a separate context/session with GitHub access and **no implementation worktree ownership**. When subagents are unavailable, run the same skill sequentially at the checkpoint with a bounded context, not inside active coding; do not fabricate parallel execution. The worker automatically reconciles concrete deferred enhancements with open/closed issues and relevant cross-repository counterparts, groups related scenarios, and persists independently deliverable future work **without routine human approval**. Do not hold every batch until PR preparation; process planning candidates before Apply, Apply candidates at the next checkpoint, and reconcile once at PR preparation. For every **qualified future evolution**:

1. Create or update a concrete GitHub issue in the responsible repository with a short summary, future behavior, explicit current non-goals, parent/source issue link, dependencies, observable acceptance and proportionate scenarios. Link the parent issue back to the evolution issue (body or comment, preserving unrelated content); link cross-repository counterparts where relevant.
2. **Always assign the evolution issue to a future evolution milestone**, never the current delivery milestone. Reuse an appropriate existing future milestone for the same product/capability and phase. If none exists, automatically create a new, clearly named evolution milestone in the owning repository, grouping related deferred work; do not create one milestone per small improvement. Never infer a milestone number or transfer milestone IDs across repositories.
3. Preserve milestones already approved for other work. Do not move or silently reprioritize unrelated issues. A future milestone is a backlog grouping, not an automatic delivery date or commitment.
4. Verify issue creation/updates, parent links and milestone assignment by reading GitHub state. If GitHub write access, milestone creation or verification is unavailable, report `EVOLUTION BACKLOG BLOCKED` with exact candidates and missing actions; **never claim the items were recorded or assigned**. Do not close the main delivery as fully handed off while accepted evolutions are untracked; a PR may be opened with an explicit tracking blocker when policy permits, but do not mark the evolution handoff complete.

A candidate qualifies for automatic registration only when it has a concrete user/business benefit, an independently deliverable outcome, a specific parent/source and no conflict with an approved decision. Pure speculation, implementation trivia and low-value edge cases do not qualify. Avoid issue spam: group closely related items and discard speculative low-value ideas with a brief reason. If qualification requires a new product direction, reprioritization, changed approved scope or a material architectural/security/contract decision, flag that decision to the owner rather than silently treating it as approved. Do not block the primary safe implementation on scheduling optional evolution work until its PR handoff; at that point ensure there is verified durable tracking or a visible blocker.

## Status and visibility

GitHub issue links and **future milestone assignments** are authoritative. After each successful checkpoint batch, the supervising agent notifies the owner with a short summary (what was created/reused, parent links, target milestones, and any blockers), without requiring approval or delaying eligible implementation. Avoid multiple noisy notifications for the same batch. The primary issue/PR should include a compact `Evolutions identified` section listing linked evolution issues, their future milestones and any candidates not yet persisted. Read status from live GitHub, not a static count or a second manually maintained backlog. A query like "what was deferred?" should group outstanding linked evolutions by milestone, distinguish proposed versus created and open versus completed, and show dependencies/next eligible step.

## Example (illustrative)

Current delivery: redeem a reward after verifying authenticated customer, sufficient balance and atomic point deduction; return a useful confirmation and safe failure on invalid requests.

Potential evolutions: historical analytics, bulk reporting or larger-volume read optimization, when those improvements are not necessary for current correctness. An unsafe double-redemption race is **not** an evolution to defer without a safe baseline.
