# Design

## Context

Motivação e limites: `proposal.md`. Contratos: deltas de distribuição, atualização e entrega nesta change.

Inspeção em `58c9b67ee4148748f83539b457d6ddf49fedb4a4`:

| Fronteira | Evidência atual | Consequência |
|---|---|---|
| `scripts/install-global:preflight` | aceita somente OpenCode e exige `api/run/service` V2 | separar dependências comuns das capacidades por agente |
| Manifesto e `install()` | schema 1 mistura seleção e inventário por SHA; caminhos, guidance e obsoletos fixos OpenCode | adicionar Codex não pode regravar manifesto imutável da mesma revisão |
| Ownership/migração | `guidance.json`, `launcher.json`, baseline Git confiável, links exatos, lock, backups/rollback | ampliar essas fronteiras, não substituir por instalador permissivo |
| Launchers/update skill | `--agent opencode` fixo e pós-check no diretório OpenCode | encaminhar seleção e verificar cada integração efetiva |
| Protocolos/entrypoints | já neutros; uma issue ativa, fresh Apply e revisão independente reais | explicitar somente mecânica nativa, sem novo scheduler |
| `tests/test_global_install.py` | fixture temporária, transporte Git local injetado internamente, fake OpenCode/OpenSpec; alguns testes OpenSpec real | ampliar fixture e manter injeção inacessível na entrada pública |
| `tests/test_install_launcher.py` | valida SHA/digest literais e igualdade dos bytes do instalador A | atualizar depois de A; preservar teste negativo de adulteração |
| `tests/smoke_global_opencode.py` | API real, dois projetos/worktree, quatro skills e HOME isolado | incluir Verify e tratar `--scope project` no CLI 2.1 quando disponível |
| Ambiente | Codex `/home/beto/.local/bin/codex` 0.171.0; `login status` autenticado via ChatGPT; OpenSpec 2.1.1 | autenticação observada não prova credencial em HOME descartável ou execução de modelo |
| Perfil | `openspec config list --json`: core; skill oficial Verify já existe neste checkout | ausência no perfil padrão não significa indisponibilidade; smoke precisa habilitação oficial isolada |

`codex --help`, `exec --help`, `resume --help` confirmam execução não interativa, `--json`, `--cd`, `--ephemeral`, sandbox, revisão e resume próprios. `features list` local mostra `multi_agent` deprecated habilitado e `multi_agent_v2` stable desabilitado: help/flag NÃO prova delegação efetiva ou independência. Não houve execução de modelo, descoberta nativa Codex ou smoke nesta fase.

Fontes oficiais consultadas em 23/11/2026:
- [Skills Codex](https://developers.openai.com/codex/skills): `$HOME/.agents/skills`, links suportados, invocação `$skill`; nomes duplicados não são mesclados.
- [AGENTS.md Codex](https://developers.openai.com/codex/guides/agents-md): `${CODEX_HOME:-$HOME/.codex}`, `AGENTS.override.md` precede `AGENTS.md`; regras locais mais próximas prevalecem.
- [Config Codex](https://developers.openai.com/codex/config-basic): CLI > projeto confiável > profile > usuário > defaults gerenciados/sistema; não alterar modelo, sandbox, trust, hooks ou permissões.
- [Setup OpenSpec](https://openspec.dev/docs/setup) e [profiles](https://openspec.dev/docs/profiles): Codex suportado, Verify opcional oficial; 2.1 usa skills globais por padrão e `--scope project` para fixtures locais.

Dependências efetivas: #75 via merge `abf0dbd2370a59169e2a19f314b12efdc9a1b11c` ancestral da base; #76 entregue na base; #52 entregue. #61 e #78 não são pré-requisitos nem alvos. Não há workflow CI versionado; descoberta anterior não encontrou proteção/check hospedado obrigatório. Revalidar regras vivas antes de merge; não inventar CI nem substituir suite local.

## Goals / Non-Goals

**Goals:** preservar as garantias de instalação com dois consumidores nativos; separar seleção operacional do snapshot imutável; manter uma única política e comprovar o runtime real sem requerer o outro CLI.

**Non-Goals:** framework de adapters executáveis, dispatcher, novo armazenamento de execução, uninstall novo, portabilidade de sessão, instalação/atualização no HOME real, mudanças M2T/aplicações ou trabalho nas #61/#78.

## Decisions

### D1 — Seleção explícita, preservada e aditiva

Manter `--agent` repetível com valores `opencode|codex` no instalador e aceitar os mesmos argumentos nos launchers. Instalação inicial sem seleção bloqueia com exemplos. Update sem flags resolve a seleção anterior somente após validar pacote/ownership. Uma seleção explícita posterior adiciona agentes à seleção anterior; não representa remoção. Omitir Codex numa instalação dupla não o remove, e a atualização verifica os dois runtimes efetivamente mantidos.

Alternativas rejeitadas: autodetectar PATH muda comportamento por acaso; default OpenCode impede Codex-only; interpretar subconjunto como desinstalação cria remoção não solicitada. Não adicionar comando de remoção nesta issue. Atualização preservada que encontra runtime selecionado ausente bloqueia com ação concreta, sem degradar silenciosamente.

### D2 — Snapshot imutável neutro, ownership existente evoluído

Evoluir manifesto do pacote para schema 2 com inventário/diretórios/modos/origem/revisão e integrações disponíveis determinísticas de ambos os agentes, independentemente da seleção atual. Nomear explicitamente essa disponibilidade, sem apresentar ambos como instalados. Não gravar seleção mutável em `versions/<SHA>/manifest.json`.

Evoluir **o existente** `guidance.json` para schema 2 contendo seleção instalada e, por agente, caminhos efetivos e hashes de blocos gerenciados. Reusar `launcher.json` e `.install.lock`. Não criar banco, registry de agentes ou serviço novo. Os links de ambos apontam para `active/skills/<nome>`.

Validar schema 1 antigo por reprodução do formato/algoritmo legado a partir do snapshot Git confiável, incluindo `directories` opcional, não por executar código baixado nem aceitar manifesto autoafirmado. Validar bloco antigo contra baseline e ownership antes de migrar `guidance.json`. Schema 2 tem reconstrução determinística própria. Não reescrever versões antigas. Adicionar segundo agente na mesma revisão muda só integração/ownership: manifesto schema 1 existente e comprovado também pode ser reutilizado sem promoção em disco, interpretando sua seleção histórica como legado e a seleção efetiva pelo ownership novo. Novos snapshots usam schema 2. Testar ambos os casos para não transformar expansão em conflito artificial de manifesto.

### D3 — Integrações pequenas por caminhos nativos

Uma tabela pequena interna ao instalador descreve somente paths, preflight e orientação:

| Agente | Skills globais | Instrução global |
|---|---|---|
| OpenCode | `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills` | mesmo root `/AGENTS.md` |
| Codex | `$HOME/.agents/skills` (não presumir relocação por CODEX_HOME) | `${CODEX_HOME:-$HOME/.codex}/AGENTS.md` |

Registrar caminhos efetivos; mudança posterior de CODEX_HOME/XDG que deslocaria uma integração existente bloqueia e pede reconciliação delimitada, sem abandonar destinos anteriores. Recusar symlinks ancestrais inseguros e caminhos de outra origem, inclusive roots customizados fora de HOME. Codex `AGENTS.override.md` não vazio que sombreia a orientação gera diagnóstico/bloqueio de prova de carregamento; nunca modificá-lo silenciosamente. `config.toml`, auth e hooks ficam intocados. Skills desabilitadas/duplicadas exigem diagnóstico; não ativar por edição automática de configuração.

Reusar orientação canônica de reserva, recuperação e OpenSpec. Variar apenas nome do runtime/invocação e caminhos; não copiar protocolos inteiros por agente. Atualizar orientação de primeiro uso para as cinco skills e seleção de ferramentas correta.

### D4 — Uma transação para a seleção efetiva inteira

Sob lock comum: obter/validar origem, seleção anterior, manifesto, blocos, links/obsoletos, launcher e todos os novos destinos antes de qualquer publicação. Preflight comum verifica Git/Python/gh/jq/curl e OpenSpec conforme contrato atual; OpenCode verifica V2 e suas capacidades atuais, Codex verifica versão/ajuda e operações necessárias sem exigir API OpenCode. Estado de autenticação e capacidade de executar modelo são fatos separados; não iniciar login, alterar config ou alegar smoke aprovado no instalador.

Preparar pacote, links e textos com recibos em memória para rollback; escrever seleção/ownership coerentes e trocar `active` por último. Reverificar destinos antes de substituição. Reverter somente bytes/links comprovadamente escritos por esta transação, em ordem inversa, cobrindo os dois agentes e o launcher. Reusar recusas EXDEV e backup pré-existente. Falha abrupta com estado intermediário inconsistente bloqueia a próxima tentativa e preserva versões para diagnóstico; não introduzir journal de recuperação automática nem apagar desconhecidos.

### D5 — Runtime nativo, não abstração de execução

Ampliar seção curta em `protocol/AI_WORKFLOW.md` e, se necessário, instruções de identidade em `WORKTREES.md`; entrypoints existentes referenciam essa política, sem ciclo próprio.

- OpenCode usa somente ferramentas/sessões realmente disponíveis no host.
- Codex usa comandos/skills nativos. Um processo novo `codex exec --json --cd <checkout>` sem `resume`, `fork` ou transcrição herdada é candidato a contexto novo; confirmar ID nativo e conteúdo efetivo no smoke antes de declarar suporte. Revisão usa sessão distinta, entrada imutável e escopo somente leitura; não tratar o simples subcomando `review` como auditoria completa da política.
- Correlacionar ID real da sessão/thread retornado pelo runtime, issue e SHA. Não inventar variável de ambiente de identidade, ID derivado de PID, ou reutilizar ID do owner; se o ID não estiver acessível ao worker, o runtime deve fornecê-lo explicitamente com origem verificável. O helper existente aceita strings seguras e não precisa conhecer um produto específico.
- Em Codex, capacidades de subagentes e callbacks precisam ser testadas; flags/documentação são evidência de disponibilidade potencial. Sem suporte comprovado, usar sessões nativas distintas verificáveis; se ainda insuficiente, bloquear somente ação afetada com próximo passo Codex, sem impor OpenCode.
- Troca de agente retoma dados duráveis e reserva reconciliada, não chat ou processo vivo. Sem prova de parada anterior, sem transferência. Sem término confiável de teste/worker, resultado desconhecido.

### D6 — Smokes reais separados de testes determinísticos

Ampliar fixtures existentes em `test_global_install.py` e `test_install_launcher.py`: seleção controlada e PATH restrito, sem vazar o outro CLI do PATH real; CODEX_HOME e todos XDG temporários. Manter o transporte Git local como injeção **interna de teste**; não adicionar `--source` público.

Adicionar `tests/smoke_global_codex.py` usando CLI real e instalação local isolada; não imitar API OpenCode. Sua prova deve ter duas partes distintas:
1. Descoberta/invocação nativas em dois repositórios + worktree com espaços, usando skills globais reais do pacote e as cinco skills oficiais geradas pelo OpenSpec. Confirmar caminhos, sessão, carregamento/invocação e término; não passar o corpo da skill no prompt como substituto da descoberta.
2. Fluxo controlado sobre tarefa/issue fixture: Explore/Propose, Apply em execução nova após transferência, testes, Verify e Archive reais em projeto descartável mínimo. Fixture GitHub de duas issues/PRs captura comandos `gh` e simula somente backend/backlog, não Codex; prova ordenação, ausência de duplicatas/comentários operacionais, leitura de progresso e não criação de evolução trivial/já rastreada. Não criar/mergear issues reais nem alterar #77 pelo smoke. Casos de retomada e capability-gap usam artefatos reais de reserva e execuções distintas, não apenas busca textual de instruções.

Identificar em resultados quais obrigações têm execução real e quais usam backend fixture. Smoke de invocação sozinho não aprova lifecycle completo, independência, sequência ou recuperação.

Proteger auth: não ler/registrar segredos em argumentos/logs; HOME/CODEX_HOME/XDG descartáveis e auth preparada por mecanismo suportado/explicitamente autorizado. Não copiar configurações do usuário nem escrever no HOME real. Se a autenticação isolada não estiver disponível, registrar bloqueio acionável, sem transformar skip em pass.

OpenSpec: selecionar `--scope project` quando o help o suporta; usar perfil oficial com união das escolhas existentes + Verify em configuração isolada. Não editar global config real nem handcraft de skill. Smokes mantêm resultados privados em `/tmp/opencode`, versão/seleção/SHA/caminhos/IDs e códigos de saída, sem telemetria de workflow.

### D7 — Publicação em A/B e merge commit obrigatório

Implementação cria commit **A** contendo novo instalador e dependências/testes pertinentes antes de alterar o pin. Depois cria **B** com `entry_revision=<SHA completo de A>` e SHA-256 literal de `git show A:scripts/install-global`, mais launchers/docs/testes que publicam a interface. Se o instalador mudar depois, criar novo A e novo B; nunca emendar objeto pinado já usado como âncora.

Os testes devem provar `A` ancestral de `B`, bytes iguais ao digest literal, download adulterado recusado, seleção encaminhada e comandos públicos em HOME/PATH descartáveis. Não resolver pin em runtime nem usar hash de B. Após archive/distribuição/docs, executar suite local final no HEAD limpo exato; qualquer commit posterior exige nova prova.

PR desta issue requer **merge commit**, não squash/rebase, mantendo A alcançável em main. Se a política viva impedir merge commit, bloquear entrega para decisão; não trocar silenciosamente método nem declarar distribuição publicada. Depois do merge confirmar ancestralidade e disponibilidade pública de A/B antes de afirmar conclusão. Não atualizar a instalação global real como parte da entrega.

## Risks / Trade-offs

- [Posse inferida de manifesto/ID] → reproduzir baseline Git e blocos; validar identidade nativa, paths e links; não confiar em autoafirmação ou owner anterior.
- [Estado mutável dentro de versão por SHA] → schema 2 neutro + evolução do ownership existente; teste de expansão na mesma revisão.
- [Falha no segundo agente inutiliza o primeiro] → preflight completo, transação conjunta, injeções nas fronteiras atuais, rollback de somente efeitos próprios.
- [Skills universais Codex colidem com skills.sh/OpenSpec] → comparar nome/origem/bytes sem assumir propriedade; escopos claros; migração específica com backup.
- [OpenSpec 2.1 move skills para HOME] → `--scope project` em fixtures e inventário dos efeitos globais antes de bootstrap; preservar 2.0 sem flag inexistente.
- [Smoke real precisa modelo/autenticação] → preflight isolado e resultado NOT RUN/BLOCKED honesto; nunca substituir por fake ou alegar suporte concluído.
- [Config/override impede orientação] → informar fonte efetiva e preservar arquivos; prova nativa verifica carregamento em sessão nova.
- [Merge squash perde A] → método explícito e verificação de ancestralidade antes/depois de publicação.
- [Docs wiki em outro repo] → README pt/en e guias versionados são alterados aqui; link de wiki deve ser consistente ou apontar ao guia correto, sem publicar fora do escopo.

## Migration Plan

1. Manter instalação real intocada; implementar e testar em HOME/PATH descartáveis.
2. Reconhecer baseline schema 1 e migrar seleção OpenCode comprovada para ownership novo somente em transação validada; conservar versões anteriores.
3. Instalação nova escolhe agente; update reutiliza seleção íntegra; expansão explícita adiciona segundo agente sem remoção implícita.
4. Atualizar docs/guia de uso, referências geradas e changelog; executar ambas interfaces públicas pinadas e smokes separados.
5. Aplicar Verify oficial, strict validate e Archive nesta branch; revisar sync/archive e executar gates no candidato final.
6. Fazer merge commit apenas após revisão independente/guardas atuais; verificar A alcançável e fluxos publicados. Em falha reter checkout/provas; rollback de instalação nunca apaga versão ou conteúdo desconhecido.

## Requirement → Test Risk Matrix

Todas as provas de implementação abaixo estão **PENDING / NOT RUN** no planejamento. Os nomes de testes novos são intenções, não resultados existentes.

| ID | Aceite/risco e consumidor real | Camada e plano | Prova suficiente / estado |
|---|---|---|---|
| T1 | Codex-only; preflight/paths/pós-check não dependem de OpenCode | ampliar `test_global_install.py`/launcher com PATH restrito, install+update Codex-only | comandos públicos + smoke Codex nativo; pendente |
| T2 | regressão OpenCode-only e baseline legado | testes existentes de instalação, update, integridade e first-use, sem Codex no PATH | grupos existentes ampliados + smoke OpenCode com Verify; pendente |
| T3 | ambos mesma fonte; expansão mesma revisão; manifesto imutável | integração de links/manifesto/ownership schema 1→2, adição de agente, update subconjunto preserva união | igualdade de destino/SHA e bytes antes/depois, ambos smokes; pendente |
| T4 | cinco skills e lifecycle oficial; novo/existente/multitool; 2.0/2.1 scope | first-use existente ampliado; `smoke_global_codex.py` novo e OpenCode existente | carregamento nativo e lifecycle fixture com IDs/artefatos/testes/Verify/archive reais; pendente |
| T5 | uma issue ativa por milestone em ambos runtimes | teste de contrato compartilhado + fixture nativa Codex com duas issues | segunda não inicia antes de entrega/park da primeira; subagentes só mesma issue; pendente |
| T6 | retomada cross-agent, single writer, não duplicar change/PR | ampliar testes de reserva/recuperação existentes e fixture smoke de interrupção | parada real/ID, transferência, mesmo checkout/change/PR e obrigação incompleta não aprovada; pendente |
| T7 | capacidades/ID/credencial não comprovados | negativos preflight/exec/review/discovery com falha/sem término ou ID errado | ação afetada bloqueada, sem fallback OpenCode ou independência fabricada; pendente |
| T8 | config/ownership/rollback: `install-global`, `guidance.json`, launcher | reusar testes de adulteração, EXDEV, symlink, migração autorizada, quatro failpoints; adicionar ambos/CODEX_HOME/override/disabled skill | bytes/modos/config/seleção/active anteriores preservados; colisão em um impede ambos; pendente |
| T9 | status somente leitura, sem analytics | fixture gh + invocação nativa dos entrypoints de status em ambos agentes | fatos vivos/capturados e próximo passo, zero escrita ou coluna de tempos; pendente |
| T10 | workers/PR não geram comentários nem novo log de eventos | testes distribuição existentes + smoke Codex com captura `gh` | ausência de issue/PR comment/evento oculto nas transições; revisão acionável não é proibida; pendente |
| T11 | melhoria cosmética/duplicada não vira issue | fixture backlog e execução nativa Codex orientada pela política canônica | nenhuma criação para duplicata/trivial; entrada qualificada continua permitida; pendente |
| P1 | confiança imutável A/B e método de merge | `test_install_launcher.py` e testes públicos existentes ampliados | A ancestral de B, digest dos bytes de A, adulteração rejeitada antes de executar, A alcançável em main após merge; pendente |
| P2 | parity/docs/referências/plugin ausente | `test_instrumentation_distribution.py`, checks docs existentes e suite completa | referências sincronizadas, pt/en equivalentes, sem plugin/coletor/framework; pendente |

### Validation commands and environment

Pré-flight de Apply: confirmar reserva/session/branch/HEAD, política atual versus esta base, árvore e fixtures; Python 3.10+, Git/gh/jq/curl, CLIs reais e versões, auth sem segredos, isolamento HOME/XDG/CODEX_HOME/PATH, ausência de outros writers. Não há Composer/npm/M2T nem serviços montados necessários. Tests fazem cópias Git e rollback em diretórios temporários; novos smokes retêm só evidência privada e dados descartáveis. Restringir PATH nos cenários exclusivos e testar caminhos com espaços/metacaracteres.

Comandos suportados (após implementar; todos pendentes):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_global_install.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_install_launcher.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_instrumentation_distribution.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/smoke_global_opencode.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/smoke_global_codex.py
openspec validate issue-77-native-codex --strict --no-interactive
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

Executar primeiro grupos focados; suite completa obrigatória no último HEAD limpo após Archive/commits. Onde `workflow-evidence` suportado, registrar/verificar prova local exata e manter ID fora do commit; não publicar comentário rotineiro. No pós-Archive, validar specs e arquivo pelos comandos oficiais efetivos, sem exigir change ativa já arquivada. Falha preexistente só é comparável no mesmo ambiente/base e não equivale a gate passado. Hosted checks reais, se surgirem na política viva, continuam obrigatórios.

## Planning handoff and review request

- run `wf-20261123T000922Z-ff820328`, worker `planning-77`, native session `ses_dfa4014d7ffe3jZCSEGGQOv3c4`.
- Escopo `single_issue`, repositório `rocker-code/my-ai-skills`, issue #77, `merge_mode=auto-if-green`, método necessário **merge commit**.
- Checkout `/home/beto/Projetos/my-ai-skills-worktrees/issue-77-native-codex`, branch `issue-77-native-codex`; base `58c9b67ee4148748f83539b457d6ddf49fedb4a4`. Reusar, não recriar. Sem PR ou sandbox M2T desta issue.
- Políticas lidas do checkout atual: `skills/implement-issue/SKILL.md`, `skills/openspec-workflow/SKILL.md`, `protocol/AI_WORKFLOW.md`, `WORKTREES.md`, `TEST_STRATEGY.md`, `REVIEW_POLICY.md`; skills oficiais locais `.agents/skills/openspec-*`. Pacote global instalado não é fonte desta política.
- Pin da proposta: commit imutável contendo este conjunto de artefatos, cujo SHA exato é retornado pelo worker ao coordenador. Não confundir esse pin de planejamento com futuros commits instalador A / launcher B.
- Revisão independente **PENDING**: o coordenador deve revisar esse SHA em contexto independente antes de despachar Apply. Foco obrigatório: seleção/compatibilidade, schema/ownership e rollback, paths/precedência Codex, identidade/independência, suficiência da matriz e publicação A/B. O planner não certifica sua própria independência.
- Após resultado da revisão, conservar referência exata no handoff existente/descrição futura da PR; findings materiais exigem proposta nova validada e revisada. Não publicar comentário/evento operacional.
- Não houve implementação, Apply, PR, update global real ou smoke nativo neste worker. Próxima ação: parar planner, obter revisão independente da proposta pinada, só então transferir reserva para sessão Apply genuinamente nova.

### Planning validation

Executado no conjunto de artefatos, antes do pin: `openspec status --change issue-77-native-codex --json` informa todos os quatro artefatos de planejamento completos; `openspec validate issue-77-native-codex --strict --no-interactive --json` aprovou 1/1, `valid=true`, `issues=[]`; `git diff --check` retornou 0. Revalidar o mesmo conjunto no commit pinado e devolver SHA/resultados ao coordenador.

Esses resultados validam **planejamento**, não implementação. Suite Python e smokes nativos continuam NOT RUN; não houve revisão independente neste contexto.
