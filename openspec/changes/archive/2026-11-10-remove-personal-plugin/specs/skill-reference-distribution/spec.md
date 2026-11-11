# Spec Delta

## Purpose

Define a distribuição das fontes oficiais das skills e de suas referências embarcadas sem depender de um plugin pessoal ou de seu catálogo no repositório.

## ADDED Requirements

### Requirement: Referências embarcadas independentes
A manutenção das skills SHALL gerar as referências compartilhadas necessárias dentro das respectivas skills sem exigir diretório, manifesto ou catálogo de plugin pessoal.

#### Scenario: Gerar referências sem scaffold de plugin
- **WHEN** a manutenção é executada em checkout com fontes oficiais, mas sem diretório ou manifesto do plugin
- **THEN** as referências declaradas das skills são geradas com o conteúdo correspondente a suas fontes e a operação termina com sucesso

#### Scenario: Repetir a geração
- **WHEN** a manutenção é executada duas vezes sem mudanças nas fontes
- **THEN** a segunda execução preserva os mesmos bytes e não produz diferenças no checkout

#### Scenario: Fonte obrigatória indisponível
- **WHEN** uma fonte requerida para uma referência está ausente
- **THEN** a manutenção informa o erro e não declara a geração completa

### Requirement: Distribuição oficial preservada
O repositório SHALL preservar as skills oficiais, protocolos, modelos, helpers e referências necessários à instalação normal e SHALL NOT distribuir o pacote pessoal ChatGPT/Codex ou seu catálogo como alternativa ativa.

#### Scenario: Consumir uma skill com referência compartilhada
- **WHEN** um agente instala uma skill oficial que referencia protocolo ou modelo embarcado
- **THEN** o conteúdo referenciado está disponível dentro da skill sem precisar do plugin pessoal

#### Scenario: Inventariar a distribuição ativa
- **WHEN** os caminhos de distribuição e instruções ativas do repositório são inspecionados
- **THEN** não há pacote, manifesto, catálogo, comando de instalação ou atualização ativa do plugin pessoal

#### Scenario: Manter agentes e fluxo Web
- **WHEN** o plugin pessoal é retirado do repositório
- **THEN** o suporte às skills do agente Codex e as orientações e skills do fluxo ChatGPT Web continuam disponíveis

### Requirement: Instruções de manutenção coerentes
A documentação ativa SHALL explicar a geração independente de referências sem instruir a instalação ou atualização do plugin pessoal e SHALL manter as variantes PT-BR e EN equivalentes.

#### Scenario: Seguir instruções atuais
- **WHEN** um mantenedor consulta os READMEs ou a orientação de atualização
- **THEN** encontra o procedimento vigente para referências e instalação oficial sem comandos de marketplace/plugin
