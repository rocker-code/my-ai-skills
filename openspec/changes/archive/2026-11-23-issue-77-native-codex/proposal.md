# Proposal

## Why

A distribuição global ainda exige OpenCode e fixa seus caminhos, impedindo uso independente por Codex CLI. A issue [#77](https://github.com/rocker-code/my-ai-skills/issues/77) pede ambos como consumidores nativos do mesmo workflow já simplificado pelas #75/#76, sem restaurar o plugin pessoal removido pela #52.

## What Changes

- Suportar seleção explícita `--agent opencode`, `--agent codex` ou ambos na instalação; atualizar a seleção comprovadamente instalada por padrão e permitir expansão explícita sem remover integrações anteriores.
- Compartilhar um único snapshot imutável de skills/protocolos/helpers, expondo links nativos e orientação mínima por agente, com integridade, ownership, preservação e rollback transacional.
- Separar inventário imutável do pacote da seleção mutável instalada para permitir adicionar o segundo agente na mesma revisão sem sobrescrever um manifesto imutável.
- Integrar Codex aos mesmos entrypoints de issue, milestone, PR, progresso e recuperação. Usar somente capacidades nativas comprovadas para identidade, execução, contexto novo e revisão independente.
- Comprovar as cinco skills oficiais Explore/Propose/Apply/Verify/Archive no runtime selecionado; Verify suportado é padrão e nunca substitui testes ou revisão.
- Estender testes determinísticos e smokes reais isolados, documentação pt-BR/en e referências geradas. Ausência de credencial/capacidade resulta em prova pendente ou bloqueio, não sucesso fabricado.
- Publicar instalador em commit A e launcher posterior B com SHA/digest literais de A, preservando A por merge commit, sem squash/rebase.
- **BREAKING (instalação inicial):** o launcher público exige agente explícito quando não existe instalação verificável; atualização sem seleção mantém os agentes existentes, inclusive instalações OpenCode antigas.

## Capabilities

### New Capabilities

Nenhuma: distribuição, atualização e execução já têm fronteiras canônicas.

### Modified Capabilities

- `global-workflow-distribution`: seleção independente/coexistente, descoberta nativa Codex/OpenCode, pacote compartilhado e bootstrap oficial incluindo Verify.
- `global-workflow-update`: preservar/expandir seleção, compatibilidade com manifesto antigo, transação multiagente e diagnóstico dos caminhos efetivos.
- `issue-delivery`: execução equivalente com capacidades verificadas por runtime, contextos realmente novos e recuperação entre agentes sem portabilidade de histórico.

## Impact

Alvos: `scripts/install-global`, `scripts/install.sh`, `scripts/update.sh`, `skills/update-ai-workflow/SKILL.md`, orientação de runtime nos protocolos/entrypoints existentes, referências sincronizadas, testes de distribuição/launcher/reserva e smokes; `README.md`, `README.en.md`, changelog e instruções referenciadas de instalação. Wiki externa é referência a verificar, não autorização implícita para publicar em outro repositório.

Base inspecionada: `58c9b67ee4148748f83539b457d6ddf49fedb4a4`; #75/#76/#52 entregues, sem dependência em #61/#78. Nenhum código de produção é alterado nesta proposta.

Fora do escopo: plugin pessoal, daemon/dispatcher/framework novo, segunda implementação OpenSpec, issues paralelas, métricas/eventos operacionais, alterações em apps/M2T, mudança de merge default, atualização da instalação real do usuário ou limpeza de conteúdo incerto.
