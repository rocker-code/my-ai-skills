# Spec Delta

## ADDED Requirements

### Requirement: Inspeção semântica da configuração de skills Codex
A inspeção SHALL interpretar o documento TOML completo antes de diagnosticar regras de skills canônicas. Grafias válidas equivalentes SHALL produzir o mesmo resultado. MUST NOT usar regex ou texto em comentários/strings como substituto da estrutura TOML nem alterar a configuração para contornar uma desabilitação.

#### Scenario: Quatro grafias da mesma regra
- **WHEN** uma regra canônica `enabled = false` usa array de tabelas literal, indentado, chave pontuada com espaços ou array inline de tabelas
- **THEN** todas são reconhecidas como regras e bloqueiam publicação com diagnóstico acionável e preservação dos bytes/modo de config

#### Scenario: Seletores e conteúdo não relacionado
- **WHEN** uma configuração contém seletor por nome ou path, aspas/chaves quoted e escapes TOML válidos
- **THEN** a inspeção usa os valores decodificados e aplica o mesmo critério de seleção, sem depender da grafia das chaves ou strings

#### Scenario: Controle sem desabilitação canônica
- **WHEN** config está ausente ou válido e não contém regra que desabilita skill canônica, inclusive comentário/string com texto semelhante ou skill não relacionada desabilitada
- **THEN** a inspeção não cria falso conflito por reconhecimento textual e os demais guardas da instalação continuam aplicáveis

### Requirement: Erro de configuração bloqueia sem perda ou vazamento
TOML malformado, UTF-8 inválido, erro de leitura ou estrutura/tipos inválidos em `skills.config` SHALL bloquear a ação afetada antes de publicar. O diagnóstico SHALL identificar caminho e causa delimitada sem conteúdo/segredos. MUST preservar configuração, credenciais e instalação anterior, sem reparo automático ou sucesso por ignorar falha.

#### Scenario: Documento ou regra inválida
- **WHEN** há chave duplicada, sintaxe incompleta, UTF-8 inválido, estrutura relevante incompatível ou `enabled` com tipo não booleano
- **THEN** a tentativa falha explicitamente e não considera a inspeção aprovada

#### Scenario: Falha em instalação com ambos agentes
- **WHEN** a inspeção Codex falha durante instalação ou atualização com ambos selecionados
- **THEN** active, seleção/ownership, links, orientações e launcher anteriores permanecem íntegros nos mesmos termos da transação multiagente

#### Scenario: Dados sensíveis no documento
- **WHEN** o documento inválido inclui segredos, hooks ou comandos
- **THEN** nenhuma dessas informações é executada ou reproduzida no diagnóstico e os bytes/modo do arquivo permanecem iguais
