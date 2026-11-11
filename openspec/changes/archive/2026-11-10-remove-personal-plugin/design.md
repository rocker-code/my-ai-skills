# Design

## Context

Em `f8fa6ac3`, `scripts/sync-plugin` primeiro copia protocolos/modelos para `skills/*/references/`, depois apaga e recopia `skills/`, `protocol/`, `templates/` e helpers para `plugins/my-ai-skills/`; sua pré-condição exige `.codex-plugin/plugin.json`. `.agents/plugins/marketplace.json` aponta só para esse pacote. `skills.sh` instala cada skill isoladamente, daí as referências são necessárias mesmo sem plugin. `tests/test_instrumentation_distribution.py` testa apenas o espelho do pacote; `tests/test_preflight_procedure.py` e `tests/test_worktree_reservation.py` também têm dependências explícitas dele. README PT-BR/EN e `update-ai-workflow` anunciam o plugin; `openspec/config.yaml` e um spec vivo citam o script antigo. Nenhuma outra distribuição ativa de plugin foi encontrada na busca do checkout (excluídos o próprio espelho e histórico arquivado).

## Goals / Non-Goals

**Goals:** preservar igualdade byte a byte das referências pertinentes com suas fontes e a função dos helpers oficiais, sem scaffold do plugin. Manter instruções PT-BR/EN equivalentes e testes de regressão proporcionais.

**Non-Goals:** remover integrações Codex/OpenCode, skills `chatgpt-web-*`, protocolos Web, histórico arquivado; desinstalar plugins pessoais remotos; antecipar a assinatura do instalador global da #50 ou o atualizador da #51.

## Decisions

1. Extrair apenas o trecho `bundle_reference` e suas chamadas de `sync-plugin` para `scripts/sync-skill-references` (nome proposto), preservando o mapa explícito de origem/destino, modo 0644, erro em fonte faltante e independência de `plugins/`. Remover o script antigo, sem criar novo gerenciador de pacotes. Alternativa descartada: manter `sync-plugin` como nome com comportamento diferente — conserva comando enganoso e testes que inferem uma distribuição extinta.
2. Apagar apenas `.agents/plugins/marketplace.json` e `plugins/my-ai-skills/` após confirmar no diff que são o catálogo e o espelho exclusivamente gerado; preservar `.agents/skills/`, `.claude/`, `.opencode/`, `skills/`, `protocol/`, `templates/` e `scripts/` oficiais. Alternativa descartada: apagar `.agents/` inteira — inclui descoberta de skills OpenSpec independente do catálogo.
3. Substituir no teste de distribuição o fixture que copiava manifesto e comparava `PLUGIN` por geração duas vezes em checkout temporário **sem plugin**, igualdade das referências mapeadas e ausência de diferenças na segunda execução; acrescentar caso de erro quando fonte obrigatória faltar. Ajustar `test_preflight_procedure.py` para comparar fontes e referências oficiais, preservando todas as asserções de paridade úteis. Em `test_worktree_reservation.py`, substituir introspecção da lista de helpers dentro de `sync-plugin` por inventário explícito dos executáveis Python oficiais exercitados, mantendo a garantia de ausência de bytecode; não silenciar nem reduzir esse teste.
4. Em Apply, reconciliar README PT-BR/EN e `skills/update-ai-workflow/SKILL.md` com o HEAD resultante de #50 antes de editar: remover somente instruções plugin/marketplace e atualizar o nome da ferramenta, sem sobrescrever o instalador global novo. #51 deverá partir do resultado reconciliado; #52 não depende da entrega da #50 para seu código, mas colisões textuais exigem integração cuidadosa. Atualizar `openspec/config.yaml` para não impor plugin inexistente. A menção em `openspec/specs/checkout-write-reservation/spec.md` é histórico de ferramenta no requisito vigente: durante sync/archive, reconciliar a redação do spec vivo com o novo nome sem mudar sua obrigação comportamental; não reescrever spec arquivado.

## Risks / Trade-offs

- [Cópia de referências incompleta] → comparar mapa/bytes com o script atual e testar referência de protocolo, modelo e Web antes e depois; não eliminar as referências embarcadas.
- [README/skill divergentes das mudanças de #50] → comparação de três vias base/HEAD da #50/#52, edição de linhas pertinentes e revisão bilíngue antes de PR; não usar checkout forçado nem sobrescrever versão nova.
- [Teste do espelho removido escondia regressão nos helpers] → preservar testes individuais de helpers e converter apenas as provas de distribuição em provas de referências e da ausência de bytecode; executar suíte completa.
- [Plugin pessoal já instalado em máquinas] → explicar descontinuação e migração para as skills oficiais; sem tocar em máquinas, caches ou credenciais.

## Migration Plan

Uma única mudança de repositório remove a distribuição gerada e publica nova ferramenta de referências; o instalador normal continua usando `skills/`. Não há migração de dados ou operação remota. Se a PR ainda não foi mesclada, revertê-la pelo fluxo normal da PR, sem editar instalações de terceiros. Ao arquivar, sincronizar o novo spec e reconciliar a referência textual obsoleta no spec vivo.

## Evidence matrix

| Cenário | Critério/risco | Camada e consumidor/fixture | Prova planejada |
|---|---|---|---|
| T1 Gerar sem scaffold, repetir | referências completas e idempotência; fixture anterior exigia `.codex-plugin` | teste isolado de cópia `tests/test_instrumentation_distribution.py`; `skills/*/references/` | executar gerador duas vezes em checkout temporário sem `plugins/`, conferir hashes/bytes e ausência de diff na segunda; teste focado |
| T2 Fonte ausente | erro explícito, não falso sucesso | mesmo teste temporário, fonte `protocol/` removida | caso de falha com exit não-zero e mensagem útil |
| T3 Protocolo/modelo/Web embarcados | não quebrar `skills.sh` nem Codex/Web | `tests/test_preflight_procedure.py`, `skills/chatgpt-web-*/references/`, `skills/contract-handoff/references/` | igualdade byte a byte das referências oficiais; inspeção da descoberta `.agents/skills`, `.opencode/`, `.claude/` |
| T4 Remoção de distribuição ativa | sem manifesto/catálogo/comando obsoleto | inspeção estática de README, skill, config, scripts; histórico excluído | busca grep/find em fontes ativas + verificação de ausências dos dois caminhos exclusivos |
| T5 Helpers sem bytecode | prova antes ligada à lista `sync-plugin` não pode desaparecer | `tests/test_worktree_reservation.py::test_helpers_do_not_write_bytecode`, executáveis Python em `scripts/` | rodar teste focado preservando asserção; `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` após demais alterações |

Ambiente: Python 3 stdlib, Bash, `openspec`; fixture de `tempfile.TemporaryDirectory` pertence ao teste e remove somente seus próprios arquivos; nenhum serviço externo nem banco. Primeiro executar amostra focada dos três módulos afetados, depois suíte completa; `openspec validate remove-personal-plugin --strict --no-interactive` após atualização da proposta e novamente no Apply. Política lida na base: `protocol/TEST_STRATEGY.md` e `protocol/WORKTREES.md` em `f8fa6ac3`; reconferir no HEAD do Apply. Esta matriz é plano, não evidência de testes executados.
