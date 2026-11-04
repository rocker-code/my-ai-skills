# Spec Delta

## Purpose

Oferecer um helper opcional, determinístico e somente leitura que antecipa duas pré-condições do pré-flight — aderência das dependências instaladas ao lockfile e mudança de política desde o commit do plano — com saída legível e máquina-legível.

## ADDED Requirements

### Requirement: Contrato comum de execução

O helper SHALL ser somente leitura, sem acesso à rede e sem credenciais, e SHALL usar apenas a biblioteca padrão do Python e o `git` local. Ele MUST retornar código 0 quando nenhuma divergência for encontrada, 1 quando houver divergência ou pré-condição reprovada, e 2 para uso inválido, entrada ilegível ou ecossistema não suportado. Ele MUST aceitar `--root <dir>` (padrão: diretório atual) e `--format text|json`; a saída JSON MUST conter `check`, `status` e a lista de achados.

#### Scenario: Uso inválido
- **WHEN** o helper é chamado sem subcomando ou com argumento desconhecido
- **THEN** ele imprime o uso em stderr e retorna 2 sem ler ou alterar arquivos

### Requirement: Verificação lockfile versus instalado

O subcomando `lock` SHALL detectar no root os lockfiles suportados — Composer (`composer.lock` contra `vendor/composer/installed.json`) e npm (`package-lock.json` contra `node_modules/.package-lock.json`) — e comparar nome e versão de cada pacote. Ele MUST reportar, por pacote, versão do lock e versão instalada para divergências, pacotes do lock ausentes na instalação e manifesto de instalação inexistente. Ele MUST retornar 2 quando nenhum lockfile suportado existir.

#### Scenario: Versão instalada diverge do lock (T3)
- **WHEN** `composer.lock` fixa `phpmd/phpmd` em `3.x-dev` e `vendor/composer/installed.json` registra `2.15.0`
- **THEN** o helper retorna 1 e o achado indica `phpmd/phpmd`, versão do lock `3.x-dev` e versão instalada `2.15.0`

#### Scenario: Instalação aderente
- **WHEN** todos os pacotes do lock estão instalados com a mesma versão
- **THEN** o helper retorna 0 com status `ok`

#### Scenario: Dependências não instaladas
- **WHEN** existe lockfile mas o manifesto de instalação correspondente não existe
- **THEN** o helper retorna 1 com achado `not-installed` para esse ecossistema

#### Scenario: Ecossistema não suportado
- **WHEN** o root não contém nenhum lockfile suportado
- **THEN** o helper retorna 2 com status `unsupported`, indicando que a verificação deve ser feita manualmente pelo procedimento

### Requirement: Verificação de política desde o commit do plano

O subcomando `policy --since <commit>` SHALL listar os arquivos de política alterados, adicionados ou removidos entre o commit informado e o estado atual do checkout (incluindo mudanças não commitadas e arquivos não rastreados). O conjunto padrão MUST incluir `AGENTS.md`, `CLAUDE.md`, `.github/workflows/`, `openspec/config.yaml` e `.ai-workflow/protocol/`; `--path <p>` repetível MUST acrescentar caminhos. Commit inexistente MUST retornar 2.

#### Scenario: Política alterada entre plano e Apply (T2)
- **WHEN** um arquivo de política padrão foi modificado depois do commit do plano
- **THEN** o helper retorna 1 e lista o caminho alterado com o tipo de mudança

#### Scenario: Política inalterada
- **WHEN** nenhum caminho de política mudou desde o commit do plano
- **THEN** o helper retorna 0 com status `ok`

#### Scenario: Commit desconhecido
- **WHEN** `--since` aponta para uma revisão inexistente
- **THEN** o helper retorna 2 sem reportar política como inalterada

### Requirement: Opcionalidade e distribuição

O procedimento de pré-flight MUST permanecer executável sem o helper; a ausência do helper MUST ser tratada como verificação manual, não como aprovação. O helper SHALL ser distribuído pelo pacote do plugin junto dos demais helpers e documentado nos READMEs em paridade.

#### Scenario: Helper indisponível
- **WHEN** o consumidor não instalou o helper
- **THEN** o agente executa as verificações equivalentes manualmente e registra o método usado
