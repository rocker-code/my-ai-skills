# Prova isolada de retomada — issue #61

## Recuperação atual — 25/11/2026

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
