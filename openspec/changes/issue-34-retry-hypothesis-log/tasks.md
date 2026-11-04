# Tasks

## 0. Entrada do Apply

- [ ] 0.1 Aguardar os merges na ordem #35 → #31 → #32 → #33; **não iniciar Apply** antes de todos. Rebasear a branch em `origin/main`, confirmar as quatro mudanças mergeadas e inspecionar os contratos efetivos: #35 `sys.dont_write_bytecode` + teste de helpers, #31 `evidence:<evidence_id>`/`obligations[].id` e linhas Validation, #32 enum de razões de espera, #33 seção de pre-flight. Conferir as áreas disjuntas de D5/R9 antes de editar; se incompatíveis, revisar/validar o OpenSpec exato antes do Apply. Registrar SHA da base e reconciliação no handoff.

## 1. Verificador do registro de tentativas

- [ ] 1.1 Criar `scripts/attempt_log.py` (stdlib) com parse do bloco ` ```attempt-log ` (Markdown ou JSON puro), agrupamento por (obrigação, assinatura normalizada) e as regras `E_FIELD`, `E_EVIDENCE_REF` (referências `evidence:ev-…`/URL GitHub/SHA, rejeição de caminhos em evidência de execução; `path#Lnn` relativo só em citações), `E_RETRY_LIMIT`, `E_NO_NEW_EVIDENCE`, `E_DIAG_INCOMPLETE`, `E_FOCUS` do design D4; verificar com `tests/test_attempt_log.py` (`test_evidence_ref_rejects_paths`, T1, agrupamento, hipótese repetida, T4) e fixtures `t1_*`, `t4_*`
- [ ] 1.2 Adicionar regras `E_CLAIM_ANCESTOR`, `E_CLAIM_INCOMPLETE`, `E_REPLAN_BASIS` e o cálculo `replan_required`; verificar com fixtures `t2_group_vs_field.json`, `t3_replan_with_basis.json` e casos negativos
- [ ] 1.3 Adicionar modo `--final` com `E_UNRESOLVED`, `E_WEAKENED` e `E_BLOCKER` + mapeamento `blocker_state` (`BLOCKED`/`RESOURCE_QUEUED`/`NEEDS_INPUT`/`NEEDS_REPLAN`) e `wait_reason` compatível (`environment`/`dependency`/`external`, `runtime_capacity`, `owner_input`); verificar com fixtures `final_unresolved.json`, `blockers.json` e `test_blocker_classification`
- [ ] 1.4 Criar CLI `scripts/attempt-log check <arquivo> [--final]` (0755, saída JSON, exit 0/1/2), definindo `sys.dont_write_bytecode = True` **antes** de importar `attempt_log.py`; provar exit codes via subprocess e ausência de bytecode sem variável de ambiente com o `test_helpers_do_not_write_bytecode` de #35 (descoberta automática pela lista de `sync-plugin`). Manter `tests/test_workflow_metrics.py` verde.

## 2. Protocolo e skills

- [ ] 2.1 Estender **apenas** "Implement and diagnose" em `protocol/TEST_STRATEGY.md` (preservar coluna/seção de evidência de #31 e pre-flight de #33) com formato do bloco único, `obligation` = ID `obligations[].id`, `evidence[]` = `evidence:<evidence_id>` quando registrado por #31, senão URL GitHub/SHA, citações `path#Lnn` só em código/definição, rejeição de caminhos absolutos/temporários, chave de grupo, diagnóstico, alternativa simples, foco, contradição, replan com fundamento, não-aprovação e bloqueio com razão de espera de #32; citar `scripts/attempt-log` e conferir frase por requisito da spec.
- [ ] 2.2 Atualizar **apenas** o parágrafo "On failure…" de `skills/apply-issue/SKILL.md` para registrar o bloco, rodar o verificador antes da 3ª tentativa e antes de declarar contradição/bloqueio, exigir prova de campo e reclassificar antes de trocar de camada; preservar as seções de #35/#33 e o parágrafo "Before commit…" de #31; verificar por leitura.
- [ ] 2.3 Atualizar `skills/prepare-pr/SKILL.md` e **acrescentar**, sem reestruturar Validation em `templates/pull-request.md`, o bloco opcional `attempt-log` **após** as linhas de obrigação `PASS|FAIL|NOT RUN: <obligation> — evidence:<id> (<verify state>)` de #31; exigir `attempt-log check --final` quando houver falha repetida, violação ⇒ `NOT READY FOR PR`; verificar por leitura.
- [ ] 2.4 Atualizar **apenas** a linha "Exceptional states" de `skills/milestone-orchestrator/SKILL.md` com classificação técnico/capacidade/decisão e mapeamento estado/razão de espera D4, preservando "Durable handoff" (#31), "Workflow timing instrumentation" (#32) e "Worktree lifecycle" (#35); verificar por leitura.
- [ ] 2.5 Atualizar `protocol/AI_WORKFLOW.md` (Proportionate test coverage), `skills/update-ai-workflow/SKILL.md` (companheiro obrigatório `attempt_log.py`) e `README.md`/`README.en.md` em paridade: parágrafo de cobertura, lista/tabela de scripts auxiliares, linhas de `cp` de CLI e módulo, `chmod` da CLI e verificações `test -x/-f` respectivas; verificar os exemplos de instalação por leitura/`grep -n attempt-log README.md README.en.md`.

## 3. Distribuição e verificação integrada

- [ ] 3.1 Acrescentar entrada própria `attempt-log` ao loop de helpers em `scripts/sync-plugin` e linha própria `install -m 0644` para `attempt_log.py` (preservando entradas de #35/#31/#33); executar `scripts/sync-plugin` **após o rebase final** e verificar que `skills/*/references/` e `plugins/my-ai-skills/` refletem as fontes, sem merge manual de cópias (`scripts/sync-plugin && git diff --exit-code -- plugins/ skills/*/references/` após a primeira regeneração; segunda execução idempotente).
- [ ] 3.2 Rodar a suíte completa `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` e `openspec validate issue-34-retry-hypothesis-log --strict`; rodar o teste de bytecode de #35 **sem** `PYTHONDONTWRITEBYTECODE` para a CLI nova, conferir a matriz D6 cenário a cenário, inspecionar diff/escopo e registrar PASS/FAIL/NOT RUN no handoff.

## Workflow follow-up

- Arquivar a change na branch da issue após verificação e validação estrita; inspecionar `openspec/specs/retry-diagnosis/spec.md` sincronizado.
- Seguir para `prepare-pr`, `pr-audit` e `post-pr-audit` (merge_mode auto-if-green).
