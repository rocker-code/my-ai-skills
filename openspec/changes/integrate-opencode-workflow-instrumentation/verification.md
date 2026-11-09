# Verificação da implementação

## Escopo e limites

Os testes automatizados usam identidades sintéticas, checkout/estado temporários e GitHub
fake. O transporte SSE usa `@opencode/client@2.2.5` realmente instalado, contra
servidor HTTP autenticado apenas em loopback. As consultas periódicas Python usam
um adaptador de comando simulado; não executam o CLI OpenCode real. O consumidor
do painel no E2E é `Background` real, sem curses/TTY; layouts/curses têm regressões
próprias. Esses testes isoladamente não validam um servidor OpenCode real nem cumprimento das skills
por um modelo; walkthroughs são testes programáticos do contrato.

**Smoke real OpenCode 2.2.5: executado com autorização explícita, em 2026-11-09.**
Sessões de teste e publicação na issue #440 foram autorizadas pelo usuário;
config e SQLite ficaram isolados em `/tmp/opencode/smoke-real-wrRs1g/`.
Não é prova de execução das skills por um modelo nem habilitação operacional geral.
Detalhes e limitações estão em "Smoke real" abaixo.

O lock protege somente escritores cooperativos no mesmo domínio de estado.
Permanece uma janela entre última leitura e escrita GitHub, sem CAS distribuído.
O teste `test_known_noncooperative_window_after_last_read_has_no_cas_guarantee`
expõe essa limitação, não prova exclusão entre máquinas.

## Rastreabilidade requisito → cenário → teste

Os nomes abaixo referem-se a métodos `test_*` nos arquivos `tests/` indicados.
Cada linha cobre os cenários do requisito na ordem da spec; nenhum cenário é
substituído por uma alegação de smoke real.

### opencode-workflow-instrumentation

| Requisito / cenário | Evidência automatizada |
|---|---|
| Observação headless / Painel fechado durante execução | `test_milestone_monitor_e2e.py`: `test_official_stream_wait_retry_gap_restart_and_closed_panels`; `test_milestone_monitor_observer.py`: `test_foreground_without_dashboard_persists_only_metadata_and_cancels` |
| Observação headless / Configuração sem autorização de runtime | `test_milestone_monitor_observer.py`: `test_no_optin_or_targets_never_starts_sources` |
| Contrato oficial fixado / Servidor atualizado sem adaptação | `test_milestone_monitor_runtime.py`: `test_process_and_version_changes_do_not_transfer_confirmation`; Node `connection.test.js`: descoberta/revalidação e erros/versões divergentes |
| Correlação / Sessão reutilizada e evento atrasado | `test_milestone_monitor_runtime.py`: `test_fact_revalidates_revision_context_checkout_and_temporal_boundary`; `test_milestone_monitor_state.py`: `test_callback_a_never_confirms_b_and_metrics_unchanged` |
| Correlação / Sessão muda de checkout | `test_milestone_monitor_runtime.py`: `test_location_is_revalidated_every_cycle_even_same_project_and_running` |
| Eventos não encerram etapas / Turno termina e etapa continua | E2E; `test_milestone_monitor_reconciliation.py`: `test_missing_resolution_and_turn_success_never_create_duration_or_stage_end` |
| Esperas sem silêncio / Dois pedidos na mesma sessão | E2E; `test_milestone_monitor_requests.py`: `test_multiple_permissions_forms_and_individual_resolution` |
| Esperas sem silêncio / Sessão inativa sem pedido | `test_milestone_monitor_requests.py`: `test_inactive_without_request_never_invents_wait` |
| Recuperação / Resposta ocorreu durante desconexão | E2E; `test_milestone_monitor_requests.py`: `test_query_recovers_current_state_not_missing_timestamps`, `test_loss_reconnection_restart_preserve_incomplete_intervals` |
| Coleta única / Segundo observador e dois painéis | `test_milestone_monitor_coordination.py`: `test_two_dashboards_only_one_collects_and_follower_refresh_coalesces`, `test_observer_handoff_rejects_old_response_and_second_observer` |
| Minimização / Evento contém conteúdo sensível | E2E; `test_milestone_monitor_observation_store.py`: `test_second_projection_bounds_and_no_content_at_rest`; Node `bridge.test.js` e `transport.test.js` |
| Operação limitada / Consumidor lento | `test_milestone_monitor_observation_store.py`: `test_saturation_marks_gap_before_dropping_known_facts`; `test_milestone_monitor_observer.py`: `test_python_supervisor_limits_read_and_stops_only_its_child`, `test_bad_envelope_drops_continuity_not_periodic_collection` |

### milestone-monitor-state

| Requisito / cenário | Evidência automatizada |
|---|---|
| Frescor / Confirmação antiga sem nova consulta | `test_milestone_monitor_observer_projection.py`: `test_old_epoch_ttl_and_heartbeat_without_new_sample_do_not_confirm` |
| Frescor / Reabrir painel com observador saudável | E2E; `test_milestone_monitor_observer_projection.py`: `test_sample_before_ui_open_requires_current_live_healthy_owner` |
| Frescor / Heartbeat sem observação nova | `test_milestone_monitor_observer_projection.py`: `test_old_epoch_ttl_and_heartbeat_without_new_sample_do_not_confirm`; `test_milestone_monitor_ownership.py`: `test_owner_metadata_heartbeat_never_renews_source` |
| Persistência / Dois painéis e armazenamento ocupado | `test_milestone_monitor_store.py`: `test_two_writers_killed_transaction_and_busy_reader`, `test_disk_full_error_does_not_replace_snapshot` |
| Persistência / Observador assume coleta antes feita pelo painel | `test_milestone_monitor_coordination.py`: `test_observer_handoff_rejects_old_response_and_second_observer`; E2E para fechar consumidor sem parar observador |
| Sinal local / Permissão pendente ainda não registrada pelo coordenador | E2E; `test_milestone_monitor_observer_projection.py`: `test_observed_pending_blocks_once_without_canonical_duration` |
| Sinal local / Runtime confirma trabalho enquanto publicação está pendente | `test_milestone_monitor_observer_projection.py`: `test_pending_publication_is_not_a_github_stage` |
| Sinal local / Espera canônica tem precedência | `test_milestone_monitor_observer_projection.py`: `test_canonical_wait_and_github_closure_have_precedence`; `test_milestone_monitor_state.py`: `test_waits_win_over_parallel_workers_and_closed_github_wins` |

### workflow-execution-state

| Requisito / cenário | Evidência automatizada |
|---|---|
| Transições / Passagem de planejamento para implementação | `test_workflow_instrumentation_contract.py`: `test_planning_to_apply_unknown_session_rework_and_another_issue_are_distinct`, `test_thirteen_frontiers_single_writer_stable_identity_and_optin` |
| Transições / Uso isolado de uma skill | `test_workflow_instrumentation_contract.py`: `test_executors_preserve_conditional_handoff_without_becoming_writers`; `test_milestone_monitor_workflow_cli.py`: `test_no_authority_or_invalid_identity_never_accepts_or_calls_github` |
| Vínculo / Despacho disponibiliza sessão depois da abertura | `test_milestone_monitor_auto_bind.py`: `test_missing_session_never_uses_coordinator_then_late_id_binds_without_opening_again` |
| Vínculo / Execução anterior deixou vínculo | `test_milestone_monitor_auto_bind.py`: `test_execution_switch_requires_exact_previous_unbind` |
| Publicador / GitHub indisponível no término da etapa | `test_milestone_monitor_publisher.py`: `test_lost_response_after_save_retries_without_duplicate_events_or_evidence`; `test_milestone_monitor_workflow_cli.py`: `test_denied_github_sanitizes_error_and_preserves_accepted_operation`; journal crash/restart |
| Publicador / Coordenador encerrado com sinais novos | E2E: observador recebe eventos sem publicar; só `reconcile` do coordenador escreve |
| Idempotência / Publicação concluída com resposta perdida | E2E; `test_milestone_monitor_reconciliation.py`: `test_lost_response_recovers_whole_atomic_pair`; `test_milestone_monitor_journal.py`: `test_same_operation_replays_and_other_payload_cannot_replace` |
| Idempotência / Dois coordenadores cooperativos | `test_milestone_monitor_publisher.py`: `test_manual_and_structured_paths_share_lock_and_baseline`; `test_duplicate_comment_or_unexpected_drift_causes_conflict_without_write`, `test_drift_between_first_and_final_read_is_detected` |
| Resultado / Agente termina resposta durante Apply | E2E; `test_milestone_monitor_reconciliation.py`: `test_missing_resolution_and_turn_success_never_create_duration_or_stage_end` |
| Resultado / Worker entrega resultado e evidência correlacionados | `test_workflow_instrumentation_contract.py`: `test_one_issue_from_dispatch_to_correlated_result_has_one_writer`; `test_milestone_monitor_reconciliation.py`: `test_terminal_worker_or_test_observation_requires_own_proof_but_manual_v1_is_unchanged` |
| Esperas / Pedidos de autorização sobrepostos | E2E; `test_milestone_monitor_reconciliation.py`: `test_overlapping_requests_union_native_precision_and_repeat_without_duplicate_time`, `test_subtracts_canonical_wait_and_inserts_backdated_gaps_without_repairing_fifo` |
| Esperas / Resolução perdida | E2E; `test_milestone_monitor_reconciliation.py`: `test_open_explicit_or_overlapping_pending_request_is_not_closed_by_first_reply`, `test_missing_resolution_and_turn_success_never_create_duration_or_stage_end` |
| Compatibilidade / Registro legado sem runtime | `test_opencode_observer_optional.py`: `test_legacy_commands_without_node_on_path`; `test_milestone_monitor_state.py`: `test_legacy_wait_and_work_times_preserved`; suíte `test_workflow*.py` |
| Compatibilidade / Dashboard autorizado apenas para leitura | E2E e testes observer/coordination: coleta não escreve; CLI exige declaração explícita de coordenador |

## Execuções

Revisão local não commitada sobre `dc9c3e405dc538d833b443a94d189c3ed837b625`.
Fingerprint SHA-256 da árvore verificada:
`d086762d4ea2e1c48229ed867a373e58bb764a68160e67d816b573fdeaeb728d`.
Inclui 375 arquivos sob `scripts/`, `tests/`, `integrations/`, `skills/`,
`protocol/`, `docs/`, `examples/milestone-monitor/`, `plugins/my-ai-skills/` e os
dois READMEs, excluindo `node_modules`/`__pycache__`. Algoritmo: ordenar os paths;
concatenar para cada um `path relativo + NUL + SHA256(conteúdo) + LF`; calcular
SHA256 dessa sequência UTF-8. Inclui as alterações visuais preexistentes preservadas;
não é um SHA de commit nem inclui este registro/checklists OpenSpec.

- Monitor: `PYTHONDONTWRITEBYTECODE=1 OPENCODE_OBSERVER_BRIDGE=<cópia-instalada>/main.js python3 -m unittest discover -s tests -p 'test_milestone_monitor*py'`: **130 PASS**, sem skips, inclui E2E.
- Instalação final isolada: `npm ci --ignore-scripts --no-audit --no-fund` em `/tmp/opencode/instrumentation-final-29xi5xkv/integrations/opencode-observer`: exit 0, cinco dependências instaladas pelo lockfile.
- Suíte Node na cópia final instalada: `npm test`: **13 PASS**, sem skips, exit 0.
- Python completa: `PYTHONDONTWRITEBYTECODE=1 OPENCODE_CONTRACT_SOURCE=/tmp/opencode/instrumentation-contract OPENCODE_OBSERVER_BRIDGE=/tmp/opencode/instrumentation-final-29xi5xkv/integrations/opencode-observer/main.js python3 -m unittest discover -s tests`: **356 PASS**, sem skips, exit 0 (inclui proveniência SHA/fontes fixadas, E2E, privacidade, compatibilidade sem Node, layouts e distribuição).
- Repetição final após última regeneração, com `OPENCODE_OBSERVER_BRIDGE=/tmp/opencode/instrumentation-distributed-6_crvyy_/integrations/opencode-observer/main.js` e as demais opções acima: **356 PASS**, sem skips, exit 0. Portanto o E2E também consumiu a ponte extraída da distribuição instalada.
- Distribuição: duas execuções de `bash scripts/sync-plugin`, com comparação SHA-256 por caminho dos **156 arquivos** gerados: idênticos; árvore da demo original idêntica antes/depois. A cópia visual gerada anterior foi comparada à fonte: a fonte preserva todo o acabamento existente e acrescenta somente os detalhes/saúde/expiração da instrumentação.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_instrumentation_distribution.py -v`: **3 PASS**. Confere módulos/referências/guias/fixture/demo, execução dos comandos distribuídos sem Node e sincronização dupla em cópia isolada com armadilha `node_modules` que não é distribuída.
- Ponte extraída do artefato distribuído para `/tmp/opencode/instrumentation-distributed-6_crvyy_`: `npm ci --ignore-scripts --no-audit --no-fund` exit 0; `npm test`: **13 PASS**, sem skips. Nenhuma dependência instalada no checkout/distribuição.
- `openspec validate integrate-opencode-workflow-instrumentation --strict --json --no-interactive`: válido, zero issues. `git diff --check`: exit 0.
- Conferência dos headings `Scenario` das três specs contra esta matriz: **34/34** possuem rastreabilidade explícita. Os testes de conteúdo/walkthrough não são avaliação comportamental de LLM; o smoke real separado está registrado abaixo.

## Smoke real OpenCode 2.2.5 (2026-11-09)

- Escopo autorizado: `rocker-code/rancho-das-figueiras-magento2#440`, run
  `wf-smoke-20261109T033414Z`, comentário
  `https://github.com/rocker-code/rancho-das-figueiras-magento2/issues/440#issuecomment-6731663170`.
  Config limitada ao milestone 13, `runtime.enabled: true`, estado isolado em
  `/tmp/opencode/smoke-real-wrRs1g/state`. Serviço e cliente oficial 2.2.5,
  Node 24; autenticação e `session.get` validados sem expor credenciais.
- `smoke-run` e dois despachos publicados; primeiro vínculo tardio e segundo
  vínculo de sessão isolada confirmados. `smoke-run-end` publicado como
  `completed` às 04:29:38Z, apenas para o run de instrumentação: as etapas
  `explore`/`tests` sintéticas não foram encerradas como entrega da issue.
- Observador `live`, heartbeat e runtime saudáveis após saída da TUI; parada
  voluntária e retomada geraram novo epoch, lacuna explícita e cobertura
  novamente `complete: true`. SSE real capturou início/sucesso e início/interrupção
  da sessão vinculada, sem transformar término de turno em `stage-end`.
  Após `run-end`, sem incarnações abertas, o observador ainda em foreground
  mostrou `degraded: sem vínculos runtime confirmados` (esperado), sem erro na
  coleta runtime; encerrar esse processo é uma ação separada do usuário.
- Formulário: `form.created` e `form.replied`. Permissão: sessão isolada com
  regra `ask` somente para `smoke_observer_noop`; `permission.asked` e
  `permission.replied` (`rejected`) observados para o mesmo ID. Estado local:
  `pending: false`, `complete: true`, início/fim cobertos, `gap: false`.
  `workflow reconcile` publicou dois pares de esperas `owner_input` de intervalos
  cobertos, sem inventar tempo para lacunas; issue real permaneceu aberta.
- Auditoria read-only dos 15 fatos `runtime-event:*` no SQLite: somente
  `binding_key`, `binding_revision`, `collector_epoch`, `consumed`, `context`,
  `continuity`, `created`, `event_id`, `projected`, `received_at`, `request_id`,
  `resolution`, `sequence`, `session_id`, `type`, `version`; nenhum campo de
  prompt, formulário, resposta humana, corpo, argumentos, saída ou credencial.
  Maior payload observado: 791 bytes. Não foi lido conteúdo da sessão.
- Incompatibilidades reais encontradas e corrigidas: `gh` 2.46 sem `api --slurp`;
  marcador `server.connected` sem `created`; eventos `session.execution.*` sem
  `location` (a ponte revalida `session.get` antes da projeção). O primeiro
  observador entrou em backoff antes das correções; cobertura histórica não foi
  reconstruída. A revalidação por consulta é posterior ao evento e não é uma
  prova atômica da localização no instante de emissão; mudanças de checkout
  continuam sujeitas à reconciliação conservadora.
- Regressão após correções: 357 testes Python executados, **355 PASS / 2 SKIP**
  (opcionais sem variáveis de proveniência/ponte), 15 testes Node PASS,
  `git diff --check` sem erros. Repetição com
  `OPENCODE_CONTRACT_SOURCE=/tmp/opencode/instrumentation-contract` e
  `OPENCODE_OBSERVER_BRIDGE=<fonte instalada>/main.js`: **357 PASS, 0 SKIP**;
  testes de distribuição: **3 PASS**. Os números anteriores acima registram a revisão
  anterior, não um fingerprint da árvore atual. O CLI `workflow-report` no
  `gh` 2.46 ainda não funciona para a issue real porque
  `gh pr list --json closingIssuesReferences` não é suportado nessa versão;
  o comentário v1 e o estado foram conferidos diretamente pela API GitHub.
