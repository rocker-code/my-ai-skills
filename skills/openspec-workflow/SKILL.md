---
name: openspec-workflow
description: Manage OpenSpec as the behavioral contract for an implementation workflow. Use when a repository contains OpenSpec and a change must be created, continued, updated, validated, or reconciled with GitHub issues, code, tests, or review feedback.
compatibility: OpenCode or another coding agent with repository access and OpenSpec tooling when available
metadata:
  category: workflow
  workflow: specification-management
---

# OpenSpec Workflow

Use OpenSpec as the behavioral and architectural contract between requirements and implementation.

## Principles

1. Requirements describe intent; OpenSpec describes agreed behavior; code implements it.
2. Do not create duplicate changes when a relevant OpenSpec change already exists.
3. Behavioral changes discovered during implementation or review must update OpenSpec before the implementation becomes authoritative.
4. Pure implementation refactors do not require specification churn unless repository conventions require it.
5. Never rewrite unrelated specifications to make the current change look consistent.

## Detect OpenSpec

Inspect the repository for OpenSpec configuration, directories, existing changes, commands, and project instructions.

If OpenSpec is not present, stop applying this skill without introducing it automatically.

## Locate an existing change

Search by:

- GitHub issue number;
- feature name;
- domain terms;
- branch name;
- related modules or capabilities.

Continue an existing matching change instead of creating a parallel specification.

## Create a change when needed

A new change is normally justified when the work modifies:

- user-visible behavior;
- domain rules or invariants;
- API or GraphQL contracts;
- persistence semantics;
- state transitions;
- integration behavior;
- architectural ownership or responsibility.

Do not create a new spec solely for formatting, mechanical cleanup, or an implementation-only refactor with no observable behavior change.

## Required sequence

Prefer this order:

```text
GitHub issue / approved requirement
    ↓
OpenSpec proposal/change
    ↓
specification and scenarios
    ↓
implementation tasks
    ↓
code and tests
    ↓
validation
```

Before implementation, verify that the specification captures the intended behavior and important constraints.

## Reconcile sources

Compare:

```text
GitHub issue
↔ issue comments
↔ OpenSpec
↔ current code
↔ tests
```

When they conflict:

- newer explicit product/architecture decisions supersede older discussion;
- current code describes reality, not necessarily desired behavior;
- tests may reveal compatibility requirements;
- OpenSpec must be updated when the approved desired behavior changes.

Do not silently reinterpret a behavioral requirement just because the current code works differently.

## Specification quality

Specifications should describe behavior rather than implementation details whenever practical.

Include:

- actors or callers;
- preconditions;
- expected behavior;
- state transitions;
- invariants;
- validation/error behavior;
- important edge cases;
- compatibility expectations;
- explicitly excluded behavior when relevant.

Avoid encoding incidental class names, internal method names, or temporary implementation details as product behavior.

## Tasks

Implementation tasks should be concrete and traceable to the specification.

Tasks should cover relevant work such as:

- model/schema changes;
- service/application changes;
- API changes;
- migration/data changes;
- tests;
- removal of obsolete implementation;
- documentation or configuration updates;
- validation.

Do not mark a task complete until the corresponding implementation exists and has been reviewed locally.

## During implementation

If new information reveals that the planned behavior must change:

1. confirm the change is actually required by the issue/review/current architecture;
2. update the relevant OpenSpec artifact;
3. validate the updated specification when tooling permits;
4. update implementation tasks;
5. then modify code/tests.

Do not use OpenSpec as after-the-fact documentation for accidental behavior.

## During PR review fixes

Classify feedback as either:

- implementation correction with no behavior change;
- specification/contract change.

For the second category, update OpenSpec before or together with the code correction.

## Validation

Before declaring the change PR-ready:

- verify the implementation matches the latest specification;
- verify tasks accurately reflect completion;
- run OpenSpec validation if available;
- ensure no unresolved specification contradiction remains.

If validation cannot run, report that explicitly.

## Archival

Do not automatically archive a change merely because implementation is complete. Archive only when the repository workflow or explicit request calls for it, commonly after merge/release.

## Completion output

Report:

- OpenSpec present or absent;
- existing change reused or new change created;
- artifacts changed;
- validation result;
- any remaining specification discrepancy.
