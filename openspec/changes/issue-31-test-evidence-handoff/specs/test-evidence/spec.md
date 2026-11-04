# Spec Delta — test-evidence

## Purpose

Registrar, transportar e verificar evidências de execução de testes vinculadas ao código exatamente testado e à matriz requisito→teste, para que outra sessão, diretório ou runtime decida sem reexecução desnecessária se a prova vale para o candidato atual.

## ADDED Requirements

### Requirement: Registro versionado de execução
O helper SHALL produzir, para cada execução registrada, um manifesto JSON com `schema` `my-ai-skills.test-evidence/v1`, `evidence_id` único, repositório, HEAD, fingerprint do código, comando (argv), seleção/filtro, diretório relativo de execução, runner/ambiente, início/fim em UTC ISO-8601, exit code, contagens, artefatos e obrigações provadas.

#### Scenario: Comando local registrado
- **WHEN** o implementador registra `python3 -m unittest discover -s tests` com obrigações `T1,T2` e seleção `tests/`
- **THEN** o manifesto contém os campos obrigatórios, o exit code original do comando, o log de saída como artefato com SHA-256 e o helper termina com o mesmo exit code do comando

#### Scenario: Relatório JUnit presente
- **WHEN** a execução declara um relatório JUnit existente
- **THEN** o relatório é copiado como artefato com checksum e as contagens (testes, falhas, erros, ignorados) são extraídas dele com a origem `junit`

#### Scenario: Relatório declarado ausente
- **WHEN** a execução declara um relatório que não existe ao término
- **THEN** o manifesto registra o artefato como `missing` e o registro não pode ser verificado como prova completa

### Requirement: Identidade do código testado
O fingerprint SHALL reutilizar `code_state`/`drift_report` de #35, incluindo o índice Git, com `exclude_paths` para saídas e `include_ignored` para configs declaradas. SHALL acrescentar hash explícito das configs. HEAD ou apenas o conteúdo do working tree MUST NOT identificar sozinho um checkout modificado.

#### Scenario: Mesmo HEAD com diff diferente (T2)
- **WHEN** um registro foi feito com o arquivo `a.py` modificado e o candidato tem o mesmo HEAD com outro conteúdo em `a.py`
- **THEN** a verificação retorna `stale` citando `a.py` como caminho divergente

#### Scenario: Working tree sujo detectado
- **WHEN** a execução é registrada com alterações não commitadas
- **THEN** o manifesto marca `dirty: true` e lista os caminhos alterados

#### Scenario: Configuração declarada alterada
- **WHEN** um arquivo de configuração declarado e ignorado pelo Git muda após o registro
- **THEN** a verificação retorna `stale` citando esse arquivo

#### Scenario: Índice alterado sem mudança de conteúdo atual
- **WHEN** o blob ou modo staged de um arquivo muda, mas HEAD, XY e bytes do working tree permanecem iguais
- **THEN** a verificação retorna `stale` citando esse arquivo, sem recalcular um segundo fingerprint canônico

### Requirement: Mudança concorrente durante a execução
O helper SHALL capturar o fingerprint antes e depois da execução, excluindo da comparação os caminhos de relatório/artefato declarados e os arquivos gerados conhecidos; se diferirem, o registro MUST ser marcado `ambiguous` e nunca verificado como prova do candidato.

#### Scenario: Arquivo alterado durante o teste
- **WHEN** um arquivo rastreado muda enquanto o comando registrado executa
- **THEN** o manifesto registra ambos os fingerprints e a verificação retorna `ambiguous`

#### Scenario: Relatório gerado dentro da árvore
- **WHEN** o comando grava o relatório JUnit declarado e bytecode dentro da árvore de trabalho
- **THEN** o registro não é marcado `ambiguous` por esses arquivos

### Requirement: Identificador emitido antes da execução
`record` SHALL gerar o `evidence_id` e emiti-lo (primeira linha em stderr, ou linha JSON) antes de executar o comando, para que o orquestrador correlacione uma execução em andamento.

#### Scenario: Execução longa observável
- **WHEN** `record` inicia um comando que ainda não terminou
- **THEN** o `evidence_id` já foi emitido e o registro local existe com estado em execução

### Requirement: Vínculo com requisito e seleção
Cada registro SHALL declarar as obrigações provadas (IDs de cenário/requisito da matriz do OpenSpec) e a seleção executada, e opcionalmente o change OpenSpec e os caminhos relevantes por obrigação, para que o revisor ligue a prova ao requisito.

#### Scenario: Revisor localiza a prova de um requisito
- **WHEN** o revisor consulta os registros pela obrigação `T3`
- **THEN** o helper lista os registros que declaram `T3`, com seleção, comando, resultado e estado de verificação

#### Scenario: Registro sem obrigação
- **WHEN** um registro é criado sem nenhuma obrigação declarada
- **THEN** o helper rejeita o registro com erro explícito

### Requirement: Armazenamento acessível entre sessões
Registros e artefatos SHALL ser armazenados fora da árvore de trabalho, em `<git-common-dir>/ai-workflow/evidence/<evidence_id>/`, de modo que qualquer worktree ou sessão do mesmo clone os encontre pelo `evidence_id`; um caminho absoluto de outro ambiente MUST NOT ser a única referência.

#### Scenario: Outra worktree verifica a prova (T1)
- **WHEN** Apply registra a prova numa worktree e prepare-pr verifica o mesmo `evidence_id` em outra worktree do mesmo clone com código idêntico
- **THEN** a verificação retorna `verified` sem reexecutar o teste

### Requirement: Pacote portátil com integridade
O helper SHALL exportar um registro como pacote único (manifesto, artefatos e checksums) e importar/verificar esse pacote em outro diretório ou runtime, rejeitando conteúdo cujo checksum diverja ou cujo caminho escape do pacote.

#### Scenario: Importação em outro runtime (T1)
- **WHEN** o pacote exportado é importado num clone diferente com o mesmo código
- **THEN** a verificação retorna `verified` e os artefatos ficam acessíveis localmente

#### Scenario: Pacote adulterado (T3)
- **WHEN** um artefato do pacote tem checksum divergente do manifesto
- **THEN** a verificação retorna `incomplete` citando o artefato e o escopo de recuperação

### Requirement: Publicação de metadados sem conteúdo sensível
A publicação SHALL enviar ao GitHub apenas o manifesto (sem logs nem relatórios) num comentário estruturado oculto, idempotente por `evidence_id`, com argv e valores mascarados para padrões de segredo; variáveis de ambiente MUST ser registradas somente por nome em lista permitida.

#### Scenario: Metadados publicados
- **WHEN** o implementador publica um registro numa issue
- **THEN** existe um único comentário com o manifesto, sem conteúdo de logs, e republicar atualiza o mesmo comentário

#### Scenario: Segredo no comando
- **WHEN** o argv contém `--token=abc123`
- **THEN** o manifesto armazenado e publicado contém o valor mascarado

### Requirement: Estados de verificação
A verificação SHALL retornar exatamente um estado por registro — `verified`, `metadata_only`, `incomplete`, `stale`, `ambiguous` ou `not_applicable` — com resultado (`passed`/`failed`), motivos concretos e escopo de recuperação, em saída humana e JSON.

#### Scenario: Prova completa e correspondente
- **WHEN** manifesto válido, artefatos presentes com checksum correto e fingerprint igual ao candidato
- **THEN** o estado é `verified`

#### Scenario: Metadados sem log
- **WHEN** apenas o manifesto publicado está disponível e os artefatos não estão acessíveis
- **THEN** o estado é `metadata_only` e a prova não é contada como verificada

### Requirement: Prova incompleta ou inacessível permanece não verificada
Registros com campos obrigatórios ausentes, exit code desconhecido, execução interrompida, artefato ausente ou checksum divergente SHALL resultar em `incomplete` ou `metadata_only` e MUST NOT ser apresentados como aprovação.

#### Scenario: Log ausente (T3)
- **WHEN** o log de saída do registro foi removido
- **THEN** o estado é `incomplete` com o artefato faltante e a obrigação a recuperar

#### Scenario: Execução interrompida
- **WHEN** o comando registrado é interrompido antes de terminar
- **THEN** o manifesto registra a interrupção e o estado é `incomplete`

### Requirement: Invalidação com motivo concreto e escopo por obrigação
Quando o fingerprint diverge, a verificação SHALL listar os caminhos alterados (inclusive alteração de índice) e, por obrigação, marcar `affected` se algum caminho cruzar os caminhos relevantes declarados (ou se nenhum foi declarado) e `unaffected` caso contrário, indicando qual obrigação precisa nova execução. O registro divergente permanece `stale` mesmo se uma obrigação for `unaffected`; essa classificação não equivale a `verified` nem substitui os gates finais.

#### Scenario: Alteração afeta apenas uma obrigação (T4)
- **WHEN** dois registros declaram caminhos relevantes distintos e o candidato altera apenas um deles
- **THEN** só a obrigação afetada recebe `stale/affected` e a outra recebe `unaffected` com a justificativa dos caminhos

#### Scenario: Sem caminhos relevantes declarados
- **WHEN** o registro não declara caminhos relevantes e qualquer caminho muda
- **THEN** todas as suas obrigações são `affected`

### Requirement: Precedência dos gates do repositório
Gates obrigatórios SHALL ser tipados `local` ou `hosted`. Gate `local` exige registro local `verified` e `passed` com fingerprint idêntico ao candidato final. Gate `hosted` exige registro hospedado `verified` e `passed`, confirmação do resultado/HEAD pela origem e candidato limpo no SHA exato. Metadados hospedados autodeclarados MUST NOT aprovar gate; resultado hospedado nunca satisfaz gate local, nem `unaffected` equivale a aprovação.

#### Scenario: CI antigo para gate local (AC5)
- **WHEN** existe apenas um resultado hospedado aprovado e a obrigação é um gate `local` obrigatório
- **THEN** a verificação retorna `not_applicable` para essa obrigação e ela permanece pendente

#### Scenario: CI do candidato exato para gate hospedado
- **WHEN** a obrigação é um gate `hosted` e existe registro hospedado aprovado com URL/run_id/head/status confirmados na origem confiável, com `head` igual ao SHA do candidato limpo
- **THEN** a verificação retorna `verified` para essa obrigação

#### Scenario: Resultado hospedado não confirmável
- **WHEN** apenas metadados de um resultado hospedado estão disponíveis e sua origem/status não podem ser conferidos
- **THEN** o estado permanece `metadata_only` e o gate `hosted` continua pendente

#### Scenario: CI de outro SHA para gate hospedado
- **WHEN** a obrigação é um gate `hosted` e o registro hospedado tem `head` diferente do candidato
- **THEN** a verificação retorna `stale` e a obrigação permanece pendente

#### Scenario: Gate obrigatório após mudança fora do escopo
- **WHEN** um gate obrigatório foi registrado e o candidato altera um caminho fora dos caminhos relevantes declarados
- **THEN** a obrigação continua exigindo nova execução

### Requirement: Retenção explícita
Registros locais SHALL ser mantidos até remoção explícita (`prune` por idade ou por `evidence_id`, com simulação por padrão) ou encerramento verificado do checkout; o helper MUST NOT apagar registros automaticamente durante registro ou verificação.

#### Scenario: Prune simulado
- **WHEN** `prune --older-than 30` é executado sem confirmação
- **THEN** o helper lista o que removeria e não remove nada

### Requirement: Independência de produtor
O registro SHALL suportar qualquer comando de teste pelo mesmo conceito, sem exigir Magento ou M2T. O bloco `producer` é provisório e MUST ser null ou ausente e não validado nesta versão; campos e `extensions` desconhecidos MUST ser preservados na leitura e reescrita.

#### Scenario: Comando não M2T
- **WHEN** um projeto sem M2T registra `npm test`
- **THEN** o registro e a verificação funcionam sem nenhum campo de produtor

#### Scenario: Extensão desconhecida preservada
- **WHEN** um manifesto contém `extensions.example_tool` criado por outra versão
- **THEN** a leitura aceita o manifesto e a exportação o preserva intacto

### Requirement: Handoff de prova no workflow
Apply SHALL encerrar com os `evidence_id` das obrigações na matriz e no handoff; prepare-pr e as auditorias SHALL verificar esses registros contra o candidato, relatar o estado por obrigação e reexecutar somente o que estiver `stale/affected`, `incomplete`, `ambiguous` ou `not_applicable`.

#### Scenario: prepare-pr com prova reaproveitável
- **WHEN** todas as obrigações do handoff estão `verified` para o candidato
- **THEN** prepare-pr reaproveita a prova sem reexecução e a seção Validation do PR traz uma linha por obrigação no formato `PASS|FAIL|NOT RUN: <obrigação> — evidence:<id> (<estado>)`

#### Scenario: prepare-pr com prova inacessível
- **WHEN** um registro do handoff não é encontrado nem importável
- **THEN** a obrigação aparece como não verificada com o escopo de recuperação, e não como aprovada
