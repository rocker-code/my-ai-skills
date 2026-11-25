# Changelog

## Não lançado

### Corrigido

- Prova residual de retomada OpenCode usa fontes Git/GitHub/OpenSpec read-only, recibo terminal correlacionado e eventos reais da ferramenta de skill nativa; rejeita leitura/prosa como invocação, mantém T7 em dois turnos da mesma sessão e resolve contrato ativo ou arquivado sem restaurar telemetria. [#61](https://github.com/rocker-code/my-ai-skills/issues/61)

- Inspeção Codex interpreta TOML completo com Tomli 2.5.0 incorporado e licenciado em Python 3.10+, sem pacote ambiente ou download extra. Regras canônicas desabilitadas são reconhecidas independentemente da grafia; configuração inválida bloqueia sem expor valores nem alterar config/auth ou a instalação anterior. Novo par imutável instalador/launcher cobre todos os bytes da dependência. [#77](https://github.com/rocker-code/my-ai-skills/issues/77)

### Adicionado

- Integração global nativa Codex CLI e coexistência com OpenCode usando a mesma fonte canônica, links/paths próprios, ownership verificável e atualização transacional; instalação inicial exige `--agent` explícito e atualizações preservam ou ampliam a seleção. Smokes isolados distinguem execução nativa de backend GitHub fixture, sem restaurar plugin pessoal ou comentários operacionais. [#77](https://github.com/rocker-code/my-ai-skills/issues/77)

- Comando global `worktree-reservation` com detecção segura da raiz do checkout mesmo sob variáveis Git herdadas, resumo operacional com recibos de execução e `--json` para automação; a instalação protege comandos existentes, preserva caminhos com metacaracteres e acompanha a versão ativa pelo instalador público verificado. [#69](https://github.com/rocker-code/my-ai-skills/issues/69)

- Retomada segura de issues e milestones em uma nova sessão OpenCode com `resume-workflow`, reconhecimento de solicitações naturais de continuação e reconciliação dos checkpoints existentes antes de qualquer escrita.

- Geração e atualização de changelogs com a skill `update-changelog`, incluindo criação do arquivo quando ausente e preservação do histórico.

### Alterado

- Removidos os comandos de métricas/eventos do workflow e suas dependências; progresso e retomada usam fontes existentes sem analytics ou comentários operacionais. Histórico e provas de testes/posse preservados. [#76](https://github.com/rocker-code/my-ai-skills/issues/76)

- Ciclo nativo OpenSpec com Verify, simplify opcional e revisão reutilizável por HEAD; retirados gates duplicados, comentários operacionais e Kaizen obrigatório. [#75](https://github.com/rocker-code/my-ai-skills/issues/75)

- O workflow mantém os sandboxes M2T de integração e GraphQL vinculados à worktree entre planejamento, Apply e revisão; no encerramento após entrega e kaizen, limpa apenas seleções comprovadamente próprias antes de remover o checkout, preservando caches compartilhados e recursos de outros trabalhos. [#70](https://github.com/rocker-code/my-ai-skills/issues/70)

- A preparação de PR registra mudanças relevantes em Não lançado; a preparação de release consolida apenas as entradas incluídas na versão antes da validação final.

- A integração OpenSpec usa as skills nativas da versão 2.0 em vez de exigir comandos `/opsx-*` legados. Projetos existentes precisam de inventário e autorização específica antes da migração dos arquivos gerados; a instalação global não inicializa nem atualiza projetos automaticamente. [#71](https://github.com/rocker-code/my-ai-skills/issues/71)
