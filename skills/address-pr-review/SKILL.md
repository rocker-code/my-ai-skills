---
name: address-pr-review
description: Resolve GitHub pull request review feedback end-to-end. Use when a PR has review comments or requested changes that must be evaluated, implemented, tested, and pushed back to the same branch without blindly following stale or incorrect feedback.
compatibility: OpenCode or another coding agent with Git and GitHub access
metadata:
  category: workflow
  workflow: pr-review-fix-loop
---

# Address Pull Request Review

Read, evaluate, and resolve pull request review feedback in the current repository.

The goal is not to obey comments mechanically. The goal is to determine which findings are valid against the latest requirements, OpenSpec, architecture, and code, then implement the correct fixes.

## Inputs

Accept one of:

- PR number, for example `246`;
- `#246`;
- full GitHub PR URL.

Infer the repository from the current worktree when only a number is supplied.

## 1. Establish PR context

Retrieve and inspect:

- PR title/body;
- base and head branches;
- linked issue(s);
- changed files and diff;
- review state;
- top-level PR conversation;
- inline review comments/threads;
- requested changes;
- CI/check status when available.

Read the linked issue and relevant comments when they define requirements.

Read repository instructions and relevant OpenSpec artifacts before modifying code.

## 2. Build the review finding list

Collect every actionable review item.

For each finding, capture:

- source/comment/thread;
- affected file/area;
- requested or implied correction;
- severity when stated;
- whether it is still applicable to the latest diff.

Ignore pure acknowledgements or already-obsolete discussion unless they reveal a still-unresolved requirement.

## 3. Classify each finding

Use one of:

### VALID

The review identifies a real correctness, architecture, maintainability, security, testing, or requirement problem.

### VALID WITH ADAPTATION

The concern is valid but the proposed fix conflicts with framework conventions or current architecture. Solve the underlying problem using the appropriate design.

### ALREADY RESOLVED

The current branch already addresses it.

### OBSOLETE

Later commits or decisions made the comment irrelevant.

### CONFLICTS WITH REQUIREMENTS

The suggestion contradicts the latest issue/OpenSpec/explicit decision.

### INVALID

The finding is based on an incorrect assumption or would make the implementation worse.

Do not implement `INVALID`, `OBSOLETE`, or requirement-conflicting feedback merely to make a thread disappear.

## 4. Reconcile behavioral changes with OpenSpec

When OpenSpec is present, determine whether each valid fix is:

- implementation-only; or
- a behavioral/contract change.

For implementation-only corrections, keep the spec unchanged.

For behavioral/contract changes, follow the `openspec-workflow` process and update the specification before or together with the code.

## 5. Inspect before editing

Trace the affected code path rather than editing only the line mentioned in the comment.

Check:

- callers/callees;
- shared services;
- domain invariants;
- tests;
- framework-native alternatives;
- concurrency/transaction implications;
- API compatibility;
- cleanup caused by the fix.

Avoid patching symptoms while leaving the underlying defect.

## 6. Implement valid corrections

For every valid finding:

1. implement the smallest coherent correction;
2. preserve framework/project conventions;
3. avoid unrelated refactoring;
4. remove obsolete code introduced by the previous implementation when the correction makes it unnecessary;
5. update/add tests for the corrected behavior;
6. update OpenSpec when the behavior or contract changed.

Use relevant installed domain skills where appropriate.

## 7. Validate

Run the narrowest relevant checks first, then broader checks when appropriate and permitted.

Examples:

- targeted tests around reviewed code;
- unit/integration tests;
- lint/static analysis/type checks;
- OpenSpec validation;
- build/schema checks.

Never claim checks passed when they were not executed.

If existing unrelated failures occur, distinguish them from regressions introduced by the fix.

## 8. Review the resulting diff

Compare the new diff against the review findings and original issue.

Verify:

- every valid finding is actually addressed;
- no accidental scope was added;
- no requirement was broken to satisfy a review comment;
- no dead compatibility code remains;
- tests genuinely cover the corrected behavior.

## 9. Commit and push

When the repository workflow expects it:

- commit only relevant changes;
- follow commit conventions;
- push to the existing PR branch;
- do not create a new PR for review fixes;
- do not force-push unless required and explicitly safe.

## 10. Respond to review threads

If GitHub tooling supports replies, respond concisely to material threads after the correction is in the branch.

For implemented findings, explain what changed.

For findings not implemented because they are obsolete, invalid, or conflict with requirements, explain the evidence briefly and professionally.

Do not mark something resolved in prose if the code does not actually address it.

## Completion report

Return:

### Review summary

Counts by classification:

```text
VALID: n
VALID WITH ADAPTATION: n
ALREADY RESOLVED: n
OBSOLETE: n
CONFLICTS WITH REQUIREMENTS: n
INVALID: n
```

### Changes implemented

Concise summary of actual corrections.

### OpenSpec

State whether it changed and why.

### Validation

List checks actually executed and their result.

### Remaining review items

List only unresolved material items and the reason.

### Branch state

State whether corrections were committed/pushed to the PR branch or remain local.
