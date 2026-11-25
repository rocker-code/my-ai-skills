# Proposal

## Why

A entrada `resume-workflow` já foi entregue pela PR #62, mas falta comprovar a retomada real da #61 em sessão OpenCode nova e encerrar seu contrato. A continuação deve preservar o trabalho acumulado e as decisões do proprietário, reconciliando a prova com o workflow nativo atual, sem restaurar telemetria removida.

## What Changes

- Reconciliar o change existente com `main@12ca324faf2865faa62d16e55715d3ddd0adb53a`; integrar esse commit por merge não forçado somente no Apply, mantendo os 38 commits exclusivos observados e os dados locais.
- Adaptar as fixtures existentes T1/T5/T7 a Git/GitHub/OpenSpec, reservas e recibos de runtime verificáveis, sem `workflow-event`, `workflow-report`, comentários operacionais ou registro substituto.
- Provar instalação da revisão candidata e descoberta/invocação nativa OpenSpec na sessão real, preservando o pedido natural de retomada e a distribuição OpenCode/Codex atual.
- Completar prova independente de writer parado em T1 e as duas fases T7 na mesma sessão; manter desconhecidos os resultados sem término/relatório acessível.
- Verificar, arquivar/sincronizar e preparar a PR residual da #61, com suíte final no HEAD limpo exato e revisão independente.

## Capabilities

### New Capabilities

- `interrupted-workflow-resume`: retomada segura por evidência em sessão nova, sem histórico de chat nem dependência de telemetria.

### Modified Capabilities

- `global-workflow-distribution`: acrescentar cenário de roteamento natural sem substituir os contratos de distribuição, cinco skills oficiais e seleção independente de agentes já entregues.

## Impact

Alterações residuais previstas: `tests/smoke_resume_candidate_opencode.py`, `tests/test_resume_reinventory.py`, `tests/fixtures/resume_gh.py`, teste público em `tests/test_global_install.py`, documentação operacional e changelog; ajustar `skills/resume-workflow/SKILL.md` somente se houver lacuna comprovada após integração. Reutilizar instalador/launchers de main sem mudar seus bytes ou pins. Sem serviço, coletor, banco, nova API ou segunda máquina de estados.

## Scope and approved decisions

Escopo único: [#61](https://github.com/rocker-code/my-ai-skills/issues/61), branch/worktree `issue-61-resume-closeout`; nenhuma execução de #78, outra issue ou milestone real. A PR #62 está MERGED (`0cbf84ff53ea8c21ecaeb0ab8847d5430fac287f`); não existe PR aberta correspondente na inspeção de 25/11/2026. Não duplicar branch, worktree, change ou PR. Merge permanece **HELD**, pois a autorização original não foi recuperada; Planning/Apply/preparação de PR não autorizam merge.

Preservar [decisão OpenSpec 2.0 nativo](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6922774044): skills oficiais reais, sem `/opsx-*` fabricado ou downgrade. Preservar [decisão T1/T7](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6931892505): T7 pergunta e pausa sem invocação nativa antes da escolha; após escolha explícita, reinventário e invocação read-only na mesma sessão; T1 exige prova terminal independente, não `pid:null` ou prosa.

As menções antigas a ledger/eventos no corpo da issue e na decisão descrevem o mecanismo então existente; sua função probatória será preservada por fontes nativas, conforme as políticas entregues em #75/#76/#77 no main pinado. Não reduzir nenhum critério T1–T7 nem reintroduzir audit/ready. Esta mudança material exige revisão independente da proposta exata antes de Apply; testes/smokes atuais continuam pendentes.
