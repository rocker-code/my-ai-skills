# issue-delivery Specification

## Purpose

Definir a entrega verificável de issues com o ciclo nativo OpenSpec, integração mínima ao GitHub e execução sequencial recuperável.

## Requirements

### Requirement: Ciclo nativo sem gates duplicados
O agente SHALL explorar contexto real e decisões uma vez quando suficientes, reutilizar artefatos existentes e invocar as skills oficiais de Propose, Apply e Archive. MUST reexplorar somente mudanças materiais e validar a revisão exata antes de Apply, sem aprovação humana rotineira.

#### Scenario: Issue completa ou planejamento recuperado
- **WHEN** uma issue tem requisitos completos ou proposta existente validada compatível
- **THEN** o agente segue o próximo estágio nativo necessário sem audit/ready separado, segunda exploração obrigatória ou plano duplicado

#### Scenario: Mudança material
- **WHEN** nova evidência altera comportamento, autorização, dados ou contrato validado
- **THEN** somente a ação afetada para, a proposta é revista e validada novamente e decisões materiais não resolvidas são escaladas

### Requirement: Verificação oficial e provas reais
O agente SHALL verificar suporte oficial e habilitar `openspec-verify-change` pelo mecanismo oficial quando suportado antes de usá-lo por padrão. MUST distinguir skill não gerada de runtime/perfil sem suporte e relatar limitações reais sem simular auditoria. Testes, análise estática, CI e revisão continuam obrigatórios; findings MUST ser resolvidos ou documentados conforme severidade e política.

#### Scenario: Verify disponível
- **WHEN** Apply termina e a skill oficial Verify está disponível
- **THEN** o agente a invoca, trata findings e preserva execução dos checks/testes obrigatórios antes da entrega

#### Scenario: Verify suportado mas ainda não gerado
- **WHEN** o suporte oficial existe mas a integração local ainda não gerou a skill Verify
- **THEN** o agente a habilita pelo mecanismo oficial preservando configuração existente e verifica a skill gerada antes de invocá-la, sem declarar indisponibilidade apenas pela ausência do arquivo

#### Scenario: Runtime ou perfil sem suporte
- **WHEN** a inspeção oficial confirma que o runtime/perfil não suporta Verify ou sua habilitação falha
- **THEN** o agente relata a capacidade ou falha exata e a próxima ação, sem fabricar um verificador ou uma invocação bem-sucedida

#### Scenario: Execução desconhecida
- **WHEN** um teste não possui término ou relatório confiável
- **THEN** o agente relata a prova incompleta e não usa sinais desconhecidos como aprovação

### Requirement: Engenharia e simplificação proporcionais
O agente SHALL priorizar código claro com arquitetura existente, verificação efetiva e melhorias relevantes. Simplificação MUST ser opcional, motivada por problema demonstrável ou pedido explícito, restrita ao escopo e preservar entradas/saídas, efeitos, ordem, autorização, erros e contratos com testes pertinentes.

#### Scenario: Código já claro
- **WHEN** a implementação funciona e não tem problema demonstrável de manutenção
- **THEN** o fluxo continua sem uma etapa obrigatória de simplificação, aprovação ou segunda auditoria

#### Scenario: Problema concreto no código alterado
- **WHEN** há duplicação ou complexidade desnecessária comprovada nos arquivos da issue
- **THEN** o agente inspeciona callers e testes, aplica mudanças pequenas reversíveis e reexecuta as provas afetadas sem ampliar comportamento

### Requirement: Revisão independente reutilizável por revisão imutável
O fluxo SHALL exigir revisão genuinamente independente quando aplicável e reutilizar revisão válida do mesmo HEAD e contexto. MUST revalidar superfícies e provas afetadas após alterações, sem duas auditorias completas obrigatórias do mesmo candidato.

#### Scenario: HEAD e contexto inalterados
- **WHEN** a revisão independente aprova o HEAD final e as decisões/checks seguem válidos
- **THEN** a elegibilidade para merge reutiliza a revisão sem exigir novo revisor completo

#### Scenario: Correção invalida prova
- **WHEN** um push altera superfície relevante ou um check obrigatório falha
- **THEN** o merge permanece bloqueado até correção, revisão/provas afetadas e checks atuais válidos

### Requirement: Fila sequencial por issue
O orquestrador SHALL selecionar dependências e manter no máximo uma issue ativa na fila autorizada. MUST concluir ou estacionar explicitamente a issue antes de iniciar outra, inclusive planejamento; subagentes só atuam na issue ativa, com isolamento, limites e um writer por checkout.

#### Scenario: Issues independentes e dependentes
- **WHEN** um milestone contém issues independentes e um consumidor dependente
- **THEN** nenhuma dupla é executada simultaneamente e o consumidor aguarda o contrato efetivo do produtor e sua dependência satisfeita

#### Scenario: Issue bloqueada
- **WHEN** a issue ativa requer ação material do dono ou dependência não satisfeita
- **THEN** o agente preserva seu estado e bloqueio, a estaciona explicitamente e só então seleciona outra issue elegível sem ampliar o escopo

### Requirement: Recuperação verificável e entrega segura
O fluxo SHALL retomar Git/GitHub/OpenSpec, ownership e evidências nativas verificáveis sem duplicar branch/change/PR. MUST manter isolamento, proteção de credenciais, contratos produtor/consumidor e autorização/branch protection. Ausência de capacidade ou sinal MUST permanecer desconhecida ou bloqueada.

#### Scenario: Interrupção ou PR existente
- **WHEN** o agente encontra uma execução interrompida ou PR correspondente à issue
- **THEN** reconcilia revisão, ownership, execução e checks, preserva trabalho e segue o próximo passo comprovado em vez de recriar a entrega

#### Scenario: Merge autorizado
- **WHEN** o modo auto-if-green está autorizado e revisão, HEAD e requisitos de repositório são satisfeitos
- **THEN** o agente pode mergear e confirma o resultado real; modo manual preserva o PR e qualquer sinal obrigatório pendente impede merge

### Requirement: Comunicação GitHub mínima
O fluxo MUST NOT publicar comentários automáticos de progresso, transições, handoff, aprovação interna, retry, auditoria rotineira ou eventos ocultos. SHALL usar corpo da issue/OpenSpec para requisitos e decisões e PR/commits/checks/reviews para entrega. Comentários ficam restritos a questão material, bloqueio que exige ação do dono ou discussão acionável de revisão.

#### Scenario: Execução normal e retomada
- **WHEN** a issue avança entre estágios ou é retomada
- **THEN** não são criados comentários operacionais nem registro oculto substituto e comentários históricos são preservados

#### Scenario: Decisão real pendente
- **WHEN** uma questão material não pode ser representada adequadamente no corpo da issue
- **THEN** o agente pode publicar uma pergunta concisa sem repetir conteúdo existente

### Requirement: Evoluções e Kaizen fora do caminho crítico
O agente SHALL registrar apenas evoluções acionáveis, independentes, valiosas e ainda não rastreadas sob a política existente. MUST manter Kaizen sob demanda ou periódico, sem bloquear merge ou próxima issue dependente, e justificar qualquer nova camada por lacuna real nas ferramentas existentes.

#### Scenario: Sugestão cosmética ou duplicada
- **WHEN** uma possível melhoria é apenas estilo, especulação ou já consta no backlog
- **THEN** nenhuma nova issue ou milestone é criada por essa sugestão

#### Scenario: Entrega concluída
- **WHEN** merge e fechamento são verificados
- **THEN** housekeeping seguro e a próxima issue elegível podem seguir sem esperar Kaizen nem coletar métricas de desempenho do workflow

### Requirement: Migração coerente dos consumidores
A simplificação SHALL migrar callers, distribuição, docs e referências antes de remover componentes. MUST preservar arquivos históricos e invariantes existentes; entrypoints mantidos precisam encaminhar de forma explícita a capacidades efetivas, sem aliases quebrados nem novo ciclo paralelo.

#### Scenario: Instalar e consultar fluxo após migração
- **WHEN** a distribuição é instalada e as referências sincronizadas
- **THEN** links ativos resolvem e os agentes encontram somente responsabilidades vigentes sem instrução contraditória de gate removido

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
