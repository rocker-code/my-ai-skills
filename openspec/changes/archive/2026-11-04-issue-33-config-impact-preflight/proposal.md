# Proposal

## Why

Issue: https://github.com/rocker-code/my-ai-skills/issues/33 — auditoria: https://github.com/rocker-code/my-ai-skills/issues/33#issuecomment-6621671121.

A política atual (`protocol/TEST_STRATEGY.md` @ `5825a9c`) diz apenas "check environment readiness and fixture assumptions before an expensive run". Na prática do consumidor (Rancho #433/PR #437, #432, #428), isso não impediu que: uma troca de defaults en_US/US/USD → pt_BR/BR/BRL passasse na prova focal e quebrasse 119 testes na suíte ampla; um artefato OpenSpec antigo proibisse Heavy Tests hospedados que a política vigente passou a exigir; e um PHPMD local 2.15 divergente do lock 3.x-dev produzisse prova enganosa. Falta um pré-flight operacional, reutilizável e verificável, integrado ao planejamento, Apply e review.

## What Changes

- `protocol/TEST_STRATEGY.md`: nova seção de pré-flight com (a) inventário de configuração compartilhada alterada e consumidores reais, (b) amostra representativa na matriz existente antes da rodada ampla, (c) checklist técnico (descoberta/caminhos, fixtures/rollback, fase/escopo da configuração, checkout montado, vendor/toolchain aderente ao lock, isolamento), (d) reconciliação de política no resume, (e) tratamento de falha da base, (f) regra de proporcionalidade para mudanças sem impacto transversal. A rodada focal não substitui a prova ampla nem gates exigidos.
- Pontos de integração curtos em `issue-explore` (identificar configuração transversal), `implement-issue` (registrar amostra, premissas e referências de política no handoff), `apply-issue` (pré-flight e reconciliação antes da primeira rodada cara), `pr-audit` (verificar que a rodada focal não foi apresentada como prova ampla, que obrigações obsoletas foram reconciliadas e que falha da base foi classificada) e `magento-review` (consumidores de país/locale/moeda/timezone/defaults).
- Novo helper opcional `scripts/preflight-check` (Python stdlib, somente leitura, sem rede): `lock` compara lockfile com dependências instaladas (Composer e npm); `policy` lista arquivos de política alterados desde o commit do plano. Fixtures de regressão e testes `unittest` no repositório; o procedimento textual continua autossuficiente quando o helper não está instalado.
- Teste de contrato do procedimento e da paridade das cópias embarcadas; `scripts/sync-plugin`, `plugins/my-ai-skills/**` regenerado e README pt-BR/en atualizados em paridade.

Fora de escopo: fixtures/testes Magento específicos (pertencem ao consumidor, ex. Rancho); log de tentativas/hipóteses (#34); registro de evidência de testes (#31); reserva de checkout (#35); estado de execução (#32); novo gate de aprovação, benchmark ou comando de usuário.

## Capabilities

### New Capabilities
- `validation-preflight`: procedimento de pré-flight de impacto e validação aplicado no Explore, planejamento, Apply e review — inventário de configuração compartilhada, amostra representativa, checklist técnico, reconciliação de política, falha da base e proporcionalidade.
- `preflight-check-cli`: helper opcional e determinístico que detecta divergência lockfile↔instalado e mudança de política desde o commit do plano.

### Modified Capabilities
- Nenhuma (não há specs vivas em `openspec/specs/`).

## Impact

- Documentação de processo: `protocol/TEST_STRATEGY.md` e cópias embarcadas em 8 skills; `skills/{issue-explore,implement-issue,apply-issue,pr-audit,magento-review}/SKILL.md`.
- Novo script `scripts/preflight-check`; `scripts/sync-plugin` passa a distribuí-lo.
- Novos testes `tests/test_preflight_check.py`, `tests/test_preflight_procedure.py` e fixtures em `tests/fixtures/preflight/`.
- Distribuição gerada `plugins/my-ai-skills/**`; `README.md`/`README.en.md`.
- Sem dependências externas, sem rede, sem credenciais, sem mudança de contrato público existente.
