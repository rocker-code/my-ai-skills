---
name: prepare-pr
description: Self-review, validate, commit/push when authorized, and prepare or create a traceable GitHub pull request for a completed implementation. Use after apply-issue and before independent pr-audit; reuses an existing PR instead of creating duplicates.
metadata:
  category: workflow
  stage: review
---

# Prepare Pull Request

Turn completed implementation into a reviewable PR with evidence and no hidden uncertainty.

## Establish context

Refresh issue comments/decisions, repository instructions, OpenSpec change, branch status, intended base, unique commits and any existing PR. Do not create from the default branch or duplicate a PR for the same branch.

## Pre-PR self-review

Review the complete diff against:

1. issue acceptance criteria;
2. latest `[DECISION]` comments;
3. OpenSpec proposal/spec/design/tasks;
4. project/domain conventions;
5. backward compatibility and migrations;
6. public schemas/contracts;
7. requirement → code → test traceability and required tests;
8. obsolete/dead code from the change.

Detect unrelated files, formatting churn, debug output, secrets, generated/local files, weakened tests and unapproved behavior. Fix in-scope defects before PR creation; preserve unrelated user work.

Run permitted validations and report skipped checks with reasons. Include a concise requirement → implementation → test matrix in the PR description; mark unverified items explicitly. Hand off the opened PR to an independent pr-audit and architecture-audit where boundaries changed.

## Git operations

When authorized, commit only relevant changes following repository conventions and push without force unless explicitly required and safe. If only asked to prepare, do not create/push without authorization.

## PR body

Follow the repository template, otherwise use [the pull request template](../../templates/pull-request.md). Include issue linkage (`Closes #...` when correct), OpenSpec change, what changed, contract changes, material decisions, tests actually run, risk/migration/compatibility and non-goals.

Do not provide a noisy file-by-file changelog. Use an outcome-oriented title.

## Completion

Return exactly one readiness state: `READY FOR PR`, `PR CREATED`, `PR ALREADY EXISTS`, or `NOT READY FOR PR — <reason>`, plus issue, OpenSpec validation, actual checks, PR URL when available and material remaining concerns.
