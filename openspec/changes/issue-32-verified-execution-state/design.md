# Design

## Context

Base: `main` @ `5825a9c`. Auditoria: https://github.com/rocker-code/my-ai-skills/issues/32#issuecomment-6621679619.

- `scripts/workflow-event` grava/atualiza um comentário oculto por issue/run (`schema_version: 1`), com `at = iso_time()` do escritor em todo evento; `--evidence` aceita apenas URL GitHub/SHA; motivos de espera fixos em `REASONS`.
- `scripts/workflow_metrics.py::summarize_run` ordena eventos por `at`, emparelha início/fim por `(stage, worker)` e fecha intervalos abertos em `as_of`; ignora tipos de evento desconhecidos; `parse_run_comment` aceita somente `schema_version == 1`.
- `scripts/workflow-report` consome `summarize_run` e gera Markdown/JSON/CSV; `skills/milestone-progress` usa o JSON.
- `skills/milestone-orchestrator/SKILL.md` define o orquestrador como escritor único; workers devolvem timestamps, mas o CLI não os aceita.
- `scripts/sync-plugin` já distribui os três scripts e empacota `protocol/AI_WORKFLOW.md`; não precisa mudar.

## Goals / Non-Goals

**Goals:**
- Representar observações de execução com fonte, horário e correlação, e derivar delas um estado verificado honesto.
- Manter o registro único por issue/run, aditivo em `schema_version: 1`.
- Expor um resumo de progresso pequeno no relatório existente.

**Non-Goals:**
- Consultar o runtime ativamente a partir dos scripts (cada executor tem APIs diferentes; o executor observa e registra).
- Adaptador M2T (CONTRACT_BLOCKED em M2T #12), notificação para celular, registro de evidência/transporte de provas (#31), reserva de checkout (#35).
- Alterar o CSV do relatório ou `scripts/workflow-status`.

## Decisions

### D1 — Extensão aditiva em `schema_version: 1`
Novos tipos de evento (`worker_dispatched`, `state_observed`) e campos opcionais (`execution`, `observed_at`, `recorded_at`, `next`, `last_seen_at`). `summarize_run` atual ignora tipos desconhecidos, então cópias distribuídas antigas continuam lendo registros novos (com métricas antigas). Alternativa rejeitada: `schema_version: 2` — `parse_run_comment` antigo rejeitaria os registros e cópias já instaladas em outros repositórios deixariam de ler o histórico.

### D2 — Novos subcomandos de `workflow-event`
- `dispatch --stage S --worker-id W [--execution-kind K --execution-id ID] [--observed-at T]`: grava `type: stage_started`, `dispatch: "async"` e `execution`. Reutilizar `stage_started` mantém o emparelhamento existente e a legibilidade por leitores antigos; o término continua sendo `stage-end` do mesmo `(stage, worker)`. Worker padrão `orchestrator` é recusado para `dispatch` (despacho é sempre para outro worker).
- `observe --stage S --state running|completed|failed|interrupted|unknown --source SRC [--worker-id W] [--execution-kind K --execution-id ID] [--exit-code N] [--report present|absent|unknown] [--log-ref REF] [--observed-at T] [--next TEXT]`: grava `type: state_observed`.
- `stage-end`, `wait-end`, `wait-start` e `stage-start` aceitam opcionalmente `--observed-at`, `--source`, `--execution-*` e `--next`.
- Fontes: confirmatórias `runtime_event`, `runtime_query`, `ci_api`, `process_exit`, `test_report`; insuficientes `agent_prose`, `container_state`. O registro guarda `confirming: true|false` calculado no escritor (o leitor recalcula a partir da fonte para não confiar em campo editável).
- Tipos de execução: `worker`, `process`, `job`, `test_run`, `ci_run`. Identificador com `SAFE_ID` existente.
- `REASONS` += `tests`, `environment`.
- `--next`: até 160 caracteres, uma linha, sem caracteres de controle. Alternativa rejeitada: derivar o próximo passo automaticamente — só é possível para poucos estados e esconderia a intenção do orquestrador.

### D3 — Horário efetivo vs. horário de gravação
Com `--observed-at`, o evento recebe `at = observed_at` (horário efetivo usado pelas métricas) e `recorded_at = agora`. Sem ele, `at = recorded_at = agora` (comportamento atual). Validação: formato ISO-8601 com `Z`/offset, `observed_at <= agora + 120 s`, `observed_at >= created_at` do run. A ordenação existente por `at` mantém a causalidade dispatch → término.

### D4 — Estado verificado em `workflow_metrics.py`
Função nova (ex.: `verified_state(record, as_of)`) chamada por `summarize_run`, que acrescenta campos sem alterar os existentes quando não há observações:
- Por `(stage, worker)` aberto: observação confirmatória mais recente após o início. `running` → `working`; `completed|failed|interrupted|unknown` → `needs_reconciliation` com o estado observado, e o intervalo de trabalho termina no `at` dessa observação (não em `as_of`). Sem observação confirmatória mas com sinal insuficiente → `unconfirmed` (trabalho ainda medido até `as_of`, rotulado). Sem nenhuma observação → `unobserved` (comportamento legado exato).
- Estado da issue (`activity_state`): espera aberta → `waiting:<reason>`; senão reconciliação pendente → `unknown`/`interrupted`/`needs_reconciliation`; senão `working`/`unconfirmed`/`unobserved`; run finalizado → `completed`/`failed`.
- `incomplete_evidence`: execuções `test_run` sem observação confirmatória terminal, ou terminal com `report` `absent|unknown`.
- `status_summary`: `current_stage`, `activity_state`, `last_confirmed` (`state`, `source`, `execution`, `log_ref`, `at`), `blocker` (espera aberta, reconciliação pendente ou `null`), `next_action` (último `next`), `verified_at` (maior `last_seen_at`/`at` confirmatório).
Escolha de cortar o trabalho na observação terminal: evita o anúncio de atividade fantasma (T2) e mantém o legado intacto porque a regra só se aplica quando há observação.

### D5 — Registro finalizado e separação por issue
`workflow-event` recusa `stage-start`, `dispatch` e `wait-start` quando o registro já tem `run_finished`; `observe`, `stage-end`, `wait-end` e `rework` continuam permitidos (fechamento tardio e reconciliação). Isso protege contra gravar a issue B no registro de A. Separação de métricas já é estrutural (um comentário por issue); o teste T4 a comprova.

### D6 — Deduplicação de observação
Se a última `state_observed` da mesma execução (ou do mesmo `(stage, worker)` sem execução) tiver mesmo `state` e `source`, o escritor só atualiza `last_seen_at` dessa observação e imprime `"deduplicated": true`. Limita o tamanho do comentário (limite GitHub ~65 536 caracteres) e torna polling repetido inócuo; a regra de preferir callbacks fica na skill.

### D7 — Referências de log
`--log-ref` aceita URL `https://github.com/...`, SHA (7–64 hex) ou `^[a-z][a-z0-9-]{1,30}:[A-Za-z0-9._:/@-]{1,200}$`. Recusa espaço, `?`, `=`, `&`, `#`. A skill documenta que referências não podem conter credenciais. Caminhos locais absolutos não são suportados como prova portátil (transporte é escopo de #31).

### D8 — Composição com #31
#31 define o registro de evidência de teste (comando, HEAD, fingerprint, contagens, relatórios) nos mesmos scripts. Esta mudança só define correlação/observação; `execution.id` é a chave para a evidência de #31 referenciar a execução. Na ordem prevista (#35 → #31 → #32), o Apply de #32 MUST reutilizar validadores/helpers que #31 tiver adicionado em `workflow_metrics.py` (padrões de referência, parse de horário, presença de relatório) em vez de duplicá-los; se #31 tiver modelado presença de relatório, `--report` mapeia para esse campo mantendo o comportamento do spec. Sem dependência rígida: se #31 não estiver mergeada, implementar helpers locais em `workflow_metrics.py`, em funções reutilizáveis. Testes em arquivo novo para reduzir conflito com #31 em `tests/test_workflow_metrics.py`.

### D9 — Documentação e distribuição
Regras de reconciliação/callback/escopo em `skills/milestone-orchestrator/SKILL.md` (seção "Workflow timing instrumentation") e `protocol/AI_WORKFLOW.md` (seção "Workflow timing and Kaizen metrics"); `skills/milestone-progress/SKILL.md` passa a ler `status_summary`; README pt/en em paridade; `scripts/sync-plugin` regenera `plugins/my-ai-skills/` e as cópias em `skills/*/references/AI_WORKFLOW.md`.

## Matriz requisito → código → teste

| Cenário / requisito | Critério ou risco | Código | Camada | Teste |
|---|---|---|---|---|
| Correlação de execução; id inseguro recusado | Correlacionar run/issue/etapa/worker/execução | `workflow-event` (`observe`, `dispatch`) | CLI com `gh` falso | novo `test_observe_records_correlation_and_rejects_unsafe_id` |
| Fonte e horário (callback, futuro/anterior) | Fonte/horário da observação | `workflow-event` validação D3 | CLI | novo `test_observed_at_is_effective_time_and_validated` |
| Sinais insuficientes | Prosa/container insuficientes | `workflow_metrics` D4 | Unidade (fixture) | novo `test_weak_sources_do_not_confirm_activity` |
| T1 despacho assíncrono | AC4 causalidade e métricas | `dispatch` + D4 | Fixture + CLI | novo `test_async_dispatch_duration_until_worker_completion` |
| T2 processo some sem relatório | AC1 reconciliação | D4 corte na observação | Fixture | novo `test_unknown_observation_stops_work_and_requires_reconciliation` |
| Processo encerrado antes de anúncio | AC1 | D4 | Fixture | mesmo teste (caso `completed` sem `stage_end`) |
| T3 decisão do usuário / CI / ambiente | AC3 | `REASONS`, D4 | Unidade | novo `test_wait_classification_owner_input_ci_environment` |
| Ausência de JUnit | AC2 | D4 `incomplete_evidence` | Fixture | novo `test_missing_report_is_incomplete_evidence` |
| T4 duas issues | AC5 | D5 + `workflow-report` | CLI + relatório | novo `test_two_issues_same_run_are_independent_and_finished_record_refuses_stage` |
| T5 callback sem polling redundante | Dedup e uso do callback | D6 | CLI | novo `test_repeated_observation_is_deduplicated` |
| Resumo simples | Resumo exigido | D4 `status_summary` + `workflow-report` Markdown/JSON | Relatório | novo `test_report_shows_status_summary` (inclui caso sem observação) |
| Referências seguras | Segredo/texto livre | D7 | CLI | novo `test_log_ref_validation` |
| Registro antigo | AC6 legibilidade | D1/D4 | Unidade | existentes em `tests/test_workflow_metrics.py` sem alteração + novo `test_legacy_record_unchanged_and_unobserved` |
| Reconciliação/continuidade do orquestrador | AC1/AC6 progresso sem comando por etapa | `skills/milestone-orchestrator/SKILL.md`, `protocol/AI_WORKFLOW.md` | Documentação | revisão + `scripts/sync-plugin` sem diff residual |

## Risks / Trade-offs

- [Comentário cresce além do limite do GitHub] → observar só em transições, deduplicação D6; o erro do `gh` já é reportado e não bloqueia o workflow.
- [Escritor único perde atualização concorrente] → regra existente de escritor único mantida; workers devolvem observações ao orquestrador.
- [Horário informado manipulado/errado] → validação D3; `recorded_at` preservado para auditoria.
- [Conflito de arquivos com #31] → serialização prevista, helpers reutilizáveis, testes em arquivo novo; rebase no início do Apply.
- [Executor sem callback/consulta suportada] → registrar `unknown` com a fonte disponível; estado nunca é promovido por sinal insuficiente.

## Migration Plan

Sem migração: registros existentes permanecem válidos. Rollback = reverter os scripts; registros com novos eventos continuam legíveis pela versão anterior (eventos ignorados).

## Open Questions

Nenhuma bloqueante. Integração final M2T aguarda o contrato de M2T #12 (follow-up fora do escopo).
