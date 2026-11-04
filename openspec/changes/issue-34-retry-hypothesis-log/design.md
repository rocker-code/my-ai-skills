# Design

## Context

Ver proposal.md — Why. Estado atual relevante (main @ `5825a9c`):

- `protocol/TEST_STRATEGY.md` ("Implement and diagnose") é a fonte única da regra de duas tentativas; é empacotado por `scripts/sync-plugin` em `skills/{implement-issue,openspec-workflow,apply-issue,prepare-pr,pr-audit,post-pr-audit,address-pr-review,milestone-orchestrator}/references/TEST_STRATEGY.md` e espelhado em `plugins/my-ai-skills/`.
- `skills/apply-issue/SKILL.md` ("Integration test feedback loop") já define as classes de falha `environment/bootstrap`, `fixture/isolation`, `implementation`, `assertion/contract`, `intermittent`.
- `skills/milestone-orchestrator/SKILL.md` já define os estados `NEEDS_INPUT`, `NEEDS_REPLAN`, `BLOCKED`, `RESOURCE_QUEUED`; `scripts/workflow-event` já define razões de espera (`owner_input`, `runtime_capacity`, `external`…).
- Helpers são Python stdlib (`scripts/workflow_metrics.py` + CLI fino `scripts/workflow-event`) com `tests/` em `unittest`.

## Goals / Non-Goals

**Goals:**
- Formato curto e único do registro de tentativas, documentado em `TEST_STRATEGY.md` e embutido no handoff existente.
- Verificador determinístico (`scripts/attempt-log check`) que torna os critérios de aceite testáveis por fixtures.

**Non-Goals:**
- Não executar testes, nem capturar logs/HEAD/fingerprint (pertence a #31), nem observar estado de processo/runtime (pertence a #32).
- Não alterar `scripts/workflow-event`/`workflow_metrics.py` nem o schema do run record.
- Não criar nova etapa, aprovação, comando de usuário ou documento de protocolo separado.
- Não interpretar semanticamente XML/config do consumidor; o verificador valida a estrutura da alegação (caminhos citados), não o domínio Magento.

## Decisions

### D1 — Dependência de #31/#32: independente, com ponto de extensão (dependência soft)

**Escolha:** planejar contra a `main` atual, sem dependência hard de #31 ou #32.

**Razões:**
1. A issue declara reuso "quando disponíveis" e que o diagnóstico "pode avançar independentemente".
2. Responsabilidades disjuntas: #31 é dono dos **fatos de execução** (comando, HEAD, fingerprint, exit code, relatórios); #32 é dono do **estado de execução** (rodando/esperando/desconhecido). #34 registra **raciocínio diagnóstico** (assinatura, obrigação, hipótese, classificação, alegação de contrato, bloqueio) — nenhum dos dois o define.
3. Para não criar sistema paralelo, o registro de tentativas **não duplica** nenhum campo de #31/#32: cada tentativa só carrega `evidence` — lista de referências opacas (URL GitHub, SHA, `path#Lnn`, ou identificador de registro de evidência). O bloqueio reutiliza estados/razões já existentes do orquestrador.
4. Nenhuma das branches de #31/#32 estava publicada na hora do planejamento; travar #34 nelas não traz contrato verificável.

**Ponto de extensão:** o verificador aceita qualquer string não vazia em `evidence[]` e expõe uma função de resolução de referência injetável (padrão: aceita). **Regra de Apply:** antes de `/opsx-apply`, rebasear em `origin/main`; se #31 estiver mergeado, `TEST_STRATEGY.md` MUST apontar `evidence[]` para os identificadores do registro de evidência de #31 (sem copiar seus campos) e o texto de `prepare-pr` MUST reutilizar o mesmo bloco de validação de #31; se #32 estiver mergeado, o mapeamento de bloqueio MUST usar seus estados/razões se ele os renomear. Isso é adaptação textual dentro do contrato validado, não mudança material. Se #31/#32 mudarem o handoff de forma incompatível (ex.: removerem a seção de validação), aplicar o gate de revisão OpenSpec.

**Alternativa rejeitada:** dependência hard de #31 — atrasaria #34 sem ganho, pois #34 só precisa de referências opacas; e criaria acoplamento ao produtor M2T, que a issue explicitamente dispensa.

### D2 — Onde vive o registro

Bloco cercado ` ```attempt-log ` contendo JSON, dentro da seção **Validation** do handoff/PR (`templates/pull-request.md`) ou do comentário de handoff do Apply. JSON (stdlib) em vez de YAML (exigiria PyYAML). O bloco é obrigatório apenas quando houve falha repetida. Alternativa rejeitada: eventos novos em `workflow-event` — o run record tem writer único (orquestrador), é editado por #31/#32 e não é lido pelo revisor do PR.

### D3 — Formato (resumo; texto normativo em `TEST_STRATEGY.md`)

```json
{"attempt_log": 1, "entries": [
  {"kind": "attempt", "seq": 1, "obligation": "R2/T1", "target": "AddressTest::testSave",
   "signature": "validator read country=US", "class": "fixture/isolation",
   "hypothesis": "override de config no escopo default", "change": "n/a (primeira)",
   "change_target": "fixture", "result": "fail", "evidence": ["https://github.com/.../runs/1"]},
  {"kind": "diagnosis", "seq": 3, "group": {"obligation": "R2/T1", "signature": "validator read country=US"},
   "class": "fixture/isolation", "checked": {"phase": "...", "scope": "...", "lifecycle": "...", "consumers": "..."},
   "runtime_proof": ["..."] , "simplest_alternative": "fixture BR", "choice_rationale": "...",
   "next_hypothesis": "fixture BR elimina dependência do escopo"},
  {"kind": "contract_claim", "seq": 5, "definition_ref": "etc/adminhtml/system.xml#L40",
   "cited_path": "section/general/group/locale", "field_path": "section/general/group/locale/field/timezone",
   "scope": "store", "observation": "...", "inference": "...", "confirmation": "...", "inheritance_proof": null},
  {"kind": "replan", "seq": 6, "basis": ["claim:5"], "openspec_revision": "requested"},
  {"kind": "blocker", "seq": 7, "type": "technical|capacity|business_decision", "evidence": ["..."],
   "diagnosis": "seq:3", "options": [], "impact": "", "researchable": false},
  {"kind": "resolution", "group": {...}, "outcome": "passed|blocked", "via_seq": 4}
]}
```

- **Chave de grupo** = (`obligation`, `normalize(signature)`), onde `normalize` = minúsculas + espaços colapsados. `target`, comando e filtro ficam fora da chave (requisito de agrupamento). O executor escreve a assinatura sem partes voláteis (timestamps, caminhos temporários); o verificador não tenta inferir isso.
- **Progresso**: `result` ∈ {`pass`, `fail`}. Uma tentativa `fail` com assinatura diferente na mesma obrigação abre novo grupo (progresso do anterior).
- `class` ∈ classes de `apply-issue`, agrupadas nas três de TEST_STRATEGY (aplicação: `implementation`; assertion/fixture: `assertion/contract`, `fixture/isolation`; ambiente/setup: `environment/bootstrap`) + `intermittent`.
- `change_target` ∈ {`application`, `test`, `fixture`, `environment`, `plan`, `none`}.

### D4 — Regras do verificador (códigos estáveis para testes)

| Código | Regra | Critério/Cenário |
|---|---|---|
| `E_FIELD` | campo obrigatório ausente/vazio | registro |
| `E_RETRY_LIMIT` | 3ª+ tentativa `fail`-group sem `diagnosis` de `seq` menor após a 2ª falha | AC1, T1 |
| `E_NO_NEW_EVIDENCE` | tentativa ≥2 com `hypothesis` normalizada já usada no grupo e sem `evidence` nova (refs não vistas antes no grupo) | AC2 |
| `E_DIAG_INCOMPLETE` | diagnóstico sem `checked.{phase,scope,lifecycle,consumers}`, `runtime_proof` (ou `"not_applicable: <motivo>"`), `simplest_alternative`, `choice_rationale`, `next_hypothesis` | T1 |
| `E_FOCUS` | grupo classificado `environment/bootstrap` e tentativa seguinte com `change_target=application` sem diagnóstico que reclassifique | T4 |
| `E_CLAIM_ANCESTOR` | `cited_path` é ancestral estrito de `field_path` e `inheritance_proof` vazio | AC3, T2 |
| `E_CLAIM_INCOMPLETE` | alegação sem `definition_ref`/`scope`/`observation`/`inference`/`confirmation` | AC3 |
| `E_REPLAN_BASIS` | `replan` cujo `basis` não aponta alegação aceita nem evidência nova | AC4, T3 |
| `E_UNRESOLVED` | (modo `--final`) grupo cuja última tentativa é `fail` sem `resolution` `blocked` válida | AC5 |
| `E_WEAKENED` | `resolution.outcome` fora de {`passed`,`blocked`} (ex.: `skipped`, `assertion_relaxed`) ou `passed` sem tentativa `pass` referenciada | AC5 |
| `E_BLOCKER` | `type` inválido; `business_decision` sem ≥2 `options` e `impact`, ou com `researchable=true`; `technical` sem `diagnosis`/`evidence`; `capacity` sem `missing_capability` | AC6 |

Saída: JSON `{ok, groups:[{key, attempts, status: open|resolved|blocked, replan_required}], violations:[{code, seq, message}], blocker_state}`; exit 0 se `ok`, 1 se violações, 2 para entrada malformada. `blocker_state` mapeia `technical→BLOCKED`, `capacity→RESOURCE_QUEUED`, `business_decision→NEEDS_INPUT`; `replan` válido → `NEEDS_REPLAN`.

### D5 — Integração nas skills (sem nova etapa)

- `TEST_STRATEGY.md`: estende o parágrafo de diagnóstico com o formato, as regras e o comando; continua sendo a única fonte (bundled).
- `apply-issue`: na seção de falhas, registrar o bloco, rodar `attempt-log check` antes da 3ª tentativa e de declarar contradição/bloqueio; exigir prova de campo; reclassificar antes de mudar de camada.
- `prepare-pr`: incluir o bloco no Validation do PR quando houver falha repetida e rodar `attempt-log check --final`; violação = `NOT READY FOR PR`.
- `milestone-orchestrator`: relato de bloqueio usa a classificação e o mapeamento de estados; fatos pesquisáveis são investigados pelo worker.
- `AI_WORKFLOW.md` linha de test coverage e READMEs: uma frase cada, em paridade.
- `pr-audit`/`post-pr-audit`/`address-pr-review` recebem a regra via `references/TEST_STRATEGY.md` regenerado — sem edição direta.

### D6 — Matriz requisito → código → teste (risk-based, TEST_STRATEGY)

| Cenário | Critério/risco | Camada | Prova (nova/existente) |
|---|---|---|---|
| T1 override sem efeito ×2 → 3ª sem diagnóstico | AC1 | Unit (fixture de execução) | novo `test_t1_retry_limit_requires_diagnosis` + `t1_override_no_effect.json` |
| T1 com diagnóstico completo + hipótese nova (fixture BR) passa | AC1, AC2, alternativa simples | Unit | novo `test_t1_diagnosed_alternative_accepted` |
| Comando/filtro renomeado mantém grupo | agrupamento | Unit | novo `test_grouping_ignores_command_and_target` |
| Hipótese repetida sem evidência | AC2 | Unit | novo `test_repeated_hypothesis_rejected` |
| T2 grupo × campo | AC3 | Unit (fixture de revisão) | novo `test_t2_group_vs_field_claim_rejected` + `t2_group_vs_field.json` |
| T3 alegação aceita → replan | AC4 | Unit (simulação handoff) | novo `test_t3_replan_with_basis` / `test_replan_without_basis_rejected` |
| T4 falha de serviço → muda app | foco | Unit (fixture de execução) | novo `test_t4_environment_focus` + `t4_service_before_phpunit.json` |
| Grupo pendente no `--final`; resolução por skip | AC5 | Unit | novo `test_final_unresolved_not_approval`, `test_weakened_resolution_rejected` |
| Bloqueios 3 tipos + pesquisável | AC6 | Unit | novo `test_blocker_classification` |
| CLI exit codes e JSON | integração do helper | Integração leve (subprocess) | novo `test_cli_check_exit_codes` |
| Distribuição | sync | Check | `scripts/sync-plugin` + `git diff --exit-code plugins/ skills/*/references/` |
| Métricas existentes | regressão | Unit | existente `tests/test_workflow_metrics.py` |

Sem risco de pagamento/autorização/dados; profundidade normal. Comando local: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`.

### D7 — Arquivos esperados no Apply

Criados: `scripts/attempt_log.py`, `scripts/attempt-log` (0755), `tests/test_attempt_log.py`, `tests/fixtures/attempt_log/{t1_override_no_effect,t1_diagnosed_alternative,t2_group_vs_field,t3_replan_with_basis,t4_service_before_phpunit,final_unresolved,blockers}.json`, `plugins/my-ai-skills/scripts/{attempt-log,attempt_log.py}` (gerados).
Editados: `protocol/TEST_STRATEGY.md`, `protocol/AI_WORKFLOW.md`, `skills/apply-issue/SKILL.md`, `skills/prepare-pr/SKILL.md`, `skills/milestone-orchestrator/SKILL.md`, `templates/pull-request.md`, `scripts/sync-plugin`, `README.md`, `README.en.md`.
Regenerados (via `scripts/sync-plugin`, nunca à mão): `skills/*/references/TEST_STRATEGY.md`, `skills/{milestone-orchestrator,milestone-progress}/references/AI_WORKFLOW.md`, `skills/prepare-pr/references/pull-request.md`, `plugins/my-ai-skills/**` correspondentes.
Arquivo OpenSpec: archive em `openspec/changes/archive/*-issue-34-retry-hypothesis-log/` e `openspec/specs/retry-diagnosis/spec.md`.

## Risks / Trade-offs

- [Assinatura escrita pelo agente pode variar artificialmente e reiniciar contagem] → `TEST_STRATEGY` exige assinatura = classe de erro + primeira mensagem relevante sem partes voláteis; revisor confere; normalização mínima evita falsos agrupamentos.
- [Verificador estrutural não prova semântica do XML] → o T2 é detectado pela relação ancestral entre caminhos citados; a confirmação da leitura continua obrigatória em prosa e revisada.
- [Conflito textual com #33 (TEST_STRATEGY/apply-issue) e #31 (prepare-pr/template)] → Apply serializado após eles; rebase e reconciliação textual antes de `/opsx-apply`; seções editadas são parágrafos distintos ("Implement and diagnose", "Integration test feedback loop").
- [Burocracia em falhas triviais] → bloco só obrigatório com falha repetida; uma tentativa única não exige registro.
- [`sync-plugin` reescreve todas as referências] → rodar após rebase final para não reverter mudanças de siblings.

## Migration Plan

Aditivo: handoffs sem bloco continuam válidos; sem mudança de schema de métricas. Rollback = reverter o PR.
