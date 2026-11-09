# Spec Delta

## Purpose

Observar atividade e bloqueios verificáveis de sessões OpenCode vinculadas ao workflow, independentemente do dashboard, fornecendo metadados correlacionados para apresentação e reconciliação pelo coordenador.

## ADDED Requirements

### Requirement: Observação headless opt-in
O sistema SHALL oferecer coleta contínua sem TTY, independente do dashboard, somente com runtime habilitado e alvos explícitos. Iniciar o dashboard MUST NOT instalar ou iniciar um serviço persistente. Encerrar o observador MUST NOT interromper agentes, jobs ou testes.

#### Scenario: Painel fechado durante execução
- **WHEN** o observador está iniciado explicitamente e o usuário fecha todos os dashboards
- **THEN** a coleta continua e uma nova abertura do painel consegue consultar as observações com seu frescor real

#### Scenario: Configuração sem autorização de runtime
- **WHEN** o runtime está desabilitado ou não há alvos configurados
- **THEN** o comando informa a condição e não inicia assinatura, descoberta de sessões ou monitoramento de projetos

### Requirement: Contrato oficial fixado
O observador SHALL consumir somente interfaces oficiais conferidas para OpenCode 2.2.5, usando o contexto de servidor e autenticação oficial do vínculo. Versão incompatível SHALL suspender confirmação de runtime sem apagar histórico. MUST NOT ler banco interno ou capturar transcript para suprir ausência de contrato.

#### Scenario: Servidor atualizado sem adaptação
- **WHEN** CLI ou servidor declara release diferente do contrato fixado
- **THEN** o observador indica incompatibilidade e não confirma atividade, esperas ou resultados pela nova versão

### Requirement: Correlação por identidade e fronteira temporal
Cada sinal SHALL ser associado a vínculo validado de issue/run/etapa/worker/execução, sessão, checkout, contexto do servidor e revisão do vínculo. Eventos anteriores à ativação do vínculo ou de identidade ambígua MUST NOT confirmar a execução atual.

#### Scenario: Sessão reutilizada e evento atrasado
- **WHEN** a sessão passa da execução A para B e chega um término observado antes da ativação do vínculo de B
- **THEN** B não recebe término, atividade ou duração de A; o sinal só permanece histórico se A for identificável

#### Scenario: Sessão muda de checkout
- **WHEN** a localização ou identidade Git diverge do vínculo, mesmo dentro do mesmo projeto OpenCode
- **THEN** o vínculo deixa de confirmar atividade e exige reconciliação explícita, sem associação por nome de branch ou título

### Requirement: Eventos de execução não encerram etapas
O observador SHALL distinguir início, sucesso, falha e interrupção de execução da sessão, quando confirmados pelo contrato. Sucesso ou inatividade de sessão MUST NOT encerrar etapa, finalizar run, aprovar teste ou confirmar término de processo filho. O coordenador SHALL decidir a transição semântica mediante resultado correlacionado e evidência própria.

#### Scenario: Turno termina e etapa continua
- **WHEN** uma execução da sessão termina com sucesso mas a etapa ainda exige trabalho ou verificação
- **THEN** o dashboard deixa de afirmar atividade sem confirmação recente e a etapa permanece aberta, sem publicação automática de conclusão

### Requirement: Esperas observadas sem inferência de silêncio
O observador SHALL identificar permissão ou formulário pendente apenas em sessão vinculada e com associação verificável, distinguindo esses sinais dos motivos canônicos de espera. Inatividade isolada MUST NOT significar espera humana. Resolver um pedido MUST NOT encerrar outros pedidos nem esperas declaradas pelo coordenador.

#### Scenario: Dois pedidos na mesma sessão
- **WHEN** existem dois pedidos pendentes e somente um é respondido
- **THEN** a pendência remanescente continua visível com sua identidade e a resolução não libera toda a execução

#### Scenario: Sessão inativa sem pedido
- **WHEN** a consulta confirma sessão inativa sem permissão ou formulário pendente
- **THEN** o sistema mostra inatividade, não inventa motivo de espera nem registra duração de espera humana

### Requirement: Recuperação de lacunas sem horários inventados
Desconexão, reinício e perda por saturação SHALL invalidar continuidade do fluxo e provocar reconciliação por consulta oficial. O sistema SHALL separar horário do evento de horário de recebimento. Estado atual obtido por consulta MUST NOT reconstruir transições ou durações ausentes; lacunas SHALL permanecer explícitas.

#### Scenario: Resposta ocorreu durante desconexão
- **WHEN** um pedido era pendente, a conexão cai e a consulta após reconectar já não o encontra
- **THEN** a pendência atual é reconciliada, mas o sistema não inventa o instante da resposta nem apresenta aquele intervalo como medição completa

### Requirement: Coleta única e consumidores independentes
O sistema SHALL impedir dois observadores ativos no mesmo diretório de estado, permitir múltiplos dashboards e impedir que um dashboard substitua amostras de um observador saudável por respostas antigas. Perda de exclusividade ou erro de persistência SHALL ser visível e não renovar frescor.

#### Scenario: Segundo observador e dois painéis
- **WHEN** um observador já possui a exclusividade e outro tenta iniciar enquanto dois painéis leem o mesmo estado
- **THEN** o segundo observador é recusado, os painéis continuam navegáveis e nenhum agente é afetado

### Requirement: Minimização antes de persistir
O observador SHALL filtrar tipos e identidades e persistir somente metadados permitidos de correlação, estado, fonte e horário. MUST NOT persistir prompts, respostas, texto de formulário, respostas humanas, argumentos ou saídas de ferramentas, raciocínio, credenciais ou erros brutos, inclusive em filas de recuperação e diagnósticos.

#### Scenario: Evento contém conteúdo sensível
- **WHEN** um evento de falha ou formulário contém segredo, corpo de ferramenta ou texto humano
- **THEN** apenas identificadores e classificação permitidos chegam ao cache e aos diagnósticos; o conteúdo não é copiado para GitHub

### Requirement: Operação limitada e cancelável
O observador SHALL aplicar limites de tamanho e fila, timeouts e backoff, reconciliar periodicamente vínculos ativos e encerrar suas conexões de forma cancelável. Eventos de sessões não vinculadas MUST NOT gerar coleta de conteúdo nem publicação de workflow.

#### Scenario: Consumidor lento
- **WHEN** a entrada excede a capacidade de processamento ou um evento excede o limite aceito
- **THEN** a coleta sinaliza lacuna, descarta confirmação insegura e retoma por reconciliação limitada, sem crescimento ilimitado de memória ou disco
