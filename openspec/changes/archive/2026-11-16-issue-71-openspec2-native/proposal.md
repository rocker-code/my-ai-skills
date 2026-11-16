# Proposal

## Why

A distribuição atual exige comandos `/opsx-*` que o OpenSpec 2.0 não gera no perfil instalado, tornando inválida uma integração nativa funcional. A issue [#71](https://github.com/rocker-code/my-ai-skills/issues/71) é pré-requisito de Apply/fechamento de #61 e #69; a decisão aprovada nessas issues fixa a versão 2.0, sem pin em 1.x nem comandos inventados.

## What Changes

- **BREAKING:** substituir a obrigação de comandos `/opsx-*` pela descoberta e invocação comprovadas das skills oficiais do perfil OpenSpec 2.0 em sessão OpenCode nova, preservando gates Explore → Propose → Apply → Archive.
- Atualizar orientação gerada em `scripts/install-global`, protocolo, skills de workflow e READMEs em paridade; instalação global continua sem `init/update` de projetos.
- Migrar explicitamente apenas arquivos gerados rastreados cuja origem/propriedade seja comprovada, inspecionando perfil multi-tool, resíduos e efeitos globais; preservar personalizações e versão anterior em conflito/falha.
- Adaptar fixtures de HOME descartável e smoke real para provar integração nova/existente, dois projetos e worktree com espaços, falhando quando descoberta/invocação não puder ser demonstrada.
- Não implementar launcher #69, retomada #61, resolução de `E_RETRY_LIMIT` ou alterações no produtor M2T #46.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `global-workflow-distribution`: primeiro uso de OpenSpec e prova nativa em nova sessão, inclusive preservação e bloqueio seguro na migração 2.0.

## Impact

`openspec/specs/global-workflow-distribution/spec.md` após archive/sync; `scripts/install-global`, `protocol/AI_WORKFLOW.md`, `skills/openspec-workflow/SKILL.md`, skills de issue que exigem comandos, `README.md`/`README.en.md`, gerados rastreados `.agents/`, `.claude/`, `.opencode/`, `tests/test_global_install.py` e `tests/smoke_global_opencode.py`. OpenSpec CLI 2.0 e OpenCode V2 são dependências da prova, não ferramentas a instalar no HOME real durante planejamento.
