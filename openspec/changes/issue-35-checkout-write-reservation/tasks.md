# Tasks

Validação focal: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_worktree_reservation -v`. Suíte final: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` e, em seguida, `python3 -m unittest discover -s tests && git status --porcelain` (sem a variável) deve sair vazio. Arquivos esperados: ver design.md › "Arquivos esperados"; qualquer arquivo fora da lista exige justificativa no PR.

## 1. Registry, lock e reserva (T1, T1b, T1c, T6, T7, T9)

- [ ] 1.1 Criar `scripts/worktree_registry.py` com resolução do common dir/primário, carga/validação do esquema D2 (`baseline`, `verified_for` e owner PID opcional), lock `fcntl` com timeout e escrita atômica (D3); provar com `test_corrupt_registry_refuses_mutation` e `test_lock_timeout_leaves_registry_unchanged`.
- [ ] 1.2 Criar `scripts/worktree-reservation` (0755, `sys.dont_write_bytecode = True` antes do import) com `reserve`, `status`, `list`, `--json` estável (campos de sucesso e erro 3/4/6 de D5) e códigos de saída D5; provar com `test_concurrent_reserve_grants_single_owner` (subprocessos reais em repositório Git temporário), reserva idempotente e asserts JSON em T1/T3/T3b.
- [ ] 1.3 Implementar `reserve --planned --repository <checkout-existente>` para caminho ainda inexistente (estado `RESERVED` sem baseline, common dir/lock via âncora, ativação após criação), impedindo duplicar issue em outro caminho; provar com `test_planned_reservation_then_activate_and_single_path_per_issue` (sem `--repository` exit 2; não inspecionar destino ausente).
- [ ] 1.4 Implementar recusa do checkout principal sem `--allow-primary`, identidade (remote/branch/caminho) e `SAFE_ID` igual ao `workflow-event` para `--session`/`--run` (exit 2); provar com `test_identity_mismatch_primary_refusal_and_safe_ids`.

## 2. Estado de código, verificação, checkpoint e drift (T3, T3a, T3b, T3c, T8)

- [ ] 2.1 Implementar API pública D1 (`FINGERPRINT_VERSION`, `SAFE_ID`, `KNOWN_GENERATED_PATTERNS`, `is_known_generated`, `code_state`, `drift_report`, `PathEntry`/`IndexEntry`/`CodeState`, `to_json`) com hash canônico de HEAD, status, working tree e entradas do índice (`git ls-files --stage -z`); suporte a `exclude_paths` e `include_ignored`; provar com `test_code_state_entries_digest_and_options` e `test_index_blob_and_mode_change_with_same_xy_and_worktree_changes_digest` (blob **e** modo, `changed_paths`, configuração ignorada, gerados separados).
- [ ] 2.2 Centralizar toda inspeção Git em `_git()` com `--no-optional-locks` e `GIT_OPTIONAL_LOCKS=0`, sem escrita de índice/refs; provar com `test_git_inspection_uses_no_optional_locks` (argv/env de todas as leituras).
- [ ] 2.3 Implementar `verify` persistindo `verified_for` no sucesso ou drift no fracasso; `checkpoint` exige recibo da sessão/baseline atual, dono e identidade, **não** trata escrita posterior ao verify como drift por si; drift previamente persistido bloqueia. Provar com `test_own_checkpoint_is_not_drift`, `test_detected_drift_cannot_be_checkpointed` e `test_external_commit_blocks_until_accept_external` (commits/caminhos/JSON).
- [ ] 2.4 Implementar `release` sem trocar baseline: recusar diferença atual e exigir checkpoint anterior, e `reserve` de entrada sem dono com comparação do baseline; provar `test_release_requires_checkpoint_after_owner_write` (fixtures separadas, sem tentar checkpoint após drift detectado) e `test_reserve_after_release_detects_external_change` (release → commit/edição externa → reserve exit 4 → aceite explícito → reserve, histórico e `changed_paths`).
- [ ] 2.5 Implementar `reconcile --accept-external --session --reason` para dono e aceite explícito em `reserve --accept-external --reason` para entrada sem dono, registrando relatório/motivo no histórico e novo baseline; provar que nenhum `checkpoint` sozinho limpa drift, e que identidade divergente não é aceita como drift.

## 3. Transferência e retomada (T2, T5)

- [ ] 3.1 Implementar `handoff` atômico (dono = origem, baseline ainda igual ao estado real, sem drift) e `mark-removed --repository <checkout-existente>` somente após ausência verificada em `git worktree list --porcelain`, sem acessar Git no caminho removido nem apagar arquivos; provar com `test_handoff_planning_to_apply_keeps_checkout_and_revokes_previous` e caso de remoção negada antes do cleanup.
- [ ] 3.2 Implementar `reconcile` sem flags (reconstrução sem dono a partir do Git real) e `--takeover` com `--expected-owner`, `--stopped-evidence` e `--owner-pid` explicitamente fornecido (sem inferir PID do CLI), recusando processo vivo no mesmo host; provar com `test_reconcile_rebuilds_without_owner_and_preserves_diff`, `test_takeover_requires_expected_owner_and_evidence_not_age` e `test_takeover_refused_when_owner_pid_alive` (subprocesso worker vivo).

## 4. Gerados conhecidos e bytecode (T4)

- [ ] 4.1 Implementar classificação gerado/desconhecido em `status` e `clean-generated` (`--ignored=matching`, ancestrais via `check-ignore`; listagem padrão, `--apply` só para dono, sem seguir symlinks, só `*.py[co]` elegíveis e `__pycache__` vazios); provar com `test_clean_generated_removes_only_bytecode` (`.venv/lib/__pycache__/m.pyc` preservado), `test_generated_files_do_not_cause_drift` e `test_clean_requires_owner`.
- [ ] 4.2 Adicionar `sys.dont_write_bytecode = True` antes do import em `scripts/workflow-event` e `scripts/workflow-report`, criar `.gitignore` com `__pycache__/` e `*.py[co]`; provar com `test_helpers_do_not_write_bytecode` (descobrir helpers Python da lista fixa de `scripts/sync-plugin`, copiar scripts para temp e rodar `--help` sem variável de bytecode, cobrindo futuros helpers #31/#33/#34) e `tests/test_workflow_metrics.py` inalterado passando.

## 5. Protocolo, skills e distribuição

- [ ] 5.1 Adicionar a `protocol/WORKTREES.md` a subseção "Reservation helper": API pública D1/versionamento, `--planned --repository`/ativação, JSON/IDs D5, sequência verify→escrita própria→checkpoint→release, comparação em reserve sem dono, códigos de saída, falha fechada sem lock e limites com agentes não cooperantes (detecção, não prevenção, autoria impossível na janela verify→checkpoint); verificar por revisão do diff contra cenários da spec.
- [ ] 5.2 Acrescentar a frase de integração D8 ao parágrafo "Worktree lifecycle" de `skills/{milestone-orchestrator,implement-issue,apply-issue,prepare-pr,github-resolution,address-pr-review}/SKILL.md` (orquestrador usa `--planned --repository` e só chama `handoff` após retorno do worker); em `milestone-progress` citar `status`/`list` somente leitura; verificar por revisão dessas seções e `grep -l worktree-reservation skills/*/SKILL.md`.
- [ ] 5.3 Atualizar `skills/update-main/SKILL.md` passo 2 (gerados conhecidos reportados, não bloqueiam; demais não rastreados bloqueiam; sem `clean`) e `skills/update-ai-workflow/SKILL.md` (companheiro `worktree_registry.py`); verificar por revisão do diff.
- [ ] 5.4 Incluir `worktree-reservation` (0755) e `worktree_registry.py` (0644) em `scripts/sync-plugin`, e documentar instalação/tabela/verificação nas seções 5 e 7 de `README.md` e `README.en.md` em paridade; executar `scripts/sync-plugin` e verificar que `plugins/my-ai-skills/scripts/` e `skills/*/references/WORKTREES.md` refletem as fontes.

## 6. Verificação integrada

- [ ] 6.1 Rodar a suíte final (com e sem `PYTHONDONTWRITEBYTECODE`) e confirmar `git status --porcelain` limpo além dos arquivos esperados; rodar `openspec validate issue-35-checkout-write-reservation --strict`; registrar PASS/FAIL e matriz T1–T9 (incluindo T1c/T3a–c, release→external→reserve, index blob/modo, API/JSON/IDs/no-optional-locks) no handoff para `prepare-pr`.

## Workflow follow-up

- Arquivar a change na branch da issue após verificação e validação strict, sincronizando `openspec/specs/checkout-write-reservation/spec.md` no mesmo PR.
- Coordenar com #31/#32 a reutilização do fingerprint/relatório de drift de `worktree_registry.py` em vez de nova definição.
