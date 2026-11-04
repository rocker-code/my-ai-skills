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

Não alterar `tests/test_workflow_metrics.py` (deve continuar passando como prova de compatibilidade), `scripts/workflow-status` nem `scripts/sync-plugin`.

## 1. Preparação e coordenação

- [ ] 1.1 Rebase sobre o `main` atual e verificar se #31 (e #35) foram mergeadas; listar helpers/campos que #31 adicionou em `scripts/workflow-event`/`scripts/workflow_metrics.py` e registrar no PR quais serão reutilizados (design D8). Verificar com `git log --oneline origin/main` e leitura dos scripts.

## 2. Registro de observações (`workflow-event`)

- [ ] 2.1 Adicionar `tests`/`environment` a `REASONS`, validadores reutilizáveis em `workflow_metrics.py` (fonte confirmatória/insuficiente, tipo/identificador de execução, `--log-ref`, `--observed-at`, `--next`) e verificar com testes de unidade dos validadores em `tests/test_workflow_execution_state.py`.
- [ ] 2.2 Implementar `observe` e `dispatch` (D2), `--observed-at` com `at`/`recorded_at` (D3) e opções aditivas em `stage-start`/`stage-end`/`wait-*`; verificar com `test_observe_records_correlation_and_rejects_unsafe_id`, `test_observed_at_is_effective_time_and_validated` e `test_log_ref_validation` usando `gh` falso.
- [ ] 2.3 Recusar `stage-start`/`dispatch`/`wait-start` em registro finalizado (D5) e deduplicar observação repetida atualizando `last_seen_at` (D6); verificar com `test_repeated_observation_is_deduplicated` e a parte de recusa de `test_two_issues_same_run_are_independent_and_finished_record_refuses_stage`.

## 3. Estado verificado e resumo (`workflow_metrics.py`)

- [ ] 3.1 Derivar estado verificado por etapa/worker e da issue, cortando trabalho na observação confirmatória terminal/desconhecida e tratando sinais insuficientes como não confirmados (D4); verificar com `test_async_dispatch_duration_until_worker_completion`, `test_unknown_observation_stops_work_and_requires_reconciliation`, `test_weak_sources_do_not_confirm_activity` e `test_wait_classification_owner_input_ci_environment`.
- [ ] 3.2 Calcular `incomplete_evidence` e `status_summary` (D4); verificar com `test_missing_report_is_incomplete_evidence` e `test_legacy_record_unchanged_and_unobserved`, e com `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_workflow_metrics` passando sem alteração do arquivo.

## 4. Relatório

- [ ] 4.1 Exibir o resumo (etapa atual, estado verificado, última prova confirmada, bloqueio, próximo passo, verificado em) e evidência incompleta no Markdown e `status_summary`/`incomplete_evidence` no JSON de `scripts/workflow-report`, mantendo o CSV idêntico; verificar com `test_report_shows_status_summary` e o caso de duas issues de `test_two_issues_same_run_are_independent_and_finished_record_refuses_stage`.

## 5. Skills, protocolo, documentação e distribuição

- [ ] 5.1 Atualizar `skills/milestone-orchestrator/SKILL.md` ("Workflow timing instrumentation") e `protocol/AI_WORKFLOW.md` com: reconciliar via callback/consulta suportada antes de anunciar atividade/conclusão (inclusive na retomada), registrar `unknown` quando não houver prova, preferir notificações a polling, `dispatch` para workers assíncronos, escritor único recebendo observações dos workers, separação por issue e ampliação de escopo só autorizada, continuidade sem comando do usuário por etapa; atualizar `skills/milestone-progress/SKILL.md` para usar `status_summary`. Verificar por leitura contra o requisito "Reconciliação e continuidade do orquestrador".
- [ ] 5.2 Documentar `dispatch`, `observe`, fontes, novos motivos de espera e o resumo em `README.md` e `README.en.md` com paridade; verificar comparando as seções e executando os exemplos documentados contra o `gh` falso do teste.
- [ ] 5.3 Executar `scripts/sync-plugin` e verificar que `plugins/my-ai-skills/` e `skills/*/references/AI_WORKFLOW.md` refletem as fontes (`git status` sem diferenças após segunda execução).

## 6. Verificação integrada

- [ ] 6.1 Executar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` e `openspec validate issue-32-verified-execution-state --strict`, ambos com sucesso, e registrar a matriz requisito → código → teste do design com o resultado no PR.

## Workflow follow-up

- Arquivar a change no branch da issue após testes e validação estrita; inspecionar `openspec/specs/workflow-execution-state/spec.md` gerado.
- Follow-up fora do escopo, CONTRACT_BLOCKED em https://github.com/rocker-code/m2t/issues/12: adaptador que consome o registro/consulta por execução do M2T e mapeia para `observe` (`execution-kind test_run`, `log-ref m2t:<id>`), após contract-handoff em final-freeze.
