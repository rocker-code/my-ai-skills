# Design — issue-31-test-evidence-handoff

## Context

Ver proposal.md (Why). Estado observado em `main @ 5825a9c`:

- `scripts/workflow-event` L113-115 aceita `--evidence` só como `https://github.com/...` ou SHA; grava strings em `event.evidence` e `record.evidence`.
- `scripts/workflow_metrics.py` `parse_run_comment` exige `schema_version == 1`; `summarize_run` repassa `evidence`; `scripts/workflow-report` L208-209 concatena as strings.
- `skills/prepare-pr/SKILL.md` L91, `skills/apply-issue/SKILL.md` ("Before commit…"), `skills/pr-audit/SKILL.md` L26 e `skills/post-pr-audit/SKILL.md` L12 descrevem em prosa prova do código exato e reuso restrito, sem mecanismo.
- `protocol/TEST_STRATEGY.md` define a matriz Scenario | Critério/risco | Camada | Teste; `scripts/sync-plugin` empacota-o em 8 skills e copia helpers para `plugins/my-ai-skills/scripts/`.
- Sem CI hospedado (`.github/` ausente). Gate local: `python3 -m unittest discover -s tests`.
- Helpers existentes usam só stdlib + `git`/`gh` por subprocess; testes usam `gh` falso em `PATH` e diretórios temporários.

## Goals / Non-Goals

**Goals:**
- Registro genérico e verificação completos para comandos não M2T (inclui comandos M2T executados como comando comum).
- Transporte entre worktrees/sessões do mesmo clone sem passo manual; entre runtimes via pacote portátil ou metadados publicados.
- Registro extensível por #32 (correlação com execução/estado) e #34 (tentativas/hipóteses) sem bifurcar o formato.

**Non-Goals:**
- Adaptador/leitura do registro nativo M2T (follow-up bloqueado por M2T #12 — ver "Contract handoff").
- Decidir suficiência de cobertura (continua em TEST_STRATEGY) ou selecionar testes por impacto (#33).
- Estado ao vivo de processos/jobs, reconciliação de execução ativa (#32).
- Reserva de escrita de checkout (#35); log de hipóteses de retry (#34).
- Upload de logs para serviços externos (gist, artifacts) — não implementado; apenas referência por URL+checksum quando o projeto já os tiver.

## Decisions

### D1. Helper novo `scripts/workflow-evidence` + biblioteca `scripts/workflow_evidence.py`
Segue o padrão `workflow-event` + `workflow_metrics.py` (CLI fino, lógica importável e testável). Biblioteca expõe `code_fingerprint(repo, config_paths)` e `load_manifest/verify_manifest` para reuso por #32/#34/#35.
Alternativa rejeitada: estender `workflow-event` — mistura registro de tempo (single-writer orquestrador, GitHub) com prova local do implementador e aumentaria conflito com #32.

Subcomandos: `record` (executa `-- <cmd...>`), `register-hosted` (resultado de CI: URL, SHA, status; sem log), `verify`, `export`, `import`, `publish`, `list`, `show`, `prune`. Saída `--format text|json`; exit codes: `record` propaga o do comando; `verify` retorna 0 somente se todos os registros pedidos estiverem `verified` e `passed`, 3 para não verificado, 2 para erro de uso.

### D2. Manifesto `my-ai-skills.test-evidence/v1`
Campos (obrigatórios em negrito): **`schema`**, **`evidence_id`** (`ev-<UTC>-<8 hex>`, mesmo padrão de `new-run-id`), **`kind`** (`local`|`hosted`), **`repository`** (owner/repo do `origin`, se houver, e toplevel relativo não publicado), **`code`** {**`head`**, **`fingerprint`**, `dirty`, `changed_paths` [{path, sha256|deleted}], `config_paths` [{path, sha256|missing}], `fingerprint_after`}, **`command`** {argv mascarado, cwd relativo ao toplevel}, **`selection`** (string livre: filtro/caminhos), **`obligations`** [{**`id`**, `required_gate`: bool, `relevant_paths`: [glob]}], `openspec_change`, **`runner`** {python, os, hostname-hash, ferramentas declaradas via `--tool name=version`, nomes de env permitidos}, **`started_at`**, **`finished_at`**, **`exit_code`** (null se interrompido), **`status`** (`passed`|`failed`|`interrupted`), `counts` {tests, failures, errors, skipped, source: `junit`|`declared`|`none`}, **`artifacts`** [{name, role: `log`|`report`, sha256, bytes, state: `present`|`missing`}], `hosted` {url, run_id, head} (kind hosted), `correlation` {run_id, issue_url, stage, worker_id} (opcional; ponto de extensão para #32), `producer` (opcional, null; reservado — ver D9), `extensions` {} (namespaced; #34 usa p.ex. `extensions.attempts`).
Leitores ignoram e preservam chaves desconhecidas; mudança incompatível exige `v2`.

### D3. Fingerprint
`sha256` sobre JSON canônico de: HEAD; para cada caminho em `git status --porcelain=v1 -z --untracked-files=all` (rastreados alterados + não rastreados não ignorados), `sha256` do conteúdo atual ou `deleted`; para cada `--config PATH` declarado (pode ser ignorado pelo Git), `sha256` ou `missing`. Ordenado por caminho. Capturado antes e depois de `record`; divergência → `status_note: concurrent_change` e verificação `ambiguous`. Custo proporcional ao diff, não à árvore inteira.
Comparação no `verify`: recalcula o fingerprint do candidato; se igual → corresponde. Se diferente, caminhos divergentes = `git diff --name-only <head_registro> <HEAD_candidato>` ∪ caminhos sujos de qualquer lado cujo hash difira ∪ configs com hash diferente.
Alternativa rejeitada: `git stash create`/árvore temporária — escreve objetos no repositório e não cobre configs ignoradas.

### D4. Armazenamento e transporte
- Local: `$(git rev-parse --git-common-dir)/my-ai-skills/evidence/<evidence_id>/{manifest.json,artifacts/…}`, comum a todas as worktrees do clone (T1 mesmo host). Nunca dentro da árvore de trabalho; nada é commitado.
- Outro runtime: `export` gera `<evidence_id>.tar.gz` (manifesto + artefatos + `SHA256SUMS`); `import` valida membros (sem caminhos absolutos, `..` ou links) e checksums antes de gravar no armazenamento local. O orquestrador transporta o pacote pelo meio já autorizado do runtime (cópia para a sessão seguinte); o helper não envia logs a terceiros.
- GitHub: `publish --issue|--pr URL` grava só o manifesto (sem logs) num comentário oculto `<!-- my-ai-skills-test-evidence:v1 -->` por `evidence_id` (atualiza se existir, como `workflow-event`); `verify --from-github URL` lê o manifesto e, sem artefatos locais, resulta `metadata_only`. Escopo de escrita idêntico ao já usado por `workflow-event`. Limite: manifesto > 60 000 bytes é rejeitado para publicação.
Alternativas rejeitadas: refs Git customizadas no `origin` (efeito remoto novo, retenção difícil); gist (exposição por URL); commit no branch (polui PR).

### D5. Conteúdo sensível
Logs e relatórios ficam apenas locais/no pacote. argv mascarado para `--*token*|--*password*|--*secret*|--*key*=valor`, `Authorization: …`, `ghp_…`/`github_pat_…`, `://user:pass@`. Ambiente: somente nomes de uma lista permitida (`CI`, `PYTHON*`, `NODE_ENV`, …) e `--env-name` explícito, nunca valores. `hostname` armazenado como hash. Documentação proíbe passar segredos em argv; `export` exibe aviso de que logs podem conter dados sensíveis e exige revisão antes de compartilhar fora do repositório.

### D6. Estados de verificação (ordem de precedência)
1. Manifesto ilegível/campos obrigatórios ausentes/schema desconhecido → `incomplete`.
2. `fingerprint != fingerprint_after` → `ambiguous`.
3. `status: interrupted` ou `exit_code` null → `incomplete`.
4. `kind: hosted` para obrigação `required_gate` → `not_applicable` (AC5).
5. Fingerprint ≠ candidato → `stale` com `changed_paths` e impacto por obrigação (`affected`/`unaffected`); obrigação `required_gate` é sempre `affected`.
6. Artefato `missing` ou ausente localmente/checksum divergente → `incomplete` (se veio do GitHub sem artefatos → `metadata_only`).
7. Caso contrário → `verified`, com `result` = `passed` se `exit_code == 0`, senão `failed` (prova verificada de falha).
Cada estado inclui `reasons[]` e `recovery` {obligations, action: `rerun`|`import_bundle`|`restore_artifact`}.

### D7. Invalidação por obrigação (T4)
`relevant_paths` declarados por obrigação no `record` (`--obligation T2:scripts/**,tests/test_x.py`). Interseção com caminhos divergentes → `affected`. Sem declaração → `affected` (conservador). `unaffected` é informativo: a decisão de reuso continua das regras de `pr-audit`/`post-pr-audit` (nunca reutilizar através de mudanças de runtime/build/dependência/teste relevantes) e o gate final obrigatório sempre roda no candidato final.

### D8. Integração ao workflow (prosa)
- TEST_STRATEGY: coluna `Evidence` na matriz (`evidence_id` + estado); seção curta "Evidence handoff" com estados, transporte, retenção e precedência dos gates.
- apply-issue: registrar as execuções focais e a suíte final via `workflow-evidence record`, exportar/publicar conforme o runtime, listar IDs no handoff.
- prepare-pr / pr-audit / post-pr-audit: `workflow-evidence verify` no candidato; reportar estado por obrigação; `metadata_only`/`incomplete`/`ambiguous`/`not_applicable` = não verificado; reexecutar apenas obrigações em `recovery`.
- address-pr-review: após correção, verificar e reexecutar só o afetado.
- milestone-orchestrator: transportar `evidence_id`/pacote no handoff do worker; `workflow-event --evidence evidence:<id>`.
- update-ai-workflow: incluir `workflow_evidence.py` como arquivo companheiro.
- Quando o helper não estiver instalado, manter o comportamento atual em prosa e marcar a prova como não verificada pelo helper (sem bloquear projetos que não o instalaram).

### D9. Fronteira M2T (contract-handoff design-review)
O registro M2T (#12) ainda não existe nem tem schema congelado. Esta mudança não lê nem mapeia campos M2T. `producer` fica reservado com a forma mínima `{name, schema, record_ref, digest}` que o adaptador futuro preencherá após `CONTRACT FROZEN`; até lá vale null. O follow-up (adaptador M2T + teste de contrato) fica CONTRACT_BLOCKED em M2T #12. Requisitos do consumidor que o produtor precisa cobrir (insumo para M2T #12, não contrato):

| Cenário do consumidor | Operação/campos necessários do produtor | Estado/erro | Ponto de validação | Evidência / lacuna |
|---|---|---|---|---|
| Ligar execução ao código testado | ID de execução, repositório, HEAD, fingerprint incl. alterações locais | ambíguo se mudou durante a execução | captura no host M2T | GAP — M2T #12 aberto, sem PR (`m2t@eb40523`) |
| Distinguir sucesso/falha/interrupção/desconhecido | fase, estado terminal verificado, exit code original, horários | incompleto/desconhecido explícito | reconciliação do runner | GAP |
| Verificar relatórios | lista de artefatos com presença e checksum, exportação portátil | ausente explícito | exportação M2T | GAP |
| Consultar de outro runtime | consulta estruturada versionada por ID / pacote exportado | schema desconhecido → rejeitar | leitura pelo consumidor | GAP |

Resultado: `CONTRACT GAP — integração nativa M2T` (apenas esse cenário). Caminho genérico não depende do produtor: `CONTRACT DESIGN READY` não se aplica porque não há contrato a consumir nesta mudança.

### D10. Retrocompatibilidade de métricas
`workflow-event` acrescenta o padrão `^evidence:ev-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}$` à validação de `--evidence`; nada mais muda em `workflow_metrics.py`/`workflow-report` (strings continuam strings, `schema_version` continua 1). Edição de uma linha para minimizar conflito com #32.

## Matriz requisito → código → teste (TEST_STRATEGY)

| ID | Critério de aceite / risco | Código | Camada | Teste (novo/existente) |
|---|---|---|---|---|
| T1 | AC1: outra sessão/diretório verifica sem repetir teste | armazenamento comum, `export`/`import`, `verify` | Fixture helper (Git temporário + `git worktree add`; segundo clone) | novo `test_record_verified_from_other_worktree`, `test_bundle_import_in_other_clone` |
| T2 | AC2: mesmo HEAD, diff diferente; mudança posterior de código | `code_fingerprint`, `verify` | Unit/helper | novo `test_same_head_different_diff_is_stale`, `test_later_commit_is_stale`, `test_ignored_config_change_is_stale` |
| T2b | AC2: mudança concorrente | fingerprint antes/depois | Helper (comando que altera arquivo) | novo `test_concurrent_change_is_ambiguous` |
| T3 | AC4: log ausente / checksum divergente / relatório ausente / interrompido | `verify` estados | Unit/helper | novo `test_missing_log_incomplete`, `test_tampered_bundle_incomplete`, `test_missing_report_incomplete`, `test_interrupted_incomplete` |
| T3b | AC4: só metadados | `publish`, `verify --from-github` | Helper com `gh` falso | novo `test_published_metadata_only_without_logs` (também prova ausência de log no comentário e idempotência) |
| T4 | Reexecução justificada só da obrigação afetada; gates respeitados | invalidação D7, `required_gate` | Simulação de handoff | novo `test_change_affects_only_one_obligation`, `test_required_gate_always_affected` |
| AC3 | Revisor liga prova a requisito e seleção | `obligations`, `list --obligation` | Helper | novo `test_list_by_obligation_shows_selection`; `test_record_requires_obligation` |
| AC5 | Histórico/CI não substitui gate local | `register-hosted`, D6 regra 4 | Unit | novo `test_hosted_result_not_applicable_for_required_gate` |
| T5 | AC6: formato anterior de métricas legível | `workflow-event` regex | Testes de métricas | existente `test_parse_hidden_run_record`, `test_event_cli_updates_one_github_comment_for_a_run` reutilizados; novo `test_legacy_record_report_unchanged`, `test_event_accepts_evidence_reference_and_rejects_path` |
| R1 | Sensível: segredo em argv, env | mascaramento D5 | Unit | novo `test_secret_argv_masked`, `test_env_values_not_recorded` |
| R2 | Pacote malicioso (path traversal) | `import` | Unit | novo `test_import_rejects_path_traversal` |
| R3 | Extensões preservadas (#32/#34) | load/export | Unit | novo `test_unknown_extensions_preserved` |
| R4 | Exit code propagado / registro em falha | `record` | Helper | novo `test_failing_command_recorded_and_exit_propagated`, `test_junit_counts_extracted` |
| R5 | Retenção explícita | `prune` | Helper | novo `test_prune_dry_run_by_default` |
| AC6b | Distribuição sincronizada | `scripts/sync-plugin` | Check de pacote | `scripts/sync-plugin` + `git diff --exit-code` após regenerar; `test -x plugins/my-ai-skills/scripts/workflow-evidence` |

Comandos: foco `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_workflow_evidence -v`; gate final `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`; `openspec validate issue-31-test-evidence-handoff --strict`. Pré-requisitos: Python 3.10+, `git` ≥ 2.25 (worktree); sem serviços externos; `gh` sempre falso nos testes.

## Arquivos esperados

Novos: `scripts/workflow-evidence`, `scripts/workflow_evidence.py`, `tests/test_workflow_evidence.py`.
Alterados: `scripts/workflow-event`, `scripts/sync-plugin`, `tests/test_workflow_metrics.py`, `protocol/TEST_STRATEGY.md`, `protocol/AI_WORKFLOW.md`, `skills/apply-issue/SKILL.md`, `skills/prepare-pr/SKILL.md`, `skills/pr-audit/SKILL.md`, `skills/post-pr-audit/SKILL.md`, `skills/address-pr-review/SKILL.md`, `skills/milestone-orchestrator/SKILL.md`, `skills/update-ai-workflow/SKILL.md`, `README.md`, `README.en.md`.
Gerados por `scripts/sync-plugin` (não editar à mão): `skills/*/references/TEST_STRATEGY.md`, `skills/*/references/AI_WORKFLOW.md`, `plugins/my-ai-skills/**` (inclui `scripts/workflow-evidence`, `scripts/workflow_evidence.py`).
Closeout OpenSpec: `openspec/changes/archive/*-issue-31-test-evidence-handoff/**`, `openspec/specs/test-evidence/spec.md`, `openspec/specs/workflow-metrics/spec.md`.
Fora: `scripts/workflow_metrics.py` e `scripts/workflow-report` não devem mudar.

## Risks / Trade-offs

- [Outro runtime sem acesso ao diretório Git comum nem pacote] → estado `metadata_only` explícito, recuperação = importar pacote ou reexecutar a obrigação; nunca aprovação implícita.
- [Custo de hash em diffs grandes] → só caminhos alterados e configs declaradas; sem cópia da árvore.
- [Mascaramento incompleto de segredos] → logs nunca publicados; argv mascarado por padrões conhecidos; documentação proíbe segredos em argv.
- [`unaffected` usado para pular reexecução indevida] → informativo; `required_gate` sempre `affected`; regras de reuso de `pr-audit`/`post-pr-audit` prevalecem.
- [Conflito com #32 em `workflow-event`] → alteração de uma linha de validação; #32 deve rebasear e manter o padrão `evidence:`.
- [Conflito com #33 em `TEST_STRATEGY.md`] → coluna da matriz + seção própria "Evidence handoff"; #33 altera seções de planejamento/retomada.
- [Bifurcação por #34] → #34 usa `extensions.attempts` / `correlation`; não cria outro formato.
- [Fingerprint duplicado por #35] → #35 deve importar `code_fingerprint` de `workflow_evidence.py`.

## Migration Plan

Aditivo: registros de run antigos continuam válidos; projetos sem o novo helper seguem o comportamento em prosa. Rollback: remover o helper e a linha de validação; registros locais em `.git/my-ai-skills/evidence` podem ser apagados com `prune` sem afetar o repositório.

## Open Questions

Nenhuma que altere specs/abordagem. A forma final do bloco `producer` será definida no follow-up após `CONTRACT FROZEN` de M2T #12.
