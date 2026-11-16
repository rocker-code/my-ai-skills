# Tasks

## 1. Inventário seguro do perfil e migração

- [x] 1.1 Em sessão Apply fresca, verificar reserva e SHA; inventariar paths gerados rastreados, symlinks, metadados de origem, resíduos locais/globais e ferramentas configuradas; comparar geração oficial 2.0 em HOME/repo descartáveis e `update --dry-run --json`; verificar relatório de diferenças e aprovação específica antes de qualquer limpeza.
- [x] 1.2 Migrar somente paths comprovadamente gerados e autorizados; preservar customizações, união de ferramentas e versão anterior em conflito/falha; verificar `git diff --name-status`, links, config/specs/changes antes/depois e dry-run final sem diferenças inesperadas.

## 2. Distribuição e orientação de primeiro uso

- [x] 2.1 Adaptar `scripts/install-global`/bloco global `AGENTS.md` para skills 2.0 e gates de autorização, sem `init/update` local na instalação; estender `tests/test_global_install.py` para HOME isolado, idempotência, colisão/rollback e preservação; verificar testes focados do instalador.
- [x] 2.2 Atualizar `protocol/AI_WORKFLOW.md`, `skills/openspec-workflow/SKILL.md` e consumidores de `/opsx-*` em skills de planejamento/Apply/closeout para interface oficial 2.0 sem remover gates; atualizar `README.md` e `README.en.md` em paridade; verificar busca de referências obsoletas e testes/documentação afetados.
- [x] 2.3 Adaptar fixtures de primeiro uso novo/existente e perfil multi-tool, incluindo arquivos customizados e resíduos, em `tests/test_global_install.py`; verificar provas focadas de preservação e bloqueio sem forçar/bootstrap implícito.

## 3. Prova de sessão nova e integração final

- [x] 3.1 Adaptar `tests/smoke_global_opencode.py` para perfis 2.0 e invocação observável de quatro skills nativas em sessão OpenCode nova para dois projetos e worktree com espaços; verificar smoke em HOME descartável e resultado persistido, inclusive ausência/falha de skill sem falso sucesso.
- [x] 3.2 Executar sample focado do instalador/smoke antes da suíte local exigida `python3 -m unittest discover -s tests`; verificar resultados no SHA candidato sem tratar falha de baseline como aprovação, e executar `openspec validate issue-71-openspec2-native --strict --json` no SHA efetivo.

## Workflow follow-up

- Depois de Apply/testes e revisão, arquivar/sincronizar o delta pela interface oficial na mesma branch, inspecionar spec viva e artefatos arquivados no PR; repetir gates exigidos no commit final.
- Após entrega de #71, revalidar as propostas #61/#69, suas provas e SHA exato antes de retomar Apply; tratar `E_RETRY_LIMIT` histórico de #69 e M2T #46 separadamente.
