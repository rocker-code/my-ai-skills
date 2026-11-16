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
4. Verify independent terminal runtime evidence of the previous writer and reservation before effects; a null PID, fixture prose or stale registry is insufficient. If ambiguous, retain and report blocker for the affected issue only.
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

O pré-requisito [#71 — contrato de distribuição nativa OpenSpec 2.0](https://github.com/rocker-code/my-ai-skills/issues/71) foi entregue pela PR #72 no merge de `main` `5e33688d2a9db702e6bd0f2027d778f3baebdf35`, integrado nesta branch sem conflitos textuais. O contrato entregue usa `.agents/skills/openspec-*/SKILL.md`, com `.agents/skills/.openspec-target` declarando `opencode`; remove `.opencode/commands/opsx-*.md` e as cópias `.opencode/skills/openspec-*/SKILL.md` legadas. `openspec --version` retornou `2.0.0`, e `openspec context --json` / `openspec list --json` reconheceram este root e o change ativo. Antes da prova, conferir novamente o CLI, o root e os arquivos reais no ambiente descartável: presença de arquivos não equivale a invocação pelo modelo. Não executar `init`/`update`, restaurar arquivos legados ou alterar a distribuição nesta continuação. O conflito P1 da revisão de #69 não integra o escopo de #61; o `E_RETRY_LIMIT` histórico é separado e não autoriza contorno.

Em HOME e repositórios descartáveis, com OpenCode/OpenSpec 2.0 reais e modelo habilitado, instalar a revisão candidata de `resume-workflow` usando o contrato nativo entregue em `.agents/skills/`, sem tocar no HOME do usuário nem substituir o pacote global. Registrar origem e hash da skill OpenSpec efetivamente carregada e comprovar descoberta **e invocação** no OpenCode por sessão nova (não inferir a partir de arquivo existente, nome de comando ou mensagem do agente); usar a skill nativa aplicável para verificar a transição até Apply, sem executar Apply sobre a issue real. Registrar SHA imutável da candidata, IDs de sessão, prompts, respostas, eventos e estado Git/OpenSpec/PR antes/depois, preservando os controles T1/T5/T7. Se modelo, ferramenta ou skills nativas não estiverem disponíveis, manter o gate bloqueado.

### Critérios executáveis da prova (lacuna P1 da revisão de `f31fc53`)

O smoke atual `tests/smoke_resume_candidate_opencode.py:125–197` só valida retorno, texto não vazio e inventário Git antes/depois; o JSON `recovery-evidence.json` é narrativa, não um registro de reserva nem ledger. No Apply, fortalecer a fixture em repositório/HOME descartáveis: criar worktrees reais quando o cenário requer, registrar e consultar a reserva pelo helper `scripts/worktree-reservation` no Git common dir descartável, e registrar/consultar eventos de run/issue/stage/execução pelos helpers `workflow-event`/`workflow-report` existentes (sem criar ledger alternativo). O shim GitHub é somente leitura e deve registrar chamadas e recusar mutações; qualquer escrita, timeout, saída não parseável ou indisponibilidade de helper/modelo é falha/bloqueio, não PASS. Antes de cada sessão, confirmar worktree, branch, HEAD, status completo, root OpenSpec, proposta validada no SHA da fixture, reserva/owner/state/digest, eventos/resultado/merge mode/dependências do ledger e PR/head simulados; capturar os mesmos estados após a sessão e comparar campos relevantes, não só o inventário Git.

Vincular o teste ao HEAD limpo da candidata por `git rev-parse HEAD`, manifesto instalado `revision`, bytes/hash de `resume-workflow` e bytes/hash da skill nativa `.agents/skills/openspec-*/SKILL.md` da fixture (anotar origem real, symlinks resolvidos e ausência de comandos legados). Para T1/T5 e **a segunda fase de T7**, reter JSONL/eventos OpenCode com ID de sessão e evento de descoberta/listagem da skill nativa seguido de chamada da ferramenta de skill ou leitura efetiva do arquivo canônico pelo agente, correlacionados ao mesmo ID e ao caminho/hash pré-registrado; corroborar a aplicação por acesso observável ao contrato/instruções OpenSpec nativas, não apenas pela resposta que diz "usei" ou por `openspec` CLI isolado. A primeira fase de T7 termina na pergunta, sem invocação nativa esperada; a resposta explícita do usuário e os eventos posteriores devem continuar no **mesmo ID de sessão**, não em uma nova sessão. Se o OpenCode não expuser eventos suficientes para provar chamada e origem, ampliar instrumentação somente na fixture descartável ou declarar gate bloqueado, sem inferir invocação de texto ou existência de arquivo. A skill aplicável pode diferir por cenário; registrar qual e por quê, sem executar Apply na issue real. Após qualquer novo commit candidato, invalidar provas de SHA anterior e repetir a prova.

| Cenário | Arranjo e resultado a comprovar | Prova existente / pendente |
| --- | --- | --- |
| T1 | Issue única com proposta validada e SHA fixo, reserva real do checkout, evento de último gate verificado e prova **independente do runtime** de que o writer anterior chegou a estado terminal (ID de execução e confirmação autoritativa acessível); `pid: null`, ausência de processo ou texto da fixture não bastam. Sem prova terminal, bloquear qualquer transição/Apply, sem reivindicar owner parado. Com prova, a sessão identifica issue/HEAD/gate e Apply como próximo passo, sem executar Apply; `status/verify` mantém owner/state/digest, ledger mantém gate e nenhum novo run/dispatch, PR ou branch/worktree/change duplicado; registra descoberta e invocação da skill nativa aplicável no mesmo ID de sessão. | `tests/test_global_install.py` prova roteamento isolado; `tests/test_worktree_reservation.py` prova posse; smoke atual não valida estes resultados. |
| T5 | Milestone descartável com PR/head simulados, `merge_mode=manual` e dependência bloqueada registrados no ledger; reservas reais para os checkouts relevantes. Asserções: sessão indica PR/head e próximo gate da PR, mantém modo manual e dependência em espera, sem novo dispatch para consumidor, sem PR duplicada e sem mutações na reserva/ledger/fixture GitHub; registra descoberta e invocação nativa no ID da sessão. | Contrato de `skills/milestone-orchestrator/SKILL.md` e testes de estado existentes; smoke atual só relata narrativa. |
| T7 | Dois candidatos efetivos com reservas/ledger distintos e igualmente plausíveis. **Fase 1:** resposta identifica ambos por issue/run, faz uma pergunta e pausa, sem escolha por recência, takeover, dispatch, escrita ou invocação nativa esperada. **Fase 2, na mesma sessão OpenCode:** usuário escolhe explicitamente issue/run; reinventariar checkout, reservas e ledger, conferir writer parado antes de transição, descobrir e invocar em modo somente leitura a skill OpenSpec 2.0 aplicável. Correlacionar evento de descoberta e invocação ao mesmo ID da fase 1 e ao caminho/hash da skill. Comparar ambas reservas/ledgers e Git/OpenSpec/GitHub antes/depois de cada fase; sem escolha explícita ou prova de segurança, permanecer bloqueado, sem promover T7 a PASS. | Contrato de `skills/resume-workflow/SKILL.md` e decisão aprovada; smoke atual não executa duas fases na mesma sessão nem detecta chamadas nativas. |

Antes de executar, confirmar descoberta do teste, ferramentas reais, isolamento do HOME/worktrees, fixture de GitHub/ledger e posse dos dados descartáveis; não tocar issues/PRs reais para simular interrupção. Revalidar esta proposta com `openspec validate issue-61-opencode-safe-resume --strict --no-interactive` no SHA exato; rodar amostra focada de instalador e helpers, depois a suite exigida `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` no **HEAD limpo e exato da candidata final após archive/sync e commits finais**, não em `80e5de0`, no merge intermediário ou em outro SHA. Resultados antigos ou de SHA diferente não aprovam o gate. O `E_RETRY_LIMIT` histórico da migração upstream não autoriza contorno, instalação forçada, downgrade ou aceite de falhas.
