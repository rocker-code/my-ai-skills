# interrupted-workflow-resume Specification

## Purpose

Retomar com segurança uma issue ou milestone em sessão nova por fontes duráveis e verificáveis, preservando trabalho, ownership, escopo e resultados desconhecidos.

## ADDED Requirements

### Requirement: Recover from a new session without prior chat

O workflow SHALL reconhecer pedido natural de retomada e identificar repositório e escopo únicos por evidência durável antes de mutações. Havendo candidatos plausíveis múltiplos, MUST pedir somente a desambiguação necessária e MUST NOT escolher por recência.

#### Scenario: Single issue is uniquely identified
- **WHEN** uma sessão OpenCode nova recebe pedido natural em checkout com uma issue interrompida identificada por evidência
- **THEN** descobre a entrada de retomada, identifica issue, último estágio comprovado e próxima ação segura, reutilizando a mesma proposta/branch/worktree/PR antes de encaminhar ao coordenador existente

#### Scenario: Ambiguous candidates
- **WHEN** dois pares issue/run são igualmente plausíveis para “continue de onde parou”
- **THEN** o agente termina com uma pergunta neutra visível que identifica ambos e pausa sem seleção, takeover, dispatch, escrita ou invocação de skill OpenSpec nativa; descoberta por listagem é permitida, mas tentativas de invocação ou leitura de conteúdo nativo, mesmo failed/cancelled, não são permitidas antes da escolha

#### Scenario: Explicit choice after ambiguous pause in the same session
- **WHEN** após a pausa o usuário escolhe explicitamente issue/run na mesma sessão OpenCode
- **THEN** o agente SHALL reinventariar ambos os checkouts, reservas e fontes Git/GitHub/OpenSpec, consultar prova independente do writer escolhido e só depois invocar a skill OpenSpec 2.x nativa aplicável em modo read-only no mesmo ID de sessão; SHALL reconferir ambos os estados sem takeover, dispatch ou escrita, correlacionando descoberta/invocação a origem/path/hash e sessão; sem segurança ou evento nativo observável a prova permanece bloqueada, não PASS

### Requirement: Preserve work and verify ownership

O workflow SHALL reutilizar branches/worktrees/OpenSpec/PRs verificados e inspecionar commits únicos, staged, unstaged, untracked e ignored relevantes. MUST NOT tomar posse sem prova fundamentada de writer parado e reconciliação do helper.

#### Scenario: Interrupted dirty worktree
- **WHEN** há alterações locais parciais ou crash antes de checkpoint
- **THEN** conteúdo/índice/commits e dados ignorados relevantes são preservados e o checkout é reconciliado/reutilizado ou retido com bloqueio, sem reset, substituição ou limpeza indiscriminada

#### Scenario: Active or uncertain owner
- **WHEN** writer anterior está ativo ou a posse é inconclusiva
- **THEN** escrita é bloqueada naquele checkout sem takeover automático, mesmo com registry antigo, ausente ou incompleto

#### Scenario: Null PID without terminal runtime proof
- **WHEN** uma reserva contém `pid:null` ou a fixture apenas afirma parada sem prova terminal independente da execução
- **THEN** o agente não declara writer parado e bloqueia transição/Apply; recibo de outro owner/run/checkout/execução também não autoriza posse

#### Scenario: T1 has grounded terminal evidence
- **WHEN** a issue tem proposta/revisão comprovadas em commit fixo e recibo terminal independente correlacionado ao writer e checkout
- **THEN** a sessão nova identifica Apply no commit validado como próxima ação sem executá-lo na prova read-only, comprova descoberta/invocação nativa e mantém reservas e artefatos inalterados; o recibo de término não substitui validação/revisão nem concessão explícita de posse

### Requirement: Evaluate recovery and write conditions in their own phase

O aceite SHALL distinguir recuperação read-only fundamentada, condições anteriores à escrita e conformidade de apresentação da fixture. MUST conferir identidade, último gate, próxima ação e condições limitadas por fatos nativos, sem converter término em posse. Convenção textual isolada MUST NOT substituir prova; gap atual, claim inseguro ou condição não classificada MUST bloquear a ação dependente.

#### Scenario: Known stopped prior owner has not transferred ownership
- **WHEN** fontes nativas observadas comprovam proposta/review/gate/inventário/recibo, sem efeitos, e owner atual é o mesmo writer anterior parado ou WAITING released unívoco com recibo correto
- **THEN** recuperar o último gate e indicar reconciliação/aquisição de posse antes de Apply satisfaz a fase read-only, mantendo escrita não autorizada; a representação estruturada da condição na fixture precisa corresponder ao checkout, owner/run/execução e fase observados, não apenas a um rótulo, e não estabelece novo protocolo de produção

#### Scenario: Real gap cannot be hidden in a later phase
- **WHEN** falta fonte ou término exigido, há conflito vivo/posse desconhecida/drift, fato nativo incompatível, efeito tentado ou declaração insegura/não classificada
- **THEN** a obrigação dependente permanece bloqueada mesmo com status favorável, lista textual vazia, snapshots iguais ou condição declarada como futura; prosa não reclassifica fatos nem autoriza escrita

#### Scenario: Presentation diagnostic without lost semantic proof
- **WHEN** os campos semânticos necessários, condições da fase e todos os fatos nativos são comprovados e coerentes, mas uma convenção textual estrita da fixture não é satisfeita
- **THEN** o diagnóstico de serialização permanece visível separadamente sem, por si só, negar o aceite read-only; isso não dispensa parse/identidade/ação seguros, não ignora blockers arbitrários e não altera o resultado original de execução falha

### Requirement: Continue only from verified gates

O workflow SHALL reconstruir estado por GitHub/Git/OpenSpec, reservas, runtime suportado e provas de teste acessíveis. MUST reutilizar prova ainda válida e MUST NOT converter falta de callback/relatório, teste interrompido ou resultado de outro SHA/execução em aprovação. MUST NOT exigir coletor, ledger de comentários ou registro substituto.

#### Scenario: Test process interrupted without an authoritative result
- **WHEN** comando de teste não tem término e relatório exigidos acessíveis
- **THEN** o resultado permanece UNKNOWN e somente obrigações incompletas/invalidadas são reexecutadas após posse/preflight/diagnóstico seguros, preservando falhas históricas e limites da evidência recuperada

#### Scenario: Native invocation proof is inconclusive
- **WHEN** há somente arquivo de skill, leitura direta, CLI isolado, stub ou resposta narrativa sem evento nativo de invocação correlacionado
- **THEN** a prova de integração nativa fica bloqueada com causa exata, sem fabricar comandos legados ou declarar PASS por presença de arquivo

#### Scenario: T5 inspects an existing PR with canonical Verify
- **WHEN** a fixture read-only T5 tem Verify oficialmente gerada/suportada e seu perfil permite carregar exatamente essa skill como alternativa aplicável a Explore/Apply
- **THEN** a prova exige catálogo/discovery e dispatch nativo genuíno bem-sucedido, fonte/path/hash/body/sessão/contexto/change corretos, strict e leituras reais PR/head/checks/manual/dependência com estado preservado; Verify pode relatar incomplete/not verified sem aprovar implementação ou archive, e carregar instruções não concede shell/FS/escrita/MCP

#### Scenario: T5 capability addition cannot approve absent invocation or leak scope
- **WHEN** Verify está ausente/unsupported/divergente ou há somente catálogo/preparação/arquivo/CLI, dispatch failed/cancelled ou prova de outra fonte/sessão/root/change
- **THEN** a prova necessária fica bloqueada com causa exata sem stub ou retro-PASS; a permissão adicional de ativação é exclusiva de T5, não amplia T1 nem os limites T7 de escolha e Explore-only, e sua mudança material exige futuro run real completo após revisão

#### Scenario: Offline diagnosis of an earlier failed native run
- **WHEN** uma correção do oráculo é avaliada sobre trace real e pré-requisitos prospectivos retidos
- **THEN** a projeção nova é registrada como diagnóstico/regressão offline separado, preservando bytes, manifesto e FAILED originais; não cria observação nativa, não resolve episódio por replay e não supre cenários que nunca rodaram

### Requirement: Bind native evidence to effective inputs without weakening final gates

O fluxo SHALL exigir prova real completa T1/T5/T7 e preservar sua identidade original. Reuso comportamental após mudança só é permitido com inputs efetivos byte-vinculados e impacto explicitamente revisado. Mudança material ou incerteza MUST invalidar a prova afetada. A suíte local completa obrigatória MUST rodar no HEAD final limpo exato após archive/preparo e novamente após qualquer commit.

#### Scenario: Archive or documentation changes only proven provenance labels
- **WHEN** um run nativo completo passa e commits posteriores alteram somente identidade/proveniência com entradas efetivas e fatos de recuperação comprovadamente equivalentes
- **THEN** revisão independente pode reutilizar essa prova comportamental com mapa acessível de bytes/refs/diferenças, sem alegar nova execução no HEAD final ou aprovar manifesto stale; suíte local e checks/reviews exigidos mantêm seus vínculos próprios

#### Scenario: A supposedly documentary change alters native input
- **WHEN** texto/tarefa/spec consumido, runtime/modelo/perfil, skill/guard/config, fixture/prompt/oráculo ou fato de recuperação muda, ou sua irrelevância não é demonstrável
- **THEN** a prova afetada permanece pendente até execução real novamente; nomes de arquivo, metadados, replay e marcação de tarefas não substituem prova nativa nem autorizam reuso

### Requirement: Prepare isolated subscription authentication without importing personal state

O harness existente SHALL preparar perfil privado novo, pausar para OAuth manual pela pessoa e retomar somente o mesmo sandbox verificado. MUST NOT autenticar pela pessoa, importar/exportar credenciais, copiar estado pessoal ou usar API paga/fallback. Preparação MUST permanecer metadata-only, sem prova de inferência ou alteração dos gates nativos/read-only.

#### Scenario: Fresh preparation pauses before any inference
- **WHEN** o pin revisado é preparado num HOME/XDG/CODEX_HOME/OPENCODE_DB privado novo com env/PATH filtrados e standalone
- **THEN** o harness valida ownership, paths/symlinks/inventário/permissões privadas e registra apenas identidade opaca/HEAD/pin/runtime/perfil não secretos; pausa antes de modelo para login manual nativo Sign in with ChatGPT, sem método adivinhado, transcript auth, token/code ou identificador pessoal em output/evidência

#### Scenario: Resume requires the same prepared private sandbox
- **WHEN** a pessoa conclui login manual e pede retomada
- **THEN** somente o mesmo sandbox previamente preparado, sem owner conflitante/processo incerto ou mismatch de runtime/HEAD/config/rota, pode avançar; perfil arbitrário, recibo adulterado, symlink ou dados pessoais importados bloqueiam sem takeover, cópia ou aceite genérico de drift

#### Scenario: OAuth or displayed zero price alone cannot prove subscription route
- **WHEN** metadados nativos suportados são consultados sem material secreto depois do login
- **THEN** a verificação exige recibo confiável do método ChatGPT descoberto e realmente passado ao CLI→processo/conclusão nativa→perfil vazio antes/única conexão OAuth ativa depois→provider/catalog coerentes; OAuth genérico, exit0 isolado, arquivo declarativo, env/key/external ou vínculo indisponível mantêm BLOCKED sem auth DB/token; método/schema/handler/proveniência não suportados param antes de pedir login, sem inventar campos públicos ausentes

#### Scenario: Explicit subscription quota authorization is distinct from numerical zero pricing
- **WHEN** o usuário autorizou consumo de quota Plus/Pro após distinção de API por uso e a rota de assinatura foi comprovada pelo recibo e entitlement confirmado
- **THEN** o modelo só pode ser escolhido no catálogo real posterior e o ramo subscription-quota pode ser elegível com cost=[] como display unknown, nunca preço numérico zero/grátis; autorização/recibo/entitlement ausentes, rota API/desconhecida, preço API nonzero ou mismatch de método/conexão/perfil/provider/catalog bloqueiam; o ramo sem credenciais conserva todos os tiers conhecidos zero e rejeita lista vazia/desconhecida; não há API paga/paygo/compra de quota extra/fallback/retry automático e custos/saldo não observados permanecem UNKNOWN

#### Scenario: Authenticated runtime compatibility and evidence exclude secret material
- **WHEN** runtime/schema mudam ou o DB privado passa a conter OAuth
- **THEN** a captura MUST usar somente projeção consistente read-only de instruções/sessão não secretas, sem backup/serialize/hash do DB inteiro nem consulta a credenciais; compatibilidade desconhecida bloqueia e modelo não recebe acesso ao DB; relatórios/manifestos/bundles usam allowlists antes de persistir e excluem SQLite/WAL/SHM, auth transcripts/material e IDs pessoais inclusive estruturados, preservando prova nativa/ordem T7 e falhas originais sem regex-only ou retro-PASS; runtime/modelo/perfil/auth novos invalidam reuso afetado e exigem revisão e novo T1/T5/T7 completo autorizado

#### Scenario: Direct local controller must be proven before spawning authentication
- **WHEN** a pessoa inicia posteriormente o controlador local revisado em seu próprio terminal nativo, sem ferramenta capturante
- **THEN** o controlador valida identidade local, capacidade OS de spawn/wait com filho inofensivo, pin/perfil/lease e FDs/foreground antes de auth; observador ausente/injetado, callable/JSON arbitrário, non-TTY ou continuidade incerta bloqueiam sem spawn; só o mesmo controlador observa Popen/wait do filho auth com FDs herdados e rotula local-controller/os-wait, nunca callback/sessão de agente inventados

#### Scenario: Local process evidence does not replace native proof or authorize inference
- **WHEN** o controlador conserva ou encerra o Supervisor após login
- **THEN** somente objeto vivo contínuo pode ser usado pelo harness completo após autorização separada e todos os checks de rota/conexão/provider/catalog/entitlement; recibo serializado, flag completed, término de pane ou probe PTY não reconstroem auth, Skill ou sessão; indisponibilidade de terminal externo e limites de recording do host são explícitos, sem captura de auth ou promessa de sigilo contra o próprio host

#### Scenario: Complete foreground continuation requires future authorization before login
- **WHEN** código revisado dispõe de continuação integral e a pessoa participa posteriormente no terminal próprio
- **THEN** grant específico real do coordenador para uma tentativa completa, ligado a HEAD/plano/runtime/perfil e condições de catálogo, é verificado antes de auth; mesmo Supervisor vivo mantém checks pós-login e escolha explícita de modelo real com confirmação local fresca antes de uma chamada do loop completo; flag/ref/JSON não inventam grant, e ausência/recusa/falha/cancel/restart bloqueiam sem inferência/retry/fallback

#### Scenario: Phase evidence excludes auth without losing live authority or native facts
- **WHEN** controlador inicia fase nativa autorizada após login e confirmação local
- **THEN** API de fase suportada no helper existente registra no mesmo processo sem capturar auth, child controller ou comando fictício; preserva log/manifest/checksums/fingerprints e artefatos reais de events/session/terminal/catalog/source/guard/snapshots para verify/export/import/revisão independente, nunca metadata-only como native PASS ou phase como suíte final/CI; suporte indisponível bloqueia antes de login
- **AND** o contrato dono test-evidence distingue modo de execução e conclusão tipada: fase usa exit_code=null, não exit OS fictício; leitores sem suporte, conclusão desconhecida e transporte inconsistente não aprovam a execução

### Requirement: Respect original scope and recovery limits

O workflow SHALL preservar limites explícitos de issue/milestone e modo de merge vigente comprovado, sem duplicar artefatos. Merge MUST permanecer retido sem autorização vigente comprovada. MUST informar dados locais perdidos/indisponíveis em vez de alegar restauração.

#### Scenario: Later explicit authorization supersedes an unknown historical mode
- **WHEN** o proprietário confirma posteriormente auto-if-green para a mesma issue
- **THEN** a autorização vigente substitui o HELD histórico sem dispensar gates/proteções/revisão e sem autorizar efeitos em uma delegação limitada a Planning

#### Scenario: Existing PR and blocked dependency in milestone
- **WHEN** milestone tem PR existente, modo manual e consumidor dependente bloqueado
- **THEN** o coordenador reconcilia PR/head/checks efetivos, preserva modo manual e dependência, não duplica PR nem despacha consumidor e mantém uma única issue ativa

#### Scenario: Lost local machine
- **WHEN** GitHub/Git/backup sobrevivem, mas checkout/registry ou arquivos locais não persistidos se perderam
- **THEN** somente artefatos disponíveis são recuperados, perdas/limites e próxima ação são explicitados, e registry ausente não concede posse implícita
