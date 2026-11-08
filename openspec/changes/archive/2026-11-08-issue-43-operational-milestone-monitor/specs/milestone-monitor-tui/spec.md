# Spec Delta

## Purpose

Oferecer um painel operacional read-only no terminal para vários projetos e milestones, com navegação independente, etapas auditáveis e degradação clara quando faltam dados.

## ADDED Requirements

### Requirement: Comando global e configuração explícita
O sistema SHALL disponibilizar instalação local documentada de `aew dashboard`, executável de qualquer diretório, com configuração explícita de alvos e estado fora do checkout. Ausência de configuração SHALL mostrar orientação e tela vazia, sem descobrir ou monitorar projetos arbitrários.

#### Scenario: Executar fora do repositório
- **WHEN** o usuário instala o launcher em diretório do PATH e executa o comando de outro diretório
- **THEN** o painel usa sua configuração de usuário e não depende do cwd nem inicia um agente

### Requirement: Sanfonas e navegação estáveis
A TUI SHALL oferecer vários milestones com sanfonas independentes, seleção por identidade, detalhes de issue, modos compacto/detalhado e rolagem. SHALL suportar setas/j/k, Enter/Espaço, a/c, f e q/Esc; atualizações MUST NOT transferir seleção ou detalhes para outra issue por alteração de índice.

#### Scenario: Duas sanfonas abertas durante atualização
- **WHEN** o usuário abre dois milestones, recolhe um e uma issue anterior à selecionada muda de milestone
- **THEN** a outra sanfona permanece aberta e a seleção continua na mesma identidade quando ainda visível

### Requirement: Contadores e filtros sem estimativas
Cada cabeçalho SHALL exibir projeto, milestone, contadores exclusivos e conclusão GitHub/total, preservando totais do inventário independentemente do filtro. Filtros SHALL incluir todas, executando, pendentes, bloqueadas e concluídas, mantendo subestados legíveis sem dupla contagem.

#### Scenario: Filtro bloqueadas
- **WHEN** o usuário filtra bloqueadas em um milestone com issues fechadas e abertas
- **THEN** aparecem somente as bloqueadas, mas o percentual e os totais do cabeçalho continuam baseados no inventário completo

### Requirement: Régua real sem conclusão implícita
A régua SHALL usar etapas do protocolo real e rótulos pt-BR, distinguir concluída registrada, atual, futura/sem registro, falha, bloqueio e espera humana. MUST NOT marcar anteriores concluídas só pela posição da atual; rework, etapas desconhecidas e paralelismo SHALL permanecer consultáveis nos detalhes.

#### Scenario: Apply sem registro de Explore
- **WHEN** há abertura de Apply sem evidência de Explore ou Proposal
- **THEN** Apply é identificada como atual registrada, as anteriores ficam sem registro e não recebem marca de conclusão

### Requirement: Detalhes somente com evidência
Os detalhes SHALL apresentar etapa/worker, atividade observada, tempos registrados com timezone, branch/worktree, PR, bloqueio e próximo passo somente quando disponíveis e com fonte/horário. Campos ausentes SHALL indicar indisponível; referências de prova MUST NOT ganhar selo de aprovação sem verificação própria.

#### Scenario: Issue sem telemetria e branch desconhecida
- **WHEN** o usuário abre os detalhes de uma issue sem run ou vínculo local
- **THEN** o painel exibe a identidade GitHub e demais campos indisponíveis, sem tempos ou atividade simulados

### Requirement: Atualização responsiva e degradação
A TUI SHALL separar renderização de coleta com timeout, oferecer refresh manual e atualização periódica limitada, e permanecer navegável durante falha, rate limit ou fonte lenta. SHALL diferenciar cache desatualizado, fonte indisponível e dados recentes, incluindo vazio e milestone sem issues.

#### Scenario: Rate limit durante navegação
- **WHEN** GitHub informa rate limit enquanto há snapshot persistente
- **THEN** a TUI permanece responsiva, preserva o snapshot e informa falha/frescor sem repetir requisições em loop apertado

### Requirement: Adaptação de terminal e idioma
A apresentação SHALL ser pt-BR por padrão, preservar nomes próprios e branches, adaptar largura/altura e oferecer fallback ASCII e sem cor. Etapas e estados SHALL continuar compreensíveis sem depender exclusivamente de cor ou caracteres Unicode.

#### Scenario: Terminal estreito sem cor
- **WHEN** o painel é redimensionado para 40x12 com cor e Unicode indisponíveis
- **THEN** continua possível navegar, abrir detalhes e sair; rótulos abreviados e viewport mostram a etapa selecionada sem erro de curses

### Requirement: Demo separada e documentação operacional
A demo offline SHALL continuar executável com Python stdlib e identificada como dados simulados. A documentação operacional SHALL cobrir instalação, teclas, fontes, arquitetura, configuração, limites, privacidade e continuidade OpenCode/Codex, com README pt-BR/en em paridade.

#### Scenario: Demo sem credenciais
- **WHEN** a demo é executada sem gh ou OpenCode
- **THEN** continua mostrando dados simulados claramente e não faz conexões reais
