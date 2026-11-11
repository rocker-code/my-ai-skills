# Spec Delta

## Purpose

Permitir que uma pessoa instale e utilize em vários repositórios o workflow completo, mantendo ferramentas compartilhadas e dados de execução isolados em cada projeto.

## ADDED Requirements

### Requirement: Instalação global em uma invocação
O instalador SHALL aceitar um ou mais agentes suportados escolhidos explicitamente e SHALL instalar todas as partes necessárias ao workflow no escopo do usuário em uma única invocação, sem exigir clone, cópia ou ativação em cada repositório.

#### Scenario: Instalação OpenCode em ambiente suportado
- **WHEN** a pessoa invoca o comando público selecionando OpenCode em ambiente com pré-requisitos disponíveis
- **THEN** skills, referências, protocolos, templates e helpers ficam acessíveis globalmente e o instalador informa a revisão instalada e como verificá-la

#### Scenario: Nenhum agente escolhido ou agente não suportado
- **WHEN** a invocação não seleciona agente ou escolhe um agente sem integração comprovada
- **THEN** o instalador falha com indicação dos agentes suportados e não configura silenciosamente outros agentes

### Requirement: Origem imutável autenticada antes de executar
O instalador SHALL obter a entrada pública por revisão Git imutável previamente aprovada e conferir seu digest contra referência confiável independente do download antes de executar a entrada. SHALL vincular o snapshot e o manifesto à mesma revisão aprovada e MUST NOT confiar em hash recebido somente do mesmo canal do artefato.

#### Scenario: Script e snapshot correspondem à revisão aprovada
- **WHEN** o script baixado corresponde ao digest publicado independentemente e o snapshot corresponde ao commit aprovado
- **THEN** a instalação pode prosseguir e registra a revisão efetivamente verificada

#### Scenario: Divergência de origem, hash ou revisão
- **WHEN** o script ou snapshot difere do digest/revisão esperados, inclusive redirecionamento para outra revisão
- **THEN** a execução é recusada antes de executar o script divergente ou publicar o pacote, e a instalação anterior permanece utilizável

### Requirement: Pacote completo e rastreável
A instalação SHALL conter os componentes oficiais necessários à execução e SHALL registrar origem, revisão exata e inventário dos arquivos que gerencia, sem incluir dados locais de projetos ou dependência operacional do plugin pessoal.

#### Scenario: Integridade do pacote instalado
- **WHEN** a instalação termina com sucesso
- **THEN** todas as skills e referências necessárias, protocolos, templates, helpers executáveis e módulos acompanhantes existem na revisão registrada sem referências internas quebradas

#### Scenario: Consumidor consulta o inventário
- **WHEN** uma atualização posterior examina a instalação
- **THEN** consegue identificar origem, revisão, agente(s) e arquivos gerenciados sem inferir propriedade de arquivos desconhecidos

### Requirement: Descoberta global sem alterar regras locais
O agente selecionado SHALL descobrir as skills e a orientação global para acessar o pacote, sem exigir alteração de arquivos de instruções de cada projeto. A orientação MUST respeitar restrições locais e do usuário; a instalação MUST preservar instruções/configurações preexistentes e MUST NOT conceder novas permissões de execução.

#### Scenario: Dois repositórios e uma worktree
- **WHEN** a pessoa inicia o agente selecionado em dois repositórios diferentes e em uma worktree
- **THEN** o agente descobre as mesmas skills e caminhos globais utilizáveis em todos, sem cópia local do workflow

#### Scenario: Instruções customizadas preexistentes
- **WHEN** há instruções globais e locais existentes, inclusive restrições de projeto
- **THEN** a instalação preserva seus conteúdos e a orientação nova condiciona o uso do workflow às restrições aplicáveis

### Requirement: Dependências declaradas e falhas explícitas
O instalador SHALL verificar dependências e capacidades do agente antes de declarar sucesso, instalar no mesmo fluxo apenas dependências próprias ausentes cuja instalação seja suportada e explicar a ação necessária para dependências externas, autenticação ou plataforma indisponíveis. MUST NOT atualizar runtimes existentes silenciosamente nem instalar stack de aplicações consumidoras.

#### Scenario: Dependência própria ausente com instalação suportada
- **WHEN** falta uma dependência própria instalável no escopo do usuário
- **THEN** o instalador a prepara e verifica na mesma invocação ou falha com causa e ação, sem declarar instalação completa

#### Scenario: Requisito de sistema ou autenticação indisponível
- **WHEN** falta requisito externo não instalável com segurança ou autenticação interativa
- **THEN** a execução falha com requisito e ação concreta, preserva instalação funcional anterior e não relata sucesso

### Requirement: Repetição e falha preservam estado anterior
O instalador SHALL ser idempotente para a mesma revisão e seleção de agentes. MUST NOT apagar arquivos desconhecidos nem substituir personalizações não reconciliadas; falha no preparo, obtenção ou publicação MUST NOT inutilizar uma instalação previamente funcional.

#### Scenario: Repetição da instalação
- **WHEN** a mesma revisão é instalada novamente com os mesmos agentes
- **THEN** os componentes permanecem equivalentes, sem duplicação de instruções, skills ou arquivos gerenciados

#### Scenario: Falha de download ou publicação
- **WHEN** a obtenção do pacote ou uma etapa de publicação falha
- **THEN** a falha é informada e a instalação funcional anterior permanece utilizável, sem apagar arquivos não gerenciados

#### Scenario: Conflito com personalização
- **WHEN** um caminho de destino já tem conteúdo de outra origem ou foi personalizado
- **THEN** o instalador preserva o conteúdo, informa o conflito e não substitui o arquivo silenciosamente

### Requirement: Primeiro uso de OpenSpec por projeto
A instalação SHALL disponibilizar o CLI OpenSpec quando suportado; no primeiro uso autorizado pelo agente a integração oficial para o agente selecionado SHALL disponibilizar skills e comandos `/opsx-*` aplicáveis ao perfil do projeto. Preparação local MUST NOT ocorrer na instalação global e MUST preservar configurações, artefatos e integrações existentes.

#### Scenario: Repositório ainda sem OpenSpec
- **WHEN** o agente inicia um fluxo que precisa de OpenSpec em repositório sem raiz configurada
- **THEN** verifica autorização e localização correta, inicializa por comando oficial para OpenCode e comprova arquivos oficiais de skills e comandos antes de qualquer proposta ou Apply

#### Scenario: Repositório com OpenSpec existente
- **WHEN** o agente inicia o fluxo em repositório já configurado
- **THEN** verifica integração efetiva, usa a existente quando completa e só propõe atualização/adição necessária com inspeção de alterações e autorização, sem sobrescrever configurações ou integrações personalizadas

#### Scenario: OpenCode recém-aberto após primeiro uso autorizado
- **WHEN** o agente prepara OpenSpec com autorização em projeto novo ou existente e uma sessão OpenCode nova é aberta no projeto
- **THEN** comandos `/opsx-explore`, `/opsx-propose`, `/opsx-apply` e `/opsx-archive` do perfil ativo e suas skills oficiais são descobertos e invocáveis, ou um bloqueio específico é reportado sem alegar integração completa

### Requirement: Isolamento de dados de execução
O pacote global SHALL compartilhar apenas ferramentas e orientação. Helpers de estado, reservas, logs e evidências MUST continuar escrevendo no escopo do repositório/worktree definido por seus contratos existentes e MUST NOT usar o diretório de instalação como armazenamento compartilhado de execuções.

#### Scenario: Execução em worktree e caminho com espaços
- **WHEN** um helper com módulo acompanhante roda em uma worktree cujo caminho contém espaços
- **THEN** resolve o módulo no pacote global, opera sobre a worktree correta e mantém estado/evidência no Git common dir correspondente

#### Scenario: Repositórios independentes
- **WHEN** o workflow executa em dois repositórios de identidades Git diferentes
- **THEN** reservas, logs e evidências de um não aparecem como estado de execução do outro
