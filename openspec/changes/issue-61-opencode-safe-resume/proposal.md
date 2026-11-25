# Proposal

## Why

A entrada `resume-workflow` já foi entregue pela PR #62, mas falta completar a prova nativa T1/T5/T7 da #61 e encerrar seu contrato. A sétima observação expôs uma sobreposição entre aceite da recuperação read-only, condição anterior à escrita e convenção JSON da fixture: o plano precisa distingui-las sem apagar a falha real nem reduzir segurança.

## What Changes

- Preservar a integração não forçada de `main@12ca324faf2865faa62d16e55715d3ddd0adb53a`, já entregue em `5b0fc0ad5ff553a0e091527ddff6ac4001b46dc4`, e o histórico exclusivo/dados locais; não repetir integração ou tarefas implementadas.
- Adaptar as fixtures existentes T1/T5/T7 a Git/GitHub/OpenSpec, reservas e recibos de runtime verificáveis, sem `workflow-event`, `workflow-report`, comentários operacionais ou registro substituto.
- Provar instalação da revisão candidata e descoberta/invocação nativa OpenSpec na sessão real, preservando o pedido natural de retomada e a distribuição OpenCode/Codex atual.
- Completar prova independente de writer parado em T1 e as duas fases T7 na mesma sessão; manter desconhecidos os resultados sem término/relatório acessível.
- Corrigir somente o oráculo da fixture: combinar campos semânticos limitados com fatos nativos obrigatórios, separar condições de posse pré-escrita e diagnóstico de serialização, sem classificar prosa, ignorar blockers arbitrários ou conceder efeitos.
- Substituir explicitamente a obrigação anterior de repetir native após qualquer commit por vínculo de entradas efetivas e revisão de impacto; T1/T5/T7 reais completos continuam obrigatórios e a suíte local completa continua vinculada ao HEAD final limpo exato.
- Verificar, arquivar/sincronizar e preparar a PR residual da #61, com suíte final no HEAD limpo exato e revisão independente.

## Capabilities

### New Capabilities

- `interrupted-workflow-resume`: retomada segura por evidência em sessão nova, sem histórico de chat nem dependência de telemetria.

### Modified Capabilities

- `global-workflow-distribution`: acrescentar cenário de roteamento natural sem substituir os contratos de distribuição, cinco skills oficiais e seleção independente de agentes já entregues.

## Impact

Alterações residuais previstas: `tests/smoke_resume_candidate_opencode.py`, `tests/test_resume_reinventory.py`, `tests/fixtures/resume_gh.py`, teste público em `tests/test_global_install.py`, documentação operacional e changelog; ajustar `skills/resume-workflow/SKILL.md` somente se houver lacuna comprovada após integração. Reutilizar instalador/launchers de main sem mudar seus bytes ou pins. Sem serviço, coletor, banco, nova API ou segunda máquina de estados.

Esta revisão estreita parte de `95007d991cd9940ed07e2c1a9ade9875dfe3fe94`, fonte de harness `fca6a971bc016d1d693e379c798a8f938605a040` e proposta aprovada `31cdb42b2d0e409e8820fa71d97177316c07f94a`. Só o Apply novo posterior à revisão poderá corrigir oráculo/testes e registrar projeção offline separada. JSON/condições aqui planejados são somente da fixture, não protocolo público de produção. Preservar os 14 itens concluídos, as sete falhas originais, T5/T7 NOT RUN e o episódio seq39/40/41.

## Scope and approved decisions

Escopo único: [#61](https://github.com/rocker-code/my-ai-skills/issues/61), branch/worktree `issue-61-resume-closeout`; nenhuma execução de #78, outra issue ou milestone real. A PR #62 está MERGED (`0cbf84ff53ea8c21ecaeb0ab8847d5430fac287f`). Não duplicar branch, worktree, change ou PR. A confirmação posterior do proprietário, **“Sim, se aprovado”**, estabelece `merge_mode=auto-if-green` para esta issue e substitui o HELD histórico: entrega futura depende de todos os gates e proteções atuais. Esta delegação é **Planning somente**, sem implementação, modelo, integração, archive, push, PR ou merge.

Preservar [decisão OpenSpec 2.0 nativo](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6922774044): skills oficiais reais, sem `/opsx-*` fabricado ou downgrade. Preservar [decisão T1/T7](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6931892505): T7 pergunta e pausa sem invocação nativa antes da escolha; após escolha explícita, reinventário e invocação read-only na mesma sessão; T1 exige prova terminal independente, não `pid:null` ou prosa.

As menções antigas a ledger/eventos no corpo da issue e na decisão descrevem o mecanismo então existente; sua função probatória será preservada por fontes nativas, conforme as políticas entregues em #75/#76/#77 no main pinado. Não reduzir nenhum critério T1–T7 nem reintroduzir audit/ready. Esta mudança material exige revisão independente da proposta exata antes de Apply; provas offline já executadas são preservadas, mas a prova nativa completa e os gates finais continuam pendentes.
