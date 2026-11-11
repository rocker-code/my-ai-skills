# Proposal

## Why

A distribuição pessoal como plugin ChatGPT/Codex nunca foi utilizada pelo usuário e duplica as skills oficiais. Sua remoção não pode interromper a geração das referências embarcadas usadas pela instalação normal das skills.

## What Changes

- **BREAKING**: retirar do repositório o pacote `plugins/my-ai-skills/`, seu manifesto `.codex-plugin/plugin.json`, o catálogo `.agents/plugins/marketplace.json` e as instruções ativas de instalação/atualização desse plugin. Instalações pessoais antigas não serão desinstaladas automaticamente.
- Separar a geração das referências de `skills/*/references/` da cópia do plugin em `scripts/sync-plugin`: manter uma ferramenta independente de manutenção, executável sem scaffold do plugin, e retirar a sincronização exclusiva do plugin.
- Ajustar testes e documentação ativa, inclusive README PT-BR/EN, orientação de atualização e contexto OpenSpec, sem remover a integração do agente Codex nem os fluxos ChatGPT Web.
- Preservar as fontes oficiais `skills/`, `protocol/`, `templates/`, scripts auxiliares e referências necessárias. Não alterar histórico Git nem artefatos OpenSpec arquivados.

## Capabilities

### New Capabilities

- `skill-reference-distribution`: geração independente e idempotente das referências embarcadas e distribuição do repositório sem o plugin pessoal.

### Modified Capabilities

Nenhuma: o contrato de não gerar bytecode em `checkout-write-reservation` continua válido; sua menção ao antigo script é uma referência de implementação a reconciliar quando os specs vivos forem sincronizados, não uma mudança comportamental.

## Impact

Issue [#52](https://github.com/rocker-code/my-ai-skills/issues/52), base `f8fa6ac3eae56544487a7f5e51c74cde8829fa85`. Afeta `scripts/sync-plugin`, `plugins/my-ai-skills/`, `.agents/plugins/marketplace.json`, `README.md`, `README.en.md`, `skills/update-ai-workflow/SKILL.md`, `openspec/config.yaml` e os testes `test_instrumentation_distribution.py`, `test_preflight_procedure.py`, `test_worktree_reservation.py`. #50 altera README e `update-ai-workflow`; reconciliar ao aplicar/mesclar, sem editar esses arquivos nesta sessão de planejamento. #51 depende de #50 e deve consumir a documentação final sem ressuscitar o plugin. Sem nova dependência externa, migração de dados ou modificação das instalações dos usuários.
