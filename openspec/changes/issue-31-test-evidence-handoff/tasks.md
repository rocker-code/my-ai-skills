# Tasks — issue-31-test-evidence-handoff

## 1. Biblioteca de evidência (manifesto, fingerprint, armazenamento)

- [ ] 1.1 Criar `scripts/workflow_evidence.py` com manifesto `my-ai-skills.test-evidence/v1` (D2), geração de `evidence_id`, leitura/escrita preservando chaves desconhecidas e armazenamento em `<git-common-dir>/my-ai-skills/evidence/` (D4); verificar com `test_unknown_extensions_preserved` e `test_record_requires_obligation` em `tests/test_workflow_evidence.py`
- [ ] 1.2 Implementar `code_fingerprint` (HEAD + alterações rastreadas/não rastreadas + configs declaradas, D3) e cálculo de caminhos divergentes; verificar com `test_same_head_different_diff_is_stale`, `test_later_commit_is_stale` e `test_ignored_config_change_is_stale` usando repositórios Git temporários
- [ ] 1.3 Implementar mascaramento de argv e registro de ambiente só por nome (D5); verificar com `test_secret_argv_masked` e `test_env_values_not_recorded`

## 2. CLI `workflow-evidence`: registrar e verificar

- [ ] 2.1 Criar `scripts/workflow-evidence` (executável) com `record -- <cmd>` (log capturado, exit code propagado, fingerprint antes/depois, `--report` JUnit com contagens, `--obligation ID[:globs]`, `--required-gate`, `--selection`, `--config`, `--openspec-change`, `--correlation-*`) e `register-hosted`; verificar com `test_failing_command_recorded_and_exit_propagated`, `test_junit_counts_extracted`, `test_missing_report_incomplete`, `test_interrupted_incomplete` e `test_concurrent_change_is_ambiguous`
- [ ] 2.2 Implementar `verify` com os estados e a precedência de D6, invalidação por obrigação de D7, saída `text|json` e exit codes de D1; verificar com `test_missing_log_incomplete`, `test_change_affects_only_one_obligation`, `test_required_gate_always_affected` e `test_hosted_result_not_applicable_for_required_gate`
- [ ] 2.3 Implementar `list` (filtro `--obligation`), `show` e `prune` (simulação por padrão, `--yes` para remover); verificar com `test_list_by_obligation_shows_selection` e `test_prune_dry_run_by_default`

## 3. Transporte entre sessões e runtimes

- [ ] 3.1 Garantir resolução pelo diretório Git comum entre worktrees; verificar com `test_record_verified_from_other_worktree` (registro numa worktree, verificação em outra, sem reexecução)
- [ ] 3.2 Implementar `export`/`import` de pacote `tar.gz` com `SHA256SUMS`, rejeitando caminhos absolutos, `..`, links e checksums divergentes; verificar com `test_bundle_import_in_other_clone`, `test_tampered_bundle_incomplete` e `test_import_rejects_path_traversal`
- [ ] 3.3 Implementar `publish --issue|--pr` (só manifesto, comentário oculto `<!-- my-ai-skills-test-evidence:v1 -->` idempotente, limite de tamanho) e `verify --from-github`; verificar com `test_published_metadata_only_without_logs` usando `gh` falso

## 4. Retrocompatibilidade de métricas

- [ ] 4.1 Em `scripts/workflow-event`, aceitar `evidence:<evidence_id>` além de URL/SHA (D10), sem alterar `workflow_metrics.py`/`workflow-report`; verificar com `test_event_accepts_evidence_reference_and_rejects_path` e `test_legacy_record_report_unchanged` em `tests/test_workflow_metrics.py`, mantendo os testes existentes passando

## 5. Protocolo, skills e distribuição

- [ ] 5.1 Atualizar `protocol/TEST_STRATEGY.md` (coluna `Evidence` na matriz e seção "Evidence handoff": estados, transporte, retenção, conteúdo sensível, precedência de gates) e `protocol/AI_WORKFLOW.md` (passo de handoff de prova); verificar que o texto referencia apenas comandos implementados (`scripts/workflow-evidence --help`)
- [ ] 5.2 Atualizar `skills/apply-issue`, `skills/prepare-pr`, `skills/pr-audit`, `skills/post-pr-audit`, `skills/address-pr-review`, `skills/milestone-orchestrator` e `skills/update-ai-workflow` (SKILL.md) conforme D8, incluindo o fallback quando o helper não está instalado; verificar por revisão de que nenhum gate final existente foi enfraquecido
- [ ] 5.3 Incluir `workflow-evidence` e `workflow_evidence.py` em `scripts/sync-plugin`; documentar instalação/uso em `README.md` e `README.en.md` com paridade (lista de cópia, `chmod`, tabela de arquivos, checks `test -x/-f`); rodar `scripts/sync-plugin` e verificar `test -x plugins/my-ai-skills/scripts/workflow-evidence` e que as referências empacotadas foram regeneradas

## 6. Verificação integrada

- [ ] 6.1 Rodar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` (gate final) e `openspec validate issue-31-test-evidence-handoff --strict`; registrar a própria suíte final com `scripts/workflow-evidence record --obligation full-suite --required-gate -- python3 -m unittest discover -s tests` e verificar `verified` antes do prepare-pr
- [ ] 6.2 Conferir o diff contra a lista "Arquivos esperados" do design (sem alterações em `scripts/workflow_metrics.py`/`scripts/workflow-report`, sem arquivos fora do escopo, sem `__pycache__`)

## Workflow follow-up

- Arquivar a mudança no branch da issue após verificação e validação estrita; inspecionar `openspec/specs/test-evidence` e `openspec/specs/workflow-metrics` sincronizados.
- Follow-up CONTRACT_BLOCKED: adaptador de leitura do registro nativo M2T (preencher `producer`) após `CONTRACT FROZEN` de https://github.com/rocker-code/m2t/issues/12.
- Coordenação: #32 estende `correlation`; #34 usa `extensions.attempts`; #35 reutiliza `code_fingerprint`.
