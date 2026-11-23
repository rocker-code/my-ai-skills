# global-workflow-distribution Specification

## Purpose

Permitir que uma pessoa instale e utilize em vários repositórios o workflow completo, mantendo ferramentas compartilhadas e dados de execução isolados em cada projeto.

## Requirements

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
A instalação SHALL disponibilizar o CLI OpenSpec quando suportado; no primeiro uso autorizado pelo agente a integração oficial OpenSpec 2.0 para o perfil selecionado SHALL disponibilizar suas skills nativas. Preparação local MUST NOT ocorrer na instalação global e MUST preservar configurações, artefatos e integrações existentes. A prova MUST verificar descoberta e invocação real no agente em sessão nova, sem exigir comandos legados ausentes.

#### Scenario: Repositório ainda sem OpenSpec
- **WHEN** o agente inicia fluxo que precisa de OpenSpec em repositório sem raiz configurada
- **THEN** verifica raiz pretendida, `context/list`, perfil e resíduos locais e globais; obtém autorização específica antes de inicializar pela interface oficial do perfil, confirma skills oficiais e preserva arquivos anteriores ou bloqueia sem escrita quando a preservação não puder ser demonstrada

#### Scenario: Repositório com OpenSpec existente
- **WHEN** o agente inicia o fluxo em repositório já configurado
- **THEN** reutiliza a integração se completa; caso contrário inventaria config, specs, changes, instruções e integrações de todas as ferramentas configuradas e efeitos globais, inspeciona dry-run/diferenças antes de pedir autorização específica para update ou inclusão de ferramenta, preservando a união das ferramentas existentes, sem `--force` nem limpeza implícita

#### Scenario: OpenCode recém-aberto após primeiro uso autorizado
- **WHEN** o agente prepara OpenSpec com autorização em projeto novo ou existente e uma sessão OpenCode nova é aberta no projeto
- **THEN** skills oficiais Explore, Propose, Apply e Archive da interface nativa do perfil ativo são descobertas e invocáveis, ou um bloqueio específico é reportado sem alegar integração completa; a ausência de comandos `/opsx-*` que a 2.0 não gera não constitui falha

#### Scenario: Resíduos gerados e personalizações
- **WHEN** uma migração encontra comandos/skills antigos, links, instruções customizadas ou conteúdo modificado em caminhos potencialmente gerados
- **THEN** identifica propriedade e alterações antes de substituir ou remover; somente gerados comprovados entram na limpeza aprovada, personalizações sobrevivem, e conflitos impedem publicação insegura sem inutilizar a versão anterior

#### Scenario: Prova não conclusiva
- **WHEN** a sessão nova não descobre ou não consegue invocar uma das skills oficiais requeridas
- **THEN** o fluxo informa o bloqueio preciso e não libera proposta, Apply ou instalação como integração comprovada

### Requirement: Isolamento de dados de execução
O pacote global SHALL compartilhar apenas ferramentas e orientação. Helpers de estado, reservas, logs e evidências MUST continuar escrevendo no escopo do repositório/worktree definido por seus contratos existentes e MUST NOT usar o diretório de instalação como armazenamento compartilhado de execuções.

#### Scenario: Execução em worktree e caminho com espaços
- **WHEN** um helper com módulo acompanhante roda em uma worktree cujo caminho contém espaços
- **THEN** resolve o módulo no pacote global, opera sobre a worktree correta e mantém estado/evidência no Git common dir correspondente

#### Scenario: Repositórios independentes
- **WHEN** o workflow executa em dois repositórios de identidades Git diferentes
- **THEN** reservas, logs e evidências de um não aparecem como estado de execução do outro

### Requirement: Launcher global de reserva utilizável no PATH
A instalação global SHALL disponibilizar `worktree-reservation` no PATH como entrada estável da versão ativa, preservando execução dos módulos acompanhantes. MUST NOT substituir comando já existente de outra origem ou personalizado e MUST informar como tornar o comando acessível quando o diretório de instalação não estiver no PATH.

#### Scenario: Uso fora do diretório do pacote
- **WHEN** a instalação termina e o usuário invoca `worktree-reservation` de um checkout independente
- **THEN** o comando executa o helper ativo com seus módulos e devolve o código e a saída originais

#### Scenario: Nome global ocupado
- **WHEN** o destino do comando ou a resolução efetiva no PATH pertence a outra origem
- **THEN** o instalador bloqueia com diagnóstico e preserva o comando existente e a instalação anterior

#### Scenario: Falha antes de publicar
- **WHEN** instalação ou atualização falha após preparar a entrada mas antes da ativação
- **THEN** o launcher e a versão ativa previamente funcionais permanecem utilizáveis, sem tomar posse de arquivos desconhecidos

#### Scenario: Diretório global fora do PATH
- **WHEN** o launcher não pode ser descoberto pelo PATH efetivo
- **THEN** a instalação não declara o comando global disponível e indica a ação necessária sem alterar o PATH do usuário silenciosamente

#### Scenario: Orientação do launcher em ambiente OpenSpec 2.0
- **WHEN** a instalação publica a orientação do comando global de reserva em ambiente com OpenSpec 2.0
- **THEN** o uso do launcher é comprovado independentemente da existência de `/opsx-*` e a orientação conserva o contrato nativo de skills oficiais entregue pela #71 no merge `5e33688d2a9db702e6bd0f2027d778f3baebdf35`, sem oferecer comandos legados fabricados nem instalação 1.x como condição para utilizar a reserva; a verificação de bootstrap OpenSpec segue seu contrato próprio e não é declarada aprovada por esta prova

### Requirement: Pin imutável do instalador no bootstrap público
`scripts/install.sh` SHALL fixar o SHA Git completo de um commit anterior A com o novo `scripts/install-global` e o SHA-256 literal dos bytes `A:scripts/install-global`, em commit posterior B. MUST NOT usar ref móvel, digest de B ou cálculo dinâmico em lugar do pin literal.

#### Scenario: Instalação pública pinada
- **WHEN** o usuário executa o comando de instalação documentado, sem checkout do pacote, com HOME/PATH descartáveis
- **THEN** o launcher público verifica o SHA-256 literal do instalador obtido de A, instala a revisão solicitada, e `worktree-reservation` no PATH importa seus módulos da revisão `active` e preserva saída e exit code

#### Scenario: Diretório de dados com metacaracteres de shell
- **WHEN** `XDG_DATA_HOME` contém aspas, `$()` ou outros metacaracteres e o instalador gera o launcher gerenciado
- **THEN** o launcher executa somente o helper sob o caminho literal `active`, sem executar conteúdo do caminho como shell, e passa argumentos e exit code intactos

#### Scenario: Digest do instalador divergente
- **WHEN** os bytes baixados de `A:scripts/install-global` diferem do SHA-256 literal em `scripts/install.sh`
- **THEN** o fluxo documentado falha antes de executar o instalador e mantém a instalação e o comando anteriores

### Requirement: Anchor de publicação alcançável
Ao publicar B, A SHALL permanecer alcançável em `main`; a distribuição MUST NOT ser declarada concluída antes das provas dos fluxos públicos com B.

#### Scenario: Uma PR entrega A e B
- **WHEN** uma PR entrega A e B na mesma branch
- **THEN** a integração é por merge commit, sem squash/rebase, e A permanece alcançável em `main`

#### Scenario: Duas PRs entregam A e B
- **WHEN** a entrega é dividida em duas PRs revisadas
- **THEN** A é integrado e alcançável em `main` antes de B, com gates aplicáveis em cada PR

### Requirement: Seleção independente de OpenCode e Codex
O instalador SHALL suportar `opencode`, `codex` ou ambos por seleção explícita repetível. SHALL exigir somente o runtime de cada agente efetivamente selecionado e dependências comuns. MUST NOT escolher agentes pela mera presença no PATH ou modificar uma integração não selecionada.

#### Scenario: Instalação somente Codex
- **WHEN** uma instalação inicial seleciona somente Codex com dependências disponíveis e sem OpenCode no PATH
- **THEN** instalação e verificação concluem sem invocar OpenCode nem criar sua configuração

#### Scenario: Instalação somente OpenCode
- **WHEN** uma instalação inicial seleciona somente OpenCode V2 e Codex não está no PATH
- **THEN** o fluxo existente permanece disponível sem invocar Codex nem criar orientação Codex

#### Scenario: Ambos selecionados
- **WHEN** a pessoa seleciona os dois agentes
- **THEN** cada runtime é verificado, os dois descobrem a mesma revisão canônica e o relatório enumera ambos

#### Scenario: Seleção inicial ausente ou inválida
- **WHEN** não há instalação verificável e nenhum agente é selecionado, ou há identificador não suportado
- **THEN** a entrada pública falha com seleção suportada e sem publicação nem escolha silenciosa

### Requirement: Descoberta nativa de uma fonte canônica
As integrações SHALL expor as mesmas skills/protocolos de um único snapshot validado pelos caminhos nativos documentados. A seleção instalada SHALL ser distinguível do inventário imutável do pacote. MUST NOT manter uma segunda implementação do workflow nem restaurar o plugin pessoal.

#### Scenario: Dois repositórios e worktree
- **WHEN** Codex ou OpenCode selecionado é iniciado em dois projetos e numa worktree com espaços no caminho
- **THEN** as skills globais resolvem para o mesmo snapshot ativo, sem copiar o workflow para cada projeto

#### Scenario: Configuração efetiva de Codex
- **WHEN** existe CODEX_HOME customizado, configuração de usuário ou orientação com precedência superior
- **THEN** a integração usa os caminhos efetivos documentados, preserva config, credenciais e restrições e informa orientação sombreada sem alegar carregamento comprovado

#### Scenario: Skill homônima ou instrução sem ownership
- **WHEN** um destino de qualquer integração contém arquivo/link desconhecido, conteúdo personalizado ou bloco sem origem comprovada
- **THEN** a instalação preserva esse conteúdo e bloqueia publicação insegura, sem assumir propriedade pelo nome

### Requirement: Cinco skills oficiais no runtime selecionado
A integração SHALL comprovar descoberta e invocação nativas de Explore, Propose, Apply, Verify e Archive em sessão nova do agente selecionado. Verify SHALL ser habilitado oficialmente quando suportado e usado por padrão após Apply. MUST preservar ferramentas/configurações existentes e autorização de bootstrap; leitura direta de arquivo ou resposta de stub MUST NOT valer como prova nativa.

#### Scenario: Codex com projeto novo e projeto mult tool existente
- **WHEN** o primeiro uso autorizado prepara a integração oficial para Codex em projeto descartável novo ou com outras ferramentas
- **THEN** cinco skills oficiais são descobertas/invocadas no Codex novo, mantendo a união de ferramentas, config/specs/changes e personalizações

#### Scenario: Verify suportado ainda ausente
- **WHEN** o perfil oficial suporta Verify mas ainda não gerou sua skill
- **THEN** o fluxo preserva escolhas existentes ao habilitá-lo oficialmente e prova sua invocação, sem verificador substituto

#### Scenario: Credencial ou capacidade ausente no smoke
- **WHEN** a execução nativa não pode autenticar, descobrir ou invocar uma skill exigida
- **THEN** a prova fica explicitamente não executada ou bloqueada com causa e ação; existência de arquivo, help e sucesso dos unitários não aprovam o smoke

#### Scenario: OpenCode permanece comprovado
- **WHEN** o smoke OpenCode é executado após a ampliação
- **THEN** comprova também Verify, além das quatro skills anteriores, sem fabricar comandos legados nem exigir Codex

### Requirement: Parser de configuração portátil e rastreável
A distribuição SHALL disponibilizar parser TOML completo em Python 3.10+ sem instalação de pacote no ambiente do usuário, serviço experimental ou download adicional de parser na execução. A dependência incorporada SHALL registrar versão, origem, digest e licença redistribuível, com política explícita de atualização e sem seleção silenciosa de biblioteca ambiente.

#### Scenario: Bootstrap standalone em Python 3.10
- **WHEN** a entrada pública validada roda com Python 3.10 sem tomllib ou pacote TOML de terceiros instalado
- **THEN** interpreta config com a dependência incorporada, sem pip, alteração do sistema, import de biblioteca ambiente ou obtenção de parser pela rede

#### Scenario: Pacote instalado e Python mais recente
- **WHEN** a mesma revisão roda standalone ou instalada num Python suportado mais recente
- **THEN** mantém o mesmo contrato semântico, proveniência e licença e não depende de arquivos externos omitidos do bootstrap

#### Scenario: Manutenção da dependência
- **WHEN** uma atualização futura modifica a versão ou os bytes incorporados
- **THEN** origem/digests/licença e testes de distribuição são revisados junto ao novo instalador, sem atualização automática ou substituição por uma referência móvel

### Requirement: Dependência coberta pelo pin completo do instalador
Os bytes executáveis da dependência SHALL estar integralmente autenticados pelo digest literal de instalador A em launcher posterior B e verificados antes de carregar o parser. Divergência SHALL bloquear sem importar conteúdo não verificado. MUST preservar âncoras publicadas, inventário instalado, rollback e merge commit das garantias existentes.

#### Scenario: Dependência incorporada alterada
- **WHEN** o download do instalador ou seu payload incorporado diverge do digest esperado
- **THEN** a execução da entrada adulterada ou o carregamento do parser divergente é recusado antes de publicar, preservando a instalação anterior

#### Scenario: Publicação corretiva
- **WHEN** a correção entrega nova dependência e lógica de inspeção
- **THEN** cria novos A_R1 e B_R1 com pin literal dos bytes completos, sem emendar A/B anteriores, e os testes públicos validam o mesmo parser distribuído

#### Scenario: Inventário ou arquivos gerenciados adulterados
- **WHEN** uma atualização encontra instalador ou documentação/licença gerenciada divergentes do snapshot confiável
- **THEN** bloqueia pelos guardas existentes, sem dispensar verificação de bytes, modo ou ownership por se tratar de dependência incorporada
