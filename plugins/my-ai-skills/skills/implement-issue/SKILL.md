---
name: implement-issue
description: Plan a GitHub issue through issue-audit, OpenSpec explore and proposal, validate the exact contract and hand it to a fresh implementation session without a routine human approval checkpoint. Use before apply-issue; stop only for unresolved material decisions.
---

# Implement Issue: planning

Fetch the live issue, comments, linked PRs and repository instructions. Resume an existing audit, OpenSpec change or PR when present. If a PR exists, hand off to review rather than duplicating work.

1. Run `issue-audit`. Resolve evidence gaps through issue refinement or `[QUESTION]` and approved `[DECISION]`.
2. Apply `openspec-workflow` for the official `/opsx-explore` with `issue-explore`; re-explore after material decisions. Pass `issue-ready`.
3. Apply `openspec-workflow` for `/opsx-proposal`, exact revision/commit pinning, independent review when warranted and official validation. Review its contract against the issue, decisions, current code, tests, dependencies and repository instructions.
4. Record scope, architecture, trade-offs, acceptance tests, risks and the durable review evidence in the handoff. Continue automatically when the proposal is validated and no material question remains. Escalate only a product/architecture decision the available evidence cannot settle.

Do not modify production code or run `/opsx-apply` in the planning session. Start a fresh implementation session and invoke `apply-issue` on the pinned validated revision. ai-memory can carry context but the review and validation record must be durable and independently verifiable.

End with `READY FOR APPLY — <proposal SHA>`, `NEEDS DECISION — <reason>`, `NEEDS REFINEMENT — <reason>` or `HAND OFF TO EXISTING PR`.
