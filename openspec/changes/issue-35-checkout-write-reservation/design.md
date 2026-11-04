# Design

## Context

Ver proposal.md (Why). Estado em `main@5825a9c`:

- `protocol/WORKTREES.md` define registry, lock, atomicidade, lifecycle `RESERVED → ACTIVE → WAITING / HANDOFF → RETAINED / CLEANUP_ELIGIBLE → REMOVED` e a proibição de tomar posse por idade; nenhum script implementa isso.
- Padrão existente de helper: executável sem extensão + módulo Python irmão (`scripts/workflow-event` importa `scripts/workflow_metrics.py` via `sys.path.insert`). Essa importação é a origem de `scripts/__pycache__/workflow_metrics.cpython-314.pyc` (reproduzido). Testes usam `unittest` com `sys.path` apontando para `scripts/`.
- `scripts/sync-plugin` copia uma lista fixa de helpers para `plugins/my-ai-skills/scripts/` e embute `protocol/WORKTREES.md` em `skills/{milestone-orchestrator,milestone-progress,implement-issue,apply-issue,prepare-pr,github-resolution,address-pr-review}/references/`.
- `skills/update-main/SKILL.md` passo 2 para em qualquer não rastreado.
- Não há `.gitignore` nem CI em `.github/`; o gate local é `python3 -m unittest discover -s tests`.

## Goals / Non-Goals

**Goals:**
- Operacionalizar o contrato já escrito em WORKTREES, sem protocolo concorrente.
- Prova executável dos cenários T1–T5 em repositórios Git temporários.
- Integração das skills por referência a comandos concretos, mantendo o texto curto.

**Non-Goals:**
- Criar, mover ou remover worktrees (continua com `git worktree add/remove` pelo coordenador; housekeeping inalterado).
- Registro de evidência de testes (#31), estado de execução/progresso (#32), preflight de configuração (#33), log de hipóteses (#34).
- Impedir agentes que não usam o protocolo; proteção de ambiente/sandbox (Docker, DB) além do campo `sandbox` já previsto.
- Lock em Windows/sem `fcntl` (falha fechada, documentada).

## Decisions

### D1. Módulo + CLI fino, seguindo o padrão de `workflow-event`
`scripts/worktree_registry.py` (lógica, importável por testes e futuramente por #31/#32) e `scripts/worktree-reservation` (argparse). O CLI define `sys.dont_write_bytecode = True` antes de importar o módulo. Alternativa rejeitada: arquivo único sem extensão — impediria reuso do fingerprint por #31.

### D2. Esquema do registry (`schema_version: 1`)
```json
{"schema_version": 1, "repository": {"remote": "<origin url normalizada>", "common_dir": "<abs>"},
 "entries": [{"path": "<abs realpath>", "issue_url": "...", "branch": "...", "base_sha": "...",
   "proposal_sha": null, "pr_url": null, "pr_head": null,
   "owner": {"session": "...", "run": "...", "stage": "planning|apply|correction|...", "host": "...", "pid": 123} ,
   "state": "RESERVED|ACTIVE|WAITING|HANDOFF|RETAINED|CLEANUP_ELIGIBLE|REMOVED",
   "sandbox": null, "head": "...", "diff_fingerprint": "sha256:...", "drift": null,
   "last_verified_at": "<UTC ISO>", "history": [{"at": "...", "event": "...", "session": "...", "detail": "..."}]}]}
```
Chave da entrada = caminho real absoluto. `owner` é `null` quando não há writer ativo (estados `WAITING`, `RETAINED`, `CLEANUP_ELIGIBLE`, `REMOVED`, ou entrada reconstruída). Campos opcionais (`proposal_sha`, `pr_*`, `sandbox`) atualizáveis por `--set`. `history` limitado às últimas 50 entradas. Entrada sem campos obrigatórios = incompleta → só `reconcile` a repara.

### D3. Lock e atomicidade
Lock: `fcntl.flock(LOCK_EX | LOCK_NB)` em `<common>/ai-workflow/worktrees.lock` com retry até `--lock-timeout` (padrão 10 s). Sem `fcntl` → exit 5. Escrita: arquivo temporário no mesmo diretório, `fsync`, `os.replace`, sob o lock. Todo comando mutante relê o registry dentro do lock (compare-and-swap natural). Alternativa rejeitada: lock por `mkdir`/arquivo exclusivo — deixa lock órfão após crash, que induziria a "roubo por idade"; `flock` é liberado pelo kernel quando o processo morre.

### D4. Fingerprint e drift
`diff_fingerprint` = sha256 de: `git status --porcelain=v1 -z --untracked-files=all --ignored=no` filtrado de gerados conhecidos + `git diff HEAD --binary` + (caminho, sha256 do conteúdo) de cada não rastreado não gerado. Ignorados não entram (são definidos pelo projeto), mas `status`/`clean-generated` os inspecionam. Drift = HEAD ≠ registrado ou fingerprint ≠ registrado. Relatório: `head_before`, `head_after`, `git log --format=%H old..new` (ou `diverged` quando `old` não é ancestral), `git diff --name-only old new` e caminhos com status alterado. Quando há drift, a entrada recebe `drift` (persistido) e `verify`/`checkpoint`/`handoff` falham com exit 4 até `reconcile --accept-external --session <dono> --reason <texto>`, que registra o relatório no `history` e grava o novo baseline. O relatório de caminhos é a base para invalidar só a evidência atingida (consumido por #31; aqui apenas emitido).

### D5. Comandos e códigos de saída
`worktree-reservation <cmd> --path <checkout> [--json]`:

| Comando | Efeito |
|---|---|
| `reserve --issue --branch --session --run [--stage] [--base-sha] [--allow-primary]` | Cria/assume entrada sem dono; idempotente para o mesmo dono; estado `ACTIVE`. |
| `verify --session` | Confere caminho, remote, branch, HEAD, fingerprint e dono; não muta (exceto marcar `drift`). |
| `checkpoint --session [--note]` | Após escrita própria: requer dono e ausência de drift persistido; grava novo HEAD/fingerprint. A janela entre o último `verify` e o `checkpoint` é atribuída ao dono (limite documentado). |
| `handoff --from-session --to-session --run [--stage]` | Requer dono = origem e sem drift; troca `owner`, registra `HANDOFF` no history e deixa `ACTIVE`. |
| `release --session --state WAITING|RETAINED|CLEANUP_ELIGIBLE` | Remove dono e muda estado. `REMOVED` só via `mark-removed`, que exige o caminho ausente de `git worktree list --porcelain`. |
| `reconcile [--session --accept-external --reason] [--takeover --expected-owner --stopped-evidence]` | Sem flags: reconstrói entrada ausente/incompleta do Git real, `owner=null`, estado `WAITING`. `--accept-external`: dono aceita drift. `--takeover`: CAS contra `--expected-owner`; recusa se `host` igual e `os.kill(pid, 0)` indica vivo; exige `--stopped-evidence`. |
| `status` / `list` | Somente leitura: entrada, estado Git real, drift calculado, não rastreados classificados (gerado/desconhecido), ignorados gerados. |
| `clean-generated --session [--apply]` | Lista (padrão) ou remove só gerados conhecidos não rastreados/ignorados dentro do checkout; requer dono; nunca segue symlinks para fora; remove diretórios `__pycache__` apenas se ficarem vazios após remover `*.py[co]`. |

Exit: 0 ok · 2 uso · 3 conflito de posse · 4 drift · 5 lock indisponível · 6 identidade divergente (repo/branch/caminho/primário) · 7 registry inválido. Saída `--json` estável para orquestrador.

### D6. Checkout principal
Primário = `git rev-parse --git-dir` igual ao common dir. `reserve` recusa com exit 6 salvo `--allow-primary` (quando as instruções do projeto permitem). O helper não cria worktrees, portanto respeita qualquer local configurado pelo projeto.

### D7. Bytecode
(a) `sys.dont_write_bytecode = True` antes do import de módulo irmão em `scripts/workflow-event`, `scripts/workflow-report` e no novo CLI. (b) `.gitignore` com `__pycache__/` e `*.py[co]` (cobre `tests/__pycache__`, que o `unittest` gera ao importar módulos de teste e que um helper não pode evitar). (c) Comando de validação documentado com `PYTHONDONTWRITEBYTECODE=1`. (d) `update-main`: não rastreados/ignorados que sejam só gerados conhecidos são reportados, não bloqueiam; qualquer outro não rastreado continua bloqueando; se Git recusar o switch/merge por causa deles, parar e reportar (sem `clean`).

### D8. Integração nas skills
Uma frase adicional no parágrafo "Worktree lifecycle" de `milestone-orchestrator`, `implement-issue`, `apply-issue`, `prepare-pr`, `github-resolution`, `address-pr-review`: quando o helper estiver instalado, usar `reserve`/`verify` antes de mutar, `checkpoint` após escrita própria, `handoff` entre sessões; drift suspende a mutação; sem helper, seguir o protocolo manualmente e relatar. O orquestrador é quem chama `handoff` ao despachar Apply (planejamento → Apply → correção). Detalhes ficam em `protocol/WORKTREES.md` (nova subseção "Reservation helper"), propagado por `sync-plugin`.

### Matriz requisito → código → teste (TEST_STRATEGY)

| ID | Cenário | Critério/risco | Camada | Código | Teste (novo em `tests/test_worktree_reservation.py`) |
|---|---|---|---|---|---|
| T1 | Duas sessões reservam o mesmo checkout | AC1 exclusividade; concorrência | Helper + processos reais + Git temporário | `reserve`, lock D3 | `test_concurrent_reserve_grants_single_owner` (N subprocessos com barreira; 1 exit 0, demais exit 3) |
| T1b | Lock retido | Fail closed | Helper | D3 | `test_lock_timeout_leaves_registry_unchanged` (exit 5, bytes iguais) |
| T2 | Writer interrompido, registry perdido, retomada | AC2/AC5 preservação; idade não dá posse | Helper | `reconcile`, takeover | `test_reconcile_rebuilds_without_owner_and_preserves_diff`; `test_takeover_requires_expected_owner_and_evidence_not_age`; `test_takeover_refused_when_prior_pid_alive` |
| T3 | Commit externo altera HEAD | AC3 detecção antes da mutação | Helper | `verify`/`checkpoint`, D4 | `test_external_commit_blocks_until_accept_external` (exit 4, lista commit/caminhos; checkpoint recusado; aceite restaura) ; `test_own_checkpoint_is_not_drift` |
| T4 | pycache + arquivo desconhecido + diff | AC4/AC5 | Helper | classificação, `clean-generated` | `test_clean_generated_removes_only_bytecode`; `test_generated_files_do_not_cause_drift`; `test_clean_requires_owner` |
| T4b | Helpers não criam bytecode | AC4 | Subprocesso sem `PYTHONDONTWRITEBYTECODE` sobre cópia de `scripts/` | D7a | `test_helpers_do_not_write_bytecode` (`workflow-event --help`, `workflow-report --help`, `worktree-reservation --help`) |
| T5 | Planejamento transfere para Apply | AC2 transferência | Simulação orquestração | `handoff` | `test_handoff_planning_to_apply_keeps_checkout_and_revokes_previous` |
| T6 | Branch/remote divergente; checkout principal | AC7 convenções; identidade | Helper | `verify`, D6 | `test_identity_mismatch_and_primary_refusal` |
| T7 | Registry corrompido | Integridade | Unit | loader D2 | `test_corrupt_registry_refuses_mutation` |
| AC6 | Limites com agentes externos | Documentação | Doc check | `protocol/WORKTREES.md` | Revisão do diff + presença da seção após `sync-plugin` |
| Dist | Cópias sincronizadas | Distribuição | Check | `sync-plugin` | `scripts/sync-plugin && git status --porcelain` sem diferença após commit |

Testes existentes reutilizados: `tests/test_workflow_metrics.py` permanece inalterado e deve continuar passando (regressão das linhas `dont_write_bytecode`).

### Arquivos esperados

Criados: `scripts/worktree-reservation` (0755), `scripts/worktree_registry.py`, `tests/test_worktree_reservation.py`, `.gitignore`.
Alterados: `scripts/workflow-event`, `scripts/workflow-report`, `scripts/sync-plugin`, `protocol/WORKTREES.md`, `skills/milestone-orchestrator/SKILL.md`, `skills/implement-issue/SKILL.md`, `skills/apply-issue/SKILL.md`, `skills/prepare-pr/SKILL.md`, `skills/github-resolution/SKILL.md`, `skills/address-pr-review/SKILL.md`, `skills/update-main/SKILL.md`, `skills/update-ai-workflow/SKILL.md`, `README.md`, `README.en.md`.
Regenerados por `scripts/sync-plugin` (não editar à mão): `skills/*/references/WORKTREES.md` e `plugins/my-ai-skills/{skills,protocol,scripts}/**` correspondentes.
OpenSpec: `openspec/changes/issue-35-checkout-write-reservation/**` (archive → `openspec/specs/checkout-write-reservation/spec.md`).

## Risks / Trade-offs

- [TOCTOU entre `verify` e a mutação; agentes externos não cooperantes] → documentado como limite; detecção na próxima verificação/checkpoint; janela curta porque `verify` antecede cada mutação.
- [Escrita externa entre `verify` e `checkpoint` atribuída ao dono] → limite documentado; mitigado por checkpoint imediatamente após a própria mutação.
- [`pid` reutilizado/host diferente] → liveness só é usada para **recusar** tomada; nunca autoriza sozinha (evidência de término é sempre exigida).
- [Fingerprint caro em checkouts grandes] → usa apenas comandos Git e hash de não rastreados não gerados; aceitável para repositórios de workflow.
- [Sobreposição com #31/#32 em `workflow-event`/`workflow-report`] → alteração restrita a uma linha antes do import; implementação serializada no milestone; rebase trivial.
- [`fcntl` ausente] → exit 5 e orientação manual, coerente com "não despachar writer concorrente".

## Migration Plan

Aditivo. Registry é criado sob demanda; checkouts existentes sem entrada são reconstruídos por `reconcile`. Rollback: remover helper e `<common>/ai-workflow/` (dado local, fora do controle de versão).
