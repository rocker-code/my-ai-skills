# Tasks

Validação focal: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_worktree_reservation -v`. Suíte final: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` e, em seguida, `python3 -m unittest discover -s tests && git status --porcelain` (sem a variável) deve sair vazio. Arquivos esperados: ver design.md › "Arquivos esperados"; qualquer arquivo fora da lista exige justificativa no PR.

## 1. Registry, lock e reserva (T1, T7)

- [ ] 1.1 Criar `scripts/worktree_registry.py` com resolução do common dir/primário, carga/validação do esquema D2, lock `fcntl` com timeout e escrita atômica (D3); verificar com `test_corrupt_registry_refuses_mutation` e `test_lock_timeout_leaves_registry_unchanged`.
- [ ] 1.2 Criar `scripts/worktree-reservation` (0755, `sys.dont_write_bytecode = True` antes do import) com `reserve`, `status`, `list`, `--json` e códigos de saída D5; verificar com `test_concurrent_reserve_grants_single_owner` (subprocessos reais em repositório Git temporário com worktree auxiliar) e reserva idempotente do mesmo dono.
- [ ] 1.3 Implementar recusa do checkout principal sem `--allow-primary` e verificação de identidade (remote/branch/caminho); verificar com `test_identity_mismatch_and_primary_refusal`.

## 2. Verificação, checkpoint e drift (T3)

- [ ] 2.1 Implementar fingerprint D4 (excluindo gerados conhecidos) e `verify`/`checkpoint` com persistência de `drift` e relatório de commits/caminhos; verificar com `test_own_checkpoint_is_not_drift` e `test_external_commit_blocks_until_accept_external`.
- [ ] 2.2 Implementar `reconcile --accept-external --session --reason` registrando o relatório no `history`; verificar no mesmo teste T3 que a verificação volta a passar só após o aceite.

## 3. Transferência e retomada (T2, T5)

- [ ] 3.1 Implementar `handoff` atômico (dono = origem, sem drift) e `release`/`mark-removed` com lifecycle D5; verificar com `test_handoff_planning_to_apply_keeps_checkout_and_revokes_previous`.
- [ ] 3.2 Implementar `reconcile` sem flags (reconstrução sem dono a partir do Git real) e `--takeover` com `--expected-owner`, `--stopped-evidence` e recusa por processo vivo no mesmo host; verificar com `test_reconcile_rebuilds_without_owner_and_preserves_diff`, `test_takeover_requires_expected_owner_and_evidence_not_age` e `test_takeover_refused_when_prior_pid_alive`.

## 4. Gerados conhecidos e bytecode (T4)

- [ ] 4.1 Implementar classificação gerado/desconhecido em `status` e `clean-generated` (listagem padrão, `--apply` só para o dono, sem seguir symlinks, só `*.py[co]` e `__pycache__` vazios); verificar com `test_clean_generated_removes_only_bytecode`, `test_generated_files_do_not_cause_drift` e `test_clean_requires_owner`.
- [ ] 4.2 Adicionar `sys.dont_write_bytecode = True` antes do import em `scripts/workflow-event` e `scripts/workflow-report`, e criar `.gitignore` com `__pycache__/` e `*.py[co]`; verificar com `test_helpers_do_not_write_bytecode` e com `tests/test_workflow_metrics.py` inalterado passando.

## 5. Protocolo, skills e distribuição

- [ ] 5.1 Adicionar a `protocol/WORKTREES.md` a subseção "Reservation helper": comandos, códigos de saída, quando chamar cada um, falha fechada sem lock, limites com agentes não cooperantes (detecção, não prevenção; janelas verify→mutação e verify→checkpoint); verificar por revisão do diff contra spec "Convenção de checkout principal e limites externos".
- [ ] 5.2 Acrescentar a frase de integração D8 ao parágrafo "Worktree lifecycle" de `skills/{milestone-orchestrator,implement-issue,apply-issue,prepare-pr,github-resolution,address-pr-review}/SKILL.md` (orquestrador chama `handoff` ao despachar Apply/correção); verificar por `grep -l worktree-reservation skills/*/SKILL.md`.
- [ ] 5.3 Atualizar `skills/update-main/SKILL.md` passo 2 (gerados conhecidos reportados, não bloqueiam; demais não rastreados bloqueiam; sem `clean`) e `skills/update-ai-workflow/SKILL.md` (companheiro `worktree_registry.py`); verificar por revisão do diff.
- [ ] 5.4 Incluir `worktree-reservation` (0755) e `worktree_registry.py` (0644) em `scripts/sync-plugin`, e documentar instalação/tabela/verificação nas seções 5 e 7 de `README.md` e `README.en.md` em paridade; executar `scripts/sync-plugin` e verificar que `plugins/my-ai-skills/scripts/` e `skills/*/references/WORKTREES.md` refletem as fontes.

## 6. Verificação integrada

- [ ] 6.1 Rodar a suíte final (com e sem `PYTHONDONTWRITEBYTECODE`) e confirmar `git status --porcelain` limpo além dos arquivos esperados; rodar `openspec validate issue-35-checkout-write-reservation --strict`; registrar PASS/FAIL e a matriz T1–T7 preenchida no handoff para `prepare-pr`.

## Workflow follow-up

- Arquivar a change na branch da issue após verificação e validação strict, sincronizando `openspec/specs/checkout-write-reservation/spec.md` no mesmo PR.
- Coordenar com #31/#32 a reutilização do fingerprint/relatório de drift de `worktree_registry.py` em vez de nova definição.
