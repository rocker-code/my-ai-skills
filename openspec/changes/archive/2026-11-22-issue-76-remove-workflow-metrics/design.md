# Design

## Context

Base inspecionada: `abf0dbd2370a59169e2a19f314b12efdc9a1b11c`, #75 entregue pela PR #79. Inventário por arquivos rastreados e busca de imports/texto:

| Componente | Consumidor verificado | Destino |
| --- | --- | --- |
| scripts/workflow-event, workflow_events.py | CLI de eventos e três suítes próprias; importa workflow_metrics | Remover ambos: único armazenamento é comentário operacional legado |
| scripts/workflow-report, workflow_metrics.py | CLI/relatórios e três suítes próprias | Remover ambos: parsing e cálculos não são usados pelos helpers de provas/posse |
| tests/test_workflow_metrics.py, test_workflow_events_api.py, test_workflow_execution_state.py | Testam comentários/eventos e analytics legados | Remover; garantias de prova/posse continuam nas suítes independentes existentes e cenários controlados de retomada |
| scripts/install-global | Exige workflow-event para validar pacote | Exigir somente helpers mantidos; preservar manifesto, integridade, rollback e config |
| tests/test_global_install.py | Atualiza fixture workflow-event e verifica publicação | Migrar fixture para helper mantido, preservando teste real de update |
| tests/test_instrumentation_distribution.py | Dois smoke commands legados; demais testes são sincronização de referências | Manter suíte de distribuição, trocar apenas smoke para helpers reais mantidos |
| tests/test_worktree_reservation.py | Lista smoke de helpers copiados | Retirar somente comandos removidos; preservar testes de posse/drift/takeover |
| specs workflow-metrics / workflow-execution-state / checkout-write-reservation | Contratos ativos do coletor e referência SAFE_ID | Deltas aprovados; preservar contratos funcionais mínimos e histórico |

Não há imports de workflow_events/workflow_metrics em workflow_evidence.py ou worktree_registry.py. O protocolo, resume e progresso já usam fontes canônicas após #75; varredura final verifica cópias distribuídas e documentação. SAFE_ID já é definido independentemente em worktree_registry.py, sem dependência de import.

## Goals / Non-Goals

Remover coleta e comentários, mantendo testes e retomada verificáveis. Não construir estado substituto, migrar comentários antigos, apagar arquivos históricos ou alterar integração Codex antes da #77. Durações de jobs CI e tempos necessários à validade de provas permanecem legítimos; não são analytics do workflow.

## Decisions

1. Remover integralmente o coletor em vez de extrair API: os únicos consumidores de estado desse módulo são seus próprios eventos/relatórios/testes. Estado nativo e provas existentes já cumprem as necessidades; duplicá-los recriaria a complexidade removida.
2. Aposentar os requisitos de workflow-metrics via delta REMOVED e Archive oficial; excluir o arquivo ativo vazio remanescente se a CLI não o remover. Atualizar Purpose de workflow-execution-state para a semântica atual sem reescrever archives.
3. Manter suites reais de workflow-evidence e worktree-reservation; remover testes cuja única obrigação é a funcionalidade excluída. Verificar negative packaging (scripts removidos não reaparecem) dentro da suíte de distribuição existente, sem framework novo.
4. Instalador bootstrap: quando install-global mudar, publicar primeiro snapshot imutável do source pelo parent; repinar scripts/install.sh e seus testes ao SHA remoto e digest verdadeiro antes do candidato final. Não usar SHA apenas local; manter validação criptográfica existente.
5. Comentários históricos permanecem no GitHub e archives; não são fonte ativa nem requisito de compatibilidade de leitura. Documentar ruptura dos comandos retirados em ambos README/CHANGELOG quando relevante.

## Risks / Trade-offs

- Confundir runtime com aprovação → conservar prova por HEAD, relatório/exit e revisão independente; cenários unknown/falha continuam bloqueando.
- Helper antigo permanecer instalado → testar update do manifesto removendo arquivo gerenciado sem apagar personalizações/desconhecidos.
- Bootstrap apontar source inexistente → pin remoto verificado antes do teste final; rollback pela versão anterior publicada ou revert da PR.
- Wiki externa não acessível pelo clone/connector → atualizar fontes e links sob controle do repo e declarar limitação; não inventar sincronização da Wiki.

## Verification

| Critérios #76 | Prova planejada |
| --- | --- |
| Remoção analytics/eventos/comentários e sem substituto | Inventário/diff + scan de imports e entrypoints ativos + teste negativo de distribuição |
| Instalação/update sem referências quebradas | Suíte test_global_install e test_install_launcher, smoke helpers mantidos |
| Retomada/worker unknown/correlação e posse | Cenários controlados nas instruções existentes e suíte worktree_reservation intacta |
| Testes/CI no HEAD e relatório ausente | Suíte workflow_evidence intacta, exit/artefatos e SHA final |
| Progresso/Kaizen sem timing e histórico preservado | Scan de fontes/cópias e diff archives pré-existentes vazio; README PT/EN |
| Contratos ativos coerentes | Verify oficial e openspec validate --strict + archive/sync |

Revisão de planejamento: o inventário acima mostra remoção de subsistema já dispensado pela #75, sem mudança de fronteira de autorização ou nova arquitetura; revisão inline suficiente. Revisão independente do diff final continua obrigatória. Nenhuma decisão material pendente.

## Verificação de implementação

Verify oficial (`openspec-verify-change`) aplicado após leitura de status/instructions e dos baselines de remoção em `abf0dbd`. Resultado advisory: sem CRITICAL, WARNING ou SUGGESTION; completude 5/5 tarefas pré-archive, 5 requisitos ADDED/MODIFIED e 19 remoções verificados. A suíte completa é o gate pós-archive obrigatório, ainda pendente neste registro; Verify não o substitui.

| Dimensão | Evidência |
| --- | --- |
| Completude | Quatro helpers, três suítes exclusivas e spec workflow-metrics removidos; callers e pins migrados |
| Correção | SAFE_ID próprio já implementado no registry intacto; retomada rejeita observação de outra execução/HEAD; progresso atual sem analytics; prova/ownership mantidos |
| Cenários | Walkthrough controlado: worker sem término permanece unknown; callback antigo/checkout ocupado bloqueia escrita; relatório necessário ausente não aprova; milestone usa estado atual e uma issue ativa. Não é E2E real |
| Coerência | Nenhum coletor substituto; imports consumidores ausentes; histórico preservado; source do instalador publicado e fixado em 96864599 com SHA-256 verificado |
| Testes executados | Instalador 37/37 (inclui update legacy→novo e personalizações preservadas); launcher 7/7; distribuição 4/4. Suíte completa final e revisão independente são requisitos da entrega, sem claim antecipado de aprovação |

A ordem de task 3.1 foi esclarecida: testes focados e Verify antes do Archive; suíte completa no HEAD final limpo após Archive, conforme follow-up. Nenhuma obrigação de teste foi removida. Wiki externa não foi alterada: este ambiente não oferece transporte de escrita para a wiki; fontes e documentação mantidas no repositório foram atualizadas.
