# Spec Delta

## Purpose

Garante que o acompanhamento do workflow relate apenas o estado de execução confirmado no runtime, correlacione cada etapa/worker com a execução observada e mantenha progresso, esperas e resultados desconhecidos separados por issue.

## ADDED Requirements

### Requirement: Correlação de execução
O registro de eventos SHALL permitir associar run, issue, etapa e worker a um identificador de execução tipado (`worker`, `process`, `job`, `test_run`, `ci_run`) em eventos de despacho, observação e término de etapa. O identificador MUST ser um identificador seguro, sem espaços nem caracteres de consulta.

#### Scenario: Observação vinculada à etapa e ao worker
- **WHEN** o orquestrador registra uma observação com etapa `tests`, worker `worker-1`, tipo `test_run` e identificador `junit-42`
- **THEN** o registro da issue contém essa correlação e o relatório a exibe junto da etapa e do worker

#### Scenario: Identificador inseguro é recusado
- **WHEN** um evento informa identificador de execução com espaço, `?`, `=` ou `&`
- **THEN** o comando falha com erro de validação e o registro não é alterado

### Requirement: Fonte e horário da observação
Toda observação SHALL registrar estado (`running`, `completed`, `failed`, `interrupted`, `unknown`), fonte, horário observado e horário de gravação. Um horário informado MUST ser ISO-8601 UTC, não posterior ao horário de gravação além de uma tolerância curta e não anterior ao início do run; caso contrário o comando MUST falhar.

#### Scenario: Horário informado por callback
- **WHEN** um callback de término informa conclusão às 10:20 e o orquestrador grava às 10:25 com esse horário
- **THEN** a observação guarda 10:20 como horário observado e 10:25 como horário de gravação, e as métricas usam 10:20

#### Scenario: Horário futuro ou anterior ao run
- **WHEN** o horário informado é futuro ou anterior ao início do run
- **THEN** o comando falha sem alterar o registro

### Requirement: Sinais insuficientes não confirmam estado
As fontes SHALL ser classificadas como confirmatórias (evento de término do runtime, consulta suportada do runtime, API de CI, código de saída de processo, relatório de teste) ou insuficientes (prosa do agente, container ligado). Uma fonte insuficiente MUST NOT, isoladamente, tornar uma etapa ativa ou concluída no estado verificado.

#### Scenario: Prosa do agente afirma que a suíte roda
- **WHEN** a única observação após o início da etapa é `running` com fonte prosa do agente ou container ligado
- **THEN** o estado verificado da etapa é não confirmado e o resumo mostra o sinal como insuficiente

### Requirement: Despacho assíncrono preserva causalidade
Um despacho assíncrono SHALL abrir a etapa do worker no horário do despacho e MUST NOT ser tratado como conclusão. A duração da etapa do worker SHALL ir do despacho até o término confirmado do próprio worker, independentemente do retorno imediato da chamada de despacho.

#### Scenario: Worker retorna imediatamente e conclui depois
- **WHEN** o worker é despachado às 10:00, a chamada retorna às 10:00:02 e o callback de término confirma conclusão às 10:30
- **THEN** a etapa do worker tem 30 minutos de duração, o despacho e a conclusão ficam ligados ao mesmo identificador de execução, e nenhuma duração de 2 segundos é reportada como trabalho do worker

### Requirement: Execução encerrada ou desconhecida é reconciliada
Quando a observação confirmatória mais recente de uma etapa aberta indicar `completed`, `failed`, `interrupted` ou `unknown`, o trabalho registrado SHALL parar no horário dessa observação e a etapa MUST aparecer como pendente de reconciliação, nunca como ativa. Etapas sem nenhuma observação mantêm a medição até o relatório, marcadas como sem observação.

#### Scenario: Processo some sem relatório
- **WHEN** uma etapa aberta recebe observação confirmatória `unknown` ou `interrupted` às 10:10 e o relatório é gerado às 11:00
- **THEN** o trabalho registrado da etapa termina às 10:10, o estado verificado é desconhecido/interrompido e o resumo indica reconciliação pendente

#### Scenario: Processo encerrado antes de novo anúncio
- **WHEN** a observação confirmatória mais recente é `completed` mas a etapa ainda não foi encerrada
- **THEN** o estado verificado não é `working` e o bloqueio exibido é reconciliação pendente

### Requirement: Classificação de esperas
O registro SHALL aceitar os motivos de espera `owner_input`, `dependency`, `ci`, `tests`, `review`, `environment`, `runtime_capacity`, `external` e `other`. Tempo em espera MUST ser excluído do trabalho da etapa e somado ao motivo correspondente; ao terminar a espera a etapa volta ao estado de trabalho.

#### Scenario: Usuário responde decisão após espera
- **WHEN** uma etapa entra em espera `owner_input` às 10:00, a espera termina às 10:40 e a etapa termina às 11:00, tendo começado às 09:50
- **THEN** a espera `owner_input` soma 40 minutos, o trabalho registrado soma 30 minutos e, entre 10:40 e 11:00, o estado verificado é trabalho

#### Scenario: CI em andamento
- **WHEN** existe espera `ci` aberta
- **THEN** o estado verificado é espera por CI e o bloqueio exibido é `ci`

#### Scenario: Ambiente indisponível
- **WHEN** existe espera `environment` aberta
- **THEN** o estado verificado é espera por ambiente, distinto de espera por testes, decisão e desconhecido

### Requirement: Evidência incompleta não aprova
Uma execução de teste sem término confirmado, ou com término confirmado mas relatório ausente ou desconhecido, SHALL ser exibida como evidência incompleta. O fechamento da etapa como concluída MUST NOT ocultar essa marcação.

#### Scenario: Ausência de JUnit
- **WHEN** a observação de uma execução `test_run` confirma término com relatório ausente e a etapa é encerrada como concluída
- **THEN** o resumo lista a execução como evidência incompleta e a última prova confirmada não a apresenta como aprovação

### Requirement: Progresso separado por issue
Cada issue SHALL manter ciclo, etapas e métricas próprios, mesmo quando várias entregas ocorrem na mesma sessão ou run. O registro MUST recusar abrir etapa, despacho ou espera num registro já finalizado, exigindo um registro da issue correta.

#### Scenario: Issue A mergeada, conversa continua na issue B
- **WHEN** o run da issue A é finalizado e o trabalho segue na issue B com o mesmo run ID
- **THEN** os ciclos e métricas de A e B são independentes no relatório e uma tentativa de abrir etapa no registro finalizado de A falha

### Requirement: Observação repetida não gera eventos redundantes
Uma observação idêntica à mais recente da mesma execução (mesmo estado e fonte) SHALL atualizar apenas o horário de última confirmação, sem acrescentar um novo evento.

#### Scenario: Runtime fornece callback de término
- **WHEN** o callback de término é registrado e a mesma observação é repetida em seguida
- **THEN** o registro contém uma única observação de término para a execução, com horário de última confirmação atualizado, e as métricas derivam do callback

### Requirement: Resumo simples de progresso
O relatório SHALL apresentar, por issue, etapa atual, estado verificado, última prova confirmada (estado, fonte, referência), bloqueio, próximo passo informado e horário da última verificação confirmatória. Campos sem dado MUST aparecer como indisponíveis, nunca estimados.

#### Scenario: Resumo com prova e próximo passo
- **WHEN** a issue tem observação confirmatória com referência de log e um próximo passo informado
- **THEN** o resumo Markdown e JSON exibe esses valores e o horário da verificação

#### Scenario: Sem observação
- **WHEN** a issue não possui observações
- **THEN** o resumo mostra estado sem observação e prova e verificação indisponíveis

### Requirement: Referências seguras de log
Referências de log e evidência de observação SHALL ser URL GitHub, SHA de commit ou referência tipada `<esquema>:<identificador-seguro>`. Valores com espaço, caracteres de consulta ou credenciais embutidas MUST ser recusados.

#### Scenario: Referência tipada aceita
- **WHEN** uma observação informa `runtime:task-7f3a` ou `m2t:run-20261104-01`
- **THEN** a referência é registrada e exibida no relatório

#### Scenario: Referência com consulta recusada
- **WHEN** a referência contém `?token=` ou espaço
- **THEN** o comando falha sem alterar o registro

### Requirement: Compatibilidade com registros antigos
Registros `schema_version: 1` sem os novos eventos SHALL continuar legíveis, com as mesmas durações, esperas, retrabalho e ciclo de antes. Os novos campos MUST ser aditivos no mesmo schema.

#### Scenario: Registro antigo
- **WHEN** o relatório lê um registro gravado antes desta mudança
- **THEN** os valores existentes são idênticos aos anteriores e o estado verificado aparece como sem observação

### Requirement: Reconciliação e continuidade do orquestrador
O orquestrador SHALL reconciliar o estado com runtime e evidência antes de anunciar atividade ou conclusão, inclusive após interrupção, compactação ou retomada, preservando resultados desconhecidos. Ele MUST preferir notificações de término do runtime a polling sem finalidade, seguir as etapas sem exigir comando do usuário por etapa e só ampliar escopo quando autorizado.

#### Scenario: Retomada após compactação
- **WHEN** o orquestrador retoma uma issue com etapa aberta cuja execução não tem término observado
- **THEN** ele consulta a fonte suportada ou registra estado desconhecido antes de relatar progresso, e continua a etapa seguinte sem pedir novo comando ao usuário
