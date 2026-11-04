# Design

## Context

Ver proposal.md (Why). Estado em `main@5825a9c`:

- `protocol/WORKTREES.md` define registry, lock, atomicidade, lifecycle `RESERVED → ACTIVE → WAITING / HANDOFF → RETAINED / CLEANUP_ELIGIBLE → REMOVED` e a proibição de tomar posse por idade; nenhum script implementa isso.
- Padrão existente de helper: executável sem extensão + módulo Python irmão (`scripts/workflow-event` importa `scripts/workflow_metrics.py` via `sys.path.insert`). Essa importação é a origem de `scripts/__pycache__/workflow_metrics.cpython-314.pyc` (reproduzido). Testes usam `unittest` com `sys.path` apontando para `scripts/`. `workflow-event` valida `run_id`/`worker_id` com `SAFE_ID = ^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$`.
- `scripts/sync-plugin` copia uma lista fixa de helpers (`for helper in …`) para `plugins/my-ai-skills/scripts/` e embute `protocol/WORKTREES.md` em `skills/{milestone-orchestrator,milestone-progress,implement-issue,apply-issue,prepare-pr,github-resolution,address-pr-review}/references/`.
- `skills/update-main/SKILL.md` passo 2 para em qualquer não rastreado.
- Não há `.gitignore` nem CI em `.github/`; o gate local é `python3 -m unittest discover -s tests`.
- Rulings do lote #31–#35 (ordem serializada #35 → #31 → #32 → #33 → #34): R1 — `worktree_registry.py` é dono do fingerprint canônico de estado de código e #31 o importa; R5 — dados locais em `<git-common-dir>/ai-workflow/`; R6 — todo helper novo desliga bytecode e entra no teste de bytecode; R9 — #35 é dono da seção "Worktree lifecycle" das skills.

## Goals / Non-Goals

**Goals:**
- Operacionalizar o contrato já escrito em WORKTREES, sem protocolo concorrente.
- Publicar uma API estável de estado de código reutilizável por #31/#32.
- Prova executável dos cenários T1–T5 em repositórios Git temporários.
- Integração das skills por referência a comandos concretos, mantendo o texto curto.

**Non-Goals:**
- Criar, mover ou remover worktrees (continua com `git worktree add/remove` pelo coordenador; housekeeping inalterado).
- Registro de evidência de testes (#31), estado de execução/progresso (#32), preflight de configuração (#33), log de hipóteses (#34).
- Impedir agentes que não usam o protocolo; proteção de ambiente/sandbox (Docker, DB) além do campo `sandbox` já previsto.
- Lock em Windows/sem `fcntl` (falha fechada, documentada).

## Decisions

### D1. Módulo + CLI fino e API pública de estado de código
`scripts/worktree_registry.py` (lógica e **API pública estável**, importada pelos testes, por `workflow_evidence.py` de #31 e consultável por #32) e `scripts/worktree-reservation` (argparse). O CLI define `sys.dont_write_bytecode = True` antes de importar o módulo. Alternativa rejeitada: arquivo único sem extensão — impediria a importação do fingerprint canônico por #31 (R1).

API pública, documentada no docstring do módulo e em WORKTREES "Reservation helper" como **fingerprint canônico de estado de código**. Mudança incompatível de cálculo exige nova versão no digest; nomes e campos abaixo não mudam sem nova versão:

```python
FINGERPRINT_VERSION = "v1"
SAFE_ID: re.Pattern                        # idêntico ao SAFE_ID de scripts/workflow-event
KNOWN_GENERATED_PATTERNS: tuple[str, ...]  # ("__pycache__/", "*.pyc", "*.pyo")

def is_known_generated(rel_path: str) -> bool
def code_state(checkout, *, exclude_paths=(), include_ignored=()) -> CodeState
def drift_report(baseline: CodeState | dict, current: CodeState, *, checkout) -> dict | None

@dataclass(frozen=True)
class IndexEntry:
    stage: int           # 0 normal; 1/2/3 em conflito
    mode: str            # modo Git do índice (ex.: 100644, 100755, 120000)
    oid: str             # blob do índice (git ls-files --stage -z)

@dataclass(frozen=True)
class PathEntry:
    path: str            # relativo à raiz do checkout, separador "/"
    status: str          # XY de `git status --porcelain=v1`; "??" não rastreado; "!!" ignorado declarado
    sha256: str | None   # conteúdo atual na working tree; None quando deleted
    deleted: bool
    index: tuple[IndexEntry, ...]  # ordenado por stage; vazio para não rastreados/ignorados

@dataclass(frozen=True)
class CodeState:
    head: str | None              # None em repositório sem commits
    digest: str                   # "sha256:v1:<64 hex>"
    entries: tuple[PathEntry, ...]  # ordenado por path
    generated: tuple[str, ...]    # gerados conhecidos vistos (fora do digest)
    def to_json(self) -> dict     # {"head","digest","entries":[{path,status,sha256,deleted,index:[{stage,mode,oid}]}],"generated"}
```

- `exclude_paths` (globs relativos) remove caminhos das entradas e do digest (ex.: relatórios de #31 gravados dentro do checkout).
- `include_ignored` (caminhos/globs relativos) inclui arquivos ignorados **declarados** (ex.: `app/etc/env.php`) com status `!!`; ignorados não declarados nunca entram.
- Gerados conhecidos nunca entram no digest; aparecem em `generated`.
- Para cada caminho alterado, `git ls-files --stage -z` fornece blobs e modos do índice, inclusive estágios de conflito; `status` e `sha256` representam a working tree. Mudança no blob ou modo staged enquanto XY e working tree permanecem iguais **muda** o digest. Não rastreados/ignorados declarados têm `index=[]`; symlinks são hasheados pelo alvo, sem segui-los. A amostragem entre chamadas Git não é atômica contra escritores externos (limite documentado).
- Digest = sha256 do JSON canônico (`sort_keys=True`, separadores compactos, UTF-8) de `{"v":"v1","head":…,"entries":[…]}` (incluindo `index`), prefixado `sha256:v1:`. Não é hash de `git diff HEAD --binary`: consumidores precisam de caminhos individuais para invalidar só a evidência afetada.

### D2. Esquema do registry (`schema_version: 1`)
```json
{"schema_version": 1, "repository": {"remote": "<origin url normalizada>", "common_dir": "<abs>"},
 "entries": [{"path": "<abs realpath>", "issue_url": "...", "branch": "...", "base_sha": "...",
   "proposal_sha": null, "pr_url": null, "pr_head": null,
   "owner": {"session": "<worker_id>", "run": "<run_id>", "stage": "planning|apply|correction|...", "host": "...", "pid": null},
   "state": "RESERVED|ACTIVE|WAITING|HANDOFF|RETAINED|CLEANUP_ELIGIBLE|REMOVED",
   "sandbox": null, "baseline": {"head": "...", "digest": "sha256:v1:...", "entries": []}, "drift": null,
   "last_verified_at": "<UTC ISO>", "verified_for": {"session": "...", "digest": "sha256:v1:..."},
   "history": [{"at": "...", "event": "...", "session": "...", "detail": {}}]}]}
```
- Chave da entrada = caminho real absoluto. `baseline` = `CodeState.to_json()` sem `generated`.
- `owner` é `null` sem writer ativo (`WAITING`, `RETAINED`, `CLEANUP_ELIGIBLE`, `REMOVED`, entrada reconstruída).
- `--session`/`--run` seguem as convenções `worker_id`/`run_id` de `workflow-event` e a mesma validação `SAFE_ID` (exit 2 se inválidos), para #32 relacionar dono e eventos de etapa sem camada de mapeamento.
- `owner.pid` só é preenchido por `--owner-pid` explícito (D5/S2).
- `baseline=null` e `verified_for=null` em `RESERVED` antes da criação; `verified_for` é `null` até `verify` bem-sucedido para o dono/baseline atual. `verify` persiste esse recibo e `last_verified_at` sob o lock; `checkpoint`, troca de dono e aceite de drift o invalidam. Não é prova de que nenhuma escrita externa ocorreu após a verificação.
- Campos opcionais (`proposal_sha`, `pr_*`, `sandbox`) atualizáveis por `--set key=value`. `history` limitado às últimas 50 entradas.
- Entrada sem campos obrigatórios = incompleta → só `reconcile` a repara.
- Uma issue tem no máximo uma entrada não `REMOVED`: `reserve` da mesma `issue_url` em outro caminho falha com exit 3 e aponta o caminho existente (one branch/worktree per issue).

### D3. Lock e atomicidade
Lock: `fcntl.flock(LOCK_EX | LOCK_NB)` em `<common>/ai-workflow/worktrees.lock` com retry até `--lock-timeout` (padrão 10 s). Sem `fcntl` → exit 5. Escrita: arquivo temporário no mesmo diretório, `fsync`, `os.replace`, sob o lock. Todo comando mutante relê o registry dentro do lock (compare-and-swap natural) e recalcula `code_state()` do checkout **existente** antes de decidir; `--planned` usa somente a âncora/inventário e `mark-removed` somente a âncora/inventário, nunca o destino ausente. Alternativa rejeitada: lock por `mkdir`/arquivo exclusivo — deixa lock órfão após crash, o que induziria a "roubo por idade"; `flock` é liberado pelo kernel quando o processo morre.

### D4. Drift e inspeção somente leitura
- Drift = `head` atual ≠ `baseline.head` ou `digest` atual ≠ `baseline.digest`, calculado para **qualquer** entrada com baseline, com ou sem dono.
- `drift_report()` tem chaves estáveis: `head_before`, `head_after`, `commits` (`git log --format=%H old..new` quando ambos existem), `diverged` (bool, `old` não ancestral de `new` quando ambos existem), `committed_paths` (`git diff --name-only old new` quando ambos existem), `changed_paths` (caminhos cujo `status`/`sha256`/`deleted`/**`index`** difere entre baselines), `detected_at`. Sem HEAD comparável, listas vazias e `diverged=false`, preservando `changed_paths`.
- Com drift, a entrada recebe `drift` persistido; `verify`, `checkpoint`, `handoff` e `reserve` falham com exit 4 e o relatório até aceite explícito (D5). O relatório por caminho é a base para invalidar só a evidência atingida (consumido por #31; aqui apenas emitido).
- **Checkpoint não é verify:** `verify` compara estado observado com baseline e persiste drift se diferir; se igual, registra `verified_for` e horário. Depois do `verify` bem-sucedido, o dono pode escrever e chamar `checkpoint` para gravar o novo estado, desde que permaneça o mesmo dono/identidade, `verified_for` corresponda a sessão/digest do baseline ainda registrado e não haja drift **previamente detectado e persistido**. O checkpoint não compara o digest novo ao anterior como condição de bloqueio — isso bloquearia a escrita própria. `handoff`/`release` exigem estado atual igual ao último checkpoint, além de ausência de drift persistido; `release` não absorve alterações no ato. Não há prova técnica de autoria de mudança concorrente entre `verify` e `checkpoint`: ela pode ser atribuída operacionalmente ao dono nessa janela; documento e testes não devem afirmar certeza impossível. Um `verify`/`release` que já detectou drift nunca é sanado por `checkpoint`; exige aceite explícito com motivo.
- **Sem lock de índice:** toda leitura Git do helper (`status`, `ls-files`, `log`, `diff`, `rev-parse`, `merge-base`, `worktree list`, `check-ignore`, `remote get-url`) roda como `git --no-optional-locks …` com `GIT_OPTIONAL_LOCKS=0` no ambiente, centralizada numa única função `_git()`. O helper nunca executa comando Git que escreva índice ou refs.

### D5. Comandos e códigos de saída
`worktree-reservation <cmd> --path <checkout> [--json]`:

| Comando | Efeito |
|---|---|
| `reserve --issue --branch --session --run [--stage] [--base-sha] [--owner-pid N] [--planned --repository EXISTING_CHECKOUT] [--allow-primary] [--accept-external --reason T]` | **Entrada nova**: grava baseline e estado `ACTIVE`. **`--planned`**: caminho ainda inexistente; `--repository` aponta checkout Git **existente** do mesmo repositório para resolver common dir/remote e lock, sem acessar Git no caminho planejado; grava `RESERVED` (sem baseline) antes de `git worktree add`; próxima `reserve` da mesma sessão após criação verifica caminho/branch e grava baseline `ACTIVE`; outra sessão recebe exit 3. **Entrada existente sem dono** (`WAITING`/`RETAINED`/reconstruída): compara com baseline; sem drift assume posse; com drift falha exit 4 com relatório, ou, com `--accept-external --reason`, assume posse registrando relatório e motivo no `history` e grava novo baseline. **Mesmo dono**: idempotente (drift continua exit 4). **Outro dono ativo**: exit 3 com dono. `--accept-external` exige `--reason` e só aceita drift conhecido, não substitui validação de identidade. |
| `verify --session` | Confere caminho, remote, branch, HEAD, digest e dono; persiste `drift` quando diverge ou `verified_for`/`last_verified_at` quando passa. |
| `checkpoint --session [--note]` | Após escrita própria: exige dono/identidade, verificação bem-sucedida anterior do baseline atual e ausência de drift persistido; grava novo baseline e horário. Diferença atual é esperada, não bloqueia por si só. Janela após `verify` é atribuída operacionalmente ao dono, sem comprovação de autoria (D4). |
| `handoff --from-session --to-session --run [--stage] [--owner-pid N]` | Requer dono = origem e sem drift; troca `owner`, registra `HANDOFF` no `history` e deixa `ACTIVE`. O coordenador só chama `handoff` depois que o worker de origem retornou (WORKTREES: "End the planning writer before starting the fresh Apply writer"). |
| `release --session --state WAITING\|RETAINED\|CLEANUP_ELIGIBLE` | Exige baseline igual ao estado atual e nenhum drift persistido; **não** grava baseline novo. Se o dono escreveu, deve antes fazer `checkpoint`; depois remove dono e muda estado. |
| `mark-removed --repository EXISTING_CHECKOUT` | Somente após cleanup seguro de WORKTREES, sem dono, e caminho ausente em `git worktree list --porcelain`; usa checkout existente como âncora do common dir/lock e registra `REMOVED`, sem remover arquivos ou worktree. |
| `reconcile [--session S --accept-external --reason T] [--takeover --session S --run R --expected-owner O --stopped-evidence T]` | Sem flags: reconstrói entrada ausente/incompleta do Git real, `owner=null`, estado `WAITING`, sem tocar em arquivos. `--accept-external`: o dono aceita drift. `--takeover`: CAS contra `--expected-owner`; exige `--stopped-evidence`; recusa se `owner.pid` registrado, `host` igual e `os.kill(pid, 0)` indicar vivo. Idade nunca é critério. |
| `status` / `list` | Somente leitura: entrada, `code_state()` atual, drift calculado, gerados conhecidos e não rastreados desconhecidos. |
| `clean-generated --session [--apply]` | Lista (padrão) ou remove só gerados conhecidos elegíveis (D7e); requer dono para `--apply`. |

**PID (S2):** o CLI e o shell do agente são efêmeros, então `getpid`/`getppid` não representam o writer. O helper só registra `pid` quando o chamador passa `--owner-pid` (processo de vida longa do runtime/worker). Liveness é **consultiva**: serve apenas para *recusar* takeover quando o processo registrado está vivo no mesmo host; ausência de pid ou pid morto nunca autoriza sozinha — `--stopped-evidence` é sempre obrigatório.

**Saída `--json` estável** (`status`, `verify`, `reserve`, e corpo de erro exit 3/4/6) — chaves mínimas que #32/orquestrador podem consumir:
`{"ok": bool, "exit_code": int, "error": str|null, "path", "issue_url", "branch", "state", "owner": {session, run, stage, host, pid}|null, "head", "digest", "drift": <drift_report>|null, "generated_paths": [...], "unknown_untracked_paths": [...], "last_verified_at"}`. Chaves novas podem ser adicionadas; as listadas não mudam de significado.

Exit: 0 ok · 2 uso/ID inválido · 3 conflito de posse · 4 drift · 5 lock indisponível · 6 identidade divergente (repo/branch/caminho/primário) · 7 registry inválido.

### D6. Checkout principal e ordem de criação
- Primário = `git rev-parse --git-dir` igual ao common dir. `reserve` recusa com exit 6 salvo `--allow-primary` (quando as instruções do projeto permitem).
- O helper não cria worktrees, portanto respeita qualquer local configurado pelo projeto.
- Ordem "inventory → reservation → creation" de WORKTREES: o coordenador faz `reserve --planned --repository <checkout-existente>` (estado `RESERVED`) antes de `git worktree add`, e `reserve` novamente após a criação (`ACTIVE`). Identidade e lock são resolvidos **exclusivamente** pelo checkout existente; `--repository` é obrigatório para `--planned` e destino não pode existir. Conferir branch/caminho desocupados no inventário; `git worktree add` também recusa caminho existente ou branch em uso. Reservar após criar sem `--planned` continua permitido (worktree preexistente ou retomada).

### D7. Bytecode e gerados conhecidos
- (a) `sys.dont_write_bytecode = True` antes do import de módulo irmão em `scripts/workflow-event`, `scripts/workflow-report` e no novo CLI.
- (b) `.gitignore` com `__pycache__/` e `*.py[co]` (cobre `tests/__pycache__`, que o `unittest` gera ao importar módulos de teste e que um helper não pode evitar).
- (c) Comando de validação documentado com `PYTHONDONTWRITEBYTECODE=1`.
- (d) `update-main`: não rastreados/ignorados que sejam só gerados conhecidos são reportados e não bloqueiam; qualquer outro não rastreado continua bloqueando; se Git recusar o switch/merge por causa deles, parar e reportar (sem `clean`).
- (e) `clean-generated` enumera com `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all --ignored=matching`. É elegível apenas arquivo `*.py[co]` (e o diretório `__pycache__` que ficar vazio) cujo caminho **não** esteja sob outro diretório ignorado além do próprio `__pycache__` (verificado com `git check-ignore` em cada ancestral). Assim `.venv/`, `node_modules/` e semelhantes nunca são varridos. Não segue symlinks; nunca remove fora do checkout.
- (f) R6: `test_helpers_do_not_write_bytecode` lê a lista de helpers de `scripts/sync-plugin` (laço `for helper in …` e linhas `install … scripts/<nome>`), executa com `--help` cada um cujo shebang é Python, numa cópia temporária de `scripts/` sem `PYTHONDONTWRITEBYTECODE`, e afirma ausência de `__pycache__`. Helpers adicionados por #31/#33/#34 passam a ser cobertos sem editar o teste.

### D8. Integração nas skills
- Uma frase adicional no parágrafo "Worktree lifecycle" de `milestone-orchestrator`, `implement-issue`, `apply-issue`, `prepare-pr`, `github-resolution`, `address-pr-review`: quando o helper estiver instalado, usar `reserve`/`verify` antes de mutar, `checkpoint` após escrita própria, `handoff` entre sessões; drift suspende a mutação até aceite registrado; sem helper, seguir o protocolo manualmente e relatar.
- `milestone-orchestrator`: usa `reserve --planned` antes de criar worktree e chama `handoff` ao despachar Apply/correção, depois que o worker anterior retornou.
- `milestone-progress` (N1): pode usar `status`/`list --json` somente leitura para a tabela de worktrees; nunca muta.
- Detalhes ficam em `protocol/WORKTREES.md` (nova subseção "Reservation helper"), propagado por `sync-plugin`.

### Matriz requisito → código → teste (TEST_STRATEGY)

| ID | Cenário | Critério/risco | Camada | Código | Teste (novo em `tests/test_worktree_reservation.py`) |
|---|---|---|---|---|---|
| T1 | Duas sessões reservam o mesmo checkout | AC1 exclusividade; concorrência | Helper + processos reais + Git temporário | `reserve`, D3 | `test_concurrent_reserve_grants_single_owner` (N subprocessos com barreira; 1 exit 0, demais exit 3) |
| T1b | Lock retido | Fail closed | Helper | D3 | `test_lock_timeout_leaves_registry_unchanged` (exit 5, bytes iguais) |
| T1c | Reserva planejada antes da criação; mesma issue em outro caminho | Lifecycle `RESERVED`; one worktree per issue; caminho ausente não tem common dir próprio | Helper | `reserve --planned --repository`, D2/D6 | `test_planned_reservation_then_activate_and_single_path_per_issue` (checkout existente como âncora; sem `--repository` exit 2; sem Git no destino inexistente) |
| T2 | Writer interrompido, registry perdido, retomada | AC2/AC5 preservação; idade não dá posse | Helper | `reconcile`, takeover | `test_reconcile_rebuilds_without_owner_and_preserves_diff`; `test_takeover_requires_expected_owner_and_evidence_not_age`; `test_takeover_refused_when_owner_pid_alive` (usa `--owner-pid` de subprocesso vivo) |
| T3 | Commit externo altera HEAD de checkout com dono | AC3 detecção antes da mutação | Helper | `verify`/`checkpoint`, D4 | `test_external_commit_blocks_until_accept_external` (exit 4, `commits`/`committed_paths`; checkpoint recusado; aceite restaura); `test_own_checkpoint_is_not_drift` (verify → escrita própria → checkpoint → verify); `test_detected_drift_cannot_be_checkpointed` |
| T3a | Escrita após checkpoint e release | Baseline do último checkpoint, sem absorção implícita | Helper | `release`, D4/D5 | `test_release_requires_checkpoint_after_owner_write` (fixture A: verify → escrita → release exit 4, drift persistido, checkpoint recusado; fixture B: verify → escrita → checkpoint → release passa) |
| T3b | `release WAITING` → commit/edição externa → `reserve` por nova sessão | AC3 em entrada sem dono (M1) | Helper | `reserve` existente, D4/D5 | `test_reserve_after_release_detects_external_change` (exit 4 com relatório; sem `--accept-external` não assume; com aceite assume e registra no `history`) |
| T3c | API canônica de estado de código | R1 contrato para #31; caminhos individuais, índice | Unit + Git temporário | `code_state`, `drift_report`, `is_known_generated` | `test_code_state_entries_digest_and_options` (digest `sha256:v1:`, entrada por caminho com sha256/deleted/index, `exclude_paths`, `include_ignored`, gerados fora do digest); `test_index_blob_and_mode_change_with_same_xy_and_worktree_changes_digest` (inclui `changed_paths`) |
| T4 | pycache + arquivo desconhecido + diff + `.venv` ignorado | AC4/AC5; limpeza proporcional | Helper | classificação, `clean-generated` D7e | `test_clean_generated_removes_only_bytecode` (inclui `.venv/lib/__pycache__/m.pyc` preservado); `test_generated_files_do_not_cause_drift`; `test_clean_requires_owner` |
| T4b | Helpers não criam bytecode | AC4; R6 | Subprocesso sem `PYTHONDONTWRITEBYTECODE` sobre cópia de `scripts/` | D7a/D7f | `test_helpers_do_not_write_bytecode` (itera helpers Python de `sync-plugin`) |
| T5 | Planejamento transfere para Apply | AC2 transferência | Simulação orquestração | `handoff` | `test_handoff_planning_to_apply_keeps_checkout_and_revokes_previous` |
| T6 | Branch/remote divergente; checkout principal; ID inválido | AC7 convenções; identidade; S3 | Helper | `verify`, D2/D6 | `test_identity_mismatch_primary_refusal_and_safe_ids` (inclui `SAFE_ID` igual ao de `workflow-event`) |
| T7 | Registry corrompido | Integridade | Unit | loader D2 | `test_corrupt_registry_refuses_mutation` |
| T8 | Inspeção sem lock de índice | S4; não bloquear `git add` do dono | Unit | `_git()` D4 | `test_git_inspection_uses_no_optional_locks` (verifica argv/env de todas as chamadas do wrapper) |
| T9 | Contrato JSON | S3 consumo por #32 | Helper | D5 | asserts das chaves mínimas em T1/T3/T3b (sem teste separado) |
| AC6 | Limites com agentes externos | Documentação | Doc check | `protocol/WORKTREES.md` | Revisão do diff + presença da seção após `sync-plugin` |
| Dist | Cópias sincronizadas | Distribuição | Check | `sync-plugin` | `scripts/sync-plugin && git status --porcelain` sem diferença após commit |

Testes existentes reutilizados: `tests/test_workflow_metrics.py` permanece inalterado e deve continuar passando (regressão das linhas `dont_write_bytecode`).

### Arquivos esperados

Criados: `scripts/worktree-reservation` (0755), `scripts/worktree_registry.py`, `tests/test_worktree_reservation.py`, `.gitignore`.
Alterados: `scripts/workflow-event`, `scripts/workflow-report`, `scripts/sync-plugin`, `protocol/WORKTREES.md`, `skills/milestone-orchestrator/SKILL.md`, `skills/milestone-progress/SKILL.md`, `skills/implement-issue/SKILL.md`, `skills/apply-issue/SKILL.md`, `skills/prepare-pr/SKILL.md`, `skills/github-resolution/SKILL.md`, `skills/address-pr-review/SKILL.md`, `skills/update-main/SKILL.md`, `skills/update-ai-workflow/SKILL.md`, `README.md`, `README.en.md`.
Regenerados por `scripts/sync-plugin` (não editar à mão): `skills/*/references/WORKTREES.md` e `plugins/my-ai-skills/{skills,protocol,scripts}/**` correspondentes.
OpenSpec: `openspec/changes/issue-35-checkout-write-reservation/**` (archive → `openspec/specs/checkout-write-reservation/spec.md`).

## Risks / Trade-offs

- [TOCTOU entre `verify` e a mutação; agentes externos não cooperantes] → documentado como limite; detecção na próxima verificação/checkpoint/reserva; janela curta porque `verify` antecede cada mutação.
- [Escrita externa entre `verify` e `checkpoint` indistinguível de escrita própria] → atribuição apenas operacional, não prova de autoria; janela mitigada por checkpoint imediatamente após a própria mutação, sem promessa de detecção infalível.
- [Mudança externa enquanto o checkout está sem dono] → `release` exige o baseline já atualizado por checkpoint, sem gravar um novo; `reserve` compara com ele (M1). Nada é absorvido sem `--accept-external` registrado.
- [`pid` efêmero/reutilizado/host diferente] → só registrado por `--owner-pid`; usado apenas para **recusar** takeover; nunca autoriza sozinho.
- [Mudança na API canônica quebra #31] → nomes/campos de D1 congelados; alteração de cálculo exige `FINGERPRINT_VERSION` novo; T3c protege o contrato.
- [Fingerprint caro em checkouts grandes] → só caminhos alterados/não rastreados são lidos; aceitável para repositórios de workflow.
- [Sobreposição com #31/#32 em `workflow-event`/`workflow-report`, `sync-plugin`, README e skills] → alteração restrita a uma linha antes do import; seções disjuntas conforme R9; implementação serializada (#35 primeiro); cópias regeneradas por `sync-plugin`, nunca mescladas à mão.
- [`fcntl` ausente] → exit 5 e orientação manual, coerente com "não despachar writer concorrente".

## Migration Plan

Aditivo. Registry é criado sob demanda em `<git-common-dir>/ai-workflow/`; checkouts existentes sem entrada são reconstruídos por `reconcile`. Rollback: remover helper e `<common>/ai-workflow/worktrees.{json,lock}` (dado local, fora do controle de versão).
