---
name: issue-explore
description: Explore a GitHub issue against its complete discussion, repository, tests, documentation and OpenSpec without implementing. Use before proposal or coding to identify reuse, risks and material questions, then return READY FOR PROPOSAL or BLOCKED BY QUESTIONS.
metadata:
  category: workflow
  stage: discovery
---

# Issue Explore

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

Load a relevant domain skill such as `magento-review` or `expo-mobile-review` when the repository matches it.

## Question gate

Do not infer a decision when alternatives materially change behavior, public contracts, data, authorization, concurrency, compatibility or scope. Add a GitHub comment using `[QUESTION]` and `templates/github/question.md` when authorized to comment; otherwise provide the exact proposed comment.

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
