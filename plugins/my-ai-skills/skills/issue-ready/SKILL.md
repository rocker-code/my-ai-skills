---
name: issue-ready
description: Reassess a GitHub issue after discovery and decisions, enforce a Definition of Ready, and determine whether OpenSpec proposal work may begin. Use after questions were answered or immediately before /opsx-proposal; never implements code.
metadata:
  category: workflow
  stage: ready
---

# Issue Ready

This is the gate between discovery and OpenSpec proposal. It does not implement code and does not replace OpenSpec.

## Mandatory refresh and second exploration

Re-fetch the complete issue and all current comments. Treat approved `[DECISION]` comments as authoritative and verify that each materially affects the issue, OpenSpec plan or acceptance criteria as needed.

Re-run the official `/opsx-explore` command against the latest repository and existing OpenSpec, applying the `issue-explore` protocol. For material work, this second exploration after decisions is mandatory; answers may expose new contradictions.

## Definition of Ready

Verify with evidence:

```text
[ ] objective and problem are explicit
[ ] expected behavior is observable
[ ] scope and non-goals are explicit
[ ] current implementation was inspected
[ ] existing/native mechanisms to reuse were identified
[ ] business rules and authorization are defined when relevant
[ ] API/GraphQL/data contracts are defined when relevant
[ ] state transitions and invariants are defined when relevant
[ ] errors and localization ownership are defined when relevant
[ ] edge cases, compatibility and migration are understood
[ ] dependencies and cross-repository order are known
[ ] tests and acceptance criteria are testable
[ ] approved decisions are recorded
[ ] no blocking question remains
```

Do not weaken the checklist because an implementation appears small. Mark irrelevant items `N/A` with a reason.

## Failure behavior

For a missing material decision, add/propose a `[QUESTION]` and stop. For a documentation gap whose answer is already explicit, update/propose the issue text without inventing new requirements.

## Output

Return the checklist, unresolved gaps and the next OpenSpec action. End with exactly one:

```text
READY FOR PROPOSAL
```

or

```text
NOT READY — <blocking reason>
```
