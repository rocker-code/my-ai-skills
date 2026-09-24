---
name: apply-issue
description: Apply an already approved OpenSpec change for a GitHub issue in a fresh implementation session. Use after proposal approval and a durable handoff; verify the exact contract, run /opsx-apply and targeted tests, then hand off to prepare-pr.
---

# Apply Issue

Start in a genuinely new agent session from the planning session. Rehydrate from the issue and `[DECISION]` comments, pinned OpenSpec change and commit, repository instructions and concise handoff. ai-memory may supplement this context; it is never the sole source of approval or source of truth.

## Entry gate

Verify the exact issue and OpenSpec change, proposal/spec/design/tasks, validation evidence and a recorded human approval identifying the approved revision. Check the branch/worktree and current diff. If approval is missing, the revision changed materially or this is still the planning session, stop with a precise handoff. Never infer approval from silence or the existence of a proposal.

Run the repository's official `/opsx-apply` command; do not invent a substitute command. Implement only the approved contract and applicable repository invariants. If new evidence changes behavior, data, authorization, architecture or public contracts, pause the affected work, update the issue and OpenSpec, then obtain approval for the revised contract.

Run focused tests and relevant static checks; record actual PASS/FAIL/NOT RUN with reasons. Map requirements to changed code and tests, inspect the complete diff for unrelated changes, and pass to `prepare-pr`. End with `READY FOR PR` or `NOT READY FOR PR — <reason>`.
