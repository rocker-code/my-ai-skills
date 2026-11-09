# Proposal

## Why

O dashboard já lê GitHub e possui um adaptador OpenCode, mas o runtime está desabilitado por padrão, os vínculos são manuais e a coleta contínua depende do painel aberto. As etapas e esperas já têm um registro canônico, porém sua gravação depende de chamadas avulsas do coordenador; falta conectar essas peças para mostrar atividade real e registrar o workflow sem comandos do usuário por etapa.

## What Changes

- Vincular automaticamente a sessão executora à issue/run/etapa/worker/execução informados pelo coordenador, preservando validação explícita e `aew bind` manual.
- Disponibilizar observador headless opt-in, independente da TUI, com eventos oficiais do OpenCode 2.2.5 e consultas periódicas de reconciliação.
- Oferecer uma operação estruturada de transição ao coordenador para registrar início, despacho, término e esperas, com repetição segura e recuperação de falhas de publicação.
- Correlacionar sinais de atividade, falha, interrupção, permissão e formulário pendentes sem deduzir etapas de prosa ou confundir término de turno com conclusão do trabalho.
- Manter o observador e o dashboard sem escrita no GitHub: somente o coordenador publica eventos de workflow pelo registrador canônico.
- Mostrar atividade, esperas observadas, lacunas de coleta e publicação pendente separadamente de etapas e tempos canônicos.
- Preservar configuração existente, registros v1, CLI manual, funcionamento sem OpenCode e mudanças visuais já em andamento.

## Capabilities

### New Capabilities

- `opencode-workflow-instrumentation`: observador opt-in de runtime, transporte oficial, correlação de sinais, ciclo de vida headless e recuperação sem captura de conteúdo.

### Modified Capabilities

- `milestone-monitor-state`: consumir observações do coletor independente com frescor verificável, preservar leitura sem mutações de workflow e distinguir espera observada de registro canônico.
- `workflow-execution-state`: transições automáticas declaradas pelo coordenador, vínculo automático, publicação idempotente e reconciliação de observações antes de registrar resultados.

## Impact

- Fontes: `scripts/milestone_monitor/{cli,config,runtime,collector,store,projection}.py`, `scripts/workflow-event`, `scripts/workflow_metrics.py` e novos módulos locais de observação/transição quando necessários.
- Integração do coordenador: `skills/milestone-orchestrator/SKILL.md`, `protocol/AI_WORKFLOW.md` e handoffs das skills executoras afetadas; automação significa chamadas estruturadas nessas fronteiras, não detecção universal de qualquer conversa.
- Testes de contrato, armazenamento, métricas, CLI, projeção e integração isolada; documentação operacional e README pt-BR/en; distribuição regenerada por `scripts/sync-plugin` na implementação.
- OpenCode fixado em 2.2.5, CLI/auth oficiais; manter Python stdlib para o monitor. Para eventos contínuos, adicionar ponte opcional Node com `@opencode/client` 2.2.5: o CLI desse release acumula a resposta inteira e não entrega o fluxo incrementalmente. Nenhum plugin obrigatório, serviço instalado automaticamente ou mudança automática da configuração real.
- Fora do escopo: inferir etapas pelo conteúdo, registrar prompts/respostas/logs, tokens/custos, controlar agentes, instrumentar subprocessos arbitrários, aprovar testes, fechar issues/mergear PRs ou fornecer runtime nativo Codex. Nenhuma alteração de layout da TUI é objetivo desta mudança.
