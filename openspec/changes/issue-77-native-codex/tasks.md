# Tasks

Execução somente em contexto Apply novo, após revisão independente da proposta pinada e transferência da reserva; este checklist não autoriza o planner a implementar. Matriz, fronteiras e comandos: `design.md`.

## 1. Seleção e inventário imutável

- [x] 1.1 Estender `scripts/install-global` com agentes suportados, dependências comuns/preflight específico e seleção inicial explícita; ampliar fixtures de `tests/test_global_install.py` com PATH exclusivo por agente e documentar requisitos pt/en; verificar T1/T2/T7 sem executar nem exigir o CLI não selecionado.
- [x] 1.2 Separar manifesto schema 2 determinístico de disponibilidade do pacote e seleção/ownership schema 2 no `guidance.json` existente; implementar verificação confiável de schema 1 sem executar código remoto; testar origem/bytes/modos/manifesto adulterados e migração de instalação OpenCode realista; verificar T2/T3/T8 e documentar ambos formatos.
- [x] 1.3 Implementar update com seleção anterior comprovada e expansão aditiva, inclusive mesma revisão/subconjunto explícito; testar idempotência, expansão sem regravar snapshot, estado anterior inválido e runtime mantido ausente; verificar T1/T2/T3/T7/T8 e exemplos correspondentes no guia pt/en.

## 2. Integração nativa e transação segura

- [x] 2.1 Expor links Codex em `$HOME/.agents/skills` e orientação no CODEX_HOME efetivo, preservando paths OpenCode; gerar orientação mínima compartilhada com cinco skills oficiais; testar roots customizados, espaços/metacaracteres, override, config/credenciais preservadas, skill desabilitada/duplicada e mudança de root; verificar T1–T4/T8 e documentar descoberta/precedência pt/en.
- [x] 2.2 Generalizar validação de links/obsoletos/ownership/migração e rollback para seleção efetiva inteira sob lock existente; ampliar testes de colisão em somente um agente, symlinks, EXDEV/backups e failpoints skills/guidance/launcher/publish; verificar active/seleção/bytes/launcher anteriores preservados em T3/T8.
- [x] 2.3 Ampliar diagnóstico local delimitado aos paths Codex e atualizar `skills/update-ai-workflow/SKILL.md` para seleção preservada, caminhos efetivos e reconciliação explícita; testar somente diagnóstico por padrão, opt-in exato e recusa de origem incerta; verificar T8 e documentação/referências pertinentes sem alterar projetos ou instalação real.

## 3. Mecânica de runtime e provas nativas

- [x] 3.1 Adicionar orientação curta de OpenCode/Codex nos protocolos/entrypoints existentes para identidade nativa, fresh exec, revisão independente e recuperação durável; não criar adapter executável/dispatcher; ampliar testes de contrato/reserva para IDs válidos, callback errado, writer ativo/desconhecido e transferência; verificar T5/T6/T7 e sincronizar referências com `scripts/sync-skill-references`.
- [x] 3.2 Criar `tests/smoke_global_codex.py` com HOME/CODEX_HOME/XDG/PATH descartáveis e preflight de auth/capacidades suportadas; confirmar ID/término de execuções distintas e evidência de contexto novo sem resume/fork; testar negativos sem credencial/capacidade/término e documentar comando/limitações pt/en; verificar T6/T7 sem gravar segredos ou configurações reais.
- [x] 3.3 Implementar descoberta/invocação Codex real do pacote e cinco skills OpenSpec em dois projetos e worktree com espaços; preparar perfil oficial incluindo Verify e scope suportado sem handcraft, preservando fixture multitool/config/specs/changes; verificar T1/T3/T4 com prova nativa e resultado não conclusivo explicitamente bloqueado.
- [x] 3.4 Ampliar `tests/smoke_global_opencode.py` para Verify e scope 2.1 detectado pelo help, mantendo prova API nativa em sessão nova e compatibilidade 2.0; executar com OpenCode real sem Codex exigido; verificar T2/T3/T4 e documentar distinção entre invocação, lifecycle e testes.
- [ ] 3.5 Adicionar ao smoke Codex fluxo mínimo real Explore/Propose→fresh Apply→testes→Verify→Archive com backend GitHub fixture capturado e duas issues sequenciais; provar ausência de duplicatas, comentários/eventos operacionais e criação de evolução trivial/já rastreada; verificar T4/T5/T10/T11 sem criar ou mergear issues reais.
- [x] 3.6 Exercitar retomada entre agentes por artefatos duráveis, PR existente e reserva real, incluindo execução interrompida sem teste aprovado, writer desconhecido e leitura de progresso em ambos; confirmar mesmo checkout/change/PR e zero mutações em consulta; verificar T6/T7/T9 e registrar limitações sem afirmar portabilidade de histórico.

## 4. Publicação verificável A/B

- [x] 4.1 Após estabilizar instalador e testes pertinentes, criar commit imutável A contendo seus bytes novos; registrar SHA completo e digest de `git show A:scripts/install-global` no handoff existente, verificando árvore/reserva e não emendando A posteriormente.
- [x] 4.2 Em commit posterior B, adaptar `scripts/install.sh`/`scripts/update.sh` para encaminhar agentes repetíveis ou preservar seleção verificada, pós-check por integração e uso seguro de argumentos; fixar SHA/digest literais de A; atualizar testes de launcher e receitas README pt/en/changelog no mesmo trabalho; verificar T1–T3/P1 com os fluxos públicos descartáveis.
- [x] 4.3 Ampliar testes de publicação para confirmar A ancestral de B, bytes/digest exatos, recusa antes de executar download adulterado e update partindo de instalação anterior para cada seleção; confirmar documentação avisa limitação de confiança do launcher obtido de main e exige merge commit sem squash/rebase; verificar P1/P2 e não atualizar o pacote global real.

## 5. Integração e validação pré-archive

- [ ] 5.1 Executar grupos focados `test_global_install.py`, `test_install_launcher.py`, `test_instrumentation_distribution.py` com bytecode desabilitado e os dois smokes reais; preencher T1–T11/P1/P2 com comandos/SHA/IDs/resultados efetivos, mantendo limites de fixture e pendências honestos; verificar ausência de plugin, novo ciclo/framework, coletor ou comentários operacionais.
- [ ] 5.2 Invocar a skill oficial local `openspec-verify-change` desta change, resolver/documentar findings conforme severidade e executar `openspec validate issue-77-native-codex --strict --no-interactive`; verificar coerência implementação/spec/tasks e não usar Verify como substituto dos testes/revisão independente.

## Workflow follow-up

- Após implementação e requisitos de revisão atendidos, invocar Archive oficial nesta branch e inspecionar specs sincronizadas/arquivo; não reescrever história arquivada para esconder mudança material.
- Completar preparação/self-review/distribuição/changelog e commits; executar e registrar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` no **HEAD limpo final exato**, verificando prova local acessível. Qualquer commit posterior invalida esse gate e exige nova execução; guardar evidence ID fora do commit.
- Obter revisão PR genuinamente independente do candidato final e aplicar os guardas vivos de HEAD/base/checks/aprovações, preservando modo `auto-if-green` somente nesta issue.
- Fazer **merge commit** para preservar A; se método não estiver permitido, bloquear sem squash/rebase. Confirmar merge/fechamento, A alcançável em main e objetos públicos/pins antes de declarar distribuição entregue.
- Parar writer e fazer housekeeping seguro do checkout desta issue pelas regras existentes. Não tocar #61/#78, instalação global real, outros worktrees, versões desconhecidas ou sandboxes M2T.
