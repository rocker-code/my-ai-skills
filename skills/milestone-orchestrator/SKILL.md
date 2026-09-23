---
name: milestone-orchestrator
description: Orchestrate a GitHub milestone issue by issue with OpenSpec, separate planning, implementation and verification subagent sessions, durable handoffs, dependency gates and one PR per issue. Use when asked to implement a milestone with subagents.
metadata:
  category: workflow
  methodology: openspec-first
---

# Milestone Orchestrator

Coordinate work; delegate exploration, proposal, implementation and verification. Do not edit production code as the orchestrator. Use the repository's existing `issue-explore`, `issue-ready`, `openspec-workflow`, `implement-issue`, `prepare-pr` and review skills. Read `../../protocol/AI_WORKFLOW.md` and repository instructions before starting.

Input: a GitHub milestone URL (or an unambiguous repository + milestone number). Output: a dependency plan, per-issue state and links to changes/PRs. This skill does not itself grant a runtime the ability to create a fresh session or a subagent. Check those capabilities first. If the runtime cannot create a genuinely isolated implementation session, stop before apply with `BLOCKED — fresh session unavailable` and provide the handoff; never continue in the planner's session or claim isolation.

## Inventory and scheduling

1. Fetch the live milestone and all its issues, including open/closed state, comments, linked PRs and latest decisions. Inspect applicable code, OpenSpec changes and repository instructions. Refresh live data at each issue boundary.
2. Classify each issue: done/merged, existing PR (route to review), in progress (resume), eligible, blocked by decisions, or blocked by dependencies. Identify cross-repository contracts and explicit issue/PR dependencies. Do not infer a business decision from milestone ordering.
3. Show the execution plan before coding: issue, dependency, existing branch/change/PR, readiness and proposed order. Start with `max_parallel_issues = 1`. Increase concurrency only after explicit user direction and proof of independent code paths/worktrees and dependency safety.
4. Default to one issue = one OpenSpec change = one branch/worktree = one implementation session = one PR. Reuse existing artifacts and PRs. Do not duplicate them or bundle several issues simply because they share a milestone. If a dependency needs merged code, wait for that merge; an opened PR does not satisfy it.
5. Check that the worktree's base contains required dependencies. Do not silently stack a dependent PR on an unmerged branch. Surface any base or sequencing decision.

GitHub issues, approved comments, OpenSpec artifacts, commits and PRs are durable state. A local progress summary is only a cache. After interruption, reconstruct from these sources before choosing the next transition.

## State machine and gates

`PENDING → EXPLORING → PLANNING → READY → IMPLEMENTING → VERIFYING → PR_CREATED → REVIEW → DONE`

Exceptional states: `NEEDS_INPUT` (blocking question), `NEEDS_REPLAN` (approved contract conflicts with evidence), `BLOCKED` (dependency/tool/permissions), `FAILED` (execution error). A PR is not DONE until repository review/merge rules are satisfied. Do not merge or close issues automatically without the requested workflow's authorization.

For each eligible issue:

1. Allocate or reuse an issue-specific branch/worktree and OpenSpec change. Keep the worktree after planning so its tracked artifacts are available to later sessions.
2. Spawn a planning subagent. It refreshes the issue and comments, runs the repository's official `/opsx-explore <issue-url>` with `issue-explore`, records material questions as `[QUESTION]`, and stops at `NEEDS_INPUT` if unanswered. After approved `[DECISION]` comments, explore again and pass `issue-ready`. Run `/opsx-proposal` using the repository's OpenSpec version and review the resulting proposal, specs, design and tasks.
3. Planning gate: verify that `proposal.md`, applicable `specs/`, `design.md` and `tasks.md` exist and agree with the issue, latest decisions, dependency baseline and acceptance criteria. Run `openspec status --change <name>` and the repository's supported OpenSpec validation command; if syntax differs, discover the installed commands and report the actual commands/results. A tooling failure or missing artifact blocks the gate. Obtain proposal approval when required by the user or repository policy.
4. Commit the planning artifacts to the issue branch so the next session can read the exact version. Capture their commit SHA. End the planning subagent; do not fork its conversation or pass its reasoning.
5. Spawn a **new implementation session** with no planning conversation. Supply only the handoff fields below. It must read the live issue, repository instructions and the committed OpenSpec artifacts at the pinned commit, then run `/opsx-apply <change-name>` and targeted tests. `implement-issue` governs implementation, but its discovery/proposal checkpoints are already satisfied and must not be repeated without a reason.
6. End that session. Spawn an independent verification session with the issue, decisions, pinned plan, implementation commit and diff. Run the repository's `/opsx-verify` if supported, review issue ↔ OpenSpec ↔ diff ↔ tests, run relevant checks and report PASS/FAIL/NOT RUN with evidence. Never claim a command ran when unavailable.
7. On PASS, use `prepare-pr` to create or reuse one PR with issue linkage, OpenSpec change, actual test results and outstanding risks. Then route to independent review. Do not advance a dependent issue past its dependency gate.

The roles are logical only if the runtime can provide isolated sessions; otherwise stop at the gate. A retry after replan uses a **new** implementation session pinned to the revised artifacts.

## Handoff contract

Pass a compact, durable record to the implementation session, without planner transcript, speculative alternatives, or unstated assumptions:

```yaml
repository: owner/name
issue_url: https://github.com/owner/name/issues/123
base_ref: main
branch: issue-123-short-name
worktree: /absolute/path/to/issue-worktree
openspec_change: issue-123-short-name
planning_commit: <sha>
artifact_paths:
  - openspec/changes/issue-123-short-name/proposal.md
  - openspec/changes/issue-123-short-name/specs/
  - openspec/changes/issue-123-short-name/design.md
  - openspec/changes/issue-123-short-name/tasks.md
dependency_commits: [<sha>]
architecture_constraints: [<document or approved decision link>]
validation_commands: [<commands established in planning>]
```

Paths are examples; resolve the repository's actual OpenSpec layout. Verify that the worktree HEAD contains `planning_commit` and dependency commits before apply. The implementation session must report its implementation SHA, tests and one of `READY FOR VERIFICATION`, `NEEDS_REPLAN`, `BLOCKED`, or `FAILED`.

The implementer treats approved artifacts as the contract. If it finds a material issue in behavior, architecture, security, data or scope, it stops affected implementation and returns `NEEDS_REPLAN` with code evidence, affected artifact and proposed change. Send that evidence to a fresh planning pass, revise the issue/decision and artifacts, validate and commit them, then spawn a new implementation session. Small implementation defects can return to an implementation session without changing the contract.

## Reporting and recovery

Report a compact ledger after each transition: issue, state, dependency gate, branch/worktree, OpenSpec change and pinned SHA, checks, PR URL, blocker and next action. Never mark a blocked issue as completed or skip it silently. If a session crashes, refresh GitHub and Git before retrying, inspect partial changes, and resume at the last verified gate; do not spawn duplicate PRs or mix unrelated worktrees.
