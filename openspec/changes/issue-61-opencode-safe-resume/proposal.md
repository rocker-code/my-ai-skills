# Proposal

## Why

A entrada `resume-workflow` já foi entregue pela PR #62, mas falta completar a prova nativa T1/T5/T7 da #61 e encerrar seu contrato. Após a revisão de aceite por fase já implementada, a auditoria de capacidade identificou exclusão artificial de Verify no perfil descartável T5; corrigir essa lacuna não transforma os runs sem dispatch nativo em aprovação.

Emenda atual: o proprietário autorizou preparar login manual novo pela assinatura ChatGPT em perfil privado isolado, sem copiar credenciais/configuração/histórico pessoais nem usar API paga. OpenCode instalado agora é 2.4.2, diferente do 2.3.2 observado; autorização de preparação não é autorização de autenticação pelo agente ou de inferência.

Revisão de `21d0712` após finding independente `ses_de5f1cb7affeU03kmjpOtA6i4m`: a autorização explícita **“autorizado”**, após distinguir quota ChatGPT Plus/Pro de API por uso, permite quota de assinatura em princípio. Supersede somente nessa rota comprovada a antiga exigência numérica all-zero; o ramo sem credenciais mantém esse guard intacto. `cost=[]` permanece display unknown, nunca zero/grátis. Entitlement ainda requer confirmação manual; API paga/paygo/quota extra/fallback não estão autorizados. O recibo concreto de método nativo→conclusão→perfil/conexão/provider/catalog está em design §6.2, com parada pré-login se suporte/proveniência não forem verificáveis.

## What Changes

- Emenda de continuação integral sobre `40c94cb966943d5cc6d0307e1eb8232f8b544f9f`: 3.12 está aprovada somente offline, mas seu CLI encerra e destrói a cadeia viva antes de 4.3. Acrescentar **3.13/§6.4/L2**: autorização futura específica do coordenador antes de login, mesma instância Supervisor até main completo, seleção/confirmação local pós-catálogo e evidência **pós-auth no mesmo processo**. Estender minimamente a biblioteca workflow_evidence existente para essa fronteira, sem envolver login no recorder capturante. Nenhuma autorização de inferência existe nesta Planning; flags/recibos não a inventam. Preservar os 20 itens concluídos e todo histórico.

- Emenda de observação local sobre `e0cea77d530270d395dd596c0a4556d8a87f1dc3`: acrescentar somente 3.12/design §6.3. O shell do agente não fornece TTY e não há observer interativo não capturante demonstrado. Permitir controlador local versionado, iniciado posteriormente pela pessoa no próprio terminal, que valida capacidade/identidade **antes** de spawn e observa diretamente Popen/wait do filho auth com FDs herdados. Essa prova é `local-controller/os-wait`, não callback/sessão OpenCode inventados. Mudança material de interface de proveniência exige revisão do novo pin antes de Apply; 3.10/3.11 concluídas offline são preservadas. Não abrir terminal, pedir login ou executar autenticação nesta Planning.

- Preservar a integração não forçada de `main@12ca324faf2865faa62d16e55715d3ddd0adb53a`, já entregue em `5b0fc0ad5ff553a0e091527ddff6ac4001b46dc4`, e o histórico exclusivo/dados locais; não repetir integração ou tarefas implementadas.
- Adaptar as fixtures existentes T1/T5/T7 a Git/GitHub/OpenSpec, reservas e recibos de runtime verificáveis, sem `workflow-event`, `workflow-report`, comentários operacionais ou registro substituto.
- Provar instalação da revisão candidata e descoberta/invocação nativa OpenSpec na sessão real, preservando o pedido natural de retomada e a distribuição OpenCode/Codex atual.
- Completar prova independente de writer parado em T1 e as duas fases T7 na mesma sessão; manter desconhecidos os resultados sem término/relatório acessível.
- Corrigir somente o oráculo da fixture: combinar campos semânticos limitados com fatos nativos obrigatórios, separar condições de posse pré-escrita e diagnóstico de serialização, sem classificar prosa, ignorar blockers arbitrários ou conceder efeitos.
- Autorizar expressamente no Apply futuro **somente em T5** uma regra `skill/openspec-verify-change/allow` e sua alternativa canônica de fonte/prova/catálogo. Isso altera materialmente a capacidade de carregar instruções, não shell/FS/escrita/MCP/credenciais; T1 e os limites T7 permanecem inalterados, sem wildcard ou nova etapa/framework.
- Estender minimamente o harness existente para preparar HOME/XDG/CODEX_HOME/DB privados novos, pausar antes de inferência para login OAuth manual nativo e retomar o **mesmo** sandbox mediante verificação de identidade/posse/runtime/HEAD/rota. Nenhum import/export de segredo ou fallback API; preço zero sozinho não prova assinatura. Se metadados nativos seguros não comprovarem a rota, manter BLOCKED (design §6.2).
- Substituir explicitamente a obrigação anterior de repetir native após qualquer commit por vínculo de entradas efetivas e revisão de impacto; T1/T5/T7 reais completos continuam obrigatórios e a suíte local completa continua vinculada ao HEAD final limpo exato.
- Verificar, arquivar/sincronizar e preparar a PR residual da #61, com suíte final no HEAD limpo exato e revisão independente.

## Capabilities

### New Capabilities

- `interrupted-workflow-resume`: retomada segura por evidência em sessão nova, sem histórico de chat nem dependência de telemetria.

### Modified Capabilities

- `global-workflow-distribution`: acrescentar cenário de roteamento natural sem substituir os contratos de distribuição, cinco skills oficiais e seleção independente de agentes já entregues.

## Impact

Alterações residuais previstas: `tests/smoke_resume_candidate_opencode.py`, `tests/test_resume_reinventory.py`, `tests/fixtures/resume_gh.py`, teste público em `tests/test_global_install.py`, documentação operacional e changelog; ajustar `skills/resume-workflow/SKILL.md` somente se houver lacuna comprovada após integração. Reutilizar instalador/launchers de main sem mudar seus bytes ou pins. Sem serviço, coletor, banco, nova API ou segunda máquina de estados.

Esta emenda parte de `a9bc6b23f5a4dd5bc512a78ca3cb8198f9386d87`; proposta antes aprovada `a0b4796fb1a2646125c6e62bfa6ca450d2118e7e`, implementação `cce46754a5494c27ab2454dd1df9feac6ca64f99`. Preservar os 17 itens concluídos e todos os treze runs inteiros FAILED, inclusive `ev-20261125T144642Z-ea89df23` (T1 fenced JSON e nenhuma invocação OpenSpec nativa; T5/T7 NOT RUN). Só Apply genuinamente novo após revisão independente do novo pin poderá implementar preparação/compatibilidade. Runtime/modelo/perfil/auth são mudanças materiais F1: exigir novo T1/T5/T7 completo depois de revisão e autorização separada do pai. Nenhum décimo quarto run, autenticação, instalação ou alteração de runtime/instruções globais nesta Planning.

## Scope and approved decisions

Escopo único: [#61](https://github.com/rocker-code/my-ai-skills/issues/61), branch/worktree `issue-61-resume-closeout`; nenhuma execução de #78, outra issue ou milestone real. A PR #62 está MERGED (`0cbf84ff53ea8c21ecaeb0ab8847d5430fac287f`). Não duplicar branch, worktree, change ou PR. A confirmação posterior do proprietário, **“Sim, se aprovado”**, estabelece `merge_mode=auto-if-green` para esta issue e substitui o HELD histórico: entrega futura depende de todos os gates e proteções atuais. Esta delegação é **Planning somente**, sem implementação, modelo, integração, archive, push, PR ou merge.

Preservar [decisão OpenSpec 2.0 nativo](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6922774044): skills oficiais reais, sem `/opsx-*` fabricado ou downgrade. Preservar [decisão T1/T7](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6931892505): T7 pergunta e pausa sem invocação nativa antes da escolha; após escolha explícita, reinventário e invocação read-only na mesma sessão; T1 exige prova terminal independente, não `pid:null` ou prosa.

As menções antigas a ledger/eventos no corpo da issue e na decisão descrevem o mecanismo então existente; sua função probatória será preservada por fontes nativas, conforme as políticas entregues em #75/#76/#77 no main pinado. Não reduzir nenhum critério T1–T7 nem reintroduzir audit/ready. Esta mudança material exige revisão independente da proposta exata antes de Apply; provas offline já executadas são preservadas, mas a prova nativa completa e os gates finais continuam pendentes.
