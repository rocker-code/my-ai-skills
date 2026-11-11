# Spec Delta

## Purpose

Permitir atualização global explícita do pacote de workflow com integridade, conservação do estado anterior e diagnóstico honesto de instalações legadas.

## ADDED Requirements

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
