# Prova isolada de retomada — issue #61

## Recuperação atual — 25/11/2026

### Apply offline a0b4796 — capacidade Verify exclusiva de T5

Emenda aprovada `a0b4796fb1a2646125c6e62bfa6ca450d2118e7e`, Apply novo
`ses_ded18b05dffeNzCsA3V4E54qkk`, mesmo checkout/branch/run, sem nova integração,
modelo, archive, push, PR ou merge. Política atual do checkout prevalece sobre
o pacote global anterior a #75/#76; nenhum audit/ready/ledger foi restaurado.
Somente 3.9 é implementada; 3.4/4.3 e fechamento integrado permanecem pendentes.

**Delta material, não “permissões inalteradas”:** somente perfil descartável T5
acrescenta `skill/openspec-verify-change/allow`, ao lado de resume/Explore/Apply.
T1 conserva as regras anteriores; T7 conserva ambas as fases e rejeita Verify/
Apply em qualquer status mesmo junto de Explore válida. Todas as regras não-skill,
prompts, guard raw/cwd/ambiente, FS/read/write/MCP, fontes PR/manual/dependência,
recibos e classificadores stateful permanecem idênticos. `allowed-tools` não é
concessão de recursos. Guard integral preservado:
`b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`.

**Fonte canônica:** `.agents/skills/openspec-verify-change/SKILL.md`,
SHA-256 `3b86fbb9734fdb6b942dd12d0afa4247457aa7f212bb48832eae133f5e66880a`.
Confirmado contra `getSkillTemplates(['verify'])`, `generateSkillContent`,
`stripVolatileFrontmatter` e `transformToSharedSkillReferences` do pacote oficial
OpenSpec2.1.1 instalado, sem gerar/substituir arquivo de runtime ou atualizar
perfil. Ausência, symlink, versão não suportada ou bytes divergentes bloqueiam
a capacidade sem fallback. O mapa T5 registra origem/arquivo/hash/gerador;
binding futuro preserva perfil/config, árvore preparada/instalada, fonte e
evento realmente invocado/sessão/catálogo, sem alterar a regra F1.

**Prova, não resposta calculada:** Verify precisa de catálogo realmente entregue
e dispatch nativo `skill` concluído, corpo/path/hash/sessão/step corretos e strict
aplicável ao root/change. Arquivo/CLI/listagem/catalog-only, failed/cancelled e
origem/sessão/root/change errados não substituem dispatch. A fixture continua
no commit real de proposta, com tarefas normalizadas pendentes; relatório
honesto incomplete/not verified é adequado à inspeção, não aprovação da
implementação ou prontidão de archive. PR/head/checks/manual/dependência,
snapshots/recibo e recusa de tentativa stateful continuam obrigatórios.

**Offline focado:** `ev-20261125T133817Z-03693f52`, 64/64, após corrigir somente
fixture unitária que omitia os contêineres `pulls/issues` (primeira execução
`ev-20261125T133631Z-644ff2c3`, KeyError, 64 testes/1 erro). Positivos sintéticos
de captura não são observação nativa. Negativos incluem a tentativa real
stateful verify19 preservada, além de T7 Verify/Apply em todos os status.
Rechecagem da fonte offline final `ev-20261125T134603Z-5c4531a2`: 64/64;
suíte preliminar `ev-20261125T134630Z-326cdee8`: **320/320**, 67,655s,
verified/passed/no_required_gate antes do commit, não gate de entrega.
Strict oficial: change **1/1**, global **13/13**; diff check e attempt-log
estrutural válidos (história nativa ainda BLOCKED). O recibo de suíte após
commit limpo fica fora deste documento/commit para evitar commit só de IDs.

**Diagnóstico de dois probes auxiliares, antes de nova execução offline:**
`ev-20261125T133957Z-e3384624` falhou por presumir advertisement a partir do
GET `/api/skill` antecipado ([] em T1, builtin-only em T5);
`ev-20261125T134147Z-80b70a25` falhou por presumir que permissões configuradas
seriam o sufixo completo do agente. Fase: API/debug sem prompt, antes de entrega
ao modelo; escopo: HOME/XDG/DB/roots novos e privados, não o operador.
Lifecycle: subprocessos terminaram normalmente, sem inferência ou worker nativo
T1/T5/T7; consumidores: somente script externo de prova, nenhuma mudança de
produção/guard. Os dumps retidos mostram o bloco exato configurado seguido por
dois denies nativos browser/browser-skill. Alternativa conservadora é manter
advertisement/delivery não comprovados; correção escolhida compara o bloco
contíguo e esses denies explícitos via debug settled, preserva o GET bruto como
antecipado e exige zero mensagens/tokens. Não converter essa evidência em
delivery/dispatch, não alterar provider/config/timeout para contornar a falha.

**Recibo corrigido** `ev-20261125T134343Z-9f1e91b9`: geração oficial e três
commits Git reais de proposta, strict/context/list/Apply ready com 0/19
concluídos, comparação byte-a-byte de regras e código preservados. Debug settled
OpenCode2.3.2 confirma Verify **deny/allow/deny** em T1/T5/T7 respectivamente.
Sessões apenas metadata `ses_ded0d5162ffe7F4bFyD4TXBoyy`,
`ses_ded0d4c1affeVBot6ZKMwwrKtx`, `ses_ded0d46f6ffeW1yUDFgpVs29q5`:
zero mensagens/tokens/custo. GET bruto não prova advertisement entregue;
captura de catálogo rejeita corretamente essas sessões sem assistant. Nenhum
dispatch skill/modelo/command bridge foi executado: fonte+config settled+testes
provam somente preflight, não comportamento integrado.

Os onze runs inteiros continuam **FAILED**, T7 **NOT RUN**; omissões anteriores
não tiveram tentativa Verify e não provam causalidade exclusiva da exclusão.
T1 anterior aprovado vale só nos inputs observados, sem modificar manifesto/
pending fields. Esta mudança material exige revisão afetada e autorização
separada do pai antes de **novo harness real completo T1/T5/T7**. Suíte completa
offline deste Apply será prova pre-smoke, nunca gate final de entrega: gate
final continua no HEAD limpo exato após archive/preparo/todos os commits.

### Décima primeira observação — override DeepSeek real, mesma omissão nativa T5

Experimento **novo explicitamente autorizado pelo pai**, um harness completo,
sem fallback automático: HEAD limpo instalado/observado
`930b1bcf701e0e2a188a2715b4ca53ce89650734`, fonte/guard/pins byte-idênticos à
revisada703ffb9, proposta aprovada `e1408dafbb7c6b2251b206afe62a2785708d1e08`.
Worker real `ses_dee5e0a18ffefE7FomnYJ9smc1`, stage
`observe61-deepseek-override`, mesma issue/branch/checkout/run, reserva própria
verify/checkpoint sem drift, nove ignorados preservados. Check não final pré-launch
valid=true/violations=[]/ready=null; diagnóstico seq51 lido, história não reiniciada.
Metadados privados `ev-20261125T124817Z-20b151f6` fundamentaram apenas a seleção
administrativa do novo modelo, nunca disponibilidade ou PASS.

**Uma chamada completa** `python3 -B tests/smoke_resume_candidate_opencode.py`,
com `env["RESUME_SMOKE_MODEL"]="opencode/deepseek-v4.1-flash-free"` explícito,
sem pop, selector, prompt padding ou patch da fonte. HOME/XDG/config/CODEX_HOME/
DB novos e privados, sem credenciais de operador; guard raw original fresh ativo,
fonte `b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`.
OpenCode2.3.2/OpenSpec2.1.1, interno360s/externo1.800s preservados.
Callback real `sh_212c703650014BjSNvmvlvqd2x` **exit1**; nenhum timeout/cancel.
Reter artefatos próprios via execution.log, sem --output-dir externo.

**Modelo efetivo comprovado**, não apenas solicitado: preflight fresco em T1
e T5 com source **RESUME_SMOKE_MODEL**, uma linha exata ativa/enabled/chat/tools,
input text+image/output text, um tier com input/output/cache read/write0.
Default contextual big-pickle não foi selecionado. Todos os **20 assistants**
do DB nativo (8 T1/12 T5) registram providerID opencode/id deepseek-v4.1-flash-free,
variant default do runtime, sem override de variante. Recibo read-only
`native-assistant-models.json` com IDs/hash dos dados brutos/tempo/tokens/custo;
SHA-256 `b9c7fdffa7c6fb241c48d409377ad7dcde95ef898e041510ee5fc0c328009cee`.
Nenhuma rota Tidepool/paga, auth import ou default global modificado.

**T1:** `ses_ded38ec4cffeYMkMO5YUGlftet`, PID1751971, terminal0 em
`2026-11-25T12:58:09.166281+00:00`, sem malformed/error events, stderr vazio.
48 eventos/8 step_finish/30 tools, custo reportado0. Nove fatos true,
prior-stopped-owner before-write corroborado, serialização passed,
proof_complete=true, mas **pending_independent_review/scenario_pass=false/
write_authorized=false**. Apply nativa37, strict33/CLI Apply34, receipt18,
inventário17/19–23, proposta/ancestralidade/review/diff26–27/30–32, GitHub38 e
handoff46 efetivos. Proposta fixture `3771f1b736da17ca5c2dfbfe8a64ee36f81d7c00`,
review `5d690df89a73956576e25554f650a044e35aafe6`, não aprovações reais.
Oito snapshots iguais e pré-requisitos físicos/Git verified=true antes/depois.
Nenhuma tentativa stateful; probes shell5/6 e reads9/10/13 negados, incluindo
read externo10, permanecem no original; snapshot igual não apaga essas tentativas.
Writer `writer-T1-61/seed-T1/wf-disposable-t1`, PID1750845, observado vivo e
terminal0 correlacionado ao checkout T1-issue-61. Aprovações T1 antigas não
substituem revisão desta resposta, inclusive seus limites textuais preservados.

**T5:** `ses_ded36fea1ffeUJ8eNr61DIvTiV`, PID1790205, terminal0 em
`2026-11-25T13:00:42.139052+00:00`, sem timeout/malformed/provider error,
stderr vazio. 65 eventos/12 step_finish/32 tools, custo reportado0.
Manifesto2, seis fontes GH9–14 exit0/não truncadas: disposable/recovery milestone3,
issue11/PR12/head `fb9ebc519fba3784dcea18f5d91bc02deef22f11`, checkSUCCESS,
manual/dependente13 bloqueado; t5_sources diagnóstico=true/outcome=true.
Inventário18–23/receipt24 efetivos; writer `writer-T5-11/seed-T5/wf-disposable-t5`,
PID1789060, observado vivo e terminal0. Sete snapshots iguais,
forbidden_attempts=[]/write_authorized=false, nenhum read fora de escopo/probe
ao produtor. Resposta63 mantém revisão da PR existente/manual/consumidor bloqueado,
divulga head de checkout diferente sem reivindicar merge ou conclusão.

**Mesma falha de obrigação/assinatura seq50, agora pela segunda vez**:
RuntimeError2438, `T5 phase 1: recovery proof incomplete`, statusfailed/
proof_complete=false. Único tool skill T5 **resume-workflow5**. Verify30 é
read de arquivo canônico, não invocação; list35/strict40 são CLI, não tool nativo.
Catálogo entregue realmente contém resume/explore/apply; Verify tool é default-deny.
Nenhuma tentativa de invocação OpenSpec, em qualquer status. Logo fonte nativa
selecionada/binding source=null e matcher discovery/invocation/instructions=[],
sem apagar strict40 nem retroinserir a skill meramente lida.

Status33/instructions36 receberam aspas não publicadas em torno do change e foram
negados **pré-spawn** pelo guard raw, sem demonstrar indisponibilidade dos locators
exatos sem aspas. Probes Git43/44/46–49 e read .git60 também negados; não ampliar
comandos/permissões/timeout para apagá-los. O novo modelo produziu a mesma omissão
observável, mas isso não prova causa exclusiva/bug de router/matcher ou justifica
fix de código/gate/prompt. **T7 NOT RUN**: nenhum turno/ID/escolha/capture inventado,
nenhuma continuação externa ou décima segunda inferência.

**Lifecycle/custo:** DB nativo termina IDLE succeeded para ambas as sessões,
clientes1751971/1790205 e writers1750845/1789060 ausentes em /proc após terminais;
nenhum kill/cancel/restart/limpeza de DB. Somas de contadores dos assistants
(não fatura liquidada): T1 input53833/output3391/reasoning6953/cache read80896;
T5 input39537/output4199/reasoning7870/cache read235648; cache write0 e custos
reportados0 em ambos. Custo final liquidado pelo provedor **UNKNOWN**.

Bindings preparados resume-effective-inputs-v1 conferidos válidos:
T1 `321cbab62c9ecc7e7c3ca9cc41186d439e5b7d3bf6fe83970001804654249591`,
T5 `821b5222413b11593a517773be3efb2ebdcb51103bd6a9dc743246f1dc9ac6c4`.
Execuções/catálogos reais capturados sem edição. Snapshot before=after T1
`1becc8600e64e1db3bb3b03b32c0b6166ab7d07101897f210d105e78fd9c3ee9`,
T5 `24c72a024a217cbdae6b5d565f6996187c14a496d0449d555e9243411b9bd1e0`.
Modelo é input material; T7 ausente impede whole F1 apesar dos fatos T1.

**Prova original** `evidence:ev-20261125T125602Z-c3f672d3`, verified/failed
antes desta retenção, no_required_gate. Log **1.605.880 bytes**,
SHA-256 `d09132e859f6d5ddea2b175886b940b97d83d3920b220d897248e66e8441204d`,
final `2026-11-25T13:00:42.511432Z`; tool opencode2.3.2/openspec2.1.1,
sandbox observe61-930b1bc-deepseek-ses_dee5e0a18ffe e model-override
opencode/deepseek-v4.1-flash-free. Originais em
`/tmp/opencode/issue61-observe-930b1bc-deepseek-ses_dee5e0a18ffe/`.
Results `5f146e9b97ba13f3402748bbe4f70c300c79e0a033bda282e484e6c646a606fb`;
T1 JSONL `1707444a0e7fc34e0bd297aac09546fc496ddb0750062dab021df78972eb918a`,
terminal `a1c0f33a18b81f1539f1b024131308ca544e38e74429bf456d43a84974940830`;
T5 JSONL `adfb67b07e2ecf178cf3db9ac528d5881c0cd35c0d930af4f2b9555d09cf3e50`,
terminal `1610da1052545f71d5d2ce7ba7fd97f7a977095995409fad7cc353afd532f9bd`.

Parada factual sem autocorreção/retry/outro modelo, source/guard/pins/registro
original alterados, archive/sync/final unit gate/PR/push/merge/tag/release.
Seq53–55 acrescentam tentativa, diagnóstico completo pós-segunda falha e bloqueio,
sem reset/resolução dos dez runs anteriores ou dos recibos de metadados.
Próxima ação mínima: revisão independente do trace/modelo realmente usado e da
mesma omissão nativa, com decisões posteriores separadas; nenhum novo experimento
autorizado. Closeout previsto somente documental: commit desta retenção, verify
e release WAITING confirmados pelo callback, mantendo final readiness false.

### Um GET de catálogo privado — ausência exata de Tidepool comprovada nesta resposta

Autorização separada somente para **um** GET `/api/model`, sem default reread,
refresh, fallback ou inferência. Entrada limpa `acd7f2188cf15a4f7bfcbd980fd5a28e5f2bda94`,
mesmo worker `ses_dee5e0a18ffefE7FomnYJ9smc1`/issue/run, stage
`metadata61-one-catalog`, reserva própria verificada sem drift. O diagnóstico
independente `ses_ded47d8eefferzm2mJPYKxv6mt` informa parser oficial correto:
envelope location/data, array de modelos habilitados/chat, match providerID/id;
o wrapper anterior perdia projeção/count no reject. Nenhum bug de fonte provado.

OpenCode **2.3.2**, perfil existente
`/tmp/opencode/issue61-metadata-tidepool-ses_dee5e0a18ffe-profile/`,
Location exato `T5`, HOME/XDG/config/DB/guard/permissões originais preservados.
Override process-local somente como candidato: `opencode/tidepool-alpha-free`,
source RESUME_SMOKE_MODEL; nenhum modelo selecionado para execução.
GET em `2026-11-25T12:48:17.506534+00:00`, resposta
`12:48:18.208140+00:00`, **exit0**, stderr vazio; `{location:object,data:array}`
com root keys data/location e Location conferido. Projeção não secreta persistida
**antes** do julgamento, limite100, **sem truncamento**.

**12 linhas**, provider opencode=12/type chat=12; **0** matches canônicos da
referência exata e **0** matches diagnósticos por modelID; **0** refs duplicadas.
Logo Tidepool está ausente **nesta resposta completa**, não ambíguo. Não recuperar
retroativamente as linhas perdidas do GET anterior nem deduzir causa de cache.
Suas capacidades/preços locais continuam UNKNOWN; candidate_metadata_eligible=false.
As 12 refs efetivamente retornadas, todas prefixadas `opencode/`, são:
`big-pickle`, `deepseek-v4.1-flash-free`, `glm-5.3-flash-free`, `hy4-flash-free`,
`iceman-free`, `inkling-2-small-free`, `longcat-2.5-free`, `flint-40b-free`,
`nemotron-3.5-super-vl-free`, `beam-free`, `mimo-v2.6-flash-free`,
`nemotron-3.5-lightning-free`. Todas têm enabled=true **literal**, status active,
type chat, tools=true, text input/output; cada uma tem **um** tier completo com
input/output/cache read/write **0**. Isso é elegibilidade de metadados, não
acesso/inferência ou escolha de alternativa. Nenhum preço veio de listagem global.

DB antes/depois: sessions/messages/parts/user/assistant/credential **0**; requests
generate/completion/tokens/custo registrado **0**. Exatamente um GET de catálogo,
zero GET default, sem outros model routes. Cliente1611867 e version1611857
terminaram0, PIDs ausentes; guard setup/disposed, sem kill/restart global.
Nenhuma credencial importada/consultada. Sem refresh explícito ou espera por
refresh; cold-cache/bundle/refresh assíncrono permanecem hipóteses, não causas provadas.

Prova `evidence:ev-20261125T124817Z-20b151f6`, **verified/passed/no_required_gate**
da observação de catálogo, distinta do candidato bloqueado. Artefatos no perfil,
`one-catalog-projection/catalog-projection.json` e `catalog-verdict.json`.
SHA-256 projeção `4c88f1a182f65c25c9a015b49488268a7cdd3d437decbca054414c923cf1cd7d`;
verdict `af28dce8b7d43dd565094650520a26f97be479418949678087aff93197661935`;
JSON root completo (sem dump de campos desconhecidos)
`ee02067900be4879b8cd5a3b27efc13a2a91ab628b998bd0a7261350d2cb3ba5`.
Próxima ação é decisão **separada do pai** sobre os fatos/refs retornados, sem
selecionar rota, registrar modelo ou executar experimento automaticamente.
Fonte/guard/pins e todo histórico FAILED/T1 aprovado nos inputs antigos/T5 sem
dispatch/T7 NOT RUN/F1 pendente intactos; final readiness false. Closeout previsto:
commit só desta nota, verify e release WAITING confirmados pelo callback, sem
suíte completa, modelo, archive/PR/push/merge.

### Revisão independente do décimo trace e preflight somente de metadados

O coordenador informa revisão independente de
`ses_dee9d76e4ffeR10I59JewObvEC`: **T1 aprovado somente nos inputs observados
703ffb9**, sessão `ses_ded625d95ffelT8lOw69u3ftnR`, com nove fatos, condição
tipada, serialização e handoff de posse seguros. Não reescrever os campos
originais pending_independent_review/scenario_pass=false. Para T5
`ses_ded609cceffe7kZ16usqNCOvbN`, fontes PR/head/manual/dependência e inventário
aprovados, mas skill2 foi apenas resume-workflow; Verify35 é leitura de arquivo,
strict48 é CLI e native_source=null continua correto. O catálogo/permissões
permitiam resume/explore/apply; Verify era default-deny como skill embora seu
arquivo canônico fosse legível. Não é quebra de perfil “quatro versus cinco”.
Prompt/adaptador/contrato já exigem dispatch real: a revisão classifica omissão
do modelo e divergência arquivo/capacidade, **sem correção de implementação
justificada**, sem relaxar gate, acrescentar Verify, forçar Apply ou inflar prompt.
Clientes nativos anteriores completos/idle succeeded, custo final liquidado
UNKNOWN; steps0 não são liquidação. Décimo run inteiro permanece FAILED,
seq50–52 intactas e T7 NOT RUN. Não há PASS F1 por aprovação de subcenário.

**Nova autorização administrativa, sem inferência:** entrada limpa
`5522981a0ec735ac8f2bb3243f41893c283733fa`, somente documentação desde
`703ffb979b21b94fbcd830f7cac3bdba0f725220`; worker real
`ses_dee5e0a18ffefE7FomnYJ9smc1`, stage `metadata61-tidepool`, mesmo run/issue/
checkout. WAITING ownerless reservado/verify/checkpoint sem drift, nove ignorados
preservados. Nenhuma nova tentativa nativa/alteração de orçamento do attempt-log.
O pai selecionou **somente para verificar metadados**
`opencode/tidepool-alpha-free`; sua listagem global não comprova esse perfil.

Wrapper temporário próprio, sem patch de fonte, bloqueia main/prepared_phase/
execute_model e subprocessos fora da allowlist. Usa o **model_preflight existente**
com override process-local `RESUME_SMOKE_MODEL=opencode/tidepool-alpha-free`;
nunca strip/fallback/variante/troca do modelo do coordenador. Instalação privada
exata5522981, HOME/XDG/config/CODEX_HOME/DB novos, sem importar auth/config do
operador. Permissões T5 idênticas após rebasing dos paths/revisão próprios,
guard original fresh ativo/disposed. OpenCode2.3.2/OpenSpec2.1.1.

**Resultado BLOCKED, não metadata-eligible:** os únicos GETs nativos foram
`/api/model/default` e `/api/model`, standalone no Location privado T5,
ambos exit0. model_preflight rejeitou:
`selected model absent/ambiguous in native catalog`.
Não foi estabelecida uma única linha local da referência exata. O wrapper não
reteve a projeção/count rejeitados; **ausente versus ambíguo continua inconclusivo**,
sem nova consulta para distinguir. enabled/active/tools/text e todos os preços
da alternativa ficam **UNKNOWN neste perfil**, sem transportar zeros/capacidades
do catálogo global. Nenhuma segunda rota, retry ou probe de token/inferência.
O default/binding/resultados antigos big-pickle permanecem imutáveis.

**Prova negativa de inferência:** DB privado read-only com session_v2,
session_message, session_part, user, assistant e credential todos **0**;
nenhum endpoint generate/completion chamado, zero tokens/custo de inferência
registrados. Isso não é disponibilidade de provedor nem teste comportamental.
Os sete processos de preparo/versão/guard/APIs retornaram0 e seus PIDs já
ausentes; guard audit contém três setup/disposed. Sem restart global, limpeza,
kill ou sessão modelo. Credencial de serviço privado gerada localmente não foi
retida; nenhuma credencial de operador lida/importada.

`evidence:ev-20261125T123047Z-cacbb737`: metadata-only **verified/failed**,
no_required_gate, não execução nativa substituta.
`evidence:ev-20261125T123238Z-53b019a3`: retenção/diagnóstico read-only
verified/passed/no_required_gate, confirma DB zero, fontes/guard/pins byte-idênticos
e log original `ev-20261125T121046Z-f787388b` intacto
(1.586.873 bytes, `ec613943a4bde9577638e4f669eccd116bcc06bee17fa0c35478da0b6b51b841`).
Artefatos próprios em
`/tmp/opencode/issue61-metadata-tidepool-ses_dee5e0a18ffe-profile/`:
`metadata-result.json` e `metadata-retention.json`, wrapper/log/hash vinculados
ao segundo recibo. Nenhum campo antigo foi retroinserido.

Não propor inferência futura enquanto a elegibilidade local estiver inconclusiva.
Se o pai decidir investigar a discrepância de catálogo, isso requer direção
separada, sem fallback automático. Qualquer experimento futuro com novo modelo
é input material: exige autorização separada, preflight local conhecido zero e
**novo T1/T5/T7 completo**, registrando ref exata/source RESUME_SMOKE_MODEL no
binding resume-effective-inputs-v1 real. Esta checagem não criou esse binding
nativo nem dispensa F1/revisão/suíte final futura. Apenas anotação documental;
final readiness false/T5 e T7 nativos não comprovados. Closeout documental previsto:
commit somente desta nota e liberação ownerless WAITING após verify, a confirmar
pelo callback real; sem décima primeira inferência, suíte completa, archive/PR/push/merge.

### Décima observação autorizada — T5 sem invocação nativa, T7 NOT RUN

Autorização nova explícita, após revisão independente da correção material
T5/T7 por `ses_dee9d76e4ffeR10I59JewObvEC`, limitada a uma observação completa,
sem closeout. HEAD limpo instalado/observado
`703ffb979b21b94fbcd830f7cac3bdba0f725220`, proposta aprovada
`e1408dafbb7c6b2251b206afe62a2785708d1e08`. Worker real
`ses_dee5e0a18ffefE7FomnYJ9smc1`, stage `observe61-native-gates`, mesmo
checkout/branch/issue/run. Reserva WAITING ownerless adquirida, verify/checkpoint
confirmados sem drift; nove ignorados preservados. Check não final antes do
launch valid=true/violations=[]/ready=null, sem resolver histórico bloqueado.
Provas no HEAD exato reverificadas verified/passed/no_required_gate:
`ev-20261125T120034Z-21120ae1` (316 testes),
`ev-20261125T120034Z-e2c1e3f6` (60 focados),
`ev-20261125T120034Z-726b5be4` (strict13/13),
`ev-20261125T120034Z-fea06b0c` (change1/1),
`ev-20261125T120034Z-43e45654` (diagnóstico/11 negativos).
Não são suíte final nem aprovação nativa.

**Uma chamada completa**, `python3 -B tests/smoke_resume_candidate_opencode.py`,
PYTHONDONTWRITEBYTECODE=1/RESUME_SMOKE_OUTPUT único, sem --output-dir externo.
Callback `sh_2129d92e9001DtET7Jx2E6Ruz1` **exit1**, evidência encerrada em
`2026-11-25T12:13:48.060320Z`. Timeout externo1.800s/interno360s preservados;
nenhum expirou. HOME/config/XDG/CODEX_HOME/DB privados novos, sem auth de operador.
OpenCode2.3.2/OpenSpec2.1.1, guard fresh ativo em T1/T5 com fonte
`b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`.
Default nativo fresco `/api/model/default` cruzado com `/api/model` escolheu
`opencode/big-pickle` separadamente nas duas fases, enabled/active/tools/text e
input/output/cache read/write conhecidos zero. Sem override/fallback pago.

**T1:** sessão `ses_ded625d95ffelT8lOw69u3ftnR`, PID942840, terminal0 em
`2026-11-25T12:12:41.383361+00:00`, sem timeout/error events/JSONL malformado.
57 eventos/12 step_finish/32 tools; custos dos steps reportados0.
Nove fatos true, condição tipada before-write/prior-stopped-owner corroborada,
serialization_compliance=passed/proof_complete=true, mas
**pending_independent_review/scenario_pass=false/write_authorized=false**.
Discovery real25 e catálogo entregue; Apply nativa33, CLI Apply19/strict30,
receipt18, inventário22–23/26–29, proposta/ancestralidade/review/diff13–17 e
GitHub44 antes do handoff55. Ordem bruta preservada, sem exigir repetição de CLI
após skill em T1. Proposta fixture `d8888d23046877b5a53c5db2533c885b62dc541d`,
review `b039cf7d31b6b074570779b0c8539eafe5b50750`, não aprovações reais.
Writer `writer-T1-61/seed-T1/wf-disposable-t1`, PID941615, observado vivo e
depois terminal0, checkout T1-issue-61. Oito snapshots iguais, pré-requisitos
de artefatos verified=true antes/depois. Nenhuma tentativa stateful; read36 do
diretório pai externo foi negado, assim como outros probes de boundary retidos.

**T5:** sessão `ses_ded609cceffe7kZ16usqNCOvbN`, PID977383, terminal **0** em
`2026-11-25T12:13:47.693228+00:00`, sem timeout/error events/JSONL malformado,
stderr vazio. 57 eventos/10 step_finish/29 tools; custos dos steps reportados0.
Custo final liquidado pelo provedor continua **UNKNOWN**, sem recibo separado.
Manifesto lido3; seis comandos GitHub15–20 exit0/não truncados comprovam
disposable/recovery milestone3/issue11/PR12, head
`ba48e0e477a101478be09059509e466091c1e4a4`, checkSUCCESS/manual/dependente13
bloqueado. t5_sources diagnóstico=true/outcome=true. Inventário24–28/receipt29
efetivos, writer `writer-T5-11/seed-T5/wf-disposable-t5`, PID976344, terminal0.
Sete snapshots iguais, forbidden_attempts=[], write_authorized=false; nenhum
read fora de escopo/probe ao produtor. Read de raiz7 e ls11 negados, preservados.
Resposta55 mantém PR existente/revisão pelo coordenador/modo manual e não
despacha13. Isso não satisfaz automaticamente o gate nativo.

**Falha efetiva:** RuntimeError2438, `T5 phase 1: recovery proof incomplete`;
status=failed/proof_complete=false. O único tool `skill` de T5 foi
resume-workflow2. O modelo **leu** Verify35 e o citou como aplicável40/55, mas
não chamou skill nativa OpenSpec alguma, em nenhum status. Verify35 é arquivo
canônico, SHA-256 `3b86fbb9734fdb6b942dd12d0afa4247457aa7f212bb48832eae133f5e66880a`,
não invocação. Context41/list42/instructions43/status44/strict48 foram efetivos,
exit0/não truncados, mas CLI e leitura não substituem tool nativo.

Os candidatos vinculados de T5 eram Explore/Apply, ambos no catálogo realmente
entregue junto de resume-workflow; Verify não estava nesse catálogo, embora seu
arquivo estivesse legível. Nenhum dos candidatos foi invocado. Matcher retorna
native=null/discovery=[]/invocation=[]/instructions=[]: esse último vazio decorre
da ausência de fonte invocada selecionada, **não** da ausência de strict48.
Execution_binding.native_source=null é verdadeiro e não será preenchido com a
skill meramente lida. Diferentemente do nono trace (Explore realmente invocada),
não é apenas Apply-only rejeitando uma invocação alternativa real. Acrescentar
Verify ao matcher, reinterpretar read35 ou apagar hashes não criaria o evento
ausente. Não se determina causa cognitiva exclusiva nem falha de provedor;
revisão independente deve examinar seleção/descoberta/invocação sem waiver.
**T7 NOT RUN**, nenhuma captura/turno/ID ou escolha T7 fabricados; sem décimo
primeiro modelo ou continuação forçada.

**Bindings resume-effective-inputs-v1 originais**, hashes recomputados válidos:
T1 `a84e5a91e1d35213d2eba855c2853e55eba755cfd8dd112fcd36dc3048c87125`,
T5 `f0f8787387b30b9b5a67c71474a810bafd587fa4b55582fb9babcb50b35b15ac`.
Execution bindings/catálogos reais capturados, source T1 Apply/source T5 null.
Digests before=after T1
`7bd8d5e08d845c2b3b957732966e22fef81967513a8eaf93fd04dec3c7a16b17`,
T5 `22f8c820dbe58d7bfb6a2ee344fcd00b269e44b90832e5f51dae629cc2371173`.
Nenhum campo original foi reescrito para aprovar resultado ou reuso F1.

**Prova** `evidence:ev-20261125T121046Z-f787388b`, verified/failed antes desta
nota, verifier3/no_required_gate. Log checksum-bound **1.586.873 bytes**,
SHA-256 `ec613943a4bde9577638e4f669eccd116bcc06bee17fa0c35478da0b6b51b841`,
integridade conferida, perfil opencode=2.3.2/openspec=2.1.1/
sandbox=observe61-703ffb9-ses_dee5e0a18ffe. Originais/bindings:
`/tmp/opencode/issue61-observe-703ffb9-ses_dee5e0a18ffe/results.json`,
SHA-256 `b43f9869bbb72920cbca0aa39aea7a8176c262a9192c4211adc58ab3e81c46f7`.
T1 JSONL `50a2e78c7b767a00a6d9ead22febc3b86f483cd5b11201e61de6d461730caaa3`,
terminal `baf7c4cadd3f80303d22b00d9ccceffada175fd276e1c68995a9ad930197140a`;
T5 JSONL `27875e1421cfec24523ab4e4e8b3a9bcd2b7b60d8358f972d749cda2ecbf8703`,
terminal `a98f41e3b93cc6e6a4742eeb4731967af5453ff4586ad1ff4c43827d37649bbd`.

Parada por falha: somente retenção documental para devolver checkout limpo
ownerless WAITING. Nenhuma fonte/prompt/guard/pin/resultado alterado, nenhuma
autocorreção, retry, suíte final, archive/sync/PR/push/merge/tag/release.
Clientes942840/977383 e writers941615/976344 ausentes em /proc após recibos
terminais; nenhum kill/cancel/restart/limpeza/remoção de DB. Todas as nove
observações falhas anteriores e suas aprovações externas limitadas aos inputs
antigos continuam intactas. Seq50–52 retêm falha/diagnóstico/bloqueio atual sem
resolver episódios anteriores ou reiniciar seu orçamento. Próxima ação:
revisão independente das respostas/eventos T1/T5 e do gap de invocação nativa;
nenhuma nova inferência autorizada.

### Correção offline do gate nativo T5/T7 — sem décima observação

Entrada limpa `c17f361b015e3480f5d127e97f89f12283e43b99`, somente notas desde
a fonte observada `3b7f98b2fc5c743f5e00a69f0bd5d36b647ccd06`; mesmo worker
`ses_dedd54912ffeUE0O1zucvX95YV`/checkout/branch/issue/run. Reserva ownerless
WAITING adquirida/verificada sem drift; Apply/context/list oficiais confirmam
16/18 e 3.4/4.3 pendentes. Nenhum novo modelo, mudança global ou closeout.

**Revisão independente posterior**, informada pelo coordenador:
`ses_dee9d76e4ffeR10I59JewObvEC` aprova os subcenários realmente observados
no nono run, **nos inputs3b7f98b**, não por reuso de45c5b72:
- T1 `ses_ded94254bffeAw0vHsGHrhKaz2`: nove fatos e condição tipada atuais,
  receipt22/inventário21/23–27/proposta31–38/Apply39/strict40/GitHub69, skill49
  e handoff80 seguro/reconcile-ownership/escritafalse. CLI anterior à skill é
  permitido para T1; serialization_compliance=failed permanece diagnóstico.
- T5 `ses_ded914169ffeL50MoN6MM82Kow`: fontes12–17 efetivas no escopo
  disposable/recovery milestone3/issue11/PR12/dependente13; PRhead
  `5b0d4ba2c6f9046faaacab030801ca7f66cfe6ba`, checkSUCCESS, nenhuma review e
  modo manual, dependente bloqueado. Diferença do head do checkout divulgada
  honestamente, sem alegação de entrega/green final. Owner22/receipt26 e
  snapshots preservados, sem tentativa stateful/probes do produtor; apenas
  listing5 negado. Final48 encaminha revisão do PR existente ao coordenador.

Os campos pending/scenario_pass dos originais **não** foram reescritos. O nono
run inteiro continua FAILED no gate nativo T5; T7 nunca rodou. Clientes/DB
terminaram normalmente/idle succeeded; steps completos reportam custo0, mas
liquidação final pelo provedor permanece UNKNOWN. Falhas/limites anteriores
continuam intactos; aprovação substantiva separada não cria F1 na fonte nova.

**Diagnóstico assertion/fixture, não provedor/aplicação/posse:** o gate fixava
Apply para T5 e ignorava o catálogo entregue. A skill efetiva foi Explore42,
fonte canônica `e776f0d8b5e36d2e5fd8149254a95c54008942bd4336d1c67e568c67e45ddcca`,
com strict45 correto depois; Apply33 era leitura de arquivo, nunca invocação.
Design e1408daf:41 exige descoberta/invocação nativa correlacionada e validação
aplicável; :45 preserva T5 PR/manual/dependência sem exigir Apply. Explore oficial
é stance read-only (:15–17). Trocar Apply-only por Explore-only repetiria a
sobre-restrição; revisor confirma correção de implementação no contrato aprovado,
sem decisão material/replan.

**Correção limitada:** reutilizar o matcher existente para T5 com Explore **ou**
Apply, cada qual com seu próprio source/path/hash/body/session e descoberta real
por ferramenta ou catálogo entregue. Strict exato da fixture, exit0/não truncado/
cwd/change corretos antes do handoff é o anchor já solicitado; help/prosa ou
instructions de outro change não o substituem. Não impor repetição pós-skill em
T1/T5 (design:41/45); a ordem bruta Explore42→strict45 fica preservada. T7 conserva
a ordem explícita do segundo prompt: reinventário antes do primeiro conteúdo/
invocação, strict após Explore. MessageID presente deve corresponder a step_start
anterior da mesma sessão; não aceitar output de outro step.

T7 permanece **Explore-only**, conforme design:45/prompt. Cada fase recaptura o
DB privado read-only; Apply é rejeitado em qualquer status mesmo após reinventário
ou junto de Explore válido, sem ampliar a política de ferramentas. Cada captura do
DB para continuidade requer mesma identidade/baseline/blob/source/
sessão, snapshot novo e user/assistant **do turno atual** obtidos do DB/correlacionados
ao step_start. Baseline alterado, stale/prepared metadata ou identidade inconclusiva
não qualificam discovery. Catálogo antes da escolha é metadata, não conteúdo,
seleção, posse ou permissão. Ele não substitui probes nem apaga conteúdo precoce
all-status. Controles de dois turnos usam DB/probes sintéticos explicitamente;
nenhum capture T7 real foi inventado. Conexões de snapshot são fechadas.

Preparo/binding enumera candidatos canônicos: T1/T5 ambos, T7 apenas Explore,
sem resposta/SHA de skill injetados no prompt. `native` fica null até observação;
execution_binding registra fonte efetivamente invocada, não placeholder Apply.
Mapa explícito adicional em resume-effective-inputs-v1 é fixture-only. Oracle/
capture/binder mudam inputs materiais; aprovações nos inputs3b não autorizam
reuso automático ou whole F1 PASS na candidata corrigida.

**Provas offline:** 60 focados passaram em
`evidence:ev-20261125T114918Z-b19c0966`, incluindo alternativas T5, T7 restrito/
catálogo atual em dois turnos e negativos source/hash/body/skill/session/catálogo/
step/cwd/change/exit/truncamento, conteúdo precoce all-status e recibo obrigatório
mesmo com discovery válido. `evidence:ev-20261125T114918Z-0b1cb4df` reavalia
T5 **real retido**: catálogo→Explore42→strict45/fontes PR comprovados, 11 negativos
em cópias rejeitados. Hashes originais results/JSONLs/terminais/manifesto/log
idênticos; log1.746.429 bytes/`de5b7198…b38646f`. Placeholder Apply e bindings
originais ficam como história, nunca reclassificados retroativamente. Novo recibo
é diagnóstico offline, não PASS nativo, resultado T7 ou resolução por replay.

Próximo passo: revisão independente afetada; só autorização separada poderá
iniciar harness **completo real T1/T5/T7**. 3.4/4.3, Verify atualizado/archive/
preparo e suíte local final no HEAD limpo exato após todos os commits seguem
pendentes; repetir após qualquer commit posterior. Guards/permissões/reader/
timeout/pins/ignorados preservados. Sem décima inferência, selector/framework,
PR/push/archive/merge.

### Nona observação — T5 assertion/native gate, sem timeout ou retry

Uma nova observação **completa**, autorizada pelo coordenador após aprovação
independente de `ses_dee9d76e4ffeR10I59JewObvEC` da correção material T5,
partiu do HEAD limpo exato `3b7f98b2fc5c743f5e00a69f0bd5d36b647ccd06`,
plano aprovado `e1408dafbb7c6b2251b206afe62a2785708d1e08`. Worker real
`ses_dee5e0a18ffefE7FomnYJ9smc1`, stage `observe61-t5-bootstrap`,
mesmo checkout/branch/issue/run; WAITING ownerless reservado/verificado sem drift,
nove bytecodes ignorados preservados. Check não final pré-launch valid=true,
violations=[]/ready=null, histórico bloqueado preservado. Provas exatas
reverificadas: 313 testes `ev-20261125T110845Z-76ae87d5`, strict13/13
`ev-20261125T111044Z-ece29cef`, change1/1 `ev-20261125T111044Z-9e087d13`,
impacto/retenção `ev-20261125T111044Z-02b1f8fa`, todas verified/passed,
**no_required_gate**, não suíte final nem PASS nativo.

Uma única chamada `python3 -B tests/smoke_resume_candidate_opencode.py`,
PYTHONDONTWRITEBYTECODE=1, RESUME_SMOKE_OUTPUT único, sem --output-dir externo;
wrapper reteve artefatos próprios em execution.log checksum-bound.
Callback real `sh_2126bcbdd001gRjhYGknha6SSc` **exit1**, evidência encerrada
`2026-11-25T11:21:17.941900Z`. Timeout externo1.800s/interno360s inalterados,
**nenhum expirou**. HOME/config/XDG/CODEX_HOME/DB privados novos, sem auth de
operador. OpenCode2.3.2/OpenSpec2.1.1; guard fresh ativo nas duas fases, fonte
`b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`.
Default nativo `/api/model/default` cruzado com `/api/model` selecionou
`opencode/big-pickle` separadamente, enabled/active/tools/text e input/output/
cache read/write conhecidos zero, não hardcode/override/fallback pago.

**T1:** `ses_ded94254bffeAw0vHsGHrhKaz2`, PID4065153, terminal0 em
`2026-11-25T11:19:33.816475+00:00`, sem timeout/error events/JSONL malformado.
82 eventos/13 step_finish/52 tools; soma dos custos reportados dos steps0.
Nove fatos true, condição tipada before-write/prior-stopped-owner comprovada;
proof_complete=true, **pending_independent_review/scenario_pass=false/
write_authorized=false**. Serialization_compliance=**failed**, pois o JSON80
inclui blocker textual de propriedade; é diagnóstico legado, não novo PASS
nem motivo para reescrever a resposta. O harness prosseguiu por fatos técnicos,
não por aprovação independente. Apply nativa49, CLI Apply39/strict40 anteriores
à skill: ordem bruta preservada para revisão, sem inferir cumprimento de ordem
que não ocorreu. Inventário21/23–27/receipt22/revisão38/diff37/GitHub69 efetivos.
Writer `writer-T1-61/seed-T1/wf-disposable-t1`, PID4064287, observado vivo e
terminal0; proposta fixture `fb6f9f06f8ff1af1145728f087262265f39fe6b3`,
review `2c5a58cb47f2d8ec5dc8273ab71b7b6f0634ddb3`, não aprovações reais.
Oito snapshots iguais, pré-requisitos físicos/Git verified=true antes/depois.
Nenhuma tentativa stateful; reads fora de escopo negados7–8 e demais boundary
denials permanecem no original, sem ler dados pessoais.

**T5:** `ses_ded914169ffeL50MoN6MM82Kow`, PID4122032, terminal **0** em
`2026-11-25T11:21:17.582760+00:00`, sem timeout/error events/JSONL malformado,
stderr vazio; 50 eventos/10 step_finish/24 tools, custos dos steps reportados0.
Não afirmar custo final liquidado por provedor: não há recibo separado disso.
Manifesto efetivamente lido8; seis fontes GitHub exatas12–17 (exit0/não truncadas)
comprovam issue11/PR12/head `5b0d4ba2c6f9046faaacab030801ca7f66cfe6ba`,
check SUCCESS, manual e dependente13 bloqueado. t5_sources diagnóstico=true,
outcome=true, forbidden_attempts=[], sem probes ao produtor ou reads fora de
escopo; apenas ls5 negado. Inventário21–27/receipt26 efetivos, writer
`writer-T5-11/seed-T5/wf-disposable-t5`, PID4121033, terminal0. Sete snapshots
iguais; write_authorized=false. Resposta final48 mantém revisão do PR existente/
merge manual pelo coordenador e não despacha13.

**Falha efetiva pós-terminal:** results T5 status=failed/proof_complete=false,
RuntimeError na linha2328: `T5 phase 1: recovery proof incomplete`.
O matcher T5 está ligado à fonte nativa **openspec-apply-change**:
native_discovery=[]/native_invocation=[], strict45 presente. O modelo leu
Apply33 mas isso não é invocação. Leu outras skills e invocou efetivamente
**openspec-explore42**, fonte canônica local/fixture idêntica
`e776f0d8b5e36d2e5fd8149254a95c54008942bd4336d1c67e568c67e45ddcca`,
antes de strict45. Não houve directory listing qualificável no matcher
native_calls, nem invocação de Apply. O catálogo entregue existe, mas a via
T5 atual não o agrega como discovery. Isso localiza o gate não satisfeito,
não autoriza trocar oracle/skill exigida, nem concluir sozinho que o modelo
ou o contrato estão errados. Revisão independente deve separar aplicabilidade
read-only e descoberta/invocação exigidas; não há erro de provedor/bootstrap
GitHub demonstrado nesta execução. **T7 NOT RUN** pelo stop normal do harness,
sem continuação forçada ou décima observação.

**Bindings originais resume-effective-inputs-v1**, hashes recomputados válidos:
T1 `43c614826194276f8641fa4d1cef83ab15de67fb897b85bd959bdf6039c745d8`;
T5 `f824dd2ebff3bc665ed2c95355041858afe2361d4e9a26e506de0188e22bb353`.
Execution bindings e catálogos realmente entregues capturados para ambos;
blob de catálogo `66f5a938235937b9e15fa3f01e95fbc82edb31fddcae5fd5ac499d969b769285`.
Digests before=after T1
`146e7e175babaa586f5d93d11419b7d2a4c6d21ee0d28b93dee0ad5f90285dbe`,
T5 `ba15e69ab086679f1b5885f32059c445adb11752d56fb52ce6adb05b5dadb19f`.
Nenhum binding/resultado/catálogo foi reconstruído ou alterado após a falha.

**Prova nativa** `evidence:ev-20261125T111624Z-0bd063a1`, verified/failed
antes desta nota, verifier3/no_required_gate. execution.log **1.746.429 bytes**,
SHA-256 `de5b71985511eb32fb05194698ced66aaf067b313c9bc3dbd00780f66b38646f`,
integridade conferida. Perfil opencode=2.3.2/openspec=2.1.1,
sandbox=observe61-3b7f98b-ses_dee5e0a18ffe. Originais e bindings em
`/tmp/opencode/issue61-observe-3b7f98b-ses_dee5e0a18ffe/results.json`;
results SHA-256 `e84dc4a65a8dd12ee33a47e8bd2a0584bdcbd38fae9cf92d62a183f3d3a556fd`.
T1 JSONL `b8537f480b855d0c9e2bf8c8aeaefa7fccb4a7b7d5219bce697a909c06742e9c`,
terminal `9714248b82db8698e0aa8ae4f62f4ff5579c21140bc78f7a74dbc49b2444e101`;
T5 JSONL `bd0fb4e2be023449b80cb740f543937150b91611695762578649f19b84f97e16`,
terminal `63c9a54ed45544a0d68f9db3bf5c05700612669991c6f89ac71bc3744b0f9d66`.

Parada sem autocorreção/retry/décimo modelo, archive/sync/PR/push/merge/suíte
final. Apenas esta retenção documental será commitada para devolver checkout
limpo ownerless WAITING; nenhum input observado será alterado. PIDs dos dois
clientes e dos dois writers acima ausentes em /proc após terminais; nenhuma
limpeza/kill/restart/cancel/remoção de DB foi feita. Sete falhas originais,
oitava falha e aprovação externa T1 limitada aos inputs45c5b72 preservadas;
seq46–48 registram nova falha/diagnóstico/bloqueio, não resolvem episódios
antigos. Próxima ação mínima: revisão independente dos eventos/respostas T1/T5,
do gate nativo T5 e do impacto F1; nenhum novo modelo está autorizado.

### Correção offline T5 — bootstrap de escopo e recusa de tentativa stateful

Entrada limpa `3fea46b81102cdf3283f244012f80aa02c02ca36`, apenas documentação
desde a fonte observada `45c5b720b84a14072e0d9763944815c2c7721b4b`. Mesmo
worker `ses_dedd54912ffeUE0O1zucvX95YV`/issue/checkout/branch/run; reserva
ownerless WAITING adquirida/verificada sem drift. Apply/context/list oficiais
confirmam **16/18**, com 3.4/4.3 ainda pendentes. Sem novo modelo ou closeout.

**Revisão posterior separada:** o coordenador informa aprovação independente de
`ses_dee9d76e4ffeR10I59JewObvEC` para o subcenário T1 efetivamente observado em
45c5b72, sessão `ses_dedb94dbbffeG1BESArNUjvaP5`: nove fatos, condição tipada
before-write/prior-stopped-owner, final71 seguro/reconcile-ownership/escritafalse
e resposta/eventos revisados. Isso vale **naqueles inputs**, não é T1 executado
na candidata corrigida nem F1 completo. Os campos originais
pending_independent_review/scenario_pass=false ficam intactos; a aprovação é
externa ao resultado original. Sete falhas históricas permanecem falhas; oitavo
run inteiro permanece FAILED pelo T5 timeout e T7 NOT RUN.

**Diagnóstico de implementação da fixture, não aplicação/provedor:** T5 seleciona
`disposable/recovery`, milestone3/issue11/PR12/dependente13/runwf-disposable-t5.
Remote/registry/shim concordam. O plano copiado descreve o produtor
`rocker-code/my-ai-skills`/issue61/PR62, somente proveniência, nunca autoridade
para trocar o alvo. No trace, root12/85 e remote/config112/166–167 foram negados;
Apply48 devolveu tarefas do produtor, probes51–53 desse alvo foram negados e
proposal81/design82 reforçaram esse contexto. O entrypoint legível
recovery-evidence.json não era indicado no prompt T5 nem lido; faltavam locators
GitHub no manifesto, embora os comandos corretos já fossem permitidos. Logs do
shim vazios confirmam ausência de leituras efetivas de PR/head/check/manual/
dependência, não indisponibilidade dos comandos corretos. Não se afirma causa
cognitiva exclusiva do modelo nem erro/quota de provedor.

Além disso, o agregador T5 consumia t5_sources sem a recusa all-status usada
pelos outros cenários: um futuro trace com fontes válidas poderia passar apesar
de verify tentado. O evento19 real tentou
`worktree-reservation verify --session "$OPENCODE_SESSION_ID"`; foi negado antes
de spawn, não é efeito consumado. Snapshots iguais não apagam essa tentativa.

**Correção mínima:** prompt T5 aponta primeiro ao manifesto existente, sem nomear
resume/native skill nem preencher resposta/SHA esperados. Somente T5 publica
selected_scope e distingue o plano produtor de fontes do alvo. Os seis locators
GitHub derivam dos objetos reais da fixture, usam shlex.join/cwd e conferem
membership nos comandos **já permitidos**: issue/pr list, APIs issue11/13,
pr view12 (head/checks/manual/dependência) e pr checks12. Não há novo endpoint,
ferramenta, autenticação, política ampliada ou protocolo de produção. T1 mantém
seu entrypoint; T7 não ganha seleção/locators antes da escolha explícita.
t5_sources agora recusa toda tentativa stateful por forbidden_attempts, inclusive
failed/cancelled/running, e exige exit0/saída não truncada nos reads. O relatório
T5 normal separa essas tentativas de leituras negadas de boundary e mantém
write_authorized=false. Nenhum campo desse relatório foi retroinserido no timeout.

**Lifecycle:** diagnóstico posterior confirmado na delegação registra último
assistant T5 finisherror/typeaborted/“Step interrupted” completo às
10:44:36.098Z e native IDLE seq784/outcomeinterrupted às 10:44:36.100Z, antes
do terminal cliente10:44:36.152Z. É diagnóstico local posterior, **não** catálogo
entregue/execution_binding capturado pelo run. ACK remoto de abort e custo final
continuam UNKNOWN. Nenhum restart/cancel/kill/limpeza de DB foi necessário ou
executado nesta correção. `ev-20261125T104933Z-6f13151c` permanece retenção
diagnóstica, não execução nativa substituta.

**Provas offline:** 57 focados passaram em
`evidence:ev-20261125T110433Z-98093eae`. Teste de locators lê o manifesto
permitido, distingue seleção do plano produtor e executa os comandos exatos no
shim real por /bin/sh, com HOME/PATH privados, payload/readlog e commit Git local
real no PR/head; sem rede/modelo. Positivo source-only e negativos de
PR/head/check/manual/dependência/exit/truncamento permanecem. O fixture negativo
retém integralmente o evento19; adicioná-lo a reads unitários sintéticos válidos
reprova o aceite, sem fabricar uma execução nativa bem-sucedida.
`evidence:ev-20261125T110541Z-5a43f2e5` confere igualdade desse evento com o
JSONL real, bindings T1/T5 originais, ausência de captures T5 e hashes inalterados
dos originais results/JSONLs/terminais/manifesto/execution.log. O log nativo
continua 1.910.748 bytes/`57fc5810…14c1276`, FAILED, sem edição de observações.

**Impacto F1:** prompt T5 e manifesto preparado são inputs **materiais** novos,
capturados pelo binding existente (harness, prompt, recovery-evidence e fontes).
Regressões confirmam invalidação por mudanças nesses bytes. Mesmo com alteração
concentrada em T5, não presumir reuso de T1: aprovação anterior pertence aos
inputs45c5b72 e não concede F1 da fonte nova. Alternativa segura mínima era manter
BLOCKED; publicação dos comandos existentes mais a recusa read-only corrige
defeitos verificáveis sem aumentar orçamento/timeout/permissões. Próximo passo:
revisão independente afetada; somente autorização separada poderá iniciar outro
harness **completo real T1/T5/T7**, sem selector/replay. 3.4/4.3/Verify atualizado/
archive/preparo/gate local final exato seguem pendentes; qualquer commit posterior
exige repetir a suíte final. Sem nona inferência, push/PR/archive/merge.

### Oitava observação — T1 tecnicamente comprovado/pending review, T5 timeout

Autorização nova do coordenador limitada a **observação somente**, sem closeout
mesmo em elegibilidade técnica. Entrada limpa exata
`45c5b720b84a14072e0d9763944815c2c7721b4b`, plano revisto aprovado
`e1408dafbb7c6b2251b206afe62a2785708d1e08`, revisão de plano
`ses_dedd9267effeMuorC3GIpcWxGc` e de implementação
`ses_dee9d76e4ffeR10I59JewObvEC`. Worker
`ses_dee5e0a18ffefE7FomnYJ9smc1`, stage `observe61-oracle`, mesmo
run/checkout/branch; reserve/verify sem drift. Proposal/design/spec/tasks e
notas atuais lidos, diagnóstico40 pós-segunda falha preservado; check não final
valid=true/violations=[]/ready=null/BLOCKED antes do lançamento.

Reverificados no HEAD exato: 312 offline
`ev-20261125T102547Z-becc9cb1`, strict global13/13
`ev-20261125T102716Z-0dfad130`, change1/1
`ev-20261125T102716Z-020c83c0`, projeção offline
`ev-20261125T102716Z-bfcdbc60`, todos verified/passed **sem required gate**.
Não são suíte final nem aprovação de modelo/replay.

**Uma chamada completa do harness**, `PYTHONDONTWRITEBYTECODE=1 python3 -B
tests/smoke_resume_candidate_opencode.py`, via `workflow-evidence record`,
sem `--output-dir` externo; saída única em `/tmp/opencode`, logs próprios
streamados para execution.log checksum-bound. Timeout shell1.800s/interno360s;
callback real `sh_21246a3190011AdWxOUtBVwlzA` exit **1**.
Instalação/HOME/XDG/CODEX_HOME/DB/Location privados novos, sem credenciais/config
pessoais. OpenCode **2.3.2**, OpenSpec **2.1.1**. Em cada fase, guard fresh
ativo fonte `b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`;
native `/api/model/default` cruzado com `/api/model` no mesmo ambiente/Location
selecionou `opencode/big-pickle`, enabled/active chat, tools/text→text e
input/output/cache read/write conhecidos zero. Sem override/fallback.

**T1:** sessão `ses_dedb94dbbffeG1BESArNUjvaP5`, PID3300711,
terminal exit **0**, sem timeout/provedor/JSONL malformado, às
`2026-11-25T10:38:32.499548+00:00`. 15 step_finish/41 tools, custo reportado0.
Nove fatos técnicos **true**, condição `before-write/prior-stopped-owner`
corroborada, serialization_compliance=passed e proof_complete=true.
**read_only_acceptance=pending_independent_review, scenario_pass=false,
write_authorized=false**: não declarar T1 PASS nem resolver episódio por isso.

- Catálogo realmente entregue à mesma sessão (epoch=through4/user5/assistant6
  concluído), blob `66f5a938235937b9e15fa3f01e95fbc82edb31fddcae5fd5ac499d969b769285`,
  snapshot `867adff1553273ad883d1bfae664fddeb6a008b1c78d6012927b39c58fe89bb0`;
  skill Apply nativa32, path/origem/hash canônicos não symlink
  `71f084a1ea26194f62cb9ed31da8e4aa837fd57abb2b91b9cbb0c6ee8d503b79`.
- Inventário35–39/41 e receipt40 efetivos; writer
  `writer-T1-61/seed-T1/wf-disposable-t1/T1-issue-61`, PID3299563 observado vivo
  e depois esperado; terminal true/exit0. Commit46/ancestralidades45–47/
  review48/diff49/strict50/Apply42/GitHub61 bem-sucedidos antes do final71.
  Proposta fixture `3516958b2d1f30b3b13cb421f006dd6f86cab647`, review
  `3a22c0261d8bd8d3fa3abfc7096c695e6fe368cf`, distintos de candidata/plano.
- Oito snapshots iguais e pré-requisitos físicos/Git de artefatos verified=true
  antes/depois. Nenhuma tentativa stateful T1; leituras negadas de boundary
  permanecem no relato. Resposta e eventos ainda exigem revisão independente.

**T5: falha real por timeout interno**, sessão `ses_dedb6cf0dffeS60EcHgP3slpEv`,
PID3349989, terminal **143/timed_out=true** em
`2026-11-25T10:44:36.152411+00:00`. `execute_model` esgotou360s e terminou o
grupo por SIGTERM; o shell externo não expirou. 217 eventos, 43 step_finish
com custo reportado0/128 tools antes da interrupção; custo final desconhecido,
não confundir preços elegíveis ou steps completos com encerramento normal.
Sem erro de provedor/JSONL malformado; não inferir quota/429 ou falha preexistente.

O modelo permaneceu fazendo leituras/probes, não ficou sem progresso de
transporte: discovery27/28, skill Apply116 e strict119 ocorreram. Contudo,
não leu recovery-evidence.json; calls/reads do shim GitHub estão vazios, nenhum
PR12/head/check/manual/dependência13 foi observado com sucesso, nem receipt.
Leu o plano copiado e tentou reiteradamente endpoints do repo real/issue61/PR62
e variantes, **todos negados pré-spawn**. Isso é fato da sequência, não prova
da causa interna da confusão nem de indisponibilidade dos comandos permitidos.
Também tentou `worktree-reservation verify --session "$OPENCODE_SESSION_ID"`
no evento19: tentativa stateful negada, identificada diagnosticamente nos
eventos originais, não apagada por snapshots iguais. Nenhuma escrita/rede real/
credencial pessoal foi executada. T5 antes/depois disponíveis/iguais nas sete
dimensões, mas sem resposta final válida ou gates completos.
Catálogo entregue e execution_binding T5 não foram capturados no fluxo normal,
pois o timeout antecedeu a agregação; não os reconstruir como prova concluída.
**T7 NOT RUN**; nenhuma nona observação ou continuação forçada.

**F1/bindings preparados antes da inferência**, ambos com hash conferido:
T1 `5264986ca1788be1ef1d7456b105188c7a8149e83b44d7b344f89f0428665978`,
T5 `99819e08cda9bf3fcee99322151648e4fb6da4a4327790b7ac418b15324300f9`,
formato `resume-effective-inputs-v1`, source45c5b72/approved e1408daf.
T1 execution_binding retém sessão, hashes reais eventos/terminal/catálogo,
source nativa e snapshots `3367c85afc15974aa39758ec0ccbf869a40675f0740de92676f1ca819444e407`.
T5 snapshots iguais `861e27c67e7f02c6330b31107425a3f33d81f17fd792ca9a3cbed774e281639d`.
Preparação não é comportamento nem aprovação de reuso; somente a nota factual
de falha será commitada, sem alterar os inputs/resultados observados.

**Prova** `evidence:ev-20261125T103548Z-f3771146`, execution.log1.910.748 bytes,
SHA-256 `57fc58105265ded7d1ba451f899ae3ed53825ef8a71ed4ab63e61b21a14c1276`,
verificada antes desta nota **verified/failed**, exit3/no_required_gate,
`--tool opencode=2.3.2 --tool openspec=2.1.1 --env-id
sandbox=observe61-45c5b72-ses_dee5e0a18ffe`. Retém results/preparações/bindings/
snapshots/guard/policy/audit/receipts e eventos/terminais/stderr de T1/T5.
Originais `/tmp/opencode/issue61-observe-45c5b72-ses_dee5e0a18ffe`:
results `a737062d2918fa9520f4bc5e4969d508688915452ef3462a53c396fd2771c0df`;
T1 JSONL `91a5b71a9cda92470ab67b1dd7d4adceee600bab7aca328a1d3059d48fc5e90f`,
terminal `45fb38a513c2d103a109116c9addcb32f7b378ac0ce721ed7bfba88e6b89f9d8`;
T5 JSONL `133c2924c757e627a0cd4c1031dff2fa05093846b63fdc84d486c32f7ba72df6`,
terminal `9057e1ee32ccc1bd68b2b72b5fa9f8020d7c2759cd0acc98a4b100677216c6d3`.

**Parada por falha T5:** sem autocorreção, fonte/teste/guard/pins alterados,
retry, nono modelo, archive/sync/PR/push/merge ou suíte final. T1 continua
pendente de revisão independente; todas as sete falhas originais e seq39/40/41
intactas. Seq42–44 registram timeout/diagnóstico/bloqueio T5, não PASS T1.
Próxima ação mínima: revisão independente de T1 e do trace T5/inventário de
locators/escopo antes de eventual decisão separada; não ampliar timeout/guard
nem lançar modelo para pesquisar a causa. Saída limpa ownerless WAITING.

### Apply offline da revisão e1408daf — sem nova observação nativa

Worker novo `ses_dedd54912ffeUE0O1zucvX95YV`, mesmo checkout/branch/issue/run.
Entrada limpa na proposta exata `e1408dafbb7c6b2251b206afe62a2785708d1e08`;
reserva ownerless WAITING adquirida pela identidade nativa própria, sem takeover
ou aceite de drift. Skill oficial `openspec-apply-change` invocada e instruções
Apply/context/list reais consultadas (14/18 antes das correções). Políticas
canônicas do checkout prevalecem sobre adaptadores globais anteriores; integração,
38 commits anteriores, nove bytecodes, instalador/pins/guard foram preservados.

**O1/T1:** `t1_handoff` agora valida campos semânticos limitados, sem igualdade
do objeto inteiro. A condição da fixture futura é `ownership_condition`:
`phase=before-write`, `kind=prior-stopped-owner|released-unreserved`,
checkout/execução/owner/run observados e `write_authorized=false`. Ela precisa
coincidir com snapshot e recibo independente corretos, mais todos os gates
nativos existentes. Inventário/receipt/identidade/proposta/Apply/GitHub/catálogo
ausentes, owner vivo/desconhecido, drift, próxima ação errada, claim estruturado
de efeito/autorização ou tentativa stateful mesmo negada continuam bloqueando.
Recibo terminal não transfere posse; reconciliação/aquisição verificada vem
antes de qualquer escrita. `apply-issue` só indica estágio posterior com essa
condição explícita.

`serialization_compliance` conserva o diagnóstico legado separado. **Nenhum
texto não vazio recebe waiver:** status/blockers/limitations não são julgados
por wordlist/LLM; mesmo com todos os predicados técnicos verdadeiros,
`read_only_acceptance=pending_independent_review` e `scenario_pass=false`.
Contradições textuais ou claims ambíguos exigem revisão independente da resposta
e de todos os eventos antes de qualquer aceite. Leituras negadas de boundary
continuam separadas de tentativas stateful; não foram apagadas.

**Projeção separada**, `evidence:ev-20261125T102143Z-5f20e853`: usa o sétimo
trace completo real e reavalia suas observações/fontes/pré-requisitos
prospectivos, não os booleans antigos. Os nove grupos de fatos técnicos e os
campos semânticos são verdadeiros; o owner é o mesmo ACTIVE anterior parado.
Final90/`reconcile-ownership`, oito dimensões inalteradas e formato legado
**failed** preservados. O novo campo tipado **não foi observado** ali: avaliação
da fixture futura permanece blocked, `native_pass=false`, escrita não autorizada.
23 negativos em cópias removem fontes reais (inclusive receipt25/GitHub72/native79),
alteram término/identidade/owner/pré-requisitos e são rejeitados. Não se inseriu
condição ou observação em eventos antigos. Hashes antes/depois de results,
JSONL, terminal, manifesto e execution.log originais são idênticos; log original
continua 675.598 bytes/`8eb68cdd…79aaf`, manifesto FAILED/exit1.
O recibo novo retém relatório e script diagnóstico completos no próprio log.
Uma primeira execução offline (`ev-20261125T101624Z-c4a15119`) falhou com
`KeyError: path`: o snapshot real conserva path no registry e campos resumidos
na reservation. Corrigida a leitura dessas fontes existentes, sem adicionar
campo ao trace; prova intermediária `ev-20261125T101744Z-e4efdc59` preservada.
Antes disso, `--artifact` externo foi recusado pelo wrapper (exit2, sem executar
o diagnóstico); a captura final usa apenas o log suportado. Nada disso é retry
de modelo ou resolução do episódio nativo.

**F1:** cada fase futura grava `effective_inputs` (`resume-effective-inputs-v1`,
SHA-256 de metadados congelados + hashes literais dos arquivos), antes de
inference. Distingue fonte candidata/proposta aprovada/contrato selecionado de
snapshot instalado/regras carregadas/fixture transformada. Enumera `.agents/`,
todo `openspec/` efetivamente copiado, artefatos normalizados/checkboxes, evidência
e locators, scripts/shim/guard/policy, recibos/estado GitHub, prompt/config/
permissões/ambiente allowlisted, executáveis/versões e modelo/metadados zero.
Credenciais/DB não entram no binding; o catálogo realmente entregue, IDs de
sessão, eventos/término, outputs CLI e snapshots ficam vinculados à execução
separadamente. O binding é preparação, não prova de comportamento.

`effective_input_diff` mostra diferenças exatas, inclusive ausência versus null;
nunca remove hashes nem normaliza texto para aprovar equivalência. Mudanças
efetivas/materialidade incerta exigem smoke completo. Diferenças só de
proveniência também ficam sem permissão de reuso automático: revisão independente
deve mapear bytes/refs imutáveis e explicar relevância. Archive/sync pode mudar
inputs copiados, live specs ou tarefas: comparar origem **e** fixture realmente
normalizada; path “docs”/checkbox não é dispensa. Mesmo byte-identical não concede
gate, e metadados/replay não substituem T1/T5/T7 reais completos.

56 testes focados offline passaram em
`evidence:ev-20261125T102143Z-697eeb34`, incluindo ACTIVE parado e WAITING
released reais na fixture, negativos de condição/fonte/efeito/tentativa e
binding de plano/skill/referência/guard/config/modelo/runtime/arquivo ausente.
Esta é amostra com diff, **não** suíte final de entrega.

**Pendente:** revisão independente das superfícies alteradas, autorização
separada para um run real completo T1/T5/T7, T7 em dois turnos no mesmo ID,
Verify atualizado/strict/archive/preparo e suíte local completa no HEAD final
limpo exato após todos os commits (repetida após qualquer commit). As sete
falhas nativas, T5/T7 NOT RUN, seq39/40/41 e diagnóstico pós-segunda falha
permanecem intactos. Retenção correta é `ev-20261125T093859Z-fc6fed7a`;
`fc7ef644` era typo, não outro recibo. Sem oitava inferência, push/PR/archive/merge.

### Sétima observação nativa revisada — 09:32–09:35 UTC, NOT READY

Nova autorização explícita do coordenador após aprovação independente
`ses_dee9d76e4ffeR10I59JewObvEC` de
`fca6a971bc016d1d693e379c798a8f938605a040`, não retry automático no source
anterior. Worker `ses_dee5e0a18ffefE7FomnYJ9smc1`, stage
`observe61-inventory`, mesmo run/checkout/branch. Reserva ownerless WAITING
adquirida/verificada sem drift; nove ignorados e histórico preservados.
Seq37/38 lidos e check não final valid=true/violations=[]/ready=null/BLOCKED
antes do lançamento; nenhuma falha histórica removida ou convertida em PASS.

Pré-smoke exato reverificado: 309 offline
`ev-20261125T092721Z-01bfec2e`, 61 focados
`ev-20261125T092721Z-caa34261`, controle released
`ev-20261125T092721Z-a7f446c7`, diagnóstico38
`ev-20261125T092721Z-471f00b6`. Strict global novo no HEAD limpo:
`ev-20261125T093202Z-8ec3776e`, `openspec validate --all --strict
--no-interactive --json`. Todos verified/passed sem required gate;
não são suíte final nem prova de modelo.

**Uma chamada** `PYTHONDONTWRITEBYTECODE=1 python3 -B
tests/smoke_resume_candidate_opencode.py` via captura
`workflow-evidence record`, sem exclusão externa. Timeout shell 1.800 s/
interno 360 s; callback completo `sh_2120c92f7001RPoSQ7Jgypa4NW`.
HOME/XDG/CODEX_HOME/DB/Location/instalação novos e privados, sem config/
credenciais do operador. OpenCode **2.3.2**, OpenSpec **2.1.1**.
Fresh native `/api/model/default` cruzado com `/api/model` no mesmo
ambiente/Location selecionou **`opencode/big-pickle`**, enabled/active chat,
tools/text→text, input/output/cache read/write conhecidos zero. Sem override
ou fallback. Guard fresh ativo SHA-256
`b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`,
policy `0e76506910f5a74bbef67ab70c8641840863ff521d30d6d3b837074a4c6b6434`;
ambos hooks e cleanup retidos, sem mudança de raw bytes/permissões.

**Terminal real:** sessão `ses_dedf35f74ffeFTglzDI0fB5HPP`, PID 2106145,
exit **0**, `timed_out=false`, terminou
`2026-11-25T09:35:30.773677+00:00`; sem erro de provedor/JSONL malformado.
16 step_finish/custo reportado **0**, 49 tool events. **Harness exit 1/T1;
T5/T7 NOT RUN.** Nenhuma oitava observação. Before/after disponíveis e
iguais nas oito dimensões; pré-requisitos de artefatos verified=true e
iguais. model_proposal_proved/model_apply_gate_proved/
model_inventory_proved **true**, write_authorized **false**.

**Observações positivas efetivas:**

- Roteamento natural `skill(resume-workflow)` **2**; catálogo realmente
  entregue à mesma sessão, epoch=through=4/user5/assistant6 concluído, blob
  `66f5a938235937b9e15fa3f01e95fbc82edb31fddcae5fd5ac499d969b769285`,
  snapshot `7a873384c23da438ec658b047b71508a8eb37cbd8cae3cff41b87a51066dfc2d`.
  Skill Apply nativa **79**, origem/path canônicos não symlink, SHA-256
  `71f084a1ea26194f62cb9ed31da8e4aa837fd57abb2b91b9cbb0c6ee8d503b79`.
- Receipt **25** exit0/terminal true, writer `writer-T1-61 / seed-T1 /
  wf-disposable-t1 / T1-issue-61`, PID 2105274 observado vivo e esperado
  pelo harness. Receipt HEAD `c9c23894219551b054eb5833288fa69e334b90dc`.
- Proposta fixture `a2504c3dbd9c79d4ef1d879144ba399d50358037`, review
  `e1b9c0a8818cb26e182c2e29c6d6f5ffea4e984f`, não candidata/source31cdb42.
  Commit **38**, ancestralidades **37/39**, review **41**, diff completo
  **40**, Apply instructions **45** ready/0 de16 e strict **46**, todos
  exit0/untruncated antes do final **90**. Corpos opcionais **83–87**.
- Inventário publicado realmente observado: worktrees **47**, status/index
  worktree **48/49**, root **50/51**, reservation list **52**. Owner atual
  ACTIVE `seed-T1/wf-disposable-t1`, PID null, digest/HEAD/path/issue/branch
  correspondem ao snapshot/receipt, sem drift/extra desconhecido.
  Isso identifica owner anterior parado; não transfere posse.

**Falha de handoff permanece:** final **90**, JSON 2.281 bytes, escolhe
RECOVERED/`reconcile-ownership`, mas inclui **um blocker**: owner ACTIVE
anterior distinto do observer e necessidade de reconciliar antes de Apply.
Há oito limitations. A estrutura está dentro dos limites; o campo blocker
não vazio reprova `t1_handoff`, `outcome=false/proof_complete=false`.
Não é ausência de inventário ou quota de corpos: esses gates passaram.
O texto confirma receipt terminal e ausência de autorização de escrita;
revisão independente deve confrontar a classificação desse pré-requisito
de escrita com o handoff read-only, sem reinterpretar a execução como PASS.
Os textos intermediários são eventos separados; o matcher usa somente
o último JSON, não a concatenação de comentários.

forbidden_attempts=[] significa nenhuma tentativa stateful classificada,
não zero tentativas de boundary. read_scope_attempts registra duas leituras
negadas de referências sob HOME **da própria fixture instalada** (6/8),
não leitura do HOME do operador. Pipe de ambiente **5**, ls **7**, endpoint
comments **75** e outras leituras não publicadas foram negados pré-spawn.
Nenhuma chamada ao repo real/credenciais do operador foi executada.
Top-level status/finished_at ausentes nessa falha de asserção, sem reconstrução.

**Prova** `evidence:ev-20261125T093223Z-ff1be68e`, execution.log
675.598 bytes/SHA-256
`8eb68cddbe87100d7e3a57f19eefbb5805c8d5b6203338da336735a883a79aaf`.
Retém preparação/results/snapshots/pré-requisitos/catálogo/proveniência,
eventos/stderr/terminal/guard/policy/audit/receipts checksum-bound.
Verificada antes desta nota: **verified/failed**, exit3/no_required_gate,
`--tool opencode=2.3.2 --tool openspec=2.1.1 --env-id
sandbox=observe61-fca6a97-ses_dee5e0a18ffe`.
Originais `/tmp/opencode/issue61-observe-fca6a97-ses_dee5e0a18ffe`;
results SHA-256 `fda97d1465273ffd3463c4cff5220189a07896b88eb3b6e104f81a189749180c`,
JSONL `e5f09cab0f79c1f590f058ec94a49f7a4230a178833d3a413080d9748c43c461`,
terminal `28bc362fe5f8406699b076a6a8289028148322f7123ee87005222edb6a6963b6`.

**Parada:** sem autocorreção/retry, oitavo modelo, archive/sync, suíte final,
push/PR/merge ou alteração de fonte/guard/pins. Mesmo episódio de handoff
com blockers não vazios (seq34 e seq39), sem reset de assinatura/contador;
diagnóstico pós-segunda falha seq40 antes de qualquer eventual nova tentativa.
Tarefas3.4/4.3 pendentes; todas as provas nativas históricas FAILED/UNKNOWN
preservadas. Somente nota factual será commitada; saída limpa ownerless
WAITING, check final valid=true/ready=false/BLOCKED. Próxima ação mínima:
revisão independente offline do blocker de ownership versus próxima ação
read-only, sem nova inferência ou ampliação de autorização.

### Correção offline de ownerstate — WAITING released não é posse desconhecida

Entrada limpa `05ea1c286f276415ec90fbc536414e9ee0513b3f`, mesmo
checkout/branch/run. Writer real `ses_deeb219ebffecKs4h8aN9D00bl`, stage
`workerfix61-released-inventory`: reserva ownerless WAITING adquirida e
verificada, nove ignorados/histórico preservados. Sem sétima inferência.

**MUST FIX confirmado pela revisão independente**
`ses_dee9d76e4ffeR10I59JewObvEC`: o predicado de inventário introduzido em
05ea1c2 aceitava somente ACTIVE com owner anterior parado. O negativo que
rotulava WAITING released/ownerless como “unknown transition” estava errado
sob `protocol/WORKTREES.md:13,21` e spec aprovada31cdb42, cenário T1:43.
Seq38 anota essa correção de seq37 sem apagar falha/evento ou resetar contador.

Condições corrigidas, somente para recuperação read-only:

- **A:** ACTIVE com owner anterior correspondente ao receipt terminal real
  continua válido; não transfere owner para a sessão nova.
- **B:** WAITING released/ownerless unívoco é válido, com list/inventário
  realmente observados, identidade path/issue/branch/HEAD/digest ligada ao
  snapshot real antes/depois e receipt independente do writer anterior
  com execução/owner/run/checkout corretos. Ausência de owner **não** prova
  término. Reserva/reconciliação continua obrigatória antes de efeitos.
- **C:** posse desconhecida/RECOVERY_REQUIRED, campos ausentes, owner null em
  ACTIVE/estado inválido, rows ambíguas, drift ou outro owner vivo continuam
  bloqueados. Checar presença dos campos evita aceitar owner/drift ausente
  como se fossem null explícitos. Nenhum comando stateful do modelo é permitido.

Controle concreto `test_publicly_released_waiting_fixture_recovers_read_only_with_prior_receipt`:
producer **conhecido e criado pelo teste**, `seed-T1/wf-unit`, usa helpers
públicos: reserve planned → cria worktree → reserve/verify pelo processo
cooperante → Popen.wait/receipt terminal → checkpoint → verify → release
WAITING. Depois faz novos readouts reais de Git/list/reader em eventos unitários
sintéticos. Nunca adota identidade de reserva do operador; só muda a fixture
descartável. O predicado anterior falhou nesse controle; o corrigido passa,
com snapshots iguais/owner ainda null, sem qualquer reserva pela recuperação.

Prova com diff `ev-20261125T092512Z-4c9146bc` contém lifecycle público real
planned/activate/checkpoint/release, receipt independente e readouts:
old_predicate=false/corrected_predicate=true/write_authorized=false.
Negativos mantêm ACTIVE null/owner vivo, receipt errado/ausente, digest/HEAD/
drift incorretos, fatos ausentes e ambiguidade. 61 focados passaram offline.
Essa prova é **pre-smoke**, não whole-run PASS ou observação de modelo.

O mesmo diagnóstico retém a sexta execução FAILED: model_inventory_proved=false,
handoff_outcome=false, blockers contraditórios, inputs originais byte-identical.
Eventos11/61 negados, limites de ignored, limitations/blockers, locators,
guard/raw commands/permissões/reader/pins/T5/T7 continuam inalterados.
As provas anteriores de 05ea1c2 (308 offline/60 focados/strict13) eram
pre-smoke e não cobriam esse positivo legítimo; não viram gates finais.
Somente `t1_inventory_proof`, seu teste e este handoff mudam. Check não final
válido; repetir focados/suíte offline/controle no HEAD limpo, sem required
gates. Strict não precisa ser repetido: contrato/OpenSpec inalterado.
Check final continua ready=false/BLOCKED. Saída limpa ownerless WAITING;
revisão afetada independente antes de qualquer sétima observação
**separadamente autorizada**. Sem PR/push/archive/merge/mudança global.

### Correção offline pós-sexta falha — inventário observado e limites do handoff

Writer `ses_deeb219ebffecKs4h8aN9D00bl`, stage
`workerfix61-inventory-handoff`, mesmo checkout/branch/run; entrada limpa
`875aab2463ac317ebdbf9f5d2593a0b2119b86f3`, source627b89a inalterado.
Reserva ownerless WAITING adquirida/verificada com identidade nativa real;
nove ignorados/histórico preservados. Revisão independente recebida de
`ses_dee9d76e4ffeR10I59JewObvEC`; nenhuma sétima inferência autorizada.

**ANNOTATED CORRECTION sem apagar seq35:** blockers vazio continua
obrigatório para RECOVERED, mas o prompt chamava blockers de “lista de
lacunas”, misturando três limites não bloqueantes com um gap real:

1. Seed controlled_fixture prova somente a revisão da fixture, não aprovação
   independente real da candidata/source31cdb42 — limite de escopo honesto.
2. SHA256 não recomputado pelo modelo/namespace source019aef5d versus fixture
   be3b9397 — limite de método/transformação, não checksum adicional exigido;
   review30/diff39 e pré-requisitos prospectivos já provaram integridade.
3. **Inventário realmente não observado**: branch/checkouts/índice/dirty/
   reservas não foram consultados com sucesso; preservação pelo harness não
   substitui inspeção pelo modelo. Status5 composto e list/status70–71 foram
   corretamente negados. Os comandos permitidos não estavam publicados
   integralmente/cwd, apesar do texto “Published list commands”.
4. Testes/smoke/CI pós-Apply ainda ausentes com 0/16 tarefas são limites do
   estágio futuro; retomada read-only identifica o último gate anterior.
   O relato sobre “versão declarada” não cria critério de bloqueio novo.

Fonte de execução `ev-20261125T083810Z-4711919b`, sessão
`ses_dee25002cffeyXijaW40o1kU0x`: modelo exit0/custo reportado0, harness1/T1,
T5/T7 NOT RUN, sem erro de provedor/timeout. O trace real usa receipt17,
Apply41, native50, strict42, proposta25/ancestralidades28–29/review30/diff39,
final79; todos os gates anteriores ao handoff foram comprovados. O final
RECOVERED+quatro blockers é incoerente e o inventário está genuinamente
ausente. A execução original continua **FAILED**.

Fase efetiva: asserção pós-terminal, contrato de saída da fixture e lacuna
de observação do consumidor de inventário; não aplicação ou paid route.
Scope: HOME/XDG/DB/Location privados novos, oito dimensões/pré-requisitos
capturados antes/depois iguais. Lifecycle: terminal completo, writer
cooperante real confirmado; isso não transfere posse nem autoriza escrita.
Mesmo receipt antigo não pode aprovar um owner atual diferente/vivo ou
inconclusivo no registry observado.

Contrato já aprovado: delta
`openspec/changes/issue-61-opencode-safe-resume/specs/interrupted-workflow-resume/spec.md:27`
e `skills/resume-workflow/SKILL.md:10,14,18` exigem inventário/reconciliação.
Publicar locators existentes de status completo, worktree porcelain,
índice staged e reservation list com repository/cwd corretos; confrontar
outputs efetivos da mesma sessão com as identidades reais da fixture e do
receipt, antes do handoff. Não impor quota se fontes nativas equivalentes
cobrirem os fatos. T7 só recebe esses locators após escolha; manter sua
ordem/reinventário e todas as tentativas de conteúdo pré-escolha proibidas.

Limite importante: `git status --untracked-files=all` não enumera ignored;
`worktree-reservation list` também não é status fresco de bytes ignorados.
Para a fixture fechada formada por arquivos rastreados, confrontar índice/
status realmente observados com o inventário físico completo antes/depois
sem paths extras; nunca alegar um scan nativo de ignored que não ocorreu.
Dados locais extras/unknown sem observação suficiente bloqueiam a ação
dependente. Inventário observado não é permissão de iniciar writer:
reconciliação/reserva seguem sendo pré-condição de qualquer efeito.

Segurança distinta: evento61 tentou `gh api repos/rocker-code/my-ai-skills/
issues/61`, repo real fora de `disposable/recovery`; guard negou **pré-spawn**.
Não houve leitura real de rede/operador. forbidden_attempts vazio significa
nenhuma tentativa stateful classificada, não zero boundary attempts.
Registrar essa tentativa de scope separadamente das variantes benignas/
unsupported negadas (ex. sha256sum66). Não transformar toda leitura negada
em falha automática, nem ampliar permissões. IDs candidate/source são
traceabilidade do produtor, não autorização de acesso ao repo real.
O replay também conserva read11 do diretório pai do sandbox, fora das
raízes declaradas: negado pré-execução, tipo filesystem; distinto do
endpoint real de repository61. Não foi leitura de arquivo do operador.

Alternativa mínima: manter bloqueio. Escolha: esclarecer blockers atuais
versus limitations de escopo/método/futuro, publicar comandos existentes e
exigir prova nativa de inventário/owner correlacionada ao receipt. Schema
pequeno somente da fixture, sem juiz LLM, wordlist, output de produção ou
resposta calculada pelo harness. RECOVERED com blocker atual continua
inválido; rótulos/limitations não substituem observações obrigatórias.
Seq34 FAILED/seq35 diagnóstico/seq36 BLOCKED são preservados; seq37 anota
esta correção sem resetar episódio. Check não final antes de novas provas;
check final continua ready=false. Sem sétimo modelo/PR/push/archive/merge;
próximo passo posterior é revisão afetada independente.

**Implementação limitada à fixture e provas com diff (não gates finais):**

| Contrato / risco | Prova |
| --- | --- |
| Separação contextual dos quatro relatos reais | `ev-20261125T091054Z-842ba1ac`: 60/60 focados. Handoff adiciona somente `limitations: list[str]` (até oito itens; JSON total limitado como antes), mantendo `blockers=[]` para RECOVERED. `next_action` também aceita `reconcile-ownership` antes de efeitos, sem novo estágio/CLI de produção. Seed, método SHA/namespace e pós-Apply são limites; inventário atual desconhecido é gap real. Sem wordlist/juiz semântico: provas tool/source continuam mandatórias. |
| Locators, não resposta injetada | Mesmo grupo executa readouts reais de Git e registry em repo/worktree descartáveis, com receipt do helper cooperante existente. Comandos/cwds publicados conferem literalmente com policy gerada; sem campos owner/resultado esperados. Formas existentes `git -C` ou cwd do checkout cobrem os mesmos fatos; não há quota de variantes. T7 não recebe inventário selecionado antes de escolha explícita. |
| Prova nova de inventário T1 | Mesmo grupo exige saída nativa bem-sucedida, não truncada, mesma sessão/cwd/identidade, pré-handoff: branch/checkouts, índice staged e status completos no root e worktree, reservation list e receipt correlacionado por execução/owner/run/checkout/HEAD. Ausência/erro/saída falsa/cwd errado, owner desconhecido ou outro vivo, receipt desconhecido/errado e duplicata conflitante falham. Snapshot/inventário físico de local-only/ignored continua independente e não concede posse. |
| Limites de dados locais / escrita | Inventário físico de fixture deve permanecer igual e conter apenas paths rastreados antes/depois; extra ignored/untracked não pode passar pela falta de enumeração de ignored no status/list. `write_authorized=false` é limite da observação, não resposta a ser repetida pelo modelo. Owner antigo parado ainda exige reconciliação/reserva antes de efeitos; nunca se assume posse do modelo. |
| Sexta falha não é reclassificada | `ev-20261125T091107Z-3bf7c926`: diagnóstico offline retém hashes originais de results/eventos/terminal, FAILED/proof_complete=false, cadeia nativa válida e oito snapshots iguais. Novo model_inventory_proved=false e handoff_outcome=false; nem uma mudança de interpretação de limitations supre as observações faltantes. T5/T7 continuam NOT RUN. Não injeta evento nem altera o trace/fixture antigo. |
| Safety e histórico | Mesmo diagnóstico guarda eventos11/61 negados pré-execução em out_of_scope_reads (filesystem/repository), separados de outras variantes negadas. Mantém forbidden_attempts como stateful somente. Compara permissões byte-a-byte e funções antigas exceto handoff/locators/main; guard/reader/receipt/snapshot/pins/seleção de modelo e T5/T7 permanecem inalterados. Todos os registros históricos até seq36 preservados literalmente e nove ignorados byte-identical. |

Falha inicial do novo teste foi preparação incompleta do repo descartável
(faltava a reserva planned antes de criar o worktree), corrigida no teste
seguindo o helper atual, sem alteração do receipt. Nenhuma tentativa de
modelo. As provas acima têm dirty=true; antes de retornar, repetir focados,
suíte offline integral, strict e diagnóstico/check não final no HEAD limpo,
sem flags de required gate. IDs clean-HEAD ficam externos ao commit; saída
limpa ownerless WAITING não altera ready=false do episódio.

### Sexta observação nativa revisada — 08:38–08:41 UTC, NOT READY

Autorização nova explícita do coordenador após aprovação independente
`ses_dee9d76e4ffeR10I59JewObvEC` do HEAD limpo exato
`627b89a32718cbda8fb01fb8f8a379678286acc3`, não retry automático da quinta
execução. Worker `ses_dee5e0a18ffefE7FomnYJ9smc1`, stage
`observe61-predicate`, mesmo run/checkout/branch; reserva ownerless WAITING
adquirida/verificada sem drift, nove ignorados/histórico preservados.
Diagnóstico seq33 lido; check não final valid=true/violations=[],
ready=null/BLOCKED antes de lançar.

Reverificadas no HEAD exato, sem required gate: 301 offline
`ev-20261125T083027Z-77b66844`, 53 focados
`ev-20261125T083011Z-9ad28b94`, strict 13/13
`ev-20261125T083027Z-ad3f7379`, replay condicional
`ev-20261125T083011Z-bcddacb5`, diagnóstico
`ev-20261125T083027Z-d677d4ce`. Não são gates finais nem prova de modelo.

**Uma chamada** `PYTHONDONTWRITEBYTECODE=1 python3 -B
tests/smoke_resume_candidate_opencode.py` via captura
`workflow-evidence record`, sem `--output-dir` externo. Timeout shell
1.800 s/interno 360 s; callback completo `sh_211daf0f10012JCP9Y5QgpiAM3`.
HOME/XDG/CODEX_HOME/DB/Location/instalação privados novos, sem configuração/
credenciais pessoais. OpenCode **2.3.2**, OpenSpec **2.1.1**.
Fresh `/api/model/default` cruzado com `/api/model` no mesmo ambiente/
Location selecionou **`opencode/big-pickle`**, chat enabled/active,
tools/text→text, preços input/output/cache read/write conhecidos zero.
Sem override, fallback, atualização global ou mudança da fonte revisada.
Guard fresh ativo: SHA-256
`b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`,
policy `5b967e2d4ed210c88ed10b42404b84a1f7a31341047d754404e188f5e483b647`;
ambos hooks/cleanup retidos no audit, sem normalizar quotes/comandos.

**Terminal:** sessão `ses_dee25002cffeyXijaW40o1kU0x`, PID 1050443,
exit **0**, `timed_out=false`, terminou
`2026-11-25T08:41:28.306891+00:00`; nenhum erro de provedor ou JSONL
malformado. 19 step_finish/custo reportado **0**, 42 tool events.
**Harness exit 1 em T1; T5/T7 NOT RUN.** Nenhuma sétima observação.
Before/after disponíveis/iguais nas **oito** dimensões; forbidden_attempts
vazio não apaga comandos compostos/variantes de leitura negados pré-spawn.
Top-level status/finished_at ausentes nessa falha de asserção, sem inferir PASS.

**Gates realmente comprovados nesta execução:**

- `skill(resume-workflow)` **1**; catálogo realmente entregue, mesma sessão
  epoch=through=4/user5/assistant6 concluído, blob
  `66f5a938235937b9e15fa3f01e95fbc82edb31fddcae5fd5ac499d969b769285`,
  snapshot `ff68cd08d555e6c6acb3c45130d4a76fe581a610ae90f57658e8fba7b9ddd06b`.
  Skill Apply nativa **50**, origem/path/hash canônicos não symlink,
  SHA-256 `71f084a1ea26194f62cb9ed31da8e4aa837fd57abb2b91b9cbb0c6ee8d503b79`.
- Recibo **17**, comando completo/cwd/identidades corretos, exit0 e terminal
  true: `writer-T1-61 / seed-T1 / wf-disposable-t1 / T1-issue-61`, writer
  PID 1049509 observado vivo e depois esperado pelo harness.
- Proposta fixture `38525365c351c31bef46f06c7ff662d19e12c910`, review
  fixture `a7c70e4d935281b13c09434bdee6611543c17938`, distintos da candidata
  e da proposta fonte `31cdb42`. Commit **25**, ancestralidades **28/29**,
  review **30**, diff completo exato **39**, strict **42** e Apply
  instructions **41** (ready/0 de 16/tasks corretos), todos bem-sucedidos
  antes do final **79**. Corpos opcionais também lidos **33–36/40**.
- Pré-requisitos **capturados antes/depois**, ambos verified=true e iguais:
  root/proposal/review/HEAD, cinco arquivos regular100644, blobs/modes de
  proposal/index, SHA-256 físico/review iguais, tracking flags H,
  filemode=true, conversion_settings=[] e attributes="". Inventário
  completo continua cobrindo untracked/ignored separadamente.
  `model_proposal_proved=true`, `model_apply_gate_proved=true`.

**Falha efetiva é o handoff, não a equivalência:** final **79** tem
status RECOVERED/Apply próximo, mas **quatro entradas em blockers**;
`t1_handoff` exige handoff coerente com blockers vazio. Assim
`outcome=false/proof_complete=false` apesar dos gates acima. As entradas
misturam limites de escopo/seed/transformação, hash não recomputado pelo
modelo, inventário/reserva não observados e gates pós-Apply não executados.
O matcher não deve reinterpretar essa resposta nesta execução.
As tentativas de status/inventário foram compostas ou variantes diferentes
dos comandos autorizados; `worktree-reservation list/status --json`
sem os argumentos publicados foram negados. Não demonstram
indisponibilidade universal da fonte, nem autorizam alargar raw guard.
Detalhes/semântica dos quatro blockers precisam de revisão independente
offline antes de decidir se há correção contratualmente justificada.
Não converter ressalvas em aprovação nem manter a antiga quota de corpos.

**Prova** `evidence:ev-20261125T083810Z-4711919b`, execution.log
601.469 bytes/SHA-256
`29d1cb3d01045e3a0b376ba7dc48b3fdd8e6ecf84380e85909108c9e9ef9e533`.
Retém preparação/results/snapshots/pré-requisitos/catálogo, proveniência,
eventos/stderr/terminal/guard/policy/audit/receipts checksum-bound.
Verificada antes desta nota: **verified/failed**, exit3/no_required_gate,
`--tool opencode=2.3.2 --tool openspec=2.1.1 --env-id
sandbox=observe61-627b89a-ses_dee5e0a18ffe`.
Originais `/tmp/opencode/issue61-observe-627b89a-ses_dee5e0a18ffe`;
results SHA-256 `7014f7b0561c68f40994b509f6aeca9fa34ba3bab03a9e20f01c884a92e04a0b`,
JSONL `570796ab32249e60d8b24915b26f1f959b1f6c0493dc1e70fecf4dab318a2a4c`,
terminal `dd4c920821882b11c0899616778e3c0fc61b5d7260650485b61467a4ede1a7c6`.

**Parada:** somente nota factual, sem autocorreção/retry, modelo adicional,
archive/sync, suíte final, push/PR/merge ou alteração do harness/guard/pins.
Tarefas 3.4/4.3 pendentes; quinta prova FAILED, seq33 e demais históricos/
UNKNOWN intactos. Check final deve manter valid=true/ready=false/BLOCKED.
Saída prevista limpa, ownerless WAITING; próxima ação é revisão offline
independente do handoff e dos comandos de inventário, não nova inferência.

### Correção offline pós-quinta falha — equivalência Git limitada

Writer `ses_deeb219ebffecKs4h8aN9D00bl`, stage
`workerfix61-artifact-equivalence`, mesmo checkout/branch/run; entrada limpa
`49f47082e98e01e9e2f38b9ade219499fe1189dd`, sucessor somente documental
de `3c85548`. Reserva ownerless WAITING adquirida/verificada com ID nativo
real; nove ignorados e histórico preservados. Revisão independente recebida
de `ses_dee9d76e4ffeR10I59JewObvEC`; nenhuma sexta inferência autorizada.
Política `TEST_STRATEGY.md` contra `31cdb42`: ok.

**ANNOTATED CORRECTION ao significado de seq31, sem apagar histórico:**
a ausência dos cinco `git show <proposal>:<artifact>` é factual; tratá-los
como quota contratual obrigatória não é. Em
`31cdb42:openspec/changes/issue-61-opencode-safe-resume/design.md:33,35,41–43,61`
e no delta `specs/interrupted-workflow-resume/spec.md:41–47`, o contrato
exige fontes/proposta/review/artefatos realmente correlacionados, invocação
nativa e gate seguinte comprovado, sem Apply executado. Não exige cinco
leituras separadas de corpos nem nova revisão semântica das features.
S253–260 publica esses locators úteis; S277–290 indevidamente exige **todos**
como se disponibilidade de inspeção fosse obrigação adicional.

**Diagnóstico completo complementar pós-quinta falha:** fase de seleção/
agregação de prova depois do terminal; assertion/fixture, não aplicação,
provedor, autorização ou falta de produto. Fonte
`ev-20261125T074809Z-c869767e`, sessão
`ses_dee52cf22ffeF4k4USxgA4K3at`: modelo exit0/custo reportado0,
harness1/T1; T5/T7 NOT RUN, sem timeout/erro de provedor. HOME/XDG/DB/
Location descartáveis, snapshots disponíveis/iguais, sem tentativas
stateful. Recibo21 real, Apply22 ready/correto, strict39, invocação53 e
handoff57 RECOVERED coerente já ocorreram.

A sessão observou proposta37, ancestralidades47/48, review Git imutável50
e **diff49 real**: `git diff --exit-code
0ac18eb710d2476f53dc3983e5a3ed0582940f53 --
openspec/changes/issue-61-opencode-safe-resume`, exit0, sem truncamento,
cwd/sessão corretos, antes do handoff. Review
`69f5523e3ba2e4402749fdbe5dc010702ab80844` aprova essa proposta e seus
cinco fingerprints. Não é declaração de diff nem metadata preparada.
Sob condições Git verificadas, esse confronto equivale à integridade dos
artefatos revisados; o JSON RECOVERED não é necessariamente falso sob o
contrato, embora o resultado **armazenado continue FAILED**.

A revisão independente verificou no repositório retido: cinco artefatos
necessários presentes/regular100644, blobs/modes de proposal/index iguais,
bytes físicos/SHA256 iguais ao review, nenhum skip-worktree/assume-unchanged,
core.filemode=true e nenhuma conversão/atributo aplicável. Isso é diagnóstico
independente, **não** novas observações feitas pelo modelo. A correção deve
verificar essas condições programaticamente em cada fixture futura **antes
e depois** do turno, retendo-as nos snapshots e exigindo igualdade; nunca
transformar a conferência histórica isolada em garantia universal.

Consumidores afetados: preparação da proposta/review, snapshot T1,
`t1_proposal_proof` e descrição dos locators de inspeção. Manter observações
efetivas de commit/ancestralidade/review/diff no escopo exato, strict, Apply
context/tasks/progress, catálogo/invocação/ordem pré-handoff, receipt,
outcome e limites stateful/T7. Corpos continuam disponíveis na mesma
allowlist, **opcionais**, sem quota. Nenhuma nova chamada precisa ser
permitida ao modelo. Pré-requisitos são leituras Git do harness no mesmo
ambiente seguro da fixture, não novo wrapper, serviço ou fonte declarativa.

Alternativa mínima: manter bloqueio. Escolha: aceitar a cadeia nativa
existente somente com presença/tracking/modes/flags/config/atributos/
fingerprints realmente verificados e estáveis. Diff genérico não cobre
path vazio/errado, ausentes não rastreados, ignored, conversões ou flags
de índice; esses casos devem reprovar a admissão/equivalência quando
aplicáveis. Inventário/snapshots existentes continuam cobrindo untracked/
ignored e demais dimensões, não atribuir essa cobertura a Git diff.
Trade-off: remove quota de comandos sem reduzir a prova de integridade.

Seq29 resolveu apenas captura/setup; seq30 permanece FAILED, seq31/32 e
seus fatos são preservados. Seq33 registra esta correção anotada antes de
provas novas; check não final antes delas. Replay com pré-requisitos
verificados agora é **diagnóstico de equivalência**, não nova execução
nativa completa, retro-PASS ou reescrita do bundle antigo. Flags/config
não capturados naquela época não devem ser inventados como snapshot
histórico. Tarefas3.4/4.3, T5/T7 e gate model-backed permanecem pendentes.
Sem decisão material de owner/replan, sexta inferência, PR/push/archive/
merge. Após provas offline, revisão afetada independente primeiro.

**Provas durante o diff, não gates finais:**

| Aceite / risco | Prova e limite |
| --- | --- |
| Cadeia nativa efetiva sem quota de corpos, com condições verificadas/estáveis | `ev-20261125T082230Z-c458534e`: 53/53 focados (retomada + raw guard). Positivo correlaciona source nativa, commit/ancestralidades/review/diff/strict/Apply e JSON pré-handoff sem body calls. Declaração de pré-requisito ausente/falso/stale não basta. |
| Integridade de artefatos não reduzida ao remover asserts de body strings | Mesmo grupo, três testes novos de Git real: path errado/vazio, proposta/review incorretos, set requerido vazio, bytes físicos modificados com tamanho/mtime preservados, arquivo ausente/deleção rastreada, modo executável, symlink, assume-unchanged/skip-worktree, core.filemode false, autocrlf/filter e atributos. Git diff vazio em escopo inexistente/flags/arquivos não rastreados não autoriza equivalência. |
| Preservação/migração de negativos | Negativos antigos de sessão/cwd/exit/truncamento/saída/commit/review/strict continuam obrigatórios para a cadeia usada. Os asserts específicos que tratavam body locator como obrigatório passam a reconhecer sua opcionalidade; payload auxiliar não é prova usada. A proteção contra alteração real de bytes/modo/tipo passa pelos novos checks de repositório antes/depois, não por uma string sintética. Inventário existente continua detectando untracked/ignored separadamente. Nenhum teste removido/skipado. |
| Quinta execução como diagnóstico condicional de equivalência | `ev-20261125T082230Z-23808ff3`: snapshots atuais reais usando `snapshot` existente com nova projeção de pré-requisitos; oito dimensões iguais. Proposal/index modes/blobs e SHA256 físicos dos cinco artefatos coincidem com review; flags H, filemode true, sem conversão/atributo. Bytes/index também conferem com os snapshots históricos. A cadeia37/47/48/49/50 + strict39 é suficiente **sob essas condições agora verificadas**; receipt21/Apply22/native53/final57 continuam efetivos. |
| Histórico e isolamento preservados | Mesmo recibo retém os três checksums originais e model_proposal_proved=false/proof_complete=false/status=failed. Não injeta tools/flags/config no bundle antigo, não relança modelo e não declara T1/T5/T7 completos. Limite explícito: config/flags anteriores ao run não foram capturados; checagem atual não os fabrica. |
| Raw guard/comandos/pins invariáveis | Mesmo recibo compara permissões geradas com a lista original byte-a-byte e preserva funções antigas exceto snapshot/proposal predicate/main, além de prompts, reader, guard/shim/instalador/skills oficiais. `seed_proposal_review` e todos os comandos de corpos permanecem idênticos/disponíveis. Nenhum comando novo é permitido ou publicado para contornar o gate. |

Os pré-requisitos futuros são capturados pelo harness no ambiente Git
privado/sanitizado que corresponde ao child existente, dentro de cada
snapshot T1. Falha prévia impede inferência; falha posterior ou diferença
entre snapshots reprova a prova. Captura inclui root/proposal/review/HEAD,
mapping mode/blob/SHA256, flags de tracking, core.filemode, atributos e
configuração relevante. Não é metadata do modelo nem substitui seus
comandos observados. T5/T7 não ganham esse gate ou nova ordem.

`ev-20261125T081512Z-b28d5c45` (45/45 retomada) e
`ev-20261125T081925Z-81617b23` foram provas anteriores da mesma correção,
com diff, também não gates finais. Check não final após seq33 mantém
valid=true/violations=[]/BLOCKED/environment. Antes do retorno, executar
novamente focados, suíte offline integral, strict e diagnóstico no HEAD
limpo como pre-smoke sem required gate; IDs ficam fora do commit. Sem nova
dependência (stat/Git existentes), executor nativo, inferência, arquivo de
guard/policy alterado, PR/push/archive/merge. Saída limpa/ownerless WAITING.

### Quinta observação nativa — 07:48–07:51 UTC, NOT READY

Continuação explicitamente autorizada pelo coordenador após a recusa
pré-spawn seq26–28: essa chamada não havia consumido observação de modelo.
Mesmo worker `ses_dee5e0a18ffefE7FomnYJ9smc1`, run/branch/checkout e
stage `observe61-locators`; entrada limpa
`77b0242df6ced96de8eab52937d05d611cba368f`. Reserva ownerless WAITING
readquirida/verificada, sem drift. Diff contra `3c85548` contém somente
65 linhas do handoff; harness, guard, instalador e pins byte-idênticos.
Revisão de fonte `ses_dee9d76e4ffeR10I59JewObvEC` continua aplicável à
fonte inalterada, não constitui revisão final deste resultado.

**Correção somente da chamada:** removido `--output-dir` externo do wrapper.
`RESUME_SMOKE_OUTPUT` continua em diretório único sob `/tmp/opencode`;
execution.log retém os bytes/hashes dos artefatos próprios. Nenhuma mudança
de fonte, guarda, quote, autorização, fixture ou matcher. Preflight
determinístico **sem modelo** `ev-20261125T074735Z-bdc7dcf0` confirmou
argumentos/perfis, identidade dos bytes e check não final valid=true.
Verificado antes da inferência como verified/passed/exit3/no_required_gate;
esse resultado não é smoke. Seq26–28 e sua falha original são preservados.

**Uma chamada real** `PYTHONDONTWRITEBYTECODE=1 python3 -B
tests/smoke_resume_candidate_opencode.py`, via wrapper de captura
`workflow-evidence record`, sem a exclusão externa. Timeout shell explícito
1.800 s/interno 360 s; callback completo
`sh_211ad22cf0017IkHnxV3FqPHJu`. HOME/XDG/CODEX_HOME/DB/Location e
instalação novos, privados e sem credenciais/config do operador.
OpenCode **2.3.2**, OpenSpec **2.1.1**. Guard fresh ativo antes da inferência,
fonte `b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`,
policy `6602c5c07a078338c240ba7e7b3240b61532646dd071e98c08a83faef19100dc`;
audit registra ambos hooks e cleanup. Native `/api/model/default` cruzado
com `/api/model` no mesmo ambiente/Location selecionou
**`opencode/big-pickle`**, enabled/active chat, tools/text→text, input/output/
cache read/write conhecidos zero. Sem override, fallback ou import de credencial.

**Terminal real:** sessão `ses_dee52cf22ffeF4k4USxgA4K3at`, PID 3471029,
exit **0**, `timed_out=false`, terminou
`2026-11-25T07:51:04.112762+00:00`, sem erro de provedor/JSONL malformado.
12 step_finish/custo reportado **0**, 34 tool events. **Harness exit 1/T1**,
T5/T7 **NOT RUN**, nenhuma sexta observação. Snapshots before/after
disponíveis/iguais nas sete dimensões; forbidden_attempts vazio não apaga
as tentativas de comandos compostos/leitura não permitida que foram negadas.
Top-level status/finished_at ausentes na falha de asserção, sem reconstrução.

**Fatos e limite do resultado:**

- Roteamento natural `skill(resume-workflow)` evento **1**. Diretório nativo
  lido no **17**; catálogo inicial realmente entregue à mesma sessão,
  epoch=through=4/user5/assistant6 concluído, blob
  `66f5a938235937b9e15fa3f01e95fbc82edb31fddcae5fd5ac499d969b769285`,
  snapshot `3556ae453fb05c215d66bf80906cda5233ec96c5226201ec37df323892151082`.
  Skill Apply nativa **53**, origem/path canônicos não symlink e hash
  `71f084a1ea26194f62cb9ed31da8e4aa837fd57abb2b91b9cbb0c6ee8d503b79`.
  Catálogo não substitui invocação nem observação de artefatos.
- **Locators funcionaram realmente:** reader **21** usa comando completo/cwd
  publicado e retorna exit0, terminal true, execution `writer-T1-61`, owner
  `seed-T1`, run `wf-disposable-t1`, checkout `T1-issue-61`; writer PID
  3470085 observado vivo e depois esperado pelo harness, não inferido por
  ausência. Apply instructions **22** é o literal sem aspas, exit0/ready,
  0/16 e tasks corretos; `model_apply_gate_proved=true`.
- Proposta fixture `0ac18eb710d2476f53dc3983e5a3ed0582940f53`, review
  fixture `69f5523e3ba2e4402749fdbe5dc010702ab80844`; não são candidata
  real ou proposta aprovada `31cdb42`. Commit **37**, ancestralidades
  **47/48**, review **50**, diff zero **49** e strict **39** têm exit0,
  sem truncamento e saídas esperadas antes do final **57**.
- **Faltam todos os cinco probes `git show <proposal>:<artifact>`**:
  design, proposal, dois specs e tasks. Não foram tentados, não foram
  negados por quotes/cwd e não há conteúdo equivalente observado em tools.
  Os comandos completos estavam publicados no evidence **11**.
  Metadata/review/diff e checks independentes da preparação não substituem
  observações da própria sessão. `model_proposal_proved=false`.
- Final **57** é JSON coerente `RECOVERED`, Apply próximo/não executado,
  `outcome=true`, mas **proof_complete=false**. A declaração é
  insuficientemente fundamentada; não transformar outcome em PASS nem
  enfraquecer o gate de artefatos. A falha efetiva difere de seq22:
  receipt/Apply/handoff agora ocorreram, mas faltam cinco leituras imutáveis.

**Prova** `evidence:ev-20261125T074809Z-c869767e`, execution.log
508.037 bytes/SHA-256
`d63e31a153afeb124615081b8b22c7379e164c368201d88e0949259702ddf50c`.
Preparação/results/snapshots/catálogo/proveniência, eventos/stderr/terminal,
guard/policy/audit/receipts retidos checksum-bound. Verificada antes desta
nota: **verified/failed**, exit3/no_required_gate com `--tool opencode=2.3.2
--tool openspec=2.1.1 --env-id sandbox=observe61-77b0242-ses_dee5e0a18ffe`.
Originais `/tmp/opencode/issue61-observe-77b0242-ses_dee5e0a18ffe`;
results SHA-256 `ab872c132bf2bcd233432c6e342fad7a6f5739a568763f3b8d1dcad132ad2068`,
JSONL `9c8fd6148785a57a568c3769faadaa949cb7a309c138ce7d706afd8223539688`,
terminal `73ea666eee463b07944d7c2975713b0be06105aa0c2a47072d360cca17f00577`.

**Parada:** sem autocorreção/retry/modelo adicional, archive/sync,
suíte final, push/PR/merge ou alteração de produção. Tarefas 3.4/4.3
pendentes; histórico FAILED/UNKNOWN intacto. Próxima ação mínima:
revisão independente offline das cinco observações ausentes e do relato
RECOVERED sem fundamentação completa, sem alterar guard ou critérios.
Somente handoff factual será commitado para saída limpa ownerless WAITING;
esse commit documental não aprova runtime nem satisfaz gate final.

### Observação autorizada não iniciada — wrapper recusado no prelaunch

Worker `ses_dee5e0a18ffefE7FomnYJ9smc1`, stage `observe61-locators`,
run `wf-20261116T064328Z-45cb0ecc`, entrada limpa exata
`3c85548fe095259fe55b9b48718022ed67105272`. Reserva ownerless WAITING
adquirida/verificada sem drift; nove bytecodes e commits preservados.
Revisão independente informada `ses_dee9d76e4ffeR10I59JewObvEC`.
Política contra `31cdb42`: ok. Diagnóstico seq25 e check não final lidos
antes do lançamento: valid=true/violations=[], ready=null/BLOCKED.
Reverificadas no HEAD exato as provas 298 offline, 50 focados, strict
13/13, usabilidade reader/CLI e diagnóstico:
`ev-20261125T072945Z-bed5e24f`, `ev-20261125T072922Z-db9333b4`,
`ev-20261125T072945Z-1d17cdda`, `ev-20261125T072922Z-6dcbbf08`,
`ev-20261125T072945Z-4383041b`; todas verified/passed sem required gate.
Não são gates finais nem prova de modelo.

**Falha operacional, antes do harness:** a única chamada externa foi
`scripts/workflow-evidence record ... --output-dir
/tmp/opencode/issue61-observe-3c85548-ses_dee5e0a18ffe -- python3 -B -c ...`,
com timeout externo explícito 1.800 s e callback real do shell
`sh_211a48aac001ATv7V152CjRros`, exit **2**:
`workflow-evidence: path must remain inside checkout`.
O wrapper rejeita outputs externos em `scripts/workflow_evidence.py:285`,
antes de criar evidence_id/manifesto (:293–307) ou executar o child (:313).
Esse `--output-dir` foi erro deste executor, não defeito demonstrado do
harness, modelo, guard ou aplicação. O diretório solicitado não existe.

**T1/T5/T7 NOT RUN**, nenhuma sessão nova, inferência, catálogo entregue,
preparação, snapshot, recibo de writer ou terminal de modelo desta tentativa.
OpenCode **2.3.2** e OpenSpec **2.1.1** foram conferidos, mas preflight fresh
de guard/modelo **não ocorreu**; não presumir modelo/default/preço/custo zero.
O exit 2 é do wrapper, não do harness ou modelo. Sem quinta observação
model-backed e sem retry corrigido: a regra explícita de parar na primeira
falha foi respeitada. Históricos failed e Dell UNKNOWN continuam intactos.

**Diagnóstico acessível** `evidence:ev-20261125T074002Z-fee6cd0b` captura os
bytes reais do erro, hash, identidade/callback, ausência do diretório e fonte
da validação pré-spawn. Verificado antes desta nota como
verified/passed/exit3/no_required_gate com `--tool opencode=2.3.2 --tool
openspec=2.1.1 --env-id sandbox=observe61-3c85548-ses_dee5e0a18ffe`.
O PASS refere-se **somente ao diagnóstico**, não à tentativa, setup ou smoke.
O wrapper recusado não produziu seu próprio evidence_id.

Próxima ação mínima para o coordenador: revisar offline a chamada de captura.
O sandbox externo deve continuar externo; a retenção checksum-bound de seus
bytes pode usar o execution.log existente, como as chamadas anteriores,
sem declarar output externo como exclusão do fingerprint do checkout.
Não mover o sandbox para o checkout, ampliar o helper ou executar modelo
para diagnosticar. Qualquer lançamento corrigido precisa de autorização
separada, preflight fresh e check após seq27, não retry automático.
Tarefas 3.4/4.3 seguem pendentes; sem Verify de closeout, archive/sync,
PR/push/merge ou suíte final. Somente este handoff factual foi alterado;
seu registro documental não aprova a candidata nem muda o código revisado.
Seq26–28 registram tentativa, diagnóstico e bloqueio; resolução `blocked`
classifica o bloqueio, **não** aprova setup. Check não final deve continuar
valid=true; check final deve permanecer ready=false/BLOCKED.
O primeiro commit documental saiu 128 (`Author identity unknown`) antes
de criar commit. Os cinco commits anteriores usam consistentemente
`OpenCode <opencode@localhost>`; essa identidade do agente foi selecionada
somente por `git -c` no commit documental, sem editar configuração.

### Correção offline pós-quarta falha — publicação literal de locators

Writer `ses_deeb219ebffecKs4h8aN9D00bl`, stage
`workerfix61-exact-locators`, mesmo checkout/branch/run; entrada
`3a3fdaa24cc775248b0ae774677eeaf8b5384674`, nota dirty do observer
preservada. Reserva ownerless WAITING adquirida/verificada com ID nativo
real; nove ignorados e histórico preservados. Revisão independente recebida
de `ses_dee9d76e4ffeR10I59JewObvEC`; nenhuma quinta inferência autorizada.

**Diagnóstico complementar ao seq23, antes de novas provas:** camada
assertion/fixture de publicação/usabilidade, com rejeição de autorização
correta e agregação pós-terminal corretamente falha. Modelo
`ses_dee7a654fffeTm0iHDWBZM9vOq` exit 0/custo reportado 0, harness 1/T1;
HOME/XDG/DB/Location descartáveis, snapshots disponíveis/iguais, nenhuma
tentativa stateful. T5/T7 NOT RUN. Proposta/catalog/native39 comprovados não
substituem Apply instructions e recibo efetivamente observados.

Fonte de execução `ev-20261125T070455Z-8f203e55`: status42/instructions43 usou
`--change "issue-61-opencode-safe-resume"` e foi negado, pois a allowlist
contém o spelling **sem aspas**. A skill oficial mostra exemplos com aspas;
para este literal os argv são semanticamente iguais, mas o guard compara
**bytes brutos**, corretamente. Não criar parser, aceitar aspas alternativas
ou modificar skill/guard para aprovar a tentativa negada.

Contraprova de source no HEAD de entrada `3a3fdaa`:
`tests/smoke_resume_candidate_opencode.py:510–512`
já constrói o comando permitido completo com `shlex.join` e os campos reais
do receipt. Porém `:1357–1359` publica só `python3 <reader>`, sem seus quatro
argumentos. Todos os 11 calls observados omitiram argumentos; não houve
owner/run incorreto efetivamente fornecido. O receipt existe, mas source/
`receipts.json` exigiam uma investigação indireta desnecessária. O reader
com aridade errada sai 2 sem usage; nenhum help wrapper é necessário se o
locator completo for publicado.

Consumidores: produtor de permissões raw, metadados existentes
`recovery-evidence.json`, prompt T1 e confirmação do reader; T5 compartilha
o locator incompleto, e T7 turno2 usa o prefixo como se fosse um path. A
correção reutiliza comandos da política existente e o mesmo `shlex.join`
com execution/owner/run/checkout do **writer cooperante**, não sessão do
modelo/observer. Publicar cwd de execução separado do checkout de identidade
do receipt. T1 recebe o Apply instructions literal já permitido; T7 turno1
não recebe locator de candidato escolhido nem Apply. Só após escolha
explícita o turno2 recebe o locator completo daquele writer, sem escrita
entre snapshots; T5 recebe seu único writer sem sugerir Apply como próximo
gate. Leituras de metadados continuam não sendo prova terminal.

Alternativa mínima: manter bloqueio sem correção. Hipótese escolhida:
publicação única dos locators completos, validada contra comandos/cwds da
política existente, remove a ambiguidade **sem mudar autorização, matcher,
reader, guards de T7 ou outcome**. Orientação genérica para usar o comando
publicado verbatim é suficiente, sem nomear recovery skill ou SHA esperado.
Limite: publicação nova e replay offline não são observação nova do modelo.
O trace quarto original deve continuar FAILED: Apply43 negado, nenhum
recibo observado, JSON87 BLOCKED; não substituir seus inputs ou resultados.
Seq22 FAILED/seq23 diagnóstico/seq24 BLOCKED e históricos failed/UNKNOWN
continuam preservados. Seq25 registra este complemento; check não final
antes de provas, `ready=false` continua correto. Próximo passo posterior:
revisão afetada independente e somente autorização separada de observação.

**Provas durante o diff, não gates finais:**

| Aceite / risco | Prova e limite |
| --- | --- |
| Locators completos coincidem com comandos/cwds já permitidos, incluindo paths com espaços | `ev-20261125T072203Z-5cfac6cd`: 42/42 em `test_resume_reinventory.py`, três testes novos. Canonical Apply sem aspas e receipt com quatro argumentos estão na política raw; variante Apply com aspas continua ausente. Publicação não altera a política. |
| Identidades vêm do writer real, não sessão; T5/T7 sem novo mecanismo | Mesmo grupo: identidade/cwd/checkout separados; T5 publica seu único receipt, T7 fase1 não publica locator selecionado nem Apply, turno2 exige escolha explícita (ambos candidatos testados). Reader real da unidade rejeita execution/owner/run/checkout errados, aridade incompleta, receipt ausente/ativo (inclui negativos existentes). Não é prova nativa de modelo. |
| Usabilidade dos comandos publicados com receipt cooperante real, não mock | `ev-20261125T072459Z-d562cea9`: dois comandos completos executados por `/bin/sh` com o child env seguro da política retida e membership raw/cwd conferido **antes**. Reader exit0 devolve exatamente o receipt `writer-T1-61 / seed-T1 / wf-disposable-t1 / T1-issue-61`, anteriormente observado vivo e aguardado por `Popen.wait()`; cwd é `T1`, não `T1-runtime` nem o checkout de identidade. Apply instructions literal exit0: change correto, ready, 0/16. |
| Trace quarto continua realmente falho | Mesmo recibo: JSONL/results/terminal com os três hashes originais; Apply43 negado, todos os 11 readers incompletos negados, runtime_reads vazio, final87 BLOCKED. Novas saídas offline ficam separadas; não foram injetadas nos eventos nem gravadas na metadata antiga. Proposta/native39 continuam comprovados, sem retro-PASS. |
| Guard/permissões/reader/matchers/pins preservados | Mesmo recibo compara **todas** as funções antigas exceto main com `3a3fdaa`, além de RUNTIME_READER e arquivos guard/shim/instalador/skills oficiais; byte-idênticos. Policy antiga `805346fa…` e seus bytes não mudaram. Prompts T5 e T7 inicial idênticos; turno2 T7 só substitui a montagem ambígua pelo locator pós-escolha. Nenhum novo guard/parser/comando permitido. |

O log checksum-bound de usabilidade tem script, locators publicados, comandos/
cwds/saídas reais, receipt fonte e trace original. Essa execução é **offline
POSIX-shell/reader/CLI**, não prova de dispatcher nativo ou nova inferência.
Repetir o executor nativo do guard seria desnecessário: seus bytes,
permissões, cwd/child env e hooks são os já comprovados. O receipt observado
é exclusivamente o writer cooperante desta fixture; não preenche receipt
histórico perdido de outro observer, que permanece UNKNOWN.

`TEST_STRATEGY.md` contra `31cdb42`: policy ok; check não final após seq25
valid=true/violations=[] e episódio seq22 blocked/environment. Antes do
retorno, registrar focados completos, suíte offline integral e strict no
HEAD limpo como **pre-smoke sem required gate**, IDs fora do commit.
Sem nova dependência, mudança de contrato, archive/sync, PR/push/merge ou
quinta inferência. Saída prevista limpa e ownerless WAITING.

### Quarta observação revisada — 07:04–07:07 UTC, NOT READY

Autorização separada do coordenador após revisão independente
`ses_dee9d76e4ffeR10I59JewObvEC` do HEAD limpo
`3a3fdaa24cc775248b0ae774677eeaf8b5384674`. Diagnóstico completo seq21
lido e `attempt-log check` não final **valid=true/violations=[]** antes da
observação; BLOCKED/ready=null não foi tratado como prontidão.
Worker real `ses_deedf03e1ffeIEi5jKBFwDgALP`, `observe61-isolated`,
mesmo run/checkout/branch; reserve/verify/checkpoint/verify sem drift.
Verificadas provas do HEAD exato: 295 offline
`ev-20261125T065636Z-70e90e55`, 47 focados
`ev-20261125T065622Z-ef5d8205`, strict 13/13
`ev-20261125T065636Z-1f095b01`, projeção
`ev-20261125T065622Z-42b2a83d`, diagnóstico
`ev-20261125T065636Z-37236387`; sem required gate, não gates finais.

**Uma chamada** `PYTHONDONTWRITEBYTECODE=1 python3 -B
tests/smoke_resume_candidate_opencode.py`, wrapper de captura
`workflow-evidence record`, timeout externo 1.800 s/interno 360 s,
output/HOME/XDG/CODEX_HOME/DB/instalação novos e descartáveis.
Sem credenciais/config pessoais, override/fallback, pacote global ou mudança
de fonte/guard/permissões/pins. OpenCode **2.3.2**, OpenSpec **2.1.1**.
Metadata fresh `/api/model/default` cruzada com `/api/model`, mesmo ambiente/
Location: **`opencode/big-pickle`**, enabled/active chat, tools/text→text,
input/output/cache read/write conhecidos zero.
Guard fonte `b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`,
policy `805346fa19447ce3b639a34b239414a4f4378b421aa3757875eee78d72605477`,
ativação fresh exata antes da inferência preservada.

**Terminal real:** sessão `ses_dee7a654fffeTm0iHDWBZM9vOq`, PID 2597597,
exit **0**, `timed_out=false`, às `2026-11-25T07:07:49.737918+00:00`;
sem erro de provedor ou JSONL malformado. 18 step_finish/custo reportado **0**,
49 tool events. **Harness exit 1 em T1; T5/T7 NOT RUN**, nenhuma quinta
observação. Before/after disponíveis e iguais, forbidden_attempts vazio;
`model_proposal_proved=true`, mas `model_apply_gate_proved=false`,
`outcome=false`, `proof_complete=false`.

**Fatos e causa:** listagem read 21 e catálogo **realmente entregue** aceitos,
separadamente da invocação `skill(openspec-apply-change)` 39, com origem/path/
hash corretos. Captura prospectiva do próprio DB descartável correlaciona
sessão/baseline epoch=through=4, user seq5/assistant seq6 concluído,
blob `66f5a938235937b9e15fa3f01e95fbc82edb31fddcae5fd5ac499d969b769285`,
snapshot `dcecf52a262f9e663adc6a48f56bb694c4b57ad3eeafa49f195d4dc247e5391e`.
Isso é prova desta sessão, não metadata-only ou catálogo retrospectivo.
Strict 45 e proposta/review/cinco artefatos foram comprovados pelo matcher.
Porém Apply instructions 43 usou aspas não presentes no comando literal
permitido e foi negado; não houve chamada correta posterior. As tentativas
do runtime reader (17/24/30/48/49/54/55/65–67/84) omitiram os quatro argumentos
correlacionados ou usaram cwd/forma incorretos e foram negadas; **runtime_reads=[]**.
O recibo existe na preparação, mas não foi observado com sucesso pelo modelo.
O último JSON 87 afirma **BLOCKED**, next_action de bloqueio e blockers
não vazios; não é handoff RECOVERED. Não alterar aspas/allowlist/detector para
aprovar, nem tomar declaração de impossibilidade como prova de indisponibilidade
do comando completo permitido. Proposta fixture
`158409571e665455a939e5939845a6f64d08b6ed`, review fixture
`64d14dc1433dffb5e449ff7711445b5ed8ac6b01`, distintos da candidata/`31cdb42`.

**Prova** `evidence:ev-20261125T070455Z-8f203e55`, execution.log 602.230 bytes,
SHA-256 `5d2bcd7fed9236efee87bfd0b88849440b3949d1be44aa013d469535420ac179`,
retém resultados/preparação/snapshots, catálogo/proveniência, eventos/stderr/
terminal/guard/policy/audit/receipts checksum-bound. Verificado antes desta
nota **verified/failed**, exit 3/no_required_gate, com `--tool opencode=2.3.2
--tool openspec=2.1.1 --env-id sandbox=observe61-3a3fdaa-ses_deedf03e1ffe`.
Originais `/tmp/opencode/issue61-observe-3a3fdaa-ses_deedf03e1ffe`;
results SHA-256 `dfb0586e84ed3cc20129ebc788ea5b6450afa12a2e96166d1f4eb8b6ca815673`,
JSONL `d9babe0ed40a39aba58c099673ec0d6e88cd5cf01f7c36c3d0cb485aadd172ff`,
terminal `51566ce26c71ef12d9ec1c84ad463bb6fff082d32bc089aaac72d9a230d52478`.
Fase status=failed; top-level status/finished_at ausentes nessa falha de
asserção, preservados sem inferência de PASS.

**Parada:** diagnóstico pós-falha abaixo; nenhum retry/autofix/quinta
observação/archive/sync/suíte final/commit/push/PR/merge. Tarefas 3.4/4.3
pendentes; falhas anteriores e Dell UNKNOWN intactos. Próxima ação mínima:
revisão independente offline da usabilidade dos locators do recibo e dos
argv publicados, sem relaxar raw guard ou critérios e antes de qualquer
eventual decisão separada. Só esta nota fica dirty; HEAD/nove bytecodes
preservados, reserva devolvida ownerless **WAITING**, sem drift.

### Correção offline pós-terceira falha — catálogo, escopos e handoff

Writer `ses_deeb219ebffecKs4h8aN9D00bl`, stage
`workerfix61-catalog-handoff`, mesmo run/checkout/branch; entrada
`a9781ef7868be18c78bdaed51f7c2b9705706308`, nota dirty do observer
preservada. Reserva ownerless WAITING adquirida/verificada com ID nativo
real. Nova revisão independente `ses_dee9d76e4ffeR10I59JewObvEC`;
nenhuma quarta observação autorizada, nenhuma decisão material pendente.

**Diagnóstico completo complementar ao seq19, antes de testes novos:**
fase pós-terminal de asserção/fixture, não aplicação nem provedor. Modelo
`ses_deea391f8ffejSwAv3yVxrB5uY` terminou exit 0/custo reportado 0;
harness 1/T1, T5/T7 NOT RUN. HOME/XDG/DB/Location descartáveis, snapshots
disponíveis/iguais e recibo independente 62 não apagam tentativas proibidas.
Fonte de execução histórica `ev-20261125T061956Z-ed61de1e` permanece failed;
não acrescentar catálogo retrospectivamente ao bundle original.

- Descoberta: evento 8 é composto negado corretamente; **continua negado**.
  A fonte oficial OpenCode v2.3.2 `packages/core/src/skill/instructions.ts`
  (render 25–33, load 62–76) e docs `/docs/skills#loading` distinguem catálogo
  de IDs/nomes/descrições entregue em `core/skill-guidance` de corpos/path.
  Snapshot read-only da DB **desta fixture**, com backup SQLite próprio em
  `/tmp/opencode`, liga `instruction_state.initial_values` desta sessão ao
  blob `66f5a938235937b9e15fa3f01e95fbc82edb31fddcae5fd5ac499d969b769285`.
  Baseline epoch/through 4 precede user seq5/assistant seq6. Fonte oficial
  `session/instruction-state.ts` (`initial`) e `session/model-request.ts`
  (`baseTranscript`) explicam como o baseline é renderizado na requisição.
  Catálogo não prova path nem invocação: evento skill 71 e corpo/fonte canônica
  hash `71f084a1…503b79` os provam separadamente. Captura limitada nova é
  **nova evidência diagnóstica**, não dado já retido no log antigo.
- Ordem T1: design aprovado `31cdb42:design.md:41–43` e delta
  `specs/interrupted-workflow-resume/spec.md:41–43` exigem correlação e gate
  real, não strict/Apply instructions depois da skill. A ordem em seq19
  descrevia o **matcher então implementado**, não obrigação contratual.
  Strict 48/instructions 56 podem preceder skill 71, desde que todas as
  observações corretas da mesma sessão precedam o **handoff final**.
  Descoberta antes de invocação e ordem explícita T7 permanecem obrigatórias;
  não atribuir causalidade dos comandos anteriores à skill posterior.
- Falha real de handoff: proposta `4a67c868…`, review `7456d242…` e os cinco
  artefatos da fixture coincidem; dez probes reais bem-sucedidos. Design
  `31cdb42:design.md:49` separa candidata/origem/proposta fixture. Reset de
  checkboxes ocorre antes de proposta/review da fixture. Comparar tasks
  candidata `019aef5d…` com fixture `be3b9397…` como se fossem o mesmo escopo
  produziu resposta final 107 **“bloquear Apply”/“NÃO comprovado”**. Isso é
  falha real, não falso negativo; substring `Apply` não prova retomada.
  Clarificar metadados de fingerprint/transformação e disclaimer de seed;
  exigir handoff terminal de resultado explícito, correlacionado e coerente,
  sem juiz LLM, lista crescente de palavras ou hash/skill dirigido no prompt.
- Falha real de limite read-only: eventos 7/86/96 tentam `worktree-reservation
  verify`, todos negados pré-spawn; 96 usa ID truncado do observer, não ID
  nativo do modelo. `scripts/worktree-reservation:374–376` altera
  `verified_for`/`last_verified_at`. Classificador all-status deve incluí-lo
  e ser aplicado também a T1. Igualdade de snapshots não apaga tentativas.
  Status/listagem são leituras, verify/ownership são stateful; nenhum novo
  comando será permitido. T7 pré-escolha também rejeita verify.

Consumidores afetados: captura/prova de catálogo T1, âncoras de
`t1_proposal_proof`/`t1_apply_gate_proof`, agregação T1, metadados existentes
da fixture, resultado final e `forbidden_attempts` (também consumidor T7).
Guard raw/cwd/ambiente/permissões, produção/instalador/pins não mudam.
Alternativa mínima: **manter bloqueio** e não corrigir. Hipótese escolhida:
correlação nativa estável + escopos explícitos + handoff e tentativas
estritos eliminam falsos negativos sem aceitar o run realmente incorreto.
Trade-off: catálogo prova descoberta apenas, nunca conteúdo ou execução;
estado preparado sem assistant real não prova entrega. A nova projeção
retém só catálogo, links/timing nativos e hashes, nunca outros prompts.

Referências contratuais exatas no commit aprovado `31cdb42`:
`openspec/changes/issue-61-opencode-safe-resume/design.md:41–43,49` e
`openspec/changes/issue-61-opencode-safe-resume/specs/interrupted-workflow-resume/spec.md:41–43`.
São correções da implementação de prova sob esse contrato, não revisão de
aceite ou autorização para dispensar um gate real.

Seq18 continua FAILED, seq20 BLOCKED. O motivo técnico atual é
**environment / assertion-fixture local**, não dependência dura inventada.
Seq21 complementa o diagnóstico; check não final deve anteceder provas
novas. Nenhum replay é nova execução completa T1 ou retro-PASS. Próxima
ação após correção/provas offline: revisão afetada independente; eventual
observação futura exige autorização separada.

**Provas durante o diff (não gates finais):**

| Aceite / risco | Prova e limite |
| --- | --- |
| Catálogo entregue, não preparado; ID/descrição separados da fonte/path/hash nativos | `ev-20261125T064610Z-9babf9fd`: nova projeção limitada de snapshot SQLite read-only da fixture retida, blob e sessão exatos; invocação 71 ligada independentemente à fonte Apply canônica. Sem ler DB do operador ou outros blobs de instruções. |
| Handoff realmente recuperado, fontes antes da resposta final; verify all-status | `ev-20261125T064502Z-1217538e`: 39/39 offline, cinco testes novos com subcasos; cobre catálogo ausente/falso/outra sessão/fonte/ordem, CLI/review/tasks inválidos, comandos após handoff, JSON bloqueado/contraditório/escopo incorreto e verify negado/ID errado/cwd/global flags. Reusa negativos existentes T7/conteúdo/raw guard. |
| Trace real permanece FAILED após corrigir detector e ordem | `ev-20261125T065006Z-428cebe2`: inputs históricos com hashes originais intactos; catálogo → skill71, strict48 e Apply56 válidos antes de final107; cinco artefatos/proposta/review iguais. Final107 rejeitado e verify7/86/96 rejeitados, inclusive se um handoff hipotético corrigido for inserido **somente na cópia offline**. Não é PASS nem execução nova do cenário. |
| Prova nativa sem inferência e limite de preparação | Mesmo recibo: OpenCode 2.3.2, sessão metadata-only `ses_dee87ff83ffeOG8U573gxkswwi`, HOME/XDG/DB/Location novos. Apenas POST `/api/session` e GET `/api/skill`, sem prompt/generate/command/tool; zero mensagens/estado de instruções/tokens/custo. Deny-all torna o catálogo permitido vazio; captura recusa esse estado preparado. **Não** demonstra entrega positiva nessa sessão nova; a positiva vem exclusivamente do snapshot da sessão nativa histórica concluída. |
| Garantias de isolamento/T7/pins preservadas | Mesmo recibo compara bytes de guard factory/preflight/permissões, executor/captura/modelo, native_calls e conteúdo-boundary T7, T7 phase1/reinventory, T5 sources, guard/shim/instalador/skills com `a9781ef`. Prompts T5/T7 idênticos. Classificador anterior preservado como subconjunto e ampliado somente para operações stateful. Prompt T1 mantém roteamento natural e adiciona escopos/JSON de resultado, sem nomear skill nativa ou SHA esperado. |

O JSON terminal possui campos limitados e correlação de issue/run/escopo/
proposta/review, resultado/último gate/próxima ação/Apply não executado e
blockers; não admite prosa contraditória, campos extras/duplicados nem
aprovação do candidato real por seed. Ele **não substitui** nenhum tool
gate. Metadados existentes agora separam fingerprint de origem e da fixture
transformada, com propósito e transformação antes do commit/review; não são
uma nova fonte autoritativa.

Falhas intermediárias mantidas: `ev-20261125T064252Z-06309488` capturou o
catálogo, mas seu assert temporal inicialmente invertia step-start/first-token
(4219/4221 no mesmo messageID). Corrigida a relação efetiva **sem tolerância
artificial**, respeitando criação → step-start → first-token → término.
`ev-20261125T064854Z-a6193b61` criou sessão nativa sem inferência, mas esperou
catálogo não vazio sob deny-all; docs oficiais explicam que deny oculta IDs.
Mantido deny-all, removida a suposição incorreta, exigida recusa de preparado
sem entrega. Ambas são assertion/fixture dos diagnósticos offline, não falhas
de modelo, aplicação ou motivo para ampliar permissões.

Política `TEST_STRATEGY.md` contra `31cdb42`: `policy: ok`. Check não final
após seq21: valid=true/violations=[], seq18 blocked/wait_reason=environment.
Antes do commit, amostra focada reaplicável; após commit limpo, suíte offline
integral/focados/strict e replay serão registrados novamente como **pre-smoke
sem required gate**; IDs exatos fora do commit. SQLite é stdlib, sem dependência
nova. Nenhum executor shell nativo precisa ser repetido: guard raw/cwd/child
env e permissões continuam byte-idênticos. Nenhuma quarta inferência,
PR/push/archive/merge. Saída prevista limpa/ownerless WAITING; tarefas
3.4/4.3 e provas model-backed continuam pendentes.

### Terceira observação T1, após seq17 — 06:19–06:23 UTC, NOT READY

Autorização separada do coordenador/revisão afetada
`ses_def0f16a9ffeAEin2bLMykHlkm` no HEAD limpo
`a9781ef7868be18c78bdaed51f7c2b9705706308`. Antes desta terceira
observação foram lidos o diagnóstico completo pós-segunda falha seq17 e
`attempt-log check`: **valid=true/violations=[]**, não aprovação dos runs
anteriores. Worker real `ses_deedf03e1ffeIEi5jKBFwDgALP`,
`observe61-isolated`, mesmo run/checkout/branch; reserva ownerless WAITING
adquirida e verify/checkpoint/verify executados, sem drift/takeover.
Preflight reutilizou e verificou no HEAD exato: 290 offline
`ev-20261125T061448Z-e7d60e05`, 42 focados
`ev-20261125T061426Z-c6d012d0`, strict 13/13
`ev-20261125T061448Z-f51d60a2`, replay
`ev-20261125T061426Z-45ffbe99`, diagnóstico
`ev-20261125T061448Z-ccecf1b4`. Todos sem required gate, não gates finais.

**Uma chamada** `PYTHONDONTWRITEBYTECODE=1 python3 -B
tests/smoke_resume_candidate_opencode.py`, wrapper `workflow-evidence record`,
timeout externo 1.800 s/interno 360 s, output novo e HOME/XDG/CODEX_HOME/DB/
instalação descartáveis. Sem credenciais/config pessoais, override/fallback,
update global ou alteração de guard/permissões/pins. OpenCode **2.3.2**,
OpenSpec **2.1.1**. Consulta fresh nativa `/api/model/default` e `/api/model`
no mesmo ambiente/Location selecionou **`opencode/big-pickle`**:
chat enabled/active, tools/text→text, input/output/cache read/write conhecidos
zero. Guard fonte `b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`,
policy `fbb8f29bf4b19dd93343574cba93895afdc3b4029aa3c48b171dc1317b9ac7ee`,
ativação fresh comprovada antes de inferência e cleanup/disposed no audit.

**Terminal:** única sessão modelo `ses_deea391f8ffejSwAv3yVxrB5uY`,
PID 1971766, exit **0**, `timed_out=false`, às
`2026-11-25T06:23:00.558484+00:00`, sem erro de provedor/JSONL malformado;
25 step_finish/custo reportado **0**, 56 tool events. **Harness exit 1 em T1;
T5/T7 NOT RUN**, nenhuma quarta observação. Snapshots disponíveis e iguais;
`outcome=true` não substitui `proof_complete=false`,
`model_proposal_proved=false`, `model_apply_gate_proved=false`.

**Causa efetivamente observada:** a única tentativa de listagem, evento 8,
usou comando composto negado pelo guard. Não houve listagem shell/read
bem-sucedida antes da skill. Leituras diretas de SKILL.md 66–68 são conteúdo,
não descoberta aceita. `skill(openspec-apply-change)` foi realmente concluída
no evento **71**, com path/hash correspondentes, mas `t1_native_inspection`
rejeita a âncora por ausência de descoberta anterior; não dizer que a skill
tool não ocorreu. `skill(resume-workflow)` ocorreu no 2. Strict real no
**48** e Apply instructions no **56** precedem a invocação 71 e não foram
repetidos depois: também não satisfazem a ordem obrigatória dos gates
separados. Os dez probes de proposta/review/artefatos/diff tiveram exit 0,
saída esperada e sem truncamento (30,41–44,47,49,55,87–88), e o recibo
independente do writer foi consultado com sucesso no 62. Isso não completa
os gates faltantes. Proposta fixture
`4a67c868b843617486229b4104513f6155daea54`, review controlado fixture
`7456d242ae4bb566bfae3cb90258b78926d4036f`, distintos de candidata/`31cdb42`.
A resposta final bloqueia Apply por comparar o hash de tasks da candidata
com a fixture intencionalmente desmarcada, apesar do diff contra a proposta
da própria fixture limpo; relato não aprova nem muda as entradas.

**Prova** `evidence:ev-20261125T061956Z-ed61de1e`, execution.log 717.634 bytes,
SHA-256 `c6ceb8c694c4c15708057fd5e51a044b53b3d591282156f1c22727bcc788b12f`,
retém preparação/results/snapshots/eventos/stderr/terminal/guard/policy/audit/
receipts checksum-bound. Verificado antes desta nota **verified/failed**,
exit 3/no_required_gate, com `--tool opencode=2.3.2 --tool openspec=2.1.1
--env-id sandbox=observe61-a9781ef-ses_deedf03e1ffe`.
Originais `/tmp/opencode/issue61-observe-a9781ef-ses_deedf03e1ffe`;
results SHA-256 `40570081c758760049ed89638d02a3fae4133864f263c97bb2eddadd511f321f`,
JSONL `6d204d029c6d4cfb9a626024102d022c4e42d7ac1ce0aa4c592c7d3bf5901094`,
terminal `1fd607186b07395b7898b7ba4ace5ccffc7a7a5b5984a4f60104dccd10ce27a4`.
Fase status=failed; top-level status/finished_at ausentes nessa falha de
asserção, sem reconstrução ou inferência de PASS.

**Parada:** diagnóstico pós-terceira falha registrado abaixo antes de qualquer
eventual tentativa futura, que este worker **não** executa nem autoriza.
Nenhuma autocorreção/retry/archive/sync/suíte final/commit/push/PR/merge;
3.4/4.3 pendentes. Próxima ação mínima: revisão independente offline dos
eventos, ordem dos gates e separação dos SHAs da fixture, mantendo guard e
critérios, antes de decidir se existe correção contratualmente justificada.
Históricos failed/UNKNOWN intactos. Só esta nota fica dirty, HEAD e nove
bytecodes preservados; reserva devolvida ownerless **WAITING** sem drift.

### Correção offline — âncora de inspeção T1, sem terceira observação

Writer delegado `ses_deeb219ebffecKs4h8aN9D00bl`,
`workerfix61-inspection-anchor`, run `wf-20261116T064328Z-45cb0ecc`,
mesmo checkout/branch, entrada `ab9dcc93ddcc9f293f23209576d5659f8ec4d963`.
Reserva ownerless WAITING adquirida e verificada com ID nativo próprio;
nota dirty factual da segunda observação preservada integralmente. Os nove
bytecodes e os 38 commits anteriores continuam preservados. Política
`protocol/TEST_STRATEGY.md` comparada com `31cdb42`: `policy: ok`;
`openspec context/list --json` confirmam root e 14/16, sem init/update.

**Diagnóstico completo pós-segunda falha, antes de qualquer terceira T1:**
a revisão independente `ses_def0f16a9ffeAEin2bLMykHlkm` e a releitura dos
eventos de `ev-20261125T055329Z-ac05900b` identificam sobre-restrição da
implementação, não mudança do contrato aprovado. Design `31cdb42:41–43,61`
e delta `specs/interrupted-workflow-resume/spec.md:41–43` exigem inspeção
nativa correlacionada, proposta/review imutáveis e Apply como próximo gate,
**sem executar Apply**; não exigem somente o ID `openspec-apply-change`.
A skill oficial Explore local (`SKILL.md:15–17`) permite inspeção read-only
e é uma postura, não uma troca do próximo gate.

Fase efetiva: comparação de asserções **após** término do modelo em T1;
escopo: HOME/XDG/DB/Location descartáveis da candidata `ab9dcc93`, sem
config/credenciais pessoais; lifecycle: modelo
`ses_deebbcb22ffeLB1Vv1Mhuu9P50` exit 0, custo reportado 0, sem timeout/erro
de provedor; harness exit 1, T5/T7 NOT RUN. Snapshots disponíveis e iguais
não são aprovação de tentativas. Consumidores: seleção T1 de
`native_calls`, âncora temporal de `t1_proposal_proof` e gate agregado.
Nenhum defeito de aplicação/produção foi demonstrado.

Na execução fonte, descoberta 45/49 precede a skill tool Explore 57, origem
não symlink/hash `e776f0d8b5e36d2e5fd8149254a95c54008942bd4336d1c67e568c67e45ddcca`
igual à fonte candidata. Os dez probes 77–81/114–116/120–121 e strict 113
tiveram exit 0, saída integral correta; Apply instructions 117 identifica o
change correto, `ready`, 0/16 e tasks da fixture. Recibo independente 102
correlaciona writer/owner/run/checkout e terminal. Resposta 163 identifica
última proposta/review/validação e Apply próximo, não executado. Tasks da
fixture são desmarcadas em `:992–995`: seu SHA distinto do source é esperado;
os cinco artefatos coincidem com a proposta **da fixture**. Não expandir
comandos para satisfazer lacunas declaradas pelo modelo.

Seq9 teve dois mecanismos reais: listagem de diretório excluída e ausência
de verificação efetiva da proposta/review/strict pelo modelo. Seq13 já tem
essas fontes verificadas, mas a âncora Apply-only exclui a inspeção Explore.
São mecanismos distintos, não renomeação para contornar limite. Seq9 é
histórico **PROGRESSED**, nunca passed; seq13 continua **BLOCKED**. HTTP 400
e observer Dell UNKNOWN continuam intactos.

Alternativa mínima compatível: manter bloqueio sem corrigir. Hipótese
escolhida: aceitar **somente** `openspec-explore` ou `openspec-apply-change`
como inspeção T1, cada qual vinculada à fonte/path/hash/sessão e descoberta
anterior; manter skill tool real, nunca read/CLI/prosa. Separadamente exigir
Apply instructions bem-sucedido do change/tasks corretos, mais todos os
probes imutáveis e strict pós-inspeção e relato Apply próximo. Explore com
prosa sozinha não prova RECOVERED. Trade-off: remove falso negativo sem
trocar inspeção por handoff nem afrouxar segurança. T7 e guard/permissões,
prompts, pins e fontes R1–R4 não precisam mudar.

O seq17 abaixo registra este diagnóstico antes de testes/replay da correção;
`attempt-log check` não final deve ser executado antes deles. Replay offline
não é nova execução nativa/model-backed nem retroaprovação do run falho.
Sem inferência autorizada neste writer; revisão afetada e eventual observação
nova cabem separadamente ao coordenador.

**Provas da correção durante o diff, não gates finais:**

| Aceite/risco afetado | Menor prova / resultado |
| --- | --- |
| Duas alternativas exatas, fonte/path/hash/sessão/ordem próprios; read/prosa/skill alheia não substituem invocação | `ev-20261125T061101Z-3d4b49a7`: 34/34 em `test_resume_reinventory.py` (inclui cinco testes novos, com subcasos). Mesmo resultado inicial em `ev-20261125T060901Z-8094b2cf`. |
| Apply próximo não se deduz de Explore nem de `ready` declarativo | Mesmo grupo: gate separado exige CLI exit 0, sem truncamento, sessão/cwd/ordem corretos, change/schema/contextFiles exatos, tarefas com id/descrição/linha/sourcePath/done e progresso correspondentes ao tasks imutável. Proposta/review/cinco artefatos/strict e relato Apply continuam gates adicionais. |
| Regressão observada no trace retido, sem fabricar execução | `ev-20261125T061141Z-267e3387`: replay offline dos inputs reais com os três hashes históricos conferidos, Explore 57 após descoberta 45/49; checks de proposta e Apply separados verdadeiros; 12 negativos rejeitados (ausência/invocação/sessão/skill/ordem/descoberta/strict/review/Apply não comprovado/change/tasks/prosa). Inputs originais inalterados, registro histórico failed/false intacto. |
| Preservação R1–R4/T7/pins sem nova superfície shell | Mesmo replay compara bytes com `ab9dcc93`: `native_calls`, permissões, guard factory/preflight, detector all-status, T7 phase1/reinventory, T5 sources, modelo/execução/captura, `t1_proposal_proof`, prompts e arquivos guard/shim/instalador/skills idênticos. Guard `b8788477…`, instalador `93cd9371…`. Não há justificativa para repetir executor nativo nem expandir guard/comandos. |

O primeiro replay `ev-20261125T061101Z-67b3f88c` falhou **somente** na
asserção de byte-identidade: um espaço de indentação em
`t1_proposal_proof` diferia do baseline. A comparação AST/source localizou
esse único delta entre as definições preservadas; restaurado o byte original,
o replay acima passou. Não era falha de modelo, CLI, permissão ou aplicação.
O log recuperável do replay aprovado contém script e inputs reais, não só
locators `/tmp`; nenhuma prova histórica foi reclassificada.

`attempt-log check` não final após seq17: exit 0, `valid=true`,
`violations=[]`, seq9 `progressed`, seq13 `blocked`, `wait_reason=dependency`.
Isso valida estrutura/diagnóstico, **não** autoriza inferência ou libera
entrega. No HEAD limpo após o commit, registrar novamente focados completos
(retomada + raw guard), suíte offline integral e strict como **pre-smoke**,
sem required gate; IDs exatos ficam no retorno ao coordenador, fora do commit.
Suite discovery/Python stdlib e Node da fixture são os consumidores offline;
sem Magento/M2T/lockfile de aplicação ou dependência nova. T1 permanece
FAILED/NOT PROVEN, T5/T7 NOT RUN, tarefas 3.4/4.3 pendentes. Estado de saída:
checkout limpo e reserva ownerless WAITING, sem push/PR/archive/merge.

### Nova observação revisada — 05:53–05:57 UTC, NOT READY

Autorização separada do coordenador após revisão afetada
`ses_def0f16a9ffeAEin2bLMykHlkm` do HEAD limpo
`ab9dcc93ddcc9f293f23209576d5659f8ec4d963`, não retry automático de
`ea49c81` nem aprovação retroativa de `ev-20261125T051622Z-335af867`.
Worker real `ses_deedf03e1ffeIEi5jKBFwDgALP`, `observe61-isolated`,
mesmo run `wf-20261116T064328Z-45cb0ecc`/checkout/branch; reserva
ownerless WAITING adquirida, verify/checkpoint/verify executados.
Reutilizadas provas do HEAD exato: offline 285
`ev-20261125T054618Z-96deec76`, focados 37
`ev-20261125T054751Z-1dab0487`, executor nativo 12 allow/21 reject
`ev-20261125T054618Z-3ee0cff6`, strict 13/13
`ev-20261125T054618Z-7630f32a`; todas verificadas com os respectivos
tool IDs, sem required gate, não suíte final.

Uma chamada efetiva `PYTHONDONTWRITEBYTECODE=1 python3 -B
tests/smoke_resume_candidate_opencode.py`, sem argumentos, em wrapper
`workflow-evidence record`, timeout externo 1.800 s/interno 360 s.
HOME/XDG/CODEX_HOME/DB/instalação descartáveis, manifesto no HEAD exato,
sem credenciais/config pessoal/override/fallback/update global.
OpenCode **2.3.2**, OpenSpec **2.1.1**. Fonte nativa fresh
`/api/model/default`, cruzada com `/api/model` no mesmo Location/ambiente:
**`opencode/big-pickle`**, enabled/active chat, tools/text→text e todos os
preços input/output/cache read/write conhecidos zero.
Guard fonte SHA-256
`b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`,
policy `bee531e2b2619ff67dcaa429c0fa05496319a5d2b93e3c668e7d5be2f2444345`;
ativação fresh exata antes de inferência e setup/active/cleanup do modelo
no audit. Rejeições permanecem pré-spawn; allowlist não foi alterada.

**Terminal:** modelo `ses_deebbcb22ffeLB1Vv1Mhuu9P50`, PID 1512799,
exit **0**, `timed_out=false`, às `2026-11-25T05:57:29.505964+00:00`;
sem erro de provedor/JSONL malformado. 28 `step_finish`, custo reportado **0**,
102 tool events. **Harness exit 1 em T1; T5/T7 NOT RUN**, nenhum segundo
modelo. Snapshots before/after disponíveis e iguais em todas as dimensões;
`outcome=true`, mas `proof_complete=false`, `model_proposal_proved=false`.

**Achado factual, sem corrigir detector:** descoberta shell eventos 45/49;
`skill(resume-workflow)` evento 2 e **`skill(openspec-explore)` evento 57**
bem-sucedidos. O matcher T1 está vinculado ao path/hash/name de
**`openspec-apply-change`**, cuja invocação não ocorreu (`native_invocation=[]`);
ler seu arquivo e executar CLI não substituem a skill tool. Todos os dez
probes de commit/ancestralidade/review/cinco artefatos/diff realmente tiveram
exit 0, saída esperada, sem truncamento (77–81, 114–116, 120–121).
Strict canônico no 113 também exit 0/saída esperada após Explore.
O agregado de proveniência ainda rejeita por falta da invocação vinculada,
não por ausência daqueles probes. Recibo independente correlacionado do
writer foi consultado no 102, terminal true/exit 0. Proposta fixture
`f885370afc0913c9bf6e11e18748cc3476e9be89`, review controlado fixture
`ee5cc33c19fb6351822053996121056f2fe279ae`, distintos da candidata e `31cdb42`.
Relato do modelo também aponta diferenças entre hashes de tasks da candidata
e da fixture com tarefas desmarcadas; não alterá-los ou expandir comandos.
Revisão independente deve confrontar skill aplicável read-only e matcher
pinado antes de qualquer correção; este worker não decide aceitação por prosa.

**Prova** `evidence:ev-20261125T055329Z-ac05900b`, execution.log 788.387 bytes,
SHA-256 `37ca4658fec659560a303e9f79546b1e01bbf0df6567ddd8ed48f94f8dcfeca4`,
retém preparação/results/snapshots/eventos/stderr/terminal/guard/policy/audit/
receipts checksum-bound. Verificado antes desta nota: `verified/failed`,
exit 3 `no_required_gate`, com `--tool opencode=2.3.2 --tool openspec=2.1.1
--env-id sandbox=observe61-ab9dcc9-ses_deedf03e1ffe`.
Originais `/tmp/opencode/issue61-observe-ab9dcc9-ses_deedf03e1ffe`;
results SHA-256 `bf3284f428652d2f6e19087f9d073bdd79847d5b83d64bee9c871a8b6da5e786`,
JSONL `a7f9811717c024ed9c234e43d4389e43ae3941f7cdb99e828eb2e6ddd9b7dbf5`,
terminal `f106ac4c2afa9a282796d394eef451feafa22b17ce6b50303d176103a9a5bad3`.
Fase `status=failed`; top-level status/finished_at ausentes nessa falha de
asserção, preservados sem inferir PASS.

**Parada:** sem autocorreção/retry, archive/sync, suíte final, commit,
push/PR/merge. 3.4/4.3 continuam pendentes; histórico 400 e Dell UNKNOWN
intactos. Próxima ação: revisão independente dos eventos e da vinculação da
skill aplicável. Só esta nota fica dirty, HEAD preservado; reserva devolvida
ownerless **WAITING**, sem drift, nove bytecodes preservados.

### Correção offline T1 — descoberta e proveniência, sem nova inferência

Writer delegado `ses_deecfd284ffeAQqQpQZa0BoTGX`,
`workerfix61-T1-correlation`, mesmo run/checkout/branch, entrada `ea49c81`.
Reserva ownerless WAITING adquirida com ID nativo próprio e verificada;
nota dirty do observer abaixo preservada e estendida, sem aceitar drift.
Os nove bytecodes continuam preservados. Escopo exclusivo: harness, regressões
e este handoff. Sem produção, instalador, pins, pacote global, credenciais,
PR/push/merge, archive/sync ou nova observação model-backed.
`protocol/TEST_STRATEGY.md` comparado com `31cdb42`: `policy: ok`; políticas
canônicas atuais e skills oficiais locais prevalecem sobre o global antigo.
`context/list/status/instructions apply` oficiais confirmam este root,
schema `spec-driven`, **14/16**; 3.4/4.3 continuam abertas. `state=ready`
do OpenSpec não comprova review imutável nem autoriza declarar teste aprovado.

**Diagnóstico independente recebido:** revisão
`ses_def0f16a9ffeAEin2bLMykHlkm`, tentativa consumida
`ev-20261125T051622Z-335af867`. A releitura offline recuperável
`ev-20261125T053935Z-6d9799ef` confirma dois problemas distintos:

- **Detector:** evento 31 é `read` bem-sucedido do diretório canônico
  `.agents/skills`, com entrada exata `openspec-apply-change/`, antes da
  invocação nativa 57. Leituras de conteúdo 51–53 não são descoberta nem
  invocação. A correção aceita somente o envelope nativo de listagem,
  diretório solicitado correto, sessão/status corretos e ordem anterior
  à invocação. Skill tool continua sendo a única invocação.
- **Proveniência faltante, não só SHA ausente na resposta:** a proposta
  `5ac5413e79b2a83656fdafa3ed4433bdae6beaa7` é ancestral real e todos os
  cinco artefatos atuais coincidem, conferidos pelo harness. Porém a sessão
  do modelo só leu o SHA declarativo no evento 30 e na issue 38; não
  inspecionou commit/review. Strict nos eventos 63/69/133 foi **negado**
  por argv diferente da allowlist. Isso não é validação executada.
  Fatos conferidos pelo executor não são observações feitas pelo modelo.

**Preservação de contrato (design 33/43/49/61):** substituir o fraco eco de
SHA na resposta por exigência **adicional e obrigatória de ferramentas**:
commit exato, ancestralidade proposta→review→HEAD, leitura Git de todos os
artefatos, diff zero dos artefatos contra a proposta, review imutável
correlacionado a SHA/hashes/validação, e strict bem-sucedido depois da skill.
Issue/run/Apply na resposta e todos os demais gates continuam obrigatórios.
Somente leitura declarativa, prosa/echo, commit/review/artefatos diferentes,
falha/ausência de exit, truncamento, sessão/cwd errados ou validação anterior
à invocação não aprovam. Não há requisito aprovado de repetir literalmente
o SHA na resposta final; não foi dispensada a correlação real.

O review semeado é explicitamente `controlled_fixture_seed`,
`fixture-reviewer`, não uma alegação de aprovação independente da candidata
real. Seu commit Git distinto fixa decisão, proposta, hashes e resultado
strict real da preparação. SHA da candidata instalada, proposta fonte
`31cdb42`, proposta da fixture e review da fixture são campos distintos.
`recovery-evidence.json` publica somente locators/comandos; fatos derivados
do Git ficam em `fixture_proposal_facts`, observações do modelo em
`model_proposal_proved`, sem confundi-los.

Allowlist prospectiva mínima: comandos literais `git show --format=%H
--no-patch <proposal>`, dois `git merge-base --is-ancestor`, `git show
<review>:<review-path>`, um `git show <proposal>:<artifact>` para cada artefato
e `git diff --exit-code <proposal> -- <change-root>`, **somente no cwd raiz
da fixture**. Nenhum `git show` genérico, wildcard, interpretador arbitrário,
export/env/composto ou argumento extra. O strict canônico existente
`openspec validate issue-61-opencode-safe-resume --strict --no-interactive`
fica publicado explicitamente; variantes negadas no run anterior continuam
negadas e são negativos da prova nativa. Não há relaxamento por prefixo.
Os dois hooks raw pré-spawn e substituição do ambiente ficam intactos.
T7 pré-escolha continua permitindo listagem, proibindo conteúdo/invocação
inclusive failed/cancelled, sem alteração de política ou skill de produção.
Prompt T1 só acrescenta confronto natural de fontes/revisão/validação,
sem nomear `resume-workflow`, SHA esperado ou lookup nativo dirigido.

**Provas durante a correção, ainda com diff (não gates finais):**

| Evidência | Resultado e limite |
| --- | --- |
| `ev-20261125T053654Z-24269ff7` | 36/36 offline antes do ajuste do envelope vazio. |
| `ev-20261125T053701Z-e632fccb` | Prova nativa falhou no assert de saída vazia: exit 0 real retornou `(no output)`, não `""`; nenhuma inferência. |
| `ev-20261125T053809Z-80f9bfe0` | 37/37 offline; negativos de listagem, proveniência e captura vazia/exit/truncamento. |
| `ev-20261125T053809Z-b1276c50` | Executor nativo 2.3.2, sessão `ses_deec9da27ffe3n6CD1yH6V9R39`: 12 leituras exatas permitidas (inclui strict real) e 21 rejeições pré-spawn; zero mensagens/tokens/custo, bytes do repo e ambiente do operador inalterados. |

A falha intermediária foi diagnosticada como **assertion/fixture**, fase de
comparação pós-executor, não autorização nem CLI: fonte oficial v2.3.2
`packages/core/src/{tool/plugin/shell.ts,shell/result.ts}` e captura nativa
mostram o marcador de stream vazio. Alternativa mínima seria manter bloqueio;
correção escolhida reconhece `(no output)` somente quando o resultado esperado
é vazio **e** exit terminal é 0, sem truncamento. Unit negativo rejeita o mesmo
marcador sem exit/exit≠0. Prova nativa seguinte confirmou strict e todas as
rejeições, sem marker fsmonitor ou progress de spawn nos negativos.
Documentação oficial V2 de plugins/server e fonte do executor foram
reconsultadas; o bridge existente chama `ctx.tool.list().find(id=shell).execute`,
não dispatcher/modelo. Fontes/policy/audit/resultados/log nativo ficam em
stdout checksum-bound de `workflow-evidence`, originais em
`/tmp/opencode/issue61-correlation-native2-ses_deecfd284ffe`.
Revisão da serialização detectou variável de loop sobrescrevendo o envelope
`native_results` impresso: corrigida antes do commit. A prova com diff acima
tem audit/proof/log completos, mas imprime só o último resultado individual;
o arquivo original contém todos. Exigir a nova prova no HEAD limpo com
envelope integral checksum-bound, sem atribuir esse complemento à antiga.

**Handoff:** registrar/verificar novamente suíte offline e prova nativa no
HEAD limpo após este commit; IDs ficam fora do commit conforme TEST_STRATEGY.
São provas **pre-smoke sem required gate**, não fechamento da entrega.
Solicitar ao mesmo revisor independente inspeção das superfícies afetadas,
proveniência/allowlist/provas; só depois cabe ao coordenador autorizar
**uma observação separada**, se segura. Este writer não lança modelo nem
retry. T1 atual continua **FAILED/NOT PROVEN**, T5/T7 **NOT RUN**; nenhuma
aprovação retroativa. Recibo Dell/observer antigo permanece **UNKNOWN**.
Devolver checkout limpo com reserva ownerless **WAITING**; nada arquivado.
O receipt de verify foi consumido pelo checkpoint intermediário; antes de
novo checkpoint/commit, renovar no baseline exato, preservando e reaplicando
somente o delta próprio com hashes conferidos, sem aceite de drift e sem
descartar a nota herdada do observer.

### Observação única residual — 05:16–05:19 UTC, NOT READY

Worker real `ses_deedf03e1ffeIEi5jKBFwDgALP`, `observe61-isolated`,
run `wf-20261116T064328Z-45cb0ecc`, mesmo checkout/branch, HEAD limpo
`ea49c81a3a40daa54f1d2f04b3fda10aeaf85a74`. Reserva ownerless WAITING
adquirida/verificada com essa identidade; nove bytecodes/histórico preservados.
Proposta `31cdb42` e revisão independente informada
`ses_def0f16a9ffeAEin2bLMykHlkm` autorizavam uma observação, sem merge.
Políticas atuais do checkout prevalecem sobre o pacote global antigo:
sem audit/ready, ledger novo, comentários rotineiros ou outra issue.
AUTO-IF-GREEN posterior cabe ao gate independente do coordenador.
Provas do mesmo HEAD verificadas e reutilizadas: 279 testes offline
`ev-20261125T050925Z-18d70bf7` e 31 focados
`ev-20261125T050925Z-bf589b97`, sem required gate, não suítes finais.
Instalador/pins inalterados; sem M2T/lockfile de aplicação relevante.

**Comando:** `PYTHONDONTWRITEBYTECODE=1 python3 -B tests/smoke_resume_candidate_opencode.py`,
sem argumentos, wrapper `workflow-evidence record`, timeout externo 1.800 s,
interno 360 s/turno. Instalação/manifesto/skill no HEAD exato em HOME/XDG/
CODEX_HOME/DB descartáveis, sem configuração/credenciais pessoais.
OpenCode **2.3.2**, OpenSpec **2.1.1**, Python **3.14.8**.
Imediatamente antes da inferência, no mesmo ambiente/Location,
`/api/model/default` selecionou **`opencode/big-pickle`**, confirmado em
`/api/model`: chat enabled/active, tools=true, text→text, todos os preços
input/output/cache read/write conhecidos e zero. Nenhum override/fallback.
Fonte do guard privado SHA-256
`b878847767fd9759d7362a6aa71707b4e13f97606258f39448c82b23f255e656`,
policy `9d8f3d2f545804da7f9836f11318eb4947bf49309061cb8bb76dfb5de7782935`;
ativação fresh da fonte exata comprovada antes do modelo. Audit também
registra setup/active do modelo, comandos literais aceitos nos dois hooks,
compostos/argv/cwd alheios rejeitados pré-spawn e cleanup/disposed.
Allowlist não foi afrouxada.

**Resultado:** harness exit **1**, T1 `proof_complete=false`, `outcome=false`;
**T5/T7 NOT RUN**. Única sessão model-backed
`ses_deeddc510ffe4gvwkMrfPETB0I`, processo 1036247, terminal exit **0** às
`2026-11-25T05:19:54.686012+00:00`, sem timeout, JSONL malformado ou evento
de erro de provedor. Os 34 `step_finish` reportam custo zero, não zero tokens.
Falha no primeiro gate de cenário: `native_discovery=[]` e resposta sem
SHA/prefixo exigido da proposta da fixture
`5ac5413e79b2a83656fdafa3ed4433bdae6beaa7`.
Existe listagem via `read .agents/skills` no evento 31, mas `native_calls`
aceita descoberta somente por glob/shell: analisar independentemente
contrato/detector, não converter em PASS. Existem invocação natural
`skill(resume-workflow)` no evento 2, `skill(openspec-apply-change)` no 57,
`openspec instructions apply` no 70 e consulta do recibo independente
`writer-T1-61` com owner/run/checkout corretos e terminal true no 130.
Não preenchem os critérios faltantes. **Snapshots before/after disponíveis
e iguais**, incluindo Git/checkouts/reservas/OpenSpec/GitHub/receipts.
Igualdade não prova ausência de tentativa: os comandos negados ficam no audit.
Falha atual de prova/assertion é distinta do HTTP 400 histórico; nenhum novo
400/429/timeout. Não houve segunda observação ou autocorreção.

**Prova:** `evidence:ev-20261125T051622Z-335af867`, execution.log 633.790 bytes,
SHA-256 `9276633f6ce364119365fddea81e11d1c26dc69112cb72203490321e79938c8c`,
retém results/preparação/snapshots, JSONL/stderr/terminal, guard/policy/audit
e receipts em stdout checksum-bound, não somente caminho temporário.
Verificado antes desta anotação com `--tool opencode=2.3.2 --tool
openspec=2.1.1 --env-id sandbox=observe61-isolated-ses_deedf03e1ffe`:
`state=verified/result=failed`, exit 3 `no_required_gate`.
Originais em `/tmp/opencode/issue61-observe-ses_deedf03e1ffe`.
`results.json` SHA-256
`1adfc9018c18e2feda616a4e477b25edfae3a87d2ea48f1ac704fe311b39e63a`;
JSONL `f46df518d0aababd7b5f7c837fde16320fade50be1574b5228ceb93067c055ca`;
terminal `b38a665c8e2d93ec59c3787e35a7ed1ccdea85043f41c920f3857ea23c9c1fb3`.
A fase registra `status=failed`; top-level `status`/`finished_at` ausentes
na falha de asserção, sem reconstruí-los nem inferir PASS.

**Parada:** tarefas 3.4/4.3 pendentes; sem archive/sync, suíte final,
commit/push/PR/merge. Próxima ação mínima: revisão independente dos eventos
e critérios faltantes, preservando prompt natural e guard, antes de qualquer
correção/execução separadamente revisada. Só esta anotação permanece dirty,
deliberadamente sem commit; a execução falha torna-se documentalmente stale,
não gate final. Checkpoint inicial da nota foi recusado por receipt de verify
consumido pelo checkpoint anterior: restaurada somente a própria anotação,
confirmado diff zero, verify renovado e nota reaplicada; sem aceite de drift.
Checkout retido e reserva devolvida a **WAITING**.

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
{"kind":"resolution","group":{"obligation":"T1","signature":"provider.invalid-request: upstream request failed: model is unavailable"},"outcome":"blocked","via_seq":8},
{"kind":"attempt","seq":9,"obligation":"T1","signature":"assertion: recovery proof incomplete; native discovery absent and response missing proposal sha","target":"ea49c81 T1 phase1 opencode/big-pickle","class":"assertion/contract","hypothesis":"reviewed guard and current native eligible default support complete natural recovery proof","change":"reviewed R1-R4 harness at exact clean HEAD; native model default revalidated without override","change_target":"test","observed_effect":"harness exit 1 after model exit 0; native_discovery empty and outcome false; before/after equal and available; T5/T7 not run","result":"fail","evidence":["evidence:ev-20261125T051622Z-335af867"]},
{"kind":"diagnosis","seq":10,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; native discovery absent and response missing proposal sha"},"class":"assertion/contract","checked":{"phase":"post-terminal T1 proof assertions, not provider/bootstrap; directory read event31 excluded by glob/shell discovery matcher; response lacks fixture proposal prefix","scope":"same isolated HOME/XDG/DB/Location and exact installed ea49c81 candidate; no operator credentials or model override","lifecycle":"native ses_deeddc510ffe4gvwkMrfPETB0I exit0 without timeout/provider error; outer harness exit1 and no next scenario; snapshots available/equal","consumers":"native_calls and T1 outcome matcher; successful natural resume skill, native Apply skill, instructions and independent writer receipt do not satisfy missing criteria"},"runtime_proof":["evidence:ev-20261125T051622Z-335af867"],"simplest_alternative":"retain failure and independently inspect directory-listing discovery semantics plus missing proposal correlation without another model","choice_rationale":"approved one-observation budget consumed; no guard relaxation, autocorrection, fallback or second observation authorized","next_hypothesis":"independent evidence review can distinguish discovery detector mismatch from response-correlation failure before any separately reviewed fix"},
{"kind":"blocker","seq":11,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; native discovery absent and response missing proposal sha"},"type":"technical","wait_reason":"dependency","evidence":["evidence:ev-20261125T051622Z-335af867"],"diagnosis":"seq:10","options":[],"impact":"T1 failed proof; T5/T7 not run; tasks 3.4/4.3 pending; no archive/final delivery suite/PR; independent event review needed","researchable":true},
{"kind":"resolution","group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; native discovery absent and response missing proposal sha"},"outcome":"blocked","via_seq":11},
{"kind":"diagnosis","seq":12,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; native discovery absent and response missing proposal sha"},"class":"fixture/isolation","checked":{"phase":"post-terminal assertion plus model source inspection: directory event31 genuinely discovers before skill57; proposal commit/review uninspected; strict63/69/133 denied exact argv","scope":"same historical isolated fixture; actual Git ancestor and five artifact hashes independently checked; factual verification is separate from model-observed evidence","lifecycle":"historical model exit0 and harness exit1 preserved; no new inference; offline native bridge exits successfully with zero messages/tokens/cost; no dispatcher claim","consumers":"native_calls directory detector and T1 provenance matcher; raw tool/shell hooks unchanged; T7 prechoice content and failed/cancelled guard unchanged"},"runtime_proof":["evidence:ev-20261125T051622Z-335af867","evidence:ev-20261125T053935Z-6d9799ef","evidence:ev-20261125T053809Z-b1276c50"],"simplest_alternative":"retain failed proof; never drop final-SHA echo alone or substitute OpenSpec ready for immutable review","choice_rationale":"approved design requires real commit/artifact/validation/review correlation, not literal final response SHA; add exact bounded read-only sources and require same-session successful probes; fixture review explicitly controlled seed not real candidate approval","next_hypothesis":"after affected independent review, a separately authorized observation may prove native directory discovery and all immutable provenance probes plus strict canonical command; offline proof does not approve T1"},
{"kind":"attempt","seq":13,"obligation":"T1","signature":"assertion: recovery proof incomplete; native apply invocation absent after successful explore invocation","target":"ab9dcc93 T1 phase1 native default","class":"assertion/contract","hypothesis":"separately reviewed discovery and provenance fixes enable complete T1 observed proof","change":"approved ab9dcc93 directory discovery and immutable proposal probes; current native model metadata revalidated","change_target":"test","observed_effect":"native exit0, harness1; discovery and all ten proposal probes plus strict succeed; skill Explore invoked but designated Apply absent; snapshots available/equal; T5/T7 not run","result":"fail","evidence":["evidence:ev-20261125T055329Z-ac05900b"]},
{"kind":"diagnosis","seq":14,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; native apply invocation absent after successful explore invocation"},"class":"assertion/contract","checked":{"phase":"post-terminal native_calls matches Apply path/hash/name; actual skill Explore at57; strict113 and all provenance probes succeeded but aggregate requires designated invocation","scope":"new isolated HOME/XDG/DB at installed ab9dcc93; no personal credentials/config; exact raw guard activation and native default zero pricing","lifecycle":"ses_deebbcb22ffeLB1Vv1Mhuu9P50 terminal exit0 without timeout/provider error; harness exit1; no next scenario; snapshots available/equal","consumers":"T1 native matcher and t1_proposal_proof invocation anchor; successful read/CLI and prose do not substitute skill tool"},"runtime_proof":["evidence:ev-20261125T055329Z-ac05900b"],"simplest_alternative":"retain failed proof and independently compare applicable read-only native skill with pinned matcher before any change","choice_rationale":"one new observation consumed; no self-correction or second model authorized; retain all failed episodes and raw streams","next_hypothesis":"independent contract/event review can resolve designated Apply versus observed Explore without altering guard or inventing PASS"},
{"kind":"blocker","seq":15,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; native apply invocation absent after successful explore invocation"},"type":"technical","wait_reason":"dependency","evidence":["evidence:ev-20261125T055329Z-ac05900b"],"diagnosis":"seq:14","options":[],"impact":"T1 failed; T5/T7 not run; no archive/final local suite/PR; independent review needed","researchable":true},
{"kind":"resolution","group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; native apply invocation absent after successful explore invocation"},"outcome":"blocked","via_seq":15},
{"kind":"diagnosis","seq":17,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; native apply invocation absent after successful explore invocation"},"class":"fixture/isolation","checked":{"phase":"post-terminal T1 assertions: ls45/49 before Explore skill57; ten immutable probes77-81/114-116/120-121 and strict113 succeed; Apply instructions117 correct change ready0/16; final163 reports last proposal/review/validation and Apply next not executed","scope":"ab9dcc93 isolated HOME/XDG/DB/Location; Explore source non-symlink hash e776f0d8b5e36d2e5fd8149254a95c54008942bd4336d1c67e568c67e45ddcca matches candidate; fixture tasks intentionally reset992-995 and all five artifacts match fixture proposal","lifecycle":"ses_deebbcb22ffeLB1Vv1Mhuu9P50 exit0/cost0 without timeout/provider error; harness1; snapshots available/equal; receipt102 terminal correlates writer/owner/run/checkout; T5/T7 not run; no new inference","consumers":"T1 native_calls selection and t1_proposal_proof anchor plus separate RECOVERED gate; assertion/fixture not application; seq9 discovery false-negative plus genuinely absent proposal verification differs from seq13 Apply-only false-negative; historical seq9 progressed not passed and seq13 blocked; T7/all-status boundaries and R1-R4/raw guard unchanged"},"runtime_proof":["evidence:ev-20261125T055329Z-ac05900b"],"simplest_alternative":"retain failed proof and stop without another observation; do not substitute Explore-plus-prose for verified Apply readiness","choice_rationale":"independent review ses_def0f16a9ffeAEin2bLMykHlkm confirms existing approved design31cdb42 requires correlated native inspection not Apply-only ID; exact Explore or Apply inspection alternatives preserve source/path/hash/session/discovery ordering while separate successful correct-change Apply instructions/tasks plus immutable probes/strict and reported handoff retain guarantee; no owner decision/replan or guard expansion","next_hypothesis":"bounded T1 inspection anchor removes implementation false-negative while independent Apply readiness rejects Explore-only/prose/unproved or mismatched change; prove offline with retained actual trace and negatives, not new native completion or retroactive PASS"}
,
{"kind":"attempt","seq":18,"obligation":"T1","signature":"assertion: recovery proof incomplete; no successful discovery and gate commands before native invocation","target":"a9781ef T1 phase1 native default","class":"assertion/contract","hypothesis":"reviewed inspection alternatives with separate Apply gate prove complete T1 after seq17 diagnosis","change":"approved a9781ef native inspection selection plus separate mandatory Apply instructions gate; fresh native default metadata and guard activation","change_target":"test","observed_effect":"model exit0/harness1; actual Apply skill71 has no successful prior listing; strict48 and Apply instructions56 occur before skill; all ten proposal probes and receipt62 succeed; snapshots available/equal; T5/T7 not run","result":"fail","evidence":["evidence:ev-20261125T061956Z-ed61de1e"]},
{"kind":"diagnosis","seq":19,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; no successful discovery and gate commands before native invocation"},"class":"assertion/contract","checked":{"phase":"post-terminal T1 proof: composed discovery command8 denied; direct content reads66-68 do not prove directory discovery; completed native Apply71 lacks earlier successful discovery; strict48 and Apply instructions56 are pre-invocation with no later repetitions","scope":"a9781ef exact installed isolated HOME/XDG/DB/Location; native default big-pickle eligible known zero; raw guard source unchanged and fresh activation; no operator config/credentials","lifecycle":"ses_deea391f8ffejSwAv3yVxrB5uY exit0/cost0 without timeout/provider error; harness1 terminal; T5/T7 not launched; snapshots available/equal; receipt62 confirms prior cooperative writer terminal","consumers":"t1_native_inspection requires earlier discovery; proposal and Apply gates require post-native validation/instructions; successful ten immutable probes do not replace timing or discovery; model also confuses candidate tasks hash with intentionally reset fixture tasks"},"runtime_proof":["evidence:ev-20261125T061956Z-ed61de1e"],"simplest_alternative":"stop retaining failed proof and request independent offline trace/ordering/fixture-SHA review; do not relax allowlist or promote prose/replay","choice_rationale":"authorized third observation consumed after complete seq17 diagnosis; no fourth run or autocorrection authorized; actual ordering differs from prior Apply-only false negative and is preserved factually without bypassing retry threshold","next_hypothesis":"independent offline review can determine whether any contract-preserving correction is justified before a separately authorized future execution"},
{"kind":"blocker","seq":20,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; no successful discovery and gate commands before native invocation"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T061956Z-ed61de1e"],"diagnosis":"seq:19","options":[],"impact":"T1 failed third observation; T5/T7 not run; local assertion/fixture proof correction and independent affected review required; no archive/final suite/PR","researchable":true},
{"kind":"resolution","group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; no successful discovery and gate commands before native invocation"},"outcome":"blocked","via_seq":20},
{"kind":"diagnosis","seq":21,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; no successful discovery and gate commands before native invocation"},"class":"fixture/isolation","checked":{"phase":"healthy completed model; post-terminal T1 aggregation: compound8 correctly denied; native initial catalog baseline4 user5 assistant6 linked to selected skill71; strict48/instructions56 pre-skill are valid T1 observations before final107, not caused by later skill","scope":"same a9781ef isolated fixture DB only, backed up read-only; initial skill-guidance blob66f5a938235937b9e15fa3f01e95fbc82edb31fddcae5fd5ac499d969b769285 is bounded new diagnosis input not original checksum bundle; canonical native source/path/body/hash independently bound; five transformed fixture artifacts match review/proposal distinct from candidate/source fingerprints","lifecycle":"ses_deea391f8ffejSwAv3yVxrB5uY exit0/cost0; harness1; no provider error/timeout; snapshots available/equal and terminal receipt62; no fourth model; actual final107 blocks Apply and denied stateful verify7/86/96 remain failures including wrong observer identity96","consumers":"T1 catalog capture/inspection/proposal/Apply gates/final handoff and all-status attempt classifier shared by T7; assertion/fixture not application; T7 explicit ordering and early content/invocation prohibition unchanged; guard raw/cwd/child env/permissions unchanged"},"runtime_proof":["evidence:ev-20261125T061956Z-ed61de1e","evidence:ev-20261125T064610Z-9babf9fd","evidence:ev-20261125T065006Z-428cebe2"],"simplest_alternative":"keep blocked; do not widen compound commands or reinterpret blocked final as success","choice_rationale":"fresh independent review ses_dee9d76e4ffeR10I59JewObvEC against31cdb42 design41-43/49 and spec41-43 distinguishes catalog/order false-negatives from actual blocked handoff and verify mutation attempts; fix bounded correlation/scope clarity and strengthen outcome/all-status boundary without material replan; technical wait environment assertion-fixture, not nonexistent prerequisite","next_hypothesis":"new bounded same-session native catalog projection plus pre-final successful immutable/Apply proof accepts genuinely ready handoff only; replay of third run must remain failed for final107 and verify attempts; prove offline and retain new diagnosis artifact separately before any separately authorized future observation"}
,
{"kind":"attempt","seq":22,"obligation":"T1","signature":"assertion: recovery proof incomplete; receipt unobserved and apply instructions denied with blocked handoff","target":"3a3fdaa T1 phase1 native default","class":"assertion/contract","hypothesis":"reviewed catalog delivery, fingerprint scope and strict handoff proof enable complete T1 without stateful attempts","change":"approved 3a3fdaa catalog/source separation and pre-handoff gate timing plus strict JSON/all-status boundaries; fresh guard/model metadata","change_target":"test","observed_effect":"model exit0/harness1; catalog and Apply skill39 plus proposal proof succeed; Apply instructions43 quoted argv denied; reader calls omit correlated arguments and all denied; runtime_reads empty; final JSON87 BLOCKED; snapshots available/equal; T5/T7 not run","result":"fail","evidence":["evidence:ev-20261125T070455Z-8f203e55"]},
{"kind":"diagnosis","seq":23,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; receipt unobserved and apply instructions denied with blocked handoff"},"class":"assertion/contract","checked":{"phase":"post-terminal T1 aggregate: delivered catalog and read21 precede real Apply39; strict45/proposal prove true; quoted instructions43 denied with no correct later call; reader17/24/30/48/49/54/55/65-67/84 omits four required arguments or uses wrong cwd; JSON87 BLOCKED not RECOVERED","scope":"exact installed 3a3fdaa disposable HOME/XDG/DB/Location; source/path/hash invocation separate from actual initial delivered catalog; no operator credentials/config or allowlist expansion; forbidden_attempts empty","lifecycle":"ses_dee7a654fffeTm0iHDWBZM9vOq exit0/cost0 without timeout/provider error; harness1 terminal; T5/T7 not launched; snapshots available/equal; prepared receipt not successfully observed by model","consumers":"t1_apply_gate_proof exact argv and t1_handoff strict JSON plus mandatory independent receipt tool proof; successful proposal/catalog/native facts cannot replace missing gates"},"runtime_proof":["evidence:ev-20261125T070455Z-8f203e55"],"simplest_alternative":"stop preserving failure and independently inspect receipt locators/published argv usability offline; do not loosen guard or turn BLOCKED into RECOVERED","choice_rationale":"one separately reviewed observation consumed; no autocorrection or fifth run authorized; declaration that base reader is unavailable is not evidence that complete allowed command is unavailable","next_hypothesis":"independent offline review may identify a bounded contract-preserving locator correction without executing another model"},
{"kind":"blocker","seq":24,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; receipt unobserved and apply instructions denied with blocked handoff"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T070455Z-8f203e55"],"diagnosis":"seq:23","options":[],"impact":"T1 fourth observation failed; T5/T7 not run; no archive/final suite/PR; independent offline diagnosis review needed","researchable":true},
{"kind":"resolution","group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; receipt unobserved and apply instructions denied with blocked handoff"},"outcome":"blocked","via_seq":24},
{"kind":"diagnosis","seq":25,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; receipt unobserved and apply instructions denied with blocked handoff"},"class":"fixture/isolation","checked":{"phase":"raw authorization correctly denies quoted status42/instructions43 and incomplete reader calls; post-terminal aggregation correctly fails Apply/receipt/final87 BLOCKED despite native39 and proposal pass","scope":"exact 3a3fdaa disposable HOME/XDG/DB/Location; allowlist510-512 already formats complete reader command from actual execution/owner/run/checkout but metadata1357-1359 publishes only prefix; cwd distinct from receipt checkout; no wrong owner/run actually supplied in eleven incomplete calls","lifecycle":"ses_dee7a654fffeTm0iHDWBZM9vOq exit0/cost0; harness1 T1; snapshots available/equal; T5/T7 not run; no fifth model; cooperative writer receipt exists independently but model never observed it successfully","consumers":"read_only_permissions raw strings versus recovery-evidence locator publication, T1 actual reader/Apply gate, T5 shared incomplete locator and T7 chosen-turn locator; preserve T7 prechoice and explicit ordering; guard/perms/reader/proof gates unchanged"},"runtime_proof":["evidence:ev-20261125T070455Z-8f203e55","evidence:ev-20261125T072459Z-d562cea9"],"simplest_alternative":"keep blocked with original failed proof; never normalize quotes or accept declarative terminal metadata","choice_rationale":"fresh independent review ses_dee9d76e4ffeR10I59JewObvEC identifies publication defect, not guard defect; use exact already-allowed command/cwd and existing shlex.join primitive with actual receipt fields; no parser/service/help wrapper or contract change; publish chosen T7 locator only after explicit choice","next_hypothesis":"complete raw-byte locators usable by actual reader/CLI remove source puzzle while unchanged trace remains failed; prove policy membership, real correlated terminal output and negatives offline without model before affected independent review"}
,{"kind":"attempt","seq":26,"obligation":"setup","signature":"evidence-wrapper: path must remain inside checkout","target":"3c85548 authorized observation prelaunch","class":"environment/bootstrap","hypothesis":"declare the external disposable sandbox as output-dir while retaining raw artifacts in execution.log","change":"add external output-dir to evidence wrapper invocation; no candidate source change","change_target":"none","observed_effect":"workflow-evidence exit2 before evidence ID and subprocess spawn; requested output directory absent; harness and model never started; T1/T5/T7 NOT RUN","result":"fail","evidence":["evidence:ev-20261125T074002Z-fee6cd0b"]}
,{"kind":"diagnosis","seq":27,"group":{"obligation":"setup","signature":"evidence-wrapper: path must remain inside checkout"},"class":"environment/bootstrap","checked":{"phase":"record argument validation at workflow_evidence.py285 before evidence allocation293 and subprocess spawn313; original shell callback exit2 and raw error retained","scope":"operator-side evidence wrapper only, exact clean3c85548; no disposable HOME/XDG/DB/Location or model preflight created; output directory absent","lifecycle":"outer shell sh_211a48aac001ATv7V152CjRros completed exit2 with explicit1800s timeout, not timeout/cancellation; no harness/model/writer child or terminal, prepared data or snapshots","consumers":"workflow-evidence safe_relative on output exclusions; external sandbox is not checkout output; no application, guard, permissions or harness defect established"},"runtime_proof":["evidence:ev-20261125T074002Z-fee6cd0b"],"simplest_alternative":"stop now preserving exact reviewed code and record failure; do not repeat the command, move sandbox inside checkout or widen evidence helper","choice_rationale":"explicit stop-first-failure controls even prelaunch failure; diagnostics only confirm original error and absence, never count as successful setup or observation","next_hypothesis":"after independent offline invocation review and separate authorization, existing execution.log capture can retain external artifact bytes without declaring an external checkout exclusion; fresh guard/model eligibility still mandatory"}
,{"kind":"blocker","seq":28,"group":{"obligation":"setup","signature":"evidence-wrapper: path must remain inside checkout"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T074002Z-fee6cd0b"],"diagnosis":"seq:27","options":[],"impact":"authorized observation did not launch; T1/T5/T7 NOT RUN, previous T1 failed proof still blocked; tasks3.4/4.3 pending; no archive/final required gate/PR; coordinator must review capture invocation before separately authorizing launch","researchable":true}
,{"kind":"resolution","group":{"obligation":"setup","signature":"evidence-wrapper: path must remain inside checkout"},"outcome":"blocked","via_seq":28}
,{"kind":"attempt","seq":29,"obligation":"setup","signature":"evidence-wrapper: path must remain inside checkout","target":"77b0242 explicitly reauthorized capture invocation","class":"environment/bootstrap","hypothesis":"omit external output exclusion while retaining sandbox artifacts in checksum-bound execution.log","change":"remove only --output-dir external argument; preserve RESUME_SMOKE_OUTPUT external path and unchanged harness/source","change_target":"none","observed_effect":"no-model capture preflight succeeds and actual harness installs candidate, prepares isolated T1 and launches/completes one model; wrapper records execution.log508037bytes; original seq26 remains failed","result":"pass","evidence":["evidence:ev-20261125T074735Z-bdc7dcf0","evidence:ev-20261125T074809Z-c869767e"]}
,{"kind":"resolution","group":{"obligation":"setup","signature":"evidence-wrapper: path must remain inside checkout"},"outcome":"passed","via_seq":29}
,{"kind":"attempt","seq":30,"obligation":"T1","signature":"assertion: recovery proof incomplete; five immutable artifact observations absent despite recovered handoff","target":"77b0242 T1 phase1 native default","class":"assertion/contract","hypothesis":"reviewed complete locators plus unchanged proposal/artifact probes allow complete grounded T1 proof","change":"explicitly authorized one model observation on doc-only successor77b0242 of reviewed3c85548; capture invocation corrected without source/guard/matcher changes","change_target":"test","observed_effect":"model exit0/cost0 and harness1; exact receipt21 and Apply22 succeed, native Apply53/catalog/discovery and strict39 plus five non-artifact provenance probes succeed; all five git-show artifact observations absent; final57 RECOVERED but model_proposal_provedfalse/proof_completefalse; snapshots available/equal; forbidden_attempts empty; T5/T7 NOT RUN","result":"fail","evidence":["evidence:ev-20261125T074809Z-c869767e"]}
,{"kind":"diagnosis","seq":31,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; five immutable artifact observations absent despite recovered handoff"},"class":"assertion/contract","checked":{"phase":"post-terminal aggregate t1_proposal_proof: five git-show proposal artifact commands have zero matching tool attempts; commit37/ancestry47-48/review50/diff49/strict39 successful before final57; actual receipt21/Apply22/native53 and delivered catalog independently proved","scope":"exact77b0242 installed with credential-free disposable HOME/XDG/CODEX_HOME/DB/Location; only operational capture exclusion removed; source/guard/pins unchanged from independently reviewed3c85548; all commands published in recovery-evidence read11; no quotes/cwd denial of missing five reads","lifecycle":"ses_dee52cf22ffeF4k4USxgA4K3at pid3471029 terminal exit0 at07:51:04.112762Z, no timeout/provider error/malformed JSONL; 12step_finish cost0; harness1 T1 then stop; T5/T7 never launched; snapshots available/equal; final RECOVERED not complete provenance proof","consumers":"t1_proposal_proof mandatory same-session successful tool observations of five immutable artifacts; metadata/review hashes/diff/fixture preparation and outcome true cannot substitute; missing artifact mechanism genuinely differs from seq22 denied Apply and unobserved receipt, both now successful; denied compound read-only commands remain denied, no stateful attempt detected"},"runtime_proof":["evidence:ev-20261125T074809Z-c869767e"],"simplest_alternative":"stop retaining failed proof for independent offline review; never accept JSON RECOVERED, prepared facts or zero diff as replacements for missing tool observations","choice_rationale":"one actual authorized observation consumed after fresh guard/default-model eligibility; capture prelaunch was not inference; no automatic sixth model, source fix, permission expansion, quote normalization or archive/PR allowed","next_hypothesis":"independent review can assess why published five artifact commands were not observed and whether any contract-preserving correction is justified, without executing another model"}
,{"kind":"blocker","seq":32,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; five immutable artifact observations absent despite recovered handoff"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T074809Z-c869767e"],"diagnosis":"seq:31","options":[],"impact":"T1 fifth model observation failed; T5/T7 NOT RUN; tasks3.4/4.3 pending; no archive/final gate/PR; independent offline proof review required","researchable":true}
 ,{"kind":"resolution","group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; five immutable artifact observations absent despite recovered handoff"},"outcome":"blocked","via_seq":32}
 ,{"kind":"diagnosis","seq":33,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; five immutable artifact observations absent despite recovered handoff"},"class":"fixture/isolation","checked":{"phase":"healthy model completed; post-terminal proof-selection overconstraint: body locators253-260 required wholesale277-290; proposal37/ancestry47-48/immutable review50/exact full scope actual diff49/strict39 all successful untruncated same-session/cwd pre-final57; receipt21/Apply22/native53/RECOVERED57 real","scope":"77b0242 isolated installed source unchanged from3c85548; review pins same proposal/all required artifact hashes; independent current repository check finds regular100644 tracked blobs/modes/physical hashes equal, no skip/assume flags, filemode true/no applicable conversion attributes; current diagnosis is not extra model observations or a fabricated historic before-snapshot","lifecycle":"ses_dee52cf22ffeF4k4USxgA4K3at model exit0/cost0, harness1 T1; no provider/timeout failure; snapshots available/equal; forbidden_attempts empty; T5/T7 not run; no sixth model; stored fifth failure retained","consumers":"fixture preparation/snapshot T1 and t1_proposal_proof required-versus-optional locators; programmatic prerequisites before/after future read-only turn plus existing inventory; actual native comparison/review probes remain mandatory; guard/reader/permissions/model selection/pins/T7 boundaries unchanged"},"runtime_proof":["evidence:ev-20261125T074809Z-c869767e","evidence:ev-20261125T082230Z-23808ff3"],"simplest_alternative":"keep blocked; do not infer universal integrity from empty diff or JSON RECOVERED","choice_rationale":"fresh independent review ses_dee9d76e4ffeR10I59JewObvEC against approved31cdb42 design33/35/41-43/61 and spec41-47 corrects seq31 semantic claim without erasure/replan; no five-body-call contract; recognize exact native Git comparison only under programmatically verified immutable required-artifact/tracking/config/inventory prerequisites stable before/after","next_hypothesis":"real Git fixture negatives and retained fifth trace equivalence diagnosis prove bounded integrity without optional body-read quota; original failed result and missing historical prerequisites remain historical limits; independent affected review before any separately authorized future observation"}
,{"kind":"attempt","seq":34,"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers","target":"627b89a T1 phase1 native default","class":"assertion/contract","hypothesis":"independently approved scoped Git comparison with verified artifact prerequisites yields complete coherent T1 handoff","change":"one newly authorized native observation on reviewed627b89a after seq33 semantic diagnosis; mandatory native provenance gates retained and body locators optional","change_target":"test","observed_effect":"model exit0/cost0 and harness1; before/after artifact prerequisites verified/equal and model_proposal_provedtrue/model_apply_gate_provedtrue; native50/receipt17/strict42/Apply41 and full provenance succeed; final79 RECOVERED includes four blockers so outcomefalse/proof_completefalse; all eight snapshots dimensions equal; forbidden_attempts empty; T5/T7 NOT RUN","result":"fail","evidence":["evidence:ev-20261125T083810Z-4711919b"]}
,{"kind":"diagnosis","seq":35,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers"},"class":"assertion/contract","checked":{"phase":"post-terminal strict t1_handoff expects coherent RECOVERED with blockers[]; final79 has four nonempty entries despite positive proposal/Apply predicates; exact commit25/ancestry28-29/review30/full-scope diff39/strict42/Apply41/native50 before final and real receipt17; optional five bodies33-36/40 also read","scope":"exact reviewed627b89a installed in fresh credential-free HOME/XDG/CODEX_HOME/privateDB/Location; artifact_comparison captured prospectively before/after verifiedtrue and equal with five physical/index/proposal hashes/modes/flags/config/attributes; no historic config fabrication; all eight snapshot dimensions equal","lifecycle":"ses_dee25002cffeyXijaW40o1kU0x pid1050443 exit0 at08:41:28.306891Z, no timeout/provider error/malformed JSONL;19steps cost0;42tools; harness1 T1 then stop;T5/T7 never launched; no seventh model; raw guard active both hooks cleanup; forbidden_attempts empty but denied raw read variants retained","consumers":"strict JSON handoff matcher/outcome and model interpretation of controlled_fixture seed/source/transformation versus post-Apply gates and inventory-source availability; scope/hash/post-Apply caveats listed as blockers; compound status5 and list/status70-71 lacking published args denied, no successful inventory tool observations; this differs from seq30 five-body overconstraint now corrected and verified prospective prerequisites, not renaming same absent proof"},"runtime_proof":["evidence:ev-20261125T083810Z-4711919b"],"simplest_alternative":"stop preserving failed strict outcome for independent offline review; do not strip blockers, widen raw guard or reinterpret final JSON as PASS","choice_rationale":"one new explicitly authorized observation consumed after affected independent review and seq33 diagnosis; successful prerequisites/provenance/receipt do not override actual contradictory strict handoff or justify automatic model rerun; no application/production defect established","next_hypothesis":"independent offline review can distinguish legitimate fixture-scope caveats from unresolved recovery blockers and inspect denied inventory command spelling/locators before any separately authorized contract-preserving correction"}
,{"kind":"blocker","seq":36,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T083810Z-4711919b"],"diagnosis":"seq:35","options":[],"impact":"T1 sixth native observation failed strict handoff; T5/T7 NOT RUN; tasks3.4/4.3 pending; no archive/final required suite/PR; independent offline handoff review required","researchable":true}
 ,{"kind":"resolution","group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers"},"outcome":"blocked","via_seq":36}
 ,{"kind":"diagnosis","seq":37,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers"},"class":"fixture/isolation","checked":{"phase":"healthy model completed; post-terminal handoff fixture schema ambiguously called all gaps blockers while mandatory observed inventory was not asserted/published; four final79 entries split scope seed, observation method/namespace, genuine unobserved inventory, future post-Apply stage","scope":"627b89a isolated HOME/XDG/DB/Location; eight prospective snapshots equal/prerequisites true; receipt17/Apply41/native50/strict42/proposal25/ancestry28-29/review30/diff39 actual; no new SHA-sum requirement or real candidate approval inside controlled fixture; ignored coverage must be honestly bounded, not inferred from status/list alone","lifecycle":"ses_dee25002cffeyXijaW40o1kU0x exit0/cost0/harness1 T1; T5/T7 not run; final79 RECOVERED plus four blockers correctly failed; no seventh model; stopped prior writer receipt does not grant ownership or approve different/live current registry owner","consumers":"T1 fixture metadata/locators, handoff blockers-versus-limitations schema and new native observed inventory proof; stateful forbidden_attempts distinct from denied out-of-scope repo read61 and benign unsupported variants; T5 checks/T7 prechoice and reinventory unchanged; guards/raw commands/permissions/pins unchanged"},"runtime_proof":["evidence:ev-20261125T083810Z-4711919b"],"simplest_alternative":"keep blocked; never strip actual blockers or assume snapshots equal means model inspected inventory or owns checkout","choice_rationale":"fresh independent review ses_dee9d76e4ffeR10I59JewObvEC distinguishes three honest nonblocking limitations from missing native inventory under approved spec27/resume-workflow10/14/18; publish existing exact inventory commands/cwds and require actual correct identity/owner/receipt observations; clarify read-only last-gate recovery versus permission before effects without new protocol/stage or LLM judge","next_hypothesis":"bounded schema with limitations plus real native inventory sources admits honest recovered fixture handoff only; unknown/live/conflicting owner or missing receipt/inventory still blocks regardless labels; retained sixth trace remains failed for genuine gap and nonempty blockers; independent affected review before any separately authorized seventh observation"}
 ,{"kind":"diagnosis","seq":38,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers"},"class":"fixture/isolation","checked":{"phase":"offline independent review found ownerstate overconstraint in05ea1c2 t1_inventory_proof: onlyACTIVE-stopped accepted; real public-helper releasedWAITING control fails old predicate despite fully observed inventory/receipt","scope":"same issue checkout/run; change only inventory predicate/test/handoff; disposable producer seed-T1 explicitly created by test uses planned reserve/activate/verify/terminal receipt/checkpoint/verify/release; no operator or foreign reservation changed; path/issue/branch/HEAD/digest/current snapshot bindings still mandatory","lifecycle":"no seventh inference; original sixth model healthy exit0/cost0 but harness1 T1, missing inventory and nonempty blockers remain FAILED; new released control is offline synthetic trace of actual Git/list/reader outputs and public lifecycle, not model proof","consumers":"T1 read-only last-gate inventory: accept either matching stopped priorACTIVE owner or unambiguous releasedWAITING ownerless; independent matching terminal receipt mandatory in both; neither state grants writes; missing facts/recoveryrequired/unknown/nullACTIVE/live conflicting owner/ambiguous rows/drift still block; all other source nodes/guard/raw permissions/reader/pins/T5T7 unchanged"},"runtime_proof":["evidence:ev-20261125T092512Z-4c9146bc","evidence:ev-20261125T083810Z-4711919b"],"simplest_alternative":"keep blocked pending affected review; never treat arbitrary ownerNull as proof a worker ended or as a grant to start a writer","choice_rationale":"fresh review ses_dee9d76e4ffeR10I59JewObvEC identifies concrete normal lifecycle false-negative against WORKTREES13/21 and approved spec43; smallest state distinction keeps public release valid for read-only recovery while retaining all observed facts/receipt and ownership-before-effects requirements","next_hypothesis":"real released public-helper positive and retained ACTIVE-stopped/unknown/live/identity/digest/drift/ambiguity negatives plus full offline suite validate the narrow correction; sixth native trace still fails; independent affected review before separately authorized seventh observation"}
,{"kind":"attempt","seq":39,"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers","target":"fca6a97 T1 phase1 native default","class":"assertion/contract","hypothesis":"reviewed limitations/current-blockers distinction plus published observed inventory and owner-state handling yields coherent read-only recovery handoff","change":"one newly authorized model observation on independently reviewedfca6a97 after diagnoses37-38; actual tool inventory mandatory and ownership not granted","change_target":"test","observed_effect":"model exit0/cost0, harness1; proposal/Apply/inventory predicates alltrue with prospective artifact prerequisites/eight snapshots equal; final90 RECOVERED next_actionreconcile-ownership still carries one ownership-precondition blocker and eight limitations; no stateful attempt; T5/T7 NOT RUN","result":"fail","evidence":["evidence:ev-20261125T093223Z-ff1be68e"]}
,{"kind":"diagnosis","seq":40,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers"},"class":"assertion/contract","checked":{"phase":"post-terminal t1_handoff rejects final90 nonempty blockers; final JSON2281bytes, valid structure/eight limitations/next_actionreconcile-ownership allowed; proposal/Apply/inventory predicates true, no other failed gate demonstrated; actual receipt25/native79/strict46/Apply45 and commit38/ancestry37-39/review41/full-change diff40 pre-final","scope":"exactfca6a97 fresh private credential-free HOME/XDG/CODEX_HOME/DB/Location; artifact prerequisites verifiedtrue before/after equal and eight full snapshots equal; worktrees47/status-index48-51/reservationlist52 really observed; ACTIVEseed-T1 owner and run/path/HEAD/digest match terminal prior writer receipt, no drift/extra unknown; no recovery write grant","lifecycle":"ses_dedf35f74ffeFTglzDI0fB5HPP pid2106145 exit0 at09:35:30.773677Z, no provider error/timeout/malformed JSONL;16steps cost0;49tools; harness1T1 then stop, T5/T7 never launched; no eighth model; guard active both hooks cleanup; boundary denials retained separately from forbidden_attempts[]","consumers":"strict handoff model classifies stopped prior ACTIVE owner and mandatory reconciliation before effects as current blocker despite choosing reconcile-ownership; unlike seq34 inventory now actually proved and known scope/future caveats mostly separated into limitations; same nonempty-blocker signature retained for second failure, not reset; fixture global-reference reads6-8 and envpipe5 denied before execution, not operator data read"},"runtime_proof":["evidence:ev-20261125T093223Z-ff1be68e"],"simplest_alternative":"stop preserving failed response and request independent offline assessment of ownership precondition versus read-only last-gate handoff; do not delete blocker text or reinterpret outcome as PASS","choice_rationale":"second same-signature failure now has complete post-failure diagnosis before any future attempt; all native proof improvements do not authorize automatic eighth model, matcher relaxation, source edit, ownership transfer or archive/PR","next_hypothesis":"independent review can compare the actual ACTIVEstopped-owner inventory/receipt and reconcile-ownership action to approved read-only stage semantics before deciding any separately authorized correction or observation"}
,{"kind":"blocker","seq":41,"group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T093223Z-ff1be68e"],"diagnosis":"seq:40","options":[],"impact":"T1 seventh observation failed handoff; T5/T7 NOT RUN; tasks3.4/4.3 pending; no archive/final required suite/PR; independent offline ownership/handoff review needed","researchable":true}
,{"kind":"resolution","group":{"obligation":"T1","signature":"assertion: recovery proof incomplete; recovered handoff carries nonempty blockers"},"outcome":"blocked","via_seq":41}
,{"kind":"attempt","seq":42,"obligation":"T5","signature":"runtime.timeout: native observation exceeded 360-second internal limit","target":"45c5b72 complete native harness T5 phase1 after technically eligible T1","class":"environment/bootstrap","hypothesis":"new reviewed e1408daf oracle with all native facts mandatory permits one complete real T1/T5/T7 observation for independent review","change":"one explicitly authorized observation-only run on approved45c5b72 with fresh guarded credential-free setup, native zero-price default and effective input binding","change_target":"test","observed_effect":"T1 proof_complete with nine facts/typed condition true but pending_independent_review/scenario_passfalse; T5 model exceeded360s and exited143 after SIGTERM,43 completedsteps/128tools, no final reply or successful GitHub fixture reads/receipt; stateful verify19 denied; snapshots available/equal; harness1; T7 NOT RUN","result":"fail","evidence":["evidence:ev-20261125T103548Z-f3771146"]}
,{"kind":"diagnosis","seq":43,"group":{"obligation":"T5","signature":"runtime.timeout: native observation exceeded 360-second internal limit"},"class":"environment/bootstrap","checked":{"phase":"execute_model communicate timeout360s in T5 before normal catalog/execution-binding/scenario aggregation; transport progressed through217 JSONL events and native Apply116/strict119, but no completed recovery handoff; outer shell1800s did not expire","scope":"exact45c5b72 installed/newapprovede1408daf, isolated HOME/XDG/CODEX_HOME/privateDB/Location; effective_inputs prepared before both T1/T5 and checksums valid; T5 never read recovery-evidence.json or successfully called disposable GitHub shim, empty reads/calls; repeated actual repo/PR source endpoints denied pre-spawn, not evidence correct fixture source unavailable","lifecycle":"T1ses_dedb94dbbffeG1BESArNUjvaP5 terminal0 at10:38:32.499548Z technically proved but independent review pending; T5ses_dedb6cf0dffeS60EcHgP3slpEv pid3349989 timeouttrue/exit143 at10:44:36.152411Z after process-groupSIGTERM;43completedstep_finish cost0 not final cost; no provider error/malformed lines; T7 never started and no ninth model","consumers":"T5 effective PR/head/check/manual/dependency recovery absent despite native skill/strict partial reads; stateful verify19 attempted and denied, original raw events preserved; before/after seven snapshots equal does not erase attempts; T5 delivered catalog/normal execution_binding not captured after timeout; no source/guard/pin/application edit justified by runtime outcome"},"runtime_proof":["evidence:ev-20261125T103548Z-f3771146"],"simplest_alternative":"stop retaining timeout and partial progress for independent T1/T5 event review; never extend timeout/widen guard, force T7 continuation or infer T5 PASS from native skill/strict/snapshots","choice_rationale":"one new complete harness invocation consumed; T1 remains pending_independent_review rather than automatic PASS or resolution of historical failures; actual repeated denied probes suggest source/scope investigation but do not prove internal cause, provider quota or pre-existing failure; no automatic rerun/source correction authorized","next_hypothesis":"independent offline review can inspect T5 locator discoverability and actual source-selection sequence alongside T1 pending semantics, without executing another model or rewriting bindings"}
,{"kind":"blocker","seq":44,"group":{"obligation":"T5","signature":"runtime.timeout: native observation exceeded 360-second internal limit"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T103548Z-f3771146"],"diagnosis":"seq:43","options":[],"impact":"complete eighth observation failed in T5; T1 technical facts proved but semantic/event review pending/scenario_passfalse, T7 NOT RUN; no archive/PR/final required gate; independent response/event review and timeout diagnosis needed","researchable":true}
,{"kind":"resolution","group":{"obligation":"T5","signature":"runtime.timeout: native observation exceeded 360-second internal limit"},"outcome":"blocked","via_seq":44}
,{"kind":"diagnosis","seq":45,"group":{"obligation":"T5","signature":"runtime.timeout: native observation exceeded 360-second internal limit"},"class":"fixture/isolation","checked":{"phase":"T5 bootstrap read-only: prompt omitted readable recovery-evidence entrypoint; locator publication omitted already-permitted GitHub source commands; Apply48/proposal81/design82 expose producer scope before any fixture GH reads; future t5_sources aggregate also lacked all-status stateful-attempt rejection","scope":"selected disposable/recovery milestone3 issue11 PR12 dependent13 runwf-disposable-t5, not copied producer rocker-code/my-ai-skills issue61 PR62; actual remote/registry/shim agree; root12/85 and remote/config112/166-167 probes denied; raw permissions/guard unchanged","lifecycle":"eighth T1 actual subscenario independently approved as reported by coordinator at observed45c5b72 inputs, without rewriting pending fields; eighth whole run still FAILED T5 timeout143/no final/empty shim logs, T7 NOT RUN; later local diagnostic assistant aborted/Step interrupted complete10:44:36.098Z then nativeIDLE784 outcomeinterrupted10:44:36.100Z before clientterminal10:44:36.152Z, not original catalog/execution binding; remote abort ACK/finalcost UNKNOWN; no new native run or cleanup","consumers":"T5 prompt, recovery-evidence selected scope/GH locators and t5_sources read-only acceptance; actual denied verify19 must reject otherwise-valid future reads at all statuses; out-of-scope reads disclosed separately; no production application/provider failure established"},"runtime_proof":["evidence:ev-20261125T103548Z-f3771146","evidence:ev-20261125T104933Z-6f13151c","evidence:ev-20261125T110433Z-98093eae","evidence:ev-20261125T110541Z-5a43f2e5"],"simplest_alternative":"keep BLOCKED preserving timeout and safe guard, without another observation; never increase timeout, add paid fallback, widen commands or infer completed PR reads from native Apply/strict/snapshots","choice_rationale":"independent review and explicit offline delegation identify bounded test-bootstrap publication and acceptance defects within approved e1408daf T5 contract; publish only existing raw command/cwd locators derived from fixture objects, distinguish producer provenance and reuse existing all-status rejection; native /bin/sh plus actual GH shim proves usability offline while original trace stays unchanged","next_hypothesis":"after affected independent review and separate authorization only, a complete real T1/T5/T7 run may test corrected material T5 inputs; old T1 approval remains at old inputs, not automatic reuse or whole F1 PASS"}
,{"kind":"attempt","seq":46,"obligation":"T5","signature":"assertion: recovery proof incomplete; T5 expected native Apply invocation/discovery absent","target":"3b7f98b complete native harness T5 phase1 after technically eligible T1","class":"assertion/contract","hypothesis":"independently approved material T5 bootstrap correction permits one complete native T1/T5/T7 observation with real fixture sources and unchanged native gate","change":"one explicitly authorized observation-only harness on exactclean3b7f98b, fresh credential-free guard/default/catalog/prepared bindings; no source changes during observation","change_target":"test","observed_effect":"T1 nine facts/typed ownership proved, pending_independent_review/scenario_passfalse/legacy serializationfailed; T5 terminal0/no timeout, real GitHub sources and inventory/receipt proved, Explore42 invoked before strict45 but expected Apply discovery/invocation absent, aggregate assertion failed; T7 NOT RUN; harness1","result":"fail","evidence":["evidence:ev-20261125T111624Z-0bd063a1"]}
,{"kind":"diagnosis","seq":47,"group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; T5 expected native Apply invocation/discovery absent"},"class":"assertion/contract","checked":{"phase":"post-terminal T5 aggregate native gate lines2258-2265 fails; statusfailed/proof_completefalse persisted, RuntimeError2328 recovery proof incomplete; native_discovery[]/native_invocation[] for designated openspec-apply-change, strict45 present; direct Apply read33 not invocation; actual Explore42 successful before strict45, no qualifying directory listing in native_calls; delivered catalog exists but current T5 matcher does not consume it","scope":"exact3b7f98b approvede1408daf in isolated HOME/config/XDG/CODEX_HOME/privateDB; manifest read8, six published fixture GitHub commands12-17 successful/no truncation prove disposable/recovery milestone3 issue11 PR12/head5b0d4ba2c6f9046faaacab030801ca7f66cfe6ba/checkSUCCESS/manual/dependent13; t5_sources diagnostictrue, no producer repo probes or out_of_scope reads, only ls5 denied","lifecycle":"T1ses_ded94254bffeAw0vHsGHrhKaz2 pid4065153 terminal0 at11:19:33.816475Z,13completedsteps/52tools; T5ses_ded914169ffeL50MoN6MM82Kow pid4122032 terminal0 at11:21:17.582760Z,10completedsteps/24tools; no timeout/provider error/malformed lines; completed-step cost sums0, no separate settled provider final-cost receipt; harness1 stop beforeT7; clientPIDs and writerPIDs4064287/4121033 absent afterward, no kill/cancel/restart/DB cleanup","consumers":"T5 sources/outcome/read-only/inventory/receipt succeeded, snapshots seven equal/forbidden_attempts[]/write_authorizedfalse; native applicability/discovery gate alone remains unsatisfied in retained matcher, not reclassified as PASS; T1 technical facts true and ownership proven with eight snapshots/prereqs equal, nonempty blocker gives legacy serializationfailed and pendingreview/scenario_passfalse; T1 ApplyCLI39/strict40 precede nativeApply49, original order retained for independent review; both prepared/execution bindings and delivered catalogs captured unchanged"},"runtime_proof":["evidence:ev-20261125T111624Z-0bd063a1"],"simplest_alternative":"stop preserving actual assertion and successful partial facts for independent contract/source/event review; do not edit oracle, relabel Explore as Apply, retrofit catalog discovery, force T7 or rerun model","choice_rationale":"new authorized complete observation consumed; unlike eighth timeout the corrected GitHub entrypoint worked and clients terminated normally, but that does not waive native gate; independent review must decide applicable read-only skill and discovery requirement against approved contract; no application/provider failure or automatic source fix established","next_hypothesis":"offline independent review can compare actual Explore42/strict45, delivered catalog versus missing qualifying listing and T5 Apply-only predicate, while separately reviewing T1 semantics/order and future F1 impact; no tenth run authorized"}
,{"kind":"blocker","seq":48,"group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; T5 expected native Apply invocation/discovery absent"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T111624Z-0bd063a1"],"diagnosis":"seq:47","options":[],"impact":"ninth whole observation FAILED T5 post-terminal native gate, not timeout; T1 pending independent response/event review with serialization diagnostic failed, T7 NOT RUN; no final required gate/archive/PR; independent applicability/discovery and F1 review needed","researchable":true}
,{"kind":"resolution","group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; T5 expected native Apply invocation/discovery absent"},"outcome":"blocked","via_seq":48}
,{"kind":"diagnosis","seq":49,"group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; T5 expected native Apply invocation/discovery absent"},"class":"fixture/isolation","checked":{"phase":"post-terminal matcher overconstraint: Apply-only plus directory-only discovery omits actual canonical Explore42 and delivered catalog despite strict45; Apply file33 auxiliary, not invocation; actual response/source semantics independently approved as reported by coordinator","scope":"observed3b7f98b approvede1408daf design41/45 and official Explore15-17 permit applicable read-only inspection without Apply-only identity; T5 real PRhead5b0d4ba2c6f9046faaacab030801ca7f66cfe6ba/manual/dependent13 sources12-17, honest checkout-head difference/owner receipt/no stateful attempts; T7 explicitly Explore-only, same-session choice then reinventory before earliest native content","lifecycle":"ninth T1ses_ded94254bffeAw0vHsGHrhKaz2 and T5ses_ded914169ffeL50MoN6MM82Kow complete/idle succeeded without timeout; no settled provider final-cost receipt, completed steps0 only; original whole FAILED/pending fields/legacy-format failure retained; T7 never executed; no tenth model or fabricated current-turn capture","consumers":"existing bounded matcher reused for T5 alternatives and T7 Explore-only; genuine catalog, strict context/cwd/session/step before handoff; private DB recaptured with unchanged baseline plus actual current-turn messages; future candidate map/actual-source binding replaces factory placeholder, never edits original record; T1 ownership/facts and T5 PR/all-status safety unchanged"},"runtime_proof":["evidence:ev-20261125T111624Z-0bd063a1","evidence:ev-20261125T112620Z-bbe58aa9","evidence:ev-20261125T114918Z-b19c0966","evidence:ev-20261125T114918Z-0b1cb4df"],"simplest_alternative":"retain BLOCKED without another observation; never weaken invocation to file/prose, switch T5 to Explore-only, broaden T7 to Apply, widen guard or grant ownership from catalog/receipt","choice_rationale":"fresh independent review ses_dee9d76e4ffeR10I59JewObvEC and explicit offline delegation identify implementation overconstraint inside e1408daf, not material acceptance change needing owner replan; reuse source/body/hash matcher and delivered catalog with applicable strict, distinguish metadata from content and initial baseline from actual current-turn delivery","next_hypothesis":"after affected independent review and separate authorization only, complete actual T1/T5/T7 may prove changed native oracle/binder inputs; old3b subscenario approvals are not automatic reuse, metadata/replay or final F1 PASS"}
,{"kind":"attempt","seq":50,"obligation":"T5","signature":"assertion: recovery proof incomplete; no native OpenSpec invocation, Verify file read only","target":"703ffb9 complete native T1/T5/T7 harness after reviewed T5/T7 native matcher correction","class":"assertion/contract","hypothesis":"independently approved bounded Explore-or-Apply T5 inspection and current-turn T7 catalog capture allow one newly authorized complete native observation without source or prompt changes","change":"one authorized observation-only run at exactclean703ffb9 with new isolated HOME/config/privateDB, fresh native guard/default/catalog and prepared bindings; no source edits during observation","change_target":"test","observed_effect":"T1 nine facts/typed condition proved, serializationpassed but pending_independent_review/scenario_passfalse; T5 terminal0/no timeout, actual sources/manual/dependency/receipt/strict proved, read Verify35 without any native OpenSpec skill-tool invocation; matcher selected source null and aggregate failed; T7 NOT RUN; harness1","result":"fail","evidence":["evidence:ev-20261125T121046Z-f787388b"]}
,{"kind":"diagnosis","seq":51,"group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; no native OpenSpec invocation, Verify file read only"},"class":"assertion/contract","checked":{"phase":"T5 post-terminal required conjunction2366-2370 not satisfied, RuntimeError2438 after statusfailed/proof_completefalse persisted; only T5 skill tool is resume-workflow2; canonical Verify file read35 and prose40/55 are not native invocation; context41/list42/instructions43/status44/strict48 succeed but cannot substitute tool event; native/source/discovery/invocation/instructions null/[] reflect no selected invoked source, not missing strict","scope":"exact703ffb9 approvede1408daf, prepared T5 candidates canonical Explore/Apply and actual delivered catalog contains both plus resume-workflow; Verify body exists/readable but no Verify native tool attempt either; fresh isolated HOME/config/XDG/CODEX_HOME/privateDB, raw guard unchanged; manifest3 and six fixture GH15-20 prove disposable/recovery milestone3 issue11 PR12/headba48e0e477a101478be09059509e466091c1e4a4/checkSUCCESS/manual/dependent13; t5_sources diagnostictrue, no producer probes/out_of_scope reads, boundary rootread7/ls11 denied","lifecycle":"T1ses_ded625d95ffelT8lOw69u3ftnR pid942840 terminal0 at12:12:41.383361Z,12completedsteps/32tools; T5ses_ded609cceffe7kZ16usqNCOvbN pid977383 terminal0 at12:13:47.693228Z,10completedsteps/29tools; no timeout/provider error/malformed JSONL, stderr empty; completed stepcost0, separate settled provider finalcost UNKNOWN; harness1 callback actual, T7 never launched; clients and writer941615/976344 absent after correlated terminal receipts, no kill/restart/cancel/DB cleanup","consumers":"T5 source facts/outcome true, inventory24-28/receipt29 and seven snapshots equal, forbidden_attempts[]/write_authorizedfalse, response55 keeps existing PR review/manual/dependency; native invocation remains missing regardless of alternate skill applicability; T1 all nine facts/typed prior-stopped-owner true, eight snapshots/prereqs equal, serializationpassed but pendingreview/scenario_passfalse; original effective/execution bindings and delivered catalogs both captured unchanged with T5 native_source null"},"runtime_proof":["evidence:ev-20261125T121046Z-f787388b"],"simplest_alternative":"stop retaining current real missing-invocation failure for independent response/event review; never widen matcher to Verify and count a file read, relabel CLI as native, change prompt/guard, fill null source, force T7 or launch eleventh model","choice_rationale":"new reviewed source/new authorization consumed exactly one complete harness; ninth failure was an actual Explore invocation rejected by Apply-only matching, while tenth has no native OpenSpec skill tool invocation at all; retain seq46-49 and all earlier blocked episodes without budget reset, replay resolution or automatic fix; no cognitive/provider/root-cause exclusivity established","next_hypothesis":"independent offline review can inspect the relation between delivered Explore/Apply catalog, readable Verify file selection and missing native tool use, alongside current T1 semantics and future F1 impact, without another model"}
,{"kind":"blocker","seq":52,"group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; no native OpenSpec invocation, Verify file read only"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T121046Z-f787388b"],"diagnosis":"seq:51","options":[],"impact":"tenth whole observation FAILED post-terminal T5 native invocation gate; current T1 pending independent response/event review despite technical facts/serializationpassed; T7 NOT RUN, no same-session two-turn proof; no final required suite/archive/PR; independent native integration/response review needed","researchable":true}
,{"kind":"resolution","group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; no native OpenSpec invocation, Verify file read only"},"outcome":"blocked","via_seq":52}
,{"kind":"attempt","seq":53,"obligation":"T5","signature":"assertion: recovery proof incomplete; no native OpenSpec invocation, Verify file read only","target":"930b1bc complete native harness, explicit one-run opencode/deepseek-v4.1-flash-free override after separate parent authorization","class":"assertion/contract","hypothesis":"one explicitly authorized different-model experiment tests actual native dispatch under unchanged reviewed703 source and gates; not fallback or prior subscenario reuse","change":"process-local RESUME_SMOKE_MODEL=opencode/deepseek-v4.1-flash-free, fresh isolated HOME/config/DB/native zero-price preflight and raw guard per phase; source/prompts/perms/timeout/pins unchanged","change_target":"test","observed_effect":"T1 nine facts/typed condition and serialization proved but pending_independent_review/scenario_passfalse; T5 terminal0/idle succeeded, real source facts/manual/dependency/inventory/receipt/strict passed, only resume skill5 and Verify file30 read, no native OpenSpec invocation; aggregate failed; both phases actual DeepSeek proved across20nativeassistants; T7 NOT RUN; harness1","result":"fail","evidence":["evidence:ev-20261125T125602Z-c3f672d3"]}
,{"kind":"diagnosis","seq":54,"group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; no native OpenSpec invocation, Verify file read only"},"class":"assertion/contract","checked":{"phase":"second same-signature failure after seq50, complete post-failure diagnosis before any further work; T5 aggregate native conjunction2366-2370 fails, RuntimeError2438 persisted statusfailed/proof_completefalse; sole skill tool resume-workflow5, Verify read30/prose not native dispatch; list35/strict40 genuine but selected native source null/discovery/invocation/instructions empty cannot be filled from file read or CLI","scope":"exactclean930b1bc installed, reviewed code703 byte-identical, approvede1408daf; explicit parent selected only opencode/deepseek-v4.1-flash-free through existing process-local override, not default big-pickle; fresh T1/T5 unique literal enabled/active/chat/tools/text/image known-zero-all-tier native metadata, source RESUME_SMOKE_MODEL; private HOME/XDG/config/CODEX_HOME/DB and unchanged raw guard, no operator auth/real GH; T5 manifest2/GH9-14 prove disposable/recovery milestone3 issue11 PR12/headfb9ebc519fba3784dcea18f5d91bc02deef22f11/checkSUCCESS/manual/dependent13; t5_sources true, snapshots seven equal, forbidden_attempts[]","lifecycle":"T1ses_ded38ec4cffeYMkMO5YUGlftet pid1751971 terminal0 at12:58:09.166281Z,8steps/30tools; T5ses_ded36fea1ffeUJ8eNr61DIvTiV pid1790205 terminal0 at13:00:42.139052Z,12steps/32tools; no timeout/cancel/malformed/provider error, stderr empty, both private native idle outcomes succeeded;20actualassistant raw model fields all DeepSeek/default runtime variant, sumreportedcost0 but settled provider finalcost UNKNOWN; clients and terminal-cooperating writer1750845/1789060 absent, no kill/restart/cleanup; T7 not launched, no twelfth model","consumers":"T5 inventory18-23/receipt24 and response63 keep existing PR review/manual/dependent13 blocked; Verify tool not allowed despite readable canonical file, Explore/Apply delivered and allowed but neither invoked; quoted status33/instructions36 and Git43/44/46-49 denied pre-spawn, .git read60 denied, no out_of_scope reads; raw quotes are not exact published commands and do not prove permitted locators unavailable; T1 facts9/typed ownership/serializationpassed/eight snapshots/prereqs true with nativeApply37 but independent semantic review pending/scenario_passfalse/write_authorizedfalse; prepared/execution/catalog bindings retained unchanged with T5 source null and material actual model linked via native DB receipt"},"runtime_proof":["evidence:ev-20261125T125602Z-c3f672d3"],"simplest_alternative":"stop retaining second real missing-dispatch failure and actual model identity for independent offline review; do not widen raw guard, add Verify, force Apply, infer native invocation from read/CLI, pad prompts, retry or select another route","choice_rationale":"new model experiment explicitly authorized once after same-profile metadata, not automatic fallback; changed actual model still omitted native OpenSpec dispatch, which is a behavioral observation not proof of exclusive model/root-cause or router/matcher defect; keep seq50-52 and ten earlier whole FAILED runs, no episode/budget reset or retrospective PASS; complete T7/F1 remains unproved","next_hypothesis":"independent parent review can compare both real same-signature traces and actual source/catalog/model fields without executing another model or granting a code/gate fix"}
,{"kind":"blocker","seq":55,"group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; no native OpenSpec invocation, Verify file read only"},"type":"technical","wait_reason":"environment","evidence":["evidence:ev-20261125T125602Z-c3f672d3"],"diagnosis":"seq:54","options":[],"impact":"eleventh whole native experiment FAILED T5 missing native dispatch despite actual explicit DeepSeek route; second same signature fully diagnosed; T1 current technical facts true but independent review pending, T7 NOT RUN/F1 incomplete; no final unit gate/archive/PR; no further inference authorized","researchable":true}
,{"kind":"resolution","group":{"obligation":"T5","signature":"assertion: recovery proof incomplete; no native OpenSpec invocation, Verify file read only"},"outcome":"blocked","via_seq":55}
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
