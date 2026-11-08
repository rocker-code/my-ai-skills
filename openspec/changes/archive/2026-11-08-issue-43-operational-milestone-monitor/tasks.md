# Tasks

## 1. Pré-flight e fronteiras de confiança

- [x] 1.1 Em fresh Apply, verificar SHA de proposta revisado, issue/comentários/PRs atuais, reserva exclusiva e dependências #17/#44 ancestrais; registrar parecer independente e reconciliação das políticas lidas na base ee33197 antes de implementar.
- [x] 1.2 Revalidar freeze técnico já documentado no design: release oficial OpenCode 2.2.5/commit `9bbb8ce18c80f099e0e448775f59d965ead40a21`, CLI e server.info/version, contexto compartilhado descoberto ou --server explícito (nunca --standalone), session.active e session.get/location. Criar fixture mínima dos envelopes oficiais sem dados pessoais e provas de ausência/401/404; divergência material volta ao plano. Rodar smoke read-only próprio M8; não tratar pesquisa já resolvida como pergunta ao usuário.
- [x] 1.3 Criar estrutura de scripts/milestone_monitor e CLI aew com config versionada/caminhos XDG/help/validação sem fontes obrigatórias; provar M6 com tests de config inválida/sem alvos e documentar configuração inicial em pt-BR/en.

## 2. Persistência e ingestão v1

- [x] 2.1 Implementar SQLite schema 1, snapshots transacionais, saúde por fonte e geração contra resposta atrasada; provar restart, rollback, dois escritores, ENOSPC/erro categorizado e schema futuro com tests store M5/M6/M9 e documentar local/limites do cache.
- [x] 2.2 Integrar parse_run_comment/summarize_run, validação de identidade, hash/upsert de snapshots, seleção de run/histórico e conflitos; provar duplicata, last_seen atualizado, empate, legado, callback A/B e registro malformado com M5 e regressões existentes metrics/execution.
- [x] 2.3 Reutilizar correlação por incarnação para projeção por worker sem segundo emparelhador; se extração interna necessária, preservar byte a byte resultados públicos nos fixtures canônicos e executar test_workflow_metrics.py/test_workflow_execution_state.py antes da suíte ampla (M4/M11).

## 3. GitHub e reconciliação

- [x] 3.1 Implementar inventário de milestones numéricos/issues/comentários completamente paginado por alvos explícitos, excluindo PRs e preservando não instrumentadas/vazios; provar M2 e falha na segunda página sem snapshot parcial em fake gh, documentando credenciais já existentes e fontes.
- [x] 3.2 Implementar vínculo verificado de PRs via candidatos/timeline e referência de fechamento, merge/head somente oficiais; provar PR ambígua, baseline por mera menção, issue aberta com PR mergeada, fechamento sem entrega e reabertura/movimentação em M7.
- [x] 3.3 Implementar timeout/backoff/rate-limit/coalescência e sanitização allowlist antes de persistência; provar M6/M9 com 401/403/404/429, JSON inválido, timeout, título ANSI e erro com segredo; documentar mensagens e recuperação sem gravar stderr bruto.

## 4. Adaptador OpenCode e projeção

- [x] 4.1 Implementar bind/unbind transacional explícito por incarnação/sessão/worktree/contexto, branch somente verificada, sem inferência de texto; provar rejeição sem alterar vínculo anterior, local incompatível, sessão reutilizada e incarnação terminal em M8; documentar comandos reais de vínculo.
- [x] 4.2 Implementar consultas oficiais dirigidas de runtime, filtrar dados não vinculados, distinguir ausente/inativa/erro e revalidar server.info/contexto e session.get/location em cada ciclo que confirme atividade; provar movimento sem restart, mesmo projeto/worktrees distintos, subpath não concatenado, envelopes sem data de location/info, troca de processo/versão, contrato fake + smoke read-only próprio e sessão ativa sem prova de test_run em M8/M9. Falha não renova TTL nem altera o agente.
- [x] 4.3 Implementar precedência exclusiva D5, frescor por fonte, conflitos, timestamps UTC e tempos canônicos sem estimativas; provar matriz M4/M11 com espera humana, outros waits, falha/interrupção, paralelo, terminal seguido de running, TTL e clock futuro; documentar significado de fechado vs entregue.

## 5. TUI operacional

- [x] 5.1 Implementar reducer por identidade, sanfonas independentes, filtros/totais, seleção estável, detalhes/histórico e modos compacto/detalhado; provar M2/M3 com testes unitários sem terminal e documentar todas as teclas.
- [x] 5.2 Implementar régua real do protocolo, labels pt-BR, estados textuais distintos e viewport da etapa atual, sem concluir etapas anteriores implicitamente; provar Apply sem Explore, etapa desconhecida, rework e paralelo em M3/M11.
- [x] 5.3 Integrar coleta em segundo plano com UI responsiva, refresh/offline e shutdown restrito ao painel; provar fila limitada/timeout e cache vazio/desatualizado em M6/M8, confirmando que sair não interrompe OpenCode.
- [x] 5.4 Implementar largura de células, resize, rolagem, ASCII/sem cor e controles sanitizados; testar render fake e smoke PTY/Ubuntu/tmux 110x30 e 40x12 com M3/M9, registrando resultado/limite observado e preservando demo simulada M1.

## 6. Instalação e distribuição

- [x] 6.1 Implementar instalador local opt-in sem sudo/alterar shell rc, recusa de symlink conflitante e launcher independente de cwd; provar em bin/state/config temporários, execução de outro diretório e saída segura sem TTY em M10, documentando PATH/uninstall/cache/clone retido.
- [x] 6.2 Atualizar allowlist/cópia do pacote em scripts/sync-plugin e regenerar distribuição; executar CLI/help/coleta fake a partir do pacote gerado e inspecionar diff sem edição manual de plugins/my-ai-skills (M10).
- [x] 6.3 Consolidar README.md/README.en.md em paridade para arquitetura, fontes, limites foreground, instalação e continuidade OpenCode/Codex; verificar exemplos executáveis com caminhos temporários e demo offline ainda claramente separada (M1/M10).

## 7. Integração e verificação final

- [x] 7.1 Executar primeiro `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_milestone_monitor_*.py'` e regressões `-p 'test_workflow_*.py'`; preencher M1–M11 com cenário→código→teste/evidência, sem apresentar fake como integração real nem metadata como veredito.
- [x] 7.2 Executar suíte completa `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`, smoke integrado com dois projetos e restart/offline e validação `openspec validate issue-43-operational-milestone-monitor --strict --json --no-interactive`; registrar verificações suportadas e qualquer NOT RUN/blocker, sem reduzir gates ou implementar outra issue.

## Workflow follow-up

- Depois de implementação, testes e verificação, usar archive oficial na branch da #43; inspecionar specs sincronizadas e arquivo, sem PR de archive separada.
- Concluir sync-plugin/self-review/commits antes do gate local final; registrar e verificar suite no HEAD limpo via workflow-evidence e manter ID fora do commit. Qualquer commit posterior invalida esse gate.
- Invocar prepare-pr, revisão independente pr-audit/architecture-audit e github-resolution conforme instrução do coordenador; não inferir CI_GREEN sem checks atuais e não alterar política de merge nesta mudança.
- Reutilizar worktree/reserva entre sessões, não escrever workflow-event em paralelo com coordenador e preservar a matriz/observações para handoff. Aplicar hooks automáticos CI_PERFORMANCE sem benchmark extra; repetir falha segue attempt-log/TEST_STRATEGY.
