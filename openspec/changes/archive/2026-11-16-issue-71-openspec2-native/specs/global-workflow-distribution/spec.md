# Spec Delta

## MODIFIED Requirements

### Requirement: Primeiro uso de OpenSpec por projeto
A instalação SHALL disponibilizar o CLI OpenSpec quando suportado; no primeiro uso autorizado pelo agente a integração oficial OpenSpec 2.0 para o perfil selecionado SHALL disponibilizar suas skills nativas. Preparação local MUST NOT ocorrer na instalação global e MUST preservar configurações, artefatos e integrações existentes. A prova MUST verificar descoberta e invocação real no agente em sessão nova, sem exigir comandos legados ausentes.

#### Scenario: Repositório ainda sem OpenSpec
- **WHEN** o agente inicia fluxo que precisa de OpenSpec em repositório sem raiz configurada
- **THEN** verifica raiz pretendida, `context/list`, perfil e resíduos locais e globais; obtém autorização específica antes de inicializar pela interface oficial do perfil, confirma skills oficiais e preserva arquivos anteriores ou bloqueia sem escrita quando a preservação não puder ser demonstrada

#### Scenario: Repositório com OpenSpec existente
- **WHEN** o agente inicia o fluxo em repositório já configurado
- **THEN** reutiliza a integração se completa; caso contrário inventaria config, specs, changes, instruções e integrações de todas as ferramentas configuradas e efeitos globais, inspeciona dry-run/diferenças antes de pedir autorização específica para update ou inclusão de ferramenta, preservando a união das ferramentas existentes, sem `--force` nem limpeza implícita

#### Scenario: OpenCode recém-aberto após primeiro uso autorizado
- **WHEN** o agente prepara OpenSpec com autorização em projeto novo ou existente e uma sessão OpenCode nova é aberta no projeto
- **THEN** skills oficiais Explore, Propose, Apply e Archive da interface nativa do perfil ativo são descobertas e invocáveis, ou um bloqueio específico é reportado sem alegar integração completa; a ausência de comandos `/opsx-*` que a 2.0 não gera não constitui falha

#### Scenario: Resíduos gerados e personalizações
- **WHEN** uma migração encontra comandos/skills antigos, links, instruções customizadas ou conteúdo modificado em caminhos potencialmente gerados
- **THEN** identifica propriedade e alterações antes de substituir ou remover; somente gerados comprovados entram na limpeza aprovada, personalizações sobrevivem, e conflitos impedem publicação insegura sem inutilizar a versão anterior

#### Scenario: Prova não conclusiva
- **WHEN** a sessão nova não descobre ou não consegue invocar uma das skills oficiais requeridas
- **THEN** o fluxo informa o bloqueio preciso e não libera proposta, Apply ou instalação como integração comprovada
