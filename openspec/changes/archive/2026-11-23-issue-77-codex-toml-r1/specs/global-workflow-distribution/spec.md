# Spec Delta

## ADDED Requirements

### Requirement: Parser de configuração portátil e rastreável
A distribuição SHALL disponibilizar parser TOML completo em Python 3.10+ sem instalação de pacote no ambiente do usuário, serviço experimental ou download adicional de parser na execução. A dependência incorporada SHALL registrar versão, origem, digest e licença redistribuível, com política explícita de atualização e sem seleção silenciosa de biblioteca ambiente.

#### Scenario: Bootstrap standalone em Python 3.10
- **WHEN** a entrada pública validada roda com Python 3.10 sem tomllib ou pacote TOML de terceiros instalado
- **THEN** interpreta config com a dependência incorporada, sem pip, alteração do sistema, import de biblioteca ambiente ou obtenção de parser pela rede

#### Scenario: Pacote instalado e Python mais recente
- **WHEN** a mesma revisão roda standalone ou instalada num Python suportado mais recente
- **THEN** mantém o mesmo contrato semântico, proveniência e licença e não depende de arquivos externos omitidos do bootstrap

#### Scenario: Manutenção da dependência
- **WHEN** uma atualização futura modifica a versão ou os bytes incorporados
- **THEN** origem/digests/licença e testes de distribuição são revisados junto ao novo instalador, sem atualização automática ou substituição por uma referência móvel

### Requirement: Dependência coberta pelo pin completo do instalador
Os bytes executáveis da dependência SHALL estar integralmente autenticados pelo digest literal de instalador A em launcher posterior B e verificados antes de carregar o parser. Divergência SHALL bloquear sem importar conteúdo não verificado. MUST preservar âncoras publicadas, inventário instalado, rollback e merge commit das garantias existentes.

#### Scenario: Dependência incorporada alterada
- **WHEN** o download do instalador ou seu payload incorporado diverge do digest esperado
- **THEN** a execução da entrada adulterada ou o carregamento do parser divergente é recusado antes de publicar, preservando a instalação anterior

#### Scenario: Publicação corretiva
- **WHEN** a correção entrega nova dependência e lógica de inspeção
- **THEN** cria novos A_R1 e B_R1 com pin literal dos bytes completos, sem emendar A/B anteriores, e os testes públicos validam o mesmo parser distribuído

#### Scenario: Inventário ou arquivos gerenciados adulterados
- **WHEN** uma atualização encontra instalador ou documentação/licença gerenciada divergentes do snapshot confiável
- **THEN** bloqueia pelos guardas existentes, sem dispensar verificação de bytes, modo ou ownership por se tratar de dependência incorporada
