# Spec Delta

## ADDED Requirements

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
