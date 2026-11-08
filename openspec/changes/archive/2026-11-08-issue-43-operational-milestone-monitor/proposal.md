# Proposal

## Why

A #43 ainda dispõe somente da demo offline entregue pela PR #44. O operador precisa acompanhar vários repositórios e milestones sem confundir dados simulados, fechamento no GitHub, etapas registradas e atividade realmente confirmada no runtime.

## What Changes

- Introduzir `aew dashboard`, TUI Python/curses de leitura, com cadastro explícito de repositórios/milestones, cache persistente, atualização manual/periódica e operação sem rede/agente ativo.
- Reutilizar comentários v1, `parse_run_comment` e `summarize_run` da #16 e evolução #32; não criar outro logger, escrever comentários pela TUI nem mudar os contratos existentes.
- Adicionar coletor GitHub paginado e adaptador OpenCode V2 por consultas oficiais, com vínculo explícito sessão/run/issue/worker/worktree. Falha de telemetria resulta em desconhecido, nunca impede o desenvolvimento.
- Projetar identidades compostas, contadores exclusivos, frescor por fonte, conflitos, esperas, interrupções e régua de etapas reais sem inferir aprovação ou etapas anteriores concluídas.
- Preservar `examples/milestone-monitor/` como demo identificada; disponibilizar instalação local explícita do launcher global e documentação em paridade pt-BR/en.

## Capabilities

### New Capabilities
- `milestone-monitor-state`: inventário multi-projeto, ingestão, persistência, reconciliação e projeção auditável de GitHub/workflow/runtime.
- `milestone-monitor-tui`: consulta operacional, navegação, apresentação acessível, instalação e limites do comando `aew`.

### Modified Capabilities

Nenhuma. `workflow-metrics` e `workflow-execution-state` são contratos consumidos sem alteração; a projeção acrescenta frescor local, não reescreve suas métricas ou vereditos.

## Impact

Novos `scripts/aew`, pacote Python `scripts/milestone_monitor/`, instalador local e testes stdlib; uso de `gh` e OpenCode V2 opcionais conforme fonte configurada. Atualizar README.md/README.en.md e distribuição pelo `scripts/sync-plugin` quando afetada. Sem serviço remoto, dependência Python externa, plugin obrigatório, alteração de autorização, implantação, publicação npm ou automação de agentes/merge. A fase opcional de notificações, custos/tokens, web e um adaptador Codex nativo ficam fora do escopo. Codex pode produzir os comentários v1 existentes.

Dependências entregues: #16/PR #17 (`4d9d561242c4c6033729432764349ac7e2a5be23`) e baseline #44 (`ee33197b8da684fff0a46df87935cd5b8b012f21`), ambas em main. O desenho e a matriz em design.md delimitam o restante operacional, sem reapresentar a baseline como entrega nova.
