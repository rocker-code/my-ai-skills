---
name: resume-workflow
description: Recover a previously interrupted my-ai-skills issue or milestone in a new OpenCode session. Use for "continue de onde parou", "retome o desenvolvimento", "resume", or recovery after a reboot/crash. Reconcile durable evidence before scheduling work; never infer completion from the old chat.
metadata:
  category: workflow
  stage: recovery
---

# Resume Workflow — interrupted OpenCode work

Use this skill when the user asks to continue interrupted work or a new session has no reliable conversation context. **This is a recovery entrypoint, not another scheduler or persistence store.** Invoke the existing `milestone-orchestrator` for an identified issue/milestone and reuse its required gates, workers and merge mode. Do not implement here in the recovery/inventory phase.

## Resolve scope without guessing

1. Read local `AGENTS.md` and applicable project instructions. Establish the actual checkout via `git rev-parse --show-toplevel`, `git remote -v`, `git rev-parse --path-format=absolute --git-common-dir` and `git worktree list --porcelain`. A worktree can belong to a different project than the terminal's previous session.
2. If the user supplied an issue/milestone URL, use that **exact** scope. Otherwise, correlate the current repository's managed worktree registry (`scripts/worktree-reservation list/status`), local branches/dirty worktrees, active/archived OpenSpec changes, relevant GitHub issues/PRs and existing `workflow-event` run records. Prefer a *uniquely evidenced* interrupted run; most recently modified files or the last chat alone are not evidence of scope.
3. If several plausible issues, milestones, repositories or merge modes remain, show the short candidate set with the evidence that differentiates them, then ask **one necessary question** before writing. Do not silently widen a single issue to a milestone/queue. If no durable candidate can be established, say so and request the missing issue/milestone or checkout.
4. Do not change merge mode by inference. Preserve a previously documented `manual` selection if it is verified for the recovered run. If the earlier mode cannot be verified, do not silently authorize a merge: continue recovery and hold the merge gate pending explicit resolution.

## Reconstruct, verify, then recover

Perform this inventory **read-only** before takeover, tests with effects, git writes, or worker dispatch:

- Refresh the exact issue, decisions and linked PR; inspect PR head and required checks at their **current SHAs**. Never treat closed issue, green historical CI, or a PR title match as delivery evidence.
- Inspect `git status --short --untracked-files=all`, staged/unstaged diffs, unique/unpushed commits, ignored artifacts with possible work data, HEAD/branch/worktree mapping, tracked OpenSpec proposal and its pinned validated revision. Keep every candidate checkout until ownership is resolved.
- Reconstruct the latest **verified** stage per issue using GitHub decisions, committed OpenSpec, `workflow-event` ledger, accessible proof bundles and actual runtime completion reports. An open stage, missing callback/JUnit, process disappearance, agent prose or test log excerpt is **unknown**, not passed. Confirm side effects and rerun only the affected obligation after preflight.
- Compare the validated plan's revision with current policy and implementation. Reuse matching completed gates; material changes return to normal proposal review/validation. No new OpenSpec change, branch, PR or test run merely because the chat/session changed.
- Establish the old writer actually stopped using independently grounded runtime/ownership evidence. A stale timestamp, missing PID or missing registry **alone** is insufficient. Follow [WORKTREES](../../protocol/WORKTREES.md): `reconcile` and its inventory digest for `RECOVERY_REQUIRED`; no automatic takeover unless stopped-writer evidence and current inventory satisfy the existing helper. Do not bypass `verify`, accept drift without its explicit documented reason, reset/clean/stash, or take another worker's reservation.
- If GitHub is unreachable, an owner is still running, registry/inventory conflict, unique commits are ambiguous, or destructive reconciliation would be necessary: retain partial work and stop **only the affected issue** with a concrete blocker. Other independently authorized issues may proceed through the normal scheduler.

## Handoff to existing orchestration

Once unique scope and safe writer transition are established, hand the following **compact, evidence-backed facts** to `milestone-orchestrator` (do not rely on a transcript):
- Repository, exact issue/milestone URL, original run ID when verified, merge mode or unresolved merge gate.
- Worktree/branch/HEAD, dirty/staged/untracked state, reservation owner/transition proof, existing PR/head.
- OpenSpec proposal/validated SHA, last gate with accessible evidence, interrupted/unknown commands and next required verification.
- Hard dependencies, blocker (if any), and the next safe action.

For a single issue use `scope=single_issue`; for a milestone use precisely that milestone. The orchestrator creates/reconciles its own ledger and continues with `implement-issue`, `apply-issue`, review and PR resolution as applicable. **Never start a fresh implementation worker in the same planning session without the required validated-plan and handoff gates.** If an existing PR is present, audit its current head instead of planning a duplicate.

## Recovery result shown to the user

Report in a few lines: identified scope, last verified stage (or `não verificado`), preserved work, next action, and exact blocker/decision only if necessary. Do not claim the user-facing phrase alone resumes a running process; it initiates verification and safe continuation.

### Irrecoverable local state

Git/GitHub/committed OpenSpec and backups can restore persisted work on another computer; an uncommitted local-only change lost with the disk cannot be reconstructed from a ledger, chat history or worktree registry. Clearly identify this boundary rather than claiming a successful recovery.
