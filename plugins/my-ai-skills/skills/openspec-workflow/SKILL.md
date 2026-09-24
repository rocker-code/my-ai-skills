---
name: openspec-workflow
description: Operate OpenSpec as the mandatory behavioral and architectural contract before implementation in repositories that use it. Use to create, resume, reconcile, review, validate and apply proposal/spec/design/tasks without replacing issue discovery or retrofitting specs after code.
metadata:
  category: workflow
  methodology: openspec-first
---

# OpenSpec Workflow

OpenSpec remains the bridge between approved GitHub intent and implementation reality. This skill orchestrates the repository's actual CLI commands, including `/opsx-explore`; it does not replace or emulate them with a parallel format.

## Required order

```text
/opsx-explore (with the issue-explore protocol)
→ questions/decisions when needed
→ /opsx-explore again after decisions
→ issue-ready
→ /opsx-proposal (plus specs/design/tasks as required)
→ proposal review
→ /opsx-apply
→ implementation verification + focused tests
→ strict validation of the active change
→ archive on the feature branch (sync approved delta specs)
→ inspect archived artifacts + live specs
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

## Implementation verification and archive

After `/opsx-apply`, finish every approved task and validate that implementation behavior matches the approved scenarios before PR preparation:

1. Run the installed official OpenSpec implementation verifier (for example, `/opsx-verify <change>`) when available. Also map each acceptance criterion/scenario to code and a proving test; report unavailable automated checks as NOT RUN.
2. Run strict validation on the active change using the command supported by the installed OpenSpec version.
3. On the issue feature branch, run the installed official archive command (for example, `/opsx-archive <change>` or its documented CLI equivalent). Archive only after tasks, tests, verification and strict validation pass. Sync only the already approved delta specs.
4. Inspect the diff: retain the completed change under `openspec/changes/archive/`, and reflect its approved delta in the corresponding live `openspec/specs/` files. Keep both in the same feature PR; do not create a separate archive PR.
5. If archive reveals a material behavior/design change beyond the approved delta, stop and obtain renewed approval. If the installed tool lacks an implementation verifier, keep an explicit evidence matrix instead of inventing a command.

Archive is a post-implementation, pre-PR closeout in this workflow. Do not defer routine archival until after merge. If tests, tasks or verification are incomplete, keep the change active and report the blocker.

If evidence requires a behavioral or architectural change, stop the affected implementation, update and validate OpenSpec, adjust tasks, then resume. Implementation-only fixes do not create artificial spec churn.

## Output

Report change reused/created, artifacts touched, commands/validation actually run, unresolved discrepancies and either `READY FOR APPLY` or `NOT READY FOR APPLY — <reason>`.
