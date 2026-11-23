# global-workflow-update Specification

## Purpose
Permitir atualização global explícita do pacote de workflow com integridade, conservação do estado anterior e diagnóstico honesto de instalações legadas.

## Requirements

### Requirement: Atualização global explícita e completa
O workflow SHALL atualizar por uma invocação explicitamente solicitada todos os componentes gerenciados do pacote global do agente suportado para uma única revisão Git completa aprovada. MUST NOT atualizar automaticamente ao iniciar sessão, issue ou milestone.

#### Scenario: Nova revisão para dois projetos
- **WHEN** a pessoa solicita atualização da instalação global OpenCode para uma revisão aprovada que inclui skill nova e helper alterado
- **THEN** skills e referências, protocolos, templates e scripts passam a corresponder à mesma revisão e ficam disponíveis em dois projetos sem repetir a atualização em cada um

#### Scenario: Tarefa comum sem pedido de atualização
- **WHEN** o agente inicia tarefa de desenvolvimento ou consulta de status sem pedido explícito de atualizar o pacote
- **THEN** nenhuma atualização do pacote é iniciada

### Requirement: Cadeia de confiança de ponta a ponta
O comando público de atualização SHALL autenticar a entrada executável por digest publicado independentemente do download e SHALL obter o pacote pela revisão Git completa aprovada, vinculando o manifesto à mesma revisão antes de ativar o pacote. MUST NOT executar entrada recebida apenas do canal do download nem resolver silenciosamente uma referência mutável como versão aprovada.

#### Scenario: Entrada e snapshot verificados
- **WHEN** a entrada corresponde ao digest independente e o snapshot corresponde à revisão aprovada
- **THEN** o pacote pode ser ativado e a revisão verificada é reportada

#### Scenario: Entrada adulterada ou SHA divergente
- **WHEN** o download da entrada diverge do digest ou o snapshot diverge da revisão aprovada
- **THEN** a execução ou ativação é recusada, respectivamente, e a instalação anterior permanece funcional

### Requirement: Revisões consistentes e recuperação
A atualização SHALL validar a propriedade e integridade da versão anterior e da nova antes da troca de versão ativa. SHALL preservar uma instalação funcional anterior diante de erro e MUST NOT apagar versões ou arquivos de propriedade desconhecida.

#### Scenario: Falha na preparação ou publicação
- **WHEN** ocorre falha antes da ativação, inclusive após criar vínculos novos ou alterar orientação gerenciada
- **THEN** a revisão anterior continua ativa e funcional e os efeitos gerenciados preparatórios são revertidos ou marcados como pendência sem alegar sucesso

#### Scenario: Repetição da mesma revisão
- **WHEN** a revisão solicitada já está ativa e todos os vínculos/arquivos gerenciados estão íntegros
- **THEN** a operação informa `already current` e não duplica orientações, vínculos nem conteúdo

#### Scenario: Estado antigo alterado ou sem origem comprovável
- **WHEN** o manifesto, os bytes ou permissões gerenciadas da instalação ativa anterior não correspondem à origem verificável
- **THEN** a atualização bloqueia antes de alterar a instalação ativa e informa a necessidade de reconciliação

### Requirement: Preservação e diagnóstico de instalações anteriores
A atualização SHALL preservar arquivos locais e globais não gerenciados e personalizações. SHALL inventariar skills globais legadas de `skills.sh` no diretório de skills OpenCode do usuário e diagnosticar sombras/cópias locais somente no projeto identificado/acessível, comparando origem, baseline e conteúdo sem presumir propriedade pelo nome. MUST NOT declarar migrados projetos não inspecionados.

#### Scenario: Skill global legada de skills.sh com nome conflitante
- **WHEN** o diretório global OpenCode contém uma skill homônima instalada por `skills.sh`, com origem/baseline comprováveis ou incertos
- **THEN** o workflow compara metadados de origem, baseline confiável e conteúdo atual, informa conflito e caminho de migração, sem sobrescrever entrada desconhecida, personalizada ou de outra origem nem declarar atualização completa da integração

#### Scenario: Skill global legada sem colisão
- **WHEN** uma skill global de `skills.sh` não colide com o pacote oficial
- **THEN** ela permanece intocada, é distinguida dos vínculos gerenciados e não é declarada migrada sem prova

#### Scenario: Skill local personalizada sombreia a global
- **WHEN** o projeto identificado contém uma skill homônima local modificada ou de origem desconhecida
- **THEN** a skill local permanece intocada, a precedência é informada e sua migração permanece pendente

#### Scenario: Cópia legada comprovadamente idêntica
- **WHEN** uma skill ou cópia `.ai-workflow/` no projeto identificado tem baseline confiável e é comprovadamente idêntica ao artefato oficial anterior
- **THEN** o workflow apenas diagnostica por padrão; somente após opt-in adicional explícito para esse projeto e esses caminhos pode reconciliar os artefatos comprovados, preservando regras e arquivos locais não gerenciados

#### Scenario: Pedido natural sem opt-in local
- **WHEN** a pessoa pede “atualize o my-ai-skills” para o pacote global sem autorizar projeto e caminhos de migração
- **THEN** o pacote global pode ser atualizado, mas cópias e instruções do repositório atual ficam intocadas, mesmo que coincidam com o baseline, e sua reconciliação é relatada como pendente

#### Scenario: Opt-in local para caminhos delimitados
- **WHEN** a pessoa autoriza separadamente reconciliar caminhos enumerados em um projeto identificado após inventário e comparação confiáveis
- **THEN** apenas esses caminhos comprovadamente pertencentes ao workflow podem ser alterados, sem modificar regras não gerenciadas nem outros projetos

#### Scenario: Cópia sem baseline ou projeto fechado
- **WHEN** uma cópia existente não tem propriedade comprovável ou o projeto consumidor não foi inspecionado
- **THEN** nenhum arquivo local é substituído/apagado e o relatório deixa a migração explicitamente pendente

### Requirement: Relatório de atualização verificável
A operação SHALL informar agente, escopo, SHA anterior e SHA realmente ativo após a tentativa, estado dos componentes (`updated`, `already current`, `partial`, `blocked`) e pendências de reconciliação, sem revelar segredos ou confundir pacote global atualizado com migração dos projetos.

#### Scenario: Atualização bem-sucedida com sombra local
- **WHEN** o pacote global é atualizado mas uma skill local ainda o sombreia
- **THEN** o relatório mostra o novo SHA global e o conflito local pendente, sem declarar migração completa

#### Scenario: Colisão com skill global legada
- **WHEN** uma skill global `skills.sh` ocupa um caminho exigido pelo pacote gerenciado e não há migração segura autorizada
- **THEN** o relatório distingue revisão global efetivamente ativa, conflito de integração e passos pendentes, sem declarar pacote integralmente utilizável

#### Scenario: Falha antes da ativação
- **WHEN** a atualização falha antes da troca do pacote ativo
- **THEN** o relatório mostra SHA anterior ainda ativo, SHA pretendido e causa/pendências, sem declarar atualização completa

#### Scenario: Pedido natural em ambiente Web
- **WHEN** a pessoa pede “atualize o my-ai-skills” sem acesso do agente ao computador onde está instalado
- **THEN** o agente informa a limitação e o procedimento CLI confiável, sem afirmar ter atualizado a máquina

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
