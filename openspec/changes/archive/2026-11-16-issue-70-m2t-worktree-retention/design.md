# Design

## Context

`protocol/WORKTREES.md@02194d7` define registro único no Git common dir, posse, handoff, retenção e closeout, mas não instrui explicitamente o ciclo do sandbox M2T. `skills/implement-issue`, `apply-issue`, `milestone-orchestrator`, `resume-workflow`, `github-resolution`, `prepare-pr` e `post-pr-audit` consomem esse protocolo, diretamente ou via referências sincronizadas. Referências em `skills/*/references/` são geradas de `protocol/` por `scripts/sync-skill-references`; a distribuição global usa `scripts/install-global`.

Contrato congelado contra M2T merge `04f0272`: `m2t test` e `graphql` produzem run ID, retorno resumido em stderr e registro consultável por `runs show <id> --json`; logs ficam em `$XDG_STATE_HOME/m2t/runs/<id>/output.log` e não há garantia de path no resumo de sucesso. `unit`/`exec` retornam recibos e logs privados sob `m2t/executions`, mas não registros `m2t runs`; sua limpeza efêmera é interna. `m2t status` lista worktree/instância/estado, sem provar ownership de workflow ou conclusão de worker. `m2t --worktree PATH down` seleciona integração; GraphQL exige `--scope graphql --sandbox-id TOKEN` para cada token próprio; `--no-wait` devolve 73 se o lock está ocupado. `down` preserva vendor compartilhado; os bancos tmpfs e volumes exclusivos não são dados reutilizáveis após remoção. O launcher de reserva #69 foi publicado em `02194d7` e não muda o lock M2T.

## Goals / Non-Goals

**Goals:**
- Vincular instâncias comprovadamente próprias à mesma worktree e evidência durável nas transições existentes; falhar fechado no closeout, sem introduzir um registry de sandbox que possa divergir.
- Fazer a política genérica do pacote global prevalecer sobre exemplos de cleanup por comando e deixar claro ao consumidor externo que precisa retirar sua instrução conflitante em issue própria.
- Provar por inspeção/fixtures do consumidor que T1–T7 são instruções coerentes com o produtor sem executar Docker/Magento neste planejamento.

**Non-Goals:**
- Alterar M2T, Rancho, CLI de `db:sql`, cache Composer, schema da reserva ou ciclo de merge/release; prometer reuso de banco após `down`; proibir cleanup obrigatório de containers efêmeros.

## Decisions

1. **Inventário no handoff/registry existente, com prova externa de posse.** Registrar caminho canônico, escopo, token GraphQL exato quando houver, run/recibo/log referenciável e motivo do status; reconciliar `m2t status` e `runs show` com execução do worker e evidência de worktree. `worktree-reservation --set sandbox` pode apontar para uma seleção, mas não codifica sozinho várias instâncias nem autentica ownership; usar o mesmo handoff durável já requerido em `WORKTREES`, sem criar ledger paralelo. Alternativa descartada: derivar ownership dos nomes Docker ou presumir que todo GraphQL listado pertence à issue.
2. **Retenção por ciclo de trabalho, não por comando.** M2T decide preparação/invalidade do seu cache; workflow exige verificação de código e teste atual. `reset` só para recuperação de sandbox avariado conforme diagnóstico explícito, nunca como pós-suite; mesmo um `down` manual não é evidência de conclusão. Alternativa: teardown periódico por sessão ou gc por idade, incompatível com PR/retomada.
3. **Closeout em duas fronteiras.** Depois dos critérios de `WORKTREES` (merge exato/kaizen, owner liberado, processos/testes finalizados, ignorados e commits inventariados, prova durável), resolver seleções comprovadas e chamar comandos públicos M2T usando `--worktree` explícito fora do checkout; reter caminho durante falha/lock/seleção incerta. Somente após cleanup completo remover a worktree com `git worktree remove` sem force e registrar resultado. Alternativa: excluir a worktree primeiro e confiar em `gc`, que perde o caminho necessário e pode tocar recursos alheios.
4. **Status ≠ prova.** `m2t status` indica busy/stopped/orphan, `runs show --json` ajuda a reconciliar run registrado, e logs permitem diagnóstico; nenhum substitui callback/liveness real, posse da reserva nem `workflow-evidence`/gates do HEAD. Abrir só o trecho necessário do log em falha; não imprimir logs sensíveis em handoff público.

## Risks / Trade-offs

- [Instância órfã sem token/posse] → reter e declarar pendência de reconciliação; não usar regex, prefixo ou gc para compensar lacuna.
- [Cleanup parcial ou lock 73] → registrar resultado por escopo e manter checkout/handoff, sem mascarar código de erro nem reexecutar `down` em loop.
- [M2T skill externa ainda sugere `gc` após remover worktree ou `reset` por interrupção] → documento consumidor fixa o gate mais estrito da issue #70 e exige diagnóstico antes de reset; não editar produtor.
- [Instrução Rancho manda `down` a cada execução] → anotar handoff para Rancho #457; não tratar a atualização externa como entrega desta PR.
- [Referências copiadas divergentes] → alterar fonte em `protocol/`, rodar `scripts/sync-skill-references`, conferir diff/README pt-BR/en e testes de distribuição.

## Migration Plan

Atualizar apenas instruções genéricas conflitantes e exemplos do pacote; sem migração de registry, instâncias ou dados. Consumidores existentes passam a registrar seleções próprias no handoff durante o próximo uso; seleções legadas sem posse demonstrável permanecem retidas. Rollback textual preserva as instâncias já existentes e não desencadeia down automático.

## Matriz de prova planejada

| Cenário | Fronteira/risco | Implementação planejada | Prova focada em Apply |
| --- | --- | --- | --- |
| T1 | Reuso versus teardown e cache | `WORKTREES` + instruções `apply-issue` | Assert documental/fixture de dois usos; não exigir M2T real para provar texto |
| T2 | Handoff, posse de código e prova atual | `implement-issue`, `apply-issue`, protocolo | `tests/test_worktree_reservation.py` já cobre posse; novo check de instrução/handoff sem confundir locks |
| T3 | PR/crash/interrupção | `resume-workflow`, `milestone-orchestrator`, protocolo | `tests/test_workflow_execution_state.py` existente e fixture de retenção/unknown |
| T4 | Merge/kaizen com outro worktree ativo | closeout em `WORKTREES`, orquestração | Fixture de seleção própria versus alheia/cache; sem gc global |
| T5 | Lock 73/falha/owner ativo | closeout fail-closed | Fixture de erro e checkout retido, próximo passo visível |
| T6 | Integração + múltiplos tokens GraphQL | comandos documentados com path/escopo/token exatos | Contrato CLI do M2T merge e fixture documental de várias seleções; nunca inferir token |
| T7 | `unit`/`exec` efêmeros e log | instruções de Apply/protocolo | Check documental de exceção + testes M2T do produtor já entregues (não rerodar nem alterar produtor) |

Base de testes do consumidor: `python3 -m unittest -v tests.test_worktree_reservation tests.test_workflow_execution_state tests.test_global_install` conforme alterações efetivas; suite final obrigatória `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` no HEAD final limpo, após archive/sync/distribuição/commit em Apply. Verificar ferramentas, paths, isolamento e política `protocol/TEST_STRATEGY.md@02194d7` antes do run amplo. Provas da PR M2T #48 são referência de contrato, não gate local deste candidato.
