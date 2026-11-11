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
A atualização SHALL preservar arquivos locais e globais não gerenciados e personalizações. SHALL diagnosticar sombras locais e cópias legadas somente no projeto explicitamente identificado/acessível, distinguir propriedade comprovada de inferida e MUST NOT declarar migrados projetos não inspecionados.

#### Scenario: Skill local personalizada sombreia a global
- **WHEN** o projeto identificado contém uma skill homônima local modificada ou de origem desconhecida
- **THEN** a skill local permanece intocada, a precedência é informada e sua migração permanece pendente

#### Scenario: Cópia legada comprovadamente idêntica
- **WHEN** uma skill ou cópia `.ai-workflow/` no projeto identificado tem baseline confiável e é comprovadamente idêntica ao artefato oficial anterior
- **THEN** o workflow pode reconciliar apenas os caminhos autorizados dessa instalação, preservando regras e arquivos locais não gerenciados

#### Scenario: Cópia sem baseline ou projeto fechado
- **WHEN** uma cópia existente não tem propriedade comprovável ou o projeto consumidor não foi inspecionado
- **THEN** nenhum arquivo local é substituído/apagado e o relatório deixa a migração explicitamente pendente

### Requirement: Relatório de atualização verificável
A operação SHALL informar agente, escopo, SHA anterior e SHA realmente ativo após a tentativa, estado dos componentes (`updated`, `already current`, `partial`, `blocked`) e pendências de reconciliação, sem revelar segredos ou confundir pacote global atualizado com migração dos projetos.

#### Scenario: Atualização bem-sucedida com sombra local
- **WHEN** o pacote global é atualizado mas uma skill local ainda o sombreia
- **THEN** o relatório mostra o novo SHA global e o conflito local pendente, sem declarar migração completa

#### Scenario: Falha antes da ativação
- **WHEN** a atualização falha antes da troca do pacote ativo
- **THEN** o relatório mostra SHA anterior ainda ativo, SHA pretendido e causa/pendências, sem declarar atualização completa

#### Scenario: Pedido natural em ambiente Web
- **WHEN** a pessoa pede “atualize o my-ai-skills” sem acesso do agente ao computador onde está instalado
- **THEN** o agente informa a limitação e o procedimento CLI confiável, sem afirmar ter atualizado a máquina
