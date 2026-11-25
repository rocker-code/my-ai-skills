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
