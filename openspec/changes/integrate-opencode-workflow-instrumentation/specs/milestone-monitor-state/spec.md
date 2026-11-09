# Spec Delta

## MODIFIED Requirements

### Requirement: Frescor separado por fonte
O monitor SHALL exibir última coleta bem-sucedida, última observação e falha por fonte. Atividade vencida MUST NOT aparecer como executando confirmado. Cache carregado e GitHub indisponível SHALL ser marcados como desatualizados, não como atualização ao vivo. Observações de um coletor independente SHALL confirmar atividade somente mediante identidade validada do coletor atual, saúde e amostra dentro do TTL; reabrir a TUI não renova confirmação.

#### Scenario: Confirmação antiga sem nova consulta
- **WHEN** a validade configurada da observação expira durante falha de rede ou runtime
- **THEN** a atividade passa a desconhecida e o horário da última confirmação permanece visível

#### Scenario: Reabrir painel com observador saudável
- **WHEN** existe amostra recente de observador vivo e saudável, do contexto e revisão do vínculo atuais
- **THEN** o painel pode mostrar atividade confirmada sem exigir que a amostra seja posterior à abertura da TUI, identificando fonte e horário reais

#### Scenario: Heartbeat sem observação nova
- **WHEN** o observador continua vivo mas perde acesso ao runtime e só atualiza seu próprio heartbeat
- **THEN** a validade da última confirmação não é renovada e o painel informa a falha da fonte

### Requirement: Persistência local e isolamento de falhas
O monitor SHALL persistir estado fora do checkout com escrita atômica e exclusão de escritores concorrentes, permitir leitores simultâneos e preservar dados em erros de armazenamento. Fechar a TUI MUST NOT parar agentes; indisponibilidade de uma fonte MUST NOT impedir visualizar as demais. Coleta headless e TUI SHALL coordenar a posse da coleta, sem competir por snapshots nem tornar a TUI publicadora de eventos de workflow.

#### Scenario: Dois painéis e armazenamento ocupado
- **WHEN** dois painéis atualizam o mesmo cache e um deles falha durante a transação
- **THEN** nenhum snapshot parcial é publicado, os leitores mantêm o último estado íntegro e nenhuma sessão OpenCode é interrompida

#### Scenario: Observador assume coleta antes feita pelo painel
- **WHEN** um observador assume a coleta compartilhada enquanto existe uma consulta do painel em andamento
- **THEN** a resposta do antigo coletor não substitui a observação da nova posse; fechar o painel não encerra o observador

## ADDED Requirements

### Requirement: Separação entre sinal local e registro canônico
O monitor SHALL apresentar atividade e pedidos pendentes observados no runtime separadamente da etapa, espera e tempo registrados no workflow. Pendência de publicação e lacunas SHALL ficar visíveis. Sinais locais MUST NOT reescrever o registro canônico, somar duração inferida ou aumentar conclusão GitHub.

#### Scenario: Permissão pendente ainda não registrada pelo coordenador
- **WHEN** o observador confirma permissão pendente mas o coordenador ainda não registrou uma espera canônica
- **THEN** o painel mostra a permissão como pendência observada, classifica a issue aberta como bloqueada enquanto o sinal for válido e não apresenta tempo canônico inventado

#### Scenario: Runtime confirma trabalho enquanto publicação está pendente
- **WHEN** existe vínculo previamente validado e atividade recente, mas uma transição não foi publicada por falha GitHub
- **THEN** os detalhes mostram atividade e publicação pendente sem apresentar a transição local como etapa já registrada no GitHub

#### Scenario: Espera canônica tem precedência
- **WHEN** há espera canônica aberta para uma issue e um worker paralelo possui atividade confirmada
- **THEN** a issue continua bloqueada, a atividade permanece nos detalhes e a issue não é contada duas vezes
