# Tasks

## 0. Entrada do Apply

- [ ] 0.1 Rebasear a branch em `origin/main`; verificar se #31, #32 e #33 foram mergeados e reconciliar textualmente `TEST_STRATEGY.md`, `apply-issue`, `prepare-pr` e o template de PR conforme design.md D1 (referências de evidência de #31, estados de #32); registrar no handoff o SHA da base e o resultado da reconciliação (sem mudança material, ou gate de revisão OpenSpec acionado)

## 1. Verificador do registro de tentativas

- [ ] 1.1 Criar `scripts/attempt_log.py` (stdlib) com parse do bloco ` ```attempt-log ` (Markdown ou JSON puro), agrupamento por (obrigação, assinatura normalizada) e as regras `E_FIELD`, `E_RETRY_LIMIT`, `E_NO_NEW_EVIDENCE`, `E_DIAG_INCOMPLETE`, `E_FOCUS` do design D4; verificar com `tests/test_attempt_log.py` (casos T1, agrupamento, hipótese repetida, T4) e fixtures `t1_*`, `t4_*`
- [ ] 1.2 Adicionar regras `E_CLAIM_ANCESTOR`, `E_CLAIM_INCOMPLETE`, `E_REPLAN_BASIS` e o cálculo `replan_required`; verificar com fixtures `t2_group_vs_field.json`, `t3_replan_with_basis.json` e casos negativos
- [ ] 1.3 Adicionar modo `--final` com `E_UNRESOLVED`, `E_WEAKENED` e `E_BLOCKER` + mapeamento `blocker_state` (`BLOCKED`/`RESOURCE_QUEUED`/`NEEDS_INPUT`/`NEEDS_REPLAN`); verificar com fixtures `final_unresolved.json`, `blockers.json`
- [ ] 1.4 Criar CLI `scripts/attempt-log check <arquivo> [--final]` (0755, saída JSON, exit 0/1/2) e teste via subprocess; verificar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` verde, incluindo `tests/test_workflow_metrics.py`

## 2. Protocolo e skills

- [ ] 2.1 Estender `protocol/TEST_STRATEGY.md` ("Implement and diagnose") com o formato do bloco, chave de grupo, conteúdo do diagnóstico, alternativa mais simples, foco por camada, prova de contradição de contrato, replanejamento com fundamento, não-aprovação e classificação de bloqueios, citando `scripts/attempt-log`; verificar que cada requisito de `specs/retry-diagnosis/spec.md` tem frase correspondente
- [ ] 2.2 Atualizar `skills/apply-issue/SKILL.md` (feedback loop e "Proportionate test coverage") para registrar o bloco, rodar o verificador antes da 3ª tentativa e antes de declarar contradição/bloqueio, e exigir reclassificação antes de trocar de camada; verificar por leitura contra os requisitos
- [ ] 2.3 Atualizar `skills/prepare-pr/SKILL.md` e `templates/pull-request.md` (seção Validation com bloco `attempt-log` opcional) para exigir `attempt-log check --final` quando houver falha repetida, com violação ⇒ `NOT READY FOR PR`; verificar por leitura
- [ ] 2.4 Atualizar `skills/milestone-orchestrator/SKILL.md` (estados excepcionais/relato de bloqueio) com a classificação técnico/capacidade/decisão e o mapeamento de estados; verificar por leitura
- [ ] 2.5 Atualizar `protocol/AI_WORKFLOW.md` (Proportionate test coverage) e `README.md`/`README.en.md` (parágrafo de cobertura e lista de scripts auxiliares) em paridade; verificar `grep -n attempt-log README.md README.en.md`

## 3. Distribuição e verificação integrada

- [ ] 3.1 Incluir `attempt-log` e `attempt_log.py` em `scripts/sync-plugin`, executar `scripts/sync-plugin` e verificar que `skills/*/references/` e `plugins/my-ai-skills/` refletem as fontes (`scripts/sync-plugin && git status --porcelain` sem diferenças após segunda execução)
- [ ] 3.2 Rodar a suíte completa `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` e `openspec validate issue-34-retry-hypothesis-log --strict`; conferir a matriz D6 cenário a cenário e registrar PASS/FAIL/NOT RUN no handoff

## Workflow follow-up

- Arquivar a change na branch da issue após verificação e validação estrita; inspecionar `openspec/specs/retry-diagnosis/spec.md` sincronizado.
- Seguir para `prepare-pr`, `pr-audit` e `post-pr-audit` (merge_mode auto-if-green).
