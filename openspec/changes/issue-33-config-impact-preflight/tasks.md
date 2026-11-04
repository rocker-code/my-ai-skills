# Tasks

## 1. Helper de pré-flight

- [ ] 1.1 Criar `tests/fixtures/preflight/lock/` com `composer-match`, `composer-phpmd-mismatch` (lock `3.x-dev`, instalado `2.15.0`), `composer-not-installed`, `npm-match`, `npm-mismatch` e `none`; verificar que cada diretório contém apenas os arquivos mínimos de lock/manifesto
- [ ] 1.2 Implementar `scripts/preflight-check` (Python stdlib, 0755) com subcomando `lock`, `--root`, `--format text|json` e códigos 0/1/2 conforme `specs/preflight-check-cli`; verificar com `tests/test_preflight_check.py` (match=0, mismatch=1 com pacote/versões, not-installed=1, none=2 `unsupported`, npm match/mismatch, uso inválido=2)
- [ ] 1.3 Implementar subcomando `policy --since <rev> [--path ...]` com caminhos padrão da spec; verificar em `tests/test_preflight_check.py` com repositório git temporário (alterado=1, inalterado=0, não rastreado=1, revisão desconhecida=2)
- [ ] 1.4 Incluir `preflight-check` no laço de helpers de `scripts/sync-plugin` e documentá-lo em `README.md` e `README.en.md` (lista de scripts auxiliares e `cp`/`chmod` do passo 5) em paridade; verificar com `grep -n preflight-check README.md README.en.md scripts/sync-plugin`

## 2. Procedimento e pontos de integração

- [ ] 2.1 Adicionar a seção `## Pre-flight for cross-cutting changes and expensive runs` em `protocol/TEST_STRATEGY.md`, entre *Plan sufficient coverage* e *Choose the proving layer*, sem alterar parágrafos existentes (D1, D2); verificar com `git diff protocol/TEST_STRATEGY.md` mostrando apenas inserção
- [ ] 2.2 Criar `tests/fixtures/preflight/planning/t1-regional-defaults.json` e `t4-docs-only.json` e `tests/test_preflight_procedure.py` (âncoras da seção para T1, T4 e critérios 2–6; referências nas skills; paridade byte a byte das cópias embarcadas e do plugin); verificar que o teste falha antes de 2.1/2.3 e passa depois
- [ ] 2.3 Inserir os pontos de integração de D5 em `skills/issue-explore`, `skills/implement-issue`, `skills/apply-issue`, `skills/pr-audit` e `skills/magento-review` (`SKILL.md`), sem nova etapa ou checkpoint; verificar com `tests/test_preflight_procedure.py`
- [ ] 2.4 Atualizar o parágrafo de cobertura proporcional em `README.md` e `README.en.md` com uma frase sobre o pré-flight, em paridade; verificar por leitura lado a lado

## 3. Distribuição e verificação final

- [ ] 3.1 Executar `scripts/sync-plugin` e verificar que só mudaram as cópias esperadas (`git status --short` restrito aos arquivos listados em design.md *Arquivos esperados*) e que uma segunda execução não gera diff
- [ ] 3.2 Executar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` (suite completa, incluindo `test_workflow_metrics`) e registrar PASS/FAIL com contagem
- [ ] 3.3 Executar `openspec validate issue-33-config-impact-preflight --strict` e conferir a matriz requisito→código→teste de design.md contra o diff final

## Workflow follow-up

- Arquivar a change no branch da issue (`openspec archive`), sincronizando `openspec/specs/validation-preflight` e `openspec/specs/preflight-check-cli`, e inspecionar archive + specs vivas no mesmo PR.
- Rebase sobre irmãs já mergeadas (#31, #34, #35, #32) antes do PR; regenerar cópias com `scripts/sync-plugin` em vez de editar cópias manualmente.
