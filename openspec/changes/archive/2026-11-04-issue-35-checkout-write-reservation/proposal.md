# Proposal

## Why

O [protocolo de worktrees](../../../protocol/WORKTREES.md) já exige registry no Git common dir, atualização atômica, lock exclusivo e um único writer por checkout, mas nada disso existe como ferramenta: `scripts/` não contém registry, lock nem verificação de HEAD/diff (issue #35). Na prática, commits de outro agente numa branch ativa só foram percebidos tarde, e `workflow_metrics.cpython-314.pyc` gerado pelos próprios helpers bloqueou `update-main` — reproduzido em `main@5825a9c`: `python3 -m unittest discover -s tests` e `scripts/workflow-event` criam `scripts/__pycache__/` e `tests/__pycache__/` não rastreados, e o repositório não tem `.gitignore`.

## What Changes

- Novo helper stdlib `scripts/worktree-reservation` (CLI) com módulo `scripts/worktree_registry.py` que materializa e valida o registry `<git-common-dir>/ai-workflow/worktrees.json` já definido em WORKTREES, sob lock exclusivo e escrita atômica.
- Comandos para reservar, verificar antes de mutação, registrar checkpoint após escrita própria, transferir posse entre sessões (planejamento → Apply → correção), liberar/mudar estado do lifecycle, reconstruir registry ausente/incompleto a partir do Git real em estado bloqueado de recuperação, cancelar reserva planejada ainda não criada, consultar estado e limpar bytecode elegível sob verificação.
- API pública versionada de estado de código (HEAD, working tree e blobs/modos staged do índice, entradas por caminho) para reuso por #31; detecção de drift inclusive em reservas sem dono, com relatório dos caminhos afetados. Checkpoint distingue escrita própria após verificação de drift já detectado, sem alegar autoria infalível durante a janela de escrita.
- Reserva `RESERVED` de caminho planejado ainda inexistente ancorada por `--repository` em checkout existente; falha de `git worktree add` pode ser seguida de `cancel-planned` apenas pelo mesmo dono, com destino ausente, inventário Git sem entrada e motivo registrado. `release` só após checkpoint do estado atual, sem absorver mudança externa.
- Registry perdido/incompleto não transforma um writer possivelmente ativo em `WAITING`: reconstrução entra em `RECOVERY_REQUIRED`, sem concessão de posse; saída exige inventário revisado e evidência de término do writer anterior, sem tomada por idade. Evidência operacional não comprova automaticamente parada de agente externo.
- Classificação de não rastreados em "gerado conhecido" (`__pycache__/`, `*.pyc`, `*.pyo`) versus desconhecido, sem implicar autoria. `track-generated --session -- <command>` é opt-in: verifica posse, observa bytecode antes/depois de uma execução cooperante concluída (sem filhos ainda executando), faz checkpoint dos efeitos do comando e registra sob o lock, no Git common dir, apenas arquivos novos com hash completo, metadados limitados e referência opaca da execução, nunca argumentos/secrets. `clean-generated --apply` exige caminho/motivo e remove somente candidato registrado ainda idêntico, sob revalidação de posse/estado; ausência de proveniência, inclusive bytecode válido criado pelo usuário, fica somente na listagem. Snapshot não comprova ausência de writer externo não cooperante na janela.
- Prevenção de bytecode incidental: helpers Python desativam escrita de bytecode antes de importar módulos irmãos (`workflow-event`, `workflow-report`, novo CLI) e o repositório ganha `.gitignore` para `__pycache__/` e `*.py[co]`.
- `protocol/WORKTREES.md` ganha seção do helper, incluindo os limites de coordenação com agentes externos não cooperantes; parágrafo "Worktree lifecycle" das skills de orquestração, planejamento, Apply, PR e correção passa a citar os comandos; `update-main` trata gerados conhecidos de forma proporcional.
- `scripts/sync-plugin`, README pt/en e `update-ai-workflow` passam a distribuir o novo helper; testes de concorrência/retomada em repositórios Git temporários.

## Capabilities

### New Capabilities
- `checkout-write-reservation`: reserva exclusiva de escrita por checkout, verificação de estado antes de mutação, transferência/retomada segura de posse e tratamento de arquivos gerados conhecidos, sobre o registry local do protocolo de worktrees.

### Modified Capabilities
<!-- Nenhuma: openspec/specs/ está vazio neste repositório. -->

## Impact

- Código: `scripts/worktree-reservation`, `scripts/worktree_registry.py` (novos); `scripts/workflow-event`, `scripts/workflow-report` (uma linha cada); `scripts/sync-plugin`; `.gitignore` (novo).
- Documentação/skills: `protocol/WORKTREES.md`; `skills/{milestone-orchestrator,milestone-progress,implement-issue,apply-issue,prepare-pr,github-resolution,address-pr-review,update-main,update-ai-workflow}/SKILL.md`; `README.md`, `README.en.md`; cópias regeneradas em `skills/*/references/WORKTREES.md` e `plugins/my-ai-skills/**` via `scripts/sync-plugin`.
- Testes: `tests/test_worktree_reservation.py` (novo).
- Dependências: nenhuma nova (Python 3.10+ stdlib, `git`); lock via `fcntl` (POSIX); sem `fcntl` o helper falha fechado.
- Sem impacto em GitHub, merge, release ou deploy: o registry continua sendo dado de coordenação local, nunca prova de entrega nem gate de validação.
