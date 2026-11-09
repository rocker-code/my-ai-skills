# Milestone Monitor operacional

`aew dashboard`: TUI read-only Python 3/curses/SQLite (stdlib). A
[demo offline](../examples/milestone-monitor/) continua separada com **DADOS
SIMULADOS**. O painel operacional não inventa atividade, tempos ou aprovação.

## Instalar e configurar

Em um clone **retido**, não uma worktree a remover:

```sh
scripts/install-aew --bin-dir "$HOME/.local/bin"
aew --help
```

Inclua esse bin no PATH por sua configuração, se necessário. O instalador só cria
symlink, recusa destino diferente, não usa sudo nem altera shell rc. O launcher
resolve seu próprio caminho e funciona de qualquer diretório. Para desinstalar,
confira `readlink ~/.local/bin/aew` e remova **somente esse symlink**; mantenha
dados/config. Também distribuído via `scripts/sync-plugin` em
`plugins/my-ai-skills/scripts/`.

Crie `$XDG_CONFIG_HOME/aew/config.json` (fallback `~/.config/aew/config.json`):

```json
{
  "schema_version": 1,
  "targets": [{"repository": "owner/repo", "milestones": [1, 2]}],
  "runtime": {"enabled": false, "expected_version": "2.2.5"},
  "timing": {"github_interval": 60, "runtime_interval": 15,
             "github_ttl": 180, "activity_ttl": 45, "timeout": 10}
}
```

Substitua alvos por repositórios/números autorizados. Só GitHub.com, inteiros
positivos; duplicatas consolidadas. Sem alvos/config = vazio com orientação,
**não descoberta**. Tempos são segundos positivos até 86400, defaults acima.
Use `gh` já autenticado para atualizar GitHub; não coloque credenciais na config.

```sh
aew collect --once --config /caminho/config.json --state-dir /caminho/cache
aew dashboard --config /caminho/config.json --state-dir /caminho/cache
aew dashboard --offline --no-color --ascii
```

`collect --once` emite projeção JSON de metadados, saída não zero em falha de fonte.
`dashboard` exige TTY, inclusive tmux; não exige agente aberto. Config/caminhos
explícitos são opcionais. UI em pt-BR, nomes próprios/branches preservados.

## Arquitetura, estado e privacidade

GitHub paginado → snapshots SQLite → projeção/overlay OpenCode → reducer/curses.
Inventário por repo, comentários por issue e runtime são fontes independentes.
Coleta em thread, fila limitada, refresh coalescido e subprocessos com timeout;
sem requisição por frame, daemon ou plugin obrigatório. Sair fecha só o painel,
**nunca agentes, testes ou jobs**.

Cache schema 1 em `$XDG_STATE_HOME/aew/monitor.sqlite3` (fallback
`~/.local/state/aew/monitor.sqlite3`). Novos diretório/arquivo: 0700/0600; não muda
permissões existentes. SQLite serializa transações curtas com busy timeout; rede
fora de locks e geração contra resposta antiga. Falha de página/JSON/rede/escrita
mantém snapshot anterior. Banco futuro/corrompido é recusado, nunca apagado,
recriado ou rebaixado automaticamente. Preserve cópia e investigue espaço,
permissões/versão antes de intervenção. Sem migração de comentários GitHub.

- **GitHub:** identidade repo/número, milestone e fechamento. PRs são candidatas
  pela timeline, vinculadas somente após referência oficial de fechamento; múltiplas
  são ambíguas. Merge/head são fatos separados. PRs não entram no total de issues.
- **Workflow v1 (#16):** parser/resumo/correlação canônicos, sem logger paralelo.
  Upsert comment ID/hash inclui last_seen_at; eventos mantêm ordem efetiva estável.
  Run mais recente por criação UTC, desempate run ID/comment ID, conflitos visíveis;
  histórico selecionável. Worktree movida/reabertura não apaga histórico local.
- **OpenCode:** overlay de atividade foreground, não prova de processo filho,
  teste/CI, aprovação ou conclusão de etapa.

Percentual = **issues fechadas/total**, nunca estimativa de implementação. Vazio:
0/0 e percentual indisponível. Fechada não prova entrega mergeada/verificada;
PR mergeada com issue aberta não aumenta conclusão. Reabrir/mover aplica próximo
inventário completo. Contagem exclusiva: fechada → concluída; espera → bloqueada
(humano distinto); falha/interrupção relevante → bloqueada; aberta confirmada
recentemente → executando; demais → pendente/desconhecida/inativa/reconciliação.
Espera vence worker paralelo; terminal vence running posterior; detalhes preservam
execuções distintas. Rework não herda estado/aprovação de incarnação anterior.

Cache reaberto sozinho não confirma atividade. Amostra anterior à abertura só
confirma com observador vivo/saudável, epoch/contexto/revisão atuais e TTL válido;
reabrir a TUI não renova horário algum. Frescor por fonte, timestamps UTC, TTL
workflow/runtime 45s/GitHub 180s por padrão. Erro/cache não renova confirmação;
horário futuro não confirma. Tempos são canônicos registrados; trabalho paralelo
somado não é calendário. Relatório presente/evidence ref não implica aprovação.

Só allowlist de metadados; sem prompts/mensagens/tokens/logs/payloads arbitrários.
Títulos/controles ANSI sanitizados antes do cache/render. argv fixo sem shell;
conteúdo externo nunca vira instrução. Erros públicos categorizados (ausente,
não autorizado, negado, rate limit, timeout, resposta/contrato inválido,
armazenamento), nunca stderr bruto. Retry-After/reset quando fornecidos, senão
backoff exponencial limitado; `r` não fura backoff.

## Runtime opt-in e continuidade

Contrato **somente OpenCode 2.2.5**, CLI e servidor. Produtor oficial
`anomalyco/opencode@9bbb8ce18c80f099e0e448775f59d965ead40a21`, schema
`packages/protocol/openapi.json`, SHA-256
`92cc33ef9a107c8af6295e6fcbdf6d339d4374955910924456bd91a76844a5db`.
Outra versão exige nova conferência; sem fallback V1/prosa/banco interno.

Habilite `runtime.enabled: true`; `runtime.server` opcional HTTP(S) sem userinfo,
query ou fragment usa o mesmo contexto/auth oficial no bind/coleta. Omitido =
descoberta do serviço compartilhado pelo CLI; **nunca --standalone**.
IDs não vinculados são descartados. Após collect com run/incarnação aberta:

```sh
aew bind --issue https://github.com/owner/repo/issues/7 \
  --run-id wf-EXISTENTE --stage apply --worker-id worker-a \
  --execution-kind worker --execution-id EXECUCAO-EXISTENTE \
  --session-id ses_EXISTENTE --worktree /caminho/checkout --branch minha-branch
aew unbind --issue https://github.com/owner/repo/issues/7 \
  --run-id wf-EXISTENTE --stage apply --worker-id worker-a \
  --execution-kind worker --execution-id EXECUCAO-EXISTENTE
```

Substitua placeholders por IDs reais; ambos aceitam `--config`/`--state-dir`.
Branch opcional só é salva após verificar Git. Bind declara sessão executora
daquele worker. Teste/job/CI vinculado mostra agente ativo, mas só observação
própria canônica confirma o filho. Vínculo terminal/ambíguo, repo/checkout incorreto
ou sessão já vinculada a outra incarnação é recusado sem substituir anterior.
Unbind também remove vínculo terminal, preservando histórico.

Cada ciclo confirmatório revalida server.info, session.get, location.get explícito
e identidade Git. location.directory já é absoluto, não concatena subpath nem
aceita projectID/canonical compartilhado como prova de checkout. Mudar
localização/processo/contexto invalida vínculo até novo bind. 404 ausente,
inativa e falha de API são distintos. Amostras não são atômicas: movimento entre
consultas aparece na próxima. outcome da sessão não encerra workflow.

OpenCode/Codex continua pelas skills e workflow-event do coordenador, escritor
único. O painel não escreve eventos, aprova testes, controla agentes, fecha issues
ou faz merge. Codex produz v1, sem adaptador runtime nativo. Notificações/iPhone,
custos/tokens e web fora do MVP. Sem dependência Figma: curses, não redesign web.

## Ponte de eventos opcional

**Smoke real controlado: executado em 2026-11-09 na issue #440 com autorização explícita; não ativar em outros ambientes sem autorização.** A ponte usa a extensão pública `fetch`
do cliente oficial para enviar a allowlist de tipos na requisição HTTP, além
do filtro local e da sanitização do IPC. A assinatura recusa redirects. O pacote
instalado está testado com servidor simulado, não com sessão OpenCode real;
a validação integrada e o smoke real são gates distintos dos testes simulados. Evidências e limitações: `openspec/changes/integrate-opencode-workflow-instrumentation/verification.md`.

O pacote [`integrations/opencode-observer`](../integrations/opencode-observer/README.md)
fixa `@opencode/client@2.2.5` e sua árvore em lockfile. Sua instalação é voluntária:
execute `npm ci --ignore-scripts --no-audit --no-fund` nesse diretório, com Node >=22.
`npm test` verifica o cliente instalado contra transporte simulado, não OpenCode real.
Nada é instalado automaticamente pelo dashboard ou por `collect --once`.
Ambos mantêm o caminho Python stdlib sem Node/dependências da ponte.

A ponte recebe allowlist de vínculos/contexto pelo stdin e emite somente NDJSON
versionado de metadados, limitado a 16 KiB por envelope. O protocolo completo,
unidades de timestamps e exemplo sintético estão no README do pacote. Usa
`Service.discover` (não inicia serviço), autenticação oficial herdada do ambiente
e revalidação de `server.info`/sessão. Nunca passe credenciais em argv/config.
Interromper a ponte cancela somente sua assinatura; não para agentes.

Sem pacote/Node ou em falha, snapshots periódicos por CLI continuam disponíveis,
mas não equivalem a cobertura contínua. O fluxo oficial é live-only: perda,
reinício ou mudança de contexto exige reconciliação e não permite reconstruir
horários ausentes. Evento de sucesso de sessão não encerra etapa nem aprova teste.
Não habilite monitoramento real ou use uma sessão atual como smoke sem autorização.

## Observador foreground e posse da coleta

Com alvos explícitos e `runtime.enabled: true`, inicie voluntariamente:

```sh
aew observe --config /caminho/config.json --state-dir /caminho/cache
```

Não exige TTY/dashboard aberto e não instala serviço. `Ctrl+C`/`SIGTERM` encerra
somente observador e ponte criada por ele, nunca sessões OpenCode, testes ou jobs.
Sem Node/pacote/vínculos confirmados, permanece em modo degradado com snapshots
CLI periódicos. Falha/timeout de uma fonte não impede a coleta da outra.

Um lock de processo em `collector.lock` coordena a coleta no mesmo diretório de
estado. Há um único dono e UUID de epoch novo por posse; dois dashboards leem
os mesmos snapshots. `collect --once` com dono ativo lê o cache e solicita refresh,
sem criar outro coletor. `r` também sinaliza o dono; refresh é coalescido e não
ignora backoff. Um observador solicita passagem à TUI (prazo do timeout configurado);
ela cessa publicações e continua navegável como leitora. Respostas antigas não
publicam na nova posse. Segundo observador é recusado. Não remova o lock para
forçar coleta; crash libera o descritor automaticamente, sem apagar histórico.

Heartbeat a cada **5s**, saúde com validade de **15s**; nenhum heartbeat renova
horário de observação ou TTL de atividade. Cache SQLite continua schema 1, com
metadados locais versão 1 em `collector:*`, `observer:*` e `runtime-event:*`.
Fatos são novamente projetados por allowlist antes do cache, limitados a **1000**
por domínio; envelope NDJSON até **16 KiB**. Saturação/perda marca lacuna antes
de descartar fatos conhecidos. Dados de versão desconhecida e operações canônicas
pendentes nunca são apagados para liberar espaço. Fatos consumidos com mais de
**7 dias** são removidos durante novas inserções; não consumidos permanecem até
consumo ou perda explicitamente marcada. Backoff é limitado a **900s**.

stdout do observador não contém fluxo bruto; saúde, fatos e lacunas ficam no estado
local. Diagnósticos são categorizados; stderr bruto da ponte é descartado. Disco
cheio/falha de escrita não renova frescor e preserva o último estado íntegro.
Reinício, reconexão ou perda exige reconciliação oficial, não reconstrução de
horários ausentes. Para rollback, pare somente esse observador, preserve SQLite
e prefira leitura offline até reconciliar pendências. Não apague cache/config.
Não executar publicadores antigos/novos simultaneamente; a versão anterior pode
ignorar metadados novos, mas não deve disputar o comentário/outbox. Rollback não
desfaz etapas GitHub já publicadas nem remove uma operação aceita para liberar espaço.

## Transições estruturadas do coordenador

**Leitores GitHub:** `dashboard`, `collect --once`, `observe`; `bind`/`unbind` só
alteram vínculos locais. **Publicadores:** `workflow transition`, `workflow reconcile`
e `scripts/workflow-event`. Reconciliação não é uma consulta read-only: pode retomar
outbox e publicar esperas comprovadas. Só o coordenador de workflow previamente
autorizado pode chamá-la. `coordinator: true`/`--coordinator` declara esse contexto,
não substitui autorização humana nem permissões `gh`; a config do monitor não
autoriza escrita por si só. Invocar uma skill isoladamente não cria esse contexto.

Exemplos **sintéticos**, somente em ambiente de teste autorizado. Salve `run.json`:

```json
{"version":1,"coordinator":true,"operation_id":"op-run","event":"run-start","issue":"https://github.com/owner/repo/issues/7","run_id":"wf-exemplo","worker_id":"orchestrator","at":"2026-11-08T00:00:00Z"}
```

E `apply.json` (a sessão executora ainda não foi disponibilizada):

```json
{"version":1,"coordinator":true,"operation_id":"op-apply-a","event":"dispatch","issue":"https://github.com/owner/repo/issues/7","run_id":"wf-exemplo","worker_id":"worker-a","stage":"apply","execution":{"kind":"worker","id":"exec-apply-a"},"at":"2026-11-08T00:00:01Z","depends_on":["op-run"],"binding":{"worktree":"/fixture/worktree","branch":"fixture"}}
```

```sh
aew workflow transition --input run.json --config /caminho/config.json --state-dir /caminho/cache
aew workflow transition --input apply.json --config /caminho/config.json --state-dir /caminho/cache
# Retry usa EXATAMENTE o mesmo arquivo/operation_id/horário; também aceita --input -.
aew workflow transition --input apply.json --config /caminho/config.json --state-dir /caminho/cache
```

Quando chegar o ID **real** do worker, salve `session.json`:

```json
{"version":1,"operation_id":"op-apply-a","session_id":"ses_EXECUTORA_REAL"}
```

```sh
aew workflow reconcile --issue https://github.com/owner/repo/issues/7 --run-id wf-exemplo \
  --coordinator --binding-input session.json --config /caminho/config.json --state-dir /caminho/cache
```

A intenção tardia é separada: não acrescente sessão ao payload original, pois
outro hash para o mesmo `operation_id` é recusado. Outra sessão para a intenção
já aceita também é recusada. Sem ID real, vínculo fica pendente; não usar sessão
coordenadora como fallback. Publicação e bind não são transação distribuída: abrir
no GitHub pode funcionar e bind falhar. Retry revalida/repara o vínculo sem abrir
outra etapa. Com coletor ativo, solicita refresh e usa apenas snapshot disponível;
sem dono, coleta pontual respeita os alvos/backoff. Contexto/PID ou execução trocada
exige reconciliar e remover exatamente o vínculo anterior com `aew unbind` antes
de novo bind; não substituir silenciosamente.

Entrada JSON até **16 KiB**, sem chaves duplicadas. Identidades seguras e execução
tipada são obrigatórias quando aplicáveis; horário efetivo UTC é preservado.
Retorno separa `accepted`, `publication` (`pending`/`published`/`conflict`), `binding`
(`not_requested`/`pending`/`bound`/`failed`) e `binding_reason`. Código 1 sinaliza
falha/pendência de instrumentação, não proibição de continuar desenvolvimento
autorizado. Antes da aceitação durável: `accepted:false`; depois dela, falha remota
mantém operação pendente e não perde o horário original. Não gere novo ID para retry.

Reconciliação fica restrita à issue/run informados; retorna até **20** operações,
`total`/`truncated` e contadores `runtime`. Esperas sobrepostas são unidas e descontam
cobertura canônica existente. `wait-intervals` publica até **32** intervalos em uma
única edição, só com pares completos, identidade inequívoca e cobertura contínua.
Não fecha espera explícita aberta; adia quando ela ou outro pedido pendente impede
pareamento seguro. Consulta sem horário da resposta mantém `unmeasured`; não repetir
em loop para inventar duração. `remaining` também inclui gates/medições não verificados.

Sucesso de turno nunca produz automaticamente `observe completed`/`stage-end`.
Observação terminal estruturada exige evidência própria; worker com fonte runtime
exige `log_ref: worker-result:<execution-id>`. `test_run` exige `report: present`,
fonte `test_report`/`process_exit` e `evidence:<execution-id>` do teste. Referência
não implica aprovação: o coordenador ainda verifica os gates e registra o término
semântico separadamente. CLI manual e métricas v1 continuam compatíveis.

### Publicação cooperativa e limites de concorrência

O coordenador estruturado e `scripts/workflow-event` compartilham lock por
diretório de estado/repo/issue/run. A CLI manual aceita `--state-dir`; use o mesmo
domínio de `aew` (default `$XDG_STATE_HOME/aew`). Nenhum campo novo é obrigatório
para registrar manualmente eventos v1. Eventos estruturados recebem metadado
opcional `operation` com identidade/hash; leitores e métricas v1 permanecem válidos.

A outbox aceita a operação antes da rede, preserva dependências e separa publicação
de vínculo. Retry relê o comentário e reconhece a operação já salva; resposta
perdida não duplica evento/evidência/duração. Comentário duplicado, payload alterado
ou deriva da base conhecida causam conflito, não overwrite deliberado. Não apagar
journal para contornar conflito. A publicação exige coordenador único autorizado;
observador, dashboard e workers não publicam.

Isso **não é CAS distribuído nem exactly-once entre máquinas**. Um escritor externo
não cooperativo pode editar entre a última leitura e a gravação GitHub, janela em
que a API de comentários não fornece exclusão atômica. Use um coordenador único
por issue/run e estado compartilhado para escritores cooperativos; concorrência
externa exige pausa/reconciliação manual. O teste fake dessa janela documenta uma
limitação, não uma garantia de proteção. Rede nunca ocorre em transação SQLite.

### Ler sinais sem confundir com registro

- **executando confirmado:** atividade recente da execução; com vínculo worker,
  exige consulta runtime válida. Não prova teste/CI nem conclusão de etapa.
- **aguardando autorização (observada):** permissão pendente na sessão vinculada;
  **aguardando resposta (observada):** formulário pendente. Apenas IDs/classificação
  são apresentados, nunca textos ou respostas. A issue aberta fica bloqueada uma
  única vez enquanto o sinal for válido. Inatividade sozinha não cria espera.
- **aguardando decisão:** espera canônica `owner_input`, declarada no workflow.
  Tem precedência sobre atividade paralela e permanece distinta do pedido runtime.
- **último sinal local:** execução de sessão iniciada/bem-sucedida/falha/interrompida,
  sem promover término de turno a resultado semântico da etapa.
- **Publicação/vínculo pendente:** intenção local ainda não publicada ou vínculo
  incompleto. Os detalhes não a apresentam como etapa já registrada no GitHub.
- **cobertura incompleta / última lacuna:** perda/reinício/reconexão preservados;
  consulta recupera o estado atual, nunca o horário de uma resposta perdida.

Exemplo sintético: `per_fixture` e `frm_fixture` pendentes no mesmo worker.
Responder a `frm_fixture` resolve somente esse ID; `per_fixture` continua pendente.
Se a permissão desaparecer em consulta após desconexão, o horário da resolução
fica desconhecido. Os tempos canônicos exibidos não recebem duração inferida.
Intervalos runtime só poderão ser publicados pelo coordenador com fronteiras
nativas confiáveis e cobertura contínua, sem sobrepor espera canônica existente.
Erro de fonte, epoch anterior ou TTL vencido remove confirmação, mesmo com
heartbeat recente. Fechamento GitHub ainda vence os sinais locais nos totais.

## Apresentação visual e layouts

O painel usa composição escura com marca `>_`, quatro indicadores contornados
(concluídas, executando, pendentes e bloqueadas), totais/filtro, cartões de
milestones e rodapé com teclas destacadas. Cada cartão mostra título, repositório
em sublinha, contadores e distribuição dos estados. A ordem recebida é preservada,
inclusive entre projetos intercalados; ao rolar dentro de um cartão, o topo mantém
contexto de repositório/milestone somente se título e repositório estiverem fora
da área visível. Na navegação normal, cartões recolhidos que cabem na área útil
são enquadrados inteiros, sem início solto de cartão no rodapé. Cartões expandidos
maiores e rolagem explícita de detalhes continuam admitindo recorte contextual.
Bordas e separadores não são itens navegáveis. Cartões recolhidos usam menos
espaço externo; contadores por extenso substituem C/E/P/B em largura ampla.

Indicadores globais e contadores usam o inventário completo, não apenas issues
visíveis: filtrar ou recolher não muda os totais. Cobertura parcial e cache vencido
continuam explícitos. Sem inventário não equivale a vazio conhecido: ambos têm
percentual indisponível, mas somente o vazio conhecido representa 0/0 confirmado.

A barra é **distribuição de estados**, não estimativa de implementação: verde
concluída, azul/ciano execução confirmada, cinza pendência e âmbar bloqueio/espera.
Exemplo **ilustrativo**: uma fechada, duas executando, uma pendente e uma bloqueada
resultam em **20% (1/5)**, não 60%. Segmentos pequenos podem não ocupar célula;
os contadores continuam sendo os valores exatos. ASCII usa segmentos D/E/R/B
(concluída/executando/restante/bloqueada), com legenda factual pelos contadores.

- **≥180 colunas:** tabela Issue / Workflow / Status / Tempo registrado, etapas
  em pílulas e status em badges textuais. As 13 etapas reais não são reduzidas
  às oito de uma imagem de referência; `...` indica etapas fora da janela,
  mantendo a etapa atual visível e os nomes completos consultáveis nos detalhes.
- **120–179:** issue/status/tempo na primeira linha, régua na seguinte.
- **80–119:** campos compactos, indicadores em 2×2 se houver altura.
- **<80 ou pouca altura:** resumo de indicadores, campos empilhados e C/E/P/B;
  decoração cede espaço à seleção e à etapa atual. 8×3 e 1×1 degradam sem erro,
  mas não comportam todas as informações. Títulos truncados usam `…` ou `...`.

Tempo registrado é o trabalho canônico do run atual, não calendário nem cronômetro
de atividade. Zero registrado aparece como 0s; ausência como indisponível.
Exemplo **ilustrativo**: 120s de trabalho e 600s de calendário mostram 2min na
tabela; os detalhes preservam ambos em segundos. Histórico altera só detalhes,
organizados em Execução / Entrega / Fontes; textos longos quebram em linhas para
consulta por rolagem. Etapa atual registrada não prova execução confirmada, e
issue fechada não faz todas as etapas receberem conclusão ou aprovação.

Tema local à aplicação: texto claro, bordas ciano, títulos em negrito e foco
restrito ao item principal, sem inverter todo o cartão. A marca de foco `●`
(`*` em ASCII) é distinta do triângulo de sanfona, com contorno reforçado no
cartão selecionado e bordas secundárias suaves. Barras pendentes são mais escuras
que seus rótulos e 0% aparece neutro, não verde. Cores estendidas são
opcionais, com fallback de 8 cores e monocromático; `--no-color` herda o fundo do
terminal e `--ascii` troca os glifos. Sem fontes especiais, redefinição de paleta,
configuração de tmux ou dependências novas. Células não reproduzem fontes,
gradientes e raios de uma interface gráfica; fidelidade é de composição e papéis
visuais, não pixel a pixel. O painel operacional não copia selo DEMO, versão ou
valores simulados da referência.

## Teclas e régua

↑/↓ ou j/k navegar; Enter/Espaço sanfona/detalhes; a/c expandir/recolher todos;
f todas/executando/pendentes/bloqueadas/concluídas; v compacto/detalhado; r refresh;
[/] histórico de runs; PgUp/PgDn rolar detalhes; q/Esc sair. Preferências por
identidade persistem; histórico muda só detalhes, nunca totais do run mais recente.

Auditoria → Explorar → Decisões → Proposta → Revisar proposta → Aplicar → Testes →
**Verificar/arquivar** → Preparar PR → Auditar PR → CI → Merge → Kaizen.
`+` encerrada/concluída registrada; `>` atual registrada (não prova running);
`.` sem registro; `!` falha/interrupção; `?` reconciliação; `B` bloqueio; `H` humano.
Anteriores não viram sucesso por posição. Etapa desconhecida fica «outra».
Viewport inclui etapa atual; largura Unicode, fallback ASCII/sem cor, contadores
estreitos C/E/P/B. Testes stdlib: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
discover -s tests`. Fixtures artificiais não são smoke de integração real.
