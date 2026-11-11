# Tasks

## 1. Entrada pública, pré-flight e pacote

- [ ] 1.1 Criar `scripts/install-global` com interface `--agent` explícita, validação de plataforma/ferramentas/versão, instalação suportada de OpenSpec ausente e falhas acionáveis; provar seleção válida/inválida, dependência ausente e não atualização de runtime com novos casos em `tests/test_global_install.py`.
- [ ] 1.2 Obter snapshot em revisão Git exata, montar skills/references/protocol/templates/scripts e módulos acompanhantes e manifesto com origem, SHA, agentes, modos e hashes; conferir por teste focado que nada depende de `plugins/my-ai-skills` ou `.ai-workflow/` e que o inventário reproduz os arquivos da revisão.
- [ ] 1.3 Adicionar lock e publicação reversível do pacote/ponteiro ativo, preservação de arquivos desconhecidos e detecção de alterações locais; provar idempotência e injeção de falha antes/durante publicação com HOME/XDG temporário e instalação anterior funcional.

## 2. Descoberta e uso do agente

- [ ] 2.1 Registrar somente skills selecionadas em fonte global documentada do OpenCode e adicionar orientação gerenciada sem substituir `~/.config/opencode/AGENTS.md` preexistente; provar descoberta, precedência local por ID, recusa de colisão e repetição em teste de integração/smoke do agente.
- [ ] 2.2 Adaptar instruções de execução das skills que exigem `.ai-workflow/` e atalhos relativos para caminhos globais, preservando invocação dos helpers originais e módulos vizinhos; verificar em dois repositórios isolados e worktree com espaços que reserva/evidência persistem no Git common dir correto, reutilizando `tests/test_worktree_reservation.py`, `tests/test_workflow_evidence.py` e teste de distribuição.
- [ ] 2.3 Incorporar orientação de primeiro uso de OpenSpec com `context/list` e autorização local quando falta raiz; provar os cenários configurado/não configurado sem executar `init` na instalação global e sem sobrescrever configuração existente.

## 3. Distribuição, documentação e integração coordenada

- [ ] 3.1 Após sincronizar com #52, adotar ferramenta independente de geração de referências sem alterar o plugin removido ou reintroduzir dependência de `scripts/sync-plugin`; validar referências embarcadas idempotentes e reconciliar os testes de `tests/test_instrumentation_distribution.py` com a versão integrada.
- [ ] 3.2 Atualizar `README.md` e `README.en.md` e orientações afetadas com o comando público real, agentes/plataformas comprovados, requisitos, verificação e legado, sem prometer ChatGPT Web automático; testar os comandos publicados em HOME isolado e comparar paridade PT-BR/EN. Esta tarefa fica somente para Apply, não para esta sessão de planejamento.
- [ ] 3.3 Rodar smoke real em HOME/XDG descartável com dois repositórios e worktree, teste focado `python3 -m unittest tests/test_global_install.py tests/test_instrumentation_distribution.py` (ajustar descoberta conforme arquivos efetivos), depois `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`; registrar agente, revisão e resultados por cenário antes de declarar implementação pronta.

## Matriz de cenários e comprovação (planejamento; evidência ainda pendente)

| ID | Requisito/risco | Fronteira/consumidor e hipótese atual | Prova prevista |
|---|---|---|---|
| T1 | Instalação completa em um comando | `README.md:476-665` hoje separa `skills add -g` de complementos | `tests/test_global_install.py`: HOME/XDG temporário + smoke OpenCode real em dois repos |
| T2 | Referências/helpers e espaços | `scripts/worktree-reservation` importa `worktree_registry.py`; `workflow-evidence` importa `workflow_evidence.py` e `worktree_registry.py`; scripts atualizados não podem depender de cwd da fonte | Teste de distribuição novo + casos focados de `tests/test_worktree_reservation.py` e `tests/test_workflow_evidence.py` em worktree com espaços; inspecionar Git common dir |
| T3 | Idempotência/personalização/regras | `tests/test_instrumentation_distribution.py` hoje assume plugin espelhado; `~/.config/opencode/AGENTS.md` pode conter texto alheio; skill local homônima prevalece no OpenCode | teste de instalação repetida e conflitos; comparação byte a byte do texto alheio e smoke de carregamento local/global |
| T4 | Falha atômica/requisitos | Instalação atual não publica snapshot global; risco de ponteiro quebrado/ausência de `gh`, `jq`, OpenSpec ou download | teste com falha injetada por fase e dependência simulada, verificar exit code e instalação anterior intacta |
| T5 | Primeiro uso OpenSpec | README atual manda `openspec init` manual; projeto com `openspec/config.yaml` não pode ser refeito | smoke de skill/instrução em repo novo e repo já configurado, sem efeitos no projeto na fase de instalação |
| T6 | Isolamento entre repos | Specs `checkout-write-reservation`, `test-evidence` e `workflow-execution-state` mantêm estado no Git common dir; não alterar seus contratos | teste em dois repos com identidades diferentes, evidência/registry não cruzados |

Antes de testes de integração, conferir existência de Python 3.10+, `git`, `gh`, `jq`, OpenSpec, CLI OpenCode, versão do agente, HOME/XDG temporário, Git author local e diretórios descartáveis; `tests/` usa `tempfile.TemporaryDirectory` e cópia/sandbox, sem banco nem serviço de app. Não executar ações remotas autenticadas nem comentar issues para testar instalador; testes de CI/broad suite só depois de focused sample. Política lida em `skills/implement-issue/references/TEST_STRATEGY.md` e `protocol/WORKTREES.md` na base `f8fa6ac3eae56544487a7f5e51c74cde8829fa85`; na sessão Apply comparar as versões e reconciliar divergências. Nenhum teste de implementação foi executado no planejamento.

## Workflow follow-up

- Após implementação/testes/verificação estrita em sessão nova, arquivar OpenSpec na mesma branch e sincronizar o novo spec durável na mesma PR.
- Coordenar integração de #52 antes de tocar README, `sync-plugin`, catálogo ou testes compartilhados; #51 lê manifesto após merge de #50.
