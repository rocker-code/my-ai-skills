---
name: milestone-orchestrator
description: Coordinate a GitHub milestone issue by issue through issue-audit, approved OpenSpec proposals, fresh implementation sessions, independent PR audits, CI and manual merge. Use when asked to execute a milestone with subagents, track dependencies and resume interrupted work.
---

# Milestone Orchestrator

Coordinate; do not edit production code as the orchestrator. Read repository instructions and ../../protocol/AI_WORKFLOW.md. Use issue-audit, implement-issue, apply-issue, prepare-pr, pr-audit, architecture-audit when relevant, post-pr-audit, final-review and kaizen. Do not reinterpret a skill's gate.

Input: a milestone URL or unambiguous repository and milestone number. Output: dependency plan, evidence-backed per-issue ledger, blockers and next action. Calling this skill does not itself create fresh sessions, subagents, worktrees, or GitHub permissions. Check capabilities before making promises. If there is no fresh implementation session, stop before Apply with a durable handoff.

## Inventory and order

1. Refresh the milestone, all issues/comments/decisions, linked PRs and their current state, relevant code, repository rules and OpenSpec changes. Reconstruct existing work before starting a new branch or change. Never duplicate a PR.
2. Build a dependency graph with links to the issue/PR or contract that proves each edge. Classify hard prerequisites (merged backend contract or schema), coordination dependencies and independent work. An open PR does not satisfy a hard prerequisite. Mark undocumented or contradictory edges UNKNOWN; ask for a decision instead of treating issue number or milestone order as a dependency. Detect cycles and block the affected issues.
3. Show an inventory: issue, evidence for dependencies, current artifact/PR, inferred state, blocker and suggested order. Choose an unblocked issue by approved priority when present; otherwise use impact/risk and a stable issue-number tie-breaker. Recheck the graph when an audit or proposal discovers another dependency. For backend → mobile changes, use contract-handoff before the consumer moves forward.
4. Start with max_parallel_issues = 1. Each issue has its own OpenSpec change, branch/worktree, planning session, fresh apply session and PR, unless existing compatible artifacts should be resumed. Increase parallelism only with explicit user direction and verified independent dependencies, code paths and isolated worktrees.

## Reconstruct state from evidence

GitHub issues/comments, approved decisions, OpenSpec artifacts committed on a branch, PRs, commits and CI on an exact SHA are durable. ai-memory is a useful handoff supplement, never an approval record. Build this ledger afresh after each interruption; a label, conversation summary or the workflow-status helper alone cannot prove a gate.

| State | Minimum evidence to enter |
|---|---|
| BACKLOG | Open milestone issue with no verified audit. |
| AUDITED | Current-code issue-audit report linked to issue; unresolved gaps recorded. |
| EXPLORING | Explore work in progress; latest questions/decisions refreshed. |
| SPECIFIED | issue-ready passed; proposal/spec/design/tasks validated and pinned to a commit. |
| AWAITING_APPROVAL | Exact planning SHA and material decisions presented to the owner. |
| APPROVED | Explicit human approval recorded for that issue and exact planning SHA; no material changes since. |
| IMPLEMENTING | A genuinely new session verified the approved SHA and started apply-issue. |
| PR_OPEN | PR at known head SHA with issue/OpenSpec linkage and actual test evidence. |
| PR_AUDITED | Independent pr-audit findings tied to current PR head; rerun after a material push. |
| CI_GREEN | Required checks succeeded on the current head SHA, with no pending/failing required jobs. |
| READY_TO_MERGE | post-pr-audit and final-review pass on current head, feedback resolved, CI green; awaiting owner decision. |
| MERGED | PR merged and issue closed per repository policy; verify both independently. |
| KAIZEN_DONE | Merged work reviewed by kaizen; record concrete change or NO PROCESS CHANGE. |

Exceptional states: NEEDS_INPUT (material unresolved decision), NEEDS_REPLAN (approved contract invalidated), BLOCKED (dependency or missing capability), FAILED (execution/check error). Preserve the last verified state and record the exact blocker and next action. A closed issue without evidence of delivered/merged work is not automatically MERGED; an empty or stale check list is not CI_GREEN.

Maintain a compact ledger after each transition with repository/issue, state, evidence links and SHAs, dependency gate, branch/worktree, spec change/approval, PR head/checks, blocker and next action. Store durable decisions or summaries in existing issue/PR comments or committed artifacts according to repository conventions; do not create a second authoritative database.

## Per-issue gates

1. Run issue-audit against live code. Route NEEDS REFINEMENT into a question/decision; leave other eligible issues visible. Then run implement-issue: official /opsx-explore, re-explore after material decisions, issue-ready and /opsx-proposal. No production code in the planning session.
2. Validate the complete OpenSpec change against the issue, architecture and dependency baseline using commands supported by the installed version. Commit the proposal artifacts to the issue branch and capture the planning SHA. Show scope, trade-offs, contracts, risks and verification plan. Stop at AWAITING_APPROVAL until the human explicitly approves this exact revision. Record the approval in a durable issue/PR decision. Changes that materially alter the proposal invalidate that approval.
3. End planning. Launch a truly separate implementation agent session without its planning transcript (not a fork carrying the same conversation). Supply the compact handoff below. The implementer independently checks the committed SHA, approval and dependency commits, then uses apply-issue and the official /opsx-apply. If the runtime cannot launch that session, return BLOCKED with the handoff; do not implement in the planning session. A replan requires approval and a new apply session.
4. Run targeted tests and supported OpenSpec verification. prepare-pr creates/reuses a PR with requirement → implementation → test traceability. Use an independent reviewer session for pr-audit, plus architecture-audit when boundaries change. Address valid findings, rerun affected tests and audits on the new head. The implementer's self-review cannot be the sole review.
5. Run final-pr-review, post-pr-audit and independent final-review on the final head. Require all configured checks green on that same SHA; unknown, skipped when required, stale or pending checks are not green. Move to READY_TO_MERGE and present evidence to the owner. Never merge, enable auto-merge, close the issue or tag/release as a side effect of orchestrating. After the owner merges, verify PR and issue states and run kaizen before scheduling a hard dependent issue.

## Durable handoff

Use the actual repository paths and commands; do not assume this sample layout:

```yaml
repository: owner/name
issue_url: https://github.com/owner/name/issues/123
base_ref: main
branch: issue-123-short-name
worktree: /absolute/path/to/issue-worktree
openspec_change: issue-123-short-name
planning_commit: <sha>
approved_decision_url: <issue-comment-or-other-durable-record>
approved_planning_sha: <same-sha>
artifact_paths: [<actual-proposal-spec-design-task-paths>]
dependency_commits: [<merged-commit-shas>]
architecture_constraints: [<AGENTS.md-or-decision-links>]
validation_commands: [<actual-supported-commands>]
```

Reject a handoff when issue, approval SHA, checked-out tree or merged dependencies disagree. Never pass the planning transcript as the only evidence.

## Recovery and completion

If a session fails, refresh GitHub and Git, inspect partial files and PR state, preserve unrelated changes, then resume at the last verified gate. Rerun only validations invalidated by new changes, but rerun final-head checks after material changes. On a contract conflict, stop affected work, update the issue and spec, request approval again and create a fresh apply session. Never silently skip a blocked issue, start a dependent issue early or claim a failed check passed.

Return the complete ledger, the issue selected now, dependencies/blocked issues, actual checks and next owner decision. After MERGED, mark KAIZEN_DONE even when kaizen finds no justified process edit. ghpending may inform what needs attention but is optional; GitHub Project remains a product view, not an execution gate.
