# Design — issue #61

## Verified context

Inspected `main` at `fce9a3cd02273f8525e463f623454ce251a865ee` and relevant blobs:
- `skills/milestone-orchestrator/SKILL.md` (blob `1ce9530f7ec4551c40f83d68f251701c4c5ce157`) already requires evidence-based resume.
- `protocol/WORKTREES.md` (blob `81adfc71f9ab304c6473011bd98aefa44d3e9b9b`) defines exclusive ownership, recovery and drift.
- `scripts/worktree-reservation` (blob `64d07bf7452f6a7b5190497cfd2c2da7305dc4bc`) implements these controls.
- `scripts/install-global` creates managed global OpenCode guidance and symlinks all discovered skills.

There was no executed end-to-end OpenCode recovery test available during authoring; the test obligation remains explicit.

## Decision

Use **one skill as entrypoint** and keep `milestone-orchestrator` as scheduler. Do not duplicate the ledger or introduce a second recovery state machine. The skill works read-only until issue/milestone scope, durable evidence and safe worktree ownership have been established; then it delegates to the existing gates.

### Reconciliation order

1. Resolve checkout/project and unique selected scope.
2. Inventory GitHub state, Git worktrees, staged/unstaged/untracked content, OpenSpec and accessible execution evidence.
3. Classify last verified gate versus unknown, blocked or conflicting states; never assume interrupted tests passed.
4. Verify stopped-writer evidence and reservation before effects; if ambiguous, retain and report blocker for the affected issue only.
5. Delegate the **same** issue/milestone, worktree, proposal and PR to the existing orchestrator.

### Tradeoffs and limits

Natural-language routing is guidance to the agent, not a native OpenCode crash hook. It cannot restart background processes automatically or recover uncommitted data from a lost disk. A session can request recovery without an earlier transcript; the evidence must remain available in Git/GitHub and local files.

## Validation plan

- Isolated global installer test proving skill installation, global routing and retained safety rules.
- Existing `tests/test_worktree_reservation.py` and `tests/test_workflow_execution_state.py` remain the primary automated contract for ownership/checkpoints.
- Real OpenCode follow-up smoke required to exercise T1/T5/T7 (resume a single issue, milestone, ambiguous candidates) and verify observed behavior. Do not mark these executed without runtime evidence.
