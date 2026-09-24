---
name: milestone-orchestrator
description: Run a GitHub milestone as one supervised workflow: audit and plan eligible issues, batch proposal approvals, schedule isolated implementation/review agents according to dependencies and conflicts, and continue to ready-to-merge or an explicit blocker. Use when asked to execute or resume a milestone.
---

# Milestone Orchestrator

Run the milestone, not just the next issue. Read repository instructions and ../../protocol/AI_WORKFLOW.md. Coordinate issue-audit, implement-issue, apply-issue, prepare-pr, pr-audit, architecture-audit when relevant, post-pr-audit, final-review and kaizen. Each worker must follow its skill gates.

## Invocation and operating modes

Input: a milestone URL (or unambiguous repository and milestone number), plus optional `merge_mode=manual` or `merge_mode=auto-if-green`. A single invocation should carry eligible work through the workflow and resume from durable state after interruption; never ask the owner to invoke a skill separately for each issue.

Default merge mode is `manual`. `auto-if-green` is an explicit per-run authorization to enable GitHub auto-merge only after all configured repository requirements and this workflow's review gates pass. Use it only for the milestone/run named by the owner. It never bypasses branch protection, required human reviews, required checks, or repository policy. If the merge method or eligibility cannot be established, stop that PR at `READY_TO_MERGE`. Never force-push, release, deploy, or tag as a side effect.

At startup, inspect available orchestration capabilities: ability to create fresh child sessions (OpenCode Task/subagent or equivalent), isolated worktrees, GitHub reads/writes, and repository-local test commands. Do not claim automation that the runtime cannot perform. If child sessions are unavailable, still inventory and prepare a consolidated plan/proposal batch, then report the precise missing capability; do not silently run Apply in the planning context. Use the available number of workers as a resource ceiling, not a fixed issue-count policy.

## One-run workflow

1. Refresh the live milestone, issues/comments/decisions, linked PRs, current code, OpenSpec changes, repository rules, and CI. Reconstruct existing progress and resume it; never duplicate a branch, OpenSpec change, or PR.
2. Build a dependency DAG with evidence links. Classify hard dependencies, coordination dependencies, likely file/module conflicts, and independent work. An open PR does not satisfy a hard dependency. Unknown edges block only affected issues; detect cycles. For backend-to-mobile work, require contract-handoff before the consumer begins.
3. Create a ledger for every issue. Preserve existing approvals, branches, proposals, implementations, PRs, reviews, and checks when their SHAs still match.
4. Schedule planning for all currently eligible issues. Use fresh planning child sessions and isolated worktrees when available. Independent issues may be planned in parallel, up to runtime capacity. Run issue-audit, then implement-issue (/opsx-explore, issue-ready, /opsx-proposal). Do not implement production code during planning. Record material questions as [QUESTION], mark that issue NEEDS_INPUT, and continue with unrelated eligible issues.
5. Once the current planning wave is complete, present one consolidated proposal review to the owner: issue, scope, trade-offs, dependencies, verification plan, artifact paths, exact immutable planning SHA, and questions/blockers. This is one approval checkpoint for the batch; approval must still identify each proposal SHA. The owner may approve all listed proposals or a subset. Do not start Apply for an unapproved proposal. Persist each explicit approval as a durable [DECISION] on its issue (or an accepted durable repository record). Any material proposal change invalidates that issue's approval and returns it to planning.
6. After the batch approval, schedule approved issues automatically. For each issue, start a genuinely fresh implementation child session with a compact durable handoff, verify the exact approved SHA and merged dependency commits, and run apply-issue plus official /opsx-apply. One issue gets one branch/worktree and one PR. Do not send the planning transcript as the only handoff.
7. Parallelize implementation only when all hard dependencies are merged, tasks are independent, expected code paths do not conflict, and each worker has an isolated worktree and fresh session. Determine concurrency from the dependency DAG, overlap risk, available agent/session capacity, CI resources, and repository limits. Serialize likely overlapping edits. Re-evaluate after each audit/diff; if a conflict appears, stop/reschedule the affected work safely. Never exceed runtime capacity or start dependent work early.
8. Each implementer runs focused tests and supported OpenSpec verification, completes approved tasks, strictly validates and archives the approved change on its feature branch, inspects archived artifacts and synchronized live specs, and invokes prepare-pr. Invoking prepare-pr authorizes only the scoped commit, non-force push, and PR creation described by that skill.
9. Run independent pr-audit and architecture-audit when relevant in fresh reviewer sessions. Address valid findings, rerun affected tests, then run final-pr-review, post-pr-audit, and independent final-review on the final PR head. Require configured CI and reviews to pass on the exact head SHA. While independent PRs wait for checks/reviews, schedule other eligible issues; do not schedule hard dependents until their prerequisite PR is merged.
10. With `merge_mode=manual`, report `READY_TO_MERGE` for the owner. With explicit `merge_mode=auto-if-green`, enable GitHub auto-merge for each PR only after its final audits pass and all current required checks and human review requirements are satisfied. Verify the resulting merge and issue closure; if auto-merge is disabled, blocked, or any signal is unknown/stale, stop that PR for the owner. After verified merge, run kaizen before scheduling hard dependents.
11. Continue the scheduler until all issues are merged/kaizen-complete, blocked on owner input/dependencies, or the runtime reaches an explicit capability/resource limit. Do not stop after one issue merely because it is the first in milestone order.

## Dynamic scheduling rules

- Hard prerequisites always determine order; issue number and milestone display order do not.
- Run independent planning or implementation work concurrently only with isolated worktrees. Start with the largest safe worker count supported by available capacity, then lower it for shared code paths, migration/contract coupling, limited test environments, provider limits, or rate limits.
- For uncertain overlap, inspect each issue's expected files/modules and current diffs. Prefer serialization when isolation or conflict risk is unclear.
- An unresolved product/architecture question blocks its issue and its dependents, not unrelated work.
- If runtime capacity is lower than safe parallelism, queue the remaining eligible work and continue automatically as workers finish.
- If a prerequisite PR is awaiting manual merge, report the dependent queue and continue independent branches where safe. Resume dependents automatically after verifying the prerequisite merge.

## Evidence ledger

GitHub issues/comments, approved decision records, committed OpenSpec artifacts, PRs, commits, review results, and checks on exact SHAs are durable. ai-memory is useful for handoff but is never an approval record. Build the ledger from live evidence after every interruption; a label, chat summary, or workflow-status heuristic cannot prove a gate.

| State | Minimum evidence |
|---|---|
| BACKLOG | Open milestone issue with no verified audit. |
| AUDITED | Current-code issue-audit report linked to the issue. |
| EXPLORING | Planning worker is exploring and refreshing questions/decisions. |
| SPECIFIED | issue-ready passed; proposal/spec/design/tasks validated and pinned to a commit. |
| AWAITING_APPROVAL | Exact planning SHA and material decisions shown in the batch review. |
| APPROVED | Explicit durable human approval for that issue and exact planning SHA; no material changes since. |
| IMPLEMENTING | Fresh child session verified the approved SHA and began apply-issue. |
| PR_OPEN | PR at known head SHA with issue linkage, test evidence, and archived/synchronized OpenSpec when applicable. |
| PR_AUDITED | Independent audits tied to current PR head; rerun after material push. |
| CI_GREEN | Required checks succeeded on current head with no pending/failing required jobs. |
| READY_TO_MERGE | Final audits pass and CI is green; awaiting owner merge in manual mode. |
| AUTO_MERGE_ENABLED | Explicit auto-if-green mode was requested and GitHub auto-merge is enabled without bypassing protections. |
| MERGED | PR merged and issue closure verified independently. |
| KAIZEN_DONE | Merged work reviewed by kaizen; record a concrete improvement or NO PROCESS CHANGE. |

Exceptional states: NEEDS_INPUT, NEEDS_REPLAN, BLOCKED, FAILED, RESOURCE_QUEUED. Preserve the last verified state, exact blocker, evidence and next automatic action. A closed issue without verified delivered/merged work is not MERGED; empty or stale checks are not CI_GREEN.

Record repository/milestone, issue, state, evidence links and SHAs, dependency gate, branch/worktree, spec approval, PR head/checks, merge mode, blocker and next action. Use existing issue/PR records and committed artifacts; do not create a competing source of truth.

## Per-issue invariants

- No implementation before the exact OpenSpec proposal revision is approved.
- Material behavior, data, authorization, architecture, public-contract, concurrency, or compatibility changes require a replan and renewed approval.
- One issue = one branch/worktree, one approved OpenSpec change, one PR, unless resuming compatible existing artifacts.
- Preserve unrelated local work; never use broad staging such as `git add .`.
- Re-run only checks invalidated by a change, but always run final-head audits and required checks after a material push.
- Never merge when the final head is unknown, CI is pending/failing, review findings remain, required human approvals are missing, or repository rules disallow it.
- Never auto-merge unless the owner explicitly selected `merge_mode=auto-if-green` for this run.

## Durable handoff

Use actual repository paths and commands, not this sample layout:

```yaml
repository: owner/name
milestone_url: https://github.com/owner/name/milestone/27
issue_url: https://github.com/owner/name/issues/123
base_ref: main
branch: issue-123-short-name
worktree: /absolute/path/to/issue-worktree
openspec_change: issue-123-short-name
planning_commit: <sha>
approved_decision_url: <issue-comment-or-other-durable-record>
approved_planning_sha: <same-sha>
artifact_paths: [<proposal-spec-design-task-paths>]
dependency_commits: [<merged-commit-shas>]
architecture_constraints: [<repository-instructions-or-decision-links>]
validation_commands: [<actual-supported-commands>]
merge_mode: manual
```

Reject a handoff when issue, approval SHA, worktree tree, or merged dependencies disagree. Never pass the planning transcript as the only evidence.

## Recovery and output

On interruption, refresh GitHub and Git, inspect partial work and PR state, preserve unrelated changes, and resume from the last verified gate. Do not rerun valid work. If a session fails, retry that issue within the configured attempt/resource limits; after repeated failure, mark FAILED and continue unrelated eligible issues. Never silently skip a blocked issue or claim a failed check passed.

Return a compact dashboard of all issues, dependency graph/order, active workers, states, evidence/SHAs, PRs/checks, blockers, merge mode, and the next automatic action. In manual mode, report all `READY_TO_MERGE` items together. In auto-if-green mode, report which PRs are queued for GitHub auto-merge and why any could not be queued. ghpending may aid triage; GitHub Project is a product view, not an execution gate.
