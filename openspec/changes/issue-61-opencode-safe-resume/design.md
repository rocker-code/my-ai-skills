# Design — issue #61

## Verified context

Inspected `main` at `fce9a3cd02273f8525e463f623454ce251a865ee` and relevant blobs:
- `skills/milestone-orchestrator/SKILL.md` (blob `1ce9530f7ec4551c40f83d68f251701c4c5ce157`) already requires evidence-based resume.
- `protocol/WORKTREES.md` (blob `81adfc71f9ab304c6473011bd98aefa44d3e9b9b`) defines exclusive ownership, recovery and drift.
- `scripts/worktree-reservation` (blob `64d07bf7452f6a7b5190497cfd2c2da7305dc4bc`) implements these controls.
- `scripts/install-global` creates managed global OpenCode guidance and symlinks all discovered skills.

There was no executed end-to-end OpenCode recovery test available during authoring; the test obligation remains explicit.

## Decision

Use **one skill as entrypoint** and keep `milestone-orchestrator` as scheduler. Do not duplicate the ledger or introduce a second recovery state machine. The skill works read-only until issue/milestone scope, durable evidence and safe worktree ownership have been established; then it delegates to the existing gates.

### Reconciliation order

1. Resolve checkout/project and unique selected scope.
2. Inventory GitHub state, Git worktrees, staged/unstaged/untracked content, OpenSpec and accessible execution evidence.
3. Classify last verified gate versus unknown, blocked or conflicting states; never assume interrupted tests passed.
4. Verify stopped-writer evidence and reservation before effects; if ambiguous, retain and report blocker for the affected issue only.
5. Delegate the **same** issue/milestone, worktree, proposal and PR to the existing orchestrator.

### Tradeoffs and limits

Natural-language routing is guidance to the agent, not a native OpenCode crash hook. It cannot restart background processes automatically or recover uncommitted data from a lost disk. A session can request recovery without an earlier transcript; the evidence must remain available in Git/GitHub and local files.

## Validation plan

- Isolated global installer test proving skill installation, global routing and retained safety rules.
- Existing `tests/test_worktree_reservation.py` and `tests/test_workflow_execution_state.py` remain the primary automated contract for ownership/checkpoints.
- Real OpenCode follow-up smoke required to exercise T1/T5/T7 (resume a single issue, milestone, ambiguous candidates) and verify observed behavior. Do not mark these executed without runtime evidence.

A PR #62 está incorporada e não é o candidato ao gate final da continuação. A branch `issue-61-resume-closeout` deve produzir uma PR de acompanhamento vinculada à #61 aberta; os checks finais devem corresponder ao HEAD limpo e exato dessa nova PR após archive/sync. Isso entrega somente a prova e o fechamento restantes, sem repetir a implementação inicial.

## Matriz de prova pendente para a retomada real

O `tests/smoke_global_opencode.py` instala a revisão publicada `c48ac58beadc0a9712f59f60458a5c3df3ed5bfb`, não a versão atual da skill; sua descoberta/expansão de comandos legados não prova T1/T5/T7 no OpenSpec 2.0. A prova em `docs/issue-61-candidate-recovery-proof.md` executou sessões reais com a skill `resume-workflow` em `80e5de0`, mas é evidência histórica de antes desta decisão: não demonstra descoberta/invocação das **skills nativas OpenSpec 2.0** nem valida a revisão candidata atual. Preservar essa evidência sem promovê-la a gate aprovado.

Na próxima execução, verificar `openspec --version`, `openspec context --json`, `openspec list --json` e os arquivos gerados reais antes de qualquer mudança: a branch ainda contém `.opencode/commands/opsx-*.md` e cópias `.opencode/skills/openspec-*/SKILL.md` geradas por 1.x. A documentação instalada de 2.0 determina skills compartilhadas em `.agents/skills/` (com links específicos por ferramenta) e substitui os comandos antigos por `openspec-explore`, `openspec-propose`, `openspec-apply-change` e `openspec-archive-change`. Esses arquivos preexistentes **não comprovam** descoberta 2.0. O conflito P1 da spec compartilhada identificado na revisão de #69 pertence à [#71 — contrato de distribuição nativa OpenSpec 2.0](https://github.com/rocker-code/my-ai-skills/issues/71), no mesmo milestone; sua entrega **incorporada** e contrato verificado são pré-requisitos para retomar Apply e aprovar o gate de #61. **Não** executar `init`/`update`, remover arquivos gerados ou alterar a distribuição nesta continuação; bloquear até o merge do produtor, sem fabricar prova baseada no legado.

Após a entrega do pré-requisito, em HOME e repositórios descartáveis, com OpenCode/OpenSpec 2.0 reais e modelo habilitado, instalar a revisão candidata de `resume-workflow` usando o contrato de distribuição nativa entregue, sem tocar no HOME do usuário nem substituir o pacote global. Registrar origem e hash da skill OpenSpec efetivamente carregada e comprovar sua invocação no OpenCode (não inferir a partir de arquivo existente ou nome de comando); usar a skill nativa aplicável para verificar a transição até Apply, sem executar Apply sobre a issue real. Registrar SHA da candidata, IDs de sessão, prompts, respostas, eventos e estado Git/OpenSpec/PR antes/depois, preservando os controles T1/T5/T7. Se o pré-requisito, modelo, ferramenta ou skills nativas não estiverem disponíveis, manter o gate bloqueado.

| Cenário | Arranjo e resultado a comprovar | Prova existente / pendente |
| --- | --- | --- |
| T1 | Issue única, proposta validada em SHA fixo, worker encerrado e checkout reservado; sessão nova recupera a revisão, indica Apply como próximo gate e não recria branch, worktree ou change. | `tests/test_global_install.py` prova roteamento isolado; `tests/test_worktree_reservation.py` prova posse; comportamento da sessão nova pendente. |
| T5 | Milestone descartável com PR já existente e dependência bloqueada; sessão nova preserva escopo/modo de merge, identifica PR e não agenda o dependente antes do gate exigido. | Contrato de `skills/milestone-orchestrator/SKILL.md` e testes de estado existentes; prova da sessão nova pendente. |
| T7 | Dois candidatos reais com evidência equivalente; sessão nova apresenta os dois, pede escolha e não escreve até a resposta. | Contrato de `skills/resume-workflow/SKILL.md`; prova da sessão nova pendente. |

Antes de executar, confirmar descoberta do teste, ferramentas reais, isolamento do HOME/worktrees, fixture de GitHub/ledger e posse dos dados descartáveis; não tocar issues/PRs reais para simular interrupção. Revalidar esta proposta com `openspec validate issue-61-opencode-safe-resume --strict --no-interactive` no SHA exato; rodar amostra focada de instalador e helpers, depois a suite exigida `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` na revisão candidata final. Resultados antigos ou de SHA diferente não aprovam o gate. O `E_RETRY_LIMIT` histórico da migração upstream não autoriza contorno, instalação forçada, downgrade ou aceite de falhas.
