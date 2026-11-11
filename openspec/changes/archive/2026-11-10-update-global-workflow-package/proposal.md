# Proposal

## Why

A #50 entrega a instalação global íntegra para OpenCode, mas não oferece um fluxo público de atualização com revisão anterior/nova e pendências. A orientação atual de `update-ai-workflow` ainda opera sobre cópias locais/`npx skills`, o que pode deixar componentes e projetos em revisões diferentes.

## What Changes

- Oferecer uma única invocação explícita para atualizar o pacote global completo, reutilizando `scripts/install-global` e sua cadeia de confiança, com revisão Git completa aprovada, inventário e publicação coerente.
- Informar SHA anterior e novo efetivamente ativo, agentes, estado (`updated`, `already current`, `partial` ou `blocked`) e pendências; preservar a instalação anterior em falhas e manter a repetição da mesma revisão sem efeitos adicionais.
- Diagnosticar skills globais legadas de `skills.sh` no diretório OpenCode, instalações locais e sombras no projeto identificado, sem varrer outros repositórios. O pedido global não autoriza editar cópias locais: qualquer reconciliação local exige opt-in adicional de projeto e caminhos, além de propriedade demonstrável; conflitos ficam pendentes.
- Adaptar `update-ai-workflow` e README PT-BR/EN para encaminhar o pedido natural ao mesmo atualizador global, distinguindo instalações legadas/parciais e execução Web; publicar a sintaxe real somente após implementação/verificação.
- Nenhuma atualização automática, upgrade de agentes/runtimes, atualização do plugin pessoal, bootstrap de OpenSpec em projetos, varredura de todos os repositórios ou reescrita de projeto fechado.

## Capabilities

### New Capabilities

- `global-workflow-update`: atualização sob demanda, relatório auditável e reconciliação segura de instalações antigas sobre o pacote global existente.

### Modified Capabilities

Nenhuma: as garantias de instalação, confiança e isolamento de `global-workflow-distribution` continuam válidas; este delta acrescenta o contrato de atualização.

## Impact

`scripts/install-global`, `tests/test_global_install.py`, `tests/smoke_global_opencode.py`, `skills/update-ai-workflow/SKILL.md`, `README.md` e `README.en.md`. O CLI existente só suporta `--agent opencode --revision <SHA completo>` e já verifica o snapshot, manifesto e arquivos ativos; uma entrada pública continua exigindo SHA-256 publicado independentemente do download. Dependências #50 (merge `a722f4c4894e62ba50ff9dd0921d7f03d87664d0`) e #52 já entregues; sem PR para #51 neste checkout.
