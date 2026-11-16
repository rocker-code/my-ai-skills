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

## Matriz de prova pendente para a retomada real

O `tests/smoke_global_opencode.py` verifica descoberta e expansão dos comandos, mas instala a revisão publicada `c48ac58beadc0a9712f59f60458a5c3df3ed5bfb`, não a versão atual da skill; portanto não prova T1/T5/T7. Na sessão Apply, preservar esse teste da distribuição pública e criar uma prova separada da revisão candidata em HOME e repositórios descartáveis, com OpenCode/OpenSpec reais, sem escrever no HOME do usuário nem substituir o pacote global. Registrar a revisão da skill efetivamente carregada, os IDs de sessão, os prompts, as respostas e o estado Git/OpenSpec antes/depois. Se for necessário um modelo para exercer a decisão do agente, não considerar como prova um smoke sem credenciais que somente verifica descoberta.

| Cenário | Arranjo e resultado a comprovar | Prova existente / pendente |
| --- | --- | --- |
| T1 | Issue única, proposta validada em SHA fixo, worker encerrado e checkout reservado; sessão nova recupera a revisão, indica Apply como próximo gate e não recria branch, worktree ou change. | `tests/test_global_install.py` prova roteamento isolado; `tests/test_worktree_reservation.py` prova posse; comportamento da sessão nova pendente. |
| T5 | Milestone descartável com PR já existente e dependência bloqueada; sessão nova preserva escopo/modo de merge, identifica PR e não agenda o dependente antes do gate exigido. | Contrato de `skills/milestone-orchestrator/SKILL.md` e testes de estado existentes; prova da sessão nova pendente. |
| T7 | Dois candidatos reais com evidência equivalente; sessão nova apresenta os dois, pede escolha e não escreve até a resposta. | Contrato de `skills/resume-workflow/SKILL.md`; prova da sessão nova pendente. |

Antes de executar, confirmar descoberta do teste, ferramentas reais, isolamento do HOME/worktrees, fixture de GitHub/ledger e posse dos dados descartáveis; não tocar issues/PRs reais para simular interrupção. Rodar amostra focada de instalador e helpers, depois a suite exigida `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` na revisão candidata final; resultados antigos ou de SHA diferente não aprovam o gate.
