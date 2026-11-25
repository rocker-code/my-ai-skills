# Spec Delta

## ADDED Requirements

### Requirement: Atualização conserva seleção comprovada
Uma atualização sem agentes explícitos SHALL reutilizar a seleção instalada com origem/ownership comprovados, incluindo manifesto legado OpenCode. Agentes explícitos SHALL ampliar a seleção, nunca desativar silenciosamente integrações anteriores. Estado inconsistente ou desconhecido MUST bloquear inferência. Runtimes não selecionados MUST NOT ser exigidos.

#### Scenario: Codex somente recebe atualização sem flags
- **WHEN** uma instalação comprovada contém somente Codex e a pessoa executa atualização sem selecionar agentes
- **THEN** somente Codex é mantido, sem dependência em OpenCode ou nova configuração deste

#### Scenario: Instalação OpenCode legada
- **WHEN** manifesto legado, pacote e orientação OpenCode correspondem à origem verificável
- **THEN** a atualização reconhece OpenCode como seleção anterior, preserva instruções não gerenciadas e mantém sua integração

#### Scenario: Acrescentar segundo agente na mesma revisão
- **WHEN** uma instalação íntegra recebe seleção explícita do segundo agente sem mudar a revisão
- **THEN** ambas integrações permanecem disponíveis usando o mesmo pacote imutável, sem conflito de manifesto nem reescrita do snapshot

#### Scenario: Update com subconjunto explícito
- **WHEN** ambos estão instalados e a atualização informa apenas Codex
- **THEN** a seleção efetiva mantém ambos, informa a união e não remove OpenCode

#### Scenario: Registro de seleção adulterado
- **WHEN** seleção, caminhos, orientação, links ou manifesto não têm correspondência comprovável
- **THEN** a atualização bloqueia com diagnóstico antes de tomar posse ou alterar a instalação anterior

### Requirement: Transação de integração multiagente
A atualização SHALL validar todos os destinos, origens e capacidades da seleção efetiva antes de publicar. Falha em qualquer integração SHALL preservar revisão ativa, seleção, links, orientação e launcher anteriores. MUST NOT deixar outra integração apontando silenciosamente para estado parcialmente publicado nem remover conteúdo desconhecido.

#### Scenario: Falha após preparar uma integração
- **WHEN** uma falha é injetada após skills, orientação, launcher ou antes da ativação com ambos selecionados
- **THEN** a instalação anterior de cada agente continua funcional e preparações gerenciadas são revertidas, com falha explícita

#### Scenario: Colisão em somente um agente
- **WHEN** um caminho Codex ou OpenCode contém skill desconhecida/personalizada
- **THEN** a atualização não publica para o outro agente, preserva todos os conteúdos e informa o caminho conflitante

#### Scenario: Versão ou registro anterior alterado
- **WHEN** bytes, modos, origem, inventário, caminhos ou ownership divergem do baseline confiável
- **THEN** a tentativa bloqueia sem aceitar manifesto autoafirmado como prova nem sobrescrever conteúdo para reparar

### Requirement: Diagnóstico nos caminhos efetivos de cada agente
O fluxo SHALL diagnosticar colisões globais e sombras locais nos caminhos documentados do agente selecionado. MUST preservar arquivos desconhecidos/configurações/credenciais e limitar reconciliação local ao projeto e caminhos explicitamente autorizados com baseline comprovado. Relatório SHALL distinguir pacote, seleção, integração e prova de runtime.

#### Scenario: Codex com skill local ou global homônima
- **WHEN** há skill nativa homônima, configuração que a desabilita ou orientação global sombreada
- **THEN** a ferramenta informa precedência/ambiguidade e ação necessária, preserva personalização e não declara descoberta efetiva sem prova

#### Scenario: Migração skills.sh autorizada
- **WHEN** uma entrada em conflito tem origem e bytes comprovados e migração explicitamente autorizada para aquela entrada
- **THEN** somente essa entrada é migrada com backup e rollback, mantendo as mesmas recusas de symlink ancestral e filesystem divergente

#### Scenario: Projeto não inspecionado
- **WHEN** o pacote global é atualizado sem opt-in de reconciliação local
- **THEN** nenhuma cópia de projeto é alterada e nenhuma migração de projeto fechado é alegada

### Requirement: Seleção atravessa entradas públicas verificadas
As entradas públicas de instalação e atualização SHALL encaminhar a seleção efetiva sem perda ou interpretação por shell e verificar os caminhos de cada integração selecionada. SHALL preservar pin literal de instalador A em launcher B e as garantias existentes da cadeia de confiança.

#### Scenario: Fluxos públicos das três seleções
- **WHEN** instalação e atualização documentadas são exercitadas em HOME/PATH descartáveis com Codex, OpenCode ou ambos
- **THEN** SHA/digest de A são verificados antes de executar, a seleção é mantida, o pacote solicitado fica ativo e o launcher global executa seus módulos

#### Scenario: Download adulterado
- **WHEN** os bytes de A não correspondem ao digest literal em B
- **THEN** nenhuma seleção é instalada e o instalador não executa, preservando a instalação anterior
