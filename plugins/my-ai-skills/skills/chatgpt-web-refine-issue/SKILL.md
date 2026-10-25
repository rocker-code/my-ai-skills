---
name: chatgpt-web-refine-issue
description: ChatGPT Web-only review and refinement of existing GitHub issues, comments and implementation questions. Analyze gaps, approved decisions and dependencies, update issues and record decisions with GitHub connector. Do not run in CLI agents.
metadata:
  category: chatgpt-web
  stage: backlog
  runtime: chatgpt-web-only
---

# Refine Existing GitHub Issue — ChatGPT Web

**Audience:** ChatGPT Web as supervisor, not executor. Never edit application code or execute OpenSpec from this skill.

Read [the ChatGPT Web issue authoring protocol](references/CHATGPT_WEB_ISSUES.md) and apply its default issue standard, plus `refine-issue` and `resolve-questions` when their functions are needed. For UI work also read [the visual artifact protocol](references/VISUAL_ARTIFACTS.md). This wrapper standardizes how conversations become durable issue changes.

## Trigger

User asks to inspect an issue, clarify an agent's question, check whether it is ready, add scope/details, revise a milestone's issue definitions, or record a chosen decision.

## Steps

1. Refresh issue body, all comments, recent edits, linked PRs/issues and relevant current repository implementation; never rely solely on previous ChatGPT conversation or a quoted comment.
2. Explain complex questions in plain Portuguese first, when discussion is requested. State the current observed behavior, what is being decided, concrete options, trade-offs and a recommendation grounded in existing project patterns. Do not post a decision before the user chooses when material authority is required.
3. Resolve routine technical ambiguity through evidence; identify material unresolved product/security/architecture choices explicitly as `[QUESTION]`.
4. After user agrees, write durable `[DECISION]` responses or update the issue. Preserve existing requirements, prior decisions and comments; do not replace entire issue body without reconciling changes. Use `[IMPLEMENTATION NOTE]` for verified facts rather than pretending they are approvals.
5. For an authorized full refinement/readiness review, apply the shared default: short opening summary, current implementation with inspected commit links, before/after behavior, scope/non-goals, acceptance and a representative scenario table with suggested proving layers. Include current → expected API signatures/examples for integration, a compact Mermaid system design for backend/integration/architecture changes, and character wireframes plus accessible approved assets for UI work. Distinguish verified facts, decisions, proposals and pending handoffs; reconcile behavior, visuals, contract, criteria and scenarios across linked issues. Reuse delivered code/tests and flag obsolete expectations. If a visual reference changed, record the approved version and whether new OpenSpec validation is needed. For narrow corrections, preserve unrelated content and update only affected sections and inconsistencies; do not expand the requested scope to reformat the whole issue.
6. Verify the resulting GitHub mutation and provide the issue/comment link or exact issue URL, plus READY FOR OPSX EXPLORE or the precise unresolved blocker.

## Guardrails

For affected user-facing content, reconcile the issue's **i18n and translation** section, acceptance and scenarios with inspected locale catalogs/helpers and API text ownership. Cover state/error/accessibility labels, safe unknown-code fallbacks and local formatting/plurals; preserve domain data. Apply this to full refinements or the affected part of a narrow correction without expanding into unrelated translation cleanup.

No invented GraphQL types, no speculative native Magento behavior, no silent change in existing product decisions, no accidental expanding scope, no automatic implementation/PR/merge. The CLI's later `issue-audit` and OpenSpec stages still independently verify the issue.
