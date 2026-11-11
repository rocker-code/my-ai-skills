# Tasks

## 1. Separar referências da distribuição pessoal

- [ ] 1.1 Extrair mapa e geração de referências de `scripts/sync-plugin` para `scripts/sync-skill-references`, sem pré-condição de plugin; verificar conteúdo de protocolos/modelos e falha explícita para fonte ausente com teste focado em `tests/test_instrumentation_distribution.py` (T1/T2).
- [ ] 1.2 Converter testes do espelho para geração em checkout temporário sem plugin e execução repetida sem diferenças; verificar `python3 -m unittest discover -s tests -p 'test_instrumentation_distribution.py'` (T1/T2).

## 2. Retirar artefatos exclusivos com preservação das fontes

- [ ] 2.1 Confirmar ownership com `git ls-files`/busca de consumidores, remover somente `plugins/my-ai-skills/`, `.agents/plugins/marketplace.json` e `scripts/sync-plugin`; verificar `git diff --name-status`, ausência desses caminhos e preservação de `skills/`, `protocol/`, `templates/`, `scripts/` oficiais e `.agents/skills/` (T4).
- [ ] 2.2 Adaptar `tests/test_preflight_procedure.py` à paridade fonte/referência e `tests/test_worktree_reservation.py` à seleção explícita de helpers Python oficiais, sem enfraquecer ausência de bytecode; verificar os dois testes focados e referências Web/modelo/protocolo (T3/T5).

## 3. Reconciliar documentação e integração com #50

- [ ] 3.1 Antes de editar arquivos compartilhados, comparar HEAD da #50 com base e branch desta issue, reconciliar `README.md`, `README.en.md` e `skills/update-ai-workflow/SKILL.md` sem sobrescrever instalação global da #50 nem antecipar #51; verificar paridade bilíngue e busca de comandos plugin/marketplace em documentação ativa (T4).
- [ ] 3.2 Atualizar `openspec/config.yaml` para indicar manutenção de referências sem plugin e documentar descontinuação sem desinstalar máquinas; verificar ausência de dependência ativa do scaffold e conteúdo Codex/Web preservado (T3/T4).

## 4. Verificação integrada

- [ ] 4.1 Executar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` e `openspec validate remove-personal-plugin --strict --no-interactive`, registrar resultados exatos, buscar referências obsoletas apenas em fontes ativas e revisar `git diff --check` e paths removidos (T1–T5).

## Workflow follow-up

- Após testes e revisão, arquivar/sincronizar o delta na branch da issue e reconciliar a menção textual obsoleta do script em `openspec/specs/checkout-write-reservation/spec.md` sem alterar o contrato de bytecode; não reescrever histórico arquivado.
- Na PR, confirmar novamente a convivência com #50 e repassar à #51 a interface efetiva da distribuição; comentários de instrumentação cabem apenas ao coordenador.
