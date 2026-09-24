---
name: apply-issue
description: Apply an already approved OpenSpec change for a GitHub issue in a fresh implementation session. Use after proposal approval and a durable handoff; verify the exact contract, run /opsx-apply and targeted tests, then hand off to prepare-pr.
---

# Apply Issue

Start in a genuinely new agent session from the planning session. Rehydrate from the issue and `[DECISION]` comments, pinned OpenSpec change and commit, repository instructions and concise handoff. ai-memory may supplement this context; it is never the sole source of approval or source of truth.

## Entry gate

Verify the exact issue and OpenSpec change, proposal/spec/design/tasks, validation evidence and a recorded human approval identifying the approved revision. Check the branch/worktree and current diff. If approval is missing, the revision changed materially or this is still the planning session, stop with a precise handoff. Never infer approval from silence or the existence of a proposal.

Run the repository's official `/opsx-apply` command; do not invent a substitute command. Implement only the approved contract and applicable repository invariants. If new evidence changes behavior, data, authorization, architecture or public contracts, pause the affected work, update the issue and OpenSpec, then obtain approval for the revised contract.

Run focused tests and relevant static checks; record actual PASS/FAIL/NOT RUN with reasons. Before handing off to `prepare-pr`, complete OpenSpec closeout on this feature branch:

1. Confirm every approved task is complete and no blocking decision or implementation mismatch remains.
2. Run the installed OpenSpec implementation-verification command (for example, `/opsx-verify <change>`) when available. Otherwise produce an explicit requirement/scenario → implementation → test evidence matrix and mark unavailable automation as NOT RUN.
3. Run strict validation on the active change (for example, `npx --no-install openspec validate <change> --strict`).
4. Run the installed official archive command on the feature branch (for example, `/opsx-archive <change>` or its documented CLI equivalent). Sync only the already approved delta specs into live specs. Inspect the result: preserve the approved change under the archive path and confirm expected live specs contain the delta. Do not create a separate archive PR.
5. If archival proposes material behavior/design changes beyond the approved delta, stop and obtain renewed approval. If tasks, verification or validation fail, do not archive.

Then inspect the complete diff for unrelated changes, preserve unrelated user work, and pass to `prepare-pr`. End with `READY FOR PR` only when implementation, verification, archive and validation gates pass; otherwise end with `NOT READY FOR PR — <reason>`.
