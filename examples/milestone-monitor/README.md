# AI Engineering Workflow — Terminal Demo

Demo visual em **Python 3 + curses**, usando somente a biblioteca padrão do Python. Nenhuma alteração no GitHub, OpenCode ou my-ai-skills.

## Executar

```bash
python3 dashboard.py
```

Se estiver executando no tmux, redimensione o painel para **100+ colunas** para ver os nomes completos de todas as etapas. Recomendado: 110 × 30 ou maior. Cores dependem do terminal.

## Teclas

| Tecla | Ação |
|---|---|
| `↑` / `↓` ou `j` / `k` | Navegar milestones/issues |
| `Enter` ou `Espaço` | Expandir/recolher milestone ou detalhes da issue |
| `a` | Expandir todos |
| `c` | Recolher todos |
| `f` | Alternar filtros: todas/executando/pendente/bloqueada/concluída |
| `q` / `Esc` | Sair |

## Notas

- Dados e progresso **fictícios**, para validar o conceito visual.
- Progressão da régua: `Explore → Proposal → Apply → Tests → PR → Review → Merge → Archive`.
- Percentual do milestone calculado por **issues concluídas / total de issues**, não por percentuais estimados das etapas.
- Há contagem separada para issues bloqueadas; elas não aparecem como executando.
- A demo não tem integração com API do GitHub/OpenCode nem atualização de dados em tempo real.

## Continuidade

Veja a [issue #43](https://github.com/rocker-code/my-ai-skills/issues/43) para o escopo aprovado da TUI operacional, fonte de eventos, integração OpenCode/GitHub, persistência e melhorias de layout. Reutilize os contratos de telemetria da [issue #16](https://github.com/rocker-code/my-ai-skills/issues/16) em vez de criar um sistema de métricas concorrente.

Esta pasta é uma **demo isolada** e não altera os comandos ou skills já instalados.
