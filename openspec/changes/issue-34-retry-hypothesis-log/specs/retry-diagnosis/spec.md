# Spec Delta

## Purpose

Torna verificável o limite de tentativas sem progresso e o diagnóstico de bloqueios técnicos no workflow, por meio de um registro curto de tentativas embutido no handoff existente e de um verificador determinístico.

## ADDED Requirements

### Requirement: Registro de tentativas no handoff existente
O workflow SHALL registrar cada tentativa de correção de uma falha repetida num bloco curto do handoff/registro atual (seção de validação do handoff do Apply/PR), com alvo, obrigação, assinatura, classificação, hipótese, mudança desde a tentativa anterior, resultado e referências de evidência. O bloco MUST NOT exigir documento, etapa ou aprovação adicionais.

#### Scenario: Falha repetida é registrada no handoff
- **WHEN** um executor repete um teste ou check que falhou
- **THEN** o handoff contém um bloco de registro de tentativas com uma entrada por tentativa contendo todos os campos obrigatórios

#### Scenario: Entrada incompleta é rejeitada
- **WHEN** uma entrada de tentativa omite assinatura, obrigação, hipótese ou resultado
- **THEN** o verificador reporta a entrada como inválida citando o campo ausente

#### Scenario: Handoff sem falha repetida
- **WHEN** nenhuma falha foi repetida durante o Apply
- **THEN** o bloco é opcional e sua ausência não invalida o handoff

### Requirement: Agrupamento por assinatura e obrigação
O workflow SHALL agrupar tentativas pela obrigação (requisito/cenário da matriz) e pela assinatura normalizada da falha. Comando, filtro, ordem de execução ou nome do alvo MUST NOT fazer parte da chave de agrupamento.

#### Scenario: Comando renomeado não reinicia a contagem
- **WHEN** duas tentativas da mesma obrigação falham com a mesma assinatura usando comandos ou filtros diferentes
- **THEN** ambas contam no mesmo grupo como tentativas sem progresso

#### Scenario: Assinatura diferente abre novo grupo
- **WHEN** uma tentativa da mesma obrigação falha com assinatura diferente
- **THEN** a tentativa é contada como progresso do grupo anterior e inicia um novo grupo

### Requirement: Diagnóstico obrigatório após duas tentativas sem progresso
Quando um grupo acumular duas tentativas falhas sem progresso, o workflow SHALL exigir um diagnóstico registrado antes de qualquer nova tentativa desse grupo, contendo classificação, verificação de fase/escopo/lifecycle/consumidores efetivos, prova de runtime ou justificativa de não aplicabilidade e a próxima hipótese.

#### Scenario: Terceira tentativa sem diagnóstico
- **WHEN** um grupo tem duas tentativas falhas equivalentes e uma terceira tentativa é registrada sem diagnóstico anterior a ela
- **THEN** o verificador reporta violação do limite de tentativas

#### Scenario: Override que não altera a configuração lida (T1)
- **WHEN** duas tentativas aplicam overrides temporários e o validador continua lendo o mesmo valor
- **THEN** o diagnóstico registrado aponta fase/escopo efetivo da configuração e a próxima tentativa testa uma hipótese diferente

### Requirement: Nova tentativa declara evidência ou hipótese nova
Toda tentativa após a primeira de um grupo SHALL declarar a mudança realizada e uma evidência nova ou uma hipótese ainda não testada no grupo. Repetir uma hipótese já testada sem evidência nova MUST ser reportado como violação.

#### Scenario: Hipótese repetida sem evidência nova
- **WHEN** uma tentativa repete a hipótese de uma tentativa anterior do mesmo grupo e não referencia evidência nova
- **THEN** o verificador reporta violação

#### Scenario: Hipótese nova explícita
- **WHEN** uma tentativa após o diagnóstico declara hipótese distinta das anteriores
- **THEN** a tentativa é aceita

### Requirement: Comparação com a alternativa mais simples
O diagnóstico SHALL registrar a alternativa mais simples compatível com o contrato aprovado (por exemplo, fixture adequada ao cenário versus overrides temporários complexos) e a justificativa da ação escolhida.

#### Scenario: Diagnóstico sem alternativa
- **WHEN** um diagnóstico não registra alternativa mais simples nem justificativa da escolha
- **THEN** o verificador reporta o diagnóstico como incompleto

### Requirement: Correção focada na camada classificada
Quando a falha for classificada como ambiente/setup, a próxima tentativa SHALL alterar apenas o ambiente descartável, fixture ou setup, e MUST NOT alterar código de aplicação, salvo nova evidência que reclassifique a falha.

#### Scenario: Falha de serviço antes do PHPUnit (T4)
- **WHEN** a falha ocorre na inicialização de serviço antes do runner de testes e a próxima tentativa altera código de aplicação sem reclassificação
- **THEN** o verificador reporta violação de foco

#### Scenario: Correção no ambiente descartável
- **WHEN** a mesma falha classificada como ambiente/setup é seguida de tentativa que altera apenas o ambiente descartável
- **THEN** a tentativa é aceita

### Requirement: Prova exigida para alegar contradição de contrato
Uma alegação de contradição com o contrato aprovado SHALL citar a definição exata, o caminho do elemento citado, o campo e o escopo, separar observação de inferência e registrar como a leitura foi confirmada. Citar um elemento ancestral do campo (por exemplo, o grupo) sem prova de herança MUST ser rejeitado.

#### Scenario: Atributo do grupo lido como do campo (T2)
- **WHEN** a alegação cita um atributo de um grupo ancestral como se fosse do campo questionado, sem prova de herança
- **THEN** o verificador rejeita a alegação como bloqueio falso e o contrato aprovado permanece válido

#### Scenario: Alegação sem separação entre observação e inferência
- **WHEN** a alegação omite a observação, a inferência ou a confirmação da leitura
- **THEN** o verificador rejeita a alegação

### Requirement: Replanejamento somente com divergência comprovada
O workflow SHALL acionar a revisão OpenSpec existente apenas quando uma alegação de contradição aceita ou evidência nova referenciada comprovar mudança material; um pedido de replanejamento sem esse fundamento MUST ser rejeitado.

#### Scenario: Nova evidência exige mudança material (T3)
- **WHEN** uma alegação de contradição aceita demonstra que o contrato não pode ser cumprido
- **THEN** o registro indica replanejamento com fundamento e o fluxo segue o gate de revisão e validação OpenSpec existente

#### Scenario: Replanejamento sem fundamento
- **WHEN** um pedido de replanejamento não referencia alegação aceita nem evidência nova
- **THEN** o verificador rejeita o pedido

### Requirement: Limite de tentativas não vira aprovação
O limite de tentativas SHALL disparar investigação e preservar a obrigação de corrigir e validar. Um grupo cuja última tentativa falhou MUST permanecer não resolvido, e uma resolução que pule teste, enfraqueça asserção ou declare sucesso sem tentativa aprovada MUST ser rejeitada.

#### Scenario: Grupo pendente no handoff final
- **WHEN** o handoff para `prepare-pr` contém um grupo cuja última tentativa falhou
- **THEN** o verificador, no modo de handoff final, reporta o grupo como não resolvido e o resultado não é aprovação

#### Scenario: Resolução por enfraquecimento
- **WHEN** um grupo é marcado resolvido por pular o teste ou enfraquecer a asserção
- **THEN** o verificador rejeita a resolução

### Requirement: Classificação de bloqueios
Um relato de bloqueio SHALL classificar-se como impedimento técnico, falta de capacidade ou decisão de negócio, com evidência, e mapear para o estado existente do orquestrador (`BLOCKED`, `RESOURCE_QUEUED` ou `NEEDS_INPUT`). Decisão de negócio MUST trazer opções e impacto; fato técnico pesquisável MUST NOT ser escalado como decisão.

#### Scenario: Decisão de negócio sem opções
- **WHEN** um bloqueio classificado como decisão de negócio não lista opções e impacto
- **THEN** o verificador rejeita o relato

#### Scenario: Fato pesquisável escalado como decisão
- **WHEN** um bloqueio classificado como decisão de negócio declara que a pendência é um fato técnico pesquisável
- **THEN** o verificador rejeita a escalada e exige investigação no fluxo

#### Scenario: Bloqueio técnico com diagnóstico
- **WHEN** um bloqueio é classificado como impedimento técnico e referencia diagnóstico e evidência
- **THEN** o relato é aceito e mapeado para `BLOCKED`

### Requirement: Verificação determinística e distribuída
O repositório SHALL fornecer um verificador do registro de tentativas, sem dependências externas, coberto por testes com fixtures de simulação dos cenários T1–T4, e distribuí-lo pelo mecanismo de sincronização existente.

#### Scenario: Fixtures de simulação
- **WHEN** a suíte do repositório é executada
- **THEN** as fixtures T1–T4 e os casos de não aprovação produzem os resultados esperados do verificador

#### Scenario: Distribuição sincronizada
- **WHEN** o mecanismo de sincronização do plugin é executado
- **THEN** o verificador e as referências de protocolo atualizadas aparecem na distribuição gerada sem diferenças pendentes
