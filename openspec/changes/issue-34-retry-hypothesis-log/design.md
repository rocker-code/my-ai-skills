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

### D1 — Pré-requisito serial de Apply, independente do schema de #31 (ruling R2)

**Escolha:** #35, #31, #32 e #33 **mergeados são pré-requisito operacional** deste Apply na ordem serial (#35 → #31 → #32 → #33 → #34); a tarefa 0.1 para se faltarem. Isso não cria dependência do **schema** do manifesto de #31: #34 não o lê, copia ou valida, nem depende de M2T. A capacidade de diagnóstico, já definida pela issue como independente do produtor M2T, compõe com os artefatos mergeados por referências portáveis e IDs de obrigação.

**Razões:**
1. A issue declara reuso "quando disponíveis" e que o diagnóstico "pode avançar independentemente" do produtor M2T; a revisão em lote fixou a ordem de integração com as mudanças deste repositório.
2. Responsabilidades disjuntas: #31 é dono dos **fatos de execução** (manifesto de evidência); #32 do **estado/correlação de execução** e do enum de razões de espera; #34 do **raciocínio diagnóstico** (assinatura, obrigação, hipótese, classificação, alegação de contrato, bloqueio) e da classificação de bloqueios.
3. Uma tentativa/grupo abrange várias execuções; por isso o registro de raciocínio não cabe no manifesto por execução de #31.
4. Os planos de #31 e #32 estão publicados e a revisão em lote (issuecomment-6621848490) fixou a composição abaixo; não há necessidade de acoplar o verificador ao formato do manifesto.

**Composição (normativa):**
- O bloco cercado ` ```attempt-log ` é o **único** registro de raciocínio de tentativas; vive na seção Validation existente do PR/handoff do Apply. #31 não reserva `extensions.attempts`; nada de #34 entra no manifesto.
- `evidence[]` de uma tentativa executada = `evidence:<evidence_id>` quando `workflow-evidence` (#31) registrou a execução; caso contrário URL GitHub ou SHA. `path#Lnn` relativo ao repositório é permitido **apenas** em citações de código/definição (`definition_ref`, `runtime_proof`, `inheritance_proof`), nunca como evidência de execução. Caminhos absolutos ou temporários (`/tmp/…`, `/home/…`) nunca são evidência (`E_EVIDENCE_REF`).
- `obligation` usa o mesmo ID da linha da matriz de validação, compartilhado com o handoff de #31; o verificador não consulta os campos do manifesto.
- O verificador trata referências como strings com validação sintática; nunca abre manifestos nem resolve `evidence:` (independente do schema de #31 e de M2T).

**Alternativa rejeitada:** gravar tentativas em `extensions` do manifesto ou resolver `evidence:` dentro do verificador — acoplaria #34 ao schema de #31 e fragmentaria um grupo entre manifestos.

### D2 — Onde vive o registro

Bloco cercado ` ```attempt-log ` contendo JSON, dentro da seção **Validation** do handoff/PR (`templates/pull-request.md`) ou do comentário de handoff do Apply, **depois** das linhas de obrigação de #31 (`PASS|FAIL|NOT RUN: <obligation> — evidence:<id> (<verify state>)`), sem reestruturar a seção (R9). JSON (stdlib) em vez de YAML (exigiria PyYAML). O bloco é obrigatório apenas quando houve falha repetida. Alternativa rejeitada: eventos novos em `workflow-event` — o run record tem writer único (orquestrador), é editado por #31/#32 e não é lido pelo revisor do PR.

### D3 — Formato (resumo; texto normativo em `TEST_STRATEGY.md`)

```json
{"attempt_log": 1, "entries": [
  {"kind": "attempt", "seq": 1, "obligation": "R2/T1", "target": "AddressTest::testSave",
    "signature": "validator read country=US", "class": "fixture/isolation",
    "hypothesis": "override de config no escopo default", "change": "n/a (primeira)",
    "change_target": "fixture", "observed_effect": "validador ainda lê US no escopo default",
    "result": "fail", "evidence": ["evidence:ev-20261104T120000Z-1a2b3c4d"]},
  {"kind": "diagnosis", "seq": 3, "group": {"obligation": "R2/T1", "signature": "validator read country=US"},
   "class": "fixture/isolation", "checked": {"phase": "...", "scope": "...", "lifecycle": "...", "consumers": "..."},
   "runtime_proof": ["evidence:ev-20261104T121500Z-5e6f7a8b", "app/code/Vendor/Module/etc/config.xml#L12"], "simplest_alternative": "fixture BR", "choice_rationale": "...",
   "next_hypothesis": "fixture BR elimina dependência do escopo"},
  {"kind": "contract_claim", "seq": 5, "definition_ref": "etc/adminhtml/system.xml#L40",
   "cited_path": "section/general/group/locale", "field_path": "section/general/group/locale/field/timezone",
   "scope": "store", "observation": "...", "inference": "...", "confirmation": "...", "inheritance_proof": null},
  {"kind": "replan", "seq": 6, "basis": ["claim:5"], "openspec_revision": "requested"},
   {"kind": "blocker", "seq": 7, "group": {"obligation": "R2/T1", "signature": "validator read country=US"}, "type": "technical", "wait_reason": "environment", "evidence": ["https://github.com/owner/repo/actions/runs/123"],
    "diagnosis": "seq:3", "options": [], "impact": "", "researchable": false},
   {"kind": "resolution", "group": {...}, "outcome": "blocked", "via_seq": 7}
]}
```

- **Chave de grupo** = (`obligation`, `normalize(signature)`), onde `normalize` = minúsculas + espaços colapsados. `target`, comando e filtro ficam fora da chave (requisito de agrupamento). O executor escreve a assinatura sem partes voláteis (timestamps, caminhos temporários); o verificador não tenta inferir isso.
- **Progresso**: `result` ∈ {`pass`, `fail`}. Uma tentativa `fail` com assinatura diferente na mesma obrigação abre novo episódio (progresso do anterior), mantendo a chave de grupo para comparação. Ver D8 para lifecycle e gate final. `observed_effect` registra o efeito factual da execução (incluindo valor/escopo/fase de runtime quando relevantes), não o ID nem a interpretação da evidência. Para comparar textos, `normalize` = minúsculas + espaços colapsados; diferenças apenas de caixa/espaço não constituem mudança. Uma nova referência não prova efeito diferente por si só.
- **Hipótese repetida**: a tentativa após a primeira do grupo tem `change` e `observed_effect`. Quando `normalize(hypothesis)` já apareceu no grupo, exige `observed_change` não vazio descrevendo concretamente a diferença entre a observação anterior dessa hipótese e a atual, `evidence[]` com ao menos uma referência ainda não usada no grupo que sustente essa diferença e `normalize(observed_effect)` diferente do efeito daquela tentativa anterior. A mesma assinatura de grupo pode coexistir com efeito observado diferente (por exemplo, valor ou fase efetiva mudou sem eliminar a falha), portanto não rejeitar só porque a assinatura é igual. Se assinatura e efeito permanecerem iguais, hipótese repetida não passa apenas por novo ID; hipótese genuinamente nova pode ser testada mesmo com o mesmo efeito. O verificador confere presença, refs e comparação normalizada; o revisor confere que o resumo e a evidência realmente sustentam a mudança, sem abrir o manifesto de #31.
- **Terceira tentativa**: contar `fail` consecutivos no episódio da chave sem progresso; uma assinatura distinta encerra o episódio, e retorno posterior à chave inicia episódio novo. Assim que houver duas falhas consecutivas no episódio, qualquer tentativa seguinte nele exige `diagnosis` completa posterior à 2ª falha e anterior à tentativa, inclusive uma declarada `pass`; o resultado posterior não cura retroativamente a falta de diagnóstico. Um `pass` zera a sequência de falhas na obrigação.
- `class` ∈ classes de `apply-issue`, agrupadas nas três de TEST_STRATEGY (aplicação: `implementation`; assertion/fixture: `assertion/contract`, `fixture/isolation`; ambiente/setup: `environment/bootstrap`) + `intermittent`.
- `change_target` ∈ {`application`, `test`, `fixture`, `environment`, `plan`, `none`}.

### D4 — Regras do verificador (códigos estáveis para testes)

| Código | Regra | Critério/Cenário |
|---|---|---|
| `E_FIELD` | campo obrigatório ausente/vazio | registro |
| `E_EVIDENCE_REF` | item de `evidence[]` (tentativa/bloqueio) que não seja `evidence:ev-<8 dígitos>T<6 dígitos>Z-<hex8>` (referência portável de #31, sem consulta ao schema), URL `https://github.com/…` ou SHA hex 7–64; caminho absoluto/temporário ou `path#Lnn` como evidência de execução é rejeitado. Citações (`definition_ref`, `runtime_proof`, `inheritance_proof`) aceitam também `path#Lnn` relativo, nunca absoluto; `basis` de replan usa `claim:<seq>` ou referência nova de evidência | registro, R2 |
| `E_RETRY_LIMIT` | qualquer tentativa posterior a duas falhas equivalentes **no episódio ininterrupto** sem `diagnosis` completa posterior à 2ª falha e anterior à tentativa, independentemente de `result=pass|fail`; `A,A,B,A` não herda streak de A antigo | AC1, T1 |
| `E_NO_NEW_EVIDENCE` | hipótese repetida sem `observed_change` concreto, sem ref nova que sustente a mudança ou com `observed_effect` normalizado igual ao da tentativa anterior dessa hipótese; ID novo isolado não basta, efeito de fato diferente com ref nova pode passar mesmo sob assinatura igual | AC2 |
| `E_DIAG_INCOMPLETE` | diagnóstico sem `checked.{phase,scope,lifecycle,consumers}`, `runtime_proof` (ou `"not_applicable: <motivo>"`), `simplest_alternative`, `choice_rationale`, `next_hypothesis` | T1 |
| `E_FOCUS` | falha `environment/bootstrap` não resolvida na mesma obrigação e edição `application`, mesmo após tentativa intermediária; somente `pass` posterior da obrigação ou diagnóstico completo de reclassificação da falha de ambiente com prova de execução nova (não só código/ID antigo), antes da edição, limpa o guard | T4 |
| `E_CLAIM_ANCESTOR` | `cited_path` é ancestral estrito de `field_path` e `inheritance_proof` vazio | AC3, T2 |
| `E_CLAIM_INCOMPLETE` | alegação sem `definition_ref`/`scope`/`observation`/`inference`/`confirmation` | AC3 |
| `E_REPLAN_BASIS` | `replan` cujo `basis` não aponta alegação aceita nem evidência nova | AC4, T3 |
| `E_UNRESOLVED` | (modo `--final`) episódio **ativo da obrigação** cuja última tentativa é `fail` sem `resolution` `blocked` válida; episódios históricos progredidos continuam não aprovados, mas não bloqueiam sozinhos | AC5 |
| `E_WEAKENED` | `resolution.outcome` fora de {`passed`,`blocked`} (ex.: `skipped`, `assertion_relaxed`), `passed` sem `via_seq` da última tentativa `pass` do grupo (um `pass` anterior não apaga falha posterior) ou `blocked` sem `blocker` válido do mesmo grupo referenciado por `via_seq` | AC5 |
| `E_BLOCKER` | `type` inválido; `wait_reason` incompatível com o tipo (tabela R7); `business_decision` sem ≥2 `options` e `impact`, ou com `researchable=true`; `technical` sem `diagnosis`/`evidence`; `capacity` sem `missing_capability` | AC6, R7 |

Saída: JSON `{valid, ready, groups:[{key, attempts, status: open|resolved|blocked|progressed, replan_required}], violations:[{code, seq, message}], blocker_state}`. `progressed` é estado **histórico não aprovado**, não um novo `resolution.outcome`: ver D8. `valid` significa apenas estrutura/regras corretas (`violations` vazio); `ready` no `--final` significa que o episódio ativo de cada obrigação está aprovado pela última tentativa `pass` com resolução `passed` referenciando essa tentativa, sem episódio ativo pendente, bloqueado ou replan pendente. Sem `--final`, `ready=null` e exit 0/1 seguem `valid`; com `--final`, exit 0 somente se `valid && ready`, 1 se violações **ou** bloqueio/replan válido porém não aprovado, 2 para entrada malformada. Um `resolution.blocked` com `via_seq` apontando `blocker` válido do mesmo episódio preserva `valid=true`, `status=blocked`, `ready=false` e exit 1 enquanto ativo; `prepare-pr` MUST NOT tratar esse exit como aprovação. `blocker_state` reflete bloqueio **ativo** ou replan pendente, não um bloqueio histórico. A tabela R7 permanece (sem novos estados do orquestrador; enum de razões de espera pertence a #32):

| Tipo (#34) | Estado do orquestrador | Razão de espera `workflow-event` |
|---|---|---|
| `technical` | `BLOCKED` | `environment` (sandbox/serviço) ou `dependency`/`external` |
| `capacity` | `RESOURCE_QUEUED` | `runtime_capacity` |
| `business_decision` | `NEEDS_INPUT` | `owner_input` |
| `replan` aceito | `NEEDS_REPLAN` | — (rework `replan`) |

### D4b — CLI sem bytecode (R6)

`scripts/attempt-log` MUST definir `sys.dont_write_bytecode = True` antes de importar `attempt_log.py`. O `test_helpers_do_not_write_bytecode` de #35 descobre automaticamente as CLIs Python no loop/lista de instalação de `scripts/sync-plugin`; incluir `attempt-log` ali faz o teste exercitá-lo sem editar manualmente o teste (confirmar isso no Apply).

### D5 — Integração nas skills (sem nova etapa)

- `TEST_STRATEGY.md`: estende apenas a seção "Implement and diagnose" (R9; #31 adiciona coluna Evidence e "Evidence handoff" após "Review and stop"; #33 insere pré-flight antes de "Choose the proving layer") com o formato, a regra de referências de D1, as regras e o comando; continua sendo a única fonte (bundled).
- `apply-issue`: apenas o parágrafo "On failure…" (R9), registrar o bloco, rodar `attempt-log check` antes de qualquer tentativa após duas falhas (inclusive a que se espera passar) e antes de declarar contradição/bloqueio; exigir prova de campo; reclassificar antes de mudar de camada.
- `prepare-pr`/template: incluir o bloco opcional no Validation do PR, após as linhas de obrigação de #31, quando houver falha repetida e rodar `attempt-log check --final`; exit 1 por violação **ou bloqueio válido** = `NOT READY FOR PR`. Revisor distingue `valid` de `ready`, sem interpretar classificação de bloqueio como liberação.
- `milestone-orchestrator`: apenas a linha "Exceptional states" (R9) — relato de bloqueio usa a classificação e a tabela R7 de estados/razões de espera; fatos pesquisáveis são investigados pelo worker.
- `AI_WORKFLOW.md` linha de test coverage e READMEs: uma frase cada, em paridade.
- `pr-audit`/`post-pr-audit`/`address-pr-review` recebem a regra via `references/TEST_STRATEGY.md` regenerado — sem edição direta.

### D6 — Matriz requisito → código → teste (risk-based, TEST_STRATEGY)

| Cenário | Critério/risco | Camada | Prova (nova/existente) |
|---|---|---|---|
| T1 override sem efeito ×2 → 3ª sem diagnóstico | AC1 | Unit (fixture de execução) | novo `test_t1_retry_limit_requires_diagnosis` + `t1_override_no_effect.json` |
| T1 duas falhas → 3ª marcada `pass` sem diagnóstico; com diagnóstico anterior passa | AC1, vedar aprovação retroativa | Unit | novo `test_third_pass_still_requires_diagnosis` + caso positivo diagnosticado |
| T1 com diagnóstico completo + hipótese nova (fixture BR) passa | AC1, AC2, alternativa simples | Unit | novo `test_t1_diagnosed_alternative_accepted` |
| Comando/filtro renomeado mantém grupo | agrupamento | Unit | novo `test_grouping_ignores_command_and_target` |
| Hipótese repetida sem evidência | AC2 | Unit | novo `test_repeated_hypothesis_rejected` |
| Hipótese repetida, ref nova mas assinatura/efeito iguais; mudança real de efeito com resumo e ref nova | AC2, prova substantiva sem rejeição indiscriminada | Unit | novos `test_new_id_same_effect_rejected`, `test_repeated_hypothesis_changed_effect_accepted`, `test_observed_change_missing_or_uncited_rejected` |
| T2 grupo × campo | AC3 | Unit (fixture de revisão) | novo `test_t2_group_vs_field_claim_rejected` + `t2_group_vs_field.json` |
| T3 alegação aceita → replan | AC4 | Unit (simulação handoff) | novo `test_t3_replan_with_basis` / `test_replan_without_basis_rejected` |
| T4 falha de serviço → muda app | foco | Unit (fixture de execução) | novo `test_t4_environment_focus` + `t4_service_before_phpunit.json` |
| Ambiente falha → outra assinatura/classe falha → edição app | T4; intermediário não limpa guard | Unit | adicionar `test_environment_focus_intermediate_does_not_bypass` |
| Ambiente falha → mesma obrigação passa → edição app | T4; guard não bloqueia sucesso anterior | Unit | adicionar `test_environment_focus_cleared_by_pass` |
| Ambiente falha → diagnóstico reclassifica com prova nova × antiga/código isolado/incompleta → edição app | T4; prova substantiva | Unit | adicionar `test_environment_reclassification_requires_new_runtime_proof` (positivo e negativos); revisor confirma conteúdo sem abrir manifesto de #31 |
| Grupo pendente no `--final`; resolução por skip | AC5 | Unit | novo `test_final_unresolved_not_approval`, `test_weakened_resolution_rejected` |
| A falha → B diferente falha → B passa, A permanece histórico não aprovado | AC1, AC5; sucesso final após progresso sem aprovação fictícia | Unit + CLI subprocess | adicionar `test_progressed_history_final_ready` (verifica `valid=true`, `ready=true`, A=`progressed`, B=`resolved`, exit 0); `test_progressed_history_active_failure_not_ready` |
| A,A → B → A falha e depois A falha novamente | AC1; reset de episódio sem perder limite em novo streak | Unit | adicionar `test_signature_return_starts_new_episode` (sem `E_RETRY_LIMIT` na 1ª/2ª A nova; na 3ª A nova sem diagnóstico → `E_RETRY_LIMIT`) |
| `passed` de tentativa anterior seguido de `fail` | AC5, sucesso não apaga falha posterior | Unit | novo `test_old_pass_cannot_resolve_last_fail` |
| Bloqueio válido associado ao grupo no `--final` | AC5, estrutural ≠ pronto para PR | Unit + CLI subprocess | novo `test_valid_blocked_final_not_ready_exit_one` (`valid=true`, `ready=false`, `violations=[]`, `blocker_state` preservado) |
| Bloqueios 3 tipos + pesquisável | AC6 | Unit | novo `test_blocker_classification` |
| CLI exit codes e JSON | integração do helper | Integração leve (subprocess) | novo `test_cli_check_exit_codes` |
| Referência absoluta/`/tmp` ou `path#Lnn` como evidência de execução | R2, #31 "Caminho /tmp … insuficiente" | Unit | novo `test_evidence_ref_rejects_paths` |
| Mapeamento tipo → estado → razão de espera | AC6, R7 | Unit | estende `test_blocker_classification` |
| CLI não grava `__pycache__` | R6, #35 | Integração leve | existente (#35) `test_helpers_do_not_write_bytecode` descobre `attempt-log` da lista de `sync-plugin` e o executa sem variável de ambiente |
| Distribuição | sync | Check | `scripts/sync-plugin` + `git diff --exit-code plugins/ skills/*/references/` |
| Métricas existentes | regressão | Unit | existente `tests/test_workflow_metrics.py` |

Sem risco de pagamento/autorização/dados; profundidade normal. Comando local: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`.

### D7 — Arquivos esperados no Apply

Criados: `scripts/attempt_log.py`, `scripts/attempt-log` (0755, `sys.dont_write_bytecode = True` antes do import), `tests/test_attempt_log.py`, `tests/fixtures/attempt_log/{t1_override_no_effect,t1_diagnosed_alternative,t2_group_vs_field,t3_replan_with_basis,t4_service_before_phpunit,final_unresolved,blockers}.json`, `plugins/my-ai-skills/scripts/{attempt-log,attempt_log.py}` (gerados).
Editados: `protocol/TEST_STRATEGY.md` ("Implement and diagnose"), `protocol/AI_WORKFLOW.md`, `skills/apply-issue/SKILL.md` ("On failure…"), `skills/prepare-pr/SKILL.md`, `skills/milestone-orchestrator/SKILL.md` ("Exceptional states"), `skills/update-ai-workflow/SKILL.md` (helper `attempt-log` + companion `attempt_log.py`), `templates/pull-request.md` (bloco opcional após linhas de #31), `scripts/sync-plugin` (entrada no loop de helpers + linha `install -m 0644` do companion), `README.md`, `README.en.md` (parágrafo de cobertura, lista de scripts, tabela de helpers, linhas de instalação `cp …/attempt-log` e `cp …/attempt_log.py`, `chmod`, `test -x .ai-workflow/scripts/attempt-log` e `test -f .ai-workflow/scripts/attempt_log.py`, em paridade). Teste de bytecode de #35: descoberta automática, **sem edição prevista**; conferir que a CLI nova entrou no teste.
Regenerados (via `scripts/sync-plugin` após o rebase final, nunca à mão): `skills/*/references/TEST_STRATEGY.md`, `skills/{milestone-orchestrator,milestone-progress}/references/AI_WORKFLOW.md`, `skills/prepare-pr/references/pull-request.md`, `plugins/my-ai-skills/**` correspondentes.
Arquivo OpenSpec: archive em `openspec/changes/archive/*-issue-34-retry-hypothesis-log/` e `openspec/specs/retry-diagnosis/spec.md`.

## Risks / Trade-offs

- [Assinatura escrita pelo agente pode variar artificialmente e reiniciar contagem] → `TEST_STRATEGY` exige assinatura = classe de erro + primeira mensagem relevante sem partes voláteis; revisor confere; normalização mínima evita falsos agrupamentos.
- [Verificador estrutural não prova semântica do XML nem veracidade da mudança observada] → T2 detectado pela relação ancestral entre caminhos citados; `observed_change` exige resumo, efeito normalizado diferente e ref nova, mas a confirmação da leitura/efeito e da ref continua obrigatória em revisão humana.
- [Conflito textual com #31/#32/#33/#35 em arquivos compartilhados] → Apply por último (#35 → #31 → #32 → #33 → #34); seções disjuntas conforme R9; rebase e reconciliação textual antes de `/opsx-apply`; cópias só via `scripts/sync-plugin`.
- [Burocracia em falhas triviais] → bloco só obrigatório com falha repetida; uma tentativa única não exige registro.
- [`sync-plugin` reescreve todas as referências] → rodar após rebase final para não reverter mudanças de siblings.
- [Assinatura B pode mascarar falha A ainda genuinamente ativa] → só progredir A quando B for **na mesma obrigação** e registrar histórico não aprovado; gate avalia último episódio da obrigação. Evidência final da obrigação continua sujeita à verificação #31 e revisão; diferença de texto sozinha não prova execução real.
- [Suposta reclassificação pode ser ref antiga ou citação de código] → diagnóstico completo posterior à falha ambiental exige prova de **execução** nova, fase/lifecycle e justificativa da troca de camada; conteúdo da prova é revisado por humano, helper não abre manifesto.

### D8 — Correção de lifecycle e foco após duas auditorias independentes do PR #41

**Estado mínimo sem novo campo obrigatório/evento:** conservar a chave (`obligation`, assinatura normalizada), sequências `seq` e entradas existentes. Processar em ordem temporal por obrigação. Cada troca de assinatura cria fronteira de **episódio**: o episódio antigo cuja última tentativa falhou torna-se `progressed` (histórico, **não `resolved` e não `passed`**); o novo é ativo. Retorno A depois de B cria outro episódio A com streak zero, mantendo as tentativas antigas visíveis. Para compatibilidade, grupos com apenas um episódio mantêm status/contagem atuais; grupos com chave recorrente podem aparecer por episódio, identificados pela primeira `seq` (ou campo equivalente), nunca confundidos com aprovação do histórico. A confirmação de progresso não é `resolution` sintética; `resolution.passed` permanece válida somente para a última tentativa `pass` do episódio ativo. `resolution.blocked` de episódio histórico não libera falha atual e `blocked` ativo nunca passa `--final`. Um `pass` posterior pode encerrar um episódio; não apaga uma tentativa inválida anterior nem um replan pendente.

**Gate por obrigação, não por histórico:** `ready` avalia o episódio ativo de **cada** obrigação; `E_UNRESOLVED` só na falha ativa. Um episódio histórico falho não recebe `E_UNRESOLVED` por estar progredido, porém nunca muda para `resolved` nem é omitido de `groups`. A semântica antiga de `E_WEAKENED` ainda proíbe `passed` antigo depois de falha, `blocked` de outro episódio/grupo, skip e asserção relaxada. Nenhum evento de outra obrigação pode encerrar o episódio ativo desta obrigação.

**Streak e hipótese:** `E_RETRY_LIMIT` conta falhas no episódio corrente; diagnóstico precisa ocorrer entre a segunda falha do episódio e a próxima tentativa nele. Hipótese repetida compara tentativas e refs do episódio atual; hipótese do A histórico não impede novo A depois de B sem progresso real — a revisão ainda confronta a assinatura normalizada e evidência para detectar renomeações artificiais. Um `pass` dentro do mesmo episódio limpa streak; falha subsequente reinicia a contagem, mas invalida aprovação anterior.

**Foco não depende de adjacência:** manter por obrigação a falha ambiental ainda não resolvida, não a classe da tentativa imediatamente anterior. Não limpar ao observar B diferente, outro grupo ou outra obrigação, `blocker` ou diagnóstico sem prova. Limpar somente por tentativa posterior `pass` **da mesma obrigação** ou por `diagnosis` completa após a falha ambiental, ligada a seu grupo, que muda `class` e cita em `runtime_proof[]` pelo menos uma referência **de execução** nova posterior à falha (não apenas `path#Lnn` ou ref previamente vista na obrigação), registra fase/lifecycle/consumidores e justifica a mudança de camada. Referência opaca nova satisfaz apenas checagem estrutural; revisor comprova que a execução realmente demonstra a nova causa. Se o diagnóstico precede a última falha ambiental, permanece insuficiente. Nova falha ambiental após liberação reativa o foco. `change_target=application` enquanto foco ativo → `E_FOCUS`, independentemente de B falhar antes. Nenhum novo estado do orquestrador, manifesto ou modo CLI.

**Reativação da change:** o diretório arquivado `archive/2026-11-04-issue-34-retry-hypothesis-log` foi movido integralmente para `changes/issue-34-retry-hypothesis-log` para revisão formal da **mesma** change no branch do PR. A spec já existe em `openspec/specs/retry-diagnosis/spec.md`, logo o delta ativo passa a `MODIFIED Requirements` (blocos completos, incluindo cenários antigos), não um novo `ADDED` da capacidade. A live spec antiga permanece sincronizada com o HEAD implementado até o próximo Apply concluir e re-arquivar a mesma change via CLI oficial; editar a live spec agora afirmaria comportamento ainda não entregue. Aprovação independente anterior `467f58f` não cobre esta revisão material.

## Migration Plan

Aditivo: handoffs sem bloco continuam válidos; sem mudança de schema de métricas. Rollback = reverter o PR.
