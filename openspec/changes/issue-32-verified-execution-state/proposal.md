# Proposal

## Why

O acompanhamento do workflow ([#32](https://github.com/rocker-code/my-ai-skills/issues/32)) registra apenas o horário em que o orquestrador grava cada evento: não correlaciona etapa/worker com processo, job ou execução de teste, não registra a fonte nem o horário de uma observação e mede uma etapa aberta como trabalho até o momento do relatório, mesmo quando o processo já terminou ou desapareceu. No milestone 31 isso permitiu anunciar uma suíte "rodando" sem PHPUnit nem JUnit, e uma conversa com várias entregas misturou métricas. O acompanhamento precisa refletir apenas o que foi confirmado no runtime e manter resultados desconhecidos como desconhecidos.

## What Changes

- `scripts/workflow-event` ganha, de forma aditiva no registro `schema_version: 1` existente:
  - evento `dispatch` (despacho assíncrono de worker) que abre a etapa do worker sem confundir o retorno imediato do despacho com a conclusão;
  - evento `observe` (observação de estado) com estado (`running`, `completed`, `failed`, `interrupted`, `unknown`), fonte classificada como confirmatória ou insuficiente, horário da observação, identificador de execução (worker/processo/job/execução de teste/CI), código de saída, presença de relatório e referência de log;
  - horário informado (`--observed-at`) validado para eventos relatados por workers/callbacks, preservando o horário de gravação;
  - motivos de espera `tests` e `environment`, além dos existentes;
  - próximo passo curto (`--next`) opcional;
  - recusa de abrir etapa/espera num registro já finalizado (a conversa que segue para outra issue precisa do registro dessa issue).
- `scripts/workflow_metrics.py` passa a derivar o estado verificado por etapa/worker (trabalho, espera por motivo, desconhecido, interrompido, concluído, sem observação), encerra a contagem de trabalho na última observação confirmada quando o processo terminou ou ficou desconhecido, marca evidência incompleta (término ou relatório ausente) sem aprovação implícita e produz um resumo simples: etapa atual, estado verificado, última prova confirmada, bloqueio, próximo passo e horário da verificação.
- `scripts/workflow-report` exibe esse resumo (Markdown e JSON); o CSV permanece compatível.
- `skills/milestone-orchestrator/SKILL.md` e `protocol/AI_WORKFLOW.md`: reconciliar com runtime/evidência antes de anunciar atividade ou conclusão, inclusive após interrupção/compactação/retomada; usar notificações de término do runtime em vez de polling sem finalidade; separar responsabilidades por issue/etapa e só ampliar escopo quando autorizado; seguir automaticamente sem exigir comando do usuário por etapa.
- `skills/milestone-progress/SKILL.md`, `README.md`/`README.en.md` (paridade) e `plugins/my-ai-skills/` regenerado por `scripts/sync-plugin`.
- Registros antigos continuam legíveis sem migração; leitores antigos ignoram os novos tipos de evento.

Fora do escopo:
- Adaptador final para o registro/consulta por execução do M2T — follow-up **CONTRACT_BLOCKED** em [M2T #12](https://github.com/rocker-code/m2t/issues/12) (capacidade inexistente em `rocker-code/m2t@eb40523`). Esta entrega aceita a referência genérica (`--execution-kind test_run`, `--log-ref m2t:<id>`) sem depender do contrato.
- Notificação externa para celular (entrega própria).
- Consulta ativa ao runtime pelos scripts: o executor faz a consulta suportada pelo seu runtime e registra a observação.
- Registro de evidência de teste reutilizável e transporte de provas ([#31](https://github.com/rocker-code/my-ai-skills/issues/31)); reserva de checkout ([#35](https://github.com/rocker-code/my-ai-skills/issues/35)); log de hipóteses de retry ([#34](https://github.com/rocker-code/my-ai-skills/issues/34)).

## Capabilities

### New Capabilities
- `workflow-execution-state`: correlação de run/issue/etapa/worker com execuções observadas, classificação verificada de trabalho/espera/desconhecido e resumo de progresso por issue a partir do registro de eventos do workflow.

### Modified Capabilities
(nenhuma — `openspec/specs/` ainda não possui capacidades)

## Impact

- Código: `scripts/workflow-event`, `scripts/workflow_metrics.py`, `scripts/workflow-report`.
- Testes: novo `tests/test_workflow_execution_state.py`; `tests/test_workflow_metrics.py` continua passando sem alteração.
- Skills/protocolo/docs: `skills/milestone-orchestrator/SKILL.md`, `skills/milestone-progress/SKILL.md`, `protocol/AI_WORKFLOW.md` (+ cópias empacotadas em `skills/*/references/`), `README.md`, `README.en.md`, `plugins/my-ai-skills/**` (gerado).
- Dados: comentário oculto por issue/run no GitHub; mudança aditiva, sem bump de schema.
- Coordenação: #31 estende os mesmos scripts; implementação serializada (#35 → #31 → #32). Sem dependência rígida.
