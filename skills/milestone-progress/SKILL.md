---
name: milestone-progress
description: Analyze live GitHub milestone development progress and return summary and per-issue Markdown tables with delivery, workflow stages, PRs, CI, blockers, next actions and recorded timings. Use for "mostre a evolução do milestone", "como está o milestone", "status do milestone" or "compare o progresso do milestone". Read-only; does not start development or manage the work queue.
---

# Milestone progress

Resolve the repository and milestone from an explicit URL/number or unique current context. Ask only for an ambiguous or missing identifier. Preserve the exact scope, including for similarly named milestones in different repositories. Read [the workflow protocol](references/AI_WORKFLOW.md) for state meanings and measurement rules. Return the report in the user's language, in Markdown tables, on every invocation.

## Gather current evidence

1. Read the live milestone and paginate **all** its issues, open and closed. When using the REST issues endpoint, filter out pull requests. Record scope, collection time/timezone and any missing pages/permissions. An empty milestone has zero issues and progress `n/a`, not 100%.
2. For every issue, inspect current state, closure reason, comments/decisions, dependencies, pinned OpenSpec evidence and linked PRs. Verify PR association using closing references or explicit issue/PR evidence; number matches and title searches alone are insufficient. Follow cross-repository links only as dependency evidence. Do not include outside issues in milestone totals. Distinguish replacement/abandoned PRs from the active delivery PR and flag unresolved associations.
3. Refresh relevant PR heads, merge state, reviews and required checks. A green historical run, approval on an old SHA, empty checks or unknown repository requirements cannot prove `CI_GREEN` or `READY_TO_MERGE`. Show raw observed CI separately when requirements are unavailable. Closed PRs without merge are not delivery. For multiple required PRs, verify all required scope, including partial/reverted delivery.
4. Derive the last verified workflow stage from evidence using the protocol. Label a stage unknown when evidence is missing; do not invent planning/Apply completion from labels or a draft PR. Keep `Blocked` separate from the last verified stage and show the exact dependency, decision or failing gate.
5. If available, use `workflow-report <milestone-URL> --format json` for recorded timings and run IDs. Supplement it with the complete live inventory: that helper omits uninstrumented issues from its run rows and uses bounded issue/PR queries, so it is not proof of complete milestone coverage. Without helpers, read existing structured timing comments via connected GitHub tools. Missing timing data remains `n/a`; still report all issues. Do not write events or comments to obtain a report.
6. If local Git is available, optionally reconcile issue worktrees and report only verified local ownership/path/state. When local evidence exists, include a worktree table with issue, path, delivery, lifecycle state and cleanup pending reason; distinguish open work from delivered leftovers. This query only reports cleanup eligibility and never removes anything. Without local access, mark worktrees unavailable; do not create checkouts to generate the report.

## Render the tables

Lead with the linked milestone, repository, collection time and evidence limitations. Use this summary shape:

| Indicador | Atual | Variação desde a referência |
|---|---:|---|
| Escopo atual | N issues | +A adicionadas / −R removidas, ou n/a |
| Entregues e verificadas | D/N (P%) | +X ou n/a |
| Fechadas no GitHub | C/N | +Y ou n/a |
| Em desenvolvimento / revisão | I / V | evidência ou n/a |
| Bloqueadas | B | evidência ou n/a |
| Cobertura de tempos | T/N | execução e período ou n/a |

Compute verified delivery percentage as `100 * D / N`, counting each issue once and using the current complete scope. Treat it as issue-count progress, never estimated effort completion. Keep GitHub closed count distinct: cancelled, duplicate, not-planned or closed-without-delivery issues are not automatically delivered. Describe these outcomes separately. Preserve overlaps explicitly: blocked is an overlay, not another mutually exclusive workflow stage. If collection is partial, mark counts/percentages partial and do not claim a complete total.

Always include a row for every in-scope issue, even without metrics:

| Issue | Etapa verificada | Entrega | PR / CI no head | Bloqueio | Próxima ação | Tempo registrado |
|---|---|---|---|---|---|---|

Link issues, PRs and evidence. Use a compact table and put evidence details immediately below when needed. Include the current stage's start/duration only when timestamp evidence exists. Separate calendar elapsed time, measured stage work and explicit waits; never label issue age as development time. Show `n/a` rather than zero for absent measurements. Offer a stage timing table only when measured data adds value. Never invent tokens, costs or model thinking time.

For a temporal evolution request, compare against an identifiable previous report in context, recorded run or supplied date. State both timestamps, membership changes, reopened/reverted work, delivered delta and blockers added/resolved. Compare issue IDs as well as totals; a changed denominator can move the percentage without any delivery. Keep removed issues outside current totals but show their scope delta. Use issue/milestone timeline evidence if reconstructing a dated baseline; if it cannot be reconstructed reliably, say `sem referência histórica verificável` and show the current snapshot. Never claim improvement based on memory or estimates. A first report does not create or persist a baseline automatically.

End with a short assessment of the main bottleneck and the next eligible actions, backed by evidence. Report-only requests do not authorize implementation, cleanup, edits, comments, merges or scheduling. Do not invoke milestone-orchestrator to execute work as a side effect.
