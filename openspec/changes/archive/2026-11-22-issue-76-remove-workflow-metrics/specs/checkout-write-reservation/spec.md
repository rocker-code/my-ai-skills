## MODIFIED Requirements

### Requirement: Reserva exclusiva de escrita
O helper SHALL conceder posse ativa de um checkout a no máximo uma sessão. Uma reserva MUST registrar repositório, issue, branch, caminho, base, dono, lifecycle, baseline de código e horário. Sessão/run MUST seguir os padrão seguro próprio `SAFE_ID` (`^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$`). Outra sessão MUST receber conflito com o dono atual; a mesma issue MUST NOT ter duas entradas não removidas em caminhos distintos.

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

