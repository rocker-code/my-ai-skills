---
name: openspec-workflow
description: Manage OpenSpec as the mandatory behavioral and architectural contract before implementation when a repository uses OpenSpec. Use to create, continue, reconcile, validate, and keep an OpenSpec change synchronized with GitHub requirements, repository reality, code, tests, and review feedback.
compatibility: OpenCode or another coding agent with repository access and OpenSpec tooling when available
metadata:
  category: workflow
  workflow: specification-management
  methodology: specification-first
---

# OpenSpec Workflow

Use OpenSpec as the formal bridge between approved requirements and implementation.

When a repository uses OpenSpec, this workflow is a **pre-implementation gate**.

The default sequence is:

```text
requirement
→ repository analysis
→ OpenSpec change
→ proposal/spec/design/tasks
→ validation/readiness
→ implementation
→ implementation validation
```

Never default to:

```text
requirement
→ code
→ generate spec afterward
```

# Principles

1. Requirements describe intent.
2. Repository inspection describes current reality.
3. OpenSpec defines the agreed target behavior and important architectural decisions.
4. Code and tests implement that contract.
5. OpenSpec must be ready before production implementation begins.
6. Do not create duplicate changes when an applicable change already exists.
7. Behavioral or architectural changes discovered during implementation or review must update OpenSpec before the affected code proceeds.
8. Pure implementation refactors with no behavioral/contract impact do not require artificial specification churn unless repository conventions say otherwise.
9. Never rewrite unrelated specifications merely to make the current change appear consistent.

# Detect OpenSpec

Inspect repository instructions, configuration, directories, existing changes, and available commands.

Common indicators include:

```text
openspec/
.openspec/
OpenSpec config
existing proposal/spec/design/tasks artifacts
OpenSpec CLI commands
repository documentation referring to OpenSpec
```

If OpenSpec is genuinely absent, stop applying this skill without introducing it automatically.

# Understand the requirement before creating artifacts

Before creating or modifying a change:

- read the complete GitHub issue or approved requirement;
- read relevant comments and later decisions;
- inspect the current implementation;
- inspect relevant tests;
- inspect existing specifications and architecture documentation.

Do not convert issue text mechanically into a spec without understanding the current system.

# Locate an existing change first

Search for a matching OpenSpec change by:

- GitHub issue number;
- feature/capability name;
- domain terminology;
- branch name;
- related modules/components.

If a matching active change exists, continue it.

Do not create a parallel change for the same approved behavior without a concrete reason.

# Create a change when needed

A change is normally justified when work modifies one or more of:

- user-visible behavior;
- domain rules or invariants;
- API/GraphQL contracts;
- validation/error semantics;
- state transitions;
- persistence semantics;
- integration behavior;
- concurrency/transaction semantics;
- architectural ownership/responsibility;
- compatibility/migration behavior;
- removal of a previously supported behavior.

A mechanical cleanup or pure implementation refactor may not require a new behavioral spec.

# Required specification lifecycle

Follow the repository's actual OpenSpec conventions, but preserve this logical order.

## 1. Proposal / intent

Describe:

- why the change exists;
- problem being solved;
- desired outcome;
- boundaries/non-goals;
- relevant dependencies;
- compatibility/migration implications when known.

## 2. Behavioral specification

Define observable behavior and domain contracts.

Cover relevant:

- actors/callers;
- preconditions;
- successful behavior;
- invariants;
- validation and public errors;
- state transitions;
- API contracts;
- persistence semantics where externally meaningful;
- edge/boundary cases;
- concurrency expectations;
- compatibility requirements;
- explicitly removed behavior.

Prefer behavior over incidental implementation details.

Avoid encoding temporary class names or low-level method structure unless the architectural contract itself requires them.

## 3. Design / architecture

For architectural or non-trivial implementation changes, decide before coding:

- component ownership;
- existing mechanisms to reuse;
- native framework facilities to prefer;
- interfaces/contracts;
- data model changes;
- transaction boundaries;
- locking/concurrency strategy;
- migration strategy;
- compatibility strategy;
- obsolete components to remove;
- significant trade-offs.

The purpose is to prevent architecture from emerging accidentally during code generation.

## 4. Tasks

Create concrete, traceable implementation tasks.

Tasks may include:

- production code;
- API/schema work;
- database/data migration;
- tests;
- cleanup/removal of legacy mechanisms;
- configuration;
- documentation;
- static/schema/OpenSpec validation.

Every important acceptance criterion should map to specification and implementation work.

Do not mark tasks complete before the corresponding work actually exists and has been inspected.

# Pre-implementation readiness gate

Before production code is modified, verify:

```text
[ ] approved requirement and comments were read
[ ] relevant repository implementation was inspected
[ ] existing applicable OpenSpec change was reused or a new one created
[ ] requested behavior is represented in the specification
[ ] important edge cases/invariants are represented
[ ] architectural decisions are explicit where needed
[ ] implementation tasks are concrete
[ ] contradictions with existing specs/code/tests were reconciled
[ ] OpenSpec validation passes when tooling supports it
```

If this gate is not satisfied, do not proceed to implementation.

If validation tooling is unavailable, perform a manual consistency review and report the limitation; do not skip the specification stage.

# Reconcile conflicting sources

Compare:

```text
GitHub issue + comments
↔ current repository
↔ current tests
↔ OpenSpec
↔ project documentation
```

Use these rules:

- the latest explicit approved product/architecture decision overrides older conflicting discussion;
- repository code describes current reality, not necessarily desired behavior;
- tests provide compatibility evidence but can be obsolete;
- OpenSpec must be updated when the approved target behavior changes;
- unrelated inconsistencies remain outside scope unless they block the approved change.

Do not silently reinterpret requirements simply because current code behaves differently.

# During implementation

Implementation must follow the approved OpenSpec tasks/spec/design.

If new information reveals a necessary change to approved behavior or architecture:

```text
STOP affected implementation
→ update OpenSpec
→ reconcile/validate
→ update tasks
→ resume code changes
```

Do not finish the implementation and then rewrite OpenSpec to legitimize accidental behavior.

# During PR review fixes

Classify each review finding into one of:

- implementation defect without contract change;
- missing implementation of an already specified requirement;
- behavioral contract change;
- architectural/design change;
- stale/invalid review feedback.

For behavioral or architectural changes:

1. update OpenSpec first;
2. validate/reconcile it;
3. update tasks if necessary;
4. then change code/tests.

A reviewer comment is not automatically authoritative over the approved specification.

# Validation before PR readiness

Perform a three-way consistency review:

```text
approved requirements
↔ OpenSpec
↔ code/tests
```

Verify:

- implementation matches the latest spec;
- tests cover relevant behavior;
- completed tasks are genuinely complete;
- no required task is silently omitted;
- removed behavior/components are reflected where appropriate;
- no unresolved specification contradiction remains;
- OpenSpec validation passes when available.

If validation cannot execute, report it explicitly.

# Archival

Do not automatically archive an OpenSpec change merely because implementation is complete.

Archive only when repository workflow or explicit instruction defines that point, commonly after merge or release.

# Completion output

Report:

- OpenSpec present or absent;
- change reused or created;
- proposal/spec/design/tasks touched;
- validation result;
- implementation-readiness status when used before coding;
- any unresolved specification discrepancy.
