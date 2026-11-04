# Tasks

Arquivos esperados (escopo do Apply):
- `scripts/workflow-event`
- `scripts/workflow_metrics.py`
- `scripts/workflow-report`
- `tests/test_workflow_execution_state.py` (novo)
- `skills/milestone-orchestrator/SKILL.md`
- `skills/milestone-progress/SKILL.md`
- `protocol/AI_WORKFLOW.md`
- `skills/milestone-orchestrator/references/AI_WORKFLOW.md`, `skills/milestone-progress/references/AI_WORKFLOW.md` (gerados por `scripts/sync-plugin`)
- `README.md`, `README.en.md`
- `plugins/my-ai-skills/**` (gerado por `scripts/sync-plugin`)
- `openspec/changes/issue-32-verified-execution-state/**` e, no archive, `openspec/specs/workflow-execution-state/spec.md`

Dependência rígida: #31 mergeada no `main` (e, transitivamente, #35). Não alterar `tests/test_workflow_metrics.py` em relação ao `main` pós-#31 (deve continuar passando, inclusive `test_event_accepts_evidence_reference_and_rejects_path`), `scripts/workflow-status` nem `scripts/sync-plugin`. Não modificar o manifest nem o `correlation` de #31 (`scripts/workflow_evidence.py`/`workflow-evidence`).

## 1. Preparação e coordenação

- [x] 1.1 Rebase sobre o `main` atual e confirmar que #35 e #31 estão mergeadas (`git log --oneline origin/main`); caso contrário, parar com BLOCKED. Confirmar a allowlist de `--evidence` de #31 em `scripts/workflow-event`, a emissão antecipada do `evidence_id` por `workflow-evidence record` e a linha `sys.dont_write_bytecode = True` de #35.
- [x] 1.2 Comparar `openspec/specs/workflow-metrics/spec.md` arquivado por #31 com `specs/workflow-execution-state/spec.md`: a allowlist de `--evidence` e a legibilidade legada permanecem sob #31, sem requisitos duplicados em #32. Se o contrato mergeado exigir mudar algum requisito existente, parar para revisar, criar delta MODIFIED completo em `workflow-metrics` e revalidar com `openspec validate issue-32-verified-execution-state --strict` antes de seguir (D11).

## 2. Registro de observações (`workflow-event`)

- [x] 2.1 Adicionar `tests`/`environment` a `REASONS` e validadores (fonte confirmatória/insuficiente, tipo/identificador de execução, `--log-ref` conforme D7, `--observed-at`, `--next`), mantendo a allowlist de `--evidence` de #31 com a mesma semântica caso seja movida para `workflow_metrics.py`, e a linha de bytecode de #35; verificar com testes de unidade dos validadores em `tests/test_workflow_execution_state.py` e `test_event_accepts_evidence_reference_and_rejects_path` passando.
- [x] 2.2 Implementar `observe` e `dispatch` (D2), `--observed-at` com `at`/`recorded_at` (D3) e opções aditivas em `stage-start`/`stage-end`/`wait-*`; para abertura tipada exigir mesmo `(kind, id)` no `stage-end`, recusar fechamento divergente/reutilização de ID tipado no mesmo par sem alterar registro, preservar términos legados sem ID. Verificar com `test_observe_records_correlation_and_rejects_unsafe_id`, `test_observed_at_is_effective_time_and_validated` (também recusa término anterior ao despacho), `test_reused_pair_stale_callback_isolated_by_execution` (CLI recusa término divergente e ID reutilizado), `test_observation_links_evidence_reference` e `test_log_ref_validation` (negativos `https://user:pass@example.com/x`, `http://evil.example/x`, URL GitHub com query/fragment ou userinfo, espaço, `?token=`; `--evidence runtime:task-7f3a` recusado) usando `gh` falso.
- [x] 2.3 Recusar `stage-start`/`dispatch`/`wait-start` em registro finalizado (D5) e deduplicar somente fatos idênticos **da mesma incarnação** atualizando `last_seen_at` sem deslocar `at` terminal (D6); verificar com `test_repeated_observation_is_deduplicated` (inclui nova referência `evidence:` no mesmo estado, que MUST criar evento), `test_reused_pair_stale_callback_isolated_by_execution` (não deduplica A com B) e a parte de recusa de `test_two_issues_same_run_are_independent_and_finished_record_refuses_stage`.

## 3. Estado verificado e resumo (`workflow_metrics.py`)

- [x] 3.1 Derivar estado verificado por incarnação de etapa/worker e da issue, correlacionar observações pela execução tipada exata e janela efetiva para abertura sem ID (sem associação ambígua), não atribuir callbacks tardios de A à execução B reutilizando etapa/worker, e cortar trabalho de intervalos **abertos e fechados** na primeira observação terminal confirmatória correlacionada; manter fechamento administrativo como tempo de parede e interseção de esperas limitada ao trabalho efetivo (D4). Verificar com `test_async_dispatch_duration_until_worker_completion`, `test_unknown_observation_stops_work_and_requires_reconciliation`, `test_delayed_stage_end_uses_terminal_observation_for_closed_work` (10:00→10:30 trabalho, `stage-end` 10:40, 40 min parede), `test_reused_pair_stale_callback_isolated_by_execution` (B sem observação e sem contaminação em resumo/métricas; ID ausente/divergente não confirma B), `test_weak_sources_do_not_confirm_activity` e `test_wait_classification_owner_input_ci_environment`.
- [x] 3.2 Calcular `incomplete_evidence` e `status_summary` com a semântica de prova de D4 (observação ≠ veredito; `test_run` mostra `evidence:<id>` ou "não verificada"), sem deixar confirmação tardia de A preencher `last_confirmed`/`verified_at`/`next_action` da incarnação atual B; verificar com `test_missing_report_is_incomplete_evidence`, `test_reused_pair_stale_callback_isolated_by_execution` (A 10:00–10:40, B inicia 10:45, callback A observado 10:30 gravado 10:50) e `test_legacy_record_unchanged_and_unobserved`, e com `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_workflow_metrics` passando sem alteração do arquivo em relação ao `main` pós-#31.

## 4. Relatório

- [x] 4.1 Exibir o resumo (etapa atual, estado verificado, última prova confirmada, bloqueio, próximo passo, verificado em) e evidência incompleta no Markdown e `status_summary`/`incomplete_evidence` no JSON de `scripts/workflow-report`, mantendo o CSV idêntico; verificar com `test_report_shows_status_summary` (inclui `test_run` com relatório presente e sem `evidence:` exibido como "não verificada", sem rótulo de aprovação) e o caso de duas issues de `test_two_issues_same_run_are_independent_and_finished_record_refuses_stage`.

## 5. Skills, protocolo, documentação e distribuição

- [x] 5.1 Atualizar `skills/milestone-orchestrator/SKILL.md` ("Workflow timing instrumentation") e `protocol/AI_WORKFLOW.md` com: reconciliar via callback/consulta suportada antes de anunciar atividade/conclusão (inclusive na retomada), registrar `unknown` quando não houver prova, preferir notificações a polling, `dispatch` para workers assíncronos, escritor único recebendo observações dos workers, separação por issue e ampliação de escopo só autorizada, continuidade sem comando do usuário por etapa, vínculo `--evidence evidence:<id>` e `--execution-kind test_run --execution-id <evidence_id>` / `ci_run` = id do run de CI (D8), e o mapeamento de bloqueios de #34 para motivos de espera (D10), editando apenas a seção "Workflow timing instrumentation" da skill (D11); atualizar `skills/milestone-progress/SKILL.md` para usar `status_summary`. Verificar por leitura contra o requisito "Reconciliação e continuidade do orquestrador".
- [x] 5.2 Documentar `dispatch`, `observe`, fontes, novos motivos de espera e o resumo em `README.md` e `README.en.md` com paridade; verificar comparando as seções e executando os exemplos documentados contra o `gh` falso do teste.
- [x] 5.3 Executar `scripts/sync-plugin` e verificar que `plugins/my-ai-skills/` e `skills/*/references/AI_WORKFLOW.md` refletem as fontes (`git status` sem diferenças após segunda execução).

## 6. Verificação integrada

- [x] 6.1 Executar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` e `openspec validate issue-32-verified-execution-state --strict`, ambos com sucesso, e registrar a matriz requisito → código → teste do design com o resultado no PR.

## Workflow follow-up

- Arquivar a change no branch da issue após testes e validação estrita; inspecionar `openspec/specs/workflow-execution-state/spec.md` gerado.
- Follow-up fora do escopo, CONTRACT_BLOCKED em https://github.com/rocker-code/m2t/issues/12: adaptador que consome o registro/consulta por execução do M2T e mapeia para `observe` (`execution-kind test_run`, `--log-ref` com a referência opaca definida pelo contrato congelado), após contract-handoff em final-freeze.
