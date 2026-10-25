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

Read [the ChatGPT Web issue authoring protocol](../../protocol/CHATGPT_WEB_ISSUES.md). Reuse the existing `refine-issue` conventions for requirements and `resolve-questions` for approved decision records; do not replace execution-side issue-audit or OpenSpec.

## Trigger

User asks to create, register, break down or plan a feature/bug/UI improvement as GitHub issues in this conversation. Prefer this skill over a generic unstructured ticket.

## Steps

1. Identify the intended repository, issue type, milestone and actual scope from user context; never default silently to Magento when mobile/operational app is indicated. Inspect live repository issues, labels, milestones, code and related PRs using the connected GitHub tools as available. Avoid duplicate or contradictory tickets.
2. Restate intent in straightforward language; distinguish what is an approved product decision from assumptions or open questions. For routine engineering details, propose pragmatic defaults that fit existing architecture. Ask only about blocking material product decisions.
3. Draft complete, actionable Markdown using the protocol's issue structure, with observable acceptance, realistic representative tests, domain-specific concerns, links to dependencies, and out-of-scope items. For visual changes record immutable approved design assets (e.g. Claude Artifacts ZIP/screenshots) and target screens; a private URL alone is not a verified export.
4. For Magento↔mobile or app operacional integration, trace consumer scenarios to producer API/GraphQL contract, including state/error boundaries; create linked producer and consumer issues when needed and explicitly record dependency order. Avoid speculative API fields.
5. Prefer existing repository labels/milestone; do not invent a label or milestone assignment. Preserve user's standing convention for issue assignee only after checking it is valid for the target repository. Create issue(s) when requested using the connected GitHub action, without an extra approval round when intent is clear.
6. Fetch/verify created issue(s) or creation result, then give exact URLs, succinct scope and any remaining blockers. Never claim an issue exists without tool confirmation.

## Quality bar

An executing agent should know **what** to implement, **where**, **what must remain unchanged**, **how to verify**, and **which dependencies must land first**, without repeated owner questions. This is not permission to invent contract or policy.
