# Proposal

## Why

O helper de reserva exige caminhos repetidos, devolve JSON volumoso para uma verificação humana simples e não está disponível como comando global. Isso favorece pipelines que mascaram códigos de erro justamente no gate de posse de worktree da issue #69.

## What Changes

- Publicar `worktree-reservation` no PATH pela instalação/atualização global, acompanhando a versão `active`, preservando comandos de outra origem e a instalação anterior em falhas.
- Para operações sobre checkout existente, resolver a raiz do worktree Git corrente quando `--path` for omitido, inclusive de subdiretórios; manter destinos ausentes e operações de planejamento/remoção com parâmetros explícitos.
- Produzir resumo humano nativo de resultado, owner, HEAD, digest e drift por padrão, incluindo `inventory.digest` completo para `reconcile`/takeover, candidatos exatos/elegibilidade para `clean-generated` e entradas de reserva para `list` quando esses comandos forem usados, sem inventário completo em cada `verify`; falhas incluem causa e próxima ação segura; preservar JSON completo com `--json`, campos/tipos e códigos de saída.
- Atualizar protocolo, orientação distribuída, exemplos e testes, sem inferir sessão do registry, relaxar verify/checkpoint ou duplicar `workflow-status`.
- No trecho da orientação distribuída tocado por esta issue, não prometer comandos OpenSpec que o CLI instalado não entrega. A migração transversal do bootstrap e das skills do workflow para OpenSpec 2.0 é pré-requisito delimitado fora da #69; não usar 1.17 nem criar comandos `/opsx-*` artificiais para passar a suíte.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `checkout-write-reservation`: seleção segura do checkout e resumo da interface pública, sem modificar os invariantes de posse.
- `global-workflow-distribution`: descoberta e execução do launcher no PATH com imports na versão ativa e tratamento seguro de colisões.
- `global-workflow-update`: continuidade do launcher através de atualizações e rollback.

## Impact

`scripts/worktree-reservation`, `scripts/install-global`, testes de reserva/instalação, `protocol/WORKTREES.md`, referências geradas por `scripts/sync-skill-references`, orientação global gerada pelo instalador e exemplos relevantes em skills/README. Não há alteração do schema do registry, fingerprint, comandos Git/OpenSpec, plugin pessoal ou dashboard. Consumidores de M2T/Rancho só adotam a nova interface depois de entrega validada; #61 conserva handoff atual. O contrato OpenSpec 2.0 de primeiro uso em `openspec/specs/global-workflow-distribution/spec.md`, as referências `/opsx-*` transversais e os testes de bootstrap 1.17 exigem mudança separada e revisada; não podem ser implicitamente sanados por esta issue.

## Evidence / boundary

- [#69 — decisão do proprietário, 16/11/2026](https://github.com/rocker-code/my-ai-skills/issues/69#issuecomment-6922770750): OpenSpec 2.0 nativo, sem pin 1.x ou comandos fabricados; revalidar antes de novo Apply e manter E_RETRY_LIMIT.
- [#61 — decisão do proprietário, 16/11/2026](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6922774044): mesma base 2.0 para descoberta/retomada, sem dispensar suíte ou garantias de reserva.
- CLI local `openspec --version` = `2.0.0`, `openspec config list` = `profile: core`, `delivery: skills (retired in 2.0, ignored)`; `openspec update --dry-run --json` planeja remover `.opencode/commands/opsx-*.md` e atualizar `~/.config/openspec/config.json`. Esses arquivos antigos existentes não comprovam disponibilidade nativa; nenhum init/update foi autorizado ou executado.
