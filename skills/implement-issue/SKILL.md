---
name: implement-issue
description: Implement a GitHub issue end-to-end using an OpenSpec-first workflow. Use when asked to implement, develop, execute, or continue work on a GitHub issue. Reads the complete issue and discussion, inspects the existing repository, creates or updates the OpenSpec change before production code when OpenSpec is available, validates proposal/spec/design/tasks, then implements, tests, validates acceptance criteria, and leaves the work ready for a pull request.
compatibility: OpenCode or another coding agent with GitHub, repository, Git, and OpenSpec access
metadata:
  category: workflow
  workflow: issue-to-implementation
  methodology: openspec-first
---

# Implement Issue

Implement a GitHub issue completely and safely using an **OpenSpec-first** development workflow.

This skill is an orchestration skill. It coordinates requirements discovery, repository analysis, OpenSpec, technical skills, implementation, tests, validation, and PR readiness.

The default behavior is **not** to start coding immediately.

When the repository uses OpenSpec, production code must not be modified until the issue has been reconciled with the current implementation and the relevant OpenSpec change is ready for implementation.

## Core workflow

```text
GitHub Issue + comments
        ↓
inspect repository and current behavior
        ↓
reconcile requirements with code/tests/docs
        ↓
OpenSpec change
        ↓
proposal / specs / design / tasks
        ↓
OpenSpec validation + implementation readiness gate
        ↓
implementation
        ↓
tests + static validation
        ↓
diff review + acceptance criteria
        ↓
PR READY
```

The OpenSpec stage is a **gate**, not optional documentation generated after coding.

# When to use

Use this skill when the user asks to:

- implement a GitHub issue;
- develop an issue;
- execute issue `#123`;
- continue an implementation from an issue;
- turn an approved GitHub issue into working code;
- prepare an issue implementation for a pull request.

Typical inputs:

```text
implement issue 123
implement #123
implement https://github.com/owner/repo/issues/123
```

# Sources of truth

Use these sources with distinct responsibilities.

## GitHub Issue — requested intent and scope

Read the complete issue and relevant discussion:

- title;
- body;
- acceptance criteria;
- comments;
- linked issues/PRs when material;
- labels/milestone when useful.

The latest explicit product or architectural decision supersedes older conflicting discussion.

Never implement from the title alone.

## Repository — current implementation reality

The repository tells you how the system currently works.

Inspect before designing.

Do not assume the issue accurately describes the current implementation.

## OpenSpec — approved behavioral and architectural contract

When OpenSpec exists, it is the contract that must bridge requested intent and implementation.

The required sequence is:

```text
requirements
→ specification
→ implementation
```

not:

```text
requirements
→ implementation
→ retroactive specification
```

## Tests — executable evidence

Tests describe expected and compatibility behavior, but may also be stale. Reconcile them with the approved issue and OpenSpec instead of blindly treating either code or tests as desired behavior.

## Repository instructions — local engineering rules

Read applicable files such as:

```text
AGENTS.md
CLAUDE.md
README.md
CONTRIBUTING.md
.github/
.opencode/
openspec/
.openspec/
docs/
```

# Mandatory phase 1 — Retrieve and understand the issue

Resolve the repository and issue from:

- issue number;
- `#<number>`;
- full URL.

Use available GitHub tooling. Retrieve the complete issue and all relevant comments.

Build an internal requirement model containing:

- objective;
- functional requirements;
- non-functional requirements;
- acceptance criteria;
- constraints;
- explicit non-goals;
- dependencies;
- architectural decisions;
- unresolved questions.

Do not ask the user to repeat information that can be obtained from GitHub or the repository.

# Mandatory phase 2 — Inspect the repository before proposing changes

Before editing production code, inspect:

- repository status and branch;
- relevant modules/components;
- existing implementation;
- entrypoints;
- application/domain services;
- persistence/integrations;
- tests;
- configuration;
- existing OpenSpec artifacts;
- related architecture documentation.

Trace the affected runtime path.

For backend work, understand roughly:

```text
entrypoint
→ auth/validation
→ application/domain behavior
→ persistence/integration
→ response
```

For frontend/mobile work, understand roughly:

```text
route/screen
→ state/form
→ API/service
→ domain/transformation
→ rendering/navigation
```

Identify what should be reused, changed, migrated, or removed.

Do not introduce parallel architecture merely because creating something new is easier than understanding what exists.

# Mandatory phase 3 — Reconcile issue, implementation, tests, and specifications

Compare:

```text
Issue + comments
↔ repository
↔ tests
↔ existing OpenSpec
↔ project documentation
```

Resolve material inconsistencies before implementation.

Classify discrepancies such as:

- repository evolved but requirement remains valid;
- original requirement was superseded by later discussion;
- current implementation conflicts with the requested target architecture;
- OpenSpec is stale;
- tests represent obsolete behavior;
- unrelated inconsistency outside issue scope.

Do not broaden scope to repair unrelated architecture.

# Mandatory phase 4 — OpenSpec-first gate

Detect whether the repository uses OpenSpec.

If OpenSpec is present, **load and follow the `openspec-workflow` skill before implementation**.

This is mandatory unless the user explicitly instructs otherwise.

## Find or create the change

First search for an existing OpenSpec change using:

- issue number;
- feature/domain terminology;
- branch name;
- related capability/module.

Reuse the existing applicable change instead of creating a duplicate.

If no suitable change exists, create one according to the repository's OpenSpec conventions.

## Translate the issue into OpenSpec

Use the GitHub issue as input, not as a replacement for specification.

The OpenSpec artifacts should make the agreed solution explicit before implementation.

Depending on the repository workflow, this can include:

- proposal;
- capability/spec delta;
- scenarios;
- design/architecture decisions;
- implementation tasks;
- migration/compatibility notes.

The specification should cover relevant behavior such as:

- actors/callers;
- preconditions;
- expected results;
- domain invariants;
- state transitions;
- validation and error behavior;
- API contracts;
- persistence semantics;
- concurrency/atomicity when relevant;
- edge cases;
- compatibility;
- explicitly removed behavior;
- non-goals.

## Design before code

If the issue contains architectural change, use the OpenSpec design artifacts to explicitly decide:

- ownership/responsibility;
- existing components to reuse;
- components to remove;
- interfaces/contracts;
- state/data model changes;
- transaction boundaries;
- concurrency strategy;
- migration strategy;
- framework-native mechanisms;
- compatibility trade-offs.

Do not allow these decisions to emerge accidentally while writing code.

## Tasks before code

Implementation tasks must be concrete and traceable to requirements/specification.

Tasks should include, when relevant:

- production changes;
- tests;
- data/schema changes;
- API/schema changes;
- cleanup/removal of obsolete implementation;
- documentation/configuration;
- validation.

## Readiness gate

Before editing production code, verify all of the following:

```text
[ ] issue and comments are understood
[ ] current implementation was inspected
[ ] applicable OpenSpec change was found or created
[ ] requested behavior is represented in specs/scenarios
[ ] important architectural decisions are represented when needed
[ ] implementation tasks exist and are coherent
[ ] obvious contradictions have been reconciled
[ ] OpenSpec validation passes when tooling supports it
```

Only after this gate passes may implementation begin.

If OpenSpec validation cannot run because of an environmental/tooling limitation, inspect the artifacts manually and report that limitation. Do not silently skip the specification stage.

## If OpenSpec is absent

If the repository genuinely does not use OpenSpec, do not introduce it automatically. Follow the remaining workflow with an explicit implementation plan before code.

# Mandatory phase 5 — Select technical skills

This skill orchestrates the workflow; it does not contain every domain rule.

Discover and load only the technical skills relevant to the implementation.

Examples can include:

- clean architecture;
- clean code;
- DDD;
- Magento/Adobe Commerce specialists;
- frontend/mobile specialists;
- API/GraphQL skills;
- security;
- performance;
- database/data modeling;
- testing;
- Git/GitHub conventions.

Prefer the smallest useful set.

Priority when instructions conflict:

1. explicit user decision;
2. repository-specific instructions;
3. approved OpenSpec contract;
4. framework/domain skill;
5. generic engineering skill.

# Mandatory phase 6 — Implement from OpenSpec tasks

Once the readiness gate passes, implement the change by following the OpenSpec tasks and the approved design/specification.

Do not treat tasks as suggestions unrelated to code. They are the implementation checklist.

## Implementation principles

- Prefer native framework mechanisms where practical.
- Extend existing architecture before creating parallel abstractions.
- Centralize domain invariants.
- Preserve transaction boundaries and data integrity.
- Explicitly analyze concurrency for reservations, inventory, payment, order state, uniqueness, counters, or shared resources.
- Avoid unrelated refactoring.
- Do not leave obsolete code behind when the approved change replaces it.
- Do not keep two sources of truth for the same behavior merely for convenience.

## Keep OpenSpec synchronized

If implementation reveals that the approved behavior/design must change:

```text
STOP implementation of that affected behavior
        ↓
update OpenSpec
        ↓
validate/reconcile specification
        ↓
update tasks if required
        ↓
resume implementation
```

Never finish coding first and update the spec afterward merely to match what was built.

# Mandatory phase 7 — Tests and validation

Tests are implementation tasks, not optional cleanup.

Add or update coverage based on changed behavior and risk.

Consider:

```text
happy path
validation failures
edge/boundary cases
authorization
state transitions
error handling
regression behavior
atomicity/concurrency when relevant
```

Run the narrowest high-confidence checks first, then broader checks as appropriate.

Possible checks include:

- unit tests;
- integration tests;
- type checking;
- lint;
- static analysis;
- schema validation;
- build/compile;
- OpenSpec validation.

Respect repository-specific restrictions such as suites that should not be executed locally.

Never claim a validation passed unless it actually ran successfully.

# Mandatory phase 8 — Review implementation against OpenSpec

Before declaring completion, perform a deliberate three-way review:

```text
GitHub acceptance criteria
↔ OpenSpec requirements/tasks
↔ final code/tests
```

Inspect the full diff and verify:

- every change maps to the approved scope;
- no requirement was missed;
- no accidental behavior was added;
- no obsolete implementation remains when removal was required;
- tests represent the final behavior;
- OpenSpec still matches implementation;
- tasks accurately reflect completion;
- unrelated working-tree changes are not included.

Internally classify every acceptance criterion:

```text
PASS
PARTIAL
FAIL
NOT APPLICABLE
```

Do not declare completion with required criteria in `PARTIAL` or `FAIL`.

# Mandatory phase 9 — PR readiness

The default endpoint is **PR READY**, not automatic PR creation.

The implementation is PR-ready only when:

- issue requirements are satisfied;
- OpenSpec is synchronized when present;
- required OpenSpec tasks are complete;
- relevant validation was executed;
- final diff was reviewed;
- acceptance criteria pass;
- no known implementation blocker remains.

Do not archive the OpenSpec change merely because implementation is complete unless repository workflow explicitly requires archival at this stage.

Create a PR only when the user or repository workflow asks for it.

# Working-tree and Git safety

Before changing files:

- inspect `git status`;
- preserve unrelated local modifications;
- do not reset or overwrite user work.

Before PR readiness:

- inspect final `git status`;
- inspect the complete diff;
- exclude unrelated/generated/local files;
- follow repository commit conventions when committing.

# Prohibited behavior

Do not:

- start writing production code immediately after reading the issue;
- implement before inspecting the existing architecture;
- skip OpenSpec when the repository uses it;
- create a spec only after implementation to document whatever was coded;
- treat OpenSpec tasks as optional;
- implement from the issue title alone;
- ignore issue comments;
- invent requirements;
- silently broaden scope;
- create duplicate architecture without examining existing mechanisms;
- blindly preserve legacy code that the approved change replaces;
- blindly change legacy behavior merely because it looks old;
- claim tests or validation passed when they did not run;
- mark acceptance criteria complete without checking them;
- discard unrelated local modifications;
- automatically archive OpenSpec changes unless required;
- automatically close the issue unless explicitly requested.

# Completion report

Return a concise structured report.

## Issue

- issue number/title;
- objective implemented.

## OpenSpec

Report one of:

```text
Reused change: <name>
Created change: <name>
OpenSpec not present
```

Then report:

- specs/design/tasks updated;
- OpenSpec validation result;
- whether implementation matches the final contract.

## Implementation

Summarize important components changed or removed and key architecture decisions.

## Validation

List only checks actually executed and their real result.

Example:

```text
PASS targeted unit tests
PASS static analysis
PASS OpenSpec validation
NOT RUN functional suite — excluded by repository instructions
```

## Acceptance criteria

State whether all required criteria passed and mention any exception.

## Status

Finish with exactly one:

```text
READY FOR PR
```

or

```text
NOT READY FOR PR — <concrete blocker>
```
