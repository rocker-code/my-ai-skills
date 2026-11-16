# Spec Delta

## MODIFIED Requirements

### Requirement: Descoberta global sem alterar regras locais
O agente selecionado SHALL descobrir as skills e a orientação global para acessar o pacote, sem exigir alteração de arquivos de instruções de cada projeto. A orientação MUST respeitar restrições locais e do usuário; a instalação MUST preservar instruções/configurações preexistentes e MUST NOT conceder novas permissões de execução.

#### Scenario: Dois repositórios e uma worktree
- **WHEN** a pessoa inicia o agente selecionado em dois repositórios diferentes e em uma worktree
- **THEN** o agente descobre as mesmas skills e caminhos globais utilizáveis em todos, sem cópia local do workflow

#### Scenario: Instruções customizadas preexistentes
- **WHEN** há instruções globais e locais existentes, inclusive restrições de projeto
- **THEN** a instalação preserva seus conteúdos e a orientação nova condiciona o uso do workflow às restrições aplicáveis

#### Scenario: Pedido natural de retomada após interrupção
- **WHEN** uma pessoa inicia nova sessão OpenCode após interrupção e pede para continuar de onde parou
- **THEN** a orientação global disponibiliza a skill de retomada para reconstruir primeiro o estado verificável, sem alterar instruções locais ou conceder novas permissões
