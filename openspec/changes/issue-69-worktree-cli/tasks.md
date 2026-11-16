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
- [ ] 3.2 Após integração protegida da #71, revisar orientação gerada, skills e exemplos relevantes para comando público sem pipes que mascarem exit status; manter README.md/README.en.md em paridade quando tocados e provar com testes de distribuição/inspeção dos exemplos em ambiente descartável. A edição parcial no checkout antigo ainda promete comandos `/opsx-*` e não pode substituir o contrato nativo 2.0 do merge `5e33688d2a9db702e6bd0f2027d778f3baebdf35`.

## 4. Verificação integrada de entrega

- [ ] 4.1 Após integração protegida e autorização expressa para superar `E_RETRY_LIMIT` G1, executar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_worktree_reservation tests.test_global_install` (ou discover com os filtros suportados) e `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`; registrar resultados e revalidar os contratos afetados sem executar instalação real. A revisão deste plano não reinicia nem reclassifica o gate histórico.
- [ ] 4.2 Rodar `openspec validate issue-69-worktree-cli --strict` e verificar matrix dos cenários contra testes, JSON público, segurança da instalação e comandos documentados antes da etapa de arquivo.

## 5. Gate de compatibilidade externo (sem ampliar o Apply da #69)

- [ ] 5.1 Confirmar a entrega da #71 no merge exato `5e33688d2a9db702e6bd0f2027d778f3baebdf35` e inspecionar contrato, orientação e testes nativos 2.0 nele, não inferir integração por existir o commit. Verificar a reserva; inventariar HEAD, status, diff e digest dos 16 arquivos Apply sem stage, preservar cópia/patch verificável sem remover os originais e preparar base isolada limpa derivada do merge. Confrontar os seis arquivos sobrepostos (`CHANGELOG.md`, `README.md`, `README.en.md`, `scripts/install-global`, `tests/test_global_install.py`, `tests/test_install_launcher.py`) e os dez restantes antes de reaplicar seletivamente; se houver perda não resolvida, parar sem merge/rebase/stash/reset no checkout sujo.
- [ ] 5.2 Em revisão independente, comparar #69 com a revisão #71 integrada e a descoberta nativa 2.0 sem fabricar comandos legados, conferir preservação dos testes #71 e do launcher #69. Manter o histórico G1 em `/tmp/opencode/issue-69-validation.md`: terceira falha da mesma assinatura antes do diagnóstico => `E_RETRY_LIMIT` bloqueado; não relabelar nem repetir G1 até decisão expressa do gate sob o protocolo. A entrega da #71, por si, não libera Apply/testes/PR.

## Workflow follow-up

- Após implementação, testes e revisão, arquivar/sincronizar os três deltas na branch conforme o protocolo OpenSpec, inspecionar especificações principais e então preparar PR sem instalar o pacote global nesta tarefa.
