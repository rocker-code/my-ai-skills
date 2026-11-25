# Prova isolada de retomada — issue #61

## Recuperação atual — 25/11/2026

**Handoff canônico da execução residual; gates pendentes.** A descrição abaixo de
16/11 é histórica, não aprovação da candidata atual nem do contrato posterior
de T1/T7. Os recibos em `/tmp` daquela máquina não estão disponíveis aqui.
Sem término/relatório acessível, o resultado permanece **UNKNOWN**.

### R1 residual — controle nativo pré-spawn, sem inferência

Writer delegado `ses_deef1ed65ffez0d4OTgc6z8rcl`, worker `fix61-rawshell`,
entrada `481b2539aadbaec9f5bcc15c93ac613e258eea8a`, mesmo checkout/branch/run
e proposta `31cdb42`. Reserva adquirida com a sessão real e checkpoint.
Escopo: **somente harness/fixture/testes/handoff**, sem merge, PR, push, archive,
credenciais, update global ou plugin pessoal/distribuído (#52).
A revisão `ses_def0f16a9ffeAEin2bLMykHlkm` confirmou R2–R4 resolvidos; R1
continuava aberto: restringir reads não conserta o scanner shell.

**Causa comprovada:** `export GIT_CONFIG_COUNT=1
GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=<hook descartável>;
git status --short` pode chegar à autorização somente como `git status --short`.
Declarações, ambiente e composição não ficam confinados por essa permissão.
Uma deny rule para `export` ou detector posterior não seria controle pré-spawn.
Nenhum arquivo/credential/config do operador foi usado como probe.

Correção mínima: `tests/fixtures/resume_shell_guard.mjs` é **copiado somente
para o runtime descartável**, fora dos checkouts da fixture. O harness referencia
seu **diretório** em `plugins`, nunca instala em HOME real, pacote global ou
`.opencode/plugins` persistente. `install-global`, componentes distribuídos,
launchers e pins permanecem inalterados.

- `tool.execute.before` rejeita a entrada shell bruta antes do executor.
- `shell.create.before` confere novamente o comando inteiro e cwd final,
  antes do scanner/permission callback e de ambos os caminhos de spawn.
  Comparação por igualdade com allowlist literal gerada das leituras já
  autorizadas; cwd precisa ser um checkout exato e real, sem alias symlink.
  Declarações, compostos, expansão, prefixos env, argv extras e cwd alheio
  **não** são normalizados para um comando permitido. Não há parser novo.
- O segundo hook fixa `/bin/sh` e substitui, não mescla, o ambiente do filho
  por constantes da fixture. Não herda `BASH_ENV`, `ENV`, loaders, funções
  exportadas ou overrides da sessão; Git ignora config global/sistema, não
  atualiza index opcional e tem fsmonitor=false. Reads/grep/glob e catálogo
  de modelo continuam com as restrições anteriores.
- Fonte/policy têm SHA-256 na preparação persistida. Preflight
  `debug agents --standalone` exige **novo** evento setup/active da fonte
  exata; log antigo, falta de ativação ou falha bloqueiam antes do modelo.
  Esse preflight usa outro processo standalone; não se confunde com prova
  de execução do modelo. A admissão de prompt nativa também espera plugins.

**API e fonte oficiais efetivamente inspecionadas (V2 / tag v2.3.2):**
[lifecycle/load](https://opencode.ai/docs/build/plugins),
[hooks shell/tool e tool.list](https://opencode.ai/docs/build/plugins/server#shell),
[API](https://opencode.ai/docs/api);
`packages/core/src/{shell.ts,tool/plugin/shell.ts,plugin/hooks.ts,
session/command.ts}` e `packages/plugin/src/{promise/tool.ts,promise/adapter.ts}`
em [anomalyco/opencode v2.3.2](https://github.com/anomalyco/opencode/tree/v2.3.2).
`Shell.create` dispara `hooks.trigger("shell","create.before",invocation)` antes
de `before(invocation)`/scanner, ID e spawn/daemon. O adapter converte rejeição
do tool-before em Tool.Error; shell-before usa Effect.promise (falha/defect
propaga, não é uma nova permissão tipada). A prova abaixo verifica o abort real
nesse runtime, não presume que o hook shell tenha um contrato tipado de deny.
O carregamento fica limitado ao lifecycle da instância e dispose no cleanup.

**Provas pre-smoke recuperáveis, não gates finais:**
Os recibos abaixo são da implementação, vinculados ao fingerprint com diff;
não são aprovação do HEAD limpo posterior nem gate pós-archive.

| Evidência | Resultado e limite |
| --- | --- |
| `ev-20261125T050448Z-7af3b952` | 31/31 offline (24 R1–R4/catálogo anteriores + 7 guard/ativação). Inclui igualdade raw, 28 variantes de injeção, cwd/argv inválidos e ativação ausente/stale. Avaliação direta/mocks são testes unitários, não prova nativa. |
| `ev-20261125T050526Z-c5403829` | OpenCode 2.3.2, sessão `ses_deee7cf4affeD8i0KAjAsDmUt1`, executor shell nativo via `ctx.tool.list().find(id=shell).execute` em comando temporário: 1 leitura permitida, 10 rejeições no hook nativo shell-before. |

A segunda evidência retém em stdout checksum-bound os resultados, audit,
policy, fonte do guard/bridge, controle positivo e log nativo redigido; os
arquivos originais ficam em `/tmp/opencode/issue61-rawshell-ses_deef1ed65ffe`.
O controle positivo executa um hook **inofensivo** somente nessa fixture.
Na execução protegida, o mesmo payload export/fsmonitor é rejeitado sem
progress/shellID, sem marker do hook e sem mudar bytes do repo (incluindo
`.git`) ou ambiente do processo harness. Todas as dez rejeições são
correlacionadas ao hook; setup/cleanup também foram observados. Sessão sem
mensagens, tokens/custo zero. O bridge chama o executor real e seu scanner/
permission/spawn internos; **não** usa modelo nem o dispatcher genérico de
tool calls, portanto não prova esse dispatcher/model-backed nem a capacidade
de inferência. Não se atribui prova runtime aos callbacks unitários.

Diagnóstico das execuções intermediárias, preservado sem reclassificar:
`ev-20261125T050017Z-{8d03877d,3190c0b3}` falharam nos asserts unitário de
None→undefined e formato da versão; `ev-20261125T050109Z-3ab7a47f` falhou no
envelope API `data`. `ev-20261125T050150Z-b19f7f75` detectou carregamento
incorreto por path de **arquivo**: OpenCode exige diretório, não carregou o
guard e a fixture inofensiva reproduziu o bypass. Corrigidos o load e a
exigência explícita de ativação antes de qualquer probe. O primeiro sucesso
nativo `ev-20261125T050239Z-37241a8d` antecede a prova completa retida acima.
Uma tentativa de anexar `/tmp` ao recorder foi recusada pela fronteira
checkout-only; nenhum contorno foi introduzido.

**Estado permanece WAITING:** zero inferências nesta correção. O attempt-log
seq6–8 abaixo conserva **HTTP 400 / blocked**, não PASS; T1/T5/T7 model-backed,
3.4/4.3, archive e gate final pós-archive continuam pendentes. Suite integral
do HEAD corrigido é somente pre-smoke; revisão independente do raw guard e
da prova é a próxima ação **antes** de autorizar qualquer inferência.

### Correção offline após revisão independente

Fonte atual de autorização: o coordenador transmitiu nesta delegação a resposta
direta do proprietário **“Sim, se aprovado”** para **AUTO-IF-GREEN**, escopo único
#61, run `wf-20261116T064328Z-45cb0ecc`. É autorização posterior, não recuperação
da autorização original desconhecida nem aprovação de gates. As referências
HELD do planejamento pinado registram o conhecimento daquela data; não foram
reescritas para fabricar histórico. O writer anterior
`ses_def08c6bdffe43exnubv86SE83` permaneceu **NO MERGE / NO PR / NO ARCHIVE**.

Revisão fonte `ses_def0f16a9ffeAEin2bLMykHlkm` no HEAD de entrada
`5de88ac47e24c95f92fa4c7dd930af9d60aa80b6`: quatro MUST FIX válidos,
preservando o contrato `31cdb42`. Correções limitadas ao harness/testes/fixture
e a este handoff; sem alteração de instalador, launchers, pins ou produção:

- R1: `read`/`external_directory` somente nos roots exatos da fixture,
  checkouts, runtime e release instalada descartável. `grep`/`glob` ficam
  negados porque autorizam regex/pattern, não o diretório pesquisado;
  descoberta por listagens shell exatas, sem wildcard de comando. Todo
  restante continua deny-by-default, inclusive outros HOME/source/tools.
- R2: preparação/snapshots/permissões/proveniência persistidos antes de
  preflight/launch. Erros de provedor, JSONL inválido e timeout retêm terminal,
  eventos redigidos e IDs; captura posterior é best-effort. Indisponibilidade
  produz `after=null`, `after_status=unavailable`, `unchanged=null`, não igualdade
  inferida; erro propaga sem próxima fase/cenário ou aprovação.
- R3: `git -C ... switch` negado/falho também invalida a pausa. Fase 2 usa
  a primeira tentativa de conteúdo/invocação de qualquer skill nativa,
  independentemente do status, não apenas Explore bem-sucedida posterior;
  mantém dois turnos no mesmo ID, escolha explícita, probes, snapshots e
  proibição de takeover/dispatch inclusive tentado.
- R4: T5 exige PR #12 lido com sucesso pelo shim e por tool event da mesma
  sessão, head/checks correlacionados ao commit, manual e dependência #13
  consultada. O shim read-only existente registra resultado/exit estruturados
  em arquivo descartável; prosa, argv sem sucesso, head/checks stale ou
  ausentes não aprovam.
- Modelo: retirado default hardcoded obsoleto. `RESUME_SMOKE_MODEL` continua
  override de uma execução; sem ele consulta `/api/model/default` e cruza
  `/api/model` no mesmo HOME/XDG/DB/Location isolados. Exige chat habilitado,
  tools e text input/output, preço conhecido zero em todos os tiers/cache.
  Ausente/incompatível/pago/desconhecido bloqueia sem fallback ou geração.
  Persiste seleção/fonte/capacidade/custo antes de lançar; não retém settings,
  headers ou credenciais. `OPENCODE_MODEL` não foi importado nem pressuposto.

Documentação oficial V2 consultada: `/docs/permissions`, `/docs/config`,
`/docs/api`, `/docs/cli`; schema real `/openapi.json` do OpenCode 2.3.2,
incluindo `Permission.Rule`, create session/request e
`Model.Info/Capabilities/Cost`. Última regra whole-value `*`/`?` prevalece;
read relativo interno/absoluto externo e external_directory são verificações
distintas; o scanner shell é best-effort, não sandbox.

Diagnóstico da **prova de regras**, separado do modelo HTTP 400: chamadas
`api --standalone` curtas retornaram deny onde se esperava allow
(`ev-20261125T043644Z-5fbb82da`, depois
`ev-20261125T043850Z-9f818664`). Consulta nativa de config confirmou as regras,
mas o snapshot de agent ainda mostrava somente base policy; os endpoints não
comprovam transformações de agent concluídas. Um probe intermediário foi
terminado pelo timeout externo de 1 s
(`ev-20261125T043820Z-5948c6e7`), não PASS nem falha de inferência.
Fase: avaliação API, nenhum prompt/tool/modelo; escopo: DB/HOME descartáveis;
lifecycle: processos terminais, sem callback presumido; consumidor: script
diagnóstico externo, não código de produção. Código oficial v2.3.2
`packages/core/src/permission.ts` confirma merge de agent + session e
`findLast`/`util/wildcard.ts`; ausência de agent usa deny. Alternativa mínima:
não inferir config carregada de uma resposta inicial. Próxima prova usa a
mesma lista explícita em `session.permissions` para verificar o avaliador
nativo com precedência final, declarando o limite: não prova scanner, leituras
reais nem settlement config→agent. Isso não resolve retroativamente falhas.

Provas da correção (pre-smoke, não gates finais):
`evidence:ev-20261125T044207Z-fa08f635`, **24/24** testes offline, incluindo
HTTP 400/nonzero, JSONL malformado, timeout, snapshot ausente, negativos
pré-escolha/primeiro native, PR ausente/falho/stale/wrong-head e catálogo
ausente/incompatível/preço desconhecido/pago. A prova de avaliador nativo
`evidence:ev-20261125T044212Z-487d246c` concluiu **64/64** avaliações da mesma
lista em `session.permissions` (32 por fase), incluindo reads necessários,
negação de HOME/source alheios, shell externo, grep/glob, execute/subagent e
precedência pré-escolha. Confirma o avaliador, **não** scanner/execução de
ferramentas ou carregamento final config→agent. Não foi importada credencial.

Metadados prospectivos desta prova: OpenCode **2.3.2** retornou
`opencode/big-pickle` de `/api/model/default`, também presente no catálogo,
chat `active/enabled`, tools=true, text→text; tier input/output/cache read/write
zero. Nenhum `RESUME_SMOKE_MODEL`, `OPENCODE_MODEL` ou modelo configurado pelo
operador foi herdado. O endpoint é fonte de default nativo, **não evidência de
preferência do usuário**; snapshots API podem anteceder settlement de plugins.
Isso difere do `tidepool-alpha-free` relatado pelo coordenador e não o invalida
nem justifica hardcode/fallback. Disponibilidade de inferência continua
**NOT VERIFIED** para ambos; a seleção será reconferida no ambiente da próxima
fase aprovada. O velho `glm-5.3-flash-free` permanece falha histórica.

Nenhuma inferência nova nesta correção. Após provas offline, **revisão
independente de isolamento/prova ANTES de qualquer modelo**. Tarefas 3.4/4.3
continuam pendentes; archive e gate final pós-archive não executados. O
attempt-log abaixo conserva o bloqueio HTTP 400 original, sem convertê-lo em
PASS por metadados ou por sucesso determinístico.

Apply novo `ses_def2616b1ffeSXukxzKlSu6sZ0`, proposta aprovada
`31cdb42b2d0e409e8820fa71d97177316c07f94a`, revisão independente informada pelo
coordenador `ses_def28f8abffeBio1TLgi1lXJaB`. Merge não forçado
`5b0fc0ad5ff553a0e091527ddff6ac4001b46dc4` preserva entrada `d34c1c1` e alvo
`12ca324faf2865faa62d16e55715d3ddd0adb53a`, incluindo os 38 commits anteriores.
Nove bytecodes ignorados sem proveniência ficam intocados. Instalador e
launchers são idênticos ao alvo: A_R1 `7c4cfb4433c4f56b9af463759e8215174b5b9663`,
B_R1 `a0806493280d062ae477a608ccdcc67a3ca337e5`, digest literal
`93cd9371b602a47c66b6bc3b20be448f6c124fc88b10a9f5d041f611dddc1a5f`.

### Provas focadas recuperáveis

- I1/D1: `evidence:ev-20261125T040028Z-81a71ed0` (distribuição) e
  `evidence:ev-20261125T040029Z-17cafeac` (launcher), exit 0 no merge.
- Fixture/detectores: `evidence:ev-20261125T040644Z-40022db6`, 18/18;
  reserva `evidence:ev-20261125T040645Z-f4f05567` e evidência
  `evidence:ev-20261125T040704Z-ff0058bc`, exit 0. São execuções durante
  implementação, não gates finais nem prova model-backed.
- Instalador inicial `evidence:ev-20261125T040711Z-a0eec998`: 54/55, falha
  de fixture introduzida por asserts OpenCode no helper agora compartilhado
  com Codex-only. Não é falha de produção nem o antigo problema XDG.
  Correção escolhe guidance/link do agente selecionado sem mudar instalador.
  Nova execução `evidence:ev-20261125T040830Z-3657e0de`, exit 0.

### Reconciliação antes da nova observação

Os comentários acessíveis relatam seq23 (T1, timeout externo após `--help`
iniciar modelo), seq28 (T7, formulário cancelado sem pergunta visível),
falhas posteriores de detector/instalador e observer `observe-61-d34c1c1`
sem recibo terminal. O attempt-log original não foi recuperado; **não**
recriamos suas sequências ou diagnósticos, não aprovamos episódios antigos
e não derivamos diagnóstico terminal da prosa `provider.no-route`.
Referências: [seq23](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6934965470),
[seq28](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6936198464),
[último preflight histórico](https://github.com/rocker-code/my-ai-skills/issues/61#issuecomment-6990765917).

Diagnóstico atual: camada **assertion/fixture** para descoberta, pergunta,
correlação e probes; **environment/bootstrap** para capacidade/isolamento.
Fase efetiva: descoberta/instalação → sessão nova → tool events → comparação
de snapshots, sem Apply de produção. Escopo: HOME/XDG/CODEX_HOME/DB
descartáveis; consumidores: harness T1/T5/T7, shim gh e instalador público.
Lifecycle: guard argv sai antes de executar; o writer é observado vivo e
esperado via `wait()`; cada modelo terá término explícito e timeout de grupo
de processos, nunca PASS por desaparecimento. A suíte offline referenciada
comprova guard, PATH/shim, negativos de receipt/native e archive, não quota
nem invocação de modelo. No preflight anterior, o runtime foi consultado isoladamente:
OpenCode 2.3.2 lista `opencode/glm-5.3-flash-free`; OpenSpec 2.1.1 está
presente. A listagem sem credenciais reais **não garante capacidade**.

Alternativa mínima: manter bloqueio e esperar evidência recuperável.
Escolha: uma observação nova e isolada do contrato reconciliado, somente
após preflight completo e HEAD limpo; não repetir automaticamente e não
trocar prompt natural T1 por lookup dirigido. Hipótese a verificar: fontes
atuais e skill tool fornecem prova nativa sem depender do ledger retirado.
Se não houver sinal/terminal/capacidade, reter UNKNOWN/bloqueio e não arquivar,
não abrir PR ou declarar suíte final. A revisão independente dos eventos
caberá a outro contexto real, nunca ao próprio Apply.

O bloco abaixo contém **somente tentativas novas com recibo acessível**, não
renumera nem substitui o attempt-log histórico perdido. Gate T1/T5/T7 continua
pendente até execução nova e conclusiva; `ready` estrutural não o aprova.

```attempt-log
{"attempt_log":1,"entries":[
{"kind":"attempt","seq":1,"obligation":"D1","signature":"fixture: missing opencode guidance in codex-only public install","target":"test_global_install.py","class":"fixture/isolation","hypothesis":"asserts de atualização OpenCode foram portados ao helper compartilhado sem seleção","change":"portar asserts de bytes/guidance","change_target":"test","observed_effect":"54/55; FileNotFoundError no AGENTS.md OpenCode em seleção Codex-only","result":"fail","evidence":["evidence:ev-20261125T040711Z-a0eec998"]},
{"kind":"attempt","seq":2,"obligation":"D1","signature":"fixture: missing opencode guidance in codex-only public install","target":"test_global_install.py","class":"fixture/isolation","hypothesis":"consultar guidance e link do agente selecionado preserva contratos de ambos","change":"selecionar paths OpenCode ou Codex no teste público, sem mudar produção","change_target":"test","observed_effect":"55/55, incluindo Codex-only, OpenCode-only e ambos","result":"pass","evidence":["evidence:ev-20261125T040830Z-3657e0de"]},
{"kind":"resolution","group":{"obligation":"D1","signature":"fixture: missing opencode guidance in codex-only public install"},"outcome":"passed","via_seq":2},
{"kind":"attempt","seq":3,"obligation":"setup","signature":"installer: gh missing from disposable path","target":"smoke_resume_candidate_opencode.py at 88171e3","class":"environment/bootstrap","hypothesis":"PATH filtrado inclui todas as dependências antes da instalação","change":"shim OpenCode isolado e fontes read-only","change_target":"test","observed_effect":"Falta gh no PATH; exit 1 antes de qualquer sessão/modelo; gh real reside no HOME filtrado","result":"fail","evidence":["evidence:ev-20261125T041342Z-1d01b591"]},
{"kind":"diagnosis","seq":4,"group":{"obligation":"setup","signature":"installer: gh missing from disposable path"},"class":"fixture/isolation","checked":{"phase":"preflight do instalador antes de qualquer execute_model","scope":"PATH do HOME descartável, não ambiente do operador","lifecycle":"exit terminal 1; nenhum JSONL/sessão de modelo","consumers":"install-global verifica which(gh); harness criava shim somente após instalar"},"runtime_proof":["evidence:ev-20261125T041342Z-1d01b591"],"simplest_alternative":"expor gh real do HOME, recusado para manter isolamento e evitar credenciais","choice_rationale":"antecipar o mesmo shim read-only já usado pela fixture satisfaz preflight sem mudar instalador","next_hypothesis":"setup completo com shim antecipado chega ao limite execute_model em prova determinística sem modelo"},
{"kind":"attempt","seq":5,"obligation":"setup","signature":"installer: gh missing from disposable path","target":"isolated installer + T1 fixture at a1e4789","class":"fixture/isolation","hypothesis":"shim gh antecipado conserva isolamento e permite preparação completa","change":"criar o mesmo shim read-only antes do preflight do instalador","change_target":"test","observed_effect":"exit 0; instalação real e fixture T1 preparadas, writer observado e esperado; limite execute_model interceptado sem modelo","result":"pass","evidence":["evidence:ev-20261125T041508Z-c662812e"]},
{"kind":"resolution","group":{"obligation":"setup","signature":"installer: gh missing from disposable path"},"outcome":"passed","via_seq":5},
{"kind":"attempt","seq":6,"obligation":"T1","signature":"provider.invalid-request: upstream request failed: model is unavailable","target":"opencode/glm-5.3-flash-free at 33e193565009f8da5744eda218878d6a9a3e847c","class":"environment/bootstrap","hypothesis":"modelo listado no runtime isolado aceita a observação após setup válido","change":"nenhuma mudança após diagnóstico/setup; uma observação sem fallback","change_target":"none","observed_effect":"HTTP 400 Model is unavailable; sessão ses_def153ec6ffevyM1h9hymDQ8O1, exit 1, zero tool calls; T5/T7 NOT RUN","result":"fail","evidence":["evidence:ev-20261125T041548Z-ed5ea997"]},
{"kind":"diagnosis","seq":7,"group":{"obligation":"T1","signature":"provider.invalid-request: upstream request failed: model is unavailable"},"class":"environment/bootstrap","checked":{"phase":"primeiro step do provedor antes de qualquer ferramenta","scope":"OpenCode 2.3.2 standalone; HOME/XDG/DB novos, sem credenciais do operador","lifecycle":"sessão nativa criada, erro terminal 400 e exit 1; nenhum timeout ou retry","consumers":"modelo público listado, instruções globais e skills carregadas no instruction_state da mesma sessão"},"runtime_proof":["evidence:ev-20261125T041548Z-ed5ea997","evidence:ev-20261125T041711Z-36eb7ff7"],"simplest_alternative":"consultar suporte/capacidade real do provedor antes de nova observação; não editar aplicação ou enfraquecer detector","choice_rationale":"listagem confirma descoberta, mas evento terminal nega disponibilidade; causa interna do provedor não é demonstrada","next_hypothesis":"somente nova disponibilidade comprovada ou seleção explicitamente fundamentada de runtime/modelo permitirá nova tentativa limitada"},
{"kind":"blocker","seq":8,"group":{"obligation":"T1","signature":"provider.invalid-request: upstream request failed: model is unavailable"},"type":"technical","wait_reason":"external","evidence":["evidence:ev-20261125T041548Z-ed5ea997","evidence:ev-20261125T041711Z-36eb7ff7"],"diagnosis":"seq:7","options":[],"impact":"T1 bloqueado; T5/T7 não executados; sem archive, suíte final de entrega ou PR","researchable":false},
{"kind":"resolution","group":{"obligation":"T1","signature":"provider.invalid-request: upstream request failed: model is unavailable"},"outcome":"blocked","via_seq":8}
]}
```

### Observação atual bloqueada e Verify nativo

Somente **uma** sessão model-backed foi iniciada nesta recuperação, no
`33e193565009f8da5744eda218878d6a9a3e847c`. O setup falho anterior não
iniciou modelo. O log checksum-bound
`evidence:ev-20261125T041548Z-ed5ea997` contém os JSONLs, recibo terminal e
recibo independente do processo cooperante; não depende somente de `/tmp`.
JSONL SHA-256 `1eb988d9d26c5192b8ce9ff1a0e06c320c074d7e336c0c216d302b5c0cd20f02`.
A leitura read-only do DB **isolado** em
`evidence:ev-20261125T041711Z-36eb7ff7` vincula a sessão ao guidance
`resume-workflow`, cinco skills oficiais e AGENTS carregado por
`instruction_state`/`instruction_blob`; isso **não** prova invocação nativa.
O callback HTTP 400 atual é factual e diferente do observer antigo UNKNOWN;
não é 429 e não contém retryAfter ou diagnóstico de quota.

Verify oficial invocado nesta sessão por `openspec-verify-change`, origem
`.agents/skills/openspec-verify-change/SKILL.md`, após integração; OpenSpec
2.1.1, sem init/update/habilitação global. `status`/`instructions apply`
resolveram este root e os cinco artefatos. Strict do change: **1/1 PASS**.

| Dimension | Status |
| --- | --- |
| Completeness | 13/16 antes desta Verify; cinco requisitos mapeados ao código. Tarefas 3.4/4.3 incompletas; 4.4 satisfeita pela invocação/relatório/strict, não por sucesso dos smokes. |
| Correctness | Mapeamento estático e 18 regressões offline conferidos. Cenários T1/T5/T7 reais **Not verified**: primeiro modelo indisponível antes de ferramenta; não pontuar como PASS. |
| Coherence | Merge/pins/remoções/fontes read-only/archive resolver conferidos; não há novo framework de produção. Revisão independente dos novos eventos não realizada pelo próprio Apply. |

**CRITICAL — completar antes de archive:** tarefas 3.4 e 4.3 em
`openspec/changes/issue-61-opencode-safe-resume/tasks.md:22,30`. Após superar
o bloqueio externo, exigir T1/T5/T7 completos e dois turnos do mesmo ID em T7,
com snapshots por fase e revisão independente. Não marcar por prosa.

**WARNING — limite histórico de prova da falha:** `execute_model` terminou antes de
`results.json` ser preenchido (`tests/smoke_resume_candidate_opencode.py:771`).
Existem terminal/eventos/DB/receipt, mas não snapshots pós-fase completos
desse run. Não reconstruir um snapshot anterior por inferência. Antes da
próxima observação, preservar também a preparação antes de chamar modelo.

Mapeamento: recuperação/escopo/UNKNOWN em `skills/resume-workflow/SKILL.md:8-20`;
preservação e receipt em `tests/smoke_resume_candidate_opencode.py:96,160,270`;
native skill/event/hash em `:292`; escolha/probes/mesma sessão em `:359,422,501`;
archive em `:188`; distribuição em `tests/test_global_install.py:648`.
Negativos e fontes read-only em `tests/test_resume_reinventory.py:245-521`;
reserva/evidência existentes cobrem crash/ownership/stale/incomplete.

**Resultado:** dois achados críticos de completude e uma limitação de
captura; cenários model-backed não verificados. **Não pronto para archive
ou PR**. Archive/sync e gate final pós-archive **NOT RUN**, sem dispensas.

## Histórico — 16/11/2026 (não é gate atual)

Execução em 2026-11-16 com OpenCode v2.3.0, OpenSpec 2.0.0 e modelo
`opencode/glm-5.3-flash-free`; pacote instalado em HOME descartável a partir do
commit candidato `80e5de0dd4351770b61941cda7dfc798b14ed7ac`. A skill carregada
`resume-workflow/SKILL.md` teve SHA-256
`dc789b2bb73d04d1719a6397bfb4abe3a317e8dc343aa0607e76025f4876a5be`.
Comando: `PYTHONDONTWRITEBYTECODE=1 python3 tests/smoke_resume_candidate_opencode.py`.
Este teste **não** substitui `tests/smoke_global_opencode.py`, que instala
`c48ac58beadc0a9712f59f60458a5c3df3ed5bfb`.

Os prompts, respostas completas, inventários antes/depois, IDs de sessão e
eventos JSONL permanecem em
`/tmp/opencode/resume-candidate-zwjamu21/results.json` e arquivos
`T{1,5,7}-events.jsonl` no mesmo diretório. Cada sessão invocou a skill
`resume-workflow` via ferramenta real do OpenCode; todas terminaram com exit 0
e resposta gerada pelo modelo. As fixtures e o HOME são descartáveis: nenhum
recurso GitHub real foi criado ou modificado. O executável `gh` da fixture
responde somente a leituras de issue/PR e recusa escritas.

| Cenário | Prompt enviado | Sessão | Inventário antes/depois e resposta observada |
| --- | --- | --- | --- |
| T1 | “Continue de onde parou nesta issue. Consulte evidências duráveis locais e OpenSpec; diga o último gate comprovado e a próxima ação. Esta prova é somente leitura: não inicie Apply nem crie branch, worktree ou change.” | `ses_e1cd1d48cffe8apOOYwwPZyuZS` | HEAD `47b9c27f933a0054ecbb59e9e3fd255007373678`; único branch/worktree `master`, status limpo, seis arquivos de change iguais antes/depois. Resposta identifica issue 61, run `wf-disposable-t1`, revisão de proposta validada `d9fdea7bd3613e12d6953acd7f0abbf7e9557668`, `proposal_review` verificado e Apply como próximo gate; nenhuma branch/change/worktree nova. |
| T5 | “Retome este milestone após interrupção. Reconstitua PR, dependência e merge mode da evidência persistida; indique a próxima ação sem agendar o consumidor. Prova somente leitura, sem operações GitHub de escrita.” | `ses_e1cd0067cffefMr9NYjOF6LSih` | HEAD `7a1542d9b84a7c42e9f0a1c9ca26f94b631eb42a`; único branch/worktree `master`, status limpo e nenhum change antes/depois. Resposta preserva milestone 3, merge `manual`, PR fixture #12/head `disposable-pr-head`, `pr_audit` pendente e issue dependente #13 bloqueada até merge; nenhum despacho. |
| T7 | “Continue de onde parou. Há duas execuções candidatas neste checkout. Use evidências duráveis e, se ambíguo, faça só a pergunta necessária. Prova somente leitura, sem escolher pela recência.” | `ses_e1ccd5d5dffeK8zwNB9k5cd89t` | HEAD `513c913922357d20da1acb1925c8bea05a514c84`; único branch/worktree `master`, status limpo e nenhum change antes/depois. Resposta apresenta runs `wf-disposable-a`/issue 21 e `wf-disposable-b`/issue 22, pede escolha; ferramenta `question` tentou perguntar, mas a execução CLI não interativa cancelou o diálogo. Nenhuma escolha/escrita. |

O inventário também compara a lista de arquivos rastreados e de change, HEAD,
branches, worktrees e `git status --porcelain` byte a byte entre os dois
momentos (`unchanged=true` em todos). O PR e a dependência de T5 são **fixture
controlada**, não confirmação de um PR real no GitHub. O diretório de prova é
local; quem revisar em outra máquina deve solicitar um pacote íntegro dos
eventos antes de tratar o transcript como prova transportável.

## Gate local pendente

No commit candidato acima, o gate preliminar
`python3 -B -m unittest discover -s tests` executou **252 testes,
6 falhas**, evidência local `ev-20261116T071456Z-0bbc6082`
(`verified/failed`). Três falhas do instalador foram reproduzidas no
`fd46eb01eda15e772a83d02fde46616d20176bef` base com a mesma versão do
OpenSpec: ausência de comandos/skill gerados pelo `openspec init` e digest
publicado do instalador divergente. As três falhas adicionais do launcher
também decorrem do digest divergente no candidato; ainda requerem comparação
de base se alguém pretender classificá-las formalmente. Falha pré-existente
**não** aprova o gate. Archive/sync, PR e validação final permanecem pendentes;
não alterar checks ou infraestrutura de outra issue para aprovar #61.
