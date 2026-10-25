---
name: chatgpt-web-create-issue
description: ChatGPT Web-only issue authoring from conversational requirements. Research repository context, design a detailed implementation-ready GitHub issue and create it using the GitHub connector. Do not run in CLI agents.
metadata:
  category: chatgpt-web
  stage: backlog
  runtime: chatgpt-web-only
---

# Create GitHub Issue — ChatGPT Web

**Audience:** ChatGPT Web as backlog/product/architecture supervisor, not Codex CLI, Claude Code or OpenCode. It does not implement code, create OpenSpec changes or open implementation PRs.

Read [the ChatGPT Web issue authoring protocol](references/CHATGPT_WEB_ISSUES.md) and apply its default issue standard. For UI work also read [the visual artifact protocol](references/VISUAL_ARTIFACTS.md). Reuse the existing `refine-issue` conventions for requirements and `resolve-questions` for approved decision records; do not replace execution-side issue-audit or OpenSpec.

## Trigger

User asks to create, register, break down or plan a feature/bug/UI improvement as GitHub issues in this conversation. Prefer this skill over a generic unstructured ticket.

## Steps

1. Identify the intended repository, issue type, milestone and actual scope from user context; never default silently to Magento when mobile/operational app is indicated. Inspect live repository issues, labels, milestones, code and related PRs using the connected GitHub tools as available. Avoid duplicate or contradictory tickets.
2. Restate intent in straightforward language; distinguish what is an approved product decision from assumptions or open questions. For routine engineering details, propose pragmatic defaults that fit existing architecture. Ask only about blocking material product decisions.
3. Draft complete Markdown with a short opening summary (what/where/dependencies), current implementation and inspected commit links, concrete expected behavior, scope/non-goals, observable acceptance and a representative scenario table (preparation/action, expected result, suggested proving layer). Identify existing code/tests to reuse or update. For UI changes include a character wireframe and accessible approved design assets/target views when available; label illustrative data and proposed layouts. For backend/integration/architecture changes include a compact Mermaid system design. Apply conditional sections proportionately.
4. For Magento↔mobile or app operacional integration, trace consumer scenarios to the producer API/GraphQL contract, including current → expected signature, types/nullability, examples and state/error boundaries. Label proposed shapes as unimplemented/unfrozen; never invent verified API fields. Create linked producer/consumer issues when needed, state dependency order and require the effective contract in the consumer issue after final handoff. Reconcile behavior, diagrams/wireframes, contract, acceptance and test scenarios before creation.
5. Prefer existing repository labels/milestone; do not invent a label or milestone assignment. Preserve user's standing convention for issue assignee only after checking it is valid for the target repository. Create issue(s) when requested using the connected GitHub action, without an extra approval round when intent is clear.
6. Fetch/verify created issue(s) or creation result, then give exact URLs, succinct scope and any remaining blockers. Never claim an issue exists without tool confirmation.

## Quality bar

For user-facing text changes, apply the protocol's **i18n and translation** standard: inspect the existing localization mechanism, record app/API text ownership and require translated states/errors/accessibility, safe unknown-code fallbacks and local formatting/plurals. Include corresponding acceptance criteria and representative scenarios; do not assume backend descriptions are already localized or translate domain names.

An executing agent should know **what** to implement, **where**, **what must remain unchanged**, **how to verify**, and **which dependencies must land first**, without repeated owner questions. This is not permission to invent contract or policy.
