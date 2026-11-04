# retry-diagnosis Specification

## Purpose
Torna verificável o limite de tentativas sem progresso e o diagnóstico de bloqueios técnicos no workflow, por meio de um registro curto de tentativas embutido no handoff existente e de um verificador determinístico.

## Requirements

### Requirement: Registro de tentativas no handoff existente
O workflow SHALL registrar cada tentativa de correção de uma falha repetida num bloco curto do handoff/registro atual (seção de validação do handoff do Apply/PR), com alvo, obrigação, assinatura, classificação, hipótese, mudança desde a tentativa anterior, efeito observado, resultado e referências de evidência. O bloco MUST NOT exigir documento, etapa ou aprovação adicionais.
Na seção Validation do PR, o bloco opcional SHALL seguir as linhas de obrigação existentes, sem reestruturá-las.

#### Scenario: Falha repetida é registrada no handoff
- **WHEN** um executor repete um teste ou check que falhou
- **THEN** o handoff contém um bloco de registro de tentativas com uma entrada por tentativa contendo todos os campos obrigatórios

#### Scenario: Entrada incompleta é rejeitada
- **WHEN** uma entrada de tentativa omite assinatura, obrigação, hipótese ou resultado
- **THEN** o verificador reporta a entrada como inválida citando o campo ausente

#### Scenario: Handoff sem falha repetida
- **WHEN** nenhuma falha foi repetida durante o Apply
- **THEN** o bloco é opcional e sua ausência não invalida o handoff

### Requirement: Referências de evidência portáveis
Cada referência em `evidence[]` para uma tentativa executada SHALL ser `evidence:<evidence_id>` quando `workflow-evidence` registrou a execução, ou URL GitHub ou SHA caso contrário. Caminho relativo com linha MUST ser aceito apenas em citações de código/definição, nunca em `evidence[]`. Caminhos absolutos ou temporários MUST ser rejeitados como prova de execução.

#### Scenario: Caminho temporário como evidência
- **WHEN** uma tentativa referencia `/tmp/run.log` ou outro caminho absoluto como evidência
- **THEN** o verificador rejeita a referência

#### Scenario: Citação de definição com linha
- **WHEN** uma alegação de contrato cita `etc/adminhtml/system.xml#L40` como definição
- **THEN** a citação é aceita, mas a mesma forma em evidência de execução é rejeitada

#### Scenario: Referência ao registro de evidência
- **WHEN** uma tentativa referencia `evidence:<evidence_id>` de uma execução registrada
- **THEN** a referência é aceita sem que o verificador abra o manifesto

### Requirement: Composição sem duplicar o manifesto
A obrigação SHALL usar o mesmo ID da linha da matriz de validação no handoff de #31. O bloco `attempt-log` SHALL ser o único registro do raciocínio de retry; nada é gravado em `extensions.attempts`. O verificador MUST NOT copiar nem ler campos do manifesto de evidência.

#### Scenario: Tentativas ligadas a uma obrigação
- **WHEN** um grupo de tentativas cita a obrigação `R2/T1` e as execuções por suas referências portáveis
- **THEN** o bloco preserva o raciocínio no handoff sem gravar tentativas no manifesto de cada execução

### Requirement: Agrupamento por assinatura e obrigação
O workflow SHALL agrupar tentativas pela obrigação (requisito/cenário da matriz) e pela assinatura normalizada da falha. Comando, filtro, ordem de execução ou nome do alvo MUST NOT fazer parte da chave de agrupamento.

#### Scenario: Comando renomeado não reinicia a contagem
- **WHEN** duas tentativas da mesma obrigação falham com a mesma assinatura usando comandos ou filtros diferentes
- **THEN** ambas contam no mesmo grupo como tentativas sem progresso

#### Scenario: Assinatura diferente abre novo grupo
- **WHEN** uma tentativa da mesma obrigação falha com assinatura diferente
- **THEN** a tentativa é contada como progresso do grupo anterior e inicia um novo grupo

### Requirement: Diagnóstico obrigatório após duas tentativas sem progresso
Depois de duas falhas sem progresso no mesmo grupo, o workflow SHALL exigir diagnóstico antes de qualquer nova tentativa, mesmo que ela declare `pass`. O diagnóstico SHALL registrar classificação, fase/escopo/lifecycle/consumidores efetivos, prova de runtime ou não aplicabilidade justificada e a próxima hipótese.

#### Scenario: Terceira tentativa sem diagnóstico
- **WHEN** um grupo tem duas tentativas falhas equivalentes e uma terceira tentativa é registrada sem diagnóstico anterior a ela
- **THEN** o verificador reporta violação do limite de tentativas

#### Scenario: Terceira tentativa declarada aprovada sem diagnóstico
- **WHEN** um grupo acumula duas falhas e a terceira tentativa é marcada `pass` sem diagnóstico registrado entre a segunda e a terceira
- **THEN** o verificador reporta a mesma violação e não aprova o handoff final

#### Scenario: Terceira tentativa após diagnóstico
- **WHEN** o diagnóstico completo é registrado depois da segunda falha e antes da terceira tentativa do mesmo grupo
- **THEN** o limite de tentativas não é violado, independentemente de a terceira tentativa passar ou falhar

#### Scenario: Override que não altera a configuração lida (T1)
- **WHEN** duas tentativas aplicam overrides temporários e o validador continua lendo o mesmo valor
- **THEN** o diagnóstico registrado aponta fase/escopo efetivo da configuração e a próxima tentativa testa uma hipótese diferente

### Requirement: Nova tentativa declara evidência ou hipótese nova
Cada nova tentativa do grupo SHALL declarar a mudança realizada e hipótese inédita ou evidência nova substantiva. Se repetir hipótese, SHALL registrar `observed_change` concreto, `observed_effect` diferente do da tentativa anterior dessa hipótese após normalizar minúsculas/espaços e uma referência nova em `evidence[]` que sustente a mudança. O verificador SHALL comparar efeito e refs; a revisão SHALL confirmar o conteúdo citado sem ler o manifesto de execução.

#### Scenario: Hipótese repetida sem evidência nova
- **WHEN** uma tentativa repete a hipótese de uma tentativa anterior do mesmo grupo e não referencia evidência nova
- **THEN** o verificador reporta violação

#### Scenario: Novo ID sem mudança de observação
- **WHEN** uma hipótese é repetida com referência nova, mas assinatura e efeito observado normalizados permanecem iguais aos da tentativa anterior dessa hipótese
- **THEN** o verificador reporta violação mesmo com o ID novo; sucesso ou novo nome de arquivo não substitui mudança observada

#### Scenario: Mudança observada não resumida ou não citada
- **WHEN** uma hipótese é repetida com efeito observado diferente, mas sem resumo concreto da mudança ou sem referência nova que a sustente
- **THEN** o verificador reporta violação

#### Scenario: Mesma assinatura com efeito alterado
- **WHEN** a hipótese e a assinatura de falha se repetem, mas o efeito observado muda de fato, é resumido e cita evidência nova
- **THEN** a tentativa satisfaz a regra de evidência substantiva mesmo sob a mesma assinatura, sujeita à confirmação da citação e aos demais gates do grupo

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
O limite de tentativas SHALL disparar investigação, não aprovação. Um grupo com última tentativa `fail` MUST permanecer não aprovado; `blocked` SHALL referenciar bloqueio válido do mesmo grupo. Resolução por skip, asserção enfraquecida ou `passed` sem referência à última tentativa `pass` do grupo MUST ser rejeitada.

#### Scenario: Grupo pendente no handoff final
- **WHEN** o handoff para `prepare-pr` contém um grupo cuja última tentativa falhou
- **THEN** o verificador, no modo de handoff final, reporta o grupo como pendente ou bloqueado, nunca aprovado para PR

#### Scenario: Bloqueio corretamente classificado no handoff final
- **WHEN** um grupo com última tentativa falha tem resolução `blocked` referenciando um bloqueio válido do mesmo grupo
- **THEN** `--final` retorna `valid=true`, `ready=false`, `status=blocked`, `blocker_state` correspondente, nenhuma violação e exit 1; `prepare-pr` não prossegue

#### Scenario: Bloqueio de outro grupo não resolve a falha
- **WHEN** uma resolução `blocked` aponta um bloqueio de obrigação ou assinatura diferente
- **THEN** a resolução é inválida e não libera o handoff

#### Scenario: Aprovação antiga seguida de falha
- **WHEN** `passed` referencia uma tentativa `pass` anterior, mas a última tentativa do grupo falhou
- **THEN** a resolução é inválida e o grupo não é aprovado

#### Scenario: Resolução por enfraquecimento
- **WHEN** um grupo é marcado resolvido por pular o teste ou enfraquecer a asserção
- **THEN** o verificador rejeita a resolução

### Requirement: Validade estrutural não é prontidão para PR
O verificador SHALL emitir `valid` para estrutura/regras e `ready` para aprovação de todas as obrigações. No `--final`, grupo pendente, bloqueado ou replan pendente SHALL produzir `ready=false`, exit 1 e `NOT READY FOR PR`, mesmo com `valid=true`. Somente `valid=true && ready=true` SHALL retornar exit 0; entrada malformada retorna exit 2.

#### Scenario: Bloqueio estruturalmente válido sem aprovação
- **WHEN** um bloqueio bem formado mantém a obrigação não aprovada no modo `--final`
- **THEN** `valid=true`, `ready=false`, `violations=[]`, estado/razão de espera preservados e exit 1

#### Scenario: Handoff sem bloqueios nem pendências
- **WHEN** todos os grupos têm tentativa `pass` e resolução `passed`, sem violações nem replan pendente
- **THEN** `--final` retorna `valid=true`, `ready=true` e exit 0

### Requirement: Classificação de bloqueios
Um bloqueio SHALL ser classificado como impedimento técnico, falta de capacidade ou decisão de negócio, com evidência, mapeando para estado e razão de espera existentes: técnico→`BLOCKED`/`environment`, `dependency` ou `external`; capacidade→`RESOURCE_QUEUED`/`runtime_capacity`; decisão→`NEEDS_INPUT`/`owner_input`. Decisão de negócio MUST trazer opções e impacto; fato pesquisável MUST NOT ser escalado.

#### Scenario: Decisão de negócio sem opções
- **WHEN** um bloqueio classificado como decisão de negócio não lista opções e impacto
- **THEN** o verificador rejeita o relato

#### Scenario: Fato pesquisável escalado como decisão
- **WHEN** um bloqueio classificado como decisão de negócio declara que a pendência é um fato técnico pesquisável
- **THEN** o verificador rejeita a escalada e exige investigação no fluxo

#### Scenario: Bloqueio técnico com diagnóstico
- **WHEN** um bloqueio é classificado como impedimento técnico e referencia diagnóstico e evidência
- **THEN** o relato é aceito e mapeado para `BLOCKED` com razão de espera `environment`, `dependency` ou `external`

#### Scenario: Razão de espera incompatível
- **WHEN** um bloqueio de falta de capacidade declara razão de espera `owner_input`
- **THEN** o verificador rejeita o relato

### Requirement: Verificação determinística e distribuída
O repositório SHALL fornecer um verificador do registro de tentativas, sem dependências externas e sem gravar bytecode ao executar, coberto por testes com fixtures de simulação dos cenários T1–T4, e distribuí-lo pelo mecanismo de sincronização e pelas instruções de instalação existentes.

#### Scenario: Fixtures de simulação
- **WHEN** a suíte do repositório é executada
- **THEN** as fixtures T1–T4 e os casos de não aprovação produzem os resultados esperados do verificador

#### Scenario: Distribuição sincronizada
- **WHEN** o mecanismo de sincronização do plugin é executado
- **THEN** o verificador e as referências de protocolo atualizadas aparecem na distribuição gerada sem diferenças pendentes

#### Scenario: Execução sem bytecode
- **WHEN** o verificador é executado no checkout
- **THEN** nenhum diretório `__pycache__` é criado em `scripts/`
