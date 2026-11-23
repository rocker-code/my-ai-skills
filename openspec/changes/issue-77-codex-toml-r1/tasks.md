# Tasks

Follow-up material R1 da mesma #77/PR81. Iniciar somente após revisão independente do novo pin e transferência para contexto Apply novo. O archive anterior e T1–T11/P1/P2 permanecem vigentes; esta lista não os substitui.

## 1. Dependência incorporada e guard semântico

- [ ] 1.1 Incorporar em `scripts/install-global` o sdist Tomli 2.5.0 de digest exato D2, sem alterar parser upstream, com licença MIT completa legível e proveniência/manutenção offline em `scripts/vendor/TOMLI.md`; implementar carregamento autenticado/allowlist/namespace temporário privado sem import ambiente, pip ou rede; ampliar testes de distribuição para hashes dos membros/licença, corrupção, standalone sem arquivos vizinhos e limpeza dos recursos; verificar R1.4/R1.5 e documentar a dependência pt/en.
- [ ] 1.2 Substituir regex em `inspect_codex()` por leitura TOML completa e travessia tipada do subconjunto relevante, mantendo critério de conflito e config intocada; ampliar `test_global_install.py` com as quatro grafias diagnósticas, nome/path, chaves quoted/escapes e controles ausente/enabled/outra skill/comentário/string; verificar R1.1/R1.2, inclusive bytes/modos preservados, e documentar o diagnóstico sem indicar config efetiva do runtime.
- [ ] 1.3 Tratar leitura/UTF-8/TOML/schema/limites de parser inválidos como bloqueio delimitado sem valores/segredos, sem fallback textual; testar documento truncado, chaves duplicadas, tipos relevantes errados e segredo sentinela em update multiagente; verificar R1.3/R1.6 com active, seleção, links, launcher, ownership, config e auth anteriores íntegros.
- [ ] 1.4 Executar os casos de parser/guard e bootstrap real em Python 3.10 isolado, sem tomllib/tomli ambiente, e Python atual; testar shadowing por `tomli` sentinela em CWD/PYTHONPATH e OpenCode-only sem carregamento Codex; registrar versão/ambiente/resultados para R1.4, sem usar mock de versão nem instalar pacote/alterar Python do usuário.

## 2. Novo par de publicação imutável

- [ ] 2.1 Criar novo commit A_R1 com instalador completo/licença/proveniência após correção e testes pertinentes; verificar SHA/digest dos bytes completos, igualdade offline com o sdist upstream pinado e ausência de mudança nas âncoras A/B existentes; registrar refs no handoff existente para R1.5/R1.7, sem emendar objetos.
- [ ] 2.2 Em commit posterior B_R1, fixar em `scripts/install.sh` o SHA completo e SHA-256 literal de A_R1, atualizar testes de launcher/receitas README pt/en/changelog e verificar que `update.sh` continua pelo mesmo pin; executar três seleções/fluxos públicos em fixtures descartáveis, recusa de download adulterado e payload interno divergente; verificar R1.4–R1.7 e exigência de merge commit.

## 3. Verificação integrada pré-archive

- [ ] 3.1 Executar grupos focados `test_global_install.py`, `test_install_launcher.py` e `test_instrumentation_distribution.py` com bytecode desabilitado e smokes nativos afetados; preencher R1.1–R1.8 com provas acessíveis/SHA/resultados e preservar T1–T11/P1/P2 sem reclassificar reprodução ou prova histórica como gate novo.
- [ ] 3.2 Invocar Verify oficial desta follow-up, tratar findings conforme política e executar `openspec validate issue-77-codex-toml-r1 --strict --no-interactive --json`; verificar coerência de parser/dependência/spec/tasks e preservar testes/revisão independente obrigatórios.

## Workflow follow-up

- Invocar Archive oficial apenas após Apply/Verify/provas pertinentes, sincronizar deltas no mesmo PR81 e preservar íntegro `archive/2026-11-23-issue-77-native-codex/`; validar specs/archives pelos comandos efetivos.
- Completar commits/archive/distribuição/descrição da PR existente e executar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` no HEAD limpo final exato, com prova local acessível e ID fora do commit. Qualquer commit posterior invalida esse gate.
- Obter revisão independente dos limites alterados no candidato final e renovar guardas vivos de HEAD/checks/aprovações. Não usar reprodução R1 nem revisão antiga para autoaprovar código novo.
- Preservar `auto-if-green` somente para #77 e **merge commit**; verificar ancestralidade e disponibilidade pública de A_R1/B_R1 e âncoras anteriores após integração, sem squash/rebase nem update do pacote real.
- Manter dados/arquivos ignorados, especialmente `scripts/__pycache__/install-globalcpython-314.pyc`, e reserva segura até handoff/housekeeping autorizado. Sem comentários operacionais, mudança de outras issues/worktrees ou nova infraestrutura de registros.
