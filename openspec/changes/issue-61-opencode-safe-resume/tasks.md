# Tasks

## Recovery entrypoint
- [x] Create global `resume-workflow` guidance and preserve existing scheduler.
- [x] Define strict candidate disambiguation, safe ownership, dirty worktree preservation, unknown test results, and cross-machine limits.
- [x] Route natural recovery requests in the managed global OpenCode guidance.

## Distribution and documentation
- [x] Add focused global installation/routing regression test.
- [x] Document user request and limits in README/changelog.
- [x] Run official OpenSpec validation on this exact proposal revision in the repository environment.
- [ ] Execute focused installer and existing worktree/execution-state suites in the repository checkout.
- [x] Preservar a prova histórica T1/T5/T7 de `80e5de0` em HOME descartável e sessões novas reais, sem tratá-la como validação da revisão candidata atual ou das skills nativas OpenSpec 2.0.
- [ ] Aguardar o merge da [#71 — contrato de distribuição nativa OpenSpec 2.0](https://github.com/rocker-code/my-ai-skills/issues/71) e verificar seu contrato entregue antes de retomar Apply; revalidar a proposta em SHA exato com OpenSpec 2.0 e inspecionar CLI/docs e arquivos gerados reais. Não resolver aqui o conflito P1 da spec compartilhada de #69, executar `init`/`update`, remover arquivos gerados ou contornar o `E_RETRY_LIMIT` histórico.
- [ ] Após o merge e a verificação do contrato da #71, reexecutar T1/T5/T7 na revisão candidata com modelo em sessões novas reais do OpenCode, comprovando invocação da skill nativa OpenSpec 2.0 aplicável além de `resume-workflow`; registrar SHA/hash/origem das skills carregadas, IDs, prompts, respostas, eventos e inventário Git/OpenSpec/PR antes/depois. Não substituir por descoberta de `/opsx-*`, prova histórica ou mock sem modelo.
- [ ] Após as provas de retomada e os testes focados, arquivar/sincronizar o OpenSpec na branch `issue-61-resume-closeout`, revisar o diff e preparar uma PR de acompanhamento da #61 para o escopo residual, sem recriar a implementação nem a PR #62 já incorporada.
- [ ] Executar e registrar a validação final obrigatória no HEAD limpo e exato da PR de acompanhamento, depois do archive/sync e dos commits finais; não reutilizar checks da #62.
