# milestone-monitor-state Specification

## Purpose
Consolidar fontes verificáveis de GitHub, workflow e runtime em um estado local reinicializável, sem alterar o workflow nem fabricar progresso ou aprovação.

## Requirements

### Requirement: Inventário completo e identidades compostas
O monitor SHALL identificar issues por repositório/número e milestones por repositório/número, carregar todos os itens dos alvos configurados com paginação e excluir PRs do total de issues. Ausência de instrumentação MUST NOT excluir uma issue.

#### Scenario: Números iguais em projetos distintos
- **WHEN** dois repositórios têm milestone 1 e issue 7 e uma página adicional contém issues sem run
- **THEN** os projetos permanecem distintos e todas as issues aparecem uma única vez no respectivo milestone

### Requirement: Reutilização do registro v1
O monitor SHALL consumir comentários estruturados v1 e preservar a semântica de correlação, métricas e evidências de workflow-metrics e workflow-execution-state. MUST NOT escrever eventos de workflow nem tratar referência de evidência ou relatório presente como aprovação.

#### Scenario: Registro legado e relatório sem veredito
- **WHEN** uma issue contém um run legado e outra tem teste com relatório presente e referência evidence
- **THEN** as métricas permanecem compatíveis e nenhum teste recebe aprovação apenas por esses campos

### Requirement: Reconstrução idempotente e segura
O monitor SHALL persistir snapshots completos por fonte e reconstruir a projeção após reinício. Releituras, duplicatas e eventos atrasados MUST NOT duplicar issues ou confirmar outra incarnação. Snapshot parcial, inválido ou interrompido MUST NOT substituir o último snapshot completo.

#### Scenario: Atualização interrompida e callback atrasado
- **WHEN** uma atualização falha após a primeira página e depois chega callback de A após abertura de B
- **THEN** o snapshot completo anterior permanece utilizável e B não herda estado ou duração de A

### Requirement: Seleção explícita de run e concorrência
O monitor SHALL selecionar por padrão o run de criação mais recente, desempatar deterministicamente e permitir consultar runs anteriores. Outros runs simultaneamente abertos SHALL ficar visíveis como conflito, sem somar issues. Workers e incarnações SHALL conservar identidades e estados próprios.

#### Scenario: Dois runs abertos e vários workers
- **WHEN** a mesma issue tem dois runs abertos, com um worker aguardando decisão e outro ativo
- **THEN** o monitor indica a concorrência, mostra cada execução nos detalhes e contabiliza a issue uma vez pela precedência documentada

### Requirement: Vínculo explícito do runtime
O adaptador SHALL aceitar vínculo validado de repositório, issue, run, etapa, worker, execução tipada, sessão e worktree. MUST NOT inferir vínculo de título, texto livre, branch parecida ou diretório do plugin; vínculo ambíguo ou incompatível SHALL produzir desconhecido sem contaminar outra issue.

#### Scenario: Sessão reutilizada em outra etapa
- **WHEN** uma sessão muda de localização ou o vínculo aponta a uma incarnação encerrada
- **THEN** a atividade posterior não confirma a incarnação antiga e o vínculo exige reconciliação explícita

#### Scenario: Sessão muda de worktree entre duas coletas
- **WHEN** uma sessão vinculada permanece ativa mas seu diretório muda para outra worktree do mesmo projeto antes da próxima coleta
- **THEN** a próxima amostra revalida a localização, recusa confirmar atividade no vínculo antigo e não usa projectID compartilhado nem concatenação de subpath como prova de igualdade

### Requirement: Captura oficial não invasiva
O adaptador OpenCode SHALL usar mecanismos oficiais compatíveis com a versão declarada e registrar somente metadados permitidos. Sessão ativa significa atividade de sessão, não aprovação de teste, término de etapa ou merge. Falha, indisponibilidade ou ausência de sessão SHALL ser distinguíveis sem alterar o workflow.

#### Scenario: Sessão inativa após reabertura do painel
- **WHEN** a consulta oficial retorna sucesso e a sessão vinculada não consta entre as ativas
- **THEN** o monitor mostra sessão inativa e reconciliação quando necessária, sem manter executando nem concluir a etapa automaticamente

#### Scenario: Runtime indisponível
- **WHEN** a API falha, nega acesso ou retorna contrato incompatível
- **THEN** o monitor preserva o histórico, informa desconhecido/indisponível e não interfere no agente

#### Scenario: Contexto ou versão do servidor muda
- **WHEN** server.info indica versão diferente do release fixado ou mudança de processo/contexto em relação ao vínculo
- **THEN** o monitor não transfere confirmação automaticamente nem renova TTL pelo cache, revalida o vínculo e exige nova conferência de contrato para release divergente

### Requirement: Frescor separado por fonte
O monitor SHALL exibir última coleta bem-sucedida, última observação e falha por fonte. Atividade vencida MUST NOT aparecer como executando confirmado. Cache carregado e GitHub indisponível SHALL ser marcados como desatualizados, não como atualização ao vivo.

#### Scenario: Confirmação antiga sem nova consulta
- **WHEN** a validade configurada da observação expira durante falha de rede ou runtime
- **THEN** a atividade passa a desconhecida e o horário da última confirmação permanece visível

### Requirement: Estados exclusivos e conclusão por GitHub
O monitor SHALL contar cada issue em exatamente um grupo: concluída, executando, pendente ou bloqueada. Decisão, falha, espera e desconhecido SHALL ter rótulos distintos. O percentual SHALL usar issues fechadas/total conforme GitHub, com zero issues exibindo 0/0 e percentual indisponível; fechamento MUST NOT provar entrega verificada.

#### Scenario: Esperas e ausência de eventos
- **WHEN** existem issues aguardando humano, com falha, sem eventos e ativas com confirmação recente
- **THEN** humano/falha contam como bloqueadas, sem eventos como pendentes, ativas como executando, sem dupla contagem

### Requirement: Reconciliação de GitHub e execução
O monitor SHALL aplicar associação de milestone e estado da issue do último inventário GitHub completo, preservando separadamente estado de PR/merge verificado e conflitos com execução. Reabrir ou mover uma issue SHALL atualizar percentual e associação sem perder seu histórico.

#### Scenario: PR mergeada com issue aberta
- **WHEN** uma PR vinculada tem merge confirmado mas a issue continua aberta
- **THEN** o merge aparece nos detalhes sem tornar a issue concluída nem aumentar o percentual de conclusão

#### Scenario: Issue fechada depois reaberta e movida
- **WHEN** o próximo inventário completo informa reabertura em outro milestone
- **THEN** a issue deixa o total concluído anterior e aparece somente no milestone atual, com histórico preservado

### Requirement: Persistência local e isolamento de falhas
O monitor SHALL persistir estado fora do checkout com escrita atômica e exclusão de escritores concorrentes, permitir leitores simultâneos e preservar dados em erros de armazenamento. Fechar a TUI MUST NOT parar agentes; indisponibilidade de uma fonte MUST NOT impedir visualizar as demais.

#### Scenario: Dois painéis e armazenamento ocupado
- **WHEN** dois painéis atualizam o mesmo cache e um deles falha durante a transação
- **THEN** nenhum snapshot parcial é publicado, os leitores mantêm o último estado íntegro e nenhuma sessão OpenCode é interrompida

### Requirement: Privacidade e autorização das fontes
O monitor SHALL usar acesso já autorizado para alvos explícitos e persistir apenas metadados necessários. MUST NOT guardar credenciais, prompts, raciocínio, corpos de ferramentas, logs extensos ou erros brutos; conteúdo externo SHALL ser tratado como dado, nunca comando, e sequências de controle SHALL ser neutralizadas na apresentação.

#### Scenario: Texto externo com escape e erro sensível
- **WHEN** título contém controles de terminal e a integração falha com mensagem contendo segredo
- **THEN** a apresentação sanitiza o título, o erro público é categorizado e cache/logs não contêm o segredo nem payload bruto
