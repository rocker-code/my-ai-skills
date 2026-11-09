# Design

## Context

Ver `proposal.md` para a motivação. Base inspecionada: `dc9c3e4` (PR #45 integrada). Captura read-only de `mobile:1.0` em 238×54 mostrou 40 milestones configurados, títulos com repositório repetido, stats sem colunas e nenhuma separação entre blocos; o Mobile ainda tinha itens «sem inventário». Essa captura prova o layout, não o frescor nem a conclusão da coleta.

Revisão aprovada pelo usuário após fornecer «Image 1» na conversa: a referência passa a orientar composição e acabamento, não apenas legibilidade. A imagem não é um arquivo versionado no checkout; a descrição e a matriz abaixo preservam as decisões para implementação futura. Nenhum arquivo Figma ou interface web integra esta entrega. Inspeção atual de `tui.py`, `projection.py`, testes e documentação confirma curses stdlib, 13 etapas reais pt-BR, cinco filtros e tempos canônicos disponíveis em `summary`.

`scripts/milestone_monitor/tui.py` já separa `UIState`, `ruler`, `detail_lines` e `render` do loop curses. `render` retorna pares identidade/texto; `dashboard` aplica reverso à seleção e negrito aos milestones. A única color pair inicializada (cyan) não é aplicada. `UIState.rows` fornece identidades estáveis e não deve receber linhas decorativas. `projection.model` já oferece repositório, totais, labels e saúde: não há necessidade de alterar a projeção ou o banco.

`tests/test_milestone_monitor_tui.py` cobre sanfonas, filtros, Unicode, terminais mínimos, régua atual no viewport, histórico, expiração e background. A demo offline tem mais hierarquia visual, mas suas etapas e conclusão implícita não são contrato operacional reutilizável.

## Goals / Non-Goals

**Goals:**
- Aproximar a referência em estrutura, paleta, cartões, barras, pílulas, badges, alinhamento e respiros, aproveitando a largura sem misturar título e estado.
- Preservar navegação, identidades, histórico, termos auditáveis e configuração existente.
- Fazer o layout e os estilos testáveis sem terminal e confirmar resultado curses em tmux isolado.

**Non-Goals:**
- Acelerar coleta, mudar TTL, cache, eventos, projeção, bind, configuração ou esquema SQLite.
- Criar interface web, novas dependências, aliases persistidos de repositório, novas sanfonas por projeto ou filtros por projeto.
- Reiniciar/enviar teclas ao painel do usuário, parar agentes ou modificar alvos configurados.
- Reproduzir pixels, fontes, logos vetoriais, gradientes, sombras ou antialiasing de interface gráfica; exigir Nerd Fonts, alterar tema do tmux/terminal ou copiar dados, selo DEMO e versão da imagem.

## Decisions

### D1 — Cartões de milestones com contexto de repositório

Cada milestone recebe contorno próprio com `╭─╮│╰─╯`, triângulo de sanfona, número/título em negrito e sublinha de repositório. Usar identidade completa `owner/repo`, sem apelidos inferidos. Preservar a ordem do modelo, inclusive projetos intercalados: substitui-se o agrupamento externo previsto antes da referência. O cartão já fornece contexto; não acrescentar cabeçalho externo redundante por projeto. Ao rolar para dentro de um cartão, repetir contexto compacto de milestone/repositório no topo do conteúdo. Em ASCII usar `+ - | > v`; decoração não recebe identidade navegável própria.

Alternativa rejeitada: inserir uma nova sanfona selecionável de projeto, pois mudaria persistência, teclas e modelo mental sem necessidade. Apenas remover o repositório de cada linha sem contexto fixo perderia identidade ao rolar.

### D2 — Tabela ampla e redução responsiva por células

Margem de uma célula e uma linha entre cartões quando houver espaço. Em ≥180 colunas, reservar aproximadamente 29% para Issue, 49% para Workflow e o restante para Status e Tempo registrado, recalculando orçamentos mínimos por células antes de truncar títulos. Separadores discretos entre linhas e cabeçalho da tabela apenas em cartão expandido. As 13 etapas exigem rótulos curtos ou janela explícita da régua mesmo em 238 colunas; o atual permanece visível e os nomes completos ficam nos detalhes. Em 120–179, issue/status/tempo ficam na primeira linha e workflow na seguinte; em 80–119, título, progresso/contadores e issues usam linhas compactas; em <80, campos empilhados com `C/E/P/B`. Reservar largura para números de vários dígitos, sem percentual ou badge colidindo com título.

O viewport tem orçamento explícito para marca, indicadores, filtros/saúde, contexto, conteúdo e rodapé. Em altura insuficiente, remover logo decorativo, converter cartões globais em resumo de uma linha, reduzir bordas/respiros e compactar atalhos antes de sacrificar seleção e etapa atual. Em 40×12 priorizar identidade, estado e etapa; 8×3 e 1×1 degradam sem erro, sem promessa de todos os campos simultâneos. Reticências `…`/`...` e indicadores de etapas ocultas são explícitos; nunca partir caracteres de largura dupla.

Alternativas rejeitadas: manter texto corrido, limitar todas as issues a 120 células (afasta da tabela da referência), comprimir 13 nomes completos numa linha ilegível ou exigir largura mínima grande.

### D3 — Modelo de apresentação com papéis e spans

Adicionar estrutura leve de linha/span (texto, papel semântico, identidade e tipo) somente em `tui.py`. Separar composição do frame e desenho curses. Manter `render` como adaptador de texto plano para os testes e consumidores internos existentes; o frame rico carrega os mesmos textos e identidades. Assim, estágio atual, concluído e futuro podem ter atributos distintos na mesma linha. `ruler` continua oferecendo sua saída textual e usa o mesmo construtor de tokens que o frame para evitar divergência.

Papéis: título claro/negrito, bordas/contexto ciano, concluída verde, execução confirmada azul/ciano, pendência cinza/claro atenuado, bloqueio e espera humana âmbar/amarelo; falha pode usar vermelho nos detalhes sem mudar o agrupamento. Pílulas `[+ Explorar]`, `[> Aplicar]`, `[. Testes]` recebem atributos por token e badges de estado mantêm texto/subestado. Etapa atual registrada não ganha selo de execução confirmada só pela posição. Seleção usa marcador textual e ênfase restrita ao título/contorno, nunca reverso em todo o cartão. Cor é reforço, não prova.

Tema escuro dentro da aplicação, com preto e texto claro quando suportado, sem mudar paleta global nem configurações do terminal. Usar cores estendidas para aproximar verde vivo/azul/cinza/âmbar quando disponíveis, sem exigir 256 cores ou redefinir cores do usuário; fallback de 8 cores preserva os papéis. Falha em `start_color`, `use_default_colors` ou pairs degrada com segurança para monocromático. Sem cor herda o fundo do terminal. Ícones Unicode simples e medidos por células, sem emojis de largura ambígua ou fontes externas. Não alterar sanitização de controles.

Alternativa rejeitada: identificar estilos fazendo parsing do texto renderizado ou pintando toda a régua de uma única cor, pois isso mistura conteúdo e semântica.

### D4 — Detalhes por seções, sem alterar evidências

Separar detalhes em «Execução», «Entrega» e «Fontes», com sublinhas indentadas de workers e horários. Preservar todos os fatos de `detail_lines`, avisos, UTC, run/histórico e «referência não implica aprovação». Sem tempos novos ou resumo que esconda conflitos. Cabeçalho global compacto mostra título, filtro e saúde, com divisor; erros ficam numa faixa de aviso própria, orçamentada no viewport. «Sem inventário» não ganha percentual zero factual ou status recente por efeito visual.

Alternativa rejeitada: mover saúde só para os detalhes, pois esconderia indisponibilidade do painel recolhido. Não introduzir painel lateral nesta entrega para evitar dois modelos de foco/rolagem.

### D5 — Mapa da referência e composição ilustrativa

Mapa normativo de intenção visual; as adaptações preservam contratos operacionais:

| Elemento da imagem | Tradução para terminal |
| --- | --- |
| Logo terminal, marca e subtítulo | Marca textual `>_`, título em negrito, subtítulo discreto; sem versão copiada |
| Quatro indicadores | Cartões contornados com ícone/marca, número destacado e rótulo; quatro lado a lado em ≥120, 2×2 em 80–119 se a altura permitir |
| Total e filtros | Totais à esquerda e cinco filtros existentes à direita quando couber; ativo entre colchetes |
| Milestone expandido/recolhido | Contorno ciano, título/subtítulo, contadores e barra segmentada; tabela só quando aberto |
| Workflow e status | Pílulas semânticas e badge textual, sem substituir o protocolo de 13 etapas pelo da imagem |
| Tempo | Trabalho canônico do run atual, explicitamente rotulado, indisponível sem dado |
| Rodapé | Linha separadora e teclas `[Enter]`, `[a]`, `[c]`, `[f]`, `[q]`, demais atalhos existentes compactados conforme espaço |

Wireframe ASCII ilustrativo, não snapshot GitHub nem promessa de quantidade fixa de cartões visíveis. As letras da barra representam cores/segmentos, não caracteres finais:

```text
 >_ AI Engineering Workflow
    Milestone Monitor | OpenCode + my-ai-skills | somente leitura
 -----------------------------------------------------------------------------
 +----------------+ +----------------+ +----------------+ +----------------+
 | + 1 Concluida  | | > 2 Executando | | o 1 Pendente   | | ! 1 Bloqueada  |
 +----------------+ +----------------+ +----------------+ +----------------+
 1 milestone / 5 issues        Filtro: [todas] executando pendentes bloqueadas ...
 GitHub: recente | coleta ... UTC
 +---------------------------------------------------------------------------+
 | v #31 Configuracao inicial                  [VVAAAACCBB] 20% (1/5)         |
 |   owner/loja                                                              |
 |   + 1 concluida   > 2 executando   o 1 pendente   ! 1 bloqueada             |
 | Issue                  | Workflow               | Status | Tempo registrado|
 | ...                    | ... [+ Explorar] ...    | ...    | ...             |
 +---------------------------------------------------------------------------+
 -----------------------------------------------------------------------------
 [j/k] navegar [Enter] abrir [a/c] todos [f] filtrar [v] detalhes [q] sair
```

### D6 — Validação isolada e distribuição

Testes determinísticos de frame com três repositórios e 40 milestones artificiais, mais fixture de composição com quatro cartões de milestones e primeiro expandido, semelhante à referência mas explicitamente simulada. Incluir títulos Unicode, números largos, todos os estados, inventário parcial/vazio, todas as 13 etapas e tempos ausentes/zero/paralelos. Não usar cache real como fixture. Smoke tmux em servidor/sessão próprios; nunca enviar teclas, resize ou restart a `mobile:1.0`. Screen fake confirma atributos, cores estendidas/8 cores/sem cor e falhas de inicialização.

Além dos testes, salvar capturas ANSI/textuais do candidato exato em 238×54, 110×30, 80×24 e 40×12. Comparar visualmente com a imagem disponível na conversa e com a matriz D5: ordem das seções, quatro indicadores, contornos, barras, tabela, pílulas/badges, cores, respiros e rodapé. Registrar diferenças justificadas pelas células, 13 etapas e dados reais, sem declarar equivalência pixel a pixel. Se a imagem original não estiver acessível na futura sessão, pedir seu reenvio antes de afirmar validação visual contra ela.

Rodar suíte focada e completa, sincronizar plugin com `scripts/sync-plugin`, verificar idempotência e validar OpenSpec. Documentação operacional pt-BR/en descreve hierarquia sem alterar configuração/instalação. Na futura aplicação, cumprir reserva/worktree e validação da revisão exata conforme protocolo antes de editar produção.

### D7 — Resumos e barras derivados sem nova semântica

Indicadores globais somam os contadores exclusivos dos milestones do modelo completo, nunca as linhas filtradas/visíveis. Totais de milestones/issues usam o mesmo inventário e a mesma cobertura. Sem alvos manter orientação; vazio conhecido admite zero; inventário ausente exige aviso de cobertura parcial e não zero factual. Cache vencido conserva valores com aviso de frescor independente. Nenhuma nova consulta por frame.

Barra de largura fixa usa segmentos na ordem concluída/execução/pendência/bloqueio, cores dos indicadores e arredondamento por maiores restos para preencher exatamente as células disponíveis; valores numéricos são a fonte exata quando um segmento pequeno não ocupa célula. Percentual continua `done/total` da projeção, nunca soma verde+azul. Sem inventário/vazio mostrar `--%` com rótulos distintos e sem barra preenchida. Usar blocos sólidos suportados, sem gradientes simulados que alterem significado.

Tempo registrado resume `summary.recorded_work_seconds` do run atual, sem fallback para relógio, mtime, abertura de issue ou calendário. Formatar duração deterministicamente com segundos/minutos/horas, mantendo zero válido; ausente aparece como indisponível, inclusive abreviado com legenda em telas estreitas. Detalhes preservam segundos canônicos e calendário. Seleção de histórico muda somente detalhes. Rejeitada a cópia de `42min` ou conclusão total de etapas apenas porque a issue está fechada.

## Risks / Trade-offs

- [Mais espaço vertical por bloco] → modo compacto reduz respiros; contexto/divisores não podem expulsar seleção e régua da tela.
- [Cabeçalhos decorativos quebram offset] → separar linhas selecionáveis de linhas desenhadas, calcular viewport após contexto e testar primeira/última seleção, filtro e resize.
- [Mudança de representação de render] → adaptador textual e testes existentes preservados, uma única fonte de tokens para régua.
- [Tema do terminal reduz contraste] → fundo escuro da aplicação quando suportado, fallback de 8 cores e monocromático herdando fundo do terminal, sem redefinir sua paleta.
- [Imagem gráfica não cabe em células] → priorizar composição e papéis visuais; cores exatas e raios são aproximações, sem promessa de fidelidade percentual.
- [Cartões globais e contornos consomem altura] → resumo compacto automático e prioridade à seleção; não exigir quatro milestones simultâneos com qualquer dado real.
- [Coleta lenta mantém cache vencido] → manter aviso honesto; esta mudança não promete resolver desempenho.

## Migration Plan

Sem migração: preferências e cache mantêm o formato. Após futura implementação validada e integrada, o usuário fecha/reabre voluntariamente `aew dashboard` para carregar o novo código. Não alterar o launcher nem o processo já aberto nesta fase. Rollback de apresentação mantém dados/config intactos.

## Verification

### Polimento após captura operacional

O usuário autorizou corrigir seis pontos observados após uso real: cartões cortados, contexto duplicado, vãos externos excessivos, barras cinzas dominantes/0% verde, foco confundido com sanfona e contadores abreviados em tela ampla. Esta revisão mantém os contratos de dados e saúde. A navegação passa a considerar limites de cartão, não somente a linha do título; cartões grandes e rolagem explícita de detalhes continuam admitindo recorte contextual. O contexto deixa de consumir linha vazia quando desnecessário. A composição evita iniciar no rodapé um cartão recolhido que não cabe, sem ocultar o item selecionado. Substitui-se o respiro externo de uma linha entre cartões recolhidos pela composição mais compacta; margens internas e rótulos preservam hierarquia. Foco usa marca própria e contorno reforçado, sem inverter dados. Segmento pendente ganha papel de barra separado do rótulo; 0% fica neutro, sem alterar seu valor.

Verificação adicional: fixture sintética de 40 milestones predominantemente em 0%, nomes longos e contadores variados, com navegação de ida/volta e capturas em cores/ASCII. O aviso de cache da captura não é tratado como defeito visual nem removido; diagnóstico/coleta continuam fora desta revisão.

Regressões adicionais cobertas por `test_collapsed_navigation_frames_complete_cards_and_no_duplicate_context`, `test_context_only_after_both_card_headers_are_hidden` e `test_neutral_zero_pending_bar_and_focus_not_accordion`. O teste antigo de contexto foi adaptado para aceitar identidade no próprio cabeçalho visível, em vez de exigir contexto fixo redundante; a nova cobertura testa separadamente sua presença e ausência. O smoke ganhou cenário recolhido e espera limitada por frame efetivo, com sockets separados por cenário: uma primeira captura vazia mostrou que atraso fixo não era prova de inicialização. A repetição com o driver corrigido passou em todos os quatro cenários. A comparação visual usa as capturas dessa fixture, nunca o banco operacional.

Ambiente inspecionado na implementação: Python 3.14.8, tmux 3.7b, checkout principal autorizado explicitamente pelo usuário, sem outro escritor confirmado por ele. Reserva local `monitor-visual`. Fixtures e banco do smoke ficam em diretórios temporários isolados; nenhum acesso ao cache/config/pane operacional. Consumidores afetados: adaptador `render`, loop curses, testes TUI e distribuição gerada. Projeção/coleta/API e demo offline não foram alteradas. As políticas `protocol/WORKTREES.md` e `protocol/TEST_STRATEGY.md` foram relidas antes das alterações.

| Cenário / risco | Camada | Prova implementada |
| --- | --- | --- |
| Texto e estilos divergirem | Unidade | `test_frame_adapter_and_semantic_stage_tokens` |
| Bordas alterarem navegação, ordem ou contexto | Unidade | `test_cards_context_order_identity_and_no_decorative_navigation` e testes de sanfonas existentes |
| Filtro mudar totais ou falta de inventário parecer zero confirmado | Unidade | `test_global_totals_coverage_filters_and_expansion` |
| Barra aumentar conclusão ou perder células | Unidade | `test_distribution_exact_width_no_mutation_and_no_activity_completion` |
| Contadores largos deslocarem colunas | Unidade | `test_multidigit_counters_keep_semantic_column_positions` |
| Tabela esconder etapa atual ou fabricar sucesso | Unidade | `test_table_columns_stage_roles_and_protocol_not_implicit` e testes de régua existentes |
| Resumo de tempo inventar calendário/atividade | Unidade | `test_registered_time_zero_missing_history_and_parallel` |
| Detalhes perderem campos longos ou fontes | Unidade | `test_details_sections_full_data_and_wrapping` e testes de histórico existentes |
| Resize/Unicode/ASCII perder seleção ou exceder células | Unidade | `test_responsive_boundaries_scroll_unicode_ascii_and_model_preserved`, com 40 milestones/3 projetos |
| Cor/foco apagar estados ou falha de cores derrubar painel | Unidade | `test_colors_fallback_and_draw_per_span` |
| Curses real divergir do frame | Smoke isolado | `tests/milestone_monitor_visual_smoke.py`, colorido e monocromático/ASCII em 238×54, 110×30, 80×24 e 40×12; também navegação/detalhes/filtro/saída |
| Empacotamento divergir do código | Integração | `scripts/sync-plugin`, igualdade byte a byte da TUI e segunda sincronização idempotente |

Comparação visual realizada com a imagem da conversa e as capturas ANSI do smoke, usando dados explicitamente simulados. A prévia PNG é uma rasterização dessas capturas, não uma captura nativa da fonte do usuário. Elementos conferidos: ordem vertical, quatro indicadores, título/subtítulo, cartões, barras sólidas segmentadas, tabela, pílulas/badges coloridos, contornos e rodapé. Diferenças preservadas deliberadamente: 13 etapas pt-BR com janela explícita, tempos apenas registrados, ausência de selo DEMO/versão fictícia, fonte e raios determinados pelas células, espaço livre dependente dos dados. Terminais estreitos reduzem decoração para manter seleção/etapa. Não se afirma equivalência pixel a pixel.

Validação de publicação em SHA limpo, CI hospedada, revisão independente e archive permanecem fora da conclusão local: esta execução implementa no checkout autorizado sem commit/push, não publica nem integra automaticamente. Resultados e identificadores das execuções finais ficam no relatório ao usuário/registro local de evidências, fora do código testado.
