# Proposal

## Why

R1 da revisão independente da PR [#81](https://github.com/rocker-code/my-ai-skills/pull/81) demonstrou que `inspect_codex()` reconhece apenas uma grafia de TOML e deixa passar skills canônicas desabilitadas por configurações válidas equivalentes. Isso viola D3 e T8 da #77; o contrato anterior já arquivado permanece histórico imutável.

## What Changes

- Substituir detecção por regex por leitura semântica com parser TOML completo, preservando Python 3.10+, configuração do usuário e o diagnóstico de skill desabilitada.
- Incorporar Tomli 2.5.0 puro Python, MIT, com origem/digest/licença explícitos e bytes-fonte autenticados dentro do instalador standalone; não depender de pacote instalado, `pip`, serviço experimental ou download extra de parser no bootstrap.
- Distinguir regras TOML de comentários/strings e bloquear configuração malformada ou estrutura relevante inválida sem publicar parcialmente, alterar config ou revelar seu conteúdo.
- Acrescentar regressões das quatro formas reproduzidas, casos de controle/erros, execução real em Python 3.10, integridade/licença/distribuição e fluxos públicos.
- Criar novos commits instalador A_R1 / launcher B_R1 com SHA/digest literais; não emendar A/B existentes; manter merge commit obrigatório.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `global-workflow-update`: explicitar interpretação semântica e falha segura na inspeção da configuração Codex, refinando o diagnóstico existente.
- `global-workflow-distribution`: parser incorporado rastreável, licenciado e autenticado como parte da entrada standalone, sem dependência implícita ou mudança do Python mínimo.

## Impact

Implementação futura restrita a `scripts/install-global`, documentação de proveniência/licença da dependência sob `scripts/`, pins/receitas em `scripts/install.sh` e README pt/en, changelog e testes relacionados. Não muda seleção de agentes, ownership, schema de manifesto, runtime/delegação, workflow ou política de entrega.

Esta follow-up usa a mesma issue #77, branch/worktree e PR81, com base corretiva `32c2b64225e2d24fbcf1e39ee5d1daf95919662c`. Não é uma nova entrega de suporte Codex: T1–T11/P1/P2 e obrigações da proposta original continuam vigentes. Não altera arquivos de produção nesta fase, a instalação real, o arquivo OpenSpec anterior nem #61/#78.
