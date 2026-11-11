# Tasks

## 1. Atualização íntegra do pacote global

- [ ] 1.1 Estender `scripts/install-global` sem criar outro gerenciador: preservar `--agent opencode --revision <SHA>`, verificar instalação antiga/manifesto e novo snapshot sob lock e trocar `active` somente após preparação; comprovar em `tests/test_global_install.py` duas revisões em HOME isolado com skill nova, referência e helper alterados e dois repositórios consumidores.
- [ ] 1.2 Inventariar skills globais legadas de `skills.sh` no diretório global OpenCode, confrontando metadados de origem/revisão, baseline confiável e bytes atuais com o pacote; tratar colisões, vínculos de propriedade demonstrada, personalizações e migração apenas de entradas/caminhos autorizados, sem sobrescrever outras origens. Comprovar conflito bloqueado e caminho de migração relatado, entrada customizada/não comprovada preservada, skill sem colisão intocada, e pointer/AGENTS/links anteriores funcionais em `tests/test_global_install.py`.
- [ ] 1.3 Exercitar falhas nos pontos `skills`/`guidance` e publicação, versão antiga adulterada e rollback de vínculos/AGENTS sob lock; comprovar revisão anterior funcional e bytes desconhecidos preservados nos fixtures existentes `test_reject_conflicts_and_rollback_before_pointer_switch`, `test_failure_after_skills_leaves_previous_snapshot` e `test_fake_active_manifest_and_extra_tree_rejected`.
- [ ] 1.4 Distinguir primeira instalação, `updated`, `already current`, `blocked` e `partial`, imprimindo SHA anterior/pretendido/ativo real, agentes e pendências sem segredos; comprovar saída e idempotência com testes de `tests/test_global_install.py`, incluindo repetição sem diferença e falha antes do switch.
- [ ] 1.5 Manter bootstrap por revisão Git aprovada, digest independente e snapshot vinculado ao SHA; testar entrada adulterada, SHA divergente e fonte não confiável em `tests/test_global_install.py` sem executar payload adulterado.

## 2. Migração e roteamento limitados ao projeto

- [ ] 2.1 Diagnosticar só o projeto explicitamente identificado para sombras em `.opencode/skills/` e cópias `.ai-workflow/`, **sem escrita por padrão** mesmo se iguais ao baseline; condicionar reconciliação a opt-in separado da raiz e caminhos enumerados, comprovando baseline e revalidando bytes antes de escrever, preservando regras locais. Testar pedido natural com cópia limpa intocada, opt-in de caminhos delimitados, cópia editada/sem baseline, clone legado e outro repo intocado em `tests/test_global_install.py`.
- [ ] 2.2 Adaptar `skills/update-ai-workflow/SKILL.md` para rotear pedido natural ao mesmo instalador autenticado e separar instalação global da local/parcial; exigir opt-in específico antes de editar repositório, pedido expresso de revisão, Web sem execução e nenhuma atualização automática. Verificar com inspeção da skill e cenário T5 documentado no teste/fixture de roteamento, sem invocar `npx skills update` ou modificar projeto sem opt-in.
- [ ] 2.3 Atualizar README PT-BR/EN em paridade com o **comando efetivo** (bootstrap por SHA de entrada/digest literal verificados após código final), revisão-alvo completa, limite de projetos fechados, migração legada, pendências e estados; conferir ambos contra CLI real e executar a receita em HOME descartável, não no HOME do operador.

## 3. Integração e revisão final

- [ ] 3.1 Executar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_global_install` como feedback focado após cada grupo e `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` no candidato final; confirmar dependências reais disponíveis e fixture HOME/Git isolados antes de rodar. Evidência de execução fica no handoff, não em artefato de produção.
- [ ] 3.2 Com OpenCode V2/OpenSpec reais disponíveis, executar `python3 tests/smoke_global_opencode.py` em HOME descartável para dois projetos e worktree; registrar quando indisponível em vez de alegar execução. Verificar `openspec validate update-global-workflow-package --strict` e revisar cada cenário da spec contra implementação/testes.

## Test matrix

| ID | Cenário/risco concreto | Fronteira e fixture | Prova planejada |
|---|---|---|---|
| T1 | Revisão A→B com skill nova, referência e helper modificados, dois consumidores | `install-global` + `active` + symlink global; `GlobalInstallTests.setUp` em HOME/Git descartáveis | Expandir `test_install_complete_idempotent_and_preserves_instructions` e smoke real (se disponível) |
| T2 | Mesmo SHA repetido e instruções preservadas | `active/manifest.json` e `AGENTS.md` gerenciado | Expandir idempotência existente; assert SHA anterior/novo e `already current` |
| T3 | Falha/aborto antes de ativação, vínculos removidos/adicionados, customização e origem antiga adulterada | lock e rollback; `MY_AI_SKILLS_FAIL_AT`, fixtures existentes | Expandir `test_reject_conflicts_and_rollback_before_pointer_switch`, `test_failure_after_skills_leaves_previous_snapshot`, `test_fake_active_manifest_and_extra_tree_rejected` |
| T4 | Cópia local personalizada sombreia global; cópia limpa sem opt-in; opt-in de projeto/caminhos; outro repo não tocado | projeto identificado, fixture com `.opencode/skills` e `.ai-workflow` | Novos casos isolados em `test_global_install.py` verificam diagnóstico read-only por padrão, escrita apenas nos caminhos autorizados com baseline, regras preservadas e pendência honesta |
| T5 | Só pedido de atualizar ativa skill global; pedido comum e Web não escrevem; pedido natural não autoriza edição local | contrato de `update-ai-workflow`, README PT/EN | Revisão dirigida da skill + fixture de roteamento/documentação; nenhum gatilho em startup nem mutação local implícita |
| T6 | Bootstrap alterado não executa payload, versão Git incorreta não ativa | entrada SHA-256 literal independente + snapshot SHA | `test_public_download_digest_checked_before_execution`, `test_revision_and_agent_and_missing_requirement` expandidos |
| T7 | Skill global legada `skills.sh`: mesma origem sem edição, editada, origem desconhecida, outra origem e sem colisão | `${XDG_CONFIG_HOME}/opencode/skills`, metadados do gerenciador e snapshot Git oficial em HOME isolado | Novos casos em `test_global_install.py` validam comparação de baseline/conteúdo, bloqueio sem overwrite, pendência e caminho de migração com opt-in, e preservação de entradas sem colisão |

Os testes usam fontes Git e HOME do `setUp`; não devem depender de rede, mutar HOME real ou remover worktrees existentes. Consumidores externos afetados: `README.md`/`README.en.md` ensinam bootstrap, `skills/update-ai-workflow/SKILL.md` roteia intenção, `.config/opencode/skills` descobre symlinks gerenciados e pode conter skills `skills.sh` legadas; `tests/smoke_global_opencode.py` assume SHA fixo da entrada e precisa ser alinhado à revisão efetivamente publicada. Rodar amostra focada T1/T3/T4/T7 antes da suite ampla. A política lida no plano é `skills/implement-issue/references/TEST_STRATEGY.md` e `skills/implement-issue/references/WORKTREES.md` no commit `a722f4c4894e62ba50ff9dd0921d7f03d87664d0`; reavaliar diferenças antes de Apply.

## Workflow follow-up

- Após implementação em sessão nova, verificar os cenários e a validação strict na revisão real; arquivar/sincronizar specs no mesmo branch antes do PR conforme `openspec-workflow`, sem abrir trabalho dependente antes da revisão do plano.
