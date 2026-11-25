# Tasks

## 1. Trabalho entregue e preservado

Os itens concluídos abaixo representam implementação histórica verificada no Git, não testes aprovados para a nova candidata. Matriz e limites em `design.md`; proposta anterior `f159134b68ca5c8d13ffcb1a38b7a3c7673dbcc8`.

- [x] 1.1 Entregar entrada global `resume-workflow` e regras de escopo/posse/preservação/UNKNOWN, mantendo `milestone-orchestrator` como único coordenador; implementação consta na PR #62 incorporada.
- [x] 1.2 Distribuir roteamento natural e teste inicial de descoberta, documentar pedido/limites em README pt/en e changelog; arquivos existentes confirmados no checkout e no alvo.
- [x] 1.3 Integrar historicamente #71/PR #72 (`5e33688d2a9db702e6bd0f2027d778f3baebdf35`) e preservar commits posteriores de fixture/recibo T1/dois turnos T7/guard de argv/detectores, identificados na entrada `d34c1c1d4438758cc88e43b3c31fce22a0cc9d30`; essa presença não aprova smoke nem suíte final.

## 2. Integração revisada no Apply novo

- [x] 2.1 Após revisão independente da proposta pinada e parada do Planning, conferir ID nativo próprio, transferência/verify da reserva, Git/dirty/ignored, issue #61 e políticas pinadas; obter `openspec instructions apply --change issue-61-opencode-safe-resume --json` e confirmar tarefas/refs sem novo change/branch/worktree.
- [ ] 2.2 Integrar exatamente `12ca324faf2865faa62d16e55715d3ddd0adb53a` com `git merge --no-ff --no-commit`, revisar/resolver somente conflitos compatíveis e criar merge commit; comprovar ambas ancestralidades, preservação dos 38 commits e nove bytecodes, sem reset/rebase/stash/clean/aceite de drift.
- [ ] 2.3 Reconciliar sobreposições com as políticas/semântica atuais, inclusive a cópia inicial do change em main, mantendo multiagente/TOML/referências/remoções de telemetria e sem audit/ready; comprovar diff, pins A_R1/B_R1 e bytes do instalador do alvo inalterados, rodando `test_instrumentation_distribution.py` e `test_install_launcher.py` por discovery antes de modelo (I1/D1).

## 3. Fixtures e provas focadas compatíveis

- [ ] 3.1 Migrar shim/prompts/snapshots para issue/corpo/decisões/PR/head/checks/dependências read-only e Git/OpenSpec/recibos; remover dependência de helpers/ledger e endpoints de semeadura de comentários; usar commits Git reais no PR/head e provar recusa de writes/erro/saída inválida em regressões offline (T4/T5/T7), sem novo registro de produção.
- [ ] 3.2 Reusar recibo do writer cooperante observado vivo e depois `wait()`/exit, acrescentar correlação de checkout/owner/run/execução e negativos faltante/incorreto/ativo; verificar T1/T3/T4 sem tratar PID ausente ou referência de processo como sessão nativa. Reusar testes de reserva/evidência para conteúdo/índice/ignored/crash/registry e perda local; acrescentar apenas lacunas concretas T2/T6 da matriz e executar os testes focados.
- [ ] 3.3 Atualizar prova de descoberta/invocação nativa para eventos reais vinculados à sessão/path/hash/revisão, sem aceitar read direto/CLI/stub/prosa como invocação; preservar descoberta natural T1 sem nomear `resume-workflow` no prompt inicial. Regressões offline devem rejeitar prova ausente/de outra sessão/SHA e manter guard de argv/PATH/shim (T1/T5/T7/D1).
- [ ] 3.4 Migrar `T7ReinventoryTest` às fontes atuais e manter `T7VisibleQuestionTest`: fase 1 pergunta neutra visível, nenhum acesso nativo/takeover/dispatch/escrita tentado; fase 2 escolha explícita e probes separados sobre ambos candidatos antes de native no mesmo ID. Provar negativos failed/cancelled, read/grep/rg de arquivo/diretório, cadeia mascaradora, writer não comprovado e sessão errada; verificar snapshots de cada fase (T7).
- [ ] 3.5 Fazer o smoke resolver contrato ativo ou archive único por commit/path/hash e preparar fixture válida sem confundir SHAs da candidata/proposta/fixture; provar casos ativo/arquivado/ausente/ambíguo offline. Atualizar documentação operacional residual e limites de recuperação, mantendo README pt/en em paridade e fatos históricos UNKNOWN, sem publicar logs sensíveis (F1/T6).
- [ ] 3.6 Portar assert de atualização pública da skill aos testes atuais do instalador, sem mudar instalador/launchers/pins; provar bytes/manifesto/symlink/AGENTS preservados em instalação e atualização pública OpenCode e executar regressões existentes de seleção Codex-only/ambos, sem exigir runtime cruzado (D1).

## 4. Verificação integrada anterior ao archive

- [ ] 4.1 Conferir discovery/imports e ferramentas reais/versões/paths, HOME/XDG/CODEX_HOME/DB/credenciais isolados, child lifecycle e checkout efetivo; executar primeiro amostra `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_resume_reinventory.py`, depois grupos de reserva/evidência/instalador/launcher/distribuição afetados. Registrar recibos e baseline equivalente no alvo quando houver falha, sem restaurar suite de execution-state retirada (matriz completa).
- [ ] 4.2 Antes de repetir qualquer obrigação model-backed, reconciliar falhas históricas disponíveis e detalhes UNKNOWN, registrar diagnóstico atual completo com prova independente no handoff/PR existente e conferir `attempt-log` quando aplicável. Não inventar seq/diagnóstico/resultado faltante nem resolver falha por nova identificação de episódio; classificar bloqueio/recurso factual e manter guards da política.
- [ ] 4.3 Com preflight/diagnóstico válidos e revisão aplicável, executar uma observação model-backed isolada T1/T5/T7 em HEAD limpo, T7 em dois turnos do mesmo ID; registrar exit/terminal/events/snapshots/skills/hashes/SHAs/provas nativas e revisar eventos independentemente. Falha, 429, timeout ou prova ausente mantém pendência, sem retry automático nem aprovação de texto/arquivo existente.
- [ ] 4.4 Descobrir/invocar Verify oficial disponível após integração, tratar findings conforme severidade e validar o change por `openspec validate issue-61-opencode-safe-resume --strict --no-interactive --json`; registrar capacidade/falha exata se não for possível, sem simular Verify nem dispensar testes/revisão.

## Workflow follow-up

- Invocar Archive nativo na branch existente após as obrigações pré-archive; sincronizar e revisar deltas/main specs sem perder cenários atuais de distribuição/Codex ou reintroduzir telemetria. Executar strict global e inspecionar arquivo/paths do archive.
- Concluir changelog/docs/distribuição/referências e commits finais antes dos gates exatos. Executar/registrar/verificar a suíte local obrigatória `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` no HEAD final limpo; guardar `evidence_id` fora do commit. Qualquer commit posterior exige nova suíte final.
- Comprovar smoke T1/T5/T7 na mesma revisão final após archive; resultado pré-archive é histórico se HEAD mudou. O harness deve funcionar com contrato arquivado; guardar relatório/exit/events em prova acessível/bundle, não somente `/tmp`.
- Preparar/reusar uma única PR residual de #61 com archive/sync, matriz e provas; conferir checks/política GitHub efetivos e obter revisão independente no HEAD/base/contexto finais, inclusive eventos do smoke. Não criar comentários operacionais.
- **DO NOT MERGE / HELD** até autorização explícita posterior: modo original desconhecido. Reter checkout/branch, nove bytecodes sem proveniência e todos os commits. Nenhum passo desta lista autoriza #78, outro trabalho, atualização global ou limpeza.
