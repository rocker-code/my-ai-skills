# Tasks

## 1. Retenção e evidência durante o trabalho

- [ ] 1.1 Explicitar em `protocol/WORKTREES.md` o vínculo entre worktree, seleção M2T, handoff existente e revalidação no código atual sem criar registry paralelo; verificar T1–T3 com inspeção da fonte e fixture/teste documental focado.
- [ ] 1.2 Alinhar `skills/implement-issue`, `apply-issue` e `resume-workflow` à retenção entre sessões, separação de posse do checkout/lock M2T e leitura de saída resumida/log pertinente; verificar T1–T3 e T7 por teste documental ou simulação de handoff sem rodar Docker.

## 2. Closeout seguro e escopos reais

- [ ] 2.1 Estender `protocol/WORKTREES.md` com gate de merge/kaizen/dono/liveness/evidência, ordem M2T antes de remoção Git, comandos públicos com path e escopos/tokens próprios, retenção em erro e cache/instâncias alheias intactos; verificar T4–T6 em fixtures de elegibilidade, falha/lock 73 e múltiplas seleções.
- [ ] 2.2 Conciliar `skills/milestone-orchestrator`, `github-resolution`, `prepare-pr` e `post-pr-audit` apenas onde aplicável ao closeout existente, sem mudar política de merge; verificar T3–T6 em inspeção de rotas e testes/fixtures focados, com resultado compacto por seleção removida/retida.

## 3. Distribuição e prova cruzada

- [ ] 3.1 Rodar `scripts/sync-skill-references`, inspecionar diff das referências geradas e atualizar README pt-BR/en apenas se documentarem o fluxo tocado; verificar sincronização e que não há obrigação de `down`/`reset` por comando nas instruções do pacote, nem comando OpenSpec 1.x fabricado.
- [ ] 3.2 Registrar no handoff da entrega o contrato efetivo para adoção posterior em Rancho #457, sem editar repos externos; verificar mapeamento T1–T7 para os merges M2T `04f0272` e my-ai-skills `02194d7`, inclusive ausência de path de log obrigatório em sucesso de test/graphql.
- [ ] 3.3 Executar testes focados existentes/ajustados da documentação/distribuição e `openspec validate issue-70-m2t-worktree-retention --strict --json`; verificar que T1–T7 estão cobertos sem model smoke, Docker, alteração de M2T ou bug separado `workflow-report`/`gh`.

## Workflow follow-up

- Após Apply, testes e verificação das tarefas, arquivar/sincronizar a spec na mesma branch e incluir artefatos arquivados e spec viva na PR.
- Após todas as edições e commit final, registrar a suíte obrigatória `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` no HEAD limpo; rerodar se houver novo commit.
