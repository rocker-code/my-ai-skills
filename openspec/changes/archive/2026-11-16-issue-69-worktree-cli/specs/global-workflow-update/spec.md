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

### Requirement: Atualização pública usa pin novo verificado
`scripts/update.sh` SHALL baixar `scripts/install.sh` da revisão escolhida em `main` e executar o instalador A por SHA Git completo e SHA-256 literal publicados em B. MUST NOT declarar a nova interface distribuída enquanto B fixar o instalador antigo.

#### Scenario: Atualização pública documentada
- **WHEN** o usuário executa o comando de atualização documentado com HOME/PATH descartáveis, partindo de instalação anterior funcional
- **THEN** `scripts/update.sh` obtém o launcher de B, valida os bytes de A pelo digest literal, troca `active` para a revisão escolhida e a mesma invocação `worktree-reservation` importa módulos da revisão nova sem launcher duplicado

#### Scenario: Colisão ou falha via atualização pública
- **WHEN** o PATH contém comando alheio, o launcher gerenciado divergiu ou há falha antes de publicar a nova revisão
- **THEN** a atualização documentada falha sem tomar posse do comando alheio, preserva o launcher anterior gerenciado e mantém `active` anterior funcional
