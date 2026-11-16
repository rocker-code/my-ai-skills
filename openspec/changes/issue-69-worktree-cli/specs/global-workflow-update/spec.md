# Spec Delta

## ADDED Requirements

### Requirement: Launcher gerenciado acompanha atualização global
A atualização global explícita SHALL manter o comando `worktree-reservation` apontado à versão ativa validada e SHALL preservar o launcher anterior em caso de falha. MUST NOT substituir ou remover comando personalizado/sem propriedade comprovada.

#### Scenario: Nova versão ativada
- **WHEN** uma atualização validada publica uma nova revisão do pacote
- **THEN** a mesma invocação global executa o helper da revisão ativa com módulos acompanhantes compatíveis, sem instalar launcher duplicado

#### Scenario: Falha de publicação e rollback
- **WHEN** a atualização falha antes da ativação da revisão nova
- **THEN** o comando global continua executando a revisão anterior funcional e o instalador informa a falha sem remover o launcher anterior

#### Scenario: Launcher antigo alterado
- **WHEN** o comando no PATH tem bytes, modo ou origem divergentes do registro gerenciado
- **THEN** a atualização bloqueia antes de sobrescrevê-lo e preserva o comando e a instalação ativa
