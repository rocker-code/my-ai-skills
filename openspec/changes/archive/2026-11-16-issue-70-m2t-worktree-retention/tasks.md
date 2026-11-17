# Tasks

## 1. Retenção e evidência durante o trabalho

- [x] 1.1 Explicitar em `protocol/WORKTREES.md` o vínculo entre worktree, seleção M2T, handoff existente e revalidação no código atual sem criar registry paralelo; verificar T1–T3 com inspeção da fonte e fixture/teste documental focado.
- [x] 1.2 Alinhar `skills/implement-issue`, `apply-issue` e `resume-workflow` à retenção entre sessões, separação de posse do checkout/lock M2T e leitura de saída resumida/log pertinente; verificar T1–T3 e T7 por teste documental ou simulação de handoff sem rodar Docker.

## 2. Closeout seguro e escopos reais

- [x] 2.1 Estender `protocol/WORKTREES.md` com gate de merge/kaizen/dono/liveness/evidência, ordem M2T antes de remoção Git, comandos públicos com path e escopos/tokens próprios, retenção em erro e cache/instâncias alheias intactos; verificar T4–T6 em fixtures de elegibilidade, falha/lock 73 e múltiplas seleções.
- [x] 2.2 Conciliar `skills/milestone-orchestrator`, `github-resolution`, `prepare-pr` e `post-pr-audit` apenas onde aplicável ao closeout existente, sem mudar política de merge; verificar T3–T6 em inspeção de rotas e testes/fixtures focados, com resultado compacto por seleção removida/retida.

## 3. Distribuição e prova cruzada

- [x] 3.1 Rodar `scripts/sync-skill-references`, inspecionar diff das referências geradas e atualizar README pt-BR/en apenas se documentarem o fluxo tocado; verificar sincronização e que não há obrigação de `down`/`reset` por comando nas instruções do pacote, nem comando OpenSpec 1.x fabricado.
- [x] 3.2 Registrar no handoff da entrega o contrato efetivo para adoção posterior em Rancho #457, sem editar repos externos; verificar mapeamento T1–T7 para os merges M2T `04f0272` e my-ai-skills `02194d7`, inclusive ausência de path de log obrigatório em sucesso de test/graphql.
- [x] 3.3 Executar testes focados existentes/ajustados da documentação/distribuição e `openspec validate issue-70-m2t-worktree-retention --strict --json`; verificar que T1–T7 estão cobertos sem model smoke, Docker, alteração de M2T ou bug separado `workflow-report`/`gh`.

## Handoff de contrato ao consumidor Rancho #457

- Base do consumidor: my-ai-skills `02194d7aaa343a481e5bff47ababfc3c669fedc1` (reserva global e `WORKTREES`). Produtor: M2T `04f027277e127890beb4058817b6d0634ce67645` (CLI, resumos e logs); não se presume `db:sql` nem unificação de instâncias.
- T1–T3: invocar `m2t test`/`graphql` no mesmo checkout conforme seleção atual, registrar no handoff as instâncias comprovadas e preservar entre comandos/sessões/PR; confirmar posse de escrita na reserva e prova de testes no código corrente, nunca pelo lock/status M2T. Retirar a regra Rancho de `down` ao fim de cada execução somente na issue consumidora.
- T4–T6: após merge/kaizen e gate de elegibilidade, conferir liveness e posse externa; com checkout ainda existente, `m2t --worktree <path> down` para integração e `m2t --worktree <path> down --scope graphql --sandbox-id <token-exato>` para **cada** token próprio. Falha ou `--no-wait` 73 retém checkout e referência; não fazer gc global, não inferir tokens alheios nem remover cache vendor compartilhado.
- T7: `unit`/`exec` possuem recibos/logs privados em `m2t/executions` e cleanup efêmero interno, independentes da retenção de integração/GraphQL; `test`/`graphql` possuem run ID consultável em `m2t runs show <id> --json` e log privado em `m2t/runs`, mas sucesso resumido **não exige** caminho do log na saída. Investigar somente trechos relevantes do log em falha; recibo/ID/status não prova aprovação.
- Prova do consumidor nesta entrega: inspeção do contrato público M2T no merge, testes documentais T1–T7 em `tests/test_m2t_worktree_guidance.py`, referências sincronizadas e suíte Python local. Sem execução M2T/Docker, edição do produtor, Rancho ou plano #61.

## Workflow follow-up

- Após Apply, testes e verificação das tarefas, arquivar/sincronizar a spec na mesma branch e incluir artefatos arquivados e spec viva na PR.
- Após todas as edições e commit final, registrar a suíte obrigatória `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` no HEAD limpo; rerodar se houver novo commit.
