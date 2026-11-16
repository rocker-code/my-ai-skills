# Spec Delta

## ADDED Requirements

### Requirement: Seleção implícita segura da raiz do checkout
Para comandos sobre um checkout existente, o helper SHALL usar `--path` explícito quando fornecido; sem ele SHALL selecionar a raiz Git do worktree que contém o diretório corrente. MUST NOT selecionar outro checkout ou presumir que um subdiretório é a raiz.

#### Scenario: Raiz e subdiretório de linked worktree
- **WHEN** uma sessão executa `verify --session <id>` na raiz ou num subdiretório de seu linked worktree
- **THEN** o helper verifica a mesma raiz canônica e a reserva desse worktree, sem consultar a reserva do checkout principal ou de outro linked worktree

#### Scenario: Caminho explícito prevalece e aceita espaços
- **WHEN** uma sessão executa `verify --path <checkout com espaços> --session <id>` de outro diretório
- **THEN** o helper verifica exclusivamente o checkout indicado e mantém a validação de repositório e owner

#### Scenario: Diretório sem checkout e sem path
- **WHEN** um comando para checkout existente é invocado fora de qualquer worktree Git sem `--path`
- **THEN** a operação falha com código de uso ou identidade e indicação para informar `--path`, sem escolher checkout de outro projeto nem conceder posse

#### Scenario: Destino ausente não é inferido
- **WHEN** `reserve --planned`, `cancel-planned` ou `mark-removed` omite o caminho de destino
- **THEN** a operação exige `--path` e os parâmetros explícitos de repositório aplicáveis, sem inventar destino a partir do diretório corrente

### Requirement: Resumo humano e JSON compatível da reserva
O helper SHALL emitir por padrão resumo nativo legível do resultado, estado, owner, HEAD, digest e drift, com causa e próxima ação segura quando falhar. `--json` MUST manter campos, tipos e códigos anteriores em sucesso e erro, com stdout exclusivamente JSON válido. O resumo MUST NOT substituir o gate de `verify` por `status` nem imprimir inventário completo em todo `verify`.

#### Scenario: Verificação humana bem-sucedida
- **WHEN** o dono executa `verify --session <id>` sem `--json`
- **THEN** a saída apresenta resultado, estado, owner, HEAD e digest completos, sem exigir pipe para filtrar o inventário

#### Scenario: Conflito, drift e falhas operacionais
- **WHEN** há sessão alheia, drift, lock indisponível, registry inválido ou identidade divergente
- **THEN** a saída legível apresenta causa, código distinto, owner ou caminhos envolvidos quando disponíveis e uma ação segura, sem mascarar a falha por formatação posterior

#### Scenario: JSON de sucesso e erro
- **WHEN** automação invoca o helper com `--json` em sucesso ou conflito
- **THEN** stdout contém somente um objeto JSON parseável com os campos/tipos estáveis, dados de diagnóstico e exit code original

### Requirement: Resumos operacionais por comando
Para `reconcile` o resumo SHALL expor `inventory.digest` completo; para `clean-generated` SHALL expor caminhos exatos, elegibilidade e motivos dos candidatos; para `list` SHALL expor as entradas de reserva com caminho e dono/estado.

#### Scenario: Inventário para takeover
- **WHEN** o operador executa `reconcile` sem `--json` para revisar um checkout antes de `--takeover`
- **THEN** o resumo inclui o `inventory.digest` completo necessário ao argumento `--inventory-digest` e dados suficientes para revisar o inventário, sem confundi-lo com o digest de código do checkout; a verificação de takeover permanece condicionada à evidência externa de término e ao inventário refeito sob lock

#### Scenario: Candidatos de limpeza
- **WHEN** o operador executa `clean-generated` sem `--json` para selecionar arquivos
- **THEN** o resumo lista cada caminho exato com elegibilidade e motivo de recusa, e não autoriza `--apply` sem seleção, posse, recibo e motivo exigidos

#### Scenario: Lista de reservas
- **WHEN** o operador executa `list --repository <checkout>` sem `--json`
- **THEN** o resumo apresenta cada reserva com caminho, issue, branch, estado e dono, inclusive lista vazia legível, sem conceder posse

### Requirement: Identidade do chamador permanece explícita
Comandos que exigem `--session` SHALL obter a identidade do chamador por argumento explícito; o helper MUST NOT inferir sessão do owner registrado, mesmo quando houver exatamente uma reserva ativa. Handoff e takeover MUST manter exigências próprias de identidade/evidência.

#### Scenario: Sessão omitida ou alheia
- **WHEN** alguém executa `verify` sem sessão ou com sessão diferente do dono
- **THEN** a ausência recebe erro de uso e a sessão alheia recebe conflito, sem registrar recibo para qualquer uma delas

#### Scenario: Handoff após checkpoint
- **WHEN** o dono verifica, escreve, faz checkpoint e transfere explicitamente para a próxima sessão
- **THEN** a sessão antiga perde autorização e a nova pode verificar o checkout, conservando os mesmos invariantes de estado e drift
