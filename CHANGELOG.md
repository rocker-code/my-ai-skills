# Changelog

## Não lançado

### Adicionado

- Comando global `worktree-reservation` com detecção da raiz do checkout, resumo operacional nativo e `--json` para automação; a instalação protege comandos existentes e acompanha a versão ativa.

- Retomada segura de issues e milestones em uma nova sessão OpenCode com `resume-workflow`, reconhecimento de solicitações naturais de continuação e reconciliação dos checkpoints existentes antes de qualquer escrita.

- Geração e atualização de changelogs com a skill `update-changelog`, incluindo criação do arquivo quando ausente e preservação do histórico.

### Alterado

- A preparação de PR registra mudanças relevantes em Não lançado; a preparação de release consolida apenas as entradas incluídas na versão antes da validação final.

- A integração OpenSpec usa as skills nativas da versão 2.0 em vez de exigir comandos `/opsx-*` legados. Projetos existentes precisam de inventário e autorização específica antes da migração dos arquivos gerados; a instalação global não inicializa nem atualiza projetos automaticamente. [#71](https://github.com/rocker-code/my-ai-skills/issues/71)
