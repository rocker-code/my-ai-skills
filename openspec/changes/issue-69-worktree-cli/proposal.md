# Proposal

## Why

O helper de reserva exige caminhos repetidos, devolve JSON volumoso para uma verificação humana simples e não está disponível como comando global. Isso favorece pipelines que mascaram códigos de erro justamente no gate de posse de worktree da issue #69.

## What Changes

- Publicar `worktree-reservation` no PATH pela instalação/atualização global, acompanhando a versão `active`, preservando comandos de outra origem e a instalação anterior em falhas.
- Para operações sobre checkout existente, resolver a raiz do worktree Git corrente quando `--path` for omitido, inclusive de subdiretórios; manter destinos ausentes e operações de planejamento/remoção com parâmetros explícitos.
- Produzir resumo humano nativo de resultado, owner, HEAD, digest e drift por padrão, incluindo `inventory.digest` completo para `reconcile`/takeover, candidatos exatos/elegibilidade para `clean-generated` e entradas de reserva para `list` quando esses comandos forem usados, sem inventário completo em cada `verify`; falhas incluem causa e próxima ação segura; preservar JSON completo com `--json`, campos/tipos e códigos de saída.
- Atualizar protocolo, orientação distribuída, exemplos e testes, sem inferir sessão do registry, relaxar verify/checkpoint ou duplicar `workflow-status`.
- No trecho da orientação distribuída tocado por esta issue, respeitar o contrato nativo OpenSpec 2.0 entregue pela #71 no merge `5e33688d2a9db702e6bd0f2027d778f3baebdf35`; não usar 1.17 nem criar comandos `/opsx-*` artificiais para passar a suíte. A integração e a validação da #69 continuam pendentes, não são aprovadas pelo merge da #71.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `checkout-write-reservation`: seleção segura do checkout e resumo da interface pública, sem modificar os invariantes de posse.
- `global-workflow-distribution`: descoberta e execução do launcher no PATH com imports na versão ativa e tratamento seguro de colisões.
- `global-workflow-update`: continuidade do launcher através de atualizações e rollback.

## Impact

`scripts/worktree-reservation`, `scripts/install-global`, testes de reserva/instalação, `protocol/WORKTREES.md`, referências geradas por `scripts/sync-skill-references`, orientação global gerada pelo instalador e exemplos relevantes em skills/README. Não há alteração do schema do registry, fingerprint, comandos Git/OpenSpec, plugin pessoal ou dashboard. Consumidores de M2T/Rancho só adotam a nova interface depois de entrega validada; #61 conserva handoff atual. A #71 já entregou a revisão separada do contrato de primeiro uso em `openspec/specs/global-workflow-distribution/spec.md`, orientação e testes 2.0; a #69 deve integrar essa base antes de completar sua implementação. O checkout da #69 em `7cdc9876865494c14f0b7759802fab659acb0e94` tem 16 arquivos Apply modificados sem stage; seis se sobrepõem à #71 (`CHANGELOG.md`, `README.md`, `README.en.md`, `scripts/install-global`, `tests/test_global_install.py`, `tests/test_install_launcher.py`). Não fazer merge/rebase/stash/reset nem substituir esses arquivos sujos para incorporar a base.

## Evidence / boundary

- [#69 — decisão do proprietário, 16/11/2026](https://github.com/rocker-code/my-ai-skills/issues/69#issuecomment-6922770750): OpenSpec 2.0 nativo, sem pin 1.x ou comandos fabricados; revalidar antes de novo Apply e manter E_RETRY_LIMIT.
- [#61 — decisão do proprietário, 16/11/2026](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6922774044): mesma base 2.0 para descoberta/retomada, sem dispensar suíte ou garantias de reserva.
- [#71 — merge da PR #72](https://github.com/rocker-code/my-ai-skills/commit/5e33688d2a9db702e6bd0f2027d778f3baebdf35): contrato nativo 2.0 entregue em revisão exata; não inferir que este worktree antigo já o contém. O `tests/test_global_install.py` deste checkout ainda exige comandos `/opsx-*` da 1.17.0; a versão entregue testa skills nativas, não comandos legados.
- `/tmp/opencode/issue-69-validation.md`: três falhas G1 da mesma assinatura ocorreram antes do diagnóstico; `E_RETRY_LIMIT` permanece bloqueado, sem limpeza retroativa, reclassificação ou novo teste G1 nesta revisão de planejamento. A próxima execução exige decisão explícita sob o protocolo de gates após integração e revisão independentes.
