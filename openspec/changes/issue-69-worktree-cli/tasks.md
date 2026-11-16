# Tasks

## 1. Seleção segura do checkout

- [x] 1.1 Adaptar parser/resolução de `scripts/worktree-reservation` para `--path` opcional apenas em checkout existente, com `--show-toplevel` read-only, precedência de caminho explícito e recusa de destino planejado/ausente sem path; provar com testes de raiz/subdiretório de dois linked worktrees, path com espaços e diretório externo em `tests/test_worktree_reservation.py`.
- [x] 1.2 Manter sessão explícita e invariantes de owner/lock/registry/drift/handoff/takeover após resolução; provar reutilizando regressões da reserva e novos casos de sessão omitida/alheia e no-optional-locks no teste focado de reserva.

## 2. Saídas públicas

- [x] 2.1 Adicionar renderização legível por padrão em `scripts/worktree-reservation` de sucesso, conflitos e próximo passo seguro, sem alterar `response()`/exit codes; provar HEAD/digest de código completos, `inventory.digest` de `reconcile` para takeover, candidatos exatos/elegibilidade/motivos de `clean-generated`, entradas múltiplas/vazias de `list`, ausência de inventário completo em `verify` e erro de drift/lock/registry em `tests/test_worktree_reservation.py`.
- [x] 2.2 Garantir `--json` íntegro na stdout para sucesso/erro, inclusive erro de uso quando selecionado, mantendo shape e códigos 0/2/3/4/5/6/7; provar com parsing e comparação de fixture de resposta em teste focado, incluindo shapes de `reconcile`, `clean-generated` e `list` e preservação de bloqueios de takeover/limpeza.
- [x] 2.3 Documentar em `protocol/WORKTREES.md` o comando curto, sessão explícita, `--json` para automação, fallback absoluto e parâmetros ainda explícitos; regenerar referências com `scripts/sync-skill-references` e verificar ausência de divergência das cópias oficiais.

## 3. Instalação e atualização globais

- [x] 3.1 Integrar launcher de `worktree-reservation` em `scripts/install-global`, detectando PATH/colisões/propriedade, imports na versão active, idempotência e rollback; provar com `tests/test_global_install.py` em HOME/PATH descartáveis para instalação, atualização e falha injetada, sem executar instalação global real.
- [ ] 3.2 Revisar orientação gerada, skills e exemplos relevantes para comando público sem pipes que mascarem exit status; manter README.md/README.en.md em paridade quando tocados e provar com testes de distribuição/inspeção dos exemplos em ambiente descartável. A edição parcial já existe no checkout, mas a orientação ainda promete quatro comandos `/opsx-*` incompatíveis com o CLI 2.0; não marcar concluído até resolver a dependência delimitada de bootstrap sem alterar testes/contratos alheios nesta issue.

## 4. Verificação integrada de entrega

- [ ] 4.1 Executar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_worktree_reservation tests.test_global_install` (ou discover com os filtros suportados) e `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`; registrar resultados e revalidar os contratos afetados sem executar instalação real.
- [ ] 4.2 Rodar `openspec validate issue-69-worktree-cli --strict` e verificar matrix dos cenários contra testes, JSON público, segurança da instalação e comandos documentados antes da etapa de arquivo.

## 5. Gate de compatibilidade externo (sem ampliar o Apply da #69)

- [ ] 5.1 Reconciliar a mudança separada de OpenSpec 2.0 para `global-workflow-distribution` (primeiro uso), orientação global, skills de Explore/Propose/Apply/Archive e testes de descoberta nos perfis reais. Referenciar as decisões [#69](https://github.com/rocker-code/my-ai-skills/issues/69#issuecomment-6922770750) e [#61](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6922774044); inventariar resíduos e mudanças globais do dry-run antes de solicitar aprovação explícita para qualquer init/update. Não executar essa migração como tarefa de implementação da #69.
- [ ] 5.2 Antes de retomar Apply, revisar a proposta da #69 contra a revisão exata da compatibilidade 2.0 e suas provas de descoberta em sessão nova; manter a suíte exigida e E_RETRY_LIMIT históricos pendentes, sem reexecutar teste até o diagnóstico e a autorização exigidos pelo protocolo.

## Workflow follow-up

- Após implementação, testes e revisão, arquivar/sincronizar os três deltas na branch conforme o protocolo OpenSpec, inspecionar especificações principais e então preparar PR sem instalar o pacote global nesta tarefa.
