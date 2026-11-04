# Spec Delta

## Purpose

Garantir que, entre participantes cooperantes do workflow, exista no máximo um writer por checkout, que mudanças externas sejam detectadas antes da próxima mutação e que retomadas e limpezas preservem trabalho parcial e arquivos desconhecidos, usando o registry local definido no protocolo de worktrees.

## ADDED Requirements

### Requirement: Registry local único com acesso serializado
O helper SHALL usar exclusivamente o registry `ai-workflow/worktrees.json` no Git common dir do repositório, criando-o quando ausente. Toda leitura-modificação-escrita MUST ocorrer sob lock exclusivo comum a todos os worktrees e gravar o arquivo de forma atômica. Se a exclusividade não puder ser estabelecida, o helper MUST falhar sem alterar o registry nem conceder posse.

#### Scenario: Registry materializado no Git common dir
- **WHEN** um writer reserva um worktree auxiliar de um repositório sem registry
- **THEN** o registry é criado em `<git-common-dir>/ai-workflow/worktrees.json`, fora da árvore rastreada, com identidade do repositório e a entrada do checkout

#### Scenario: Lock indisponível
- **WHEN** outro processo mantém o lock além do tempo de espera ou o mecanismo de lock não existe na plataforma
- **THEN** o comando termina com código de lock indisponível e o registry permanece byte a byte inalterado

#### Scenario: Registry corrompido
- **WHEN** o registry existe mas não é JSON válido no esquema esperado
- **THEN** o helper recusa mutações, preserva o arquivo e orienta a reconstrução verificada

### Requirement: Reserva exclusiva de escrita
O helper SHALL conceder posse ativa de um checkout a no máximo uma sessão. Uma reserva MUST registrar repositório, issue, branch, caminho absoluto, base, dono (sessão, run, etapa, host e processo), estado do lifecycle, HEAD, fingerprint do diff e horário da verificação. Pedido de outra sessão para checkout com dono ativo MUST falhar com conflito explícito que identifica o dono atual.

#### Scenario: Dois writers disputam o mesmo checkout
- **WHEN** duas sessões cooperantes executam a reserva do mesmo checkout ao mesmo tempo
- **THEN** exatamente uma recebe posse e a outra recebe código de conflito com o dono vencedor, sem posse simultânea

#### Scenario: Reserva idempotente do próprio dono
- **WHEN** a sessão que já é dona repete a reserva sem mudança externa
- **THEN** a reserva é confirmada sem criar segunda entrada

### Requirement: Identidade verificada antes de mutação
Antes de escrita, teste com efeitos, commit ou push, o participante SHALL verificar com o helper que caminho, repositório, branch, HEAD, fingerprint do diff e dono correspondem à reserva. Divergência MUST impedir a mutação e informar o que divergiu.

#### Scenario: Branch ou repositório diferente
- **WHEN** o checkout está em outra branch ou o remote não corresponde à identidade registrada
- **THEN** a verificação falha com código de identidade divergente e nenhuma mutação é autorizada

#### Scenario: Sessão que não é dona
- **WHEN** uma sessão diferente do dono registrado pede verificação para escrever
- **THEN** a verificação falha com conflito de posse

### Requirement: Alteração externa detectada e distinguida de escrita própria
O helper SHALL comparar HEAD e fingerprint do diff atuais com o último checkpoint do dono. Escrita autorizada do próprio dono MUST ser registrada por checkpoint após a mutação; qualquer diferença não registrada MUST ser tratada como alteração externa, suspender mutações até reconciliação explícita e listar commits e caminhos afetados para invalidar somente a evidência atingida.

#### Scenario: Commit externo altera HEAD
- **WHEN** outro agente cria commit na branch reservada depois do último checkpoint
- **THEN** a próxima verificação falha com código de drift, lista o intervalo de commits e os caminhos alterados, e checkpoint ou nova verificação continuam recusados até o dono reconciliar explicitamente

#### Scenario: Escrita própria registrada
- **WHEN** o dono verifica, altera um arquivo e registra checkpoint
- **THEN** a verificação seguinte passa e não reporta alteração externa

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
O helper SHALL reconstruir uma entrada ausente ou incompleta a partir do estado real do Git, sem dono ativo e sem alterar arquivos do checkout. Idade da reserva MUST NOT autorizar tomada de posse. Assumir checkout com dono registrado MUST exigir o dono anterior esperado e evidência de término; se o processo anterior estiver comprovadamente vivo no mesmo host, a tomada MUST ser recusada.

#### Scenario: Writer interrompido e registry perdido
- **WHEN** o registry desaparece após um writer deixar diff parcial
- **THEN** a reconstrução registra branch, HEAD e fingerprint reais, nenhum dono ativo, e o diff permanece intacto

#### Scenario: Reserva antiga sem evidência de término
- **WHEN** outra sessão tenta assumir uma reserva antiga sem informar dono anterior e evidência de término
- **THEN** a tomada é recusada independentemente da idade

#### Scenario: Tomada após término comprovado
- **WHEN** a sessão nova informa o dono anterior esperado, evidência de término, e o processo anterior não está vivo
- **THEN** a posse é transferida, a evidência é registrada no histórico e o diff é preservado

### Requirement: Arquivos gerados conhecidos separados de trabalho do usuário
O helper SHALL classificar caminhos não rastreados e ignorados como gerados conhecidos (`__pycache__/`, `*.pyc`, `*.pyo`) ou desconhecidos. A limpeza MUST remover apenas gerados conhecidos dentro do checkout reservado, pelo dono, com listagem prévia por padrão e relatório dos caminhos removidos; arquivos desconhecidos, rastreados e alterações parciais MUST permanecer intactos.

#### Scenario: Pycache e arquivo desconhecido coexistem
- **WHEN** o checkout contém `scripts/__pycache__/x.pyc`, um arquivo novo desconhecido e uma alteração rastreada, e o dono executa a limpeza aplicada
- **THEN** somente o bytecode é removido, e o arquivo desconhecido e a alteração rastreada permanecem

#### Scenario: Limpeza sem posse
- **WHEN** uma sessão sem posse pede a limpeza aplicada
- **THEN** nada é removido e o comando falha com conflito de posse

### Requirement: Helpers não criam bytecode que bloqueie o fluxo
Os helpers Python distribuídos SHALL executar sem gravar bytecode dos seus módulos, e o repositório MUST ignorar `__pycache__/` e `*.py[co]`. Arquivo gerado conhecido MUST NOT exigir decisão de produto para seguir com atualização de `main`.

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
