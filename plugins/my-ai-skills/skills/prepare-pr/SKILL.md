---
name: prepare-pr
description: Self-review, validate, and prepare a traceable GitHub pull request for a completed implementation. Invoking this skill authorizes scoped staging, commit, push, and PR creation; it never authorizes merge. Use after apply-issue and before independent pr-audit; reuses an existing PR instead of creating duplicates.
metadata:
  category: workflow
  stage: review
---

# Prepare Pull Request

Turn completed implementation into a reviewable PR with evidence and no hidden uncertainty.

## Establish context

Refresh issue comments/decisions, repository instructions, validated OpenSpec artifacts, branch status, intended base, unique commits and any existing PR. OpenSpec closeout must be complete: inspect the archived change and synchronized live specs in the diff. If a completed change is still active, hand back to `apply-issue` for verification/archive before creating the PR. Do not create from the default branch or duplicate a PR for the same branch.

## Pre-PR self-review

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
