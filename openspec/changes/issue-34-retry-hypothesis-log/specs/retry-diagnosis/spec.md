# Spec Delta

## MODIFIED Requirements

### Requirement: Agrupamento por assinatura e obrigação
O workflow SHALL agrupar tentativas pela obrigação (requisito/cenário da matriz) e pela assinatura normalizada da falha. Comando, filtro, ordem de execução ou nome do alvo MUST NOT fazer parte da chave de agrupamento. A assinatura distinta após falha SHALL tornar a assinatura anterior histórica/progredida, não aprovada; somente a última tentativa da obrigação é sua obrigação ativa.

#### Scenario: Comando renomeado não reinicia a contagem
- **WHEN** duas tentativas da mesma obrigação falham com a mesma assinatura usando comandos ou filtros diferentes
- **THEN** ambas contam no mesmo grupo como tentativas sem progresso

#### Scenario: Assinatura diferente abre novo grupo
- **WHEN** uma tentativa da mesma obrigação falha com assinatura diferente
- **THEN** a tentativa é contada como progresso do episódio anterior e inicia um novo episódio ativo; a falha antiga permanece visível e não aprovada, mas não bloqueia `--final` se o episódio ativo for aprovado

#### Scenario: Assinatura A falha, B falha e B passa
- **WHEN** A falha, uma assinatura B diferente falha e a tentativa seguinte de B passa com resolução `passed`
- **THEN** A permanece histórico/progredido, B é o único episódio ativo aprovado e `--final` pode retornar `ready=true` sem resolução `passed` fictícia para A

#### Scenario: Retorno à assinatura anterior
- **WHEN** A falha duas vezes, B distinto registra progresso, e uma falha A reaparece depois de B
- **THEN** A inicia novo episódio com uma falha, sem herdar a sequência de duas falhas anterior; A é novamente a obrigação ativa pendente até passar ou ser bloqueada validamente

### Requirement: Diagnóstico obrigatório após duas tentativas sem progresso
Depois de duas falhas sem progresso no episódio contínuo da mesma assinatura/obrigação, o workflow SHALL exigir diagnóstico antes de qualquer nova tentativa nesse episódio, mesmo que ela declare `pass`. O diagnóstico SHALL registrar classificação, fase/escopo/lifecycle/consumidores efetivos, prova de runtime ou não aplicabilidade justificada e a próxima hipótese.

#### Scenario: Terceira tentativa sem diagnóstico
- **WHEN** um grupo tem duas tentativas falhas equivalentes e uma terceira tentativa é registrada sem diagnóstico anterior a ela
- **THEN** o verificador reporta violação do limite de tentativas

#### Scenario: Terceira tentativa declarada aprovada sem diagnóstico
- **WHEN** um grupo acumula duas falhas e a terceira tentativa é marcada `pass` sem diagnóstico registrado entre a segunda e a terceira
- **THEN** o verificador reporta a mesma violação e não aprova o handoff final

#### Scenario: Terceira tentativa após diagnóstico
- **WHEN** o diagnóstico completo é registrado depois da segunda falha e antes da terceira tentativa do mesmo grupo
- **THEN** o limite de tentativas não é violado, independentemente de a terceira tentativa passar ou falhar

#### Scenario: Override que não altera a configuração lida (T1)
- **WHEN** duas tentativas aplicam overrides temporários e o validador continua lendo o mesmo valor
- **THEN** o diagnóstico registrado aponta fase/escopo efetivo da configuração e a próxima tentativa testa uma hipótese diferente

#### Scenario: Progresso zera a sequência, não apaga o histórico
- **WHEN** duas falhas A são seguidas de tentativa B com assinatura distinta e, mais tarde, uma tentativa A
- **THEN** a tentativa B não requer diagnóstico para A e a primeira tentativa do novo episódio A não viola o limite; as duas falhas anteriores continuam registradas, sem aprovação

### Requirement: Nova tentativa declara evidência ou hipótese nova
Cada nova tentativa do episódio SHALL declarar a mudança realizada e hipótese inédita ou evidência nova substantiva. Se repetir hipótese no episódio, SHALL registrar `observed_change` concreto, `observed_effect` diferente do da tentativa anterior dessa hipótese após normalizar minúsculas/espaços e uma referência nova em `evidence[]` que sustente a mudança. O verificador SHALL comparar efeito e refs; a revisão SHALL confirmar o conteúdo citado sem ler o manifesto de execução.

#### Scenario: Hipótese repetida sem evidência nova
- **WHEN** uma tentativa repete a hipótese de uma tentativa anterior do mesmo grupo e não referencia evidência nova
- **THEN** o verificador reporta violação

#### Scenario: Novo ID sem mudança de observação
- **WHEN** uma hipótese é repetida com referência nova, mas assinatura e efeito observado normalizados permanecem iguais aos da tentativa anterior dessa hipótese
- **THEN** o verificador reporta violação mesmo com o ID novo; sucesso ou novo nome de arquivo não substitui mudança observada

#### Scenario: Mudança observada não resumida ou não citada
- **WHEN** uma hipótese é repetida com efeito observado diferente, mas sem resumo concreto da mudança ou sem referência nova que a sustente
- **THEN** o verificador reporta violação

#### Scenario: Mesma assinatura com efeito alterado
- **WHEN** a hipótese e a assinatura de falha se repetem, mas o efeito observado muda de fato, é resumido e cita evidência nova
- **THEN** a tentativa satisfaz a regra de evidência substantiva mesmo sob a mesma assinatura, sujeita à confirmação da citação e aos demais gates do grupo

#### Scenario: Hipótese nova explícita
- **WHEN** uma tentativa após o diagnóstico declara hipótese distinta das anteriores
- **THEN** a tentativa é aceita

### Requirement: Correção focada na camada classificada
Enquanto houver falha de ambiente/setup não resolvida numa obrigação, tentativas posteriores nessa obrigação MUST NOT alterar código de aplicação, mesmo após tentativas intermediárias de outra classe/assinatura. O foco cessa com tentativa `pass` posterior na obrigação ou diagnóstico completo posterior à falha que reclassifique a causa com prova nova de runtime; uma assinatura diferente, isoladamente, não prova reclassificação.

#### Scenario: Falha de serviço antes do PHPUnit (T4)
- **WHEN** a falha ocorre na inicialização de serviço antes do runner de testes e a próxima tentativa altera código de aplicação sem reclassificação
- **THEN** o verificador reporta violação de foco

#### Scenario: Correção no ambiente descartável
- **WHEN** a mesma falha classificada como ambiente/setup é seguida de tentativa que altera apenas o ambiente descartável
- **THEN** a tentativa é aceita

#### Scenario: Falha intermediária não contorna o foco
- **WHEN** falha de ambiente é seguida por falha de outra assinatura/classe na mesma obrigação, sem sucesso nem reclassificação comprovada, e a próxima tentativa muda a aplicação
- **THEN** o verificador reporta violação de foco

#### Scenario: Sucesso posterior encerra o foco
- **WHEN** uma tentativa posterior na mesma obrigação passa após a falha de ambiente e uma tentativa seguinte altera a aplicação
- **THEN** a falha de ambiente anterior não produz `E_FOCUS` (outros gates continuam aplicáveis)

#### Scenario: Reclassificação substantiva antes de mudar a aplicação
- **WHEN** após a falha de ambiente um diagnóstico completo para essa falha reclassifica a causa, cita evidência de execução nova de fase/lifecycle efetivos e justifica a mudança de camada antes da edição da aplicação
- **THEN** a edição pode prosseguir, sujeita à confirmação semântica da prova pelo revisor; diagnóstico incompleto, prova antiga ou só citação de código não libera o foco

### Requirement: Limite de tentativas não vira aprovação
O limite de tentativas SHALL disparar investigação, não aprovação. Um episódio ativo com última tentativa `fail` MUST permanecer não aprovado; episódio histórico progredido SHALL permanecer não aprovado, mas não bloqueia sozinho a prontidão da obrigação ativa. `blocked` SHALL referenciar bloqueio válido do mesmo episódio. Skip, asserção enfraquecida ou `passed` sem referência à última tentativa `pass` do episódio MUST ser rejeitados.

#### Scenario: Grupo pendente no handoff final
- **WHEN** o handoff para `prepare-pr` contém episódio ativo cuja última tentativa falhou
- **THEN** o verificador, no modo de handoff final, reporta o episódio como pendente ou bloqueado, nunca aprovado para PR

#### Scenario: Bloqueio corretamente classificado no handoff final
- **WHEN** um episódio ativo com última tentativa falha tem resolução `blocked` referenciando bloqueio válido desse episódio
- **THEN** `--final` retorna `valid=true`, `ready=false`, `status=blocked`, `blocker_state` correspondente, nenhuma violação e exit 1; `prepare-pr` não prossegue

#### Scenario: Bloqueio de outro grupo não resolve a falha
- **WHEN** uma resolução `blocked` aponta bloqueio de outra obrigação ou episódio
- **THEN** a resolução é inválida e não libera o handoff

#### Scenario: Aprovação antiga seguida de falha
- **WHEN** `passed` referencia tentativa `pass` anterior, mas a última tentativa do episódio ativo falhou
- **THEN** a resolução é inválida e o episódio não é aprovado

#### Scenario: Episódio histórico não é aprovado pela assinatura seguinte
- **WHEN** o episódio A tem última tentativa `fail` e B é aprovado após progresso de A
- **THEN** A tem estado histórico/progredido, nunca `resolved` ou `passed`, e apenas a obrigação ativa B pode satisfazer `--final`

#### Scenario: Bloqueio antigo não aprova nem oculta falha ativa
- **WHEN** B falha após A progredir ou A volta a falhar após B
- **THEN** `--final` permanece `ready=false` até o episódio ativo passar; bloqueio válido continua não pronto

#### Scenario: Resolução por enfraquecimento
- **WHEN** um grupo é marcado resolvido por pular o teste ou enfraquecer a asserção
- **THEN** o verificador rejeita a resolução

### Requirement: Validade estrutural não é prontidão para PR
O verificador SHALL emitir `valid` para estrutura/regras e `ready` para aprovação do episódio ativo de cada obrigação. `groups` SHALL preservar episódios históricos progredidos sem os marcar aprovados. No `--final`, episódio ativo pendente, bloqueado ou replan pendente SHALL produzir `ready=false`, exit 1 e `NOT READY FOR PR`, mesmo com `valid=true`. Somente `valid=true && ready=true` SHALL retornar exit 0; entrada malformada retorna exit 2.

#### Scenario: Bloqueio estruturalmente válido sem aprovação
- **WHEN** um bloqueio bem formado mantém a obrigação não aprovada no modo `--final`
- **THEN** `valid=true`, `ready=false`, `violations=[]`, estado/razão de espera preservados e exit 1

#### Scenario: Handoff sem bloqueios nem pendências
- **WHEN** o episódio ativo de cada obrigação tem tentativa `pass` e resolução `passed`, sem violações nem replan pendente (episódios históricos progredidos podem ter última tentativa `fail`)
- **THEN** `--final` retorna `valid=true`, `ready=true` e exit 0
