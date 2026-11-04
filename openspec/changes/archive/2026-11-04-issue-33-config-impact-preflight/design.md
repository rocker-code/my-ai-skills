# Design

## Context

Ver `proposal.md` (Why). Estado em `main` @ `5825a9c`:

- `protocol/TEST_STRATEGY.md` é a fonte da política de testes; `scripts/sync-plugin` a copia byte a byte para `skills/{implement-issue,openspec-workflow,apply-issue,prepare-pr,pr-audit,post-pr-audit,address-pr-review,milestone-orchestrator}/references/` e para `plugins/my-ai-skills/`. Hoje todas as cópias são idênticas à fonte.
- `skills/apply-issue/SKILL.md` L18–20 já lista checks Magento baratos (PHPUnit config, checkout montado, arquivos restaurados pelo Composer, isolamento) — não cobre lock/toolchain nem reconciliação de política; o entry gate (L12) verifica a revisão da proposta, não as referências de política.
- O instalador de skills não copia `scripts/` (README, seção de instalação passo 4); helpers são opcionais e copiados para `.ai-workflow/scripts/` pelo consumidor.
- `tests/` só tem `test_workflow_metrics.py` (padrão: `unittest`, `sys.path` para `scripts/`, CLI testado via `subprocess`). Não há CI no repositório; o gate é `python3 -m unittest discover -s tests`.

## Goals / Non-Goals

**Goals:** tornar o pré-flight operacional (procedimento + pontos de integração + helper determinístico + fixtures de regressão) preservando a política existente e sem nova etapa.

**Non-Goals:** fixtures Magento do consumidor; detecção automática de consumidores de configuração (é análise do agente no código); suporte a yarn/pnpm/pip/bundler no helper; log de tentativas (#34); registro de evidência (#31); reserva de checkout (#35); estado de execução (#32).

## Decisions

### D1 — Uma seção nova no TEST_STRATEGY, sem reescrever parágrafos existentes

Inserir `## Pre-flight for cross-cutting changes and expensive runs` entre `## Plan sufficient coverage` e `## Choose the proving layer`. Conteúdo (em inglês, como o restante do protocolo): gatilho proporcional; inventário de configuração/consumidores; amostra representativa na matriz existente; checklist técnico; reconciliação de política; falha da base; "focal ≠ ampla". A frase existente "Check environment readiness…" em *Implement and diagnose* permanece intacta.
*Alternativa rejeitada:* editar *Implement and diagnose* — é o trecho que #34 altera; conflito garantido.

### D2 — Precedência na reconciliação de política

Gates exigidos pela política vigente do repositório sempre se aplicam (mesmo que o plano os omita/proíba). Obrigações explícitas validadas no OpenSpec que a política atual deixou de exigir permanecem até revisão OpenSpec (TEST_STRATEGY já manda "preserve explicit validated obligations"). Ou seja: a reconciliação nunca reduz prova silenciosamente. Divergência que muda comportamento/aceite → gate de revisão OpenSpec existente. Registro no handoff ou `[IMPLEMENTATION NOTE]` na issue.
*Rationale:* deriva diretamente de AI_WORKFLOW ("latest explicit approved decision") + TEST_STRATEGY; não requer decisão do owner.

### D3 — Helper `scripts/preflight-check` (Python stdlib) com `lock` e `policy`

- `lock`: Composer (`composer.lock` `packages`+`packages-dev` vs `vendor/composer/installed.json`, formatos v1 lista e v2 `{"packages": [...]}`) e npm (`package-lock.json` `packages` lockfileVersion ≥ 2 vs `node_modules/.package-lock.json`). Compara `version` normalizada (strip de `v` inicial). Achados: `version-mismatch`, `missing`, `not-installed`. Sem lockfile suportado → `unsupported`, exit 2.
- `policy --since <rev>`: `git rev-parse --verify <rev>^{commit}` (falha → exit 2); `git diff --name-status <rev> -- <paths>` (inclui working tree) + `git ls-files --others --exclude-standard -- <paths>`.
- Exit 0/1/2; `--format text|json`; `--root`.
*Rationale:* T3 pede explicitamente "Helper/fixture"; T2 é simulação de handoff que precisa de verificação determinística. Composer cobre a evidência (PHPMD) e npm cobre o consumidor Expo (`expo-mobile-review`). Python segue `workflow_metrics.py`; bash+jq seria menos testável.
*Alternativas rejeitadas:* helper Magento-específico (fixtures pertencem ao consumidor); chamar `composer`/`npm` (exige toolchain e pode ter efeitos/rede); só documentação (não atende "verificações reutilizáveis com fixtures de regressão").

### D4 — Fixtures de regressão e testes neste repositório

- `tests/fixtures/preflight/lock/{composer-match,composer-phpmd-mismatch,composer-not-installed,npm-match,npm-mismatch,none}/` — lockfile + manifesto instalado mínimos (o caso PHPMD 2.15 × 3.x-dev reproduz Rancho #428).
- `tests/test_preflight_check.py` — CLI via `subprocess` sobre as fixtures (T3) e sobre repositório git temporário criado em `tempfile` (T2: política alterada/inalterada/commit desconhecido/arquivo não rastreado).
- `tests/fixtures/preflight/planning/{t1-regional-defaults,t4-docs-only}.json` — cenários de planejamento com os elementos que o procedimento precisa nomear; `tests/test_preflight_procedure.py` verifica que a seção de pré-flight da fonte contém cada elemento exigido (T1, T4, critérios 2–6), que as skills integradas referenciam a seção, e que todas as cópias embarcadas/plugin são idênticas à fonte.
*Rationale:* único meio determinístico de proteger um procedimento textual contra regressão; o teste checa âncoras estáveis (termos-chave), não frases inteiras, para não engessar redação.

### D5 — Pontos de integração mínimos nas skills

Uma frase ou bullet por skill, apontando para a seção do TEST_STRATEGY (ou, em `issue-explore`/`magento-review`, que não embarcam TEST_STRATEGY, descrevendo o item em uma linha):
- `issue-explore`: novo bullet em *Identify* — configuração compartilhada alterada e consumidores reais.
- `implement-issue`: acrescentar ao passo 4 o registro de amostra focal, premissas de fixture e referências de política (paths + commit) no handoff.
- `apply-issue`: nova seção curta `## Pre-flight and policy reconciliation` entre *Entry gate* e *Integration test feedback loop*, citando o helper opcional.
- `pr-audit`: uma frase no fim do 1º parágrafo de *Proportionate test coverage*.
- `magento-review`: bullet em *Inspect as relevant* — defaults de país/locale/moeda/timezone e consumidores (fixtures, importadores, Admin, pagamentos, e-mails).
Sem mudança em `AI_WORKFLOW.md`, `prepare-pr`, `post-pr-audit` ou templates (evita sobreposição com #31/#32).

### D6 — Distribuição

`scripts/sync-plugin`: incluir `preflight-check` no laço de helpers instalados (0755). README pt-BR/en: helper na lista de *Scripts auxiliares* e no `cp`/`chmod` do passo 5, em paridade. Regenerar `plugins/my-ai-skills/` só via `scripts/sync-plugin`.

## Matriz requisito → código → teste (risk-based)

| Cenário / critério | Risco concreto | Implementação | Camada | Prova (existente/nova) |
|---|---|---|---|---|
| T1 / AC1 defaults pt_BR/BR/BRL | Prova focal passa e suíte ampla quebra (Rancho #433: 119 falhas) | TEST_STRATEGY pré-flight (inventário + amostra); issue-explore; magento-review | Fixture de planejamento | Nova: `test_preflight_procedure` × `planning/t1-regional-defaults.json` |
| AC2 caminho/fixture inválido | Rodada cara desperdiçada | Checklist técnico (TEST_STRATEGY, apply-issue) | Fixture de planejamento | Nova: `test_preflight_procedure` (âncoras discovery/paths/fixtures/rollback) |
| T3 / AC2 vendor ≠ lock | Prova enganosa (Rancho #428 PHPMD) | `preflight-check lock` | Helper/fixture | Nova: `test_preflight_check` (mismatch=1, match=0, not-installed=1, none=2, npm) |
| T2 / AC3 política mudou | Instrução antiga aplicada contra a atual (Rancho #432) | Reconciliação (TEST_STRATEGY, apply-issue, pr-audit); `preflight-check policy` | Simulação handoff (git temp) | Nova: `test_preflight_check` (alterado=1, inalterado=0, desconhecido=2, untracked=1) + âncoras de precedência |
| T4 / AC4 alteração documental | Matriz extensa sem necessidade | Regra de proporcionalidade | Fixture de planejamento | Nova: `test_preflight_procedure` × `planning/t4-docs-only.json` |
| AC5 obrigações mapeadas e reuso | Testes duplicados | Matriz existente estendida (sem novo artefato) | Fixture de planejamento | Nova: âncora "existing" / reuso na seção |
| AC6 falha preexistente | Aprovação com suíte exigida falhando | Seção falha da base; pr-audit | Fixture de planejamento | Nova: âncoras base/comparable/not passed |
| Distribuição sincronizada | Cópias divergentes da fonte | `scripts/sync-plugin` | Contrato | Nova: paridade byte a byte em `test_preflight_procedure` |
| Regressão do existente | Quebra de métricas | — | Unit | Existente: `test_workflow_metrics` (suite completa) |

Proporcionalidade: mudança de processo + helper pequeno; sem Magento, sem rede, sem persistência. Nenhum teste hospedado. Gate final: suíte completa `unittest` + `openspec validate --strict` + paridade de sync (`git diff --exit-code` após `scripts/sync-plugin`).

## Arquivos esperados

Novos: `scripts/preflight-check`; `tests/test_preflight_check.py`; `tests/test_preflight_procedure.py`; `tests/fixtures/preflight/lock/**`; `tests/fixtures/preflight/planning/{t1-regional-defaults,t4-docs-only}.json`; `plugins/my-ai-skills/scripts/preflight-check` (gerado).
Alterados: `protocol/TEST_STRATEGY.md`; `skills/{implement-issue,openspec-workflow,apply-issue,prepare-pr,pr-audit,post-pr-audit,address-pr-review,milestone-orchestrator}/references/TEST_STRATEGY.md` (gerados); `skills/{issue-explore,implement-issue,apply-issue,pr-audit,magento-review}/SKILL.md`; `scripts/sync-plugin`; `plugins/my-ai-skills/{protocol/TEST_STRATEGY.md,skills/**}` (gerados); `README.md`; `README.en.md`. Archive: `openspec/changes/archive/*-issue-33-config-impact-preflight/**` e `openspec/specs/{validation-preflight,preflight-check-cli}/spec.md`.
Qualquer outro arquivo é fora de escopo.

## Risks / Trade-offs

- [Conflito com #34/#31 em TEST_STRATEGY/apply-issue/pr-audit] → seções/frases novas em pontos distintos (D1, D5); implementação serializada; rebase sobre irmãs já mergeadas e regenerar cópias com `scripts/sync-plugin` em vez de resolver conflitos nas cópias.
- [Teste de âncoras textual frágil] → âncoras são termos-chave, documentadas no fixture; mudança de redação atualiza fixture conscientemente.
- [Helper cobre só Composer/npm] → `unsupported` (exit 2) remete ao procedimento manual; nunca é aprovação.
- [Versões Composer com alias/normalização] → compara `version` literal após strip de `v`; divergência de formato aparece como achado para análise humana (falso positivo preferível a falso negativo).
- [Política fora do repo (skills instaladas globalmente)] → procedimento exige registrar a versão/commit das skills usadas; helper cobre apenas caminhos no checkout.

## Migration Plan

Aditivo; sem migração. Rollback = revert do PR.
