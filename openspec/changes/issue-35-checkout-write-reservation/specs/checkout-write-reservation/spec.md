# Spec Delta

## Purpose

Garantir que, entre participantes cooperantes do workflow, exista no máximo um writer por checkout, que mudanças externas sejam detectadas antes da próxima mutação e que retomadas e limpezas preservem trabalho parcial e arquivos desconhecidos, usando o registry local definido no protocolo de worktrees.

## ADDED Requirements

### Requirement: Registry local único com acesso serializado
O helper SHALL usar exclusivamente o registry `ai-workflow/worktrees.json` no Git common dir do repositório, criando-o quando ausente. Toda leitura-modificação-escrita MUST ocorrer sob lock exclusivo comum a todos os worktrees e gravar o arquivo de forma atômica. Se a exclusividade não puder ser estabelecida, o helper MUST falhar sem alterar o registry nem conceder posse.

#### Scenario: Registry materializado no Git common dir
- **WHEN** o coordenador planeja um novo worktree auxiliar de um repositório sem registry
- **THEN** o registry é criado em `<git-common-dir>/ai-workflow/worktrees.json`, fora da árvore rastreada, com identidade do repositório e a entrada `RESERVED` do caminho planejado; checkout preexistente sem entrada não recebe posse direta

#### Scenario: Lock indisponível
- **WHEN** outro processo mantém o lock além do tempo de espera ou o mecanismo de lock não existe na plataforma
- **THEN** o comando termina com código de lock indisponível e o registry permanece byte a byte inalterado

#### Scenario: Registry corrompido
- **WHEN** o registry existe mas não é JSON válido no esquema esperado
- **THEN** o helper recusa mutações, preserva o arquivo e orienta a reconstrução verificada

### Requirement: Reserva exclusiva de escrita
O helper SHALL conceder posse ativa de um checkout a no máximo uma sessão. Uma reserva MUST registrar repositório, issue, branch, caminho, base, dono, lifecycle, baseline de código e horário. Sessão/run MUST seguir os IDs seguros de `workflow-event`. Outra sessão MUST receber conflito com o dono atual; a mesma issue MUST NOT ter duas entradas não removidas em caminhos distintos.

#### Scenario: Dois writers disputam o mesmo checkout
- **WHEN** duas sessões cooperantes executam a reserva do mesmo checkout ao mesmo tempo
- **THEN** exatamente uma recebe posse e a outra recebe código de conflito com o dono vencedor, sem posse simultânea

#### Scenario: Campos do dono registrado
- **WHEN** uma sessão reserva um checkout com run, etapa e `--owner-pid` opcional
- **THEN** owner registra sessão, run, etapa, host e somente o PID explicitamente fornecido; branch, caminho absoluto, base, issue e baseline ficam no registry

#### Scenario: Reserva idempotente do próprio dono
- **WHEN** a sessão que já é dona repete a reserva sem mudança externa
- **THEN** a reserva é confirmada sem criar segunda entrada

#### Scenario: Reserva planejada antes da criação
- **WHEN** o coordenador reserva um caminho ainda inexistente com `--planned --repository <checkout existente>` antes de `git worktree add`
- **THEN** identidade e lock vêm do checkout existente, o caminho planejado recebe estado `RESERVED` sem baseline e sem chamadas Git nele, e somente a mesma sessão/run pode ativá-lo após criação/verificação da branch; ausência de `--repository` é erro de uso

#### Scenario: Git worktree add falha sem criar destino
- **WHEN** o dono da reserva `RESERVED` informa `cancel-planned --session --run --repository <checkout existente> --reason <motivo>` e o destino não existe nem aparece em `git worktree list --porcelain`
- **THEN** sob lock a entrada passa a `REMOVED` com motivo no histórico, sem acessar Git no destino nem excluir arquivos

#### Scenario: Cancelamento de criação parcial ou por outro dono
- **WHEN** o destino existe, figura no inventário Git, a entrada já foi ativada ou sessão/run não correspondem ao dono `RESERVED`
- **THEN** `cancel-planned` recusa a operação sem remover worktree, diretório ou entrada; a criação parcial precisa de inspeção manual

#### Scenario: Identificadores incompatíveis ou issue duplicada
- **WHEN** sessão/run não obedece ao padrão seguro ou outra entrada não removida já usa a mesma issue em outro caminho
- **THEN** a primeira reserva falha por uso inválido, ou a segunda por conflito com indicação do caminho existente, sem conceder posse

### Requirement: API canônica versionada de estado de código
O módulo `worktree_registry.py` SHALL expor `FINGERPRINT_VERSION`, `SAFE_ID`, `is_known_generated`, `code_state(checkout, *, exclude_paths=(), include_ignored=())` e `drift_report(baseline, current, *, checkout)`. O estado SHALL conter HEAD, digest `sha256:v1:<hex>` e entradas por caminho com XY, conteúdo e índice; gerados são separados. O digest MUST incluir blobs/modos/estágios do índice; mudanças incompatíveis MUST usar nova versão. O relatório MUST comparar entradas completas.

#### Scenario: Alteração staged com working tree e XY iguais
- **WHEN** o blob ou modo de um caminho no índice é alterado mas HEAD, XY e conteúdo atual da working tree permanecem iguais
- **THEN** o digest muda e o relatório inclui esse caminho

#### Scenario: Exclusões, configuração ignorada e gerados
- **WHEN** um relatório de teste é excluído, uma configuração ignorada é declarada e apenas um bytecode conhecido aparece
- **THEN** o relatório e o bytecode não alteram o digest, a configuração declarada entra na entrada por caminho e seu hash afeta o digest, e os gerados são reportados separadamente

### Requirement: Identidade verificada antes de mutação
Antes de escrita, teste com efeitos, commit ou push, o participante SHALL verificar caminho, repositório, branch, HEAD, digest e dono contra a reserva. Divergência MUST impedir a mutação e informar o que divergiu. Toda inspeção Git do helper MUST desabilitar locks opcionais, sem escrever índice ou refs.

#### Scenario: Branch ou repositório diferente
- **WHEN** o checkout está em outra branch ou o remote não corresponde à identidade registrada
- **THEN** a verificação falha com código de identidade divergente e nenhuma mutação é autorizada

#### Scenario: Sessão que não é dona
- **WHEN** uma sessão diferente do dono registrado pede verificação para escrever
- **THEN** a verificação falha com conflito de posse

#### Scenario: Inspeção sem lock do índice e contrato JSON
- **WHEN** `status --json` ou `verify --json` inspeciona o checkout e o dono pode executar `git add` em paralelo
- **THEN** chamadas Git usam `--no-optional-locks` e `GIT_OPTIONAL_LOCKS=0`, e a resposta contém os campos estáveis de posse, estado de código, drift e classificação de caminhos

### Requirement: Respostas JSON consumíveis pelo orquestrador
O helper SHALL manter em `status`, `verify` e `reserve` com `--json`, inclusive erros 3/4/6, as chaves `ok`, `exit_code`, `error`, `path`, `issue_url`, `branch`, `state`, `owner`, `head`, `digest`, `drift`, `generated_paths`, `unknown_untracked_paths`, `last_verified_at`. O relatório de drift SHALL conter `head_before`, `head_after`, `commits`, `diverged`, `committed_paths`, `changed_paths` e `detected_at`.

#### Scenario: Drift no formato estável
- **WHEN** `reserve --json` detecta drift em checkout sem dono
- **THEN** retorna exit 4 e campos de estado, dono nulo e relatório com commits/caminhos alterados

### Requirement: Alteração externa detectada e distinguida de escrita própria
O helper SHALL comparar HEAD/digest com o baseline, inclusive sem dono em entradas liberadas. `verify` SHALL persistir drift ou recibo do dono/baseline. `checkpoint` SHALL exigir recibo válido, dono/identidade iguais e nenhum drift detectado, gravando o novo baseline após escrita. Drift detectado MUST suspender mutações até aceite explícito com motivo/histórico. `release` SHALL exigir igualdade com o checkpoint, sem absorver diferença. Autoria entre verify e checkpoint não é comprovável.

#### Scenario: Commit externo altera HEAD
- **WHEN** outro agente cria commit na branch reservada depois do último checkpoint
- **THEN** a próxima verificação falha com código de drift, lista o intervalo de commits e os caminhos alterados, e checkpoint ou nova verificação continuam recusados até o dono reconciliar explicitamente

#### Scenario: Escrita própria registrada
- **WHEN** o dono verifica, altera um arquivo e registra checkpoint
- **THEN** a verificação seguinte passa e não reporta alteração externa

#### Scenario: Drift já detectado não é escrita própria
- **WHEN** `verify` detecta diferença do baseline e o dono tenta `checkpoint`
- **THEN** checkpoint é recusado até aceite explícito do drift, mesmo que a sessão se declare autora

#### Scenario: Release após escrita própria
- **WHEN** o dono escreve após `verify` e tenta `release` sem checkpoint
- **THEN** release falha com drift e não troca dono nem baseline; após um checkpoint feito antes de detectar drift, release com baseline igual ao estado atual passa

#### Scenario: Release, mudança externa e reserva de outro writer
- **WHEN** uma reserva é liberada em `WAITING`, outro agente faz commit ou edição, e nova sessão tenta `reserve`
- **THEN** a reserva falha com drift e relatório sem assumir posse; somente `--accept-external --reason` explícitos registram o aceite/histórico e permitem assumir com novo baseline

#### Scenario: Arquivo gerado conhecido não é drift
- **WHEN** apenas arquivos gerados conhecidos surgem após o checkpoint
- **THEN** a verificação passa e os reporta separadamente como gerados

### Requirement: Transferência explícita de posse entre sessões
O helper SHALL transferir a posse de um checkout de uma sessão para outra de forma atômica, somente quando a sessão de origem é a dona atual e o estado verificado não tem drift. A transferência MUST manter caminho, branch, HEAD, trabalho parcial e histórico da entrada; após ela, a sessão anterior MUST perder a autorização de escrita.

#### Scenario: Planejamento transfere para Apply
- **WHEN** a sessão de planejamento transfere para a sessão de Apply o checkout com commit de proposta e diff parcial
- **THEN** a sessão de Apply verifica com sucesso o mesmo caminho/branch/HEAD/diff, e a sessão de planejamento passa a receber conflito de posse

#### Scenario: Transferência por quem não é dono
- **WHEN** uma sessão sem posse tenta transferir o checkout
- **THEN** a transferência é recusada e o registry não muda

### Requirement: Retomada e reconstrução sem tomada de posse por idade
O helper SHALL reconstruir entrada ausente/incompleta do Git real em `RECOVERY_REQUIRED`, com `owner=null` significando posse desconhecida, sem alterar arquivos. Baseline observado nesse estado MUST NOT autorizar `reserve`, `verify`, `checkpoint`, `release`, `handoff`, aceite de drift ou limpeza aplicada. SHALL expor inventário de worktrees/branch/HEAD/estado/diff/caminhos desconhecidos e digest para revisão. Idade MUST NOT autorizar posse.

#### Scenario: Writer interrompido e registry perdido
- **WHEN** o registry desaparece após um writer deixar diff parcial
- **THEN** a reconstrução registra branch, HEAD e fingerprint reais, `owner=null` e estado `RECOVERY_REQUIRED`, e o diff permanece intacto sem conceder posse

#### Scenario: Registry perdido enquanto writer anterior segue vivo sem PID registrado
- **WHEN** um writer ainda atua no checkout, o registry desaparece, e outra sessão tenta `reconcile` seguido de `reserve` (inclusive com `--accept-external --reason`)
- **THEN** o checkout fica em `RECOVERY_REQUIRED` e a nova sessão recebe conflito, sem posse ou absorção de diff; o operador deve comprovar o término fora do helper antes de retomar

#### Scenario: Entrada incompleta não é checkout livre
- **WHEN** uma entrada de registry perde campos obrigatórios e a sessão nova tenta reservá-la
- **THEN** `reconcile` preserva os dados recuperáveis e a bloqueia em `RECOVERY_REQUIRED`, sem substituir silenciosamente o dono por uma entrada `WAITING`

### Requirement: Takeover condicionado a término e inventário revisados
Takeover MUST exigir dono anterior esperado (ou `unknown` se perdido), referência a evidência externa de término revisada pelo coordenador/operador e digest do inventário revisado, refeito sob lock. PID anterior explicitamente fornecido ainda vivo no mesmo host MUST impedir takeover; ausência de PID ou idade não substitui evidência. Sem evidência confiável, manter bloqueio. O helper não autentica a referência nem impede writers externos não cooperantes.

#### Scenario: Reserva antiga sem evidência ou inventário revisado
- **WHEN** outra sessão tenta assumir uma reserva antiga sem dono anterior esperado, evidência de término revisada ou digest de inventário atual
- **THEN** a tomada é recusada independentemente da idade

#### Scenario: Retomada depois de término e inventário revisados
- **WHEN** a sessão nova informa o dono anterior esperado (ou `unknown` no registry perdido), referência à evidência externa de término revisada, digest do inventário revisado, e não há PID anterior registrado vivo no mesmo host
- **THEN** o helper refaz inventário sob lock, concede posse somente se o digest ainda corresponder, registra motivo/evidência e baseline no histórico e preserva o diff; inventário alterado impede a tomada

#### Scenario: PID explícito ainda vivo
- **WHEN** a reserva registrou `--owner-pid` de um worker ainda vivo no mesmo host e outra sessão apresenta evidência de término
- **THEN** o takeover é recusado sem apagar trabalho nem inferir que o processo do CLI efêmero é o worker

### Requirement: Arquivos gerados conhecidos separados de trabalho do usuário
O helper SHALL classificar não rastreados/ignorados como gerados (`__pycache__/`, `*.pyc`, `*.pyo`) ou desconhecidos; nome MUST NOT autorizar exclusão. `clean-generated` SHALL listar elegíveis/recusados e razões. Somente arquivos regulares não rastreados/não staged `*.py[co]` com header igual ao `importlib.util.MAGIC_NUMBER` do Python em execução são elegíveis; outros cabeçalhos MUST permanecer. Header é indício de formato, não prova de autoria ou integridade.

#### Scenario: Pycache e arquivo desconhecido coexistem
- **WHEN** o checkout contém `scripts/__pycache__/x.pyc` com magic header reconhecido, um arquivo novo desconhecido e uma alteração rastreada já no baseline, e o dono seleciona `x.pyc` com motivo após verificação válida
- **THEN** somente o bytecode selecionado é removido e reportado, e o arquivo desconhecido e a alteração rastreada permanecem

#### Scenario: Nome pyc sem origem verificável
- **WHEN** um arquivo `*.pyc` contém bytes arbitrários ou magic header não reconhecido, ou o dono pede `--apply` sem caminhos exatos ou motivo
- **THEN** nada desse arquivo é removido, mesmo que tenha sido classificado como gerado pelo nome

### Requirement: Limpeza aplicada verificada e restrita ao selecionado
`clean-generated --apply` MUST exigir dono, seleção exata e motivo; sob lock MUST revalidar identidade, posse, HEAD/digest, recibo `verified_for` atual e ausência de drift antes de reenumerar. MUST revalidar metadados e header antes de desvincular cada arquivo, sem seguir symlinks, varrer diretórios ignorados por outros motivos ou remover arquivos desconhecidos/rastreados/diff. Só remove `__pycache__` vazio após remoção própria; não promete proteção contra corrida final de writer externo.

#### Scenario: Drift ou verificação inválida antes da limpeza
- **WHEN** houve drift persistido/novo, recibo de verify ausente/obsoleto, mudança de identidade ou de dono antes de `--apply`
- **THEN** a verificação refeita sob lock impede qualquer remoção e relata a divergência

#### Scenario: Candidato muda ou vira symlink
- **WHEN** o arquivo selecionado ou um ancestral se torna symlink, ou metadados/cabeçalho mudam antes de desvincular
- **THEN** o helper recusa o candidato sem segui-lo nem apagar o novo conteúdo

#### Scenario: Limpeza sem posse
- **WHEN** uma sessão sem posse pede a limpeza aplicada
- **THEN** nada é removido e o comando falha com conflito de posse

#### Scenario: Bytecode dentro de diretório ignorado alheio
- **WHEN** `.venv/lib/__pycache__/x.pyc` está ignorado por `.venv/` e há bytecode elegível selecionado em `scripts/__pycache__/`
- **THEN** a limpeza aplicada preserva `.venv/` e remove somente o bytecode elegível de `scripts/`

### Requirement: Helpers não criam bytecode que bloqueie o fluxo
Os helpers Python distribuídos SHALL executar sem gravar bytecode dos seus módulos, inclusive futuros helpers distribuídos por `scripts/sync-plugin`, e o repositório MUST ignorar `__pycache__/` e `*.py[co]`. Arquivo gerado conhecido MUST NOT exigir decisão de produto para seguir com atualização de `main`.

#### Scenario: Executar helpers e testes
- **WHEN** os helpers são executados sem `PYTHONDONTWRITEBYTECODE` e a suíte de testes roda
- **THEN** `scripts/` não recebe `__pycache__` pelos helpers e `git status --porcelain` permanece limpo

### Requirement: Convenção de checkout principal e limites externos
O helper SHALL recusar reservar o checkout principal para escrita de issue, salvo opção explícita quando a convenção do projeto permitir, e MUST NOT criar, mover ou remover worktrees. A documentação MUST declarar que o controle coordena apenas participantes cooperantes: agentes externos não são impedidos, somente detectados na próxima verificação.

#### Scenario: Reserva do checkout principal
- **WHEN** uma sessão pede reserva do checkout principal sem a opção explícita
- **THEN** a reserva é recusada com orientação para usar o worktree da issue

#### Scenario: Limite documentado
- **WHEN** um participante lê o protocolo de worktrees
- **THEN** encontra os limites de coordenação com agentes que não usam o protocolo e o comportamento de detecção por verificação
