# Instrumentação do workflow pelo coordenador

Este contrato aplica-se **somente** quando há contexto explícito de workflow
executor autorizado, com issue/run definidos. Invocar uma skill isoladamente não
cria contexto, run, etapa, vínculo ou autorização GitHub. Não deduzir etapa de
prosa, título, ferramenta usada ou skill carregada. Não instalar dependências,
alterar configuração real ou iniciar `observe` automaticamente.

## Posse e capacidade

O coordenador é o único escritor por issue/run: chama `aew workflow transition`
e `aew workflow reconcile`. Workers, observador e dashboard nunca publicam
autonomamente. A capacidade pode ser verificada com `aew workflow --help` ou o
launcher `scripts/aew` realmente disponível. Sem helper, acesso GitHub ou ponte,
registrar capacidade degradada/NOT RUN e continuar o desenvolvimento autorizado;
não inventar aprovação ou cobertura de runtime. OpenCode/Codex mantêm o caminho
GitHub-only; não há adaptador runtime nativo Codex nesta versão.

`coordinator: true` e `reconcile --coordinator` declaram uma autorização prévia
real para aquele escopo; não são autorização obtida da config read-only. Nunca
fabricar essa declaração para uma skill isolada. Usar o mesmo `--state-dir` em
todas as operações e no logger manual; não criar outro domínio para contornar
outbox/conflito. O observador é opcional, opt-in e independente da TUI, não outro
orquestrador.

## Identidades duráveis e fronteiras

Manter no ledger/handoff `issue_url`, `run_id`, `stage`, `worker_id`,
`execution.kind`, `execution.id`, `operation_ids`, `session_id`, `worktree`,
`branch`, `state_dir` e horários efetivos UTC. `run_id` é reutilizado na retomada;
`operation_id` é único no diretório de estado, inclusive entre issues do mesmo run.
Gerar cada ID uma vez e preservá-lo com o payload/horário original em todo retry.
Uma nova execução/rework recebe novo `execution.id`, não um ID novo para tentar
novamente a mesma publicação. Dependências `depends_on` apontam para operações
já aceitas do mesmo escopo. Não reutilizar ID com payload diferente.

| stage | Fronteira real e gate correspondente |
|---|---|
| issue_audit | Início/resultado do audit atual da issue. |
| explore | Exploração oficial e evidência do código/contrato atual. |
| resolve_questions | Pesquisa/decisões resolvidas; owner input só quando há decisão material real. |
| proposal | Criação/revisão dos artefatos oficiais de proposta. |
| proposal_review | Revisão/validação da revisão exata e gates independentes aplicáveis. |
| apply | Despacho da sessão Apply fresca e entrega correlacionada do contrato validado. |
| tests | Execução de testes e prova própria do runner/relatório; não atividade do agente. |
| verify_archive | Verificação/validação/archive e inspeção dos artefatos resultantes. |
| prepare_pr | Preparação/publicação do PR no escopo autorizado e SHA conhecido. |
| pr_audit | Auditoria independente do head exato, incluindo arquitetura quando aplicável. |
| ci | Resultado oficial dos checks exigidos no head exato. |
| merge | Merge/fechamento realmente confirmados, respeitando merge_mode e políticas. |
| kaizen | Resultado de melhoria pós-entrega ou NO PROCESS CHANGE documentado. |

Em cada fronteira aplicável, o coordenador envia JSON limitado a 16 KiB com
`version:1`, `coordinator:true`, `operation_id`, `event`, issue/run, identidade
tipada e `at`. Use `stage-start` no início síncrono e `dispatch` no despacho
assíncrono: retorno imediato do despacho não é término. Abra `run-start` uma vez
por issue. Se uma etapa não é aplicável ou não foi executada, registre a razão no
ledger, não fabrique uma execução concluída. O usuário não precisa emitir comando
por etapa: o coordenador executa as chamadas nas fronteiras reais.

Workers de planejamento com várias subetapas devolvem fronteiras estruturadas e
horários reais, pelo canal de progresso disponível ou no retorno final. O coordenador
registra os horários efetivos recebidos sem inferi-los do transcript. Ausência de
canal incremental é uma limitação, não justificativa para atribuir um início/término
fictício. Planning → Apply continua exigindo sessão genuinamente fresca e revisão
validada exata; a instrumentação não substitui esse gate.

## Despacho, retorno e sessão tardia

O handoff instrumentado inclui:

```yaml
workflow_instrumentation:
  enabled: true # somente no workflow executor previamente autorizado
  issue_url: https://github.com/owner/repo/issues/7
  run_id: wf-exemplo
  stage: apply
  worker_id: worker-a
  execution: {kind: worker, id: exec-apply-a}
  operation_ids: {dispatch: op-apply-a}
  dispatched_at: <UTC real do despacho>
  session_id: null # preencher somente quando o runtime devolver ID real
  worktree: /caminho/checkout-validado
  branch: branch-validada
  state_dir: /caminho/estado-compartilhado
```

O worker valida issue/run/etapa/execução/worktree antes de agir, preserva IDs nas
continuações e devolve esse envelope com `started_at`, `finished_at`,
`result` (completed/failed/interrupted/unknown), `evidence_refs`, comandos e
PASS/FAIL/NOT RUN, candidato/SHA e gates efetivamente verificados. Ausência de
`session_id` continua `null`; nunca usar sessão coordenadora como fallback,
extrair ID de prosa ou afirmar atividade por retorno do despacho.

Se a abertura declarou worktree/branch mas o ID chega depois, o coordenador usa
`reconcile --binding-input` com `{version:1,operation_id,session_id}`. Não altera
o payload da abertura. Retry repara publicação/vínculo separadamente, sem nova
abertura. Troca de execução exige reconciliar a anterior e remover exatamente
seu vínculo com `aew unbind`; não substituir silenciosamente uma sessão vinculada.
Contexto/PID ou checkout divergentes exigem nova validação, nunca aproximação.

## Resultado, esperas e recuperação

Antes de término semântico, correlacionar o retorno do worker ao envelope e
verificar os gates da etapa na revisão exata. Só então emitir `observe` e
`stage-end` compatíveis. Sucesso/inatividade de sessão não produz `observe completed`,
conclusão de etapa, prova de processo filho ou aprovação de teste. Worker com fonte
runtime exige evidência e `log_ref: worker-result:<execution-id>`; `test_run` usa
o ID real emitido por `workflow-evidence`, fonte `test_report`/`process_exit`,
`report:present` e `evidence:<execution-id>` verificada no candidato. Referência
presente não é verdict: executar o verificador exigido e preservar gates hosted.
Registrar resultado desconhecido/incompleto quando faltar prova, sem promover a pass.

Esperas explícitas do coordenador usam `wait-start`/`wait-end` no instante real,
com motivo permitido. Permissão/formulário runtime permanece sinal local enquanto
aberto. `reconcile` só materializa intervalos completos, cobertos e correlacionados:
une sobreposições, subtrai cobertura canônica e publica pares v1 atomicamente.
Não fecha espera explícita de outra origem. Lacuna/consulta sem horário mantém
intervalo não medido; inatividade não é espera humana.

Na retomada/interrupção, ler ledger, GitHub e outbox; executar `workflow reconcile`
para cada issue/run autorizado antes de decidir nova fronteira. Retomar pendências
com os mesmos IDs; não duplicar branch/run/abertura. `accepted`, `publication` e
`binding` têm significados distintos. Código não zero de instrumentação exige
relato da pendência, não interrupção do desenvolvimento já autorizado nem aprovação
de gate desconhecido. Não alternar para publicação manual após aceitação incerta:
primeiro reconciliar o mesmo domínio. Fallback manual só quando não há operação
estruturada pendente e a reconciliação demonstra que não haverá duplicação.

Continuar outra issue exige envelope próprio, mesmo dentro da mesma conversa.
Preservar rework/execuções anteriores como histórico; nunca reaproveitar seus
resultados para confirmar a execução atual. Ao terminar o workflow, registrar
`run-end` somente após seus gates/estado final reais. Não escrever prompts,
formulários, respostas humanas, erros/logs brutos ou credenciais em payload/evidência.

Exemplos completos, limites e recuperação: `docs/milestone-monitor.md` e versão
`.en.md`. Nenhuma destas instruções garante cumprimento automático por qualquer
modelo nem substitui autorização ou política do repositório.
