# workflow-metrics Specification

## Purpose
Manter o registro estruturado de execuções do workflow por issue (comentário oculto no GitHub) e sua leitura por relatórios, preservando compatibilidade com registros anteriores.

## Requirements

### Requirement: Referências de evidência no registro de run
`workflow-event --evidence` SHALL aceitar URL do GitHub, SHA de commit ou referência `evidence:<evidence_id>` e MUST rejeitar outros valores; o registro de run permanece com `schema_version: 1` e `evidence` como lista de strings.

#### Scenario: Referência de evidência aceita
- **WHEN** um evento é registrado com `--evidence evidence:ev-20261104T030000Z-1a2b3c4d`
- **THEN** a referência é gravada no evento e em `record.evidence` como string

#### Scenario: Valor inválido rejeitado
- **WHEN** um evento é registrado com `--evidence /tmp/run.log`
- **THEN** o comando falha sem alterar o comentário

### Requirement: Leitura retrocompatível de registros anteriores
O parser e os relatórios SHALL ler registros `schema_version: 1` gravados antes desta mudança, com `evidence` contendo apenas URLs/SHAs ou ausente, produzindo os mesmos resumos de antes.

#### Scenario: Registro antigo (T5)
- **WHEN** `workflow-report` lê um comentário de run anterior sem referências `evidence:`
- **THEN** o relatório é gerado com as mesmas métricas e evidências de antes

#### Scenario: Registro misto
- **WHEN** um registro contém URLs, SHAs e referências `evidence:`
- **THEN** o relatório lista todas as referências sem erro
