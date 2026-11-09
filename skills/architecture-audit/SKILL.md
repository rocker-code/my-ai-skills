---
name: architecture-audit
description: Audit architectural impact of an issue, OpenSpec change or PR against code and repository boundaries. Use when reviewing new dependencies, domain ownership, state, contracts or persistence; works without LikeC4 and reports evidence-backed risks.
---

# Architecture Audit

## Handoff instrumentado (condicional)

Somente com `workflow_instrumentation.enabled: true` e contexto executor autorizado,
seguir [o contrato](references/WORKFLOW_INSTRUMENTATION.md): preservar issue/run/
etapa/worker/execução, `operation_ids`, sessão real ou `session_id: null`, worktree/
branch; devolver horários, revisão exata e evidência ao coordenador. Não publicar
o registro de workflow como worker; invocação isolada não ativa instrumentação.
Preservar independência e gates da auditoria arquitetural, sem aprovação inferida.

Read repository AGENTS.md and architecture material that actually exists. Inspect relevant code, module dependencies, events, API/GraphQL schemas, persistence and callers on both sides of each changed boundary. LikeC4 is optional evidence, never a prerequisite; if the repository requires architecture documentation for this change, check that policy separately.

Describe before → after for domain ownership, dependency direction, source of truth, public contracts, state transitions, data consistency, concurrency and operational implications. Distinguish intended changes in the issue's approved decisions and validated OpenSpec from unexpected coupling. Check reuse of native mechanisms and existing invariants without making new requirements.

Return a table: decision/boundary, evidence (paths), impact, risk, required action or no action. Flag unknowns and propose focused verification. Use review-policy severity for PR findings. End with `ARCHITECTURE OK`, `CHANGES REQUIRED` or `UNVERIFIED — <missing evidence>`. Do not modify code or require a LikeC4 repository.
