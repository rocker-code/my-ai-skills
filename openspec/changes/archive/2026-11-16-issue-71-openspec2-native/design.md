# Design

## Context

Ver `proposal.md` e o delta de `global-workflow-distribution`. O checkout isolado em `fd46eb01` ainda rastreia cinco comandos em `.opencode/commands/opsx-*`, cinco em `.claude/commands/opsx/`, cópias de skills em `.opencode/skills/` e `.claude/skills/`, além da origem compartilhada em `.agents/skills/`. A árvore primária após `openspec update` 2.0 contém `.agents/skills/openspec-update-change`, remove comandos/cópias OpenCode e usa links Claude; é referência para inventário, **não** prova de migração aprovada. `openspec context/list` encontra raiz local, e o `new change` oficial cria metadados. `scripts/install-global` escreve orientação global exigindo os arquivos legados, enquanto testes e smoke reproduzem a exigência. O gerador 2.0 pode mudar: evidência do perfil instalado prevalece sobre nomes inferidos da versão.

## Goals / Non-Goals

**Goals:** alinhar contrato, arquivos distribuídos e verificação ao perfil nativo; preservar fronteiras de autorização e publicação atômica, distinguir skill do pacote global de skill local OpenSpec; bloquear quando prova real falhar.

**Non-Goals:** executar update no checkout de planejamento ou no HOME real; inventar comandos ou adaptar #61/#69 além de exigir posterior revalidação no SHA exato; reescrever histórico arquivado.

## Decisions

1. **Descoberta baseada em skills nativas, não em comandos.** Roteamento por `openspec-explore`, `openspec-propose`, `openspec-apply-change`, `openspec-archive-change` gerados pelo perfil atual (e outros exigidos pelo perfil), junto com `openspec context/list/status/instructions/validate --strict` oficiais. A invocação da skill no OpenCode é o gate; listar arquivos sozinho ou criar sessão via API sem mensagem de invocação não comprova nada. Alternativa de manter aliases `/opsx-*` recusada pela decisão #61/#69.
2. **Migração explícita de arquivos gerados.** No Apply, comparar índice Git, conteúdos e symlinks contra geração oficial 2.0 em cópia descartável e dry-run, registrar propriedade e customização de cada caminho; somente o conjunto comprovadamente gerado, não modificado e autorizado pode ser versionado como remoção/alteração. Verificar `.agents/skills/.openspec-target` e união real de `claude`, `codex`, `opencode`; preservar arquivo desconhecido/alterado e abortar conflito antes de publicar. Não executar `update` neste worktree sem nova autorização específica de migração; autorização de update da árvore primária não aprova limpeza indistinta aqui. Alternativa de copiar todo `git diff` da árvore primária rejeitada por confundir estado sujo com entrega.
3. **Primeiro uso separado de instalação global.** `install-global` só prepara pacote e CLI, gera instrução que exige inspeção de raiz, resíduos locais e prompts globais e autorização específica; não executa `init/update` local. Em projeto novo autorizado, confirmar opções CLI 2.0, multi-tool e conflitos antes de `init`; em projeto existente completo reutilizar; incompleto examinar `update --dry-run --json`, config/specs/changes e efeitos globais antes de escrita. Sem preservação demonstrada, bloquear, nunca `--force`.
4. **Prova descartável end-to-end.** Reusar `tests/test_global_install.py` (HOME temporário e fixtures) e `tests/smoke_global_opencode.py` (OpenCode V2 real) para projetos novo/existente e worktree com espaços. Usar endpoints de skill do servidor OpenCode e sessão recém-criada por localização, confirmar `location`, ID/path da skill e mensagem efetiva de invocação; não exigir expansão de comando. Não autenticar modelo nem alegar execução de Apply de produção. Preservar resultado/diagnóstico em `results.json` fora do HOME do operador; falha de API ou skill ausente é bloqueio, não skip silencioso.

## Risks / Trade-offs

- [CLI 2.0 altera geração/metadata do perfil] → confirmar `--version`, perfil real e dry-run em sandbox antes de decidir caminhos gerados; teste falha fechado se não houver prova.
- [Delete de arquivo legado customizado ou link quebrado] → confrontar origem por caminho, inventário de conteúdo e diff; exigir aprovação específica, preservar versão anterior em falha/conflito.
- [Smoke assíncrono ou API OpenCode muda] → aguardar descoberta com limite, checar escopo exato e mensagem da invocação; indisponibilidade marcada NOT RUN/BLOCKED, nunca sucesso inferido.
- [Mudança compartilhada cruza testes/README/instruções] → pesquisar consumidores fora do instalador (`protocol/AI_WORKFLOW.md`, `skills/issue-explore`, `skills/issue-ready`, `skills/implement-issue`, `skills/apply-issue`, `skills/openspec-workflow`, README, fixtures), preservar gates e executar teste focado antes da suíte obrigatória.

## Migration Plan

1. No Apply fresco, verificar reserva, revisão e política vigente; inventariar arquivos gerados rastreados, instruções globais e resíduos, comparar perfil 2.0 descartável e dry-run; registrar diffs e aprovação por alvo, sem assumir que update da árvore primária autoriza este checkout.
2. Ajustar orientação e teste em HOME isolado antes da migração versionada; migrar somente arquivos de origem demonstrada, preservando conteúdo customizado e união de ferramentas. Confirmar `openspec update --dry-run --json` final sem diferenças não avaliadas; inspecionar config/specs/changes antes e depois.
3. Provar instalação/primeiro uso e nova sessão OpenCode no sandbox; rodar regressões focadas, suíte exigida e `openspec validate issue-71-openspec2-native --strict --json`. Arquivar/sincronizar delta na mesma branch apenas depois de Apply e gates, inspecionar spec viva e arquivada no mesmo PR.
4. Em falha, não publicar instalação parcial nem limpar desconhecidos; conservar a versão global anterior e o commit/arquivos preexistentes, documentando rollback seletivo autorizado e próxima ação. #61/#69 revalidam seus próprios contratos e testes no novo SHA antes de Apply.
