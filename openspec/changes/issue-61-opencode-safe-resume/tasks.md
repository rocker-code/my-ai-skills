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
- [ ] Construir uma prova isolada de retomada T1/T5/T7 que instale a revisão candidata da skill em HOME descartável e abra sessões novas reais do OpenCode com modelo; não substituir esta prova pelo smoke de descoberta que instala `c48ac58`.
- [ ] Executar T1/T5/T7 na revisão candidata e registrar SHA/versão da skill carregada, IDs das sessões, prompts, respostas e inventário Git/OpenSpec/PR antes/depois; comprovar Apply na proposta validada, bloqueio de dependência e desambiguação sem escrita.
- [ ] Após as provas de retomada e os testes focados, arquivar/sincronizar o OpenSpec na branch `issue-61-resume-closeout`, revisar o diff e preparar uma PR de acompanhamento da #61 para o escopo residual, sem recriar a implementação nem a PR #62 já incorporada.
- [ ] Executar e registrar a validação final obrigatória no HEAD limpo e exato da PR de acompanhamento, depois do archive/sync e dos commits finais; não reutilizar checks da #62.
