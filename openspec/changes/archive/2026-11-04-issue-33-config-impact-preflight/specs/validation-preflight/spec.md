# Spec Delta

## Purpose

Definir o pré-flight de impacto e validação que o fluxo aplica antes de execuções caras, para detectar cedo mudanças transversais de configuração, pré-condições técnicas inválidas, instruções de política desatualizadas e falhas preexistentes, sem substituir a prova ampla nem os gates exigidos.

## ADDED Requirements

### Requirement: Inventário de configuração compartilhada no Explore

Durante o Explore, o fluxo SHALL identificar se a mudança altera configuração compartilhada, defaults globais, toolchain ou infraestrutura de teste consumidos fora do módulo alterado. Quando houver, o fluxo MUST listar os consumidores reais encontrados no código, com caminho de arquivo, e as premissas de fixture que dependem do valor anterior.

#### Scenario: Troca de defaults regionais (T1)
- **WHEN** o plano altera defaults en_US/US/USD para pt_BR/BR/BRL
- **THEN** a matriz requisito→teste lista os consumidores reais afetados (por exemplo fixtures de endereço US, valores em USD, textos em inglês, rótulos de importação/CSV) com caminho de evidência e a premissa de fixture de cada um

#### Scenario: Consumidor não encontrado
- **WHEN** a busca por consumidores não encontra uso fora do módulo alterado
- **THEN** o plano registra a busca realizada e a conclusão "sem impacto transversal", sem criar linhas de matriz adicionais

### Requirement: Fronteiras Magento no inventário

Em repositórios Magento, o inventário de configuração compartilhada MUST considerar país, locale, moeda, timezone e demais defaults que afetam fixtures, importadores, Admin, pagamentos e e-mails.

#### Scenario: Default de moeda alterado
- **WHEN** a mudança altera a moeda base ou de exibição
- **THEN** o inventário avalia fixtures com valores monetários, importadores, Admin, pagamentos e e-mails e registra quais foram encontrados no código

### Requirement: Amostra representativa antes da rodada ampla

Para mudança com impacto transversal, o plano SHALL escolher, na mesma matriz requisito→teste existente, uma amostra representativa por fronteira afetada, justificada pelo consumidor real no código, para executar antes da rodada ampla. A amostra MUST reutilizar testes existentes quando eles cobrem a fronteira. O fluxo MUST NOT tratar a aprovação da amostra como equivalente à suíte ampla ou a gates locais/hospedados exigidos pelo consumidor.

#### Scenario: Amostra focal passa e suíte ampla continua obrigatória
- **WHEN** a amostra representativa passa
- **THEN** o registro de validação a identifica como rodada focal e a suíte ampla e os gates exigidos permanecem pendentes até serem executados

#### Scenario: Nova obrigação mapeada e reuso
- **WHEN** o pré-flight acrescenta uma linha à matriz
- **THEN** a linha indica o critério de aceite ou risco concreto e o teste existente reutilizado, ou a justificativa para um teste novo

### Requirement: Checklist técnico antes da primeira rodada cara

Antes da primeira execução cara (integração, funcional, suíte ampla ou hospedada), o Apply SHALL verificar e registrar: descoberta e caminhos dos testes, fixtures e rollback, fase e escopo de aplicação da configuração, checkout montado, vendor/toolchain aderente ao lockfile e isolamento do sandbox. Pré-condição reprovada MUST bloquear a rodada cara até correção ou bloqueio reportado.

#### Scenario: Caminho ou fixture inválido (critério 2)
- **WHEN** um teste planejado aponta para caminho inexistente, não é descoberto pela configuração do runner ou depende de fixture ausente
- **THEN** o pré-flight registra a pré-condição reprovada e a rodada ampla não é iniciada até a correção

#### Scenario: Toolchain divergente do lock (T3)
- **WHEN** a versão instalada de uma ferramenta difere da versão do lockfile (por exemplo PHPMD 2.15 instalado contra 3.x-dev no lock)
- **THEN** a pré-condição técnica bloqueia a prova e o registro indica pacote, versão instalada e versão do lock

### Requirement: Ambiente divergente não é prova

O fluxo MUST NOT apresentar como prova o resultado obtido em ambiente cuja pré-condição técnica foi reprovada.

#### Scenario: Resultado em ambiente divergente
- **WHEN** uma suíte é executada com vendor divergente do lockfile
- **THEN** o resultado é registrado como não comprobatório e a execução é refeita após corrigir o ambiente

### Requirement: Reconciliação de política na retomada

Na retomada (Apply ou correção em sessão nova), o fluxo SHALL comparar as referências de política registradas no plano (caminhos e commit de leitura) com as instruções vigentes e registrar a reconciliação no handoff ou na issue. Instrução antiga MUST NOT ser aplicada silenciosamente contra a política atual.

#### Scenario: Política de Heavy Tests mudou entre proposta e Apply (T2)
- **WHEN** o plano proíbe Heavy Tests hospedados e a política vigente do repositório passou a exigi-los
- **THEN** o Apply registra a divergência, aplica o gate vigente e não trata a proibição antiga como válida

#### Scenario: Política inalterada
- **WHEN** nenhuma referência de política mudou desde o commit do plano
- **THEN** o registro indica "política inalterada" e nenhuma reconciliação é necessária

### Requirement: Precedência na reconciliação

Gates exigidos pela política vigente do repositório SHALL se aplicar mesmo que o plano os omita ou proíba. Obrigações explícitas validadas no OpenSpec que a política atual não exige MUST permanecer até revisão pelo fluxo OpenSpec. Divergência que altere comportamento, contrato ou critério de aceite MUST seguir o gate de revisão OpenSpec existente.

#### Scenario: Plano exige verificação extra que a política deixou de exigir
- **WHEN** o OpenSpec validado exige uma verificação que a política atual não exige mais
- **THEN** a verificação permanece obrigatória até uma revisão OpenSpec validada removê-la

### Requirement: Falha da base distinguida de regressão

Quando uma suíte falhar, o fluxo SHALL comparar com evidência da base em ambiente equivalente antes de classificar a falha como preexistente, registrando evidência comparável, origem provável e ação definida. Uma suíte exigida que falha MUST NOT ser declarada aprovada por ser falha preexistente.

#### Scenario: Falha preexistente (critério 6)
- **WHEN** a mesma falha ocorre na revisão base em ambiente equivalente
- **THEN** a falha é registrada como preexistente com evidência, origem e ação, e o gate exigido permanece reprovado ou bloqueado, não aprovado

#### Scenario: Regressão introduzida
- **WHEN** a falha não ocorre na base equivalente
- **THEN** a falha é tratada como regressão da mudança e corrigida no escopo

### Requirement: Escopo antes de alterar testes externos

Antes de alterar testes fora dos arquivos da mudança para corrigir uma falha, o fluxo MUST verificar se a correção cabe no escopo autorizado; caso contrário, MUST reportar bloqueio ou follow-up pelo fluxo existente.

#### Scenario: Correção fora do escopo
- **WHEN** a falha preexistente exige alterar testes de outro módulo não coberto pela issue
- **THEN** o fluxo registra o bloqueio ou follow-up em vez de alterar esses testes silenciosamente

### Requirement: Proporcionalidade

O pré-flight estendido SHALL ser aplicado somente quando houver impacto transversal ou execução cara. Mudança sem impacto transversal MUST NOT receber matriz extensa por padrão; mudança somente documental MUST usar validação documental/de pacote proporcional.

#### Scenario: Alteração documental (T4, critério 4)
- **WHEN** a mudança altera apenas documentação
- **THEN** o plano registra em uma linha a ausência de impacto transversal e a validação documental/de pacote aplicável, sem inventário de consumidores nem amostra representativa

### Requirement: Integração ao fluxo e à revisão

As skills de Explore, planejamento, Apply e auditoria de PR SHALL referenciar o pré-flight da política de testes compartilhada, sem criar nova etapa, comando de usuário ou checkpoint de aprovação. A revisão de PR MUST verificar que a rodada focal não foi apresentada como prova ampla, que divergências de política foram reconciliadas e que falhas preexistentes foram classificadas sem declarar aprovação de suíte exigida falhando. As cópias distribuídas da política MUST permanecer idênticas à fonte.

#### Scenario: Distribuição sincronizada
- **WHEN** a política fonte é alterada
- **THEN** todas as cópias embarcadas nas skills e no pacote do plugin são idênticas à fonte após a sincronização
