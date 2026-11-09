# Tasks

## 1. Frame semântico e cartões de milestones

- [x] 1.1 Introduzir linhas/spans semânticos em `tui.py`, manter adaptador `render` textual e construtor único de tokens da régua; verificar igualdade entre texto do frame e adaptador e testes existentes de régua/semântica.
- [x] 1.2 Compor cartões contornados com sanfona, número/título, repositório em sublinha e contexto de rolagem, sem cabeçalhos externos redundantes ou novos itens selecionáveis; verificar ordem recebida com três projetos intercalados, seleção por identidade, sanfonas/filtros persistidos e ASCII.
- [x] 1.3 Atualizar `docs/milestone-monitor.md` e `.en.md` sobre cartões, hierarquia e contexto, sem mudar teclas/configuração; verificar paridade e correspondência com o frame.

## 2. Marca, indicadores e barras da referência

- [x] 2.1 Implementar marca `>_`, título/subtítulo e quatro cartões globais, totais de milestones/issues e cinco filtros com ativo destacado; verificar fixture conhecida, invariância sob filtro/expansão e aviso de cobertura parcial/cache vencido, sem selo DEMO ou versão copiada.
- [x] 2.2 Implementar barras segmentadas de largura fixa e percentual fechado/total nos cartões; verificar distribuição 1/2/1/1 com 20% (1/5), arredondamento por células, contadores largos e distinção entre vazio conhecido e sem inventário, sem alterar o modelo.
- [x] 2.3 Documentar indicadores, cobertura, barras e conclusão factual em pt-BR/en; conferir exemplos ilustrativos contra fixtures e explicar que execução não aumenta conclusão.

## 3. Tabela de issues, pílulas e tempo registrado

- [x] 3.1 Compor tabela Issue / Workflow / Status / Tempo registrado em ≥180 colunas, com divisores, pílulas e badges por spans; verificar alinhamento em 238×54, títulos Unicode longos, subestados e ausência de conclusão implícita nas 13 etapas pt-BR.
- [x] 3.2 Resumir tempo canônico do run atual em segundos/minutos/horas, sem estimativa nem incremento local; verificar 120s versus 600s de calendário, zero válido, ausência, trabalho paralelo e invariância sob histórico/filtro.
- [x] 3.3 Organizar detalhes em Execução/Entrega/Fontes e faixa de saúde separada; verificar preservação de todos os campos/avisos/UTC, nomes completos de etapas, rework/paralelismo, falhas de fonte, histórico e ausência de telemetria.
- [x] 3.4 Atualizar documentação pt-BR/en sobre tabela, legenda das pílulas, tempo registrado e detalhes; verificar exemplos contra testes e distinção entre etapa registrada, atividade confirmada e entrega verificada.

## 4. Tema, acabamento e adaptação de terminal

- [x] 4.1 Aplicar tema escuro, bordas ciano, texto claro, verde/azul/cinza/âmbar e foco restrito a título/contorno; verificar screen fake em cores estendidas, 8 cores, --no-color, --ascii e falha de inicialização, sem redefinir paleta ou configurações do terminal.
- [x] 4.2 Implementar tabela em duas linhas para 120–179 colunas, layouts compacto/estreito abaixo disso, redução de indicadores/decoração por altura, truncamento explícito e rodapé com teclas destacadas; verificar limites por células em 179/180 colunas, 110×30, 80×24, 40×12, 8×3 e 1×1.
- [x] 4.3 Adicionar fixtures determinísticas de 40 milestones/3 projetos e composição de quatro cartões com primeiro expandido; verificar primeira/última seleção, mudança de ordem, filtros, scroll detalhado, etapa atual visível após resize e nenhuma alteração nos totais/modelo.
- [x] 4.4 Documentar tema, fallback, layouts, truncamento e limites de fidelidade gráfica em pt-BR/en; verificar paridade, ausência de novas dependências e manutenção das teclas/configuração existentes.

## 5. Verificação visual integrada e distribuição

- [x] 5.1 Executar testes focados `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_milestone_monitor*py'` e suíte completa `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`; verificar retorno zero e registrar evidências do candidato exato.
- [x] 5.2 Executar smoke curses em servidor tmux isolado com fixtures/cache temporários, navegando sanfonas/detalhes/filtros e resize 238×54→110×30→80×24→40×12, com/sem cores/ASCII; verificar capturas ANSI/textuais legíveis e saída normal sem tocar `mobile:1.0` ou banco/config reais.
- [x] 5.3 Comparar visualmente capturas do candidato exato com a imagem do usuário e a matriz D5 de `design.md`, conferindo composição, indicadores, contornos, barras, tabela, pílulas/badges, cores, espaçamento e rodapé; registrar diferenças inevitáveis de terminal/protocolo e corrigir divergências não justificadas, solicitando reenvio da imagem se estiver indisponível antes de afirmar fidelidade visual validada.
- [x] 5.4 Regenerar distribuição com `scripts/sync-plugin` e conferir segunda execução sem diff adicional, validar `openspec validate improve-milestone-monitor-readability --strict --json --no-interactive` e diff check; verificar demo offline intacta e nenhuma mudança de contrato de dados/API.

## 6. Polimento após uso real

- [x] 6.1 Enquadrar cartões recolhidos completos na navegação, mostrar contexto apenas quando título/repositório estiverem ocultos e evitar cartão/borda órfãos no rodapé; verificar regressões de rolagem, detalhes, resize e fixture de 40 milestones predominantemente em 0%.
- [x] 6.2 Reduzir vãos externos, usar contadores por extenso em largura ampla, foco distinto da sanfona e barras pendentes/0% discretos; verificar papéis semânticos, alinhamento, limites de células e comparação visual isolada com a captura do usuário.
- [x] 6.3 Atualizar documentação pt-BR/en, sincronizar distribuição e verificar idempotência, suítes focada/completa, smoke tmux isolado e validação OpenSpec estrita; registrar evidências do candidato sem tocar painel/config/cache reais nem mascarar avisos de saúde.

## Workflow follow-up

- Revisar a implementação contra o plano e os cenários antes de arquivar; cumprir gates do repositório para a revisão exata.
- Arquivar/sincronizar OpenSpec após verificação aprovada e revisar o resultado na mesma PR, se houver publicação autorizada.
- Informar ao usuário quando a mudança estiver disponível; recarregar o dashboard somente por ação voluntária dele, sem encerrar o processo atual.
