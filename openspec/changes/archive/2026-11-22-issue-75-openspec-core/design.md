# Design

## Context

Revisão base `42eb306d29d2f89d4e9c0fde5d12a282bcacb0c4`; issue #75 consultada via integração, sem comentários nem PR existente. OpenSpec instalado 2.1.1; integração versionada gerada por 2.0.0. O protocolo e skills atuais sobrepõem audit/explore/ready/planning/apply e duas revisões. `scripts/sync-skill-references` copia protocolos/templates para consumidores e testes verificam essas cópias e instruções. Contratos existentes de reserva, evidence, M2T e distribuição permanecem válidos, exceto a dependência de Kaizen no closeout M2T explicitamente modificada nesta proposta. Ver motivação em proposal.md.

## Goals / Non-Goals

**Goals:** entregar dois checkpoints verificáveis: primeiro o caminho de uma issue, depois scheduler estritamente sequencial, com políticas canônicas pequenas e testes proporcionais.

**Non-Goals:** novo executor, serviço, registro persistente, catálogo, dispatcher ou substituto de OpenSpec. Remover helpers e spec de métricas pertence a #76; seleção e instalação Codex a #77; auditoria geral de arquivos a #78. Arquivos métricos existentes não autorizam continuar publicando eventos pelo fluxo normal.

## Decisions

1. `openspec-workflow` fica como adaptador de capacidades/integrações: descoberta do perfil real, issue/decisões/contratos, trabalho isolado, validação exata, teste/CI e archive. Não reescrever prompts oficiais. Verificar suporte real ao Verify e habilitá-lo pelo mecanismo oficial do perfil antes de concluir indisponibilidade; arquivo ainda não gerado não é perfil sem suporte. Preservar configurações existentes e reportar falha de habilitação precisamente. Remover gates audit/ready/explore após migrar callers; `implement-issue` e `apply-issue` só permanecem como roteamento mínimo quando o uso público justificar preservar essas entradas. Alternativa rejeitada: mover toda a antiga orquestração para um arquivo gigante.
2. Consolidar regras gerais em AI_WORKFLOW e política de revisão existente. Uma revisão independente atual aprovada satisfaz o gate final; checagem de merge confirma validade e requisitos, sem reexecutar auditoria completa. Mudança de HEAD invalida provas afetadas e a aprovação do candidato anterior, exigindo avaliação independente das mudanças pertinentes. Preservar domínio Magento/Mobile/segurança quando aplicável.
3. Reduzir milestone-orchestrator a escopo, ordem por dependências, uma issue ativa, ownership/recuperação e entrega. Nenhuma fase de outra issue roda durante a ativa; estacionar inclui motivo, revisão/branch/checkpoint e próxima ação no conteúdo canônico existente. Subagentes disponíveis podem executar planejamento/Apply/revisão da mesma issue em contextos realmente independentes; indisponibilidade é explícita, nunca simulada.
4. Recuperação lê Git/GitHub/OpenSpec e fontes nativas de execução; não depende de workflow-event/comments. Protocolos WORKTREES, TEST_STRATEGY, REVIEW_POLICY e INCREMENTAL_DELIVERY continuam como fonte de invariantes. Modificar a requirement `Closeout condicionado a elegibilidade e posse` de `m2t-worktree-lifecycle` para remover somente a dependência obrigatória de Kaizen, preservando seus cenários e demais salvaguardas; preservar cleanup seguro e sandboxes M2T até elegibilidade real.
5. `simplify` é a única nova skill aprovada, porque oferece capability reutilizável explicitamente pedida, sem coordenar workflow. Adaptar princípios upstream descritos na issue, sem copiar regras específicas TypeScript. Não executar sem problema concreto/pedido.
6. Comunicação mínima prevalece em todos consumidores ativos, incluindo capture-evolutions, prepare-pr, resume/status e templates que pedem relatos de etapas. Atualizar conteúdo canônico, sem apagar comentários antigos. Eventos/relatórios permanecem fisicamente até #76, mas não são chamados pelo workflow normal.
7. Não há nova camada executável de scheduler para provar prosa. Validar o comportamento de skills com cenários controlados/forward-tests em contextos independentes, scanner de referências e testes existentes de segurança/distribuição. Não inventar E2E real de agente quando apenas inspeção estática ocorreu.

## Migration Plan

- Inventariar referências rastreadas nos grupos runtime/skills/protocol/docs/installer/tests antes de cada remoção. Separar documentação ativa de archives históricos e specs de métricas ainda vigentes para #76.
- Checkpoint 1: migrar ciclo single-issue e revisão, consumidores, testes e README PT/EN; sincronizar referências e verificar links/consistência. Guardar diff/commit reversível.
- Checkpoint 2: reduzir scheduler e retomada/progresso; testar sequência com independentes, contrato produtor/consumidor, blocker estacionado, interrupção e PR existente.
- Rodar suíte local obrigatória, validação OpenSpec estrita, revisão independente e archive no branch da issue; preservar artifacts/specs no PR. Rollback por revert de commits específicos, sem apagar trabalho ou reset forçado.

## Validation matrix

| Requisito / risco | Alteração planejada | Prova proporcional |
| --- | --- | --- |
| T1/T2 ciclo simples e replanejamento | Adaptador nativo e callers migrados | Cenário controlado, scanner de gates e OpenSpec strict |
| T3/T4 review e HEAD | Revisão consolidada/merge loop | Cenários HEAD igual, push e CI falho; testes evidence existentes |
| T5 fila e contratos | Scheduler uma issue ativa | Forward-test milestone independente + produtor/consumidor |
| T6 retomada/PR existente | Resume a partir de fontes canônicas | Cenário interrupção após Propose/Apply e PR existente, sem duplicação |
| T7 limites reais e segurança | Worktree/evidence/credenciais inalterados | Suítes test_worktree_reservation/test_workflow_evidence e revisão independente |
| T8 comentários | Política prospectiva e callers migrados | Scan de instruções de log/comentário e cenário normal sem publicação |
| T9 Verify gerado, não gerado suportado ou sem suporte | Descoberta/habilitação oficial, limitação explícita | Perfil real, geração oficial quando suportada e cenários de limitação, sem verificador custom |
| T10 simplify | Capability pequena opcional | Cenários código claro e duplicação concreta, com provas preservadas |
| Distribuição e referências | Sync e docs ativos | `scripts/sync-skill-references`, testes de pacote/links, suíte unittest |

Comandos existentes: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`; `bash scripts/sync-skill-references`; `openspec validate issue-75-openspec-core --strict`. Testes dedicados a gates removidos precisam migrar para invariantes observáveis sem enfraquecer provas de segurança. Metadados de performance permanecem sob responsabilidade de #76.

## Risks / Trade-offs

- [Perder salvaguardas escondidas em wrappers] → inventariar callers e manter menor adaptador necessário, verificando ownership, CI/reviews e contratos.
- [Fontes geradas divergentes] → sincronizar a partir do protocolo canônico e verificar idempotência/links antes de declarar pronto.
- [Supor capacidade Verify/subagente] → consultar capacidades reais e registrar NOT RUN/limitação; nunca criar skill falsa nem aprovação independente simulada.
- [Simplificar instruções sem comprovar execução real] → distinguir checks estáticos, cenários controlados e execução nativa de agente nos resultados.
- [Mudança simultânea de instalador/métricas] → sequenciar #75 → #76 → #77 → #78 e manter responsabilidade explícita de cada PR.

## Planning review

Revisão inline: requisitos/decisões atuais mapeados na spec e matriz; nenhum acréscimo de produto, contrato aplicativo ou custo externo. Isolamento, evidência final, proteção de credenciais, revisão independente e auto-if-green/manual preservados. Revisão independente solicitou alinhar o contrato M2T de cleanup sem Kaizen e distinguir Verify não gerado de perfil sem suporte; ambas as correções foram incorporadas aos deltas/design/tasks. Proposta apta à rechecagem independente de arquitetura antes de Apply, sem pedir aprovação rotineira ao usuário. A validação formal será executada sobre os artefatos completos; resultados exatos seguem no handoff do worker, não em comentário GitHub.

Revisão independente de planejamento: `review_plan75` aprovou a revisão `025023f90cb580c71fc7fc6267eaaf2fc69f7401` após corrigir os dois achados e reexecutar validação estrita.

## Implementation verification

A revisão independente `review75` aprovou `2ee67ea627581fe47b901ec83d976c795287f319`; strict foi rechecado independentemente. A skill oficial `openspec-verify-change`, gerada por OpenSpec 2.1.1 com profile custom preservando workflows existentes, foi executada como instrução nativa pelo agente sobre esta change. Não existe comando CLI inventado de Verify.

| Dimensão | Resultado |
| --- | --- |
| Completeness | 12/12 tarefas; 9 requirements de issue-delivery e 1 MODIFIED M2T mapeadas |
| Correctness | Políticas/callers em AI_WORKFLOW, openspec-workflow, entradas mínimas, pr-audit/merge eligibility, scheduler/resume e WORKTREES; cenários controlados independentes e suíte preliminar 271 testes PASS |
| Coherence | Decisões do design preservadas, bootstrap publicado intacto, referências sincronizadas e guards de evidência/ownership mantidos |

Nenhum achado crítico ou divergência material identificado no Verify/review. Limitação: cenários de interpretação de skills são forward-tests controlados, não E2E real de sessão OpenCode/Codex ou merge hospedado. Testes/CI reais continuam obrigatórios; o gate local final será executado no HEAD limpo publicado, fora deste commit. Métricas/helpers físicos permanecem para remoção por #76; seu uso foi retirado das instruções ativas.
