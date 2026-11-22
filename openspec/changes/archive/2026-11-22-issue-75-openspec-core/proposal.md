# Proposal

## Why

O fluxo atual repete exploração, planejamento, execução e auditoria em várias skills, cria comentários administrativos e permite issues concorrentes. A issue #75 aprova OpenSpec 2.0 como único ciclo e uma fila estritamente sequencial, preservando segurança, evidências e recuperação.

## What Changes

- Integrar Explore → Propose → Apply → Verify → Archive nativos, com adaptadores mínimos apenas para GitHub, isolamento, testes/M2T e entrega.
- **BREAKING**: retirar gates autônomos `issue-audit`, `issue-ready`, wrappers duplicados de exploração e segunda auditoria completa; migrar seus consumidores antes da remoção física.
- Consolidar revisão independente no HEAD final, revalidando somente superfícies/evidências invalidadas por mudanças.
- Reduzir o orquestrador à fila/dependências, com uma issue ativa e delegação dentro dela; retirar Kaizen do caminho crítico.
- Impedir comentários operacionais automáticos; requisitos/decisões ficam no corpo da issue/OpenSpec e entrega no PR/checks/reviews.
- Disponibilizar `simplify` pequeno e opcional, com preservação de comportamento e testes existentes.
- Explicitar os três princípios de engenharia e impedir novas camadas sem lacuna demonstrada.

## Capabilities

### New Capabilities

- `issue-delivery`: execução e recuperação de uma issue via ciclo nativo, revisão/entrega verificável e fila sequencial.

### Modified Capabilities

- `m2t-worktree-lifecycle`: retirar somente a exigência de Kaizen verificado antes de cleanup; entrega/merge, evidências, ausência de owner/processo e seleção/ordem seguras continuam obrigatórias.

Contratos existentes de distribuição, reservas e evidências continuam obrigatórios. Retirada de métricas é #76, suporte de instalação Codex é #77 e inventário final de limpeza é #78.

## Impact

`protocol/AI_WORKFLOW.md`, políticas de revisão/evolução/worktrees quando vinculadas, skills de entrada/execução/revisão/retomada/progresso, referências geradas, README PT/EN, docs ativos, sincronizador e testes afetados. Não altera aplicações, M2T, histórico arquivado, permissões ou política auto-if-green. Revisão base: `42eb306d29d2f89d4e9c0fde5d12a282bcacb0c4`; issue #75 sem comentários e sem PR existente na consulta inicial.
