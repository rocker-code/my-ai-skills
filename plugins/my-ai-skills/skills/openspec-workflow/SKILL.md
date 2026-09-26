---
name: openspec-workflow
description: Enforce the required OpenSpec contract across planning, implementation and PR correction. Use from implement-issue, apply-issue and address-pr-review for official proposal, exact-revision approval, Apply, verification, strict validation and archive; do not bypass OpenSpec or replace its CLI commands.
---

# OpenSpec Contract

Own the OpenSpec-specific commands and evidence gates. `implement-issue` owns issue planning, `apply-issue` owns implementation in a fresh session, and `github-resolution` owns PR corrections. This skill defines the contract each of them must enforce, rather than acting as another end-to-end issue orchestrator.

## Locate and plan

Read the live issue, approved `[DECISION]` comments and repository instructions. Find an existing OpenSpec change by issue, branch and capability before creating one; do not duplicate it. Run the installed official `/opsx-explore` with `issue-explore` before proposal, and again after material decisions. Require `issue-ready` before the official `/opsx-proposal`.

Build proposal, specifications/scenarios, design and tasks against the actual repository: behavior and errors, public contracts, authorization, state, data/migrations, concurrency, compatibility, tests, cleanup and boundaries. Validate the proposal with the installed official OpenSpec command. Record its exact revision/commit and obtain explicit human approval for that revision before any production implementation. An approval for an older materially different revision does not carry forward.

## Apply and close out

Run the official `/opsx-apply` only in the fresh implementation session after approval. Verify the approved scenarios against code and proving tests. Complete tasks and run the installed official implementation verifier when available; otherwise record an explicit requirement/scenario → code → test matrix and mark automated verification NOT RUN. Run strict validation on the active change using the installed version's supported command.

Archive on the issue feature branch only after implementation, tests, verification and strict validation pass. Use the installed official archive command, sync only the approved delta into live `openspec/specs/`, and inspect both archived artifacts and synchronized live specs in the same PR. Do not create a separate archive-only PR or defer routine archival until after merge.

If new evidence or PR feedback requires material behavior, data, authorization, architecture, concurrency or public-contract changes, stop affected implementation, update issue decisions and proposal/spec/design/tasks, validate and obtain approval of the revised exact revision before resuming. Implementation-only fixes that preserve the approved contract need code/tests, not speculative spec edits. Never silently rewrite archived approved behavior.

If OpenSpec is missing or an official command is unavailable, report the precise blocker; do not replace an absent contract with an agent-generated retrospective spec or invent commands. Read the installed CLI's help and repository setup to recover supported usage.
