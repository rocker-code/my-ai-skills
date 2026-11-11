---
name: refine-issue
description: Refine an idea or existing GitHub issue into a detailed, implementation-ready work item without coding. Use in OpenCode, Codex CLI, Claude Code, ChatGPT/Claude Web or another supervisory agent to inspect current code/context, clarify scope and acceptance criteria, and update or draft the issue.
metadata:
  category: web-supervision
  stage: discovery
---

# Refine Issue

Create the best available source of requested intent before executor exploration. Do not implement code or create OpenSpec artifacts; OpenSpec follows after readiness.

## CLI routing

In OpenCode, Codex CLI or Claude Code, before drafting or editing read [the existing issue authoring protocol](references/CHATGPT_WEB_ISSUES.md) and apply its principles, default issue standard, evidence/reuse rules, conditional sections, authoring template, GitHub conventions and refinement completion requirements. This entry explicitly applies those authoring requirements in the CLI: the protocol's Web audience/runtime wording does not prohibit this use or require a Web connector. Use the available authorized GitHub CLI/MCP integration instead; do not invoke the Web-only skills.

For CLI UI work also read [the visual artifact protocol](references/VISUAL_ARTIFACTS.md). Resolve bundled references relative to this skill. Require the opening summary, inspected revision/evidence, expected behavior, scope/non-goals, observable acceptance and scenario table with ID, preparation/action, expected result and suggested layer. Apply contracts, Mermaid, wireframes and i18n only when relevant; do not substitute an execution checklist for the shared standard. Reconcile these sections before publishing, read back the result and report links/blockers without claiming unavailable evidence. Preserve unrelated valid content and approved decisions on narrow edits; do not expand a targeted correction into a full rewrite.

New CLI issues use `create-issue`. Implementation requests retain their existing execution/OpenSpec routing. Web refinement keeps its existing entry and behavior; these additional routing instructions apply only to CLI authoring.

## Refinement

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
