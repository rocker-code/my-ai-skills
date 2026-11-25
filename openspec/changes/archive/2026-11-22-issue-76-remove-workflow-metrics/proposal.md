# Proposal

## Why

A infraestrutura legada mede o próprio workflow e grava comentários operacionais, contrariando a simplificação aprovada na #75. Sua remoção deve preservar fatos verificáveis de execução, provas de testes e posse do checkout sem criar outro coletor.

## What Changes

- **BREAKING:** remover workflow-event, workflow-report e seus módulos, testes exclusivos e entradas de distribuição; comentários antigos ficam históricos.
- Atualizar instalação, smoke tests e documentação sem enfraquecer integridade, atualização ou personalizações.
- Retirar contratos ativos de métricas/eventos; manter estado confiável por runtime nativo, Git/GitHub/OpenSpec, workflow-evidence e worktree-reservation já existentes.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `workflow-metrics`: aposentar todos os requisitos da capacidade removida.
- `workflow-execution-state`: substituir contratos do coletor por requisitos mínimos de correlação e reconciliação a partir das fontes nativas existentes, sem armazenamento novo.
- `checkout-write-reservation`: referenciar o padrão SAFE_ID próprio em vez do comando removido, preservando sua semântica.

## Impact

Scripts de métricas/eventos e seus testes; exigência de helper no instalador; fixtures e smoke de instalação; specs ativas e referências. O ciclo sequencial, revisão/merge, runtime, evidência de testes e registry continuam existentes. Não alterar aplicações, M2T ou histórico arquivado; suporte Codex pertence à #77 e limpeza ampla à #78.
