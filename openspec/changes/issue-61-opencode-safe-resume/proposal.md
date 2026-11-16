# Proposal

## Why

The established orchestrator and worktree helpers already prescribe resuming after an interrupted run, but a **new OpenCode session** has no explicit, globally discoverable recovery entrypoint for a natural request such as “continue de onde parou”. The request must trigger evidence-first recovery without trusting old chat, guessing a worktree, repeating passed gates, or stealing a running writer.

## What Changes

- Add the global `resume-workflow` skill to identify scope and reconstruct the last verified state before handing off to the existing `milestone-orchestrator`.
- Add a short routing rule in the managed global OpenCode `AGENTS.md` guidance to use the skill after interruptions.
- Cover global skill installation/discovery in the existing isolated installer test and document the user journey.
- Leave worktree reservations, event records, GitHub state, validation gates and merge permissions unchanged.

## Capabilities

### New Capabilities

- `interrupted-workflow-resume`: evidence-based safe recovery from a new OpenCode session.

### Modified Capabilities

- `global-workflow-distribution`: managed global guidance also routes natural recovery requests.

## Impact

`skills/resume-workflow/SKILL.md`, `scripts/install-global`, `tests/test_global_install.py`, `README.md`, `README.en.md`, changelog. Reuse the existing worktree and workflow protocols. No new runtime service, persisted database, UI or public API.

## Continuação da issue aberta

A PR #62 já foi incorporada: sua implementação inicial permanece válida, mas não comprova os cenários T1/T5/T7 nem arquiva/sincroniza este change. A continuação da #61 na branch/worktree `issue-61-resume-closeout` SHALL preservar o trabalho entregue, construir e executar uma prova isolada em sessões novas reais do OpenCode com modelo e com a **revisão candidata** da skill instalada, e registrar respostas e estado antes/depois. Uma PR de acompanhamento desta mesma issue SHALL conter apenas o escopo residual verificado, incluindo o OpenSpec arquivado/sincronizado; o gate final SHALL incidir sobre o HEAD limpo e exato dessa PR de acompanhamento, não sobre o HEAD histórico da #62. Não recriar a implementação inicial nem duplicar a PR incorporada.

Conforme a [DECISION da #61](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6922774044), a prova de descoberta/retomada terá como alvo o OpenSpec **2.0 nativo**: descobrir e invocar as skills `openspec-*` disponibilizadas ao OpenCode em `.agents/skills/`, sem exigir arquivos `/opsx-*` de comandos legados nem recorrer ao CLI 1.x. **Dependência entregue:** [#71 — contrato de distribuição nativa OpenSpec 2.0](https://github.com/rocker-code/my-ai-skills/issues/71), incorporada pela PR #72 em `main` no commit `5e33688d2a9db702e6bd0f2027d778f3baebdf35` e integrada nesta branch por merge não forçado. Essa entrega desbloqueia o planejamento e a verificação da prova nativa, mas não a aprova automaticamente: a sessão nova deve comprovar a descoberta e invocação efetiva da skill nativa aplicável na revisão candidata. O conflito P1 da spec compartilhada identificado na revisão independente de #69 não será resolvido em #61; o `E_RETRY_LIMIT` de #69 permanece separado e não autoriza contorno. Não restaurar arquivos legados removidos pela #71.

A revisão independente de `f31fc534086adcbcc7036cf3260fdff925cce52a` identificou lacuna P1 histórica: o smoke registrava narrativa e inventário Git superficial, sem reservas/ledger descartáveis nem invocação nativa comprovável. A candidata atual já semeia worktrees/reservas e ledger reais, compara snapshots e examina eventos OpenCode, mas ainda não comprova T7 em dois turnos na mesma sessão nem T1 com observação terminal independente do runtime; o evento `completed` escrito pela fixture e `pid: null` não bastam. A continuação SHALL exigir asserts sobre estados antes/depois de cada fase, evidência de descoberta, caminho/hash e chamada nativa no mesmo ID após a escolha explícita T7 e falha fechada se faltar prova terminal T1. Saída textual isolada e provas da revisão antiga não aprovam o gate. A correção pendente pertence ao Apply posterior, não a este planejamento.

Conforme a [DECISION posterior da #61](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6931892505), T7 exige **duas fases na mesma sessão OpenCode**: primeiro mostrar os dois candidatos igualmente plausíveis, fazer uma única pergunta de desambiguação e pausar sem seleção, takeover, dispatch ou escrita; descoberta nativa somente leitura é permitida, mas **invocação de skill OpenSpec nativa é proibida antes da escolha**. Só após escolha explícita de issue/run pelo usuário, reinventariar checkout, reserva e ledger, conferir que o writer anterior parou e então invocar a skill OpenSpec 2.0 apropriada em modo somente leitura, com evento de descoberta e invocação, origem, caminho e hash correlacionados ao mesmo ID de sessão. Comparar reservas, ledgers, Git, OpenSpec e GitHub antes/depois de cada fase. Em T1, `pid: null` ou texto de fixture afirmando “stopped” não satisfaz o gate: exigir prova terminal independente do runtime do writer anterior; sem ela bloquear transição/Apply. Prova histórica e suíte preliminar não aprovam esses gates.
