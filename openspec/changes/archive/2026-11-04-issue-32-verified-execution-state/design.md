# Design

## Context

Base: `main` @ `5825a9c`. Auditoria: https://github.com/rocker-code/my-ai-skills/issues/32#issuecomment-6621679619.

- `scripts/workflow-event` grava/atualiza um comentário oculto por issue/run (`schema_version: 1`), com `at = iso_time()` do escritor em todo evento; `--evidence` aceita apenas URL GitHub/SHA; motivos de espera fixos em `REASONS`.
- `scripts/workflow_metrics.py::summarize_run` ordena eventos por `at`, emparelha início/fim por `(stage, worker)` e fecha intervalos abertos em `as_of`; hoje um `stage-end` tardio estende até o fim até mesmo um intervalo cujo runtime terminou antes. Ignora tipos de evento desconhecidos; `parse_run_comment` aceita somente `schema_version == 1`.
- `scripts/workflow-report` consome `summarize_run` e gera Markdown/JSON/CSV; `skills/milestone-progress` usa o JSON.
- `skills/milestone-orchestrator/SKILL.md` define o orquestrador como escritor único; workers devolvem timestamps, mas o CLI não os aceita.
- `scripts/sync-plugin` já distribui os três scripts e empacota `protocol/AI_WORKFLOW.md`; não precisa mudar (nenhum helper novo).
- Pré-requisitos mergeados antes do Apply (ordem #35 → #31 → #32): #35 adiciona `sys.dont_write_bytecode = True` nos helpers; #31 define a allowlist de `--evidence` (URL GitHub, SHA ou `^evidence:ev-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}$`), o comando `workflow-evidence` (`record`/`verify`) e o teste `test_event_accepts_evidence_reference_and_rejects_path`, deixando `workflow_metrics.py` inalterado.
- `ci_api`/`ci_run` designam uma fonte/execução genérica **quando existir**; não há `.github/` nem gate de CI hospedado configurado nesta base. Esta proposta não cria um.

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
Novo tipo de evento `state_observed`, `stage_started` existente para despacho assíncrono, e campos opcionais (`dispatch`, `execution`, `observed_at`, `recorded_at`, `next`, `last_seen_at`). `summarize_run` atual ignora tipos desconhecidos e campos extras, então cópias distribuídas antigas continuam lendo registros novos (com métricas antigas). Alternativa rejeitada: `schema_version: 2` — `parse_run_comment` antigo rejeitaria os registros e cópias já instaladas em outros repositórios deixariam de ler o histórico.

### D2 — Novos subcomandos de `workflow-event`
- `dispatch --stage S --worker-id W [--execution-kind K --execution-id ID] [--observed-at T]`: grava `type: stage_started`, `dispatch: "async"` e `execution`. Reutilizar `stage_started` mantém a legibilidade por leitores antigos; o término continua sendo `stage-end` do mesmo `(stage, worker)` e, para abertura tipada, da mesma execução. Worker padrão `orchestrator` é recusado para `dispatch` (despacho é sempre para outro worker).
- `observe --stage S --state running|completed|failed|interrupted|unknown --source SRC [--worker-id W] [--execution-kind K --execution-id ID] [--exit-code N] [--report present|absent|unknown] [--log-ref REF] [--evidence REF] [--observed-at T] [--next TEXT]`: grava `type: state_observed`. `--evidence` reutiliza o argumento existente com a allowlist de #31, sem ampliação.
- `stage-end`, `wait-end`, `wait-start` e `stage-start` aceitam opcionalmente `--observed-at`, `--source`, `--execution-*` e `--next`.
- Para intervalo iniciado com `execution {kind, id}`, `stage-end` deve repetir ambos os campos; um término sem execução só pode fechar início sem execução. Reutilizar o mesmo `(stage, worker)` em novo despacho/abertura exige identificador de execução distinto para cada execução tipada do run. CLI recusa `stage-end` de execução divergente em vez de fechar outra execução; chamadas legadas sem execução continuam emparelhadas por `(stage, worker)`.
- Fontes: confirmatórias `runtime_event`, `runtime_query`, `ci_api`, `process_exit`, `test_report`; insuficientes `agent_prose`, `container_state`. O registro guarda `confirming: true|false` calculado no escritor (o leitor recalcula a partir da fonte para não confiar em campo editável).
- Tipos de execução: `worker`, `process`, `job`, `test_run`, `ci_run`. Identificador com `SAFE_ID` existente.
- `REASONS` += `tests`, `environment`.
- `--next`: até 160 caracteres, uma linha, sem caracteres de controle. Alternativa rejeitada: derivar o próximo passo automaticamente — só é possível para poucos estados e esconderia a intenção do orquestrador.

### D3 — Horário efetivo vs. horário de gravação
Com `--observed-at`, o evento recebe `at = observed_at` (horário efetivo usado pelas métricas) e `recorded_at = agora`. Sem ele, `at = recorded_at = agora` (comportamento atual). Validação: formato ISO-8601 com `Z`/offset, `observed_at <= agora + 120 s`, `observed_at >= created_at` do run; observações e término de etapa vinculados a um despacho/abertura não podem preceder o início correspondente. A ordenação existente por `at` então mantém a causalidade dispatch → término.

### D4 — Estado verificado em `workflow_metrics.py`
Função nova (ex.: `verified_state(record, as_of)`) chamada por `summarize_run`, que acrescenta campos sem alterar os existentes quando não há observações:
- Cada `stage_started`/`dispatch` cria uma **incarnação** de intervalo identificada pelo próprio evento de abertura (posição estável no registro); armazena a execução tipada quando houver. Um `stage-end` com execução fecha apenas a incarnação com o mesmo `(stage, worker, kind, id)`; sem execução, fecha somente abertura sem execução. Para registros legados inteiramente sem execução, preservar o emparelhamento FIFO existente.
- Uma `state_observed` confirmatória só altera a incarnação da mesma etapa/worker **e da mesma execução**: se a abertura é tipada, exigir igualdade exata de `kind` e `id` (ausência de ID não é curinga); se a abertura não tem execução, só observação sem execução se associa. Desempatar reincarnações sem ID pelo `observed_at`/`at` efetivo dentro da janela da abertura: de sua abertura até seu fechamento, e nunca após a próxima abertura do mesmo par; se houver sobreposição ou ambiguidade, não atribuir a nenhuma. ID tipado é único por `(stage, worker)` no run, inclusive após fechamento. Callback atrasado da execução A pode ser registrado após o início de B e associado retrospectivamente a A quando seu horário efetivo pertence à janela de A; ID divergente, horário fora da janela ou correspondência ambígua permanecem observações históricas não correlacionadas e não alteram atividade, `incomplete_evidence`, `last_confirmed` nem `verified_at` de B. O escritor recusa término tipado sem correspondência e reutilização do mesmo ID, mas não descarta observações tardias válidas de A.
- Por incarnação aberta: observação confirmatória correlacionada mais recente após o início. `running` → `working`; `completed|failed|interrupted|unknown` → `needs_reconciliation` com o estado observado. A primeira observação terminal confirmatória da incarnação limita o trabalho definitivamente: `effective_work_end = min(stage_end_at se fechado, as_of se aberto, terminal_observed_at)`, sempre não anterior à abertura; uma observação posterior `running` não reativa a mesma incarnação sem novo início. Para intervalo fechado, `stage_end_at` continua sendo o horário administrativo de fechamento para `elapsed_seconds` (tempo de parede), mas `recorded_work_seconds` e sobreposição de esperas usam somente `[start, effective_work_end]`: callback às 10:30 e `stage-end` às 10:40 ⇒ 30 minutos de trabalho desde 10:00, não 40; o tempo de parede pode ser 40. Para intervalo aberto sem terminal, fim de trabalho é `as_of`. Sem observação confirmatória mas com sinal insuficiente → `unconfirmed` (trabalho medido até fim do intervalo, rotulado). Sem nenhuma observação correlacionada → `unobserved` (métricas legadas exatas).
- Estado da issue (`activity_state`): espera aberta → `waiting:<reason>`; senão reconciliação pendente → `unknown`/`interrupted`/`needs_reconciliation`; senão `working`/`unconfirmed`/`unobserved`; run finalizado → `completed`/`failed`.
- `incomplete_evidence`: execuções `test_run` sem observação confirmatória terminal, ou terminal com `report` `absent|unknown`.
- `status_summary`: `current_stage`, `activity_state`, `last_confirmed` (`state`, `source`, `execution`, `log_ref`, `evidence`, `at`), `blocker` (espera aberta, reconciliação pendente ou `null`), `next_action` (último `next` pertinente), `verified_at` (maior `last_seen_at`/`at` confirmatório). Para etapa/worker corrente, `last_confirmed`, `verified_at` e `next_action` derivados de observação consideram só a incarnação corrente; callback tardio de A não se apresenta como prova ou próximo passo de B. Se não há intervalo corrente, o histórico ainda pode mostrar a última confirmação com sua execução identificada.
- Semântica de prova: `last_confirmed`, `state` e `--report` são fatos de observação de runtime, não veredito. O veredito de prova é `workflow-evidence verify` (#31). Para `test_run`, o resumo mostra `evidence: evidence:<id>` quando vinculado (via `--evidence`) ou `evidence: "não verificada"`; nem `--report present` nem o mero vínculo `evidence:` autorizam rótulo de verificada/aprovada. `verified_at` significa "estado observado em", não "prova verificada".
Escolha de cortar o trabalho de intervalos abertos e fechados na observação terminal da própria incarnação: evita atividade fantasma e duração inflada por fechamento tardio, mantendo o legado intacto porque a regra só se aplica quando há observação correlacionada.

### D5 — Registro finalizado e separação por issue
`workflow-event` recusa `stage-start`, `dispatch` e `wait-start` quando o registro já tem `run_finished`; `observe`, `stage-end`, `wait-end` e `rework` continuam permitidos (fechamento tardio e reconciliação). Isso protege contra gravar a issue B no registro de A. Separação de métricas já é estrutural (um comentário por issue); o teste T4 a comprova.

### D6 — Deduplicação de observação
Se a última `state_observed` da mesma execução **na mesma incarnação** (ou do mesmo `(stage, worker)` sem execução na mesma incarnação não ambígua) repetir **todos** os fatos (`state`, `source`, `exit_code`, `report`, `log_ref`, `evidence`, `next`), o escritor só atualiza `last_seen_at` dessa observação e imprime `"deduplicated": true`. Nunca deduplicar entre incarnações nem deslocar o `at` terminal usado para cortar o trabalho por atualizar `last_seen_at`. Novas provas ou mudança de resultado geram evento novo, nunca são descartadas por deduplicação. Limita o tamanho do comentário (limite GitHub ~65 536 caracteres) e torna polling repetido inócuo; a regra de preferir callbacks fica na skill.

### D7 — Referências de log
`--log-ref` aceita: (a) URL HTTPS analisada como URL (host exato `github.com`, sem userinfo, porta, query ou fragment, caminho não vazio restrito a `[A-Za-z0-9._/-]`, sem `@`, `//` nem segmento `..`; recusar escapes percentuais para não ocultar credenciais ou consultas); (b) SHA 7–64 hex; (c) referência tipada `^(?!(?:https?|file):)[a-z][a-z0-9-]{1,30}:(?!.*//)[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$` — sem `@`, `//`, espaço, `?`, `=`, `&`, `#`, e sem os esquemas `http`/`https`/`file`, de modo que URLs só entram pelo ramo GitHub. Usar `fullmatch` e limitar o comprimento também no ramo URL. Casos negativos obrigatórios: `https://user:pass@example.com/x`, `http://evil.example/x`, `https://github.com/o/r?token=secret`, `https://github.com/o/r#fragment`, `https://github.com/user:pass@evil.example/x`, `runtime:a b`, `runtime:x?token=1`. A skill documenta que referências não podem conter credenciais. Caminhos locais absolutos não são prova portátil (transporte é escopo de #31).
`--evidence` não é alterado: continua com a allowlist de #31 (R4). Se o Apply mover validadores para `workflow_metrics.py`, o padrão de #31 mantém a mesma semântica e `test_event_accepts_evidence_reference_and_rejects_path` continua passando sem alteração.

### D8 — Composição com #31 (R3)
- #32 é dono de `execution {kind, id}` nos eventos do registro de run e MUST NOT estender ou modificar o manifest de #31 nem seu `correlation {run_id, issue_url, stage, worker_id}`.
- Vínculo registro de run → evidência: `--evidence evidence:<evidence_id>` existente em `observe`/`stage-end`.
- Execução local registrada por `workflow-evidence`: `--execution-kind test_run --execution-id <evidence_id>`; #31 emite o `evidence_id` antes de executar o comando, permitindo observar `running` antes do término. Execução hospedada: `--execution-kind ci_run --execution-id <id do run de CI>` (= `hosted.run_id` de #31).
- Execuções não registradas por `workflow-evidence` (worker, processo, job) usam identificadores do runtime; `test_run` sem `evidence:` vinculada aparece como "não verificada".
- Dependência rígida: #31 mergeada (allowlist `evidence:`, emissão antecipada do `evidence_id`, teste de allowlist) e, transitivamente, #35. Testes em arquivo novo para reduzir conflito.

### D10 — Motivos de espera e estados de bloqueio (R7)
#32 é dono do enum de motivos; #34 é dono da classificação de bloqueios. Mapeamento documentado na skill do orquestrador: `technical` → `BLOCKED` / `environment` (sandbox/serviço) ou `dependency`/`external`; `capacity` → `RESOURCE_QUEUED` / `runtime_capacity`; `business_decision` → `NEEDS_INPUT` / `owner_input`; `replan` aceito → `NEEDS_REPLAN`. `tests` é espera por execução de teste local em andamento (não bloqueio). Nenhum estado novo do orquestrador.

### D11 — Arquivos compartilhados (R6/R9)
Ao editar `workflow-event`/`workflow-report`, manter a linha `sys.dont_write_bytecode = True` de #35 antes do import de `workflow_metrics`. Em `skills/milestone-orchestrator/SKILL.md`, editar somente "Workflow timing instrumentation" (#31 "Durable handoff", #34 "Exceptional states", #35 "Worktree lifecycle"). Após rebase, rodar `scripts/sync-plugin`; nunca mesclar cópias à mão.
Antes do Apply, comparar a versão mergeada/arquivada de `openspec/specs/workflow-metrics/spec.md` com esta proposta: a regra de allowlist e a leitura retrocompatível de #31 não são reafirmadas em requisitos próprios daqui; apenas a nova observação as consome. Se o contrato mergeado diferir e exigir mudança de requisito existente, parar para revisar o contrato e adicionar um delta MODIFIED com o bloco integral do requisito, em vez de duplicá-lo; revalidar estritamente.

### D9 — Documentação e distribuição
Regras de reconciliação/callback/escopo em `skills/milestone-orchestrator/SKILL.md` (seção "Workflow timing instrumentation") e `protocol/AI_WORKFLOW.md` (seção "Workflow timing and Kaizen metrics"); `skills/milestone-progress/SKILL.md` passa a ler `status_summary`; README pt/en em paridade; `scripts/sync-plugin` regenera `plugins/my-ai-skills/` e as cópias em `skills/*/references/AI_WORKFLOW.md`.

## Matriz requisito → código → teste

| Cenário / requisito | Critério ou risco | Código | Camada | Teste |
|---|---|---|---|---|
| Correlação de execução; id inseguro recusado | Correlacionar run/issue/etapa/worker/execução | `workflow-event` (`observe`, `dispatch`) | CLI com `gh` falso | novo `test_observe_records_correlation_and_rejects_unsafe_id` |
| Observação vinculada a `evidence:ev-…` | R3 vínculo run → evidência | `observe --evidence` (allowlist #31) + D4 | CLI + relatório | novo `test_observation_links_evidence_reference` (aceita e mostra em `last_confirmed`) |
| Fonte e horário (callback, futuro/anterior) | Fonte/horário da observação | `workflow-event` validação D3 | CLI | novo `test_observed_at_is_effective_time_and_validated` |
| Sinais insuficientes | Prosa/container insuficientes | `workflow_metrics` D4 | Unidade (fixture) | novo `test_weak_sources_do_not_confirm_activity` |
| T1 despacho assíncrono | AC4 causalidade e métricas | `dispatch` + D4 | Fixture + CLI | novo `test_async_dispatch_duration_until_worker_completion` |
| T2 processo some sem relatório | AC1 reconciliação | D4 corte na observação | Fixture | novo `test_unknown_observation_stops_work_and_requires_reconciliation` |
| Callback 10:30, `stage-end` 10:40 | Fechamento administrativo não infla trabalho de intervalo fechado | D4 fim efetivo e interseção com esperas | Unidade (fixture) | novo `test_delayed_stage_end_uses_terminal_observation_for_closed_work` (30 min trabalho, 40 min parede) |
| Reutilização de etapa/worker por A e B | Callback tardio de A não confirma nem corta B | D2/D4/D6 identidade/incarnação | CLI + fixture | novo `test_reused_pair_stale_callback_isolated_by_execution` (A abre 10:00, fecha 10:40; B abre 10:45; callback de A observado 10:30 chega 10:50; B segue sem observação, resumo e duração de B intactos; término com ID divergente recusado) |
| Processo encerrado antes de anúncio | AC1 | D4 | Fixture | mesmo teste (caso `completed` sem `stage_end`) |
| T3 decisão do usuário / CI / ambiente | AC3 | `REASONS`, D4 | Unidade | novo `test_wait_classification_owner_input_ci_environment` |
| Ausência de JUnit | AC2 | D4 `incomplete_evidence` | Fixture | novo `test_missing_report_is_incomplete_evidence` |
| Relatório presente sem `evidence:` | Prova não aprovada por observação | D4 semântica de prova | Fixture + relatório | `test_report_shows_status_summary` afirma "não verificada" e ausência de rótulo de aprovação |
| T4 duas issues | AC5 | D5 + `workflow-report` | CLI + relatório | novo `test_two_issues_same_run_are_independent_and_finished_record_refuses_stage` |
| T5 callback sem polling redundante | Dedup e uso do callback | D6 | CLI | novo `test_repeated_observation_is_deduplicated` |
| Resumo simples | Resumo exigido | D4 `status_summary` + `workflow-report` Markdown/JSON | Relatório | novo `test_report_shows_status_summary` (inclui caso sem observação) |
| Referências seguras | Segredo/credenciais/http; `--evidence` não ampliado | D7 | CLI | novo `test_log_ref_validation` (negativos `https://user:pass@example.com/x`, `http://evil.example/x`, URL GitHub com query/fragment ou userinfo, espaço, `?token=`; `--evidence runtime:task-7f3a` recusado) + `test_event_accepts_evidence_reference_and_rejects_path` de #31 inalterado |
| Registro antigo | AC6 legibilidade | D1/D4 | Unidade | existentes em `tests/test_workflow_metrics.py` sem alteração em relação ao `main` pós-#31 + novo `test_legacy_record_unchanged_and_unobserved` |
| Reconciliação/continuidade do orquestrador | AC1/AC6 progresso sem comando por etapa | `skills/milestone-orchestrator/SKILL.md`, `protocol/AI_WORKFLOW.md` | Documentação | revisão + `scripts/sync-plugin` sem diff residual |

## Risks / Trade-offs

- [Comentário cresce além do limite do GitHub] → observar só em transições, deduplicação D6; o erro do `gh` já é reportado e não bloqueia o workflow.
- [Escritor único perde atualização concorrente] → regra existente de escritor único mantida; workers devolvem observações ao orquestrador.
- [Horário informado manipulado/errado] → validação D3; `recorded_at` preservado para auditoria.
- [Par `(stage, worker)` reutilizado / callback fora de ordem] → identidade de execução tipada e janela efetiva por incarnação (D4); eventos sem correlação confiável permanecem históricos, nunca promovem B; legados sem observações não mudam.
- [Conflito de arquivos com #31] → dependência rígida de #31 mergeada, seções disjuntas (D11), testes em arquivo novo; rebase no início do Apply.
- [Executor sem callback/consulta suportada] → registrar `unknown` com a fonte disponível; estado nunca é promovido por sinal insuficiente.

## Migration Plan

Sem migração: registros existentes permanecem válidos. Rollback = reverter os scripts; registros com novos eventos continuam legíveis pela versão anterior (eventos ignorados).

## Open Questions

Nenhuma bloqueante. Integração final M2T aguarda o contrato de M2T #12 (follow-up fora do escopo).
