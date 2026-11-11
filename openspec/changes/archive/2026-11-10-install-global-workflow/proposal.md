# Proposal

## Why

Hoje `skills add -g` distribui as skills, mas não os protocolos, templates e helpers; o README ainda exige clone, cópias e instruções por repositório. A #50 torna a instalação pessoal completa e utilizável em múltiplos projetos a partir de uma única invocação, sem misturar ferramentas globais com estado de execução local.

## What Changes

- Introduzir entrada pública de instalação global com seleção explícita de agente, descoberta das skills e bootstrap global não destrutivo; OpenCode é o caminho principal a comprovar.
- Distribuir em uma revisão identificada todas as skills, referências, protocolos, templates, scripts executáveis e módulos Python acompanhantes; registrar origem, revisão e inventário gerenciado para atualização futura (#51).
- Resolver referências e helpers a partir do pacote global em qualquer checkout; no primeiro uso autorizado, disponibilizar também as integrações oficiais OpenSpec (`/opsx-*`, skills e comandos OpenCode) em projetos novos ou existentes sem recriar configurações.
- Vincular a entrada pública e o snapshot baixado à revisão imutável aprovada com hash independente, verificando-os antes de executar código remoto.
- Tratar pré-requisitos, falhas parciais, repetição e personalizações preexistentes sem perda silenciosa; preservar regras locais e estado/evidências por repositório.
- Após implementação, atualizar instruções e README PT-BR/EN com o comando real e verificações. Nenhum README será editado nesta fase de planejamento.

## Capabilities

### New Capabilities

- `global-workflow-distribution`: instalação global completa, descoberta, integridade e isolamento do pacote de workflow.

### Modified Capabilities

Nenhuma. Os contratos dos helpers de reserva, evidências e execução permanecem inalterados; só o modo de distribuição e invocação muda.

## Impact

Novo instalador em `scripts/`, skills que referenciam caminhos locais, documentação de instalação, testes de distribuição e bootstrap do agente. Dependências de runtime: Git, Python 3.10+ POSIX, `gh`, `jq`, OpenSpec e mecanismo de descoberta do agente. #51 consome o inventário; #52 remove o plugin pessoal e separa a geração de referências, com integração dos caminhos compartilhados somente na implementação coordenada.
