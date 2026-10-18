---
name: issue-explore
description: Supply the supervised GitHub workflow and question gate used when the CLI runs OpenSpec's official /opsx-explore command. Use before proposal or coding to inspect issue, code, tests and OpenSpec without implementing, then return READY FOR PROPOSAL or BLOCKED BY QUESTIONS.
metadata:
  category: workflow
  stage: discovery
---

# Issue Explore

This skill augments, but never replaces, OpenSpec's official CLI command:

```text
/opsx-explore <GitHub issue URL>
```

When operating in the CLI, execute exploration through `/opsx-explore`; apply the GitHub markers, question gate and output contract below around that command. Do not introduce or instruct the user to run a competing `/issue-explore` command.

Explore before proposing or coding. **Never implement during exploration.** Do not modify production code, generate an apply change, open a PR or silently decide ambiguous business behavior.

## Input

Accept an issue URL, `owner/repo#number`, or a number inferred from the current repository.

## Refresh first

Fetch the live issue, all comments and linked items. Read comments newer than any previous execution. Recognize `[QUESTION]`, `[DECISION]`, `[IMPLEMENTATION NOTE]` and `[RESOLVED]`; the latest explicit approved decision wins when discussion conflicts.

## Inspect current reality

Read applicable repository instructions and trace the affected runtime path through code, tests, configuration, schemas and documentation. Locate active OpenSpec changes by issue number, branch, capability and domain terms. Do not create a duplicate change.

Identify:

- current behavior and intended change;
- existing components and framework-native mechanisms to reuse;
- affected boundaries, contracts, state, data and authorization;
- compatibility, migration, concurrency and operational risks;
- obsolete code that replacement would remove;
- expected unit/integration/E2E evidence;
- contradictions among issue, decisions, code, tests and OpenSpec.

For work that crosses repositories or consumes another system's behavior, invoke contract-handoff in design-review mode. Map each consumer scenario (including wireframes and approved decisions) to the producer's public operation, fields, state/error, and authoritative enforcement point. Record producer and consumer issue links and a hard dependency in the OpenSpec exploration. If a required signal or behavior is absent, implicit, or unimplemented, identify the exact producer follow-up and do not release the dependent proposal. Do not require unrelated issues to wait.

Check security/correctness at the boundary when relevant: authorization and ownership, sensitive-data exposure, stale reads, retry/idempotency, concurrency, partial failure, and revalidation at commit.

Load a relevant domain skill such as `magento-review` or `expo-mobile-review` when the repository matches it.

## Question gate

Do not infer a decision when alternatives materially change behavior, public contracts, data, authorization, concurrency, compatibility or scope. Add a GitHub comment using `[QUESTION]` and [the question template](references/question.md) when authorized to comment; otherwise provide the exact proposed comment.

Group related questions, include evidence and trade-offs, and stop. Recommendations are allowed but are not decisions.

Implementation details that follow established project conventions are not automatically blocking questions.

## Output

Report:

- objective and scope/non-goals;
- current implementation and reuse points;
- affected contracts and architecture;
- risks/edge cases/tests;
- OpenSpec change found or needed;
- questions created or proposed.

End with exactly one:

```text
READY FOR PROPOSAL
```

or

```text
BLOCKED BY QUESTIONS
```
