---
name: prepare-pr
description: Self-review, validate, and prepare a traceable GitHub pull request for a completed implementation. Invoking this skill authorizes scoped staging, commit, push, and PR creation; it never authorizes merge. Use after apply-issue and before independent pr-audit; reuses an existing PR instead of creating duplicates.
metadata:
  category: workflow
  stage: review
---

# Prepare Pull Request

## Handoff instrumentado (condicional)

Somente com `workflow_instrumentation.enabled: true` e contexto executor autorizado,
seguir [o contrato](references/WORKFLOW_INSTRUMENTATION.md): preservar issue/run/
etapa/worker/execução, `operation_ids`, sessão real ou `session_id: null`, worktree/
branch; devolver horários, candidato/SHA e evidência ao coordenador. Não publicar
o registro de workflow como worker; invocação isolada não ativa instrumentação.
Isso não substitui gates de commit/push/PR nem amplia suas escritas autorizadas.

Turn completed implementation into a reviewable PR with evidence and no hidden uncertainty.

## Establish context

Refresh issue comments/decisions, repository instructions, validated OpenSpec artifacts, branch status, intended base, unique commits and any existing PR. OpenSpec closeout must be complete: inspect the archived change and synchronized live specs in the diff. If a completed change is still active, hand back to `apply-issue` for verification/archive before creating the PR. Do not create from the default branch or duplicate a PR for the same branch.

## Pre-PR self-review

When a failure was repeated, retain the single `attempt-log` block after the evidence/obligation lines in Validation and run `scripts/attempt-log check <handoff-file> --final`. Require `valid=true && ready=true` and exit 0. Exit 1 for a rule violation **or a valid but blocked/replan-pending group** means `NOT READY FOR PR`; do not treat a well-classified blocker as a passing gate. No block is required without a repeated failure.

Review the complete diff against:

1. issue acceptance criteria;
2. latest `[DECISION]` comments;
3. pinned, validated OpenSpec proposal/spec/design/tasks, active during implementation or preserved under `openspec/changes/archive/` after closeout, plus synchronized live specs;
4. project/domain conventions;
5. backward compatibility and migrations;
6. public schemas/contracts;
7. requirement → code → test traceability and required tests;
8. obsolete/dead code from the change.

Detect unrelated files, formatting churn, debug output, secrets, generated/local files, weakened tests and behavior outside the validated contract. Fix in-scope defects before PR creation; preserve unrelated user work.

Run permitted validations and report skipped checks with reasons. For integration or API-functional coverage, verify the final required local suites ran on the exact source checkout being committed, distinguish narrow development runs from the final suite, and list unresolved environment/fixture failures. A repository-mandated pre-commit suite that is missing or failing means `NOT READY FOR PR`; do not replace it with a previous CI result. Include a concise requirement → implementation → test matrix in the PR description; mark unverified items explicitly. Hand off the opened PR to an independent pr-audit and architecture-audit where boundaries changed.

Where installed, use `workflow-evidence verify <id> --format json` against the candidate and check manifest/log accessibility, checksum, HEAD/index/diff/config and declared environment IDs. Distinguish `verified/passed` from `metadata_only`, `incomplete`, `ambiguous`, `stale` or `not_applicable`; inspect per-obligation recovery rather than rerunning merely because a previous runtime's path is unavailable. For another clone import an integrity-checked bundle; a public local projection alone cannot pass. Complete archive/sync, generated distribution, self-review and commit **before** the final required local gate; run it via `record` at the final clean HEAD, verify, then push and create/update the PR. Keep its ID outside the commit; any subsequent commit requires a fresh final gate. Hosted gates require exact-SHA API confirmation **and** a trusted base-policy-to-check binding; hosted results never satisfy required local gates. If the helper is unavailable, report helper verification NOT RUN and retain the existing manual proof and gates. Include obligation → code → test → evidence state in Validation.

## Git operations

Invoking `/prepare-pr` is the owner's standing authorization to complete routine Git operations for the current issue: stage only issue-related files, commit them following repository conventions, push the current feature branch without force, and open the PR against the verified base using the reviewed title and body. Do not ask for a second confirmation for these scoped actions.

Before writing, verify the current branch is not the default branch, confirm the intended base, and identify the exact issue-related files. Inspect the staged diff before committing. Preserve unrelated user changes and never use broad staging such as `git add .`. If file scope, branch, or base cannot be established safely, stop and report the specific blocker rather than asking a generic authorization question.

This authorization does not include merging, releasing, deploying, force-pushing, or changing unrelated files. The audited resolution workflow owns the final merge gate and uses the owner's standing auto-if-green preference unless the direct request opts out. If the user explicitly asks for a prepare-only or review-only run, do not commit, push, or open a PR; return `READY FOR PR` with the prepared title, body, checks, and scope.

## PR body

Follow the repository template, otherwise use [the pull request template](references/pull-request.md). Include issue linkage (`Closes #...` when correct), OpenSpec change, what changed, contract changes, material decisions, tests actually run, risk/migration/compatibility and non-goals.

Do not provide a noisy file-by-file changelog. Use an outcome-oriented title.

## Completion

Return exactly one readiness state: `READY FOR PR`, `PR CREATED`, `PR ALREADY EXISTS`, or `NOT READY FOR PR — <reason>`, plus issue, OpenSpec validation, actual checks, PR URL when available and material remaining concerns.

## Automatic CI performance routing

Read [the CI performance protocol](references/CI_PERFORMANCE.md). For performance or material workflow/test-infrastructure changes, automatically use `ci-performance-audit` in review mode as self-review. Include baseline/candidate inputs, measured versus provisional benefit, runner-minute cost, retained obligations and rollback in the PR. Ordinary test additions need only a lightweight check; self-review does not replace independent `pr-audit`.

## Proportionate test coverage

Read [the test strategy](references/TEST_STRATEGY.md). Self-review test sufficiency and duplication against the planned evidence matrix. Include the proving layer, reused/new tests and material residual uncertainty in the existing PR evidence. Add coverage only for a concrete missing obligation; preserve required checks.

Inspect existing tests for the affected behavior for redundant cases or obsolete expectations under the test strategy. Keep ordinary cleanup small and scope-bound; for a wider suite audit use a dedicated issue. Any consolidation, migration or removal needs a current-obligation → retained/replacement proof (or authoritative obsolescence evidence) map and applicable validation.

## Worktree lifecycle

Follow [the worktree protocol](references/WORKTREES.md) before checkout writes or worker dispatch. Inventory and reuse the verified issue checkout; transfer its single writer reservation across fresh sessions. Preserve partial work, isolate test resources and retain manual-merge work. Close out only verified eligible worktrees using non-forced Git operations.

When installed, use `worktree-reservation reserve`/`verify` before mutating, `checkpoint` after own writes and `handoff` between returned workers; drift suspends writes until recorded acceptance. Without the helper, coordinate manually under WORKTREES and report the gap.
