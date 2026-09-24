---
name: update-main
description: Safely update the current repository's local main branch from origin after a pull request is merged. Use when the user asks to sync, refresh, or update main after merge; preserve uncommitted work and stop on unsafe or ambiguous Git state.
---

# Update Main

Update the current repository's local `main` from `origin/main` after a merge. Preserve all user work.

## Procedure

1. Locate the repository with `git rev-parse --show-toplevel`. Run all Git commands from that repository root.
2. Inspect `git status --short --branch` and `git branch --show-current`.
   - If the worktree has staged, unstaged, or untracked changes, stop. Do not stash, reset, clean, commit, or move those changes. Report the status and tell the user to commit or safely stash them before retrying.
   - If a merge, rebase, cherry-pick, or revert is in progress, stop and report it.
3. Confirm the local `main` branch and remote `origin/main` exist. If either is missing, stop and report the exact missing ref; do not create or rename branches or change remotes.
4. Run `git fetch origin` to refresh remote refs.
5. Switch to `main` with `git switch main`. If Git refuses, stop and report the reason; do not force the switch.
6. Fast-forward only with `git merge --ff-only origin/main`. Do not use reset, rebase, or a non-fast-forward merge. If the branches diverged, stop and explain that manual reconciliation is needed.
7. Verify `git status --short --branch`, `git rev-parse HEAD`, and `git rev-parse origin/main`. Confirm the active branch is `main`, the worktree is clean, and both commit SHAs match.

## Completion

Report the repository, active branch, resulting commit SHA, and whether the worktree is clean and synchronized with `origin/main`. If any gate fails, report what was checked and the safe next action. Never delete the merged feature branch, close issues, or perform another merge.
