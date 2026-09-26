---
name: implement-issue
description: Plan a GitHub issue through issue-audit, OpenSpec explore and proposal, then stop at an explicit human approval gate. Use to prepare implementation; a separate fresh session uses apply-issue for production code.
---

# Implement Issue: planning

Fetch the live issue, comments, linked PRs and repository instructions. Resume an existing audit, OpenSpec change or PR when present. If a PR exists, hand off to review rather than duplicating work.

1. Run `issue-audit`. Resolve evidence gaps through issue refinement or `[QUESTION]` and approved `[DECISION]`.
2. Apply `openspec-workflow` for the official `/opsx-explore` with `issue-explore`; re-explore after material decisions. Pass `issue-ready`.
3. Apply `openspec-workflow` for `/opsx-proposal`, validation and exact revision/commit approval. Review its contract against issue, current code, tests, dependencies and repository instructions.
4. Present scope, architecture, trade-offs, acceptance tests, risks and handoff. Stop for an explicit human approval of this proposal revision.

Do not modify production code or run `/opsx-apply` in this session, even if the proposal is approved here. After approval, start a fresh implementation session and invoke `apply-issue`. ai-memory can carry context but approval and artifacts must be durable and independently verifiable.

End with `AWAITING PROPOSAL APPROVAL`, `NEEDS REFINEMENT — <reason>` or `HAND OFF TO EXISTING PR`.
