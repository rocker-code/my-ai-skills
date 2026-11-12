---
name: create-issue
description: Create GitHub issues from ideas, bugs or feature requests in OpenCode, Codex CLI or Claude Code using the same detailed authoring standard as the Web workflow. Use for natural requests such as "crie uma issue", "registre este bug" or "divida em issues", without implementing code.
metadata:
  category: cli-backlog
  stage: discovery
---

# Create Issue — CLI

Use this entry for CLI backlog authoring. Web agents keep using `chatgpt-web-create-issue`; do not change or invoke that Web-only entry from the CLI. For an existing issue, use `refine-issue` instead. Requests to implement or take care of an existing issue continue through the existing execution workflow.

## Shared authoring standard

Before drafting, read [the existing issue authoring protocol](references/CHATGPT_WEB_ISSUES.md). Apply its principles, default issue standard, evidence/reuse rules, conditional sections, authoring template, GitHub conventions and creation completion requirements. This entry explicitly applies those authoring requirements in the CLI: the protocol's Web audience/runtime wording does not prohibit this use or require a Web connector. Use the available authorized GitHub CLI/MCP integration instead; do not assume access.

For UI work, also read [the visual artifact protocol](references/VISUAL_ARTIFACTS.md). Resolve bundled references relative to this skill, never the target project's working directory. Keep these generated copies synchronized with the existing sources; do not maintain a second, simplified CLI template.

## Procedure

1. Identify the target repository and requested scope, milestone and assignee from context. Inspect its instructions, live issues/comments, labels, milestones, relevant PRs, code/schema and tests to avoid duplicates. Record the inspected revision and evidence paths/links. Use remote commit links only for revisions verified on that remote; otherwise label the local checkout revision and paths explicitly. Distinguish verified facts, approved decisions, proposals and unknowns; report unavailable evidence.
2. Draft using the shared template: opening summary, current/expected behavior, scope/non-goals, observable acceptance criteria, dependencies and proportionate scenarios in `ID | Preparação/ação | Resultado esperado | Camada sugerida` format. Identify existing implementation/tests to reuse. Do not replace the issue body with an execution checklist alone.
3. Apply sections by scope: compact Mermaid for backend/integration/architecture; verified current → proposed contracts for integrations; wireframe and accessible approved references for UI; i18n and text ownership for user-facing content. Do not force GraphQL, wireframes or localization into a tooling-only issue. Reconcile behavior, contracts, design, criteria and scenarios.
4. Resolve routine details from evidence; ask only about material unresolved decisions. Preserve explicit non-goals. Create linked producer/consumer issues only when independently deliverable boundaries require them, and record ordering and contract handoff.
5. When creation is requested, publish through the authorized GitHub integration without another confirmation. Use verified repository metadata. Read back the issue and verify its body and assignments before returning links, scope and blockers. If writing is unavailable, provide a copy-ready title/body and state that nothing was published.

Read [incremental delivery](references/INCREMENTAL_DELIVERY.md) when drafting new capabilities: distinguish the complete safe first delivery from genuinely optional future evolutions, and do not turn speculative scenarios into mandatory acceptance criteria. Automatically record qualified evolutions as separate issues without routine approval, and notify after registration; when recorded, assign each to a verified future evolution milestone and cross-link the parent; do not invent or reuse the current delivery milestone.

When the requested change spans independently deliverable user outcomes or material cross-repository dependencies, suggest a small sequence of delivery milestones, not one mega-milestone; require observable completion and preserve the user's approved roadmap. Follow [incremental delivery](references/INCREMENTAL_DELIVERY.md).

## Boundary

Stop at backlog authoring. Do not implement code, initialize/update the workflow, create OpenSpec artifacts or start Apply merely because the request came through a CLI. Subsequent execution retains independent issue-audit, readiness and OpenSpec gates. Do not claim checks ran or evidence was inspected unless verified.
