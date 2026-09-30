---
name: apply-issue
description: Apply a pinned, validated OpenSpec change for a GitHub issue in a fresh implementation session. Use after planning review and durable handoff; verify exact revision and gates, run /opsx-apply and targeted tests, then hand off to prepare-pr.
---

# Apply Issue

Start in a genuinely new agent session from the planning session. Rehydrate from the issue and `[DECISION]` comments, pinned OpenSpec change and commit, repository instructions and concise handoff. ai-memory may supplement this context; it is never the sole source of validation evidence or source of truth.

## Entry gate

Verify the exact issue and OpenSpec proposal/spec/design/tasks, pinned revision, review evidence and official validation result. Check the branch/worktree, current diff and merged prerequisites. If evidence is missing, the revision changed materially, a blocking decision remains or this is still the planning session, stop with a precise handoff. A proposal's existence alone does not pass the gate.

Run the repository's official `/opsx-apply` command; do not invent a substitute command. Implement only the validated contract and applicable repository invariants. If new evidence changes behavior, data, authorization, architecture or public contracts, pause the affected work, update the issue and OpenSpec, then review and validate the revised pinned contract; ask the owner only for unresolved material decisions.

Run focused tests and relevant static checks; record actual PASS/FAIL/NOT RUN with reasons. Apply `openspec-workflow` for the mandatory post-Apply closeout: complete validated tasks, verify scenarios against implementation and tests, use the official verifier when available, strictly validate, archive on this feature branch, synchronize validated live specs and inspect both archived artifacts and live specs. If verification or archive fails or changes the validated behavior, stop and follow its revision review and validation gate. Do not hand an active incomplete change to `prepare-pr`.

Then inspect the complete diff for unrelated changes, preserve unrelated user work, and pass to `prepare-pr`. End with `READY FOR PR` only when implementation, verification, archive and validation gates pass; otherwise end with `NOT READY FOR PR — <reason>`.

## Automatic CI performance routing

Read [the CI performance protocol](references/CI_PERFORMANCE.md). Automatically apply `optimize-ci` inside this fresh session for validated performance experiments. For ordinary feature changes to expensive fixtures, test discovery or CI setup, use its lightweight preservation checklist without expanding scope. Record before/after only when the validated work requires it; retain normal verification and archive gates.
