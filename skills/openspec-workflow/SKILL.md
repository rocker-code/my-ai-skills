---
name: openspec-workflow
description: Operate OpenSpec as the mandatory behavioral and architectural contract before implementation in repositories that use it. Use to create, resume, reconcile, review, validate and apply proposal/spec/design/tasks without replacing issue discovery or retrofitting specs after code.
metadata:
  category: workflow
  methodology: openspec-first
---

# OpenSpec Workflow

OpenSpec remains the bridge between approved GitHub intent and implementation reality. This skill orchestrates the repository's actual `/opsx:*` commands; it does not replace or emulate them with a parallel format.

## Required order

```text
issue-explore
→ questions/decisions when needed
→ issue-explore again
→ issue-ready
→ /opsx:proposal (plus specs/design/tasks as required)
→ proposal review
→ /opsx:apply
→ validation
```

Never default to requirement → code → retrospective spec.

## Detect and resume

Read repository instructions and locate an existing change by issue number, branch, capability and domain terminology before creating one. Resume an applicable change. Do not duplicate proposal/spec/design/tasks already present and coherent.

If OpenSpec is genuinely absent, do not introduce it automatically; return control to the calling workflow with an explicit implementation plan requirement.

## Artifacts

Use the repository's conventions and official commands.

- **Proposal:** why, outcome, boundaries, dependencies, compatibility.
- **Specification/scenarios:** observable behavior, validation, errors, state transitions, contracts, invariants, concurrency and edge cases.
- **Design:** ownership, native mechanisms reused, interfaces, data changes, transactions/locks, migration, compatibility, removals and trade-offs.
- **Tasks:** traceable production, schema/data, tests, cleanup, docs/config and validation work.

For cross-repository behavior, read and use [the integration contract template](../../templates/github/integration-contract.md) or its project equivalent.

## Proposal checkpoint

Before apply, summarize and review:

- files/modules or capabilities affected;
- public contract changes and backward compatibility;
- existing mechanisms reused;
- data/migration implications;
- test plan;
- risks and explicit non-goals.

For medium/large changes, stop for proposal approval when the user or repository workflow requires supervision. Correcting a proposal is cheaper than correcting generated implementation.

## Readiness gate

Before production code:

```text
[ ] issue-ready passed
[ ] matching OpenSpec change is selected
[ ] behavior/scenarios cover acceptance criteria
[ ] architectural decisions are explicit where material
[ ] tasks are concrete and traceable
[ ] contradictions are reconciled
[ ] official OpenSpec validation passes, or a reported manual review explains why it could not run
```

## During implementation/review

If evidence requires a behavioral or architectural change, stop the affected implementation, update and validate OpenSpec, adjust tasks, then resume. Implementation-only fixes do not create artificial spec churn.

Do not archive a change automatically; follow repository policy, commonly after merge/release.

## Output

Report change reused/created, artifacts touched, commands/validation actually run, unresolved discrepancies and either `READY FOR APPLY` or `NOT READY FOR APPLY — <reason>`.
