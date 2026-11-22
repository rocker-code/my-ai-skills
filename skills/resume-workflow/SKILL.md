---
name: resume-workflow
description: Recover an interrupted issue or milestone using durable Git/GitHub/OpenSpec, ownership, native runtime and test evidence; never infer success from old chat.
---

# Resume interrupted work

This recovery entry routes to `milestone-orchestrator`, not a second scheduler or persistence layer. Begin read-only. Identify exact repository/issue/milestone, branch/worktree, proposal/head, existing PR, last verified action and original merge mode from authoritative evidence. A URL fixes scope; if multiple candidates remain, show the small evidenced set and ask one necessary question. Unknown prior merge authorization holds the merge action, not useful safe inspection. Never widen single-issue scope.

Refresh live issue/decisions, current PR base/head/checks/reviews, Git status/diffs/staged/untracked/ignored data, unique commits and active/archived OpenSpec. Use `git worktree list --porcelain`, Git common dir and `worktree-reservation list/status/reconcile` when installed. Historical CI, closed issue, title match, chat, elapsed time or a missing process is not delivery proof. No new branch/change/PR merely because the session changed.

Distinguish issue, stage, worker and actual typed execution ID. Reconcile supported native runtime callback/query with current Git and accessible test/CI proof. Reject delayed observations from another repository, issue, worker/execution ID or HEAD; a previous worker result cannot approve the current execution. Dispatch is not completion; a disappeared worker, absent callback/JUnit or incomplete test termination/report remains `unknown` (UNKNOWN). No hidden workflow event comments or timing records are required or consumed. Re-execute only incomplete/invalidated obligations under current [TEST_STRATEGY.md](references/TEST_STRATEGY.md); validate a materially changed contract through native OpenSpec before implementation.

Before any writer/test with effects, establish the old writer actually stopped and reconcile inventory/ownership under [WORKTREES.md](references/WORKTREES.md). Age, missing PID or missing registry alone is insufficient. For `RECOVERY_REQUIRED`, use documented takeover with independently grounded stopped-writer evidence and inventory digest; never bypass verify, accept unexplained drift, force-reset/clean/stash or steal another reservation. Unknown ownership retains partial work and blocks that action. Follow the existing retry diagnosis policy; do not relaunch unbounded workers.

M2T: reconcile existing handoff checkout, each proved integration/GraphQL selection, current code/selection, actual worker liveness and test proof. Keep owned sandboxes on crash, unknown status or open/manual PR. `m2t runs show <run-id> --json` is for test/graphql, not unit/exec receipts; bounded output and relevant private-log excerpts only. Do not `down`/`reset` to resume by default. M2T status/lock/container does not grant checkout ownership or prove success; WORKTREES governs eventual safe closeout.

Return compact authoritative refs: exact scope/mode, checkout/branch/head and dirty state, owner and transition proof, pinned proposal/review/validation, PR/head/checks, last verified action, incomplete obligations, blocker and next action. Hand this to the existing coordinator; resume the same active issue before advancing the sequential queue, or explicitly park it after all writers stop. Reuse a matching proposal; an existing PR goes to review/fix. A missing independent runtime cannot be replaced by role switching.

Report preserved work and the next safe action honestly. Git/GitHub/committed OpenSpec/backups can restore durable data; uncommitted local-only work lost with a disk cannot be reconstructed from a transcript or registry.
