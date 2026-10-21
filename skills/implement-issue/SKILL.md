---
name: implement-issue
description: Plan a GitHub issue through issue-audit, OpenSpec explore and proposal, validate the exact contract and hand it to a fresh implementation session without a routine human approval checkpoint. Use before apply-issue; stop only for unresolved material decisions.
---

# Implement Issue: planning

Fetch the live issue, comments, linked PRs and repository instructions. Resume an existing audit, OpenSpec change or PR when present. If a PR exists, hand off to review rather than duplicating work.

1. Run `issue-audit`. Resolve evidence gaps through issue refinement or `[QUESTION]` and approved `[DECISION]`.
2. Apply `openspec-workflow` for the official `/opsx-explore` with `issue-explore`; re-explore after material decisions. Pass `issue-ready`.
3. Apply `openspec-workflow` for `/opsx-propose`, exact revision/commit pinning, independent review when warranted and official validation. Review its contract against the issue, decisions, current code, tests, dependencies and repository instructions.
4. For changes needing integration or API-functional tests, plan a requirement → boundary → test matrix before Apply: identify the smallest existing test class/fixture patterns, positive and failure cases, test data ownership/rollback, service dependencies, the repository's exact local commands and sandbox isolation, and which tests must pass before commit. Distinguish a focused feedback run from the final required suite; record environment prerequisites and known setup cost in the handoff. Do not propose a new test helper or suite bypass solely to shorten the loop.
5. Record scope, architecture, trade-offs, acceptance tests, risks and durable review evidence in the handoff. Apply the proposal approval checklist in the AI workflow protocol: verify issue traceability, scope, consistency with decisions and project patterns, risk coverage, exact-revision official validation, and required independent review. When all checks pass, approve the proposal as the planning agent, mark `READY FOR APPLY`, and continue automatically. Do not ask the owner to approve the proposal or wait for a yes/no response.
6. Resolve routine uncertainties from code, native behavior, repository conventions, tests and prior approved decisions. Escalate only a genuinely unresolved material product/architecture choice, unrequested scope, public-contract break, authorization/sensitive-data change, irreversible/destructive action, or material external cost/commitment. State the exact decision and impact; do not stop unrelated eligible work.

Do not modify production code or run `/opsx-apply` in the planning session. Start a fresh implementation session and invoke `apply-issue` on the pinned validated revision. ai-memory can carry context but the review and validation record must be durable and independently verifiable.

End with `READY FOR APPLY — <proposal SHA>`, `NEEDS DECISION — <reason>`, `NEEDS REFINEMENT — <reason>` or `HAND OFF TO EXISTING PR`.

## Automatic CI performance routing

Read [the CI performance protocol](references/CI_PERFORMANCE.md). For CI/test-performance issues, automatically apply `optimize-ci` as a planning lens after the diagnosis from `issue-audit`. Put the preservation contract and benchmark plan into the normal OpenSpec proposal; do not introduce a second planner or approval checkpoint.

## Proportionate test coverage

Read [the test strategy](references/TEST_STRATEGY.md). During proposal planning, extend the existing evidence matrix with scenario, acceptance criterion/concrete risk, proving layer and existing/new test. Reuse current tests and select sufficient coverage before handoff; do not generate exhaustive combinations or duplicate obligations across layers.
