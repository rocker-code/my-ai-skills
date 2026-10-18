---
name: milestone-orchestrator
description: Run one GitHub issue, a repository work queue or a specific milestone as one supervised workflow that audits eligible issues and PRs, batches OpenSpec proposal reviews, schedules isolated workers by dependencies, and continues through verified merge or an explicit blocker. Use for "cuide da fila deste projeto", "cuide da fila deste projeto, sem merges", "cuide deste milestone", or "cuide da issue <issue URL>".
---

# Issue, Work Queue and Milestone Orchestrator

Run the entire selected scope: one issue, a project queue or a milestone. Read repository instructions and [the AI workflow protocol](references/AI_WORKFLOW.md). Coordinate issue-audit, implement-issue, apply-issue, prepare-pr, pr-audit, architecture-audit when relevant, github-resolution and kaizen. Delegate per-PR correction, final independent audit and merge to github-resolution; this skill owns the milestone dependency scheduler. Each worker must follow its skill gates.

## Invocation and operating modes

Accept these natural requests without requiring a mode parameter:
- "Cuide da fila deste projeto": use the single repository established by the current checkout/remote or explicit conversation context; inventory all open PRs and open issues in that repository.
- "Cuide da fila deste projeto, sem merges": use the same queue with `merge_mode=manual` for this run.
- "Cuide deste milestone": use the supplied milestone URL or a unique milestone identified by the current request/context. Do not guess among multiple candidates; request only the missing milestone identifier when needed.

- "Cuide da issue: <GitHub issue URL>" or "Cuide desta issue: <GitHub issue URL>": use `scope=single_issue`, selecting exactly that issue and its verified linked implementation PR. A number is sufficient only when the repository is uniquely established; ask only for a missing/ambiguous identifier.
- "Cuide da issue: <GitHub issue URL>, sem merge" or "sem merges": use the same single-issue scope with `merge_mode=manual`.

A repository URL/name is sufficient if there is no local checkout. Never silently widen a named milestone to the whole repository or another repository's queue. A single invocation carries eligible work through the workflow and resumes from durable state after interruption; never ask the owner to invoke another skill for each issue.

Default merge mode is `auto-if-green` under the owner's standing instruction for this workflow. A direct "do not merge" or `merge_mode=manual` request overrides it for the selected run. The default authorizes merge only after all configured repository requirements and this workflow's review gates pass. Apply this only to the selected single issue, repository queue or milestone run. It never bypasses branch protection, required human reviews, required checks, or repository policy. If the merge method or eligibility cannot be established, stop that PR at `READY_TO_MERGE`. Never force-push, release, deploy, or tag as a side effect.

At startup, inspect available orchestration capabilities: ability to create fresh child sessions (OpenCode Task/subagent or equivalent), isolated worktrees, GitHub reads/writes, and repository-local test commands. Do not claim automation that the runtime cannot perform. If child sessions are unavailable, still inventory and prepare a consolidated plan/proposal batch, then report the precise missing capability; do not silently run Apply in the planning context. Use the available number of workers as a resource ceiling, not a fixed issue-count policy.

## Single-issue scope

For `scope=single_issue`, run the same gates and workers below with a one-ticket ledger. Refresh the issue, comments, decisions, code, existing OpenSpec artifacts, linked PRs and current checks. Verify repository identity before any write; an explicit issue URL determines the target repository, so a different checkout requires the correct checkout/worktree or a capability blocker. A PR URL is not an issue identifier.

Read related issues and prerequisite PRs only to establish dependency/contract evidence. Do not implement, modify or merge prerequisites, siblings, other milestone issues or unrelated PRs without an explicit scope expansion. If a hard prerequisite is unmerged or its contract is unfrozen, report `BLOCKED` with evidence and the exact prerequisite; do not start dependent implementation.

Resume the last verified gate. For an existing implementation PR, independently audit its current head and hand it to `github-resolution`; do not recreate the plan, branch or PR when their evidence remains valid. If multiple candidate PRs exist, verify which delivers this issue and report unresolved ambiguity instead of selecting or merging every linked PR. A closed issue does not authorize reopening or new work: verify existing delivery and report its state; if closed without delivered work, report that fact and request a scope decision.

For a new eligible issue, run issue-audit, implement-issue, exact-revision proposal review/validation, fresh-session apply-issue, tests/verification/archive, prepare-pr, independent pr-audit (architecture-audit when relevant), then github-resolution and independent post-pr-audit. Continue automatically through confirmed merge/closure and kaizen in auto-if-green mode, or `READY_TO_MERGE` in manual mode. Do not ask the owner to invoke each skill. Material unanswered questions and missing runtime capabilities remain explicit blockers. Carry the existing automatic CI performance hooks.

## One-run workflow

1. Resolve the unique repository and selected scope. Refresh all open issues and PRs in the project queue, the selected milestone's issues and their linked PRs, or exactly the selected issue and its verified linked PR; read comments/decisions, current code, OpenSpec changes, repository rules and CI. Skip drafts from implementation with reasons; audit eligible existing PRs before scheduling new issue work. Reconstruct existing progress and resume it; never duplicate a branch, OpenSpec change, or PR.
2. Build a dependency DAG with evidence links. Classify hard dependencies, coordination dependencies, likely file/module conflicts, and independent work. An open PR does not satisfy a hard dependency. Unknown edges block only affected issues; detect cycles. For cross-repository producer-to-consumer work, run contract-handoff during planning before releasing the consumer proposal and again in final-freeze mode after producer delivery, before consumer implementation. A missing contract capability is a hard dependency for only the affected consumer issues.
3. Create a ledger for every issue and pre-existing PR in scope. Preserve existing decisions, validated proposal revisions, branches, implementations, PRs, reviews, and checks when their SHAs still match.
4. Schedule planning for all currently eligible issues. Use fresh planning child sessions and isolated worktrees when available. Independent issues may be planned in parallel, up to runtime capacity. Run issue-audit, then implement-issue (/opsx-explore, issue-ready, /opsx-propose). Do not implement production code during planning. Do not create/release a dependent consumer proposal until the required producer capability is delivered in merged code or verified at an explicit immutable producer ref and contract-handoff passes. An open producer issue or planned schema is not delivery; mark only affected consumer issues CONTRACT_BLOCKED and continue eligible producer/unrelated work. Record material questions as [QUESTION], mark that issue NEEDS_INPUT, and continue with unrelated eligible issues.
5. Collect each planning worker's review against the issue, latest [DECISION] comments, current code, architecture, requirements, tests, dependencies and OpenSpec scenarios. Verify the official validation result and immutable proposal SHA; use an independent planning reviewer for material boundaries when available if not already completed. Reuse matching evidence instead of rerunning unchanged validation. Publish a consolidated progress summary without waiting for a routine owner approval. Questions that require a new product or architecture decision mark only affected issues NEEDS_INPUT; failed validation returns them to planning. A material proposal change invalidates the prior review and must be reviewed again.
6. Schedule validated, decision-complete proposals automatically. For each issue, start a genuinely fresh implementation child session with a compact durable handoff, verify the exact reviewed proposal SHA, validation evidence and merged dependency commits. For dependent consumers, rerun contract-handoff in final-freeze mode against merged producer code/schema and require CONTRACT FROZEN before apply-issue plus official /opsx-apply. One issue gets one branch/worktree and one PR. Do not send the planning transcript as the only handoff.
7. Parallelize implementation only when all hard dependencies are merged, tasks are independent, expected code paths do not conflict, and each worker has an isolated worktree and fresh session. Determine concurrency from the dependency DAG, overlap risk, available agent/session capacity, CI resources, and repository limits. Serialize likely overlapping edits. Re-evaluate after each audit/diff; if a conflict appears, stop/reschedule the affected work safely. Never exceed runtime capacity or start dependent work early.
8. Each implementer runs focused tests and supported OpenSpec verification, completes validated tasks, strictly validates and archives the validated change on its feature branch, inspects archived artifacts and synchronized live specs, and invokes prepare-pr. Invoking prepare-pr authorizes only the scoped commit, non-force push, and PR creation described by that skill.
9. Run independent pr-audit and architecture-audit when relevant in fresh reviewer sessions. Hand each audited PR to github-resolution with the verified issue/proposal SHA and this run's merge mode. That skill coordinates address-pr-review corrections, refreshed audit, independent post-pr-audit and exact-head CI. While PRs wait for checks/reviews, schedule other eligible issues; do not schedule hard dependents until their prerequisite PR is merged.
10. With `merge_mode=manual`, collect the per-PR `READY_TO_MERGE` results for the owner. With the default `merge_mode=auto-if-green`, let github-resolution/post-pr-audit perform or queue the eligible merge; verify actual merge and issue closure before running kaizen or scheduling hard dependents. If GitHub cannot enforce applicable gates or any signal is unknown/stale, report that PR's blocker.
11. Continue the scheduler until all issues are merged/kaizen-complete, blocked on owner input/dependencies, or the runtime reaches an explicit capability/resource limit. Do not stop after one issue merely because it is the first in milestone order.

## Dynamic scheduling rules

- Hard prerequisites always determine order; issue number and milestone display order do not.
- Run independent planning or implementation work concurrently only with isolated worktrees. Start with the largest safe worker count supported by available capacity, then lower it for shared code paths, migration/contract coupling, limited test environments, provider limits, or rate limits.
- For uncertain overlap, inspect each issue's expected files/modules and current diffs. Prefer serialization when isolation or conflict risk is unclear.
- An unresolved product/architecture question blocks its issue and its dependents, not unrelated work.
- If runtime capacity is lower than safe parallelism, queue the remaining eligible work and continue automatically as workers finish.
- If a prerequisite PR is awaiting manual merge, report the dependent queue and continue independent branches where safe. Resume dependents automatically after verifying the prerequisite merge.

## Evidence ledger

GitHub issues/comments, approved product decision records, committed OpenSpec artifacts, PRs, commits, review results, and checks on exact SHAs are durable. ai-memory is useful for handoff but is never a proposal validation or decision record. Build the ledger from live evidence after every interruption; a label, chat summary, or workflow-status heuristic cannot prove a gate.

| State | Minimum evidence |
|---|---|
| BACKLOG | Open issue or PR in the selected queue with no verified audit. |
| AUDITED | Current-code issue-audit report linked to the issue. |
| EXPLORING | Planning worker is exploring and refreshing questions/decisions. |
| SPECIFIED | issue-ready passed; proposal/spec/design/tasks created and pinned to a commit, pending review. |
| PLAN_REVIEW | Exact proposal SHA undergoing traceability and official validation. |
| PLAN_VALIDATED | Exact proposal SHA, review evidence and official validation recorded; no unresolved material decision. For cross-repository consumers, contract design review passed. |
| CONTRACT_BLOCKED | Consumer has an evidenced missing/unfrozen producer capability; exact producer dependency, scenario gap and next action are recorded. Independent work continues. |\n| IMPLEMENTING | Fresh child session verified the validated proposal SHA and began apply-issue; dependent consumers also have CONTRACT FROZEN evidence. |
| PR_OPEN | PR at known head SHA with issue linkage, test evidence, and archived/synchronized OpenSpec when applicable. |
| PR_AUDITED | Independent audits tied to current PR head; rerun after material push. |
| CI_GREEN | Required checks succeeded on current head with no pending/failing required jobs. |
| READY_TO_MERGE | Final audits pass and CI is green; awaiting owner merge in manual mode. |
| AUTO_MERGE_ENABLED | Auto-if-green mode applies and GitHub auto-merge is enabled without bypassing protections. |
| MERGED | PR merged and issue closure verified independently. |
| KAIZEN_DONE | Merged work reviewed by kaizen; record a concrete improvement or NO PROCESS CHANGE. |

Exceptional states: NEEDS_INPUT, NEEDS_REPLAN, BLOCKED, FAILED, RESOURCE_QUEUED. Preserve the last verified state, exact blocker, evidence and next automatic action. A closed issue without verified delivered/merged work is not MERGED; empty or stale checks are not CI_GREEN.

Record repository and selected scope (`single_issue`, `project_queue` or `milestone`), issue/PR, state, evidence links and SHAs, dependency gate, branch/worktree, proposal revision/review evidence, PR head/checks, merge mode, blocker and next action. Use existing issue/PR records and committed artifacts; do not create a competing source of truth.

## Per-issue invariants

- No implementation before the exact OpenSpec proposal revision is reviewed, officially validated and pinned.
- Material behavior, data, authorization, architecture, public-contract, concurrency, or compatibility changes require a new plan review and validation; seek the owner when a new decision cannot be derived from existing decisions and project policy.
- One issue = one branch/worktree, one validated OpenSpec change, one PR, unless resuming compatible existing artifacts.
- Preserve unrelated local work; never use broad staging such as `git add .`.
- Re-run only checks invalidated by a change, but always run final-head audits and required checks after a material push.
- Never merge when the final head is unknown, CI is pending/failing, review findings remain, required repository human reviews are missing, or repository rules disallow it.
- Use the owner's standing auto-if-green instruction by default for the selected run; never merge after an explicit manual-mode or no-merge instruction.

## Durable handoff

Use actual repository paths and commands, not this sample layout:

```yaml
repository: owner/name
scope: single_issue # or project_queue / milestone
# Include milestone_url only for scope: milestone.
issue_url: https://github.com/owner/name/issues/123
base_ref: main
branch: issue-123-short-name
worktree: /absolute/path/to/issue-worktree
openspec_change: issue-123-short-name
planning_commit: <sha>
decision_urls: [<applicable-issue-decisions-if-any>]
validated_proposal_sha: <planning-commit-sha>
proposal_review_evidence: <durable-review-record>
openspec_validation: <exact-command-and-result>
artifact_paths: [<proposal-spec-design-task-paths>]
dependency_commits: [<merged-commit-shas>]
architecture_constraints: [<repository-instructions-or-decision-links>]
validation_commands: [<actual-supported-commands>]
merge_mode: auto-if-green
```

Reject a handoff when issue, validated proposal SHA, review/validation evidence, worktree tree, or merged dependencies disagree. Never pass the planning transcript as the only evidence.

## Recovery and output

On interruption, refresh GitHub and Git, inspect partial work and PR state, preserve unrelated changes, and resume from the last verified gate. Do not rerun valid work. If a session fails, retry that issue within the configured attempt/resource limits; after repeated failure, mark FAILED and continue unrelated eligible issues. Never silently skip a blocked issue or claim a failed check passed.

Return a compact dashboard of the selected scope's issues and PRs, dependency graph/order, active workers, states, evidence/SHAs, checks, blockers, merge mode, and the next automatic action. In manual mode, report all `READY_TO_MERGE` items together. In auto-if-green mode, report which PRs are queued for GitHub auto-merge and why any could not be queued. ghpending may aid triage; GitHub Project is a product view, not an execution gate.

## Automatic CI performance routing

Read [the CI performance protocol](references/CI_PERFORMANCE.md). Carry automatic `ci-performance-audit`/`optimize-ci` routing in relevant worker handoffs. Permit independent planning, but serialize optimization experiments sharing workflows, databases/sandboxes, runner resources or measured workload unless isolation and contention are explicitly accounted for. Reconstruct baseline/candidate evidence from the ledger; do not require the owner to invoke another skill or add an unconditional benchmark job.
