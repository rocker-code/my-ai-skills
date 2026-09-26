---
name: pr-status
description: Read and classify the live state of a GitHub pull request across issue decisions, OpenSpec, diff, CI and review feedback. Use when asked what remains or before resuming a PR; read-only by default and recommends exactly one next action.
metadata:
  category: workflow
  stage: review
---

# PR Status

Fetch live PR metadata, base/head, commits/diff, changed files, reviews/threads/conversation, CI, linked issue/comments, OpenSpec and local state when available. Read all updates newer than the last execution.

Correlate issue + decisions ↔ OpenSpec ↔ diff ↔ tests/checks ↔ review findings. Distinguish applicable findings from comments already resolved or made obsolete by later commits.

Classify as one:

- `DRAFT / IN PROGRESS`;
- `NEEDS FIXES`;
- `CI BLOCKED`;
- `SPEC BLOCKED`;
- `READY FOR REVIEW`;
- `READY FOR FINAL AUDIT`;
- `READY TO MERGE`;
- `UNKNOWN / INSUFFICIENT EVIDENCE`.

Output PR/title, state, issue, OpenSpec, CI, actionable/obsolete review counts, branch status, concrete blockers and exactly one dominant next action.

This skill is read-only. Do not edit, resolve threads, push, merge or change issue/PR state unless separately and explicitly requested; route correction to `github-resolution` and final eligibility to `post-pr-audit`.
