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

## Apply handoff (parcial)

### Estado atual (substitui pendências iniciais abaixo)

- Auth isolada resolvida pelo [fallback oficial de cache headless](https://developers.openai.com/codex/auth.md?surface=cli): somente auth.json explícito copiado com permissão restrita e removido ao finalizar; config real intocada. Probe nativo Codex exit 0, thread `01a205d7-9681-7f81-b853-a83d5ce40a6c`, sem ferramentas; prova privada em `/tmp/opencode/issue77-native-probe-mbw28l2_`.
- Instalador A atual: `e6e1b5c2c7f83bf6efcb3246ee8526afd5f77c8d`, digest `0a683e0295d67ed63fa439d0a541d0192d5b1846a36051d23b055ba9d0a614de`. As âncoras anteriores `d8dd884...`, `d06b4dc...`, `acc97c8...`, `0613945...` e `1b6f01f...` não foram emendadas: novas revisões A incorporaram endurecimento de seleção, preservação CRLF/modos/rechecks, diagnóstico de skill desabilitada por nome, migração simultânea de aliases e recusa de estados parciais inconsistentes. O launcher posterior fixa A atual literalmente; refs finais de B/HEAD ficam fora deste commit. Merge commit permanece obrigatório; API viva confirmou `allow_merge_commit=true`.
- Grupos de desenvolvimento: instalador completo 48 testes/exit 0 (`ev-20261123T005353Z-aa800272`), launcher 8/exit 0 (`ev-20261123T005203Z-8157c284`), distribuição 4/exit 0 (`ev-20261123T005212Z-f3f326d8`). Suite ampla no B limpo: 232 testes/exit 0 (`ev-20261123T005710Z-6660bf45`), **não é gate final pós-archive**. Novas alterações posteriores exigem novas provas.
- Smoke OpenCode nativo: `ev-20261123T004648Z-5123e676`, exit 0, cinco skills oficiais carregadas/invocadas por API em dois projetos/worktree; `/tmp/opencode/smoke-global-opencode-5jzx8baq/results.json`. Não houve execução de modelo nesse smoke; não certifica lifecycle completo/independência Codex.
- Smoke Codex ainda **BLOCKED/pendente**, não aprovado: primeira tentativa (`ev-20261123T004648Z-acaea6be`) tinha asserção de path incompatível com raízes compactas nativas rN; corrigida por resolver tabela real, sem aceitar paths presumidos. Segunda (`ev-20261123T005353Z-887e90e2`) comprovou cinco skills em três locais, contextos distintos e sete execuções nativas terminadas, mas parou após commit de proposta por checkpoint sem reverify. Diagnóstico: fixture/controlador escreveu depois de checkpoint sem abrir novo intervalo verificado; a recusa do helper estava correta. Corrigido o smoke, não a proteção. Ainda faltam execução completa, retomada/consulta cross-agent e provas finais.
- Uma falha focada do baseline schema 1 usava modos de diretórios do working tree copiado (ex. 0664) em vez do checkout Git normalizado; corrigida a fixture para reconstruir manifesto do snapshot Git confiável. Grupo completo também revelou fixture de fallback OpenSpec sem launcher no PATH após mudança da ordem segura de preflight; foi corrigido somente o PATH, preservada a asserção de digest adulterado recusado.
- Terceira execução nativa (`ev-20261123T010347Z-334e49f9`) passou por descoberta, fresh context, proposta e revisão independente (oito threads terminadas) e transferência Codex→sessão OpenCode real. Parou corretamente por shell OpenCode ainda `running` no primeiro GET: API é assíncrona. Smoke agora espera o resultado terminal do comando exato, com prazo finito, antes de avaliar exit; nunca converte dispatch em aprovação.
- Inspeção dos eventos também revelou apps ChatGPT habilitados por default apesar de HOME vazio: a revisão tentou consultas reais somente leitura ao repo fixture (404). Nenhuma mutação real foi observada. Próximas execuções desabilitam apps, busca/browser/computer-use/remote-plugin e subagentes por opções oficialmente suportadas, além de recusar eventos MCP/web; todo backend GitHub deve passar pelo `gh` fixture capturado. Isso restringe somente o smoke, não o usuário.
- Quarta execução (`ev-20261123T011722Z-6ae30314`): retomada passou com Codex planner `01a205fc-682f-7c41-9784-f0ce1b36b32f` → OpenCode `ses_dfa0274f5ffeGyhVDeJWLA5b60` → status Codex novo `01a205fd-91ab-76b1-b97f-386a90f19694` → fresh Apply `01a205fe-214f-72f3-87ed-f951e5768105`. Mesmo checkout/change/PR draft fixture; writer desconhecido recusado; shell interrompido não aprovado; snapshots de arquivos Git e HEAD inalterados nas consultas. OpenCode aqui executa sessão/skills/shell, não modelo; sem portabilidade de chat.
- Nessa execução, Apply e teste real (1/1) passaram e Verify oficial em thread `01a205fe-be27-7710-a044-91d7e0cb3d76` retornou VERIFY_CLEAN. Archive em `01a205ff-6820-7ae1-ae08-a9e6e26641df` corretamente pediu confirmação: a proposta fixture havia omitido design.md, mas o CLI ainda o marcava ready. Smoke continua falho (não houve archive/PR/segunda issue). Correção: exigir explicitamente todos os artefatos do schema na proposta fixture e validar grafo antes de review/Apply, não dispensar a confirmação nem criar design durante Archive. Também fixar main como branch inicial da fixture, coerente com o backend, e python3 nos comandos planejados.
- Novo B limpo `687a18064362f6d18a085e30c4d017c43167af26`: suite ampla de desenvolvimento 234 testes/exit 0 (`ev-20261123T011722Z-fc123b4d`), smoke OpenCode exit 0 (`ev-20261123T011722Z-660f5359`). Ainda não é gate final pós-closeout.
- Self-review encontrou o caso real de skills.sh com diretório universal Codex e alias OpenCode do mesmo nome. Teste novo inicialmente recusou baseline no segundo agente porque o fetch repetia o mesmo diretório temporário. A atual compartilha o baseline confiável por nome e migra aliases antes do diretório, revertendo em ordem inversa. Prova focada com rollback dos dois caminhos: 7 testes/exit 0, `ev-20261123T013419Z-39a81adf`; sem enfraquecer origem/bytes/EXDEV/backup.
- A fixture de lifecycle agora usa Git real com origin bare local e main coerente, permitindo commit/push não forçado de preparação sem acesso a GitHub real; somente o backend gh é simulado. Isso não comprova publicação/CI/review hospedados.
- Para cumprir a transação coerente de D4, o ownership schema 2 (novo, ainda não publicado) vincula explicitamente a revisão ativa e aceita links anteriores somente quando inventariados no pacote anterior comprovado. Estado interrompido com revisão divergente, links órfãos ou skill anterior ausente bloqueia sem reparo/adopção implícitos. É detalhe de integridade do registro operacional existente, não store/lifecycle novo nem redução do contrato aprovado; schema 1 publicado permanece compatível. Prova focada: 13 testes/exit 0 (`ev-20261123T015259Z-ae54d69f`). Uma edição intermediária de indentação falhou antes da execução (`ev-20261123T015211Z-8f4ca06b`); corrigida no próprio código e refeito o grupo sem mudar asserções.

### Registro inicial histórico (não é o status atual)

- Apply `ses_dfa33e1cfffeWdMuWMEgF2qi91` confirmou reserva e SHA `2a6572d8271a467118aa61f0e952365783af8626`. Revisão independente desse SHA: sessão `ses_dfa3609e4ffenAb7XCzOZXHb6A`, callback APPROVED informado pelo coordenador; planner parado por callback. Política de teste do checkout não mudou desde o pin.
- Preflight nativo: Python 3.14.8, OpenSpec 2.1.1, OpenCode v2.3.2, Codex 0.171.0. Sem Composer/npm/M2T/serviços. Fixtures Git/HOME descartáveis; instalação real não alterada.
- Bloqueio de auth Codex isolada: `/tmp/opencode/issue77-codex-auth-9tra60y2/result-ready.json`, `codex login status` exit 1, `Not logged in`. HOME/CODEX_HOME/XDG novos, sem OPENAI_API_KEY/CODEX_ACCESS_TOKEN; nenhuma credencial real copiada. Invocação de modelo e independência Codex não comprovadas. Precisa autenticação isolada autorizada por mecanismo suportado, não troca de agente nem skip.
- Diagnóstico de testes focados: a execução exclusiva passou (1 teste); o primeiro grupo de 9 teve 8 falhas por launcher real vazando no PATH da fixture; a segunda execução teve 8 falhas distintas (`Falta gh no PATH`) após restringir PATH. Ambos ocorrem no preflight de instalação, antes de publicação/skills; são fixture/setup, não aplicação. `command -v gh` confirma `/home/beto/.local/bin/gh`. Alternativa simples: manter PATH herdado e ignorar colisão foi rejeitada por esconder risco. Correção escolhida: diretório fixture de dependências comuns com links explícitos para Git/gh/jq/curl/Python, sem expor launcher/runtime não selecionado. Nenhuma asserção foi removida ou enfraquecida. Esses resultados não são gate final e nenhuma falha é declarada preexistente.
- Após correção da fixture: `ev-20261123T003400Z-f1b218d1`, 10 testes focados, exit 0; `workflow-evidence verify` retornou `verified/passed` antes desta anotação. Evidência de desenvolvimento em árvore suja, não gate final; esta anotação posterior altera seu fingerprint. Comando exato e log checksum-bound no registro. A suite completa, os grupos completos e ambos smokes ainda não foram executados; não há contagem aprovada para eles.
- Estado parcial: somente `scripts/install-global`, `tests/test_global_install.py` e este handoff alterados. Nenhum dos 17 itens está integralmente concluído (faltam documentação/contratos/pós-checks e provas nativas); checkboxes continuam abertos. Não há commit A/B, pin novo, PR, archive/sync ou invocação Verify desta implementação. O pin público anterior não corresponde aos bytes de trabalho novos até a publicação A/B futura; não usar o checkout como distribuição concluída.
- Pesquisa de auth: [documentação oficial](https://developers.openai.com/codex/auth/) confirma cache em `CODEX_HOME/auth.json` ou keyring, login por browser/API key/access token e tratar auth.json como senha. `codex login --help` confirma `--with-api-key`, `--with-access-token`, `--device-auth`; nenhuma opção foi usada para iniciar login. Próxima ação: preparar autenticação isolada autorizada ou autorizar explicitamente reutilização protegida do cache existente, sem copiar config, expor segredos ou escrever no HOME real; depois retomar Apply no mesmo checkout/reserva.

As duas falhas históricas abaixo foram observadas no transcript nativo da sessão Apply, no HEAD indicado e com alterações locais. O SHA identifica esse contexto, não certifica uma execução limpa nem constitui prova independente; só o terceiro resultado possui log checksum-bound. Assinaturas diferentes refletem mensagens reais diferentes do preflight, não reclassificação artificial de uma mesma falha.

```attempt-log
{
  "attempt_log": 1,
  "entries": [
    {
      "kind": "attempt", "seq": 1, "obligation": "installer-focused",
      "signature": "InstallError: comando de outra origem precede launcher no PATH",
      "target": "9 testes focados GlobalInstallTests", "class": "environment/bootstrap",
      "hypothesis": "A fixture herdada usa somente dependências de teste",
      "change": "Implementação inicial de seleção e testes novos", "change_target": "application",
      "observed_effect": "8/9 falharam no preflight porque o launcher real era descoberto",
      "result": "fail", "evidence": ["2a6572d8271a467118aa61f0e952365783af8626"]
    },
    {
      "kind": "attempt", "seq": 2, "obligation": "installer-focused",
      "signature": "InstallError: falta gh no PATH",
      "target": "mesmos 9 testes focados GlobalInstallTests", "class": "environment/bootstrap",
      "hypothesis": "PATH com diretórios de sistema evita launcher real e contém dependências comuns",
      "change": "Restringir PATH da fixture a bin local e diretórios de sistema", "change_target": "fixture",
      "observed_effect": "8/9 falharam antes de instalar: gh está no bin do usuário, não no sistema",
      "result": "fail", "evidence": ["2a6572d8271a467118aa61f0e952365783af8626"]
    },
    {
      "kind": "diagnosis", "seq": 3,
      "group": {"obligation": "installer-focused", "signature": "InstallError: falta gh no PATH"},
      "class": "environment/bootstrap",
      "checked": {
        "phase": "preflight do instalador, antes de manifesto e publicação",
        "scope": "HOME/PATH descartáveis da fixture unittest",
        "lifecycle": "instalação inicial bloqueada; active ainda ausente",
        "consumers": "preflight precisa gh; inspect_launcher recusa comando real de outra origem"
      },
      "runtime_proof": ["2a6572d8271a467118aa61f0e952365783af8626"],
      "simplest_alternative": "Restaurar PATH herdado foi rejeitado: reintroduz colisão real",
      "choice_rationale": "command -v gh confirmou bin do usuário; links explícitos isolam dependências sem abrir o PATH do usuário",
      "next_hypothesis": "Diretório comum de ferramentas fixture resolve gh sem vazar launcher ou runtime não selecionado"
    },
    {
      "kind": "attempt", "seq": 4, "obligation": "installer-focused",
      "signature": "InstallError: falta gh no PATH",
      "target": "mesmos 9 testes + cenário exclusivo por agente", "class": "fixture/isolation",
      "hypothesis": "Links explícitos para dependências comuns isolam o preflight",
      "change": "Diretório common-tools fixture com Git/gh/jq/curl/Python; manter PATH restrito",
      "change_target": "fixture", "observed_effect": "10 testes passaram, exit 0",
      "result": "pass", "evidence": ["evidence:ev-20261123T003400Z-f1b218d1"]
    },
    {
      "kind": "resolution",
      "group": {"obligation": "installer-focused", "signature": "InstallError: falta gh no PATH"},
      "outcome": "passed", "via_seq": 4
    },
    {
      "kind": "attempt", "seq": 5, "obligation": "codex-smoke",
      "signature": "AssertionError: absolute skill path absent in native compact inventory",
      "target": "smoke_global_codex.py", "class": "assertion/contract",
      "hypothesis": "debug prompt-input apresenta cada caminho absoluto completo",
      "change": "Smoke nativo inicial", "change_target": "test",
      "observed_effect": "Uma thread real terminou; inventário codifica paths como rN mais tabela de roots",
      "result": "fail", "evidence": ["evidence:ev-20261123T004648Z-acaea6be"]
    },
    {
      "kind": "attempt", "seq": 6, "obligation": "codex-smoke",
      "signature": "reservation checkpoint exit 3: verify current baseline before writing/checkpointing",
      "target": "smoke_global_codex.py", "class": "fixture/isolation",
      "hypothesis": "Resolver roots compactos permite seguir pelo lifecycle real",
      "change": "Resolver rN e exigir carregamento real do corpo das cinco skills", "change_target": "test",
      "observed_effect": "Descoberta em três locais e contexto novo passaram; sete threads terminaram; controle parou após commit sem reverify",
      "result": "fail", "evidence": ["evidence:ev-20261123T005353Z-887e90e2"]
    },
    {
      "kind": "diagnosis", "seq": 7,
      "group": {"obligation": "codex-smoke", "signature": "reservation checkpoint exit 3: verify current baseline before writing/checkpointing"},
      "class": "fixture/isolation",
      "checked": {
        "phase": "controlador após retorno Codex e git commit da proposta",
        "scope": "worktree descartável registrada; sessão nativa real como owner",
        "lifecycle": "checkpoint fechou intervalo anterior; controlador precisava reverify antes do commit",
        "consumers": "handoff/commit/checkpoint do smoke; proteção worktree-reservation correta"
      },
      "runtime_proof": ["evidence:ev-20261123T005353Z-887e90e2"],
      "simplest_alternative": "Adicionar verify imediatamente após cada checkpoint e antes da próxima escrita",
      "choice_rationale": "Não aceitar drift automaticamente nem enfraquecer helper; código de produção não é a causa",
      "next_hypothesis": "Intervalos de escrita explícitos permitem commit e fresh Apply sem perder proteção"
    },
    {
      "kind": "attempt", "seq": 8, "obligation": "installer-complete",
      "signature": "AssertionError: digest refusal absent; launcher path missing",
      "target": "test_global_install.py", "class": "fixture/isolation",
      "hypothesis": "Fixture de fallback ainda satisfaz pré-requisitos anteriores ao download",
      "change": "Grupo completo após publicação B", "change_target": "none",
      "observed_effect": "46/47 passaram; fallback recusou launcher fora do PATH antes de atingir digest",
      "result": "fail", "evidence": ["evidence:ev-20261123T005212Z-f8047ef4"]
    },
    {
      "kind": "attempt", "seq": 9, "obligation": "installer-complete",
      "signature": "AssertionError: digest refusal absent; launcher path missing",
      "target": "test_global_install.py", "class": "fixture/isolation",
      "hypothesis": "Incluir bin global descartável alcança a mesma fronteira negativa de digest",
      "change": "Somente PATH da fixture; mesma asserção de digest e não execução", "change_target": "fixture",
      "observed_effect": "48 testes passaram, incluindo novo negativo de capacidade Codex", "result": "pass",
      "evidence": ["evidence:ev-20261123T005353Z-aa800272"]
    },
    {
      "kind": "resolution",
      "group": {"obligation": "installer-complete", "signature": "AssertionError: digest refusal absent; launcher path missing"},
      "outcome": "passed", "via_seq": 9
    },
    {
      "kind": "attempt", "seq": 10, "obligation": "codex-smoke",
      "signature": "AssertionError: native OpenCode shell still running on first GET",
      "target": "smoke_global_codex.py --cross-agent-opencode", "class": "fixture/isolation",
      "hypothesis": "Reverify após checkpoint permite revisão e retomada nativa",
      "change": "Intervalos verificados e cenário de retomada por sessão/shell OpenCode", "change_target": "test",
      "observed_effect": "Oito threads terminaram; proposta/review e handoff passaram; shell assíncrono não tinha resultado terminal no GET imediato",
      "result": "fail", "evidence": ["evidence:ev-20261123T010347Z-334e49f9"]
    },
    {
      "kind": "diagnosis", "seq": 11,
      "group": {"obligation": "codex-smoke", "signature": "AssertionError: native OpenCode shell still running on first GET"},
      "class": "fixture/isolation",
      "checked": {
        "phase": "leitura da mensagem shell após POST API 204",
        "scope": "servidor privado OpenCode no HOME descartável",
        "lifecycle": "shell nativo despachado, ainda running; não é teste aprovado",
        "consumers": "native_shell e verificação do teste interrompido"
      },
      "runtime_proof": ["evidence:ev-20261123T010347Z-334e49f9"],
      "simplest_alternative": "Esperar status terminal do comando exato por leitura nativa delimitada",
      "choice_rationale": "Preservar a asserção de término/exit; não usar sleep fixo nem aceitar running como sucesso",
      "next_hypothesis": "Resultado terminal real permite distinguir consulta bem-sucedida e teste interrompido sem aprovar este último"
    },
    {
      "kind": "attempt", "seq": 12, "obligation": "codex-smoke",
      "signature": "AssertionError: native archive awaited confirmation for unfinished design artifact",
      "target": "smoke_global_codex.py --cross-agent-opencode", "class": "fixture/isolation",
      "hypothesis": "Esperar shell terminal permite avançar retomada e lifecycle",
      "change": "Wait nativo delimitado e restrição de conectores externos", "change_target": "test",
      "observed_effect": "Retomada, fresh Apply, teste real e Verify passaram; Archive manteve change ativa por design.md ready",
      "result": "fail", "evidence": ["evidence:ev-20261123T011722Z-6ae30314"]
    },
    {
      "kind": "diagnosis", "seq": 13,
      "group": {"obligation": "codex-smoke", "signature": "AssertionError: native archive awaited confirmation for unfinished design artifact"},
      "class": "fixture/isolation",
      "checked": {
        "phase": "Archive oficial após Apply/teste/Verify concluídos",
        "scope": "proposta fixture mínima, artefato design.md ausente",
        "lifecycle": "CLI status mantém design ready e skill exige confirmação de artefato pendente",
        "consumers": "contrato schema planning → Archive; a recusa nativa é correta"
      },
      "runtime_proof": ["evidence:ev-20261123T011722Z-6ae30314"],
      "simplest_alternative": "Exigir design e demais artefatos do schema no Propose antes de review/Apply",
      "choice_rationale": "Não simular confirmação nem reduzir gate; manter Archive e validação oficiais intactos",
      "next_hypothesis": "Grafo de planejamento completo permite sync/archive sem aprovação excepcional"
    }
  ]
}
```
