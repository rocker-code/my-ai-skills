# Tasks

## 1. Contrato e ponte oficial de eventos

- [x] 1.1 Adicionar fixtures mínimas de eventos/consultas do produtor 2.2.5 fixado em `design.md`, incluindo timestamps, identidades, permissões e formulários; verificar SHA do schema, relação dos tipos com definições do produtor e ausência de conteúdo sensível, sem confundir fixtures com integração real.
- [x] 1.2 Criar pacote opcional `integrations/opencode-observer/` com cliente oficial 2.2.5 fixado e lockfile; verificar instalação reproduzível, import do pacote instalado, descoberta por `Service.discover` e autenticação explícita equivalente ao CLI, sem `ensure`, `stop` ou acesso privado a credenciais.
- [x] 1.3 Implementar assinatura cancelável, allowlist de tipos/sessões e projeção NDJSON versionada antes do IPC; testar sessão alheia, contexto divergente, evento inválido/grande, falha/autenticação negada, encerramento e segredo em formulário/erro, verificando saída e stderr sanitizados.
- [x] 1.4 Documentar instalação opcional e protocolo da ponte no pacote e no guia operacional pt-BR/en; verificar exemplos contra o contrato e confirmar que `dashboard` e `collect --once` continuam utilizáveis sem Node ou dependências instaladas.

## 2. Observador headless e posse compartilhada da coleta

- [x] 2.1 Adicionar posse de coleta com lock/epoch e estado versionado em `store.py`, preservando schema SQLite 1; testar concorrência entre processos, saída/crash do dono, heartbeat vencido sem roubo de lock, respostas antigas e bancos existentes/futuros/corrompidos sem recriação ou perda.
- [x] 2.2 Implementar `aew observe` foreground com validação opt-in, workers GitHub/runtime e supervisão da ponte; testar ausência de alvos/runtime/ponte, modo degradado, timeout, cancelamento e manutenção da coleta sem TTY ou dashboard aberto, sem interromper sessões do agente.
- [x] 2.3 Coordenar `dashboard`, `collect --once` e refresh com a posse existente, incluindo passagem segura da coleta da TUI ao observador; testar dois painéis, segundo observador recusado, consulta antiga em voo e backoff preservado, sem publicações concorrentes ou encerramento de agentes.
- [x] 2.4 Persistir fatos normalizados, saúde e lacunas com limites/retenção de D8; testar saturação, envelope acima de 16 KiB, disco cheio e falha de escrita sem renovar frescor nem apagar dados desconhecidos; documentar ciclo de vida, limites e saída no guia pt-BR/en.

## 3. Correlação, estado e pendências observadas

- [x] 3.1 Estender `runtime.py` para consumir fatos da ponte e reconciliar atividade/permissões/formulários por consulta oficial, reutilizando validações Git/localização; testar revisão de vínculo, contexto/PID/versão, worktree movida, evento anterior ao bind e evento atrasado de A após B, sem contaminar a execução atual.
- [x] 3.2 Modelar pedidos pendentes por identidade e cobertura temporal, sem persistir textos/respostas; testar múltiplos pedidos, resposta/rejeição/cancelamento individual, inatividade sem pedido, perda/reconexão/reinício e consulta sem horário da resolução, preservando lacunas explícitas.
- [x] 3.3 Adaptar projeção e detalhes/saúde da TUI para observador vivo, sinais locais e publicação pendente sem redesenhar cartões; testar amostra anterior à abertura com dono saudável, epoch antigo, TTL vencido, heartbeat sem observação nova, espera canônica com worker paralelo e fechamento GitHub, sem dupla contagem ou duração inventada.
- [x] 3.4 Documentar rótulos e distinções entre runtime, etapa registrada, espera observada e tempo canônico em pt-BR/en; verificar exemplos contra fixtures e executar regressões `test_milestone_monitor_state.py`, `test_milestone_monitor_runtime.py` e `test_milestone_monitor_tui.py` com bytecode desabilitado.

## 4. Transições canônicas, idempotência e publicação

- [x] 4.1 Extrair validação/construção de eventos do `workflow-event` para API compartilhada, mantendo comandos manuais e v1; testar todas as fronteiras existentes, horário efetivo de `run-start`, IDs tipados, callbacks atrasados e métricas legadas, sem novos campos obrigatórios para usuários existentes.
- [x] 4.2 Implementar journal/outbox transacional local com `operation_id`, hash, dependências e estados separados de publicação/vínculo; testar mesma operação, ID reutilizado com outro payload, crash antes/depois da aceitação, limite de 1000 pendências e disco cheio sem descartar operação aceita ou chamar rede sob transação SQLite.
- [x] 4.3 Implementar publicação pelo coordenador com metadado opcional de operação no evento v1 e lock compartilhado com a CLI manual; testar perda de resposta após GitHub salvar, comentário duplicado, deriva inesperada, concorrência cooperativa e ordem causal de início/espera/término, sem duplicar evidências ou duração; documentar limite de proteção entre máquinas não cooperativas.
- [x] 4.4 Disponibilizar `aew workflow transition` e `aew workflow reconcile` com JSON limitado e retornos de aceitação/publicação/vínculo; testar entrada inválida, identidade/escopo errado, falta de autorização/helper/GitHub, replay e estado pendente, verificando que a instrumentação falha explicitamente sem impedir desenvolvimento autorizado.
- [x] 4.5 Integrar bind automático após publicação de abertura, incluindo chegada posterior do ID real da sessão e troca explícita de execução; testar falha parcial de publicação/bind, retry sem nova abertura, sessão já vinculada e ID ausente, sem substituição silenciosa ou uso da sessão coordenadora como fallback.
- [x] 4.6 Implementar reconciliação conservadora de resultado/esperas conforme D5-D7, com união de pedidos sobrepostos e exclusão de intervalos já canônicos; testar turno bem-sucedido sem entrega, teste sem prova, esperas explícitas concorrentes, resposta perdida e intervalos incompletos, preservando métricas v1 e sem converter sinal de sessão em conclusão de etapa.
- [x] 4.7 Documentar as operações e exemplos de retry/recuperação em pt-BR/en, incluindo comandos leitores versus publicadores e limites de medição; verificar `--help`, exemplos isolados e regressões de `workflow-event`, `workflow-report` e `workflow_metrics.py`.

## 5. Integração nas fronteiras reais do coordenador

- [x] 5.1 Atualizar `skills/milestone-orchestrator/SKILL.md` e `protocol/AI_WORKFLOW.md` para emitir transições estruturadas nas 13 etapas, carregar IDs estáveis e reconciliar na retomada; verificar contrato por testes de conteúdo e walkthrough de uma issue do despacho até resultado, sem criar outro escritor ou exigir comando do usuário por etapa.
- [x] 5.2 Atualizar handoffs das skills executoras efetivamente afetadas com issue/run/etapa/worker/execução/sessão/worktree e retorno de evidência, preservando gates; testar planning para Apply, subagente sem ID disponível, rework e continuação de outra issue, sem ativar instrumentação por mera invocação isolada de skill.
- [x] 5.3 Atualizar README e documentação operacional pt-BR/en com ativação voluntária, observador independente, recuperação/rollback e capacidade degradada; verificar paridade, comandos reais, ausência de instalação automática de serviço e manutenção do fluxo GitHub-only/Codex sem adaptador runtime nativo.

## 6. Verificação integrada e distribuição

- [x] 6.1 Executar cenário ponta a ponta isolado com GitHub fake e transporte oficial simulado: início/transição/bind, atividade, pedido humano, publicação perdida, queda/retomada e painel fechado; verificar estado local, comentário v1, métricas e identidades contra todos os cenários das três specs, sem qualquer escrita em alvos/config/cache reais.
- [x] 6.2 Executar smoke OpenCode 2.2.5 com ponte/pacote instalados e sessão de teste explicitamente autorizada, estado/config isolados e sem publicação real não autorizada; verificar eventos incrementais, autenticação, permissão/formulário, interrupção, reconexão, observador sobrevivendo à saída da TUI e apenas metadados nos artefatos. Sem ambiente autorizado, registrar NOT RUN e a pendência, sem declarar integração real validada.
- [x] 6.3 Executar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_milestone_monitor*py'`, suíte Python completa e testes do pacote Node pelo comando entregue em seu manifest; verificar retorno zero, sanitização de segredos, ausência de dependência Node nos caminhos antigos e preservação dos layouts da revisão final.
- [x] 6.4 Regenerar distribuição com `scripts/sync-plugin`, incluindo ponte opcional e referências canônicas necessárias; verificar segunda execução idempotente, ausência de `node_modules`/segredos, execução do artefato distribuído e demo offline intacta.
- [x] 6.5 Revisar rastreabilidade requisito-cenário-teste e evidências da revisão exata, executar `openspec validate integrate-opencode-workflow-instrumentation --strict --json --no-interactive` e `git diff --check`; verificar nenhum gate anunciado sem evidência e registrar limitações de smoke/concorrência antes da revisão final.

## Workflow follow-up

- Revisar a proposta e a implementação na revisão exata antes de arquivar; sincronizar deltas e inspecionar as specs resultantes somente no workflow de archive.
- Commit, push e PR dependem do escopo de publicação autorizado; esta proposta não os executa.
- Ativar runtime, instalar dependências opcionais e iniciar observador no ambiente real somente por ação explicitamente autorizada; não encerrar nem recarregar o dashboard/agente atual como efeito colateral.
