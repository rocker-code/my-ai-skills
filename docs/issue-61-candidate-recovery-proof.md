# Prova isolada de retomada — issue #61

## Recuperação atual — 25/11/2026

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
