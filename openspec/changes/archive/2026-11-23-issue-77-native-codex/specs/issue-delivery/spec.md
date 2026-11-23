# Spec Delta

## ADDED Requirements

### Requirement: Execução nativa equivalente sem dependência cruzada
OpenCode e Codex SHALL consumir os mesmos entrypoints e políticas canônicas para issue, milestone, PR e progresso. Cada agente SHALL usar somente sua execução nativa comprovada. MUST NOT exigir OpenCode de usuário Codex, duplicar o ciclo OpenSpec, adicionar dispatcher obrigatório ou processar duas issues simultaneamente.

#### Scenario: Issue completa a partir de Codex
- **WHEN** Codex recebe uma issue com contrato suficiente e capacidades disponíveis
- **THEN** usa Explore/Propose, Apply em contexto novo após handoff, Verify oficial, testes, Archive e revisão/entrega conforme as mesmas políticas, sem gate audit/ready paralelo

#### Scenario: Milestone de duas issues independentes
- **WHEN** o coordenador Codex recebe um milestone de duas issues elegíveis
- **THEN** mantém uma ativa inclusive no planejamento, só inicia a outra após entrega ou estacionamento explícito e restringe subagentes à issue ativa

#### Scenario: Consulta de status em qualquer runtime
- **WHEN** o usuário pede progresso atual da issue ou milestone
- **THEN** ambos consultam fontes atuais de forma somente leitura, mostram bloqueio e próximo passo e não criam métricas de tempo ou iniciam trabalho

### Requirement: Identidade e independência comprovadas por runtime
Workers SHALL apresentar identidade nativa real e correspondência de issue, checkout, entrada e saída imutáveis. Contexto novo e revisão independente SHALL ter prova de execução distinta e isolamento apropriado. MUST NOT reutilizar ID do owner, confundir processo com sessão, assumir API OpenCode em Codex ou certificar independência por troca de papel.

#### Scenario: Nova execução Codex
- **WHEN** o runtime inicia um worker Codex para Apply ou revisão
- **THEN** confirma ID e término pelo mecanismo suportado, sem carregar a conversa anterior como contexto herdado, e verifica os artefatos recebidos e ownership antes de escrever

#### Scenario: Capacidade insuficiente
- **WHEN** não há mecanismo verificável para um contexto novo, revisão independente ou conclusão de worker
- **THEN** somente a ação dependente fica bloqueada com próxima ação concreta, sem simular sucesso, exigir troca para OpenCode ou dispensar revisão

#### Scenario: ID ou callback de outra execução
- **WHEN** um resultado pertence a outra issue, checkout, worker ou SHA
- **THEN** o fluxo rejeita sua utilização como aprovação da execução atual e preserva o estado desconhecido

### Requirement: Recuperação entre agentes por evidência durável
A recuperação entre Codex e OpenCode SHALL reutilizar branch/worktree/change/PR e provas verificáveis, reconciliando writer anterior e reserva antes de transferir. MUST NOT alegar portabilidade de chat, sessão viva ou resultados incompletos; ausência de histórico acessível MUST permanecer explícita.

#### Scenario: Troca de agente após interrupção
- **WHEN** o writer anterior comprovadamente parou e Git/GitHub/OpenSpec e ownership identificam trabalho parcial
- **THEN** o novo agente retoma os mesmos artefatos após transferência explícita, reexecuta obrigações incompletas/invalidadas e não cria duplicatas

#### Scenario: Writer anterior desconhecido ou ativo
- **WHEN** o novo agente não consegue comprovar parada ou encontra reserva concorrente
- **THEN** preserva trabalho e bloqueia escrita, sem takeover por idade, PID ausente ou nome de branch

### Requirement: Políticas compartilhadas sem eventos operacionais
Ambos os runtimes SHALL preservar comunicação GitHub mínima, critérios de evolução e guardas de teste/revisão/merge existentes. MUST NOT adicionar comentários rotineiros ou ocultos, coletor de eventos, métricas de workflow, melhoria cosmética/duplicada ou mudança silenciosa do modo de merge.

#### Scenario: Transições e preparação de PR
- **WHEN** o fluxo Codex passa por workers e prepara uma entrega normal
- **THEN** requisitos e provas ficam nos artefatos existentes e PR/commits/checks/reviews, sem comentários operacionais nem registro substituto

#### Scenario: Melhoria já rastreada ou trivial
- **WHEN** um agente encontra sugestão cosmética, especulativa ou já presente no backlog
- **THEN** não cria issue redundante nem gate obrigatório de melhoria

#### Scenario: Merge sem prova necessária
- **WHEN** falta teste, revisão independente, aprovação exigida, check ou confirmação do HEAD atual
- **THEN** nenhum runtime declara merge elegível; o modo auto-if-green não dispensa os guardas existentes
