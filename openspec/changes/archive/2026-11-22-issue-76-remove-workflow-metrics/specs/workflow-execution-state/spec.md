## REMOVED Requirements

### Requirement: Correlação de execução
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Fechamento preserva identidade da execução
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Fonte e horário da observação
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Sinais insuficientes não confirmam estado
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Despacho assíncrono preserva causalidade
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Execução encerrada ou desconhecida é reconciliada
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Trabalho termina no horário terminal observado
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Observações pertencem à incarnação da execução
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Observação sem execução exige janela inequívoca
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Classificação de esperas
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Evidência incompleta não aprova
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Observação de runtime não é veredito de prova
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Progresso separado por issue
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Observação repetida não gera eventos redundantes
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Resumo simples de progresso
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Referências seguras de log
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

### Requirement: Reconciliação e continuidade do orquestrador
**Reason**: Contrato do coletor de eventos/métricas descontinuado pela #76.
**Migration**: Preservar histórico; usar fontes nativas e provas existentes sem comentários operacionais nem cálculo de duração.

## ADDED Requirements

### Requirement: Estado confirmado por fontes existentes
O acompanhamento SHALL usar runtime suportado, Git/GitHub/OpenSpec, posse do checkout e provas de testes existentes para distinguir execução em andamento, concluída, falha, interrompida e desconhecida. Prosa do agente, container ligado ou ausência de eventos MUST NOT confirmar sucesso. O fluxo MUST NOT criar coletor, banco ou registro de comentários substituto.

#### Scenario: Worker sem término confirmado
- **WHEN** uma retomada encontra worker sem callback, consulta suportada ou prova suficiente de término
- **THEN** o resultado permanece desconhecido e a ação dependente fica bloqueada sem perder o trabalho

### Requirement: Correlação e continuidade sem telemetria
A retomada SHALL correlacionar repositório, issue, checkout, worker/execução quando disponíveis e SHA efetivo nas fontes existentes. Resultado de outra execução ou HEAD antigo MUST NOT aprovar a execução atual. O fluxo SHALL preservar uma issue ativa por fila e um writer por checkout, sem exigir comando do usuário em cada etapa.

#### Scenario: Resultado atrasado e checkout ocupado
- **WHEN** chega resultado de worker anterior ou outra sessão possui o checkout
- **THEN** a execução atual não é aprovada e a escrita fica bloqueada até reconciliação verificável

### Requirement: Progresso atual sem analytics
Consultas de progresso SHALL apresentar entrega, atividade confirmada, bloqueios e próximo passo de cada issue por evidência atual. Dado indisponível MUST permanecer indisponível. O fluxo MUST NOT calcular tempos de etapas, esperas, retrabalho, percentis ou custos, nem ler comentários legados como fonte ativa.

#### Scenario: Milestone sem registros de métricas
- **WHEN** a pessoa consulta um milestone contendo issues com PR, CI e dependências conhecidas
- **THEN** o resumo exibe estados atuais e próximo passo sem colunas ou seções de tempo e cobertura de métricas

### Requirement: Prova de teste independente da observação
Término de processo e presença de relatório SHALL permanecer fatos de runtime, sem substituir verificação de conteúdo, identidade e resultado exigida pela política de testes. Ausência de término ou relatório necessário MUST NOT resultar em aprovação; preservar workflow-evidence e confirmação de CI no SHA efetivo.

#### Scenario: Término sem relatório necessário
- **WHEN** um teste termina mas seu relatório obrigatório está ausente, ou pertence a outro HEAD
- **THEN** a prova é incompleta e a entrega não é aprovada por esse sinal
