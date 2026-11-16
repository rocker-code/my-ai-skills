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
- [x] Integrar o merge da [#71 — contrato de distribuição nativa OpenSpec 2.0](https://github.com/rocker-code/my-ai-skills/issues/71), PR #72, `main` `5e33688d2a9db702e6bd0f2027d778f3baebdf35`; verificar `.agents/skills/.openspec-target` (`opencode`), skills nativas em `.agents/skills/`, remoção das cópias/comandos legados e CLI OpenSpec 2.0. Não resolver aqui o conflito P1 da spec compartilhada de #69, executar `init`/`update` ou contornar o `E_RETRY_LIMIT` histórico.
- [ ] Revalidar esta proposta no SHA exato com OpenSpec 2.0 antes do Apply; inspecionar novamente contrato e arquivos reais na fixture descartável, sem confundir presença de arquivos com invocação.
- [ ] Reexecutar T1/T5/T7 na revisão candidata com modelo em sessões novas reais do OpenCode, comprovando descoberta e invocação da skill nativa OpenSpec 2.0 aplicável além de `resume-workflow`; registrar SHA/hash/origem das skills carregadas, IDs, prompts, respostas, eventos e inventário Git/OpenSpec/PR antes/depois. Não substituir por descoberta de `/opsx-*`, prova histórica ou mock sem modelo.
- [ ] Após as provas de retomada e os testes focados, arquivar/sincronizar o OpenSpec na branch `issue-61-resume-closeout`, revisar o diff e preparar uma PR de acompanhamento da #61 para o escopo residual, sem recriar a implementação nem a PR #62 já incorporada.
- [ ] Executar e registrar a validação final obrigatória, incluindo `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`, no HEAD limpo e exato da PR de acompanhamento, depois do archive/sync e dos commits finais; não reutilizar checks da #62 nem de `80e5de0`.
