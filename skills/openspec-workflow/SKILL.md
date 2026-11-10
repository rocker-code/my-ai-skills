---
name: openspec-workflow
description: Enforce the required OpenSpec contract across planning, implementation and PR correction. Use from implement-issue, apply-issue and address-pr-review for official proposal, exact-revision validation, Apply, verification, strict validation and archive; do not bypass OpenSpec or replace its CLI commands.
---

# OpenSpec Contract

Own the OpenSpec-specific commands and evidence gates. `implement-issue` owns issue planning, `apply-issue` owns implementation in a fresh session, and `github-resolution` owns PR corrections. This skill defines the contract each of them must enforce, rather than acting as another end-to-end issue orchestrator.

Command names follow OpenSpec's per-agent convention: `/opsx-explore`, `/opsx-propose`, `/opsx-apply` and `/opsx-archive` in Codex and OpenCode; `/opsx:explore`, `/opsx:propose`, `/opsx:apply` and `/opsx:archive` in Claude Code. Use the form installed for the current agent.

## Locate and plan

Read the live issue, approved `[DECISION]` comments and repository instructions. Find an existing OpenSpec change by issue, branch and capability before creating one; do not duplicate it. Run the installed official `/opsx-explore` with `issue-explore` before proposal, and again after material decisions. Require `issue-ready` before the official `/opsx-propose`.

Build proposal, specifications/scenarios, design and tasks against the actual repository: behavior and errors, public contracts, authorization, state, data/migrations, concurrency, compatibility, tests, cleanup and boundaries. Validate the proposal with the installed official OpenSpec command. Pin its exact revision/commit and record a requirement/scenario → implementation plan → proving test matrix, plus a review of architecture, data, contracts and risk. Request an independent reviewer for material boundary changes when available; otherwise record the inline review. If validation and review pass with no unresolved material decision, hand off automatically to a fresh Apply session. Do not treat an older revision's review as evidence for a materially changed proposal.

## Apply and close out

Run the official `/opsx-apply` only in the fresh implementation session after validating the pinned proposal and review evidence. Verify the pinned scenarios against code and proving tests. Complete tasks and run the installed official implementation verifier when available; otherwise record an explicit requirement/scenario → code → test matrix and mark automated verification NOT RUN. Run strict validation on the active change using the installed version's supported command.

Archive on the issue feature branch only after implementation, tests, verification and strict validation pass. Use the installed official archive command, sync only the validated delta into live `openspec/specs/`, and inspect both archived artifacts and synchronized live specs in the same PR. Do not create a separate archive-only PR or defer routine archival until after merge.

If new evidence or PR feedback requires material behavior, data, authorization, architecture, concurrency or public-contract changes, stop affected implementation, update the issue and proposal/spec/design/tasks, review and validate the revised exact revision before resuming. Ask the owner when the new decision cannot be derived from existing approved decisions and project policy. Implementation-only fixes that preserve the validated contract need code/tests, not speculative spec edits. Never silently rewrite archived validated behavior.

If OpenSpec is missing or an official command is unavailable, report the precise blocker; do not replace an absent contract with an agent-generated retrospective spec or invent commands. Read the installed CLI's help and repository setup to recover supported usage.

## Proportionate test coverage

Read [the test strategy](references/TEST_STRATEGY.md). Use the existing requirement/scenario matrix to record concrete risks, proving layers and existing/new tests. Plan representative scenarios with deeper coverage for affected high-risk behavior. A proving test can satisfy multiple rows; do not require a separate integrated and GraphQL matrix for the same rule. Retain every explicit validated obligation.
