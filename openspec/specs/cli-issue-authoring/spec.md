# cli-issue-authoring Specification

## Purpose
Garantir que pedidos naturais de autoria no CLI produzam issues com o padrão existente do Web, sem alterar o ciclo de implementação.

## Requirements

### Requirement: Autoria CLI com padrão compartilhado
O agente CLI SHALL aplicar o padrão de autoria e o template atuais do protocolo Web ao criar ou refinar issues, com evidências, critérios observáveis e cenários proporcionais ao risco.

#### Scenario: Pedido natural de criação no CLI
- **WHEN** o usuário pede para criar uma issue no OpenCode, Codex CLI ou Claude Code
- **THEN** a entrada de criação exige resumo, comportamento, escopo e não objetivos, evidências/revisão e tabela de cenários com camada sugerida
- **AND** contratos, system design, wireframe e i18n são exigidos apenas quando aplicáveis

#### Scenario: Refinamento pontual
- **WHEN** o usuário pede uma revisão pontual de issue pelo CLI
- **THEN** o agente aplica o mesmo padrão preservando decisões e conteúdo fora do escopo autorizado

### Requirement: Compatibilidade e limite de execução
A autoria CLI SHALL preservar as entradas Web e encerrar no backlog, sem iniciar implementação ou OpenSpec e sem exigir confirmações extras para publicação já autorizada.

#### Scenario: Migração de instruções sem mudar o Web
- **WHEN** o pacote é atualizado com o suporte de autoria CLI
- **THEN** skills e protocolos Web permanecem inalterados e pedidos de implementação continuam no fluxo existente

### Requirement: Referências portáveis
As skills de autoria CLI SHALL receber cópias sincronizadas dos protocolos de autoria e referências visuais para funcionar também quando distribuídas isoladamente.

#### Scenario: Sincronização repetida
- **WHEN** as referências são geradas duas vezes
- **THEN** correspondem às fontes oficiais e a segunda execução não produz diferenças
