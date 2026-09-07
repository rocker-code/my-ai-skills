---
name: implement-issue
description: Implement a GitHub issue end-to-end in the current repository. Use when asked to implement, develop, execute, or continue work on a GitHub issue. Reads the complete issue and discussion, inspects the current codebase, uses OpenSpec when present, selects relevant installed technical skills, implements the change, validates acceptance criteria, runs appropriate checks, and leaves the work ready for a pull request.
---

# Implement Issue

Implement a GitHub issue completely and safely in the current repository.

This is a workflow/orchestration skill. It coordinates issue discovery, repository analysis, OpenSpec, implementation, testing, validation, and PR readiness.

It does not replace specialized technical skills. Discover and use the relevant installed skills for the actual domain and technology instead of duplicating their guidance here.

## When to use

Use this skill when the user asks to:

- implement a GitHub issue;
- develop an issue;
- work on issue `#123`;
- execute the requirements from an issue;
- continue implementation of an issue;
- turn a GitHub issue into working code;
- prepare an implemented issue for a pull request.

Typical invocations include:

```text
implement issue 123
implement #123
implement https://github.com/owner/repo/issues/123
```

## Expected outcome

Unless a concrete blocker prevents completion, finish with:

1. requirements understood from the complete issue and discussion;
2. current implementation inspected;
3. OpenSpec created or updated when required and available;
4. appropriate technical skills selected;
5. production code implemented;
6. obsolete code removed when replacement/removal is part of scope;
7. relevant tests added or updated;
8. appropriate validation executed;
9. final diff reviewed;
10. every acceptance criterion verified;
11. repository left ready for a pull request.

Do not stop after planning when the request is to implement.

# Sources of truth

Use the following precedence model.

## Requested scope

The GitHub issue is the primary source for what the user wants changed.

Read:

- issue title;
- complete issue body;
- acceptance criteria;
- labels and milestone when useful;
- all relevant issue comments;
- linked issues or PRs when they materially affect the requirement.

Never implement from the title alone.

Issue comments may contain later decisions that supersede the original description.

## Behavioral contract

When OpenSpec is present, treat the applicable OpenSpec artifacts as the behavioral and architectural contract.

If the issue contains a newer explicit behavioral decision that conflicts with OpenSpec, update OpenSpec before or alongside implementation.

Do not silently let implementation details become the specification.

## Current implementation reality

The repository is authoritative for how the system currently works.

Inspect existing code before designing changes. An issue may describe an older version of the architecture.

## Project conventions

Repository-level instructions override generic workflow preferences when they do not contradict the requested behavior.

Look for files such as:

```text
AGENTS.md
CLAUDE.md
README.md
CONTRIBUTING.md
.opencode/
.github/
openspec/
.openspec/
docs/
```

# Workflow

## 1. Resolve the issue and repository

Accept any of:

- issue number;
- `#<number>`;
- full GitHub issue URL.

If only a number is provided, infer the repository from the current Git worktree.

If a full URL is provided, use the repository identified by that URL.

Use available GitHub tooling, preferably GitHub CLI or native GitHub integrations already available in the environment.

Retrieve the complete issue and comments.

Do not ask the user to paste content that can be retrieved directly.

## 2. Establish repository state

Before editing, inspect:

- repository root;
- current branch;
- default branch when relevant;
- remote repository;
- working-tree status;
- project/runtime/framework;
- test infrastructure;
- static analysis and lint tooling;
- repository instructions;
- OpenSpec presence;
- relevant architecture.

Do not discard, overwrite, stage, or accidentally include unrelated local changes.

If the worktree contains unrelated modifications, preserve them and isolate your changes as much as practical.

## 3. Build a requirement model

Before implementation, derive an internal model of the issue.

Identify:

### Objective

What outcome must exist when the issue is complete?

### Functional requirements

What behavior must be added, changed, migrated, or removed?

### Non-functional requirements

Consider explicit requirements involving:

- security;
- concurrency;
- performance;
- observability;
- accessibility;
- maintainability;
- compatibility;
- data integrity.

### Acceptance criteria

Extract every explicit criterion, including criteria added or clarified in comments.

### Constraints

Identify requirements such as:

- reuse a specific existing service;
- use native framework behavior;
- preserve API compatibility;
- avoid a particular implementation;
- do not run a certain test suite;
- avoid schema changes;
- maintain a specific state transition model.

### Non-goals

Record things explicitly excluded from the issue.

Do not implement them opportunistically.

### Dependencies

Identify related:

- issues;
- modules;
- packages;
- APIs;
- integrations;
- database entities;
- shared services;
- frontend screens;
- configuration.

### Open questions

Resolve ambiguity from the issue, comments, repository, tests, OpenSpec, and project documentation before asking the user.

Do not ask questions already answered by repository evidence or prior issue discussion.

## 4. Inspect the existing implementation

Search for the current implementation before proposing a new one.

Use domain terminology and identifiers from the issue to locate:

- classes;
- interfaces;
- services;
- models;
- database tables;
- GraphQL operations;
- REST endpoints;
- controllers;
- commands;
- jobs;
- event handlers;
- configuration;
- UI screens;
- hooks/state;
- tests.

Trace the relevant execution flow.

For backend work, understand the path roughly as:

```text
entrypoint
→ authorization/validation
→ application/domain logic
→ persistence/integration
→ response
```

For frontend/mobile work, understand the path roughly as:

```text
route/screen
→ state/form
→ service/API
→ transformation/domain logic
→ rendering/navigation
```

Identify existing extension points and reusable abstractions.

Prefer extending the current architecture over introducing a parallel implementation.

## 5. Reconcile issue, code, tests, and specifications

Compare:

```text
GitHub issue
↔ issue comments
↔ OpenSpec
↔ repository
↔ tests
```

Classify material discrepancies.

### Repository evolved, requirement still valid

Adapt the solution to the current architecture while preserving the requested outcome.

### Requirement was superseded

Follow the latest explicit decision.

### Current implementation conflicts with requested architecture

Change it when the issue clearly requests that refactor.

### OpenSpec is stale

Update OpenSpec when the desired observable behavior has changed.

### Unrelated inconsistency

Do not broaden scope simply to clean it up.

Record important unrelated findings in the completion report if useful.

## 6. Use OpenSpec when present

Detect whether the repository uses OpenSpec.

Common indicators include:

```text
openspec/
.openspec/
OpenSpec configuration
existing change artifacts
OpenSpec commands or documentation
```

If OpenSpec is not used by the repository, continue without inventing it.

If OpenSpec is used, inspect the repository's OpenSpec instructions and existing changes before acting.

### Find an existing change first

Search for an existing change related to:

- issue number;
- feature name;
- domain terminology;
- current branch.

Continue an applicable change instead of creating a duplicate.

### Create or update a change when appropriate

A specification change is usually warranted when the issue materially modifies:

- user-visible behavior;
- domain rules;
- API contracts;
- persistence semantics;
- state transitions;
- integration behavior;
- architectural responsibility.

A pure implementation refactor with no behavioral or contract change may not require a new spec unless repository conventions require one.

### Preferred sequence

```text
GitHub issue
→ OpenSpec proposal/change
→ specification/design/tasks
→ implementation
→ validation
```

Follow the actual OpenSpec workflow configured in the repository rather than assuming exact command names or artifact structure.

If implementation reveals a necessary behavioral change not represented by the spec, update the spec before continuing with that behavior.

## 7. Discover and use relevant technical skills

This skill orchestrates work; technical skills provide domain-specific guidance.

Inspect available installed skills and load only those relevant to the issue.

Examples may include skills for:

- clean architecture;
- clean code;
- domain-driven design;
- framework-specific development;
- APIs;
- database modeling;
- orders/payments;
- catalog;
- configuration;
- security;
- performance;
- frontend/mobile development;
- testing;
- Git/GitHub conventions.

Do not activate every skill indiscriminately.

Select the smallest useful set based on the files and behavior involved.

When skill instructions conflict, prefer in this order:

1. explicit user requirement;
2. repository-specific instructions;
3. applicable behavioral specification;
4. framework/domain-specific skill;
5. generic engineering skill.

Never use a generic architecture rule to override a required native framework pattern without a concrete reason.

## 8. Create an implementation plan

Before editing, produce a concrete internal plan mapping requirements to code changes.

Identify:

- components to modify;
- components to add;
- components to remove;
- behavior to preserve;
- APIs/schema changes;
- persistence changes;
- migration/data patch needs;
- OpenSpec changes;
- tests to add/update;
- compatibility impact;
- cleanup required by the issue.

Prefer the smallest coherent implementation.

Avoid:

- speculative abstractions;
- duplicate services;
- premature generalization;
- hidden compatibility layers;
- parallel implementations of native framework capabilities;
- leaving dead code after a requested replacement.

If the issue explicitly replaces an old implementation, include removal of obsolete code in the plan where safe and within scope.

## 9. Implement the change

Implement the plan using the repository's architecture and conventions.

### Prefer native mechanisms

Use framework-native behavior when practical rather than recreating platform features.

### Centralize invariants

Do not duplicate core business rules across multiple entrypoints.

If the same invariant applies to API, admin, CLI, job, or other paths, place it in the appropriate shared application/domain layer.

### Preserve transactional integrity

When several persistent operations represent one logical state transition, evaluate whether they must be atomic.

### Evaluate concurrency

Explicitly inspect race conditions for functionality involving:

- reservation/scheduling;
- inventory;
- payment;
- order transitions;
- uniqueness;
- counters;
- shared resources.

### Avoid unrelated refactoring

Refactor adjacent code only when required to implement the issue correctly or to avoid leaving a structurally broken solution.

## 10. Remove obsolete implementation when required

Do not treat implementation as additive by default.

If the issue changes architecture or replaces an existing mechanism, inspect whether any of the following are now obsolete:

- classes;
- interfaces;
- configuration;
- schema fields;
- database writes;
- observers/plugins/listeners;
- jobs;
- feature flags;
- compatibility branches;
- tests;
- dead methods.

Remove obsolete code when it is safe, explicitly intended, and within issue scope.

Do not retain a second source of truth merely because the old code already exists.

## 11. Add and update tests

Tests are part of implementation, not optional cleanup.

Map tests to changed behavior and regression risk.

Consider coverage for:

```text
happy path
validation failures
boundary conditions
authorization
state transitions
error handling
regressions
concurrency/atomicity when relevant
```

Prefer updating existing tests when they already model the affected behavior.

Do not weaken, delete, or skip meaningful tests just to make validation pass.

Respect repository instructions regarding suites that should not be executed locally.

## 12. Validate incrementally

Run the narrowest high-confidence checks first, then broader checks where appropriate.

Depending on the project, this may include:

- targeted unit tests;
- targeted integration tests;
- type checking;
- linting;
- static analysis;
- schema validation;
- compilation/build;
- OpenSpec validation.

Run broader suites only when appropriate for the repository, environment, issue risk, and explicit instructions.

Never claim a check passed unless it was actually executed successfully.

If a validation step cannot run because of an environmental limitation, report it accurately instead of fabricating success.

## 13. Review the complete diff

Before declaring completion, inspect the final diff and working-tree status.

Look for:

- unrelated changes;
- accidental generated files;
- duplicated logic;
- debug statements;
- temporary code;
- commented-out implementation;
- hardcoded values;
- incomplete cleanup;
- naming inconsistency;
- missing error handling;
- security issues;
- compatibility mistakes;
- excessive abstractions;
- missing tests.

Ask:

> Does every changed line contribute to satisfying the issue or keeping that implementation correct?

Remove accidental scope.

## 14. Verify every acceptance criterion

Return to the complete issue and comments after implementation.

Verify every requirement individually.

Internally classify each criterion as:

```text
PASS
PARTIAL
FAIL
NOT APPLICABLE
```

Do not declare the issue complete while a required criterion remains `PARTIAL` or `FAIL`.

Pay attention to requirements introduced in comments, not only Markdown checkboxes in the original body.

## 15. Finalize OpenSpec state

When OpenSpec is in use:

- update implementation tasks accurately;
- validate the changed artifacts;
- ensure the final implementation matches the specification;
- do not archive a change unless repository workflow or user instruction says this stage should archive it.

Do not mark tasks complete merely because files were edited.

## 16. Prepare Git state for PR

Before considering the work PR-ready:

- inspect `git status`;
- inspect the final diff;
- ensure unrelated files are excluded;
- ensure local/generated artifacts are excluded;
- confirm the branch is appropriate;
- follow repository commit conventions if committing.

Do not rewrite unrelated commits or destroy existing work.

If commit-related skills are installed, use them when they add value.

## 17. Pull request readiness

The default endpoint of this skill is **PR-ready**, not necessarily PR creation.

The work is PR-ready when:

- requested behavior is implemented;
- acceptance criteria pass;
- relevant tests/checks have been run as far as the environment allows;
- OpenSpec is consistent when applicable;
- final diff has been reviewed;
- no known implementation blocker remains.

If the user explicitly asks to create the pull request as part of the same request, create it using available GitHub tooling after validation.

Do not automatically open a PR when the user only asked to implement unless repository/project instructions explicitly define that behavior.

# GitHub interaction rules

Prefer native GitHub integrations or `gh` when available.

When retrieving the issue, make sure comments are included.

When the issue references another issue or PR whose content materially affects implementation, inspect that reference rather than guessing.

Do not post progress noise to the GitHub issue unless explicitly requested by the user or repository workflow.

Do not close the issue automatically unless the user or established project workflow requires it.

# Failure handling

## GitHub retrieval failure

If the issue cannot be retrieved:

1. verify repository and issue identifier;
2. try another available GitHub mechanism when reasonable;
3. report the exact blocker if access still fails.

Do not invent issue requirements.

## Tool or command failure

When OpenSpec, tests, linters, build tools, or other commands fail:

1. inspect the failure;
2. determine whether it is caused by the implementation;
3. fix implementation-caused failures;
4. distinguish pre-existing failures from regressions;
5. report unresolved environmental or unrelated failures.

## Existing failing checks

Do not silently absorb unrelated failures into issue scope.

Identify whether the failure is:

- pre-existing;
- caused by the current changes;
- environmental;
- directly required to fix for the issue.

## Requirement cannot be satisfied

If a requirement cannot be implemented because of a concrete technical constraint, report:

- the affected requirement;
- the constraint;
- supporting repository/tool evidence;
- impact;
- safest next step.

# Prohibited behavior

Do not:

- implement from issue title alone;
- ignore issue comments;
- assume the issue description matches current code;
- invent requirements;
- silently broaden scope;
- ask for information already available in GitHub or the repository;
- create duplicate architecture without inspecting existing code;
- replace native framework capabilities with custom infrastructure without justification;
- blindly follow stale issue text over newer explicit decisions;
- allow implementation to silently redefine OpenSpec behavior;
- mark acceptance criteria complete without verification;
- claim tests/checks passed when they were not run;
- delete unrelated local modifications;
- include unrelated files in commits or PRs;
- keep obsolete code as a second source of truth when the issue explicitly replaces it;
- stop after writing a plan when implementation was requested.

# Completion report

At the end, provide a concise structured report using the following format.

## Implementation summary

Describe the implemented outcome, not every command executed.

## Architecture

Summarize meaningful architectural decisions, especially reuse of existing components and removal/replacement of old mechanisms.

## Files/components

Summarize important components added, changed, or removed.

## OpenSpec

State one of:

```text
Updated existing change: <name>
Created change: <name>
No specification change required
OpenSpec not present
```

## Validation

Report only checks actually executed.

Example:

```text
PASS Unit tests
PASS Static analysis
PASS Lint
PASS OpenSpec validation
NOT RUN Functional tests — excluded by repository instructions
```

## Acceptance criteria

State whether all criteria were satisfied and identify any intentional or unavoidable exception.

## PR readiness

End with exactly one of:

```text
READY FOR PR
```

or:

```text
NOT READY FOR PR
```

If not ready, state the concrete blocker immediately after it.
