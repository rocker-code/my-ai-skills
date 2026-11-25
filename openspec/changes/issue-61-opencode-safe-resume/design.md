# Design

## Context

Reconciliação em 25/11/2026: entrada `d34c1c1d4438758cc88e43b3c31fce22a0cc9d30`, proposta anterior `f159134b68ca5c8d13ffcb1a38b7a3c7673dbcc8`, alvo imutável `12ca324faf2865faa62d16e55715d3ddd0adb53a`. O diff da branch contém 38 commits exclusivos; árvore rastreada inicialmente limpa e nove bytecodes ignorados preservados. Ver motivação e decisões aprovadas em `proposal.md`.

Foram lidos no alvo `skills/{implement-issue,openspec-workflow,resume-workflow,milestone-orchestrator}/SKILL.md`, `protocol/{AI_WORKFLOW,TEST_STRATEGY,WORKTREES,REVIEW_POLICY}.md` e specs `issue-delivery`, `workflow-execution-state`, `checkout-write-reservation`, `global-workflow-distribution`. #71 já está integrada; #69/#70 e #75/#76/#77 estão entregues no alvo, não são novas issues a executar. Main retirou helpers/testes de telemetria e audit/ready, mantém um coordenador e suporta Codex sem exigir OpenCode. Seu change #61 ainda conserva planejamento inicial desatualizado: não sobrescrever esta reconciliação com essa cópia.

O código existente já implementa dois turnos T7, recibo `Popen.wait()` de writer cooperante, guard de argumentos e rejeição de leituras nativas pré-escolha por skill/read/grep/rg, mesmo failed/cancelled. Não descrevê-los como ausentes nem reimplementá-los do zero. Ainda há dependências incompatíveis: `snapshot`, `t7_reinventory`, prompts e semeadura usam ledger/`workflow-event`/`workflow-report`; `native_calls` aceita leitura direta como invocação; T5 usa `disposable-pr-head` não Git SHA; a fixture copia `openspec/` inteiro, mas valida o nome fixo do change como ativo, sem resolver seu archive.

CLI local observado: OpenSpec `2.1.1`; `context/list/status` resolvem este root e change. Explore/Propose/Apply/Archive/Update estão geradas em `.agents/skills`, com `generatedBy: "2.0.0"`. Perfil global observado `core`, delivery `skills`; Verify não está gerada aqui, mas sua skill oficial já está rastreada no alvo. Não concluir incompatibilidade nem executar init/update/config global nesta Planning. No Apply, integrar e descobrir Verify existente; se necessário habilitar oficialmente com união das escolhas e autorização de impacto, sem simular sua execução. OpenSpec 2.x nativo não exige arquivos de comando `/opsx-*`.

## Goals / Non-Goals

**Goals:** preservar T1–T7; restaurar compatibilidade com o alvo; provar roteamento natural, continuidade e limites reais sem telemetria; entregar apenas o fechamento residual de #61.

**Non-Goals:** implementar #78 ou outra issue, novo scheduler/dispatcher/registro de execução, coletar métricas, publicar comentários de progresso, substituir o pacote global do usuário, limpar os nove bytecodes, executar Apply/merge/testes caros nesta Planning ou portar o smoke #61 para Codex. Os contratos Codex existentes permanecem e seus testes relevantes não podem regredir.

## Decisions

### 1. Integração somente no Apply com preservação de histórico

Após revisão independente do commit desta proposta, encerrar o writer de Planning e transferir a reserva para identidade nativa real de um Apply novo. Verificar HEAD/proposta/review, alvo e inventário. Integrar **exatamente** `12ca324faf2865faa62d16e55715d3ddd0adb53a` por `git merge --no-ff --no-commit <SHA>` no mesmo checkout, inspecionar índice/diff/conflitos e só então criar merge commit. Não rebase/reset/stash/clean, estratégia ours/theirs em massa nem aceitação de drift. Conflito não resolvível dentro do contrato fica preservado e bloqueia somente a integração; não descartar estágios ou trabalho parcial. Confirmar ancestralidade do HEAD de entrada e do alvo e conservar os 38 commits.

Resolver semanticamente a eventual sobreposição em `skills/resume-workflow/SKILL.md`, `tests/test_global_install.py` e neste change: manter o workflow curto de main, sua seleção multiagente, parser TOML autenticado, referências geradas e remoções de #75/#76; portar somente as garantias residuais de #61. Não restaurar o estado antigo para fazer os testes antigos passarem. O teste `test_workflow_execution_state.py` e os helpers de ledger removidos não são dependências a ressuscitar.

**Instalador:** usar os bytes do alvo sem mudanças. A_R1=`7c4cfb4433c4f56b9af463759e8215174b5b9663`, SHA-256 literal de `scripts/install-global`=`93cd9371b602a47c66b6bc3b20be448f6c124fc88b10a9f5d041f611dddc1a5f`, B_R1=`a0806493280d062ae477a608ccdcc67a3ca337e5`. O blob do instalador no alvo é `6935d06c383894e00d97af883e2418c2407f6785`; o bootstrap público instala o snapshot solicitado, não somente A_R1. Não recolocar A/digest anteriores. Se for demonstrada necessidade real de alterar bytes compartilhados, parar essa ação e revisar a proposta para novos anchors A/B imutáveis, sem emendar os publicados; manter sua alcançabilidade e merge commit.

### 2. Fontes existentes em vez de ledger

Reutilizar `tests/fixtures/resume_gh.py` como shim estritamente read-only para issue/corpo/decisões, PR/head/checks e dependências. A fixture é entrada de teste, não novo protocolo persistente de produção. Preparar estado por arquivos descartáveis do harness, sem endpoints de escrita, flag de semeadura de comentários ou registro de eventos. Recusar escrita GitHub e registrar tentativas localmente apenas para auditar o teste. Comentários históricos reais ficam intactos e não são consumidos como ledger ativo.

Last gate/proposta vêm de commits, validação OpenSpec e revisão identificada; escopo/dependência/merge mode vêm de requisitos/decisões explícitos; sucesso de teste vem da prova executada acessível; parada do writer vem do runtime. Confrontar fontes e SHA, em vez de confiar em `recovery-evidence.json` declarativo. `run_id` histórico é apenas correlação, nunca um estado autoritativo ou autorização de merge. Incluir checks no SHA efetivo e resultados ausentes como UNKNOWN. PR/head simulado deve apontar a commit Git real da fixture e não a placeholder.

Snapshots de cada fase cobrem Git da raiz e dos checkouts (HEAD/branches/worktrees, índice e conteúdo staged/unstaged/untracked/ignored relevante), change/specs e seus bytes, reservas completas owner/state/digest, issue/PR/head/checks/dependências/mode e recibos independentes. Separar leituras/probes com exit próprio: nenhum `;`, pipe, redirecionamento ou `&&` pode mascarar falha. Snapshots iguais provam ausência de efeitos, não ausência de tentativa proibida; inspecionar também todos os tool calls, inclusive failed/cancelled. Não alegar segurança de shell arbitrário apenas por uma lista de verbos: usar permissões read-only efetivas quando suportadas e revisão dos eventos.

### 3. Prova real e nativa na revisão candidata

Instalar snapshot de HEAD limpo em HOME/XDG/DB descartáveis; preservar shim OpenCode absoluto com quoting, launcher de reserva primeiro no PATH e exclusão do HOME real. Fixar revisão no manifesto, bytes/hash de `resume-workflow`, regras carregadas, origem/path real/symlink/hash de cada skill oficial e versões reais. Não alterar o prompt inicial T1 para nomear `resume-workflow`: isso trocaria descoberta natural por lookup dirigido. Guard de `--help`/argumentos inválidos deve continuar saindo antes de fixture, descoberta ou modelo.

Manter sessões reais novas T1/T5/T7 e **um mesmo ID nativo** nos dois turnos T7. Exigir evento de descoberta e invocação **nativa** efetiva correlacionado ao caminho/hash e sessão, além do acesso observável às instruções/validação aplicáveis. Leitura de `SKILL.md`, CLI isolado, help, stub ou resposta “usei” não bastam como invocação; são evidência auxiliar. Adaptar `native_calls` a esse contrato atual sem enfraquecer o guard pré-escolha. Se o runtime não expuser o sinal requerido, bloquear com limitação exata, não inferir PASS.

T1 confirma proposta/review no commit real e que Apply é a próxima ação, sem executar Apply no smoke. O harness observa um writer cooperante real ainda vivo e depois seu término por `wait()`/exit, com identidade do processo e checkout/owner/run correlacionados; recibo fora do checkout do modelo, sem derivar parada de PID ausente. Referência de processo da fixture não pode se apresentar como session ID nativo OpenCode. Exercitar ausência, identidade errada e writer ativo como negativos; em produção apenas evidência autoritativa disponível ou recuperação local fundamentada autoriza transição.

T5 preserva PR/head/checks, modo manual e consumidor bloqueado, sem dispatch/duplicação/mutação. T7 fase 1 termina em uma pergunta neutra visível com os dois pares issue/run, sem seleção/takeover/dispatch/escrita ou invocação/leitura de conteúdo de skill nativa. Cancelamento de `question` não substitui a pergunta visível. Fase 2 recebe escolha explícita no mesmo ID, reinventaria ambos os checkouts/reservas e fontes, consulta prova do writer escolhido e só depois invoca Explore nativa read-only. Conferir snapshots antes/depois de **cada fase**, preservando o candidato não escolhido. Falha/timeout/falta de evento ou prova mantém bloqueio.

### 4. Entrada do smoke independente do archive

Não copiar cegamente `openspec/changes/issue-61-opencode-safe-resume` do HEAD: após archive ela muda de caminho. O harness deve selecionar o contrato ativo ou seu único archive correspondente, usando manifesto/commit/path/hash, e preparar a partir dele uma fixture OpenSpec válida, conservando a distinção entre **SHA da candidata instalada**, **SHA da proposta revisada** e **SHA do commit de contrato na fixture**. Não substituir esses SHAs entre si nem confiar só em strings de resultado.

Uma execução completa T1/T5/T7 é necessária na revisão final candidata. Realizar amostras offline antes de gastar modelo. Após Verify/archive/sync/docs/distribuição/commits finais, executar smoke no mesmo HEAD limpo ou refazê-lo se qualquer commit tiver invalidado sua candidata. O smoke produz prova local externa ao commit; o arquivo de prova não requer novo commit. Revisão dos eventos por execução independente é adicional à asserção automática, não troca de papel no executor. Reusar revisão válida do mesmo SHA/contexto.

## Evidence matrix

Todos os resultados atuais abaixo estão **PENDING/NOT RUN** nesta Planning; evidência histórica não aprova nova candidata.

| ID | Aceite/risco e consumidor/assunção atual | Camada e menor prova planejada | Evidência exigida |
| --- | --- | --- | --- |
| I1 | Main novo versus 38 commits antigos; distribuição/semântica compartilhada | Integração Git: merge preservado, ancestralidades, diff de pins/remoções, `test_instrumentation_distribution.py` | Merge SHA + testes focados no novo HEAD |
| D1 | Roteamento/atualização pública; `test_global_install.py` já cobre descoberta, seleção e pins novos | Estender `test_public_install_and_update_execute_pinned_installer_and_active_command` para bytes da skill nova, manifesto/symlink/AGENTS preservado; reusar seleção Codex-only/ambos sem runtime cruzado, `test_install_launcher.py` | Recibo local de instalação/atualização e checks de digest; stub não prova modelo |
| T1 | Issue/proposta/review existentes; `terminal_receipt` já espera child real, `native_calls` ainda aceita read | Offline negativo ausência/owner/run/checkout incorretos e writer vivo; depois OpenCode real, roteamento natural, último gate/Apply e recibo terminal, nenhuma execução Apply | Eventos nativos + identidade/término + snapshots + SHA validado/review |
| T2 | Preservar staged/unstaged/untracked/ignored e crash pré-checkpoint | Reusar `test_index_blob_and_mode_change_with_same_xy_and_worktree_changes_digest`, `test_incomplete_baseline_is_recovered_without_discarding_diff`; estender fixture apenas para conteúdo/ignored não coberto | Bytes/índice inalterados e commits preservados em teste de reserva |
| T3 | Writer ativo ou posse inconclusiva não permite escrita | Reusar `test_reconcile_recovery_required_blocks_active_worker`, `test_takeover_requires_expected_owner_evidence_and_inventory_digest`, `test_takeover_refused_when_owner_pid_alive` e handoff | Recusa sem alteração de código/posse, ID do chamador próprio |
| T4 | Comando/teste interrompido não é PASS; suite de execution-state foi retirada | Reusar casos incomplete/stale de `test_workflow_evidence.py`; acrescentar à fixture retomada sem terminal/relatório e resultado de outro SHA/execução | UNKNOWN e somente obrigação afetada pendente, sem coletor |
| T5 | PR existente/manual e dependência bloqueada; placeholder de head inválido | Fixture read-only com commits/checks reais correlacionados; regressão offline de fontes/sem escrita; sessão OpenCode real com invocação nativa | PR/head/mode/dependência e reservas intactos; consumidor sem dispatch |
| T6 | Registry ausente/checkout perdido; reconstruir só dados disponíveis | Reusar recovery/incomplete em `test_worktree_reservation.py`; fixture pequena de perda local com refs Git sobreviventes e dado local explicitamente indisponível | Sem posse implícita, nada inventado/restaurado por prosa |
| T7 | Dois candidatos; detector atual lê ledgers e prova read como native | Migrar `T7ReinventoryTest` às fontes atuais; preservar `T7VisibleQuestionTest`, probes isolados, negativos failed/cancelled/grep/rg/cadeias/ID errado; depois dois turnos reais | Mesmo ID, escolha explícita entre fases, ambos snapshots, native só pós-escolha |
| F1 | Smoke precisa sobreviver archive; suíte final não pode ser SHA anterior | Regressão offline ativo/arquivado/ausente/ambíguo; Verify oficial, strict/archive/sync; suíte local completa no HEAD final limpo | `workflow-evidence` verified/passed exato + eventos smoke + revisão/CI aplicáveis |

## Migration Plan

1. Planning revisa apenas os cinco artefatos existentes; valida pelo CLI oficial e fixa commit. Revisor independente verifica principalmente substituição de fontes, T1/T7, pins, matriz e compatibilidade do smoke pós-archive. Sem aprovação independente, não iniciar Apply.
2. Apply novo verifica reserva e referências políticas atuais contra este alvo, integra main como acima e migra fixtures/testes/documentação em pequenos passos. Usar `unittest discover -s tests -p <arquivo>`: import de irmão não funciona com o comando antigo `tests.test_resume_reinventory`. Rodar amostra de retomada/reserva/distribuição antes de smoke; não chamar o smoke para “descobrir” sua CLI.
3. Preflight antes de execução cara: ferramentas Git/Python/OpenCode/OpenSpec e versões reais, paths/import/discovery, todos HOME/XDG/CODEX_HOME/DB/credenciais/sandbox efetivos, child lifecycle, checkout testado e rollback de fixture. A fixture de main já remove `XDG_STATE_HOME` externo no instalador; preservar isso em vez de editar produção para satisfazer lock em path errado. Não há Magento/M2T nem lockfile de aplicação relevante; registrar não aplicável, sem criar sandbox de serviço.
4. Diagnosticar falhas com prova comparável no alvo exato e ambiente equivalente antes de chamá-las preexistentes. Registrar repetições no handoff/PR existente conforme `protocol/TEST_STRATEGY.md`; conferir `scripts/attempt-log check` antes de nova tentativa e `--final` antes da PR quando aplicável. Falha de ambiente mantém guard contra editar produção sem reclassificação comprovada.
5. Só executar uma observação model-backed por tentativa após preflight/diagnóstico/revisão aplicáveis; sem retry/fallback automático. Timeout externo adequado ao smoke (histórico: 30 min) não garante capacidade do provedor. Reter relatório/exit/events/receipts/hash em `workflow-evidence`/bundle, não somente caminho temporário.
6. Após implementação, invocar Verify oficial, resolver findings, validar estritamente change e specs, invocar Archive nativo na branch e inspecionar sync sem sobrescrever cenários atuais de main. Completar docs pt/en, changelog e referências antes do commit final. Workflow follow-up não é checkbox que exija archive para ficar completo.
7. No HEAD limpo final, rodar/registrar/verificar `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`, strict global e smoke final conforme matriz. Qualquer novo commit invalida a suíte final e a prova smoke do HEAD anterior. Verificar checks/proteções/review exigidos ao abrir/reusar a PR; não inventar hosted gate ausente (nenhum workflow `.github/` rastreado foi localizado no alvo), mas consultar política GitHub atual. A revisão independente final vincula mesmo HEAD/base/contexto e inspeciona eventos. Merge HELD; reter checkout/branch/dados.

## Risks / Trade-offs

- [Política antiga instalada e checkout anterior a #75/#76/#77] → ler sempre as refs pinadas atuais; integração não é atualização global implícita. Reconciliar divergência de base/política antes de Apply; novo alvo material exige nova revisão.
- [Receipts/relatórios antigos indisponíveis] → UNKNOWN, jamais PASS; não reconstruir detalhes de diagnóstico sem evidência. Reexecutar apenas obrigações incompletas ou invalidadas pela integração revisada, mantendo o histórico abaixo.
- [Runtime/modelo não oferece capacidade nativa ou quota] → bloquear ação dependente com causa exata; não substituir por read/stub ou simular independência.
- [Helper coordena só writers cooperantes] → reserva/checkpoint não autenticam stopped-evidence nem autoria; preservar dados e parar quando houver incerteza.

## Historical evidence and recovery limits

| Fato acessível | Classificação e consequência |
| --- | --- |
| PR #62 MERGED; proposta anterior `f159134b`; 38 commits preservados em `d34c1c1` | Continuidade de Git, não prova dos gates residuais |
| `docs/issue-61-candidate-recovery-proof.md` conserva prova de `80e5de0dd4351770b61941cda7dfc798b14ed7ac` | Preservar documento histórico; não comprova candidata atual nem invocação nativa OpenSpec requerida pelas decisões posteriores |
| Comentários históricos relatam 6/252 falhas, T7 sem correlação/probes, 429, `--help` iniciando modelo/timeout, lock XDG e teardown | Fatos relatados, não recibos novos; não apagar episódios nem fabricar causa do teardown, cujo detalhe permanece UNKNOWN |
| Comentários relatam T1 seq23 timeout e T7 seq28 ativos, além de diagnósticos/correções posteriores | Sem `/tmp/opencode/issue-61-validation.md` e recibos originais acessíveis, estado final/diagnóstico completo não é recuperável. Antes de nova tentativa equivalente, registrar limites e diagnóstico atual completo fundamentado; não dar aprovação retroativa nem falsificar seq/resultado antigo |
| `ev-20261118T202412Z-a5a4576f` acessível, exit 0, HEAD `d34c1c1`, log checksum `a6230498215dae3553d2751131c861d27f61a74f3a22db0b6f01b89ef31bff4b` | 12 testes offline antigos do detector, não smoke nem suíte final; após novo commit é evidência histórica/stale |
| Observer `observe-61-d34c1c1` sem recibo terminal acessível | UNKNOWN; `provider.no-route` na prosa do registry não comprova erro terminal nem PASS |
| Coordenador verificou host ASUS/ext4 local `/dev/nvme0n1p2`, boot `2026-11-24T19:22:59Z`, ID `482bd630-eb91-4a6c-88aa-ccb824e0ddc7`, e nenhum writer pós-boot identificado em runtime/proc | Fundamenta nova reserva local após reboot, não takeover remoto: o hash histórico Dell e terminal original indisponível não são prova de smoke nem de término daquele observer |

O `run_id=wf-20261116T064328Z-45cb0ecc` é continuidade histórica sem logs operacionais novos. Não recriar ledger nem publicar comentário GitHub rotineiro. Manter fatos e provas no OpenSpec existente, handoff/PR e artefatos de teste já suportados.
