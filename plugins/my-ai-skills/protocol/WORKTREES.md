# Worktree lifecycle

## Inventory and ownership

Before planning, Apply, PR corrections or cleanup, verify the repository remote, run `git worktree list --porcelain`, and inspect branch, HEAD, `git status --short --untracked-files=all` and linked PR for each relevant checkout. Resolve the Git common directory with `git rev-parse --path-format=absolute --git-common-dir`; worktrees share refs and administrative state. Do not treat a missing path as permission to recreate or prune it.

Use one branch/worktree per issue across planning, Apply and PR corrections. A fresh session is a context boundary, not a reason to create another checkout. Reuse the existing verified issue worktree and proposal commit. If several candidates exist, reconcile their branches, unique commits, diffs and PRs before choosing; preserve every candidate until ownership is clear. Never change another worker's branch or move its files.

Keep the primary checkout for coordination. Respect the repository's configured worktree location; otherwise use a sibling directory `<repository>-worktrees/issue-<number>-<slug>`, outside the source tree. Use a verified remote base for a new branch and record its SHA. Do not repoint an existing issue branch to the newest base. Refresh remote refs when online; report stale/offline evidence explicitly.

The coordinator serializes inventory → reservation → creation and grants only one active writer per issue worktree. Maintain a local registry in the Git common directory (`ai-workflow/worktrees.json`), outside tracked source, containing repository identity, issue URL, branch, absolute path, base SHA, proposal SHA, PR URL/head, owner session/run, lifecycle state, test sandbox and last verified timestamp. Update atomically. Across coordinators, use a repository-common exclusive lock with an available locking mechanism; if exclusivity cannot be established, do not dispatch a concurrent writer. Do not steal a lock or release a reservation based only on age: establish that the prior session stopped. The registry is local coordination data, never proof of GitHub delivery or a validation gate.

Lifecycle: `RESERVED` → `ACTIVE` → `WAITING` / `HANDOFF` → `RETAINED` / `CLEANUP_ELIGIBLE` → `REMOVED`. Reconcile registry entries with actual Git and live GitHub state on resume. An absent registry is a reason to reconstruct ownership, not to duplicate or delete existing worktrees. Block only an ambiguous/conflicting issue.

## Session handoff and environments

Record issue, path, branch, HEAD, clean/dirty state, owner, pinned proposal revision, PR, last verified gate and next action. End the planning writer before starting the fresh Apply writer on that same checkout. Transfer ownership explicitly. Reviewers can read immutable commits; serialize operations that mutate a checkout, index, generated files or test environment. Stop the writer or use an isolated review checkout if review tools write files; register any temporary review checkout and subject it to the same cleanup rules.

Before commands that write, commit, test or push, verify working directory, repository, branch, HEAD and reservation. Run commands with an explicit working directory. Stage exact paths only. Do not copy uncommitted files between worktrees, stash somebody else's changes, force checkout/reset, or create a replacement branch to bypass a dirty checkout. Preserve partial work and report the precise recovery action when ownership cannot be established.

A worktree does not isolate Docker mounts, databases, ports, caches or Magento generated files. Record the actual mounted source and sandbox for each test worker. Allocate isolated disposable resources or serialize shared resources; never silently test another checkout. Follow repository setup commands and keep secrets/generated assets out of commits.

## Automatic housekeeping

Worktree cleanup is a required workflow closeout action, not an optional suggestion to the owner. After each verified issue delivery and kaizen, automatically inspect and remove eligible managed worktrees before scheduling more work. Do not create a separate worktree for every phase or retry. Reuse the same issue checkout through proposal, Apply, fixes and final review whenever exclusive access is possible.

At every orchestrator startup/resume and at run end, reconcile worktrees previously created by this workflow in the selected repository. Remove eligible leftovers from prior runs, including completed issues outside the currently selected milestone, only when durable registry/handoff evidence establishes workflow ownership and all safe-closeout conditions below pass. This housekeeping does not authorize implementing or merging outside the selected scope. Unknown/user-created checkouts stay untouched. Do not ask the owner to approve routine removal of verified eligible managed worktrees. An open PR or an unfinished issue remains retained. If GitHub or local ownership cannot be verified, retain it and report the blocker; continue cleaning other eligible worktrees.

Finish with a compact inventory table: issue, branch/path, PR/delivery, action (`reused`, `removed`, `retained`) and reason. List any residual managed worktree and its exact pending condition, including removal refused by Git. A successful delivery report must disclose incomplete housekeeping instead of silently abandoning directories.

## Safe closeout

In manual merge mode, retain the issue worktree and branch at `READY_TO_MERGE`. Retain blocked, failed and interrupted work with its recovery handoff. An open PR, old timestamp or green CI never makes a checkout disposable.

After verified merge, complete required kaizen and release the worker. Mark cleanup eligible only after confirming: the PR's delivered scope and head match this issue; no active owner, tests or shell depends on the directory; tracked, untracked and ignored files contain no work/data to preserve; no unique unpushed or undelivered commits remain; and proposal/validation/handoff evidence is durable. Inspect ignored files as well as ordinary status. For squash/rebase merges, establish delivery from the merged PR and its exact reviewed head; lack of ancestry alone does not mean work is undelivered. Any uncertainty means retain with a reason.

Remove an eligible checkout only with non-forced `git worktree remove <verified-path>` from another directory. If Git refuses, retain and explain; never retry with `--force`, `rm -rf`, forced branch deletion or blanket `git clean`. Branch deletion is optional and follows repository policy; use `git branch -d` only when Git considers it merged, otherwise retain it (including squash-merged branches). Do not prune other worktree records or delete remote branches as a side effect. Mark registry removal only after verifying Git's worktree list. Report created, reused, retained and removed worktrees with reasons.
