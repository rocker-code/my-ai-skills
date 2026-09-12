---
name: implement-issue
description: Implement or continue a GitHub issue through an OpenSpec-first gated workflow. Use after discovery/decisions to resume completed checkpoints, validate the approved proposal/spec/design/tasks, implement code and tests, and finish READY FOR PR without guessing material requirements.
metadata:
  category: workflow
  stage: implementing
  methodology: openspec-first
---

# Implement Issue

Implement safely without restarting completed work. OpenSpec is mandatory when the repository uses it and remains the pre-code contract.

## Refresh and route

Fetch the live issue, all comments and linked PRs before acting. Read repository instructions and status. Then route:

- existing PR → use review/fix workflows, not a duplicate implementation/PR;
- existing implementation → inspect and resume;
- matching validated OpenSpec change → reuse it;
- unresolved `[QUESTION]` or Definition of Ready gap → run `/opsx-explore`, apply the `issue-explore` protocol, then use `issue-ready` and stop;
- ready issue with no approved proposal → run `openspec-workflow` through proposal review;
- approved proposal → continue to apply.

Treat latest `[DECISION]` comments as authoritative. Never infer material product or architecture decisions.

## Pre-code gate

Production code may change only when:

```text
[ ] live issue/comments were refreshed
[ ] current runtime path and tests were inspected
[ ] issue-ready passed
[ ] OpenSpec proposal/spec/design/tasks are coherent when OpenSpec exists
[ ] proposal checkpoint was reviewed when required
[ ] OpenSpec validates or the tooling limitation is explicit
[ ] no blocking question remains
```

If the repository has no OpenSpec, do not install it automatically; create an explicit implementation plan first.

## Domain analysis

Load only relevant technical skills. Use `magento-review` for Adobe Commerce/Magento and `expo-mobile-review` for Expo/React Native. Prefer existing project/framework mechanisms over parallel abstractions.

## Implement

- follow approved issue decisions and OpenSpec;
- make the smallest coherent change;
- preserve module/boundary conventions;
- update public contracts, data and configuration deliberately;
- remove obsolete code when replacement is in scope;
- avoid unrelated refactoring;
- add tests that prove behavior rather than only implementation shape;
- never weaken existing assertions simply to pass.

If implementation reveals a new contract decision, stop the affected work, record a question/decision, update OpenSpec and revalidate before resuming.

## Validate and self-review

Run targeted checks first and broader permitted checks as justified. Record PASS/FAIL/NOT RUN honestly. Compare:

```text
issue + decisions ↔ OpenSpec ↔ final diff ↔ tests
```

Verify acceptance criteria, compatibility, failure paths, cleanup, no accidental files/secrets/debug code and no unjustified complexity.

Do not open a PR unless asked; hand off to `prepare-pr` for PR creation.

## Completion

Report implementation, OpenSpec status, files/areas changed, validations actually executed, acceptance criteria and remaining blockers. End with exactly one:

```text
READY FOR PR
```

or

```text
NOT READY FOR PR — <concrete blocker>
```
