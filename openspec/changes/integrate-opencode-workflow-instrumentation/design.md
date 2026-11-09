# Design

## Context

Ver motivação em `proposal.md`. A exploração verificou:

- `runtime.py` já valida CLI/servidor 2.2.5, `session.get`, `location.get`, identidade Git e revisão do vínculo; `session.active` só informa sessões `running`.
- `collector.py` executa coleta independente por fonte, mas seus workers pertencem ao processo da TUI; a CLI só oferece `collect --once` para uso headless.
- `projection.py` exige amostra posterior à abertura da TUI, o que impede aproveitar observador anterior mesmo quando vivo. `store.py` já possui snapshots geracionais e chaves locais SQLite, além de proteção contra ABA de vínculo.
- `workflow-event` implementa comandos de etapa/espera/observação e grava um comentário v1 por issue/run. Não há outbox nem idempotência geral de transições; a deduplicação atual cobre somente certas observações.
- A skill `milestone-orchestrator` define o coordenador como escritor único e já exige instrumentar fronteiras e reconciliar resultados. Essas são instruções executadas pelo agente, não um scheduler programático que detecte qualquer mudança de etapa.
- A outra mudança ativa altera apresentação e documentação do monitor. Este plano não depende do seu arquivamento nem autoriza modificar seus arquivos nesta fase; Apply deverá integrar mudanças sobre a revisão então existente, preservando o acabamento visual.

Evidência externa do contrato: `anomalyco/opencode@9bbb8ce18c80f099e0e448775f59d965ead40a21`, `packages/protocol/openapi.json`, SHA-256 `92cc33ef9a107c8af6295e6fcbdf6d339d4374955910924456bd91a76844a5db` (igual à fixture local). O endpoint `event.subscribe` oferece tipos filtrados, mas seu fluxo é volátil, sem replay; desconexão perde eventos. `session.permission.list` e `session.form.list` permitem reconciliar pendências atuais. Eventos `session.execution.*` existem, mas não possuem a identidade semântica de nossa etapa/worker.

Detalhe decisivo: `packages/cli/src/commands/handlers/api.ts` desse commit usa `response.text()` antes de escrever stdout. Portanto `opencode api event.subscribe` não é transporte incremental utilizável. O pacote `@opencode/client` do mesmo release tem versão 2.2.5 e APIs oficiais `Service.discover`, `Service.headers` e assinatura assíncrona de eventos. Isso foi conferido no código, não validado em integração real nesta fase.

## Goals / Non-Goals

**Goals:**
- Duas saídas consistentes: estado runtime recente para o painel e transições canônicas publicadas pelo coordenador.
- Fronteiras explícitas e repetíveis, sem o usuário precisar emitir comandos por etapa.
- Continuar observando sem TUI e continuar o desenvolvimento mesmo quando a instrumentação falhar.
- Testar causalidade, crash/retry, privacidade e concorrência antes de habilitação real.

**Non-Goals:**
- Detector universal de etapas, scheduler autônomo novo ou garantia de que um agente sempre cumprirá instruções.
- Término de turno como término de etapa, ou atividade do agente como prova de execução de filho/teste.
- Replay de transcript/log de sessão, captura de conteúdo ou descoberta de todas as sessões do usuário.
- Instalação automática de serviço, plugin obrigatório, atualização de OpenCode ou ativação automática na máquina do usuário.

## Decisions

### D1. Separar observação, transição e publicação

```text
OpenCode -- cliente oficial --> observador -- metadados --> SQLite
                                                            |
                                   +------------------------+
                                   v                        v
                               dashboard                coordenador
                                                            |
                                                  transicao estruturada
                                                            |
                                                     outbox local
                                                            |
                                                workflow-event / GitHub
```

O observador só lê APIs e escreve estado local. A TUI só lê fontes e mantém preferências/cache, nunca publica workflow. Apenas o coordenador autorizado consome fatos e chama a operação de transição/publicação. Os workers devolvem identidades, resultados e timestamps; não compartilham o escritor do comentário.

Alternativas: permitir que um plugin publique comentários eliminaria a dependência do coordenador para escrita, mas criaria um segundo orquestrador, conflitos de comentário e encerramentos sem gates. Deduzir etapas a partir de skills/ferramentas também foi rejeitado.

### D2. Contratos de CLI propostos e ativação

- `aew observe --config ... --state-dir ...`: comando foreground contínuo, sem TTY. Pode ser mantido por tmux/supervisor escolhido pelo usuário, mas o instalador não registra serviço. É a única nova operação contínua.
- `aew workflow transition --input <arquivo-ou-> --config ... --state-dir ...`: recebe JSON limitado contendo `operation_id`, evento canônico, issue, run, etapa/worker/execução quando aplicáveis, horário efetivo e os campos permitidos do evento. Para abertura executora, aceita ID de sessão, worktree e branch. Faz validação, journal local, publicação e tentativa de bind; retorna estados separados para publicação e vínculo.
- `aew workflow reconcile --issue ... --run-id ...`: ação do coordenador que revalida fatos e retoma pendências daquele escopo. Não expande alvos nem decide etapas pela última atividade.
- Manter `dashboard`, `collect --once`, `bind`, `unbind` e comandos manuais de `workflow-event`. Esses comandos também respeitarão posse de coleta/publicação quando escreverem nos mesmos recursos.

Não é necessária nova flag persistente para a primeira versão: `runtime.enabled` e alvos autorizam observação; iniciar `observe` é explícito. Publicação é ação separada de workflow já autorizado e depende de acesso `gh`; configuração read-only nunca a autoriza por si só. `aew --help` e documentação distinguem claramente as operações leitoras e publicadoras.

### D3. Ponte de eventos opcional, pequena e sem credenciais exportadas

Adicionar pacote auxiliar em `integrations/opencode-observer/`, com JavaScript para Node e dependência exata `@opencode/client@2.2.5`, lockfile e testes próprios. A integração opcional não adiciona dependências Python nem é instalada ao executar o dashboard. A distribuição inclui os arquivos necessários e instruções de instalação explícita, nunca `node_modules`.

A ponte usa apenas o cliente oficial para conexão e autenticação. Para serviço compartilhado, usar `Service.discover`, nunca `ensure`/`stop`, para não criar, substituir ou interromper o servidor. Para servidor explícito, seguir o comportamento conferido em `packages/cli/src/services/server-connection.ts` e `packages/cli/src/env.ts`: URL configurada e credencial já herdada no ambiente (`OPENCODE_PASSWORD`, com a compatibilidade legada do release), usuário `opencode` e `Service.headers(endpoint)`. Construir o cliente com esses headers e revalidar `server.info`; não exportar credenciais ao Python, passá-las em argv/config ou ler arquivos privados. Credencial ausente/negada é falha categorizada; não trocar de servidor para contorná-la.

A ponte emite NDJSON versionado já sanitizado para o observador Python. Tipos permitidos: `server.connected`, mudanças de contexto relevantes, `session.execution.started/succeeded/failed/interrupted`, `permission.asked/replied`, `form.created/replied/cancelled`. Não assinar texto, raciocínio, conteúdo de skill ou ferramentas. Confirmar semântica de timestamps/IDs pelas definições do produtor e testar o pacote instalado, não apenas fixtures.

Conferência durante Apply: o cliente de alto nível 2.2.5 aplica `types` somente após receber o fluxo. Conforme escolha explícita do usuário, usar a extensão pública `fetch` de `OpenCode.make` para acrescentar a allowlist fixa como query `types` repetida no endpoint oficial `/api/event` (incluindo eventual prefixo da URL). Manter parser SSE, autenticação e cancelamento do cliente oficial, sem imports privados nem atualização do pacote. A requisição da assinatura recusa redirects; o filtro local continua como defesa adicional. Testar a query recebida pelo servidor simulado com o pacote instalado. Isso não acrescenta filtro servidor por sessão nem permite assinar conteúdo.

O observador envia à ponte apenas a allowlist de sessões/contexto atualmente vinculados. O filtro por tipo não implica filtro servidor por sessão: filtrar identidades antes de projetar dados, sem consultar conteúdo de sessões alheias. Como o cliente pode compartilhar eventos de várias localizações, a localização do plugin/servidor nunca vale como localização da sessão.

Sem Node/ponte/pacote compatível: reportar modo degradado e continuar snapshots periódicos por CLI; não afirmar cobertura contínua ou horários exatos de transições. Essa degradação não atende sozinha à validação final do caminho completo de eventos.

Alternativas rejeitadas: SSE via CLI acumulador; acesso a banco/registro privado de credenciais; tornar TypeScript obrigatório para a TUI; plugin carregado em todas as sessões apenas para monitoramento.

### D4. Posse de coleta, estado local e frescor

Usar lock exclusivo de processo no diretório de estado para posse da coleta; liberar por fechamento do descritor ao terminar. Cada posse recebe UUID novo (`collector_epoch`), identidade do processo/host e horário de início. Heartbeat indica saúde do coletor, não atividade do runtime. Expiração temporal sozinha não autoriza roubar lock.

`observe` mantém workers GitHub/runtime existentes e a ponte. Dashboards e `collect --once` tentam assumir coleta somente sem outro dono; quando há observador, leem os snapshots compartilhados e não criam coletores concorrentes. Refresh solicita atualização ao dono com sinal local coalescido; não ignora backoff. Na troca de dono, invalidar respostas de gerações/epochs anteriores. Um observador substitui posse do coletor da TUI somente após cessarem suas publicações; não executar dois escritores simultâneos.

Persistir metadados versionados em chaves próprias de `local`, aproveitando transações SQLite existentes, sem alterar `user_version=1` nem reinterpretar snapshots antigos. Separar `observer:*`, `runtime-event:*`, `workflow-operation:*`, `workflow-pending:*` e `collector:*`; validar versões dos payloads. Guardar fila limitada de fatos normalizados para retomada do coordenador, não eventos brutos. Esgotamento descarta cobertura de observação com marcador de lacuna; operações canônicas aceitas e não confirmadas nunca são descartadas para liberar espaço.

Na projeção, uma amostra anterior à abertura da TUI pode confirmar atividade somente com TTL válido, epoch atual cuja posse esteja verificavelmente viva, fonte saudável, contexto e `binding_revision` atuais. Depois de reiniciar o observador, requerer reconciliação nova: cache/heartbeat antigos não bastam. Sem observador, manter o comportamento conservador de coleta da TUI.

### D5. Associação automática não é associação inferida

Reutilizar `find_incarnation`, `bind`, validações Git/localização, guardas geracionais e revisão única existentes. Sequência: aceitar transição com ID estável, publicar abertura canônica, atualizar snapshot correspondente e só então bind validado. Se publicação falhar, a intenção fica pendente e não é apresentada como etapa GitHub; se bind falhar, a abertura publicada permanece, mas atividade fica desconhecida com erro de vínculo visível. Não prometer atomicidade entre SQLite, API OpenCode e GitHub.

No despacho assíncrono, abrir no instante do despacho e completar o bind quando o runtime fornecer ID real de sessão. A ausência desse ID é capacidade indisponível, não motivo para usar o ID do coordenador ou extrair identidade de prosa. Na troca de etapa/execução, remover exatamente o vínculo anterior após reconciliá-lo; nunca substituir silenciosamente. Contexto/PID alterado exige novo bind explícito do coordenador.

Para o ID tardio, `workflow reconcile --binding-input` recebe uma intenção local separada `{version, operation_id, session_id}`, limitada e idempotente, ligada ao hash da abertura. A worktree/branch continuam sendo as declaradas no payload imutável da abertura; outra sessão para a mesma intenção é recusada. Isso não cria evento canônico nem altera o hash original. Com coletor ativo, o coordenador solicita refresh e tenta o bind somente contra snapshot já disponível; sem dono, assume coleta pontual respeitando backoff. Falha parcial permanece pendente/visível, sem disputar snapshots do observador. Troca de execução exige reconciliação e `aew unbind` exato antes do novo bind automático.

Cada fato inclui contexto, epoch, revisão, ID/timestamp nativo quando disponível, recebimento UTC e identidade do pedido/execução de sessão quando houver. Rejeitar confirmação anterior a `bound_at`. Eventos de sessão que não permitam associar uma execução de etapa de forma inequívoca servem para reconciliar snapshot atual, não para publicar término. `session.execution.succeeded` não vira `observe completed` da etapa; isso cortaria indevidamente o tempo canônico e impediria retomada na mesma incarnação.

### D6. Operações canônicas idempotentes, não transação distribuída

Extrair validação e construção de eventos de `workflow-event` para API reutilizável, mantendo a CLI manual. O adaptador estruturado registra operação em SQLite antes da chamada remota. Envelope mínimo: versão local, ID seguro, payload normalizado/hash, identidade issue/run, dependências causais, horário efetivo, estado (`pending`, `published`, `conflict`) e resultado de vínculo separado. A mesma identidade com outro hash falha.

Adicionar metadado opcional de identidade de operação a eventos v1. Uma operação que produz mais de um evento usa IDs derivados estáveis por evento. Retry relê comentário, procura IDs já gravados e valida payload antes de reenviar; confirmação perdida após sucesso não duplica eventos nem evidências. `run-start` ganha o mesmo caminho idempotente e horário efetivo validado; a CLI legada mantém defaults atuais. Publicar eventos em ordem de dependência, sem passar término antes da abertura.

Um lock de publicação por domínio de estado/issue/run serializa os coordenadores cooperativos e o registrador manual que usa o mesmo domínio. Antes de cada atualização, reler e comparar base/identidades; duplicatas de comentário ou deriva inesperada geram conflito. A API de edição de comentários não fornece aqui uma transação distribuída: não prometer exactly-once nem exclusão de escritores em outra máquina/estado não compartilhado. Documentar coordenador único por issue/run; concorrência externa não cooperativa exige pausa e reconciliação manual, não overwrite deliberado. Testar a janela conhecida e explicitar sua limitação.

Não manter rede sob transação SQLite. Timeout/backoff e filas são limitados; retorno estruturado indica aceita localmente/publicada/vinculada ou falha. Falha antes da persistência significa instrumentação indisponível, não aceitação durável. Após crash, o próximo coordenador retoma pendências; o observador não despacha publicação.

### D7. Esperas: sinal imediato local, duração canônica só com cobertura

Permissões e formulários têm IDs e estados próprios. Mostrar imediatamente pendência observada nos detalhes e contar issue aberta como bloqueada enquanto o sinal for recente; não mostrar o texto do pedido/resposta. Rejeição/cancelamento encerra somente aquele pedido; o efeito sobre sucesso/falha da etapa depende do coordenador.

Esperas explícitas do coordenador continuam `wait-start/end` em tempo real. Para espera originada no runtime, o coordenador só publica intervalo canônico quando início e resolução têm identidade/horários confiáveis e continuidade de coleta. Enquanto aberta, permanece sinal local. Ao resolver, publica o par com horários efetivos originais, unindo pedidos sobrepostos e subtraindo intervalos já cobertos por esperas canônicas do mesmo worker/etapa/motivo; não abrir pares duplicados ou fechar espera explícita. Se outra espera aberta impedir calcular a cobertura, adiar a publicação desse intervalo.

Depois de desconexão, a consulta atual resolve o estado presente, mas não o instante da resposta perdida. Marcar cobertura incompleta localmente e não publicar duração exata daquele intervalo. Isso preserva métricas v1 sem introduzir um tipo de espera incerta que leitores antigos interpretariam como tempo medido. O painel distingue `aguardando autorização`, `aguardando resposta`, espera canônica `owner_input` e indisponibilidade; não deduzir todas as dependências/revisões a partir de pedidos humanos.

A operação estruturada `wait-intervals` materializa pares v1 completos numa única edição do comentário, até 32 intervalos por operação e com identidade derivada estável por evento. Ela valida a execução e preserva o pareamento FIFO de todas as esperas existentes antes de publicar; não há exposição remota de um par parcial. Assim, lacunas históricas não sobrepostas podem ser inseridas sem reinterpretar esperas anteriores. Timestamps efetivos preservam frações de segundo e comparações usam instantes, não ordem lexicográfica de strings. Observações terminais estruturadas exigem evidência própria: resultado de worker não é sucesso de sessão; `test_run` exige relatório/evidência do teste. A CLI manual v1 continua sem novos campos obrigatórios.

### D8. Continuidade, privacidade e limites

Após conectar, receber `server.connected`, reiniciar ou perder o fluxo, revalidar contexto/vínculos e consultar atividade, permissões e formulários das sessões permitidas. A assinatura é live-only: consultas recuperam estado atual, nunca histórico exato. Não usar `experimental.session.log` para compensar lacunas nesta entrega, pois inclui eventos de conteúdo e exige outro desenho de minimização.

Heartbeat padrão de 5s e validade de saúde de 15s; atividade continua sob `activity_ttl` existente. Fila de fatos até 1000 itens por domínio e envelopes NDJSON de até 16 KiB; NDJSON excedente/ponte encerrada invalida continuidade. Backoff reaproveita limites existentes (até 900s). Outbox até 1000 operações pendentes: ao atingir limite, recusar nova aceitação com erro explícito, nunca descartar silenciosamente. Retenção de fatos consumidos de 7 dias; remover apenas consumidos ou fatos cuja perda já esteja marcada como lacuna, nunca operações pendentes. Esses são defaults de implementação documentados, não novos knobs obrigatórios de configuração.

Permissões/erros/formulários podem conter dados sensíveis mesmo sem mensagens. Projetar allowlist na ponte antes do IPC e novamente antes do cache. Nenhum log bruto de stdout/stderr da ponte, corpo de erro, argv de ferramenta, formulário ou resposta humana é persistido. Os IDs de operação e execução são validados com regras seguras existentes. Testes injetam segredos em todos esses pontos.

## Risks / Trade-offs

- [Coordenador deixa de emitir uma transição] -> As skills e handoffs passam a exigir a operação estruturada; mostrar ausência de registro, nunca tentar completar por inferência. Esta integração não é garantia universal de cumprimento pelo modelo.
- [Ponte adiciona runtime Node opcional] -> Isolar pacote e dependência fixada; dashboard/GitHub/CLI manual seguem sem Node. Testar artefato instalado e distribuição real.
- [Contextos de autenticação divergentes entre CLI e ponte] -> Mesmo ambiente herdado, URL e `Service.headers` do release, com testes de credencial ausente/negada; nunca fallback para outro servidor ou persistência de segredo.
- [Perda de evento] -> Invalidar continuidade, consultar estado atual e não publicar duração exata sem cobertura; isso sacrifica completude por veracidade.
- [Dois escritores externos não cooperativos] -> Posse local e deriva detectável reduzem risco, mas não oferecem CAS distribuído. Exigir coordenador único por issue/run e não prometer proteção inexistente.
- [Estado cresça ou disco falhe] -> Limites explícitos e recusa de aceitação; nunca remover banco, pendência não publicada ou dados reais automaticamente.
- [Contenção com mudanças visuais existentes] -> Integrar somente novos campos de detalhes/saúde sem redesenhar cartões; rodar a suíte de layout da revisão final.

## Migration Plan

1. Entregar operações e leitura retrocompatíveis com runtime ainda desabilitado por default. Não reescrever comentários v1 nem alterar a configuração real.
2. Distribuir ponte opcional com instrução de instalação fixa e verificar ausência de Node no caminho GitHub-only.
3. Validar em diretórios de estado/config e repositório/issue de teste explicitamente autorizados; sem publicação em issues reais por padrão. Fixtures e servidor fake não contam como smoke real OpenCode.
4. No smoke real controlado, testar sessão vinculada, atividade, pedido humano, interrupção, retomada, saída do painel e observador ainda ativo; coletar somente metadados sanitizados. Se não houver ambiente autorizado, registrar integração real NOT RUN, sem afirmar validação completa.
5. Habilitação operacional é ação posterior e explícita do usuário: configurar runtime, iniciar observador e iniciar workflow instrumentado. Não encerrar o dashboard ou agente atual.
6. Rollback: encerrar somente o observador/ponte desta integração e pausar publicação; preservar SQLite/outbox e comentários. A versão anterior ignora chaves locais novas, mas não deve operar em paralelo com o novo publicador; usar leituras offline até reconciliar pendências. Não apagar registros nem desfazer etapas publicadas automaticamente.
