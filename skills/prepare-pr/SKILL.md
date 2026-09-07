---
name: prepare-pr
description: Prepare and optionally create a high-quality GitHub pull request from the current branch. Use after implementation is complete to validate the diff, correlate the work with its issue and OpenSpec change, run final checks, compose the PR, and ensure reviewers have enough context.
compatibility: OpenCode or another coding agent with Git and GitHub access
metadata:
  category: workflow
  workflow: implementation-to-pr
---

# Prepare Pull Request

Turn a completed implementation into a reviewable pull request without hiding uncertainty or including unrelated changes.

## Objectives

A PR must let an independent reviewer quickly understand:

- why the change exists;
- what changed;
- how the implementation works;
- which issue/spec it satisfies;
- how it was validated;
- what is intentionally out of scope;
- what risk or follow-up remains.

## 1. Establish context

Determine:

- repository and default branch;
- current branch and upstream;
- working-tree status;
- commits unique to the branch;
- associated GitHub issue(s);
- relevant OpenSpec change when present;
- repository PR/commit conventions.

Read repository instructions such as `AGENTS.md`, `CONTRIBUTING.md`, PR templates, and relevant agent instructions.

Do not create a PR from the default branch.

## 2. Inspect the complete change

Review the branch diff against the intended base.

Check for:

- unrelated files;
- accidental formatting churn;
- debug output;
- secrets or credentials;
- generated/local files;
- dead code;
- obsolete implementation that should have been removed;
- schema/config changes without required migration steps;
- test changes that merely weaken assertions;
- behavior not described by the issue/spec.

If the branch contains unrelated work, keep it out of the PR when safely possible. Do not silently rewrite unrelated user commits.

## 3. Reconcile with requirements

Read the issue body and relevant comments when an issue exists.

Verify every acceptance criterion against the resulting implementation.

When OpenSpec is present, verify the branch matches the current specification and tasks.

If requirements are not satisfied, do not create a misleading "complete" PR. Fix the implementation first when feasible; otherwise mark the PR as draft and describe the blocker if creation was explicitly requested.

## 4. Validate

Run the appropriate final checks allowed by repository instructions.

Prefer targeted checks first, then broader checks when justified:

- unit tests;
- integration tests;
- lint/format checks;
- static analysis;
- type checking;
- schema validation;
- OpenSpec validation;
- build/package validation.

Never claim a check passed unless it actually ran successfully.

Record skipped checks and the reason.

## 5. Commit quality

If uncommitted implementation remains and the workflow calls for committing it:

- exclude unrelated files;
- follow repository commit conventions;
- use conventional commits when configured;
- keep the message centered on the implemented change.

Use installed commit-related skills where helpful rather than duplicating their rules.

Do not squash/rewrite existing history unless requested or required by repository workflow.

## 6. Push

When PR creation is requested, ensure the branch exists remotely and contains the intended commits.

Do not force-push unless explicitly required and safe.

## 7. Compose the PR

Follow the repository PR template when present.

Otherwise use this structure when applicable:

```markdown
## Summary

Concise explanation of the outcome.

## Why

Business/technical motivation and issue reference.

## Implementation

Important design and architectural decisions.

## Changes

- Relevant change
- Relevant change
- Relevant removal/refactor

## OpenSpec

OpenSpec change name/status, or state that no spec change was required.

## Validation

- PASS: ...
- PASS: ...
- NOT RUN: ... — reason

## Risks / Notes

Only material risks, migration notes, compatibility constraints, or intentional limitations.

Closes #<issue>
```

Do not fill the body with a file-by-file changelog that reviewers can get from the diff.

## 8. Title

Use a concise outcome-oriented title following repository conventions.

Examples:

```text
feat: use Magento order status for private event requests
fix: prevent duplicate rental slot allocation
refactor: consolidate private-event order lifecycle
```

Avoid vague titles such as `changes`, `fix issue`, or `update code`.

## 9. Create or prepare

If explicitly asked to create/open the pull request, do so using available GitHub tooling.

If only asked to prepare it, leave the branch in PR-ready state and output the proposed title/body.

If a PR already exists for the current branch, do not create a duplicate. Treat the existing PR as the target and report it.

## Completion report

Return:

### PR readiness

`READY FOR PR`, `PR CREATED`, `PR ALREADY EXISTS`, or `NOT READY FOR PR`.

### Issue

Associated issue(s), if any.

### OpenSpec

Relevant change and validation status.

### Validation

Only checks actually executed.

### PR

When created or already present, provide its number/URL when available.

### Remaining concerns

Only concrete blockers or material review notes.
