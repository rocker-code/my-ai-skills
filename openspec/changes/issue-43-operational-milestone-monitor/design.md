# Design

## Context

Motivação e limites em proposal.md. Auditoria em 2026-11-08, checkout/base `ee33197b8da684fff0a46df87935cd5b8b012f21`:

| Evidência inspecionada | Constatação e consequência |
|---|---|
| #43, corpo completo, comentários e timeline GitHub | Aberta, sem comentários/decisões anteriores; única referência de PR é #44. Lista de PRs abertas vazia. Não há implementação operacional a retomar. |
| #16 e PR #17 | Issue fechada; PR mergeada em 2026-10-18, commit `4d9d561242c4c6033729432764349ac7e2a5be23`, ancestral de main. Dependência satisfeita. |
| PR #44 | Merge em main em 2026-11-07, commit igual à base acima; entrega somente baseline, não fecha #43. |
| `examples/milestone-monitor/dashboard.py:11-55,95-108,110-122,170-196`; README da demo | Dados globais fictícios, quatro grupos, régua ilustrativa, anteriores implicitamente concluídas; vazio oculto por build_view e divisão por len. Não reutilizar essas inferências. |
| `scripts/workflow-event:20-31,127-150,235` | Comentário oculto v1 por issue/run; escritor coordenador, sem event_id obrigatório. Fontes e execuções tipadas já existem. |
| `scripts/workflow_metrics.py:44-54,61-93,95-175,240-307` | Parser e resumo canônicos, correlação por incarnação, estado/última confirmação/incompletude separados. Resumo mantém métricas legadas, não faz freshness TTL. |
| `scripts/workflow-report:30-54,57-84,86-101` | Pagina comentários, mas inventário por título tem limite 500 e qualidade tem limite 20 PRs; gera linhas somente para runs encontrados. Não serve sozinho como inventário operacional completo. |
| `openspec/specs/workflow-metrics/spec.md` e `workflow-execution-state/spec.md`, íntegros | Consumir sem alterar contrato. Runtime/relatório/referência de prova não significam veredito. |
| `tests/test_workflow_metrics.py`; `tests/test_workflow_execution_state.py:16-85,134-181` | Fixtures de runs e executável gh fake com TemporaryDirectory, sem serviços externos; reutilizar o padrão. |
| `scripts/sync-plugin:73-85`; README.md/en; `openspec/config.yaml` | Helpers são copiados por allowlist; pacote novo precisa ser distribuído explicitamente. Python stdlib/unittest e docs bilíngues são o padrão. |

Exploração oficial realizada pelo skill instalado `openspec-explore` (equivalente `/opsx-explore`) e novamente contra os achados antes da proposta. `issue-ready`: objetivo, comportamento, escopo, fontes, autorização, identidades/estados, compatibilidade, erros, localização, dependências e testes definidos nas seções abaixo; migração de dados existente N/A (cache novo); nenhuma decisão material do proprietário em aberto. READY FOR PROPOSAL é prontidão de conteúdo, não aprovação independente desta revisão.

### Contrato externo inspecionado — design review de contract-handoff

OpenCode instalado: `opencode v2.2.5`. Fontes oficiais lidas em 2026-11-08:
- https://opencode.ai/v2/docs/build/plugins e `/build/plugins/server`: `Plugin.define`, `ctx.event.subscribe`, `ctx.session.get`; contexto de plugin não identifica automaticamente a sessão recebida.
- https://opencode.ai/v2/docs/api e https://opencode.ai/v2/openapi.json. Documento OpenAPI 3.1, info `opencode HttpApi`/`0.0.1`, SHA-256 dos bytes `e125622e0c95f590bf902f0e2480e79148cf120ea0030ee871e3737ed189a1be` (880117 bytes). A versão info não identifica a versão do aplicativo.
- `opencode api --help`: operação por ID ou método/path; usa descoberta/autenticação oficial. Consulta real `opencode api session.active`: exit 0, envelope `data` objeto, valores `{type: running}`. Nenhum ID de sessão foi publicado.

| Cenário consumidor | Operação/campos entregues | Semântica/erro/validação |
|---|---|---|
| Sessão ainda ativa | GET `/api/session/active`, operationId `session.active`, `data[sessionID].type=running` | Apenas drains foreground do processo consultado; ausência significa inativa nesse processo, não sucesso da etapa. 400/401 categorizados. |
| Verificar vínculo de localização | GET `/api/session/{sessionID}`, `session.get`, envelope `data`: `id`, `projectID`, `location`, `subpath`; `outcome` opcional succeeded/failed/interrupted | Comparar localização/worktree explicitamente; 404 = sessão ausente, não conclusão. Não guardar tokens/cost/permissions/title/metadata retornados. |
| Evento de execução opcional | `session.execution.started/succeeded/failed/interrupted`: `id`, `created`, `durable.aggregateID/seq/version`, `data.sessionID` | Sem ID de etapa do workflow; não basta para concluir uma incarnação. |
| Reconectar após perda de eventos | GET `/api/event`, SSE, `event.subscribe` | Contrato diz volátil, perda em desconexão e overflow. Não existe promessa de replay nessa operação. Preferir consulta dirigida no MVP. |
| Sem autorização, contrato incompatível, fonte ausente | 401/404/JSON inválido/timeout | Fonte desconhecida, histórico preservado; sem fallback para banco interno ou prosa. |

CONTRACT DESIGN READY para o adaptador de leitura limitado acima: mecanismos já entregues e consulta ativa confirmada. Não declarar CONTRACT FROZEN do release remoto apenas por documentação mutável: fresh Apply deve verificar versão/contexto e o contrato do runtime alvo antes da implementação do adaptador; discrepância material retorna a planejamento. Não há pedido de mudança ao produtor nem capacidade de produtor ausente nesse desenho. O teste completo real de sessão/get por localização ainda não foi executado nesta sessão; será prova de integração, não fato presumido.

## Goals / Non-Goals

**Goals:** separar inventário, resumo canônico e overlay de runtime; reconstrução determinística; leitura offline responsiva; limite de confiança explícito para cada fonte.

**Non-Goals:** registrar eventos no lugar do coordenador, aprovar evidências, iniciar/interromper agentes, ler mensagens/logs privados, descobrir outros projetos, instalar plugin/configuração OpenCode automaticamente ou implementar notificações opcionais. Não alterar protocolos, seleção de testes ou CI por conveniência.

## Decisions

### D1 — Núcleo Python stdlib, adaptador externo oficial

Criar `scripts/aew` e pacote `scripts/milestone_monitor/` (cli, configuração, armazenamento, github, runtime, projeção e tui separados). Usar `curses`, `sqlite3`, `subprocess`, `json`, `datetime`, `threading`/fila e `unittest`. Reutilizar `workflow_metrics` via scripts resolvido pelo arquivo, nunca cwd. A arquitetura da issue é proposta sujeita à análise: plugin não é critério obrigatório; consultas oficiais satisfazem captura real sem adicionar dependência JS ou instalar código dentro do agente. Alternativas: plugin com eventos exigiria versão/pacote extra e replay; parsing de texto é expressamente proibido. O adaptador usa subprocess argv fixo, sem shell, e timeout; nunca executa conteúdo GitHub.

### D2 — Configuração/CLI, instalação e dados

Config JSON schema_version 1 em `$XDG_CONFIG_HOME/aew/config.json` (fallback `~/.config/aew/config.json`), alvo `{repository: owner/repo, milestones: [inteiros]}`. Sem alvos = tela vazia com instrução, não varredura implícita. Estado em `$XDG_STATE_HOME/aew/monitor.sqlite3` (fallback `~/.local/state/aew/monitor.sqlite3`), sobrescrevível por `--state-dir` para testes. Configuração explícita por `--config`. Nome de repo/números/URLs precisam de validação, deduplicação e host GitHub.com; Enterprise não é prometido.

Superfície a implementar: `aew dashboard [--config PATH] [--state-dir PATH] [--offline] [--no-color] [--ascii]`; `aew collect --once` com os mesmos caminhos, para diagnóstico/headless; `aew bind`/`aew unbind` para vínculo local explícito (issue URL, run-id, stage, worker-id, execution-kind/id, session-id, worktree, e branch opcional verificada por Git). Sintaxe final desses argumentos deve seguir esses nomes no help/teste. `bind` exige run/incarnação existente e aberta no cache, identidade igual ao GitHub e sessão/location compatível; falha não altera vínculo anterior. `unbind` remove somente vínculo exato e não apaga histórico. IDs seguem SAFE_ID existente; session-id começa com `ses`. Nunca copiar credenciais para config/estado.

Instalador `scripts/install-aew --bin-dir PATH` cria symlink para launcher resolvido por realpath (default `~/.local/bin`), recusa destino existente diferente, orienta PATH e informa dependência do clone retido. Não usar sudo, curl pipe, publicar pacote ou modificar shell rc. Desinstalação manual do symlink exato documentada; manter dados por padrão. Alternativa pip/npm não condiz com o repositório atual. Distribuir launcher/pacote/instalador pelo sync-plugin e testar o pacote copiado, sem editar gerados manualmente. Não apontar instalação durável a worktree efêmera sem avisar.

### D3 — Armazenamento atômico e modelo

SQLite local versionado (schema 1, transações, busy_timeout limitado), diretório 0700/arquivo 0600 ao criar, sem alterar permissões de dados preexistentes de terceiros. Tabelas lógicas: targets; milestones; issues; snapshots de runs por `(repo, issue, comment_id)` com run_id/hash; bindings por incarnação; observações runtime; saúde por fonte; estado visual. Preservar somente allowlist, não corpos arbitrários dos comentários. Validar estrutura antes de chamar parser/resumo; eventos conhecidos preservam ordem e campos necessários, desconhecidos não viram comandos/etapas concluídas.

Cada coleta publica transação apenas após todas as páginas do seu escopo serem válidas. Coleta de inventário repo, comentários por issue e runtime são fontes independentes; uma pode falhar sem invalidar as outras. Remover/mover issue da projeção só após inventário completo; manter histórico local. Guardar geração de início de coleta; resultado antigo que termina depois de uma coleta nova não sobrescreve a nova. SQLite serializa commit; não manter transação durante rede, não compartilhar conexão entre threads. Exceções/ENOSPC/corrupção: mensagem categorizada, não apagar/recriar banco automaticamente; modo leitura do último estado íntegro quando possível. Schema futuro desconhecido é erro seguro, nunca downgrade destrutivo.

Comentários são snapshots mutáveis, não append-only nem eventos com IDs universais. Upsert por comment_id + hash do conteúdo permitido; repetir snapshot não o concatena. Validar repo/issue/url internos contra item consultado. Snapshot diferente mesmo run em dois comentários = conflito de origem, não unir silenciosamente. Guardar histórico necessário do snapshot aceito; reprocessar em tempo efetivo estável usando canônico. Não ordenar por recorded_at nem deduplicar eventos distintos de mesmo timestamp. `last_seen_at` é atualização real, não ignorar hash por count igual. Não migrar/regravar registros v1 do GitHub.

### D4 — Coleta GitHub e seleção de PR

Reutilizar gh autenticado, somente GET/GraphQL de leitura: milestones por número e `/repos/{owner}/{repo}/issues?milestone=N&state=all&per_page=100`, todas as páginas; excluir objetos pull_request. Comentários via API paginada, parsing pelos marcadores canônicos. Não usar limite 500/título do workflow-report como inventário nem uma chamada de qualidade por frame. Repos/milestones explicitamente configurados, UTC com fuso nas coletas. 401/403/404/429, rate limit secundário, timeout e resposta malformada são categorias de falha distintas, sem stderr bruto em cache/tela. Respeitar Retry-After/reset quando presente; caso contrário backoff limitado exponencial.

PRs: consumir timeline/cross references paginadas como candidatos, verificar repo e referência de fechamento na PR antes de classificá-la como implementação; múltiplas candidatas ficam ambíguas. Guardar URL, estado, mergeCommit/mergedAt e head SHA somente quando retornados oficialmente. Menção #43 da baseline #44 não equivale a fechamento/entrega. Não calcular CI_GREEN de lista vazia nem aprovação por merge local. Ausência/erro de consulta de PR não apaga fatos anteriores; marcar frescor separadamente. Reabertura do GitHub invalida done mesmo que um run anterior tenha finished_at.

### D5 — Runs, workers, precedência e frescor

Run selecionado por maior created_at UTC válido; empate por run_id lexical e comment_id numérico, exibindo empate/conflito. Histórico selecionável nos detalhes (teclas `[`/`]`); default volta ao mais recente ao trocar de issue. Runs simultaneamente abertos ou duplicados conflitantes têm aviso. Aplicar `summarize_run(record, as_of=clock)` sem modificar resultado histórico; status visual é overlay separado. Para projeção por worker/incarnação, reutilizar a correlação canônica, extraindo uma API interna compartilhada somente se necessário e com regressão integral dos resumos. Não construir um segundo emparelhador simplificado.

Precedência por issue no run selecionado: (1) issue GitHub fechada -> grupo done, rótulo «fechada no GitHub», conflito se atividade aberta; (2) qualquer espera explícita aberta -> blocked (owner_input destacado como decisão; demais motivos nomeados); (3) falha/interrupção terminal relevante -> blocked, rótulos próprios; (4) pelo menos uma incarnação aberta com confirmação recente e sem terminal -> running; (5) restantes -> pending, distinguindo nunca iniciada, desconhecida, inativa e reconciliação. Uma espera de outro worker ganha o resumo conservador blocked, mas atividade paralela fica visível. Falha de incarnação anterior resolvida por nova abertura não bloqueia eternamente a nova. Conflito entre runs permanece aviso, não conta extra.

Freshness local: GitHub a cada 60s, runtime a cada 15s apenas para vínculos abertos, timeout por subprocess 10s; TTL GitHub 180s/runtime ou observação workflow 45s, configuráveis e validados positivos. São defaults operacionais de apresentação (não alteram significado de histórico nem medem desempenho). `r` solicita refresh com coalescência, sem furar rate limit. Na primeira abertura, antes de consulta válida, running histórico é desconhecido. Clock injetável e monotônico para agendamento, UTC para evidência; horário futuro inválido não confirma atividade. Cada fonte guarda attempted_at, fetched_at, observed_at, erro categorizado e retry_at. Nunca atualizar verified_at ao simplesmente abrir cache.

### D6 — Runtime é overlay, nunca prova de etapa

Executar `opencode api session.active` uma vez por ciclo, filtrar IDs vinculados; `opencode api get /api/session/{id}` somente nos vínculos novos, retomados ou que precisam revalidar localização. Não publicar IDs não vinculados, não guardar lista bruta. `session.active` é do processo consultado: config/runtime deve apontar ao mesmo contexto de descoberta usado no bind; se houver servidor explícito, usar `--server` com endereço sem credenciais e mesma autenticação oficial, não implementar auth paralela. Vínculos em servidor/contexto diferente não são comparáveis. Guardar identificador local não secreto desse contexto.

Comparar Session.Info.location/subpath com worktree canônico. Sessão que muda de localização invalida o vínculo. Sessão reutilizada requer novo bind para nova incarnação; runtime não sabe run/stage. Em conflito com terminal do workflow, terminal prevalece e atividade vira aviso «sessão ativa, execução encerrada». Consulta bem-sucedida ausente = sessão inativa, nunca sucesso/falha inferidos; 404 = ausente; erro de API = desconhecida. `outcome` de sessão é detalhe observado, não término automático da etapa. Para teste/job/CI a presença de sessão não confirma o processo filho: mostrar «agente ativo» nos detalhes, mas running da incarnação exige observação própria canônica; vínculo runtime confirma atividade somente para execução `worker` cujo executor declarado é aquela sessão. Sucesso de sessão não satisfaz tests/CI, nem encerra wait/reconciliation.

Sem stream/plugin no MVP: polling dirigido existe para impedir falso running e revalidar vínculos, não para inferir produtividade. O stream oficial perde eventos desconectado, então não pode sustentar sozinho reconstrução. `opencode api get /openapi.json` local nesta versão devolveu JSON truncado (~262144 caracteres); não assumir esse output como esquema íntegro. O JSON público completo foi inspecionado e hashado; Apply deve usar esquema íntegro do runtime ou fonte oficial do release para freeze e teste de localização. Não usar banco interno nem coletar mensagens como fallback.

### D7 — Régua e TUI

Etapas do protocolo em `skills/milestone-orchestrator/SKILL.md:136-139`: issue_audit, explore, resolve_questions, proposal, proposal_review, apply, tests, verify_archive, prepare_pr, pr_audit, ci, merge, kaizen. `verify_archive` ocorre ANTES de prepare_pr/merge, não Archive após Merge como na demo. Labels pt-BR mapeados, abreviados conforme largura; etapas opcionais não registradas são «sem registro», não sucesso presumido. Rework mantém histórico. Etapa desconhecida aparece como «outra: <id sanitizado>» em detalhes, não descartada.

Separar reducer de UI/renderização e chamadas de rede. Fundo coleta em fila limitada e publica modelo imutável; loop curses só renderiza e trata teclas, com shutdown cancelando somente tarefas do painel. Chaves de expansão/seleção por repo/milestone/issue, nunca índices; se item desaparecer selecionar vizinho válido deterministicamente. `v` compacto/detalhado, `r` refresh, `[`/`]` histórico de runs além das teclas da issue. Régua com viewport que inclui etapa selecionada mesmo em 40 colunas; detalhe oferece labels completos. Headers/título/status usam largura disponível sem sobreposição. Sanitizar controles e calcular largura de células Unicode; fallback ASCII explícito/automático em locale incompatível e cor opcional. Milestone vazio não some no filtro todas; filtro sem matches mostra mensagem sem quebrar seleção. Persistir preferências visuais por identidade, não tratar fechamento da TUI como término de agente.

## Risks / Trade-offs

- [Foreground não cobre jobs/background] -> explicitar «sessão/agente ativo» e desconhecido para trabalho filho sem evidência própria; não prometer telemetria que a API não oferece.
- [Consultas não observam toda transição entre amostras] -> snapshot observado, não inventar durações de runtime; métricas somente canônicas. Evitar plugin obrigatório para MVP.
- [Contrato experimental externo muda] -> versão/documento com hash, fixture e freeze antes de Apply do adaptador; incompatibilidade degrada a desconhecido e pode exigir replan.
- [Documento oficial vivo não prova release instalado] -> validar shape/location com release alvo e fonte íntegra antes de alegar integração real. Não declarar freeze antecipadamente.
- [Dados privados em respostas] -> allowlist antes de persistência e mensagens categorizadas; não capturar payloads nos logs/evidências, não imprimir stdout inteiro em erro.
- [Inventário grande/rate limits] -> paginação fora do loop de renderização, cache/refresh por fonte, coalescência/backoff; nada de uma consulta por frame.
- [Closed não equivale merged] -> percentual explicitamente de fechamento e entrega em campo separado, conforme fonte GitHub e protocolo.
- [Estado SQLite compartilhado] -> transação curta, geração anti-resposta atrasada, testes de dois escritores e falha parcial; sem daemon obrigatório ou recurso externo compartilhado.

## Migration Plan

Adicionar novos arquivos sem substituir a demo ou migrar comentários GitHub. Cache começa vazio; preencher somente por alvos configurados. Instalação é opt-in do launcher; gh/OpenCode ausentes não impedem leitura de cache/demo. Remoção do launcher reverte disponibilização; manter DB/config e exportar/copiar antes de qualquer intervenção manual. Não fazer downgrade destrutivo de schema. Regenerar distribuição apenas no Apply e inspecionar diff.

## Validation

### Matriz requisito / cenário / plano / prova

Todas as provas novas estão **planejadas, NÃO EXECUTADAS**. Arquivos `tests/test_milestone_monitor_*.py` abaixo são propostos, não já existentes. Reutilizar fixtures pequenas/TemporaryDirectory; relógio e subprocess fake determinísticos. Sem DB/porta/container compartilhados, sem credenciais necessárias na suíte.

| ID / aceite #43 | Cenário / risco concreto | Camada e implementação | Prova planejada ou existente |
|---|---|---|---|
| M1 / baseline independente | Demo da #44 continua simulada/stdlib | Preservação, sem integração no exemplo | PR #44 entregue; smoke de import/compile via py_compile com saída em temp, execução Ubuntu/tmux |
| M2 / múltiplos projetos, contadores | Mesmos números em 2 repos, páginas >500, PRs misturadas, zero issues, filtro não muda total | Integração github + projeção | Novo test_milestone_monitor_github.py: fake gh paginado completo; novo state.py: grupo exclusivo e 0/0 |
| M3 / sanfonas, filtros, régua | Abrir duas/recolher uma; seleção estável após mover issue; Apply não conclui Explore | Unidade UI/reducer + smoke curses | Novo test_milestone_monitor_tui.py; smoke PTY/tmux 110x30 e 40x12; teclas T1/T2/T3/T8 |
| M4 / estados distintos | owner_input vs falha vs testes/CI; worker ativo paralelo não duplica nem vence espera; futuro/TTL vencido | Unidade projeção com clock | Novo test_milestone_monitor_state.py, tabela D5; T4/T6; reaproveitar correlação de test_workflow_execution_state.py |
| M5 / v1, persistência, restart | Mesmo comentário repetido, last_seen atualizado, evento atrasado de A/B, legado, run empatado, fonte duplicada | Unidade canônica + integração SQLite | test_workflow_metrics.py/test_workflow_execution_state.py preservados + novos testes state/store; T5 |
| M6 / offline/ausência de fontes | Falha página 2, 401/429 com backoff, timeout, gh/OpenCode ausentes, sem alvos, schema futuro | Integração armazenamento/coleta | Novos github/store/runtime/cli: snapshot anterior intacto, erro categorizado, no tight loop; T7 |
| M7 / reconciliação GitHub | PR mergeada/issue aberta, fechada sem PR, reaberta/movida, PRs ambíguas | Integração fake gh + projeção | Novo github/state com timeline paginada e referências de fechamento; T9 |
| M8 / captura OpenCode não invasiva | bind válido/errado, location mudada, sessão ausente vs API falha, processo errado, worker terminal, sessão ativa não prova test_run | Integração fake opencode e smoke real consentido | Novo runtime/cli; fixture mínima do contrato oficial; leitura real de sessão de teste própria, sem mensagens; confirmar que q não interrompe agente |
| M9 / privacidade e concorrência | Título com ANSI, segredo em erro, prompt inesperado em payload, duas coletas fora de ordem, kill antes de commit, arquivo ocupado | Integração limites reais | Novo github/runtime/store; afirmar ausência de segredos em DB e saídas; dois subprocessos com state-dir descartável |
| M10 / instalação/docs | Instalação em bin temporário, execução de outro cwd, conflito de symlink, pacote distribuído, documentação bilíngue | Integração CLI/distribuição | Novo cli; `bash scripts/sync-plugin` no Apply, inspeção do diff e comandos do pacote; README pt-BR/en em paridade |
| M11 / prova e tempos | relatório present/evidence ref sem aprovação; stage-end sem observação; durações paralelas não viram calendário | Regressão canônica e apresentação | Testes existentes metrics/execution + unidade state/tui dos campos indisponíveis/fuso |

Pré-flight transversal: consumers reais são workflow-event/report/status, testes metrics/execution e distribuição sync-plugin. Fixtures legadas esperam schema_version 1 e os tempos atuais. Não mudar defaults compartilhados, CI ou descoberta. Se extrair API interna de correlação, executar primeiro metrics/execution e os novos state tests, depois suíte completa. Políticas lidas: protocol/AI_WORKFLOW.md, TEST_STRATEGY.md, WORKTREES.md, CI_PERFORMANCE.md e skills locais referenciadas, todas na base `ee33197`. Não é issue de performance: hooks de CI performance permanecem no handoff sem benchmark novo nem otimização lateral.

Comandos existentes para planejamento: `openspec validate issue-43-operational-milestone-monitor --strict --json --no-interactive`; `git diff --check`. OpenSpec instalado 1.16.1. Não há workflow `.github` no checkout/base; inventário GitHub `/contents/.github` respondeu 404. Fresh Apply/PR deve reavaliar checks/policy vigentes, não inferir que nenhum gate remoto é exigido.

Comandos após implementação: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_milestone_monitor_*.py'`; regressão `... -p 'test_workflow_*.py'`; suíte obrigatória `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`. Não confundir estes comandos planejados com testes novos executados. Para gate final: concluir archive/sync/commit, registrar e verificar suíte no HEAD limpo via workflow-evidence, mantendo ID fora do commit. Depois de qualquer commit, repetir o gate invalidado. Verificador automático de implementação só se suportado pelo OpenSpec instalado; senão matriz cenário→código→teste explícita. Archive oficial somente após implementação/testes/strict validate, na mesma branch.

## Review and Handoff

Este commit contém somente planejamento. Revisão inline: critérios #43 cobertos M1–M11, demo já entregue não duplicada; contratos existentes não alterados; etapas/estado sem inferências; riscos de identidade, frescor, concorrência, autorização e segredos com provas planejadas. Não há [QUESTION] de produto em aberto. Decisões D1–D7 são derivadas das fontes acima e escolhas técnicas reversíveis, não decisões novas atribuídas ao proprietário.

**Gate pendente:** revisão independente das novas fronteiras de estado/persistência/runtime pelo coordenador/reviewer, no SHA exato retornado. Não alegar PLAN_VALIDATED ou READY FOR APPLY antes desse parecer e do freeze técnico de versão/contrato externo. Esta sessão não dispõe de ferramenta de criação de child session exposta; revisão deve ocorrer em outra sessão real, não ser simulada pelo planejador.

Reviewer: ler issue/comentários atuais, proposta, ambas specs, D5/D6 e M1–M11 no SHA; conferir precedência, foreground vs filho, completude da paginação, ausência de aprovação implícita, limites de bind e cache. Rodar validação oficial exata e publicar parecer no SHA; achado material volta ao planejamento. Não editar produção.

Fresh Apply: somente após aprovação independente e contrato conferido, usar a MESMA branch/worktree, verificar SHA limpo e dependências ancestrais, comparar políticas atuais, transferir reserva após retorno do planejador, carregar apply-issue e skill oficial openspec-apply-change. Não fazer Apply no contexto de planejamento. Não iniciar segunda PR/worktree por fase. Coordenador é único escritor de workflow-event: ID local da reserva `issue-43-planning` não é run GitHub; este worker retorna observações, não cria run concorrente.
