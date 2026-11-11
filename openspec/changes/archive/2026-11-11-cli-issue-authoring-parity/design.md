# Design

## Context

Ver proposal.md. Revisão inspecionada: ebb58afb6b07ac17a39ad9aa89d17b15eed0c34e. create-issue não existe; refine-issue é genérica; o protocolo detalhado é Web. O instalador global enumera skills com SKILL.md, sem lista fixa.

## Goals / Non-Goals

Encaminhar criação/refinamento CLI à fonte de qualidade existente. Não alterar o Web, migrar instalações, modificar #451/#445 nem executar features das issues produzidas.

## Decisions

Adicionar create-issue exclusiva do CLI para descoberta por pedidos naturais. Em refine-issue, adicionar apenas encaminhamento condicional CLI, preservando seu caminho Web.

Reutilizar CHATGPT_WEB_ISSUES.md sem editar seu texto. As entradas CLI explicitam que aplicam suas regras de autoria/template e que o rótulo Web não proíbe este uso; não invocam chatgpt-web-* nem assumem conector Web. Isso evita duplicar e deixar dois templates divergirem. Referências são geradas com o mecanismo existente.

## Risks / Trade-offs

- Texto do protocolo menciona Web → entrada CLI esclarece explicitamente a adaptação de runtime e a manutenção das barreiras de execução.
- Descoberta varia por agente → descrição explícita com pedidos naturais; sem promessa de execução real em OpenCode não disponível neste ambiente.

## Migration Plan

Após merge, atualização explícita do pacote e nova sessão do agente tornam a entrada disponível. Nenhuma atualização do computador do usuário ocorre nesta PR. Reverter os arquivos restaura o comportamento anterior.

## Verification

Plano validado estritamente na revisão 187cc7d antes da implementação; revisão local sem nova decisão de arquitetura.

| Requisito | Implementação | Evidência |
| --- | --- | --- |
| Autoria e refinamento CLI | create-issue e bloco CLI de refine-issue | Avaliação independente com pedido de migração gerou resumo, evidências/limitações, comportamento, Mermaid, critérios, tabela com camada e não objetivos; nada publicado |
| Preservação Web e execução | Encaminhamento restrito ao CLI e limite de backlog | Diff vazio contra ebb58af para skills Web e protocolos Web/visual; inspeção dos limites de execução |
| Referências portáveis | sync-skill-references e entradas no teste existente | 3 testes de distribuição passaram, incluindo igualdade com fontes e idempotência; links das entradas resolvidos |
| Distribuição global | Descoberta automática existente | 26 testes de instalação: 24 passaram, 2 pulados; 7 testes do launcher passaram |

A suíte global inicialmente teve duas falhas porque herdou XDG_STATE_HOME do ambiente, enquanto suas fixtures usam ~/.agents. Reexecução com `env -u XDG_STATE_HOME` passou; não houve alteração de produto/teste para esconder o problema. Não foi executada sessão OpenCode real nem migração local do usuário. Na avaliação foi identificado link para revisão apenas local; a entrada agora exige verificar presença remota antes de usar links de commit.
