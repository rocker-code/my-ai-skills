# Proposal

## Why

A criação Web segue o protocolo detalhado, mas a entrada de criação proíbe CLI e refine-issue não exige esse padrão. As issues Magento #451 (CLI) e #445 (Web) exemplificam a diferença de estrutura e evidências.

## What Changes

- Criar entrada create-issue para pedidos naturais no CLI.
- Encaminhar refinamento no CLI ao mesmo padrão de autoria já usado pelo Web.
- Distribuir as referências existentes com as duas skills e verificar sincronização.
- Preservar integralmente skills/protocolos Web e o ciclo de implementação OpenSpec.

## Capabilities

### New Capabilities

- `cli-issue-authoring`: criação e refinamento de issues pelo CLI com o padrão de qualidade Web.

### Modified Capabilities

Nenhuma.

## Impact

Skills create-issue/refine-issue, gerador de referências e teste de distribuição. Instalador global já descobre todas as skills dinamicamente, portanto dispensa mudança e republicação do instalador fixado. Não modifica issues existentes nem a instalação local do usuário.
