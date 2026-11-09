# Spec Delta

## MODIFIED Requirements

### Requirement: Contadores e filtros sem estimativas
Cada cabeçalho SHALL identificar projeto, milestone, contadores exclusivos e conclusão GitHub/total, com repositório em sublinha do cartão ou contexto visível do viewport. SHALL preservar totais do inventário independentemente do filtro. Filtros SHALL incluir todas, executando, pendentes, bloqueadas e concluídas, mantendo subestados legíveis sem dupla contagem.

#### Scenario: Filtro bloqueadas
- **WHEN** o usuário filtra bloqueadas em um milestone com issues fechadas e abertas
- **THEN** aparecem somente as bloqueadas, mas o percentual e os totais do cabeçalho continuam baseados no inventário completo

## ADDED Requirements

### Requirement: Hierarquia visual por projeto
A TUI SHALL apresentar cada milestone em cartão com título e identidade de repositório em sublinha, mantendo a ordem recebida e contexto de projeto visível durante a rolagem. Bordas, cabeçalhos e separadores decorativos MUST NOT virar alvos de navegação nem alterar identidades, filtros ou sanfonas persistidas.

#### Scenario: Navegar entre projetos
- **WHEN** o painel contém milestones de três repositórios e o usuário navega entre eles
- **THEN** a sublinha de cada cartão identifica seu repositório sem misturá-lo ao título, preservando a ordem recebida mesmo quando projetos se intercalam
- **AND** j/k percorre somente milestones e issues, preservando as sanfonas independentes

#### Scenario: Rolagem com seleção no meio de um projeto
- **WHEN** a lista rola até ocultar o cabeçalho do cartão selecionado
- **THEN** o viewport mantém identificação inequívoca do projeto dos itens visíveis
- **AND** a seleção e a régua da issue selecionada continuam visíveis em navegação normal

### Requirement: Colunas e espaçamento responsivos
A TUI SHALL separar visualmente milestones, issues e rodapé. Em largura ampla, SHALL usar tabela Issue / Workflow / Status / Tempo com colunas alinhadas. Em largura reduzida, SHALL empilhar campos sem sobreposição, preservando número, estado, conclusão e etapa atual; títulos longos SHALL indicar truncamento. Decoração SHALL ceder espaço à seleção em terminais baixos.

#### Scenario: Terminal largo com títulos diferentes
- **WHEN** o painel usa 238×54 células com títulos de comprimentos variados
- **THEN** progresso e contadores compartilham posições horizontais, separadas do título
- **AND** há separação visível entre milestones e entre o conteúdo e as teclas do rodapé

#### Scenario: Terminal estreito e títulos Unicode
- **WHEN** o terminal muda entre 238×54, 110×30, 80×24 e 40×12 com títulos Unicode longos
- **THEN** não há escrita além da largura disponível nem colisão de campos
- **AND** a issue selecionada mostra seu estado e etapa atual, com abreviações quando necessário
- **AND** os limites mínimos de 8×3 e 1×1 não causam erro de renderização

### Requirement: Estilos semânticos com fallback textual
A TUI SHALL distinguir seleção, conclusão, execução confirmada, pendência, bloqueio e espera humana por rótulos ou marcas, com cor opcional. A régua SHALL usar pílulas de etapas e badges de status, distinguindo atual, concluídas e futuras. O destaque de seleção MUST NOT apagar essa distinção nem sugerir atividade confirmada apenas por uma etapa atual registrada.

#### Scenario: Atual e concluída na mesma régua
- **WHEN** uma issue contém etapas concluídas, uma atual e etapas sem registro
- **THEN** a atual usa marca própria e ênfase distinta, as concluídas mantêm sua marca e as demais não recebem conclusão implícita

#### Scenario: Sem cor ou inicialização de cor indisponível
- **WHEN** o usuário ativa --no-color ou o terminal não permite inicializar cores
- **THEN** seleção, estados e etapas continuam distinguíveis por texto, marcas e atributos suportados
- **AND** --ascii remove dependência de caracteres Unicode decorativos

### Requirement: Detalhes e saúde visualmente separados
A TUI SHALL organizar os detalhes da issue em seções identificadas de execução, entrega e fontes, distinguindo metadados secundários de status. O cabeçalho SHALL separar filtro e saúde das fontes de progresso, sem ocultar erro, cache vencido ou ausência de inventário nem representar dados ausentes como fatos confirmados.

#### Scenario: Issue com falha de fonte e detalhes extensos
- **WHEN** o usuário abre detalhes de uma issue enquanto uma fonte está indisponível
- **THEN** as seções preservam horários UTC, referências e avisos existentes e são consultáveis por rolagem
- **AND** o erro da fonte não se mistura ao título ou aos contadores de progresso
- **AND** histórico altera somente os detalhes, sem modificar totais atuais

### Requirement: Composição visual baseada na referência
A TUI SHALL aproximar a imagem fornecida pelo usuário com título/subtítulo, quatro cartões de indicadores, faixa de totais/filtros, cartões contornados de milestones e rodapé com teclas destacadas. Em terminal compatível SHALL usar fundo escuro, texto claro, bordas ciano, conclusão verde, execução azul/ciano, pendência cinza e bloqueio âmbar, sem depender de fontes ou ícones externos.

#### Scenario: Composição em terminal amplo
- **WHEN** o painel é renderizado em 238×54 com cor e Unicode disponíveis
- **THEN** apresenta os elementos na mesma ordem vertical da referência, com quatro indicadores lado a lado, bordas finas, títulos em negrito e respiros entre cartões
- **AND** o foco não inverte todo o cartão nem torna ilegíveis os estados coloridos
- **AND** não copia o selo DEMO, a versão v0.3.0 nem valores fictícios para o painel operacional

#### Scenario: Tema e glifos indisponíveis
- **WHEN** o terminal limita cores ou o usuário ativa --ascii ou --no-color
- **THEN** o painel conserva a hierarquia por bordas, alinhamento e palavras, usando equivalentes suportados sem exigir troca de fonte ou configuração do terminal

### Requirement: Indicadores globais sem distorção por filtro
Os quatro indicadores SHALL mostrar concluídas, executando, pendentes e bloqueadas do inventário monitorado, junto aos totais de milestones/issues. SHALL permanecer independentes do filtro e da expansão. Dados ausentes ou vencidos SHALL manter aviso explícito; totais parciais MUST NOT aparentar inventário completo confirmado.

#### Scenario: Filtrar e recolher cartões
- **WHEN** o usuário muda o filtro e recolhe todos os milestones de um inventário conhecido
- **THEN** os quatro indicadores e totais globais não mudam, e o filtro ativo permanece destacado entre as cinco opções existentes

#### Scenario: Inventário parcialmente indisponível
- **WHEN** um alvo monitorado não tem inventário disponível ou possui cache vencido
- **THEN** o resumo identifica a cobertura parcial ou o cache vencido junto aos valores conhecidos, sem transformar ausência de dados em zero confirmado

### Requirement: Barra segmentada e conclusão factual
Cada cartão SHALL mostrar barra de distribuição dos estados exclusivos e percentual issues fechadas/total. Segmentos de execução e bloqueio MUST NOT aumentar conclusão. Sem issues ou sem inventário SHALL apresentar percentual indisponível e rótulo correspondente, sem barra que sugira progresso conhecido.

#### Scenario: Execução não conta como conclusão
- **WHEN** um milestone possui cinco issues, uma fechada, duas executando, uma pendente e uma bloqueada
- **THEN** a barra representa essa distribuição, e a conclusão textual é 20% (1/5), independentemente do filtro

#### Scenario: Vazio e ausência de inventário
- **WHEN** há milestone conhecido sem issues e outro sem inventário
- **THEN** ambos têm percentual indisponível, mas o primeiro indica vazio 0/0 e o segundo indica sem inventário, sem equivalência factual entre eles

### Requirement: Etapas e tempo reais na tabela
A tabela SHALL preservar as etapas reais pt-BR e seus significados, mesmo quando abreviadas ou parcialmente visíveis por falta de largura. Tempo SHALL identificar trabalho canônico registrado do run atual, sem confundir com calendário ou atividade contínua; ausência SHALL aparecer como indisponível. A aparência da referência MUST NOT reduzir o protocolo a oito etapas nem fabricar conclusões.

#### Scenario: Protocolo completo e janela da etapa atual
- **WHEN** uma issue tem registro em Aplicar sem evidência das etapas anteriores
- **THEN** Aplicar fica visível como atual registrada e as anteriores permanecem sem registro, com indicação de etapas ocultas quando houver recorte
- **AND** os detalhes mantêm nomes completos, etapas desconhecidas, paralelismo e rework consultáveis

#### Scenario: Trabalho registrado versus calendário
- **WHEN** uma issue tem trabalho canônico de 120 segundos e calendário de 600 segundos, e outra não tem telemetria
- **THEN** a coluna Tempo registrado mostra 2min para a primeira e indisponível para a segunda, sem incremento local ou estimativa
- **AND** detalhes preservam ambos os tempos em segundos e suas fontes, e histórico não altera o resumo do run atual

### Requirement: Enquadramento e acabamento de cartões
Na navegação normal, cartões recolhidos que cabem no viewport SHALL aparecer completos, sem borda órfã no rodapé. Contexto fixo SHALL aparecer somente quando título e repositório do cartão no topo estiverem ocultos. Foco SHALL ser distinto da sanfona; 0% e segmentos pendentes SHALL ser neutros/discretos. Em largura ampla SHALL usar contadores com rótulos, mantendo estados, totais e avisos de saúde.

#### Scenario: Navegar uma lista longa recolhida
- **WHEN** o usuário navega para o primeiro, intermediários e último de 40 milestones recolhidos em terminal largo
- **THEN** o cartão selecionado aparece completo, sem contexto duplicado nem começo isolado de outro cartão junto ao rodapé
- **AND** 0% não recebe destaque verde e contadores usam rótulos por extenso

#### Scenario: Rolagem dentro de detalhes extensos
- **WHEN** a rolagem oculta título e repositório do cartão no topo
- **THEN** o contexto fixo identifica esse cartão, sem impedir a consulta de detalhes ou esconder a etapa atual em navegação normal
