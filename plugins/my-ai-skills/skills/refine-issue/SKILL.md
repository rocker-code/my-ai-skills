---
name: refine-issue
description: Refine an idea or existing GitHub issue into a detailed, implementation-ready work item without coding. Use in ChatGPT/Claude Web or another supervisory agent to inspect current code/context, clarify scope and acceptance criteria, and update or draft the issue.
metadata:
  category: web-supervision
  stage: discovery
---

# Refine Issue

Create the best available source of requested intent before executor exploration. Do not implement code or create OpenSpec artifacts; OpenSpec follows after readiness.

Read the existing issue/comments and inspect relevant repository/code/docs when access exists. Preserve valid existing content and later decisions.

Define:

- problem, objective and user/business value;
- current vs expected behavior;
- scope and explicit non-goals;
- business rules, actors and authorization;
- states/transitions/invariants;
- API/GraphQL/data contract when known;
- errors and localization ownership;
- compatibility, migration, concurrency and edge cases;
- affected components and reuse expectations;
- test expectations and observable acceptance criteria;
- dependencies and cross-repository order;
- decisions taken and genuinely open questions.

Use an `Integration Contract` section for producer/consumer issues. Do not invent decisions merely to make the issue appear complete; label them `[QUESTION]`.

When authorized, update/create the GitHub issue. Otherwise output a copy-ready title/body. Finish with `READY FOR OPSX EXPLORE` or `NEEDS DECISIONS — <summary>`.
