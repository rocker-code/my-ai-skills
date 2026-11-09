# Spec Delta

## ADDED Requirements

### Requirement: Transições instrumentadas pelo coordenador
O coordenador SHALL registrar início, despacho, término e esperas nas fronteiras reais do workflow por operação estruturada, sem exigir comandos do usuário por etapa. A operação SHALL receber identidade completa e horário efetivo; MUST NOT deduzir etapa de título, prosa, ativação isolada de skill ou ferramenta utilizada.

#### Scenario: Passagem de planejamento para implementação
- **WHEN** o coordenador verifica os gates, encerra o planejamento e despacha o worker de Apply
- **THEN** registra as transições correspondentes à issue/run e worker corretos, preservando o horário real do despacho e sem considerar o retorno imediato como término

#### Scenario: Uso isolado de uma skill
- **WHEN** uma sessão ativa uma skill sem contexto explícito de workflow instrumentado
- **THEN** nenhum run, etapa ou vínculo é criado apenas pela ativação

### Requirement: Vínculo automático validado
Ao obter a sessão executora, o coordenador SHALL estabelecer o vínculo da execução tipada com sessão e checkout pelo mesmo contrato de validação do vínculo manual. Falha de vínculo SHALL ficar explícita sem bloquear o desenvolvimento nem associar outra sessão por aproximação. IDs de sessão indisponíveis SHALL manter atividade desconhecida.

#### Scenario: Despacho disponibiliza sessão depois da abertura
- **WHEN** a etapa já foi aberta e a resposta do despacho disponibiliza o ID real da sessão executora
- **THEN** o coordenador valida o vínculo antes de confirmar atividade, sem criar nova etapa ou usar o ID da sessão coordenadora como substituto

#### Scenario: Execução anterior deixou vínculo
- **WHEN** o mesmo contexto de sessão já está vinculado a outra execução
- **THEN** a operação recusa substituir o vínculo silenciosamente e exige reconciliação e desvinculação exatas antes de prosseguir

### Requirement: Publicador único e recuperação de transições
Somente o coordenador SHALL publicar o registro canônico por issue/run. Transições aceitas SHALL sobreviver a interrupção com identidade de operação e ordem causal, distinguindo pendente de publicada. Observador, dashboard e workers MUST NOT publicar autonomamente; falha de instrumentação MUST NOT impedir o trabalho autorizado.

#### Scenario: GitHub indisponível no término da etapa
- **WHEN** uma transição válida é aceita localmente mas sua publicação falha
- **THEN** ela permanece pendente para retomada do coordenador, com horário efetivo preservado, sem aparecer como publicada ou bloquear outras tarefas

#### Scenario: Coordenador encerrado com sinais novos
- **WHEN** o observador coleta uma interrupção enquanto não há coordenador ativo
- **THEN** persiste somente metadados locais e o próximo coordenador reconcilia a execução antes de publicar; o observador não altera o comentário GitHub

### Requirement: Repetição idempotente de operações
Repetir uma operação com a mesma identidade e os mesmos dados SHALL produzir no máximo um efeito canônico, inclusive após resposta de publicação perdida. Reutilizar a identidade com dados diferentes SHALL falhar sem mutação. Um publicador concorrente ou mudança inesperada do registro SHALL causar conflito visível, não sobrescrita cega.

#### Scenario: Publicação concluída com resposta perdida
- **WHEN** o GitHub salva a transição mas a resposta se perde e o coordenador tenta novamente
- **THEN** o coordenador reconhece a identidade já publicada, confirma a pendência e não duplica abertura, espera, evidência ou duração

#### Scenario: Dois coordenadores cooperativos
- **WHEN** dois coordenadores tentam publicar no mesmo domínio de estado compartilhado
- **THEN** somente o detentor da posse de publicação escreve, e o outro informa conflito sem substituir o registro

### Requirement: Reconciliação sem promoção indevida de resultado
O coordenador SHALL reconciliar sinais OpenCode com a execução e seus gates antes de publicar observação ou término de etapa. Término de turno ou consulta de sessão inativa MUST NOT virar observação terminal da etapa. Sucesso de worker sem prova dos gates SHALL manter conclusão não verificada e reconciliação pendente.

#### Scenario: Agente termina resposta durante Apply
- **WHEN** a sessão emite sucesso de execução, mas o coordenador ainda não recebeu resultado de entrega que satisfaça os gates
- **THEN** a etapa não recebe `stage-end` nem observação terminal confirmatória baseada somente naquele sucesso

#### Scenario: Worker entrega resultado e evidência correlacionados
- **WHEN** o coordenador recebe término do worker e verifica identidade, resultado e evidência exigida para aquela etapa
- **THEN** registra observação e término compatíveis sem promover o resultado a aprovação de outras etapas ou testes

### Requirement: Esperas automáticas preservam origem e limites
O coordenador SHALL registrar suas esperas explícitas e converter pedido runtime em espera canônica somente quando identidade, início e resolução forem inequívocos. Pedidos simultâneos SHALL formar a união dos intervalos pertinentes, sem dupla contagem. Lacuna temporal SHALL permanecer não medida e MUST NOT fechar espera explícita de outra origem.

#### Scenario: Pedidos de autorização sobrepostos
- **WHEN** dois pedidos confirmados do mesmo worker têm intervalos sobrepostos e ambos são resolvidos sem lacunas de coleta
- **THEN** a espera canônica cobre a união dos intervalos, sem dobrar o tempo sobreposto nem terminar na primeira resposta

#### Scenario: Resolução perdida
- **WHEN** a resolução não foi observada e uma consulta atual apenas confirma ausência do pedido
- **THEN** o coordenador informa reconciliação e intervalo incompleto, sem inventar horário de resposta ou duração exata e sem encerrar espera explícita independente

### Requirement: Compatibilidade e ativação explícita
A instrumentação SHALL preservar registros `schema_version: 1`, tipos de evento e métricas existentes e permitir comandos manuais sem novos campos obrigatórios. Publicação automática SHALL exigir contexto explícito de workflow autorizado; a configuração do monitor por si só MUST NOT autorizar escrita GitHub ou alterar configuração real do usuário.

#### Scenario: Registro legado sem runtime
- **WHEN** um run antigo é lido ou registrado manualmente sem sessão OpenCode e sem identidade de operação
- **THEN** permanece utilizável com as mesmas métricas e sem criar vínculo, observador ou transição automática

#### Scenario: Dashboard autorizado apenas para leitura
- **WHEN** o usuário habilita coleta runtime para o monitor sem iniciar workflow executor
- **THEN** o sistema coleta os vínculos autorizados, mas não publica comentários nem inicia etapas
