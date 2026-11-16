# Spec Delta

## ADDED Requirements

### Requirement: Launcher global de reserva utilizável no PATH
A instalação global SHALL disponibilizar `worktree-reservation` no PATH como entrada estável da versão ativa, preservando execução dos módulos acompanhantes. MUST NOT substituir comando já existente de outra origem ou personalizado e MUST informar como tornar o comando acessível quando o diretório de instalação não estiver no PATH.

#### Scenario: Uso fora do diretório do pacote
- **WHEN** a instalação termina e o usuário invoca `worktree-reservation` de um checkout independente
- **THEN** o comando executa o helper ativo com seus módulos e devolve o código e a saída originais

#### Scenario: Nome global ocupado
- **WHEN** o destino do comando ou a resolução efetiva no PATH pertence a outra origem
- **THEN** o instalador bloqueia com diagnóstico e preserva o comando existente e a instalação anterior

#### Scenario: Falha antes de publicar
- **WHEN** instalação ou atualização falha após preparar a entrada mas antes da ativação
- **THEN** o launcher e a versão ativa previamente funcionais permanecem utilizáveis, sem tomar posse de arquivos desconhecidos

#### Scenario: Diretório global fora do PATH
- **WHEN** o launcher não pode ser descoberto pelo PATH efetivo
- **THEN** a instalação não declara o comando global disponível e indica a ação necessária sem alterar o PATH do usuário silenciosamente

#### Scenario: Orientação do launcher em ambiente OpenSpec 2.0
- **WHEN** a instalação publica a orientação do comando global de reserva em ambiente com OpenSpec 2.0
- **THEN** o uso do launcher é comprovado independentemente da existência de `/opsx-*` e a orientação conserva o contrato nativo de skills oficiais entregue pela #71 no merge `5e33688d2a9db702e6bd0f2027d778f3baebdf35`, sem oferecer comandos legados fabricados nem instalação 1.x como condição para utilizar a reserva; a verificação de bootstrap OpenSpec segue seu contrato próprio e não é declarada aprovada por esta prova
