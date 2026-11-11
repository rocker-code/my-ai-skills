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
A instalação SHALL disponibilizar o CLI OpenSpec quando suportado; a preparação de configuração local necessária SHALL ocorrer apenas no primeiro uso pelo agente, após inspecionar o repositório, sem sobrescrever configuração existente e sem reinstalar o workflow.

#### Scenario: Repositório ainda sem OpenSpec
- **WHEN** o agente inicia um fluxo que precisa de OpenSpec em repositório sem raiz configurada
- **THEN** prepara a configuração local necessária somente conforme autorização e regras do projeto, antes de qualquer proposta ou Apply

#### Scenario: Repositório com OpenSpec existente
- **WHEN** o agente inicia o fluxo em repositório já configurado
- **THEN** reutiliza sua configuração e comandos oficiais sem inicializar novamente ou substituir configurações locais

### Requirement: Isolamento de dados de execução
O pacote global SHALL compartilhar apenas ferramentas e orientação. Helpers de estado, reservas, logs e evidências MUST continuar escrevendo no escopo do repositório/worktree definido por seus contratos existentes e MUST NOT usar o diretório de instalação como armazenamento compartilhado de execuções.

#### Scenario: Execução em worktree e caminho com espaços
- **WHEN** um helper com módulo acompanhante roda em uma worktree cujo caminho contém espaços
- **THEN** resolve o módulo no pacote global, opera sobre a worktree correta e mantém estado/evidência no Git common dir correspondente

#### Scenario: Repositórios independentes
- **WHEN** o workflow executa em dois repositórios de identidades Git diferentes
- **THEN** reservas, logs e evidências de um não aparecem como estado de execução do outro
