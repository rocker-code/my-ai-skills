# Proposal

## Why

Na sessão tmux `mobile:1.0`, com 238×54 células e 40 milestones configurados, textos e estados se misturam. O usuário aprovou reformular o plano para ficar o mais próximo possível da imagem fornecida na conversa, incluindo composição, cores, cartões, barras, tabela e acabamento, mantendo a interface no terminal.

## What Changes

- Reproduzir a hierarquia da referência: marca/título e subtítulo, quatro cartões de indicadores, linha de totais/filtros, cartões de milestones e rodapé de atalhos em teclas contornadas.
- Aplicar tema escuro com texto claro, bordas ciano, conclusão verde, execução azul/ciano, pendência cinza e bloqueio âmbar, com fallback ASCII/monocromático.
- Apresentar cada milestone em bloco contornado, com sanfona, título, repositório em sublinha, contadores e barra segmentada de distribuição, mantendo percentual de conclusão GitHub separado de atividade.
- Usar tabela Issue / Workflow / Status / Tempo em largura ampla, com etapas em pílulas e badges de estado; adaptar para linhas empilhadas quando faltar espaço, sem perder a etapa atual.
- Preservar as 13 etapas pt-BR do protocolo e seus estados auditáveis; tempo resumido usa apenas trabalho canônico registrado, sem cronômetro presumido, aprovação ou conclusão implícita.
- Manter contexto de projeto durante a rolagem sem cabeçalhos externos redundantes; preservar ordem do modelo, identidades, filtros e teclas existentes.
- Organizar detalhes em seções e separar saúde das fontes dos dados de progresso, sem mudar a semântica nem fabricar atividade.
- Validar layouts determinísticos e smokes em tmux isolado, sem reiniciar ou enviar teclas ao dashboard do usuário.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `milestone-monitor-tui`: composição visual baseada na referência, indicadores globais, cartões com barras, tabela responsiva, tema semântico e detalhes seccionados.

## Impact

Implementação principal em `scripts/milestone_monitor/tui.py`, testes em `tests/test_milestone_monitor_tui.py` e smokes relacionados. Documentação operacional pt-BR/en e distribuição regenerada com `scripts/sync-plugin`. Sem novas dependências, migração SQLite, alterações de API, eventos, coleta, configuração, TTL ou contratos de projeção. A lentidão da coleta observada anteriormente fica fora desta mudança visual; a demo offline permanece intacta.
