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

### Requirement: Fechamento preserva identidade da execução
Uma abertura com execução tipada SHALL ser fechada somente por `stage-end` com a mesma dupla `(kind, id)` e o mesmo par etapa/worker. Um término sem execução SHALL fechar somente abertura sem execução, preservando o emparelhamento legado. Execuções tipadas do mesmo par MUST ter IDs distintos durante todo o run, inclusive após fechamento. Término divergente e abertura que reutilize um ID MUST falhar sem alterar o registro.

#### Scenario: Término de outra execução recusado
- **WHEN** a etapa/worker abre a execução A e recebe `stage-end` com execução B ou sem identificador
- **THEN** o comando falha sem alterar o registro nem fechar A

#### Scenario: ID de execução não é reutilizado
- **WHEN** o mesmo par etapa/worker tenta iniciar outra execução com o mesmo `(kind, id)` no mesmo run
- **THEN** o comando recusa a nova abertura sem alterar o registro

### Requirement: Fonte e horário da observação
Toda observação SHALL registrar estado (`running`, `completed`, `failed`, `interrupted`, `unknown`), fonte, horário observado e horário de gravação. Um horário informado MUST ser ISO-8601 com fuso (`Z` ou offset), normalizado para UTC, não posterior ao horário de gravação além de uma tolerância curta e não anterior ao início do run; caso contrário o comando MUST falhar.

#### Scenario: Horário informado por callback
- **WHEN** um callback de término informa conclusão às 10:20 e o orquestrador grava às 10:25 com esse horário
- **THEN** a observação guarda 10:20 como horário observado e 10:25 como horário de gravação, e as métricas usam 10:20

#### Scenario: Horário futuro ou anterior ao run
- **WHEN** o horário informado é futuro ou anterior ao início do run
- **THEN** o comando falha sem alterar o registro

#### Scenario: Término anterior ao despacho
- **WHEN** a observação ou o término informado para um worker precede o despacho correspondente
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
- **THEN** a etapa do worker registra 30 minutos de trabalho, o despacho e a conclusão ficam ligados ao mesmo identificador de execução, e nenhuma duração de 2 segundos é reportada como trabalho do worker

### Requirement: Execução encerrada ou desconhecida é reconciliada
Quando uma observação confirmatória correlacionada a uma incarnação de etapa indicar `completed`, `failed`, `interrupted` ou `unknown`, uma etapa ainda aberta SHALL aparecer como pendente de reconciliação, nunca como ativa. Uma observação posterior `running` da mesma incarnação MUST NOT reativá-la sem nova abertura. Etapas sem observação correlacionada SHALL manter a medição legada até o fechamento ou relatório, marcadas como sem observação.

#### Scenario: Processo some sem relatório
- **WHEN** uma etapa aberta recebe observação confirmatória `unknown` ou `interrupted` às 10:10 e o relatório é gerado às 11:00
- **THEN** o trabalho registrado da etapa termina às 10:10, o estado verificado é desconhecido/interrompido e o resumo indica reconciliação pendente

#### Scenario: Processo encerrado antes de novo anúncio
- **WHEN** a observação confirmatória mais recente é `completed` mas a etapa ainda não foi encerrada
- **THEN** o estado verificado não é `working` e o bloqueio exibido é reconciliação pendente

### Requirement: Trabalho termina no horário terminal observado
O trabalho de intervalo aberto ou fechado SHALL terminar na primeira observação terminal confirmatória correlacionada, ou antes se a etapa fechar primeiro. Seu fim efetivo SHALL ser o menor entre observação terminal, `stage-end` (se fechado) e horário do relatório (se aberto). A sobreposição de esperas usada para descontar trabalho SHALL respeitar esse fim. `elapsed_seconds` de etapa fechada SHALL continuar medindo o tempo de parede até o fechamento administrativo.

#### Scenario: Fechamento tardio após callback terminal
- **WHEN** a etapa inicia às 10:00, recebe callback confirmatório `completed` às 10:30 e `stage-end` é registrado às 10:40
- **THEN** o trabalho da etapa é 30 minutos, inclusive após seu fechamento; `elapsed_seconds` pode mostrar 40 minutos de parede, e uma espera posterior a 10:30 não reduz o trabalho já encerrado

### Requirement: Observações pertencem à incarnação da execução
Cada abertura de etapa/worker SHALL ser uma incarnação distinta. Observação tipada SHALL confirmar somente a incarnação da mesma etapa, worker, tipo e ID; ausência de ID MUST NOT atuar como curinga para abertura tipada. Callback atrasado de outra execução MUST NOT alterar estado, duração, evidência incompleta, `last_confirmed`, `verified_at` ou próximo passo da incarnação atual, mesmo se chegar após seu início; MAY atualizar apenas a incarnação anterior identificável.

#### Scenario: Callback de A chega após abertura de B no mesmo par
- **WHEN** A e B usam a mesma etapa/worker com IDs distintos, A abre às 10:00 e fecha às 10:40, B inicia às 10:45 e um callback de A observado às 10:30 é gravado às 10:50
- **THEN** a observação é atribuída somente a A; B mantém seu estado sem observação, sua duração, próximo passo e campos de última confirmação sem dados de A

#### Scenario: Observação sem ID não confirma execução tipada
- **WHEN** B está aberto com ID tipado e chega uma observação sem ID ou com ID não correspondente à execução de B
- **THEN** B permanece sem confirmação, mesmo que a etapa e o worker coincidam

### Requirement: Observação sem execução exige janela inequívoca
Uma observação sem execução SHALL confirmar somente uma abertura sem execução da mesma etapa/worker cujo horário observado esteja entre a abertura e seu fechamento, sem ultrapassar a próxima abertura do par. Se não houver correspondência inequívoca, a observação SHALL permanecer histórica, sem alterar o estado ou a duração de nenhuma incarnação. Registros legados sem observações SHALL manter o emparelhamento e as métricas anteriores.

#### Scenario: Horário efetivo não identifica uma única abertura sem ID
- **WHEN** uma observação sem execução cai fora da janela de qualquer abertura sem execução ou em janela ambígua
- **THEN** nenhuma incarnação recebe confirmação, e o evento permanece no histórico

### Requirement: Classificação de esperas
O registro SHALL aceitar os motivos de espera `owner_input`, `dependency`, `ci`, `tests`, `review`, `environment`, `runtime_capacity`, `external` e `other`. Tempo em espera MUST ser excluído do trabalho da etapa e somado ao motivo correspondente; ao terminar a espera a etapa volta ao estado observado anterior, ou permanece sem confirmação quando não houver observação confirmatória.

#### Scenario: Usuário responde decisão após espera
- **WHEN** uma etapa com execução confirmada em andamento entra em espera `owner_input` às 10:00, a espera termina às 10:40 e a etapa termina às 11:00, tendo começado às 09:50
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

### Requirement: Observação de runtime não é veredito de prova
Estado observado e presença de relatório SHALL ser tratados apenas como fatos de runtime. O resumo MUST NOT rotular uma execução de teste como verificada ou aprovada com base em `--report present` ou em mera referência `evidence:<id>`; ele SHALL exibir a referência vinculada ou "não verificada". O veredito sobre a prova pertence à verificação do registro de evidência.

#### Scenario: Relatório presente sem evidência vinculada
- **WHEN** uma execução `test_run` tem término confirmado com relatório presente e nenhuma referência `evidence:` vinculada
- **THEN** o resumo mostra a execução como "não verificada", sem rótulo de aprovação

#### Scenario: Observação vinculada a evidência registrada
- **WHEN** uma observação informa `--evidence evidence:ev-20261104T031855Z-8da5fbe0`
- **THEN** a observação é aceita e a última observação confirmada exibe essa referência sem afirmar que a prova foi verificada

### Requirement: Progresso separado por issue
Cada issue SHALL manter ciclo, etapas e métricas próprios, mesmo quando várias entregas ocorrem na mesma sessão ou run. O registro MUST recusar abrir etapa, despacho ou espera num registro já finalizado, exigindo um registro da issue correta.

#### Scenario: Issue A mergeada, conversa continua na issue B
- **WHEN** o run da issue A é finalizado e o trabalho segue na issue B com o mesmo run ID
- **THEN** os ciclos e métricas de A e B são independentes no relatório e uma tentativa de abrir etapa no registro finalizado de A falha

### Requirement: Observação repetida não gera eventos redundantes
Uma observação idêntica à mais recente da mesma execução (mesmo estado, fonte, resultado, relatório, referência de log, evidência e próximo passo) SHALL atualizar apenas o horário de última confirmação, sem acrescentar um novo evento. Informação de prova nova MUST ser registrada, nunca deduplicada como idêntica.

#### Scenario: Runtime fornece callback de término
- **WHEN** o callback de término é registrado e a mesma observação é repetida em seguida
- **THEN** o registro contém uma única observação de término para a execução, com horário de última confirmação atualizado, e as métricas derivam do callback

#### Scenario: Nova evidência para mesmo estado
- **WHEN** uma observação posterior mantém estado e fonte, mas acrescenta `evidence:<id>`
- **THEN** a nova referência é registrada e aparece na última observação confirmada

### Requirement: Resumo simples de progresso
O relatório SHALL apresentar, por issue, etapa atual, estado verificado, última prova confirmada (estado, fonte, referência), bloqueio, próximo passo informado e horário da última verificação confirmatória. Campos sem dado MUST aparecer como indisponíveis, nunca estimados.

#### Scenario: Resumo com prova e próximo passo
- **WHEN** a issue tem observação confirmatória com referência de log e um próximo passo informado
- **THEN** o resumo Markdown e JSON exibe esses valores e o horário da verificação

#### Scenario: Sem observação
- **WHEN** a issue não possui observações
- **THEN** o resumo mostra estado sem observação e prova e verificação indisponíveis, sem alterar as métricas legadas

#### Scenario: Registro anterior à observação de runtime
- **WHEN** o relatório lê um registro `schema_version: 1` criado antes desta mudança
- **THEN** durações, esperas, retrabalho, evidências e ciclo existentes continuam legíveis com os mesmos valores, e apenas o novo estado verificado aparece como sem observação

### Requirement: Referências seguras de log
`--log-ref` SHALL aceitar URL HTTPS do host `github.com`, SHA de commit ou referência tipada `<esquema>:<identificador-seguro>`. URLs MUST recusar userinfo, porta, query, fragment, escapes percentuais e caminho inseguro; referências tipadas MUST recusar `http`, `https`, `file`, `@`, `//`, espaço e `?`, `=`, `&`, `#`. A validação de `--evidence` MUST permanecer independente desta regra.

#### Scenario: Referência tipada aceita
- **WHEN** uma observação informa `--log-ref runtime:task-7f3a`
- **THEN** a referência é registrada e exibida no relatório

#### Scenario: Referência com consulta ou espaço recusada
- **WHEN** a referência contém `?token=` ou espaço
- **THEN** o comando falha sem alterar o registro

#### Scenario: Credenciais embutidas ou http recusados
- **WHEN** a referência é `https://user:pass@example.com/x` ou `http://evil.example/x`
- **THEN** o comando falha sem alterar o registro

#### Scenario: URL GitHub com credenciais em consulta ou userinfo recusada
- **WHEN** `--log-ref` recebe `https://github.com/o/r?token=secret`, `https://github.com/o/r#fragment` ou `https://github.com/user:pass@evil.example/x`
- **THEN** o comando falha sem alterar o registro

### Requirement: Reconciliação e continuidade do orquestrador
O orquestrador SHALL reconciliar o estado com runtime e evidência antes de anunciar atividade ou conclusão, inclusive após interrupção, compactação ou retomada, preservando resultados desconhecidos. Ele MUST preferir notificações de término do runtime a polling sem finalidade, seguir as etapas sem exigir comando do usuário por etapa e só ampliar escopo quando autorizado.

#### Scenario: Retomada após compactação
- **WHEN** o orquestrador retoma uma issue com etapa aberta cuja execução não tem término observado
- **THEN** ele consulta a fonte suportada ou registra estado desconhecido antes de relatar progresso, e continua a etapa seguinte sem pedir novo comando ao usuário
