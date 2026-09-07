---
name: pr-status
description: Inspect the current state of a GitHub pull request and summarize issue linkage, branch state, OpenSpec status, CI/checks, review feedback, and the exact next action. Use before continuing work on an existing PR or when asked what remains to be done.
compatibility: OpenCode or another coding agent with Git and GitHub access
metadata:
  category: workflow
  workflow: pull-request-status
---

# Pull Request Status

Produce an evidence-based status of an existing pull request without modifying code or GitHub state unless explicitly requested.

## Inputs

Accept:

- PR number;
- `#<number>`;
- full GitHub PR URL.

Infer the repository from the current worktree when possible.

## Inspect

Retrieve and correlate:

- PR title and state;
- base/head branches;
- draft/merge state when available;
- associated issue(s);
- PR description;
- changed files and current diff summary;
- review decisions;
- inline review comments/threads;
- top-level PR comments;
- CI/check status when available;
- local branch/worktree state when operating inside the repository;
- OpenSpec change associated with the issue/branch/feature when present.

Read the linked issue and relevant comments if they affect whether the PR is complete.

## Determine implementation completeness

Compare the PR against:

```text
GitHub issue + comments
↔ OpenSpec
↔ current PR diff
↔ tests/checks
↔ review findings
```

Identify:

- acceptance criteria apparently satisfied;
- criteria still missing;
- review findings still applicable;
- review comments already made obsolete by later commits;
- CI failures caused by this branch;
- unrelated/pre-existing CI failures when distinguishable;
- missing OpenSpec synchronization;
- branch or merge blockers.

Do not treat an old unresolved comment as automatically actionable if the current diff already addresses it.

## Status classification

Use the most accurate high-level state:

### READY FOR REVIEW

Implementation appears complete and validation is sufficient; waiting for reviewer action.

### NEEDS FIXES

One or more valid review findings or requirement gaps remain.

### CI BLOCKED

Required checks are failing or incomplete and currently block confidence/merge.

### SPEC BLOCKED

OpenSpec/behavioral contract is inconsistent or incomplete.

### READY TO MERGE

Requirements, review, and required checks appear satisfied and no known blocker remains.

### DRAFT / IN PROGRESS

The PR intentionally remains incomplete.

### UNKNOWN / INSUFFICIENT EVIDENCE

Available tooling/data cannot establish a reliable state.

## Recommend exactly one next action

Prefer one concrete action, for example:

```text
Run `address-pr-review` for PR #246.
Fix the failing integration test before further review.
Update the OpenSpec change to reflect the revised order-status contract.
Request/perform another review; no implementation blocker remains.
Merge the PR if repository policy permits.
```

Do not produce a vague list of possible next steps when one is clearly dominant.

## Output

Use a compact structure:

```text
PR: #246 — <title>
State: NEEDS FIXES
Issue: #245
OpenSpec: <change-name> — synchronized / needs update / not present
CI: PASS / FAIL / PARTIAL / UNKNOWN
Review: <n> actionable findings, <n> obsolete/already resolved
Local branch: clean/dirty/unknown

Blockers:
- ...

Next action:
<single recommended action>
```

When useful, list the unresolved findings with severity or affected area, but do not duplicate the entire review discussion.

## Read-only rule

This skill is read-only by default.

Do not:

- edit code;
- resolve comments;
- push commits;
- create a new PR;
- change issue state;
- merge.

If the user explicitly asks for one of those actions, invoke the appropriate workflow rather than silently extending `pr-status`.
