# Design

## Context

Correção material **R1**, não novo suporte Codex. Base/PR: `32c2b64225e2d24fbcf1e39ee5d1daf95919662c`, [PR81](https://github.com/rocker-code/my-ai-skills/pull/81), mesma issue77/branch/worktree. Ver motivação em `proposal.md`.

- Auditor independente `ses_df99f2ca6ffe8Zsz7iGkJ0OFee`: sole MUST FIX em `scripts/install-global:384–391`.
- Reprodutor `ses_df998c87dffeHmZOFqycX3mDti`: `ev-20261123T031826Z-1962e5f7`, `verified/passed`, `no_required_gate`, quatro casos diagnósticos. Literal bloqueia; indentado, `[[ skills . config ]]` e array inline são TOML válido com a mesma regra false e passam. **É prova do defeito, não da correção ou gate obrigatório**; o verificador retorna exit 3 para ausência de gate apesar de registrar `verified/passed`.
- `tests/test_global_install.py:test_codex_custom_paths_config_override_and_root_drift` cobre apenas as formas literais por path/nome; usa diretório temporário, preservação de config/auth, override e drift de root. Ampliar aqui e nos testes públicos, sem outra infraestrutura de testes.
- `install-global` já exige Python 3.10+, publica quatro componentes incluindo `scripts/` recursivo e autentica snapshots/manifesta/ownership. `install.sh` baixa só a entrada standalone para arquivo temporário e verifica SHA-256 antes de executar; importar módulo vizinho não disponível nesse bootstrap seria regressão.
- Âncoras existentes: A `e6e1b5c2c7f83bf6efcb3246ee8526afd5f77c8d`, B `651af7167d5800fe5a5378731d8b24be3e3be1d8`. Não emendar nem substituir seus objetos.

### Native update versus follow-up

A skill oficial local `openspec-update-change` só revisa artefatos existentes da change ativa. `openspec list --json` não lista issue77; `status --change issue-77-native-codex --json` confirma que não é uma change ativa. O CLI oferece `new/change/archive`, sem operação de reabertura descoberta. `skills/openspec-workflow/SKILL.md` proíbe reescrever história arquivada para esconder requisito mudado.

Logo esta correção usa Propose oficial e scaffold `issue-77-codex-toml-r1`, relacionado a `openspec/changes/archive/2026-11-23-issue-77-native-codex/`. Não move/desarquiva nem edita esse diretório; não duplica issue, PR ou worktree. Os deltas acrescentam precisão aos requisitos de diagnóstico/distribuição atuais, sem copiar novamente todo o contrato anterior. Apply/Verify/Archive futuros são nativos nesta follow-up.

## Goals / Non-Goals

**Goals:** interpretar TOML de verdade, eliminar o bypass sintático R1 e preservar Python mínimo, configuração/credenciais, integridade e rollback. Tornar explícita a nova dependência de produção e sua cadeia de distribuição para revisão independente.

**Non-Goals:** parser próprio, API/service experimental Codex, `pip`/venv/instalação de pacote no ambiente do usuário, framework de dependências, nova política de seleção/merge, fusão de todas as camadas de configuração Codex, alteração de runtime/smoke fixture ou dos contratos T1–T11 não afetados.

## Decisions

### D1 — Tomli upstream puro Python incorporado, uma implementação em todos os Pythons suportados

Escolha: **Tomli 2.5.0**, sem alterações na gramática/código upstream, usado para esta leitura em **todo Python 3.10+**. Não selecionar `tomli` do ambiente. Não é necessário manter dois caminhos stdlib/fallback: a dependência já precisa acompanhar o bootstrap 3.10, e um único parser elimina diferenças de versão TOML entre interpretadores.

Pesquisa oficial em 23/11/2026:
- [`tomllib`](https://docs.python.org/3/library/tomllib.html) só existe desde 3.11; suporta TOML 1.0 até Python 3.14 e 1.1 desde 3.15.
- [Tomli README 2.5.0](https://raw.githubusercontent.com/hukkin/tomli/2.5.0/README.md): parser completo, puro Python, zero dependências de runtime; `load/loads` retornam tipos básicos; erro TOML explícito. Versões 2.4+ interpretam TOML 1.1, incluindo 1.0.
- [Metadados da release PyPI](https://pypi.org/pypi/tomli/2.5.0/json): `requires-python >=3.8`, MIT, sdist de 17.662 bytes. A versão é compatível com 3.10, sem wheel binária ou build.
- [Changelog da release](https://raw.githubusercontent.com/hukkin/tomli/2.5.0/CHANGELOG.md): inclui correções recentes de limites de chaves/aninhamento; não escolher versão antiga apenas para evitar suporte 1.1.

Alternativas:
- `tomllib` somente: quebra 3.10; rejeitada.
- `tomllib` + fallback Tomli: viável, mas duplica caminhos/testes e aceita gramáticas diferentes conforme o Python; não reduz a dependência que já precisa ser embutida; rejeitada para esta integração pequena.
- Codex experimental `app-server` para config parseada: acopla instalação a API/service e capacidades de produção adicionais; rejeitada.
- `pip`, `tomlkit`/outra biblioteca ambiente ou download de parser em cada instalação: custo/configuração/trust extras desnecessários; rejeitados.
- ampliar regex ou escrever subset parser: mantém bypass e assume manutenção de gramática; rejeitado.

Isso não declara que o instalador valida todo o schema nativo do Codex ou o torna compatível com sintaxe que o próprio runtime não aceite. Ele só usa uma gramática completa e estável para o diagnóstico de configuração já existente.

### D2 — Proveniência e licença exatas

Artefato escolhido:

```text
Upstream: https://github.com/hukkin/tomli
Version: 2.5.0
Git commit da tag anotada 2.5.0: a2a578949199336ebc3884eeba4aede87da41ef2
Source URL: https://files.pythonhosted.org/packages/b0/78/9ad63712633ed3ab5cc1a648d863d7e7da371e9425e209555a0fe711b695/tomli-2.5.0.tar.gz
Source SHA-256: 264507556cd8b8c8e7c6ee037cdf443a463f03f4c958e57195e3d369711b8ff6
License: MIT
Copyright: (c) 2021 Taneli Hukkinen
License SHA-256: b80816b0d530b8accb4c2211783790984a6e3b61922c2b5ee92f3372ab2742fe
```

O planner leu o sdist em memória, conferiu seu digest publicado, licença, metadados e imports, sem executá-lo nem salvar dependência em produção. Comparou os seis arquivos abaixo aos bytes obtidos do **commit Git imutável** acima; todos os hashes coincidiram:

| Arquivo no sdist sob `tomli-2.5.0/` | SHA-256 |
|---|---|
| `src/tomli/__init__.py` | `7182927b251660b7d649eec79e0dcaf03a59973793400990a693d9f6f8b73eca` |
| `src/tomli/_parser.py` | `3e782f1bc85639ecef630ae686df3d849f2bedd2e9c987d8f5109a5a154df131` |
| `src/tomli/_re.py` | `a12359fe294523a72112e434d58452a14c9d050affa2417f9927474e4166bfdd` |
| `src/tomli/_types.py` | `f864c6d9552a929c7032ace654ee05ef26ca75d21b027b801d77e65907138b74` |
| `src/tomli/py.typed` | `f0f8f2675695a10a5156fb7bd66bafbaae6a13e8d315990af862c792175e6e67` |
| `LICENSE` | `b80816b0d530b8accb4c2211783790984a6e3b61922c2b5ee92f3372ab2742fe` |

A MIT permite redistribuição com preservação do aviso de copyright e licença completos, inclusive disclaimer. A implementação incluirá o texto completo como comentário legível no próprio `scripts/install-global` e em documentação de proveniência sob `scripts/vendor/TOMLI.md`, com instrução offline para inspecionar o payload. Não basta linkar a licença nem adicionar somente `MIT` ao changelog. O sdist incorporado também contém a licença; mantê-la no standalone e na instalação.

### D3 — Bootstrap autocontido e bytes completos autenticados

Incorporar **os bytes exatos do sdist pinado** como literal binário codificado determinísticamente em `scripts/install-global` (por exemplo Base85). Não criar fork do parser, reconstruir sdist ou baixar dependência em runtime. Esse único payload é fonte canônica vendorizada; não manter segunda árvore editável de parser.

Carregamento deve:
1. Decodificar o literal, conferir tamanho/digest do sdist **antes** de descomprimir ou carregar código.
2. Ler apenas os seis membros regulares explicitamente listados em D2; validar nomes/tipos/tamanhos/hashes esperados. Não usar extração ampla, aceitar links, paths absolutos/`..` ou executar build/setup/entrypoints do sdist.
3. Disponibilizar os módulos upstream intactos em diretório temporário privado, por importação explícita em namespace privado do instalador. Não importar `tomli` de CWD, PYTHONPATH ou site-packages, nem alterar `sys.path` global para permitir shadowing.
4. Evitar bytecode persistente; liberar módulo/recursos temporários ao final da inspeção, também em falha. Nenhum parser/config é publicado em HOME, no ambiente Python ou em diretório de execução compartilhado.

O wrapper de carregamento usa apenas stdlib Python 3.10 e não interpreta TOML. Carregar preguiçosamente apenas quando o fluxo Codex inspecionar config existente; OpenCode-only não precisa iniciar parser/serviço Codex. Erro no payload ou carregamento vira bloqueio explícito, nunca fallback para regex, outra biblioteca ou config ignorada.

O hash externo em B_R1 autentica **todos** os bytes de A_R1, inclusive payload e constantes. O hash interno do sdist fixa proveniência e detecta corrupção, mas não substitui a confiança externa: modificar payload e digest interno ainda altera o instalador e deve ser recusado pelo pin externo. O snapshot instalado inventaria os bytes completos do instalador e os docs/licença pelos mecanismos atuais.

### D4 — Interpretar estrutura, preservar o guard existente e falhar de forma segura

Substituir somente leitura/detecção em `inspect_codex()` por parse completo do arquivo UTF-8 em modo binário e travessia dos objetos. Reconhecer table arrays, dotted keys, chaves quoted, inline tables, escapes, espaços/indentação e comentários como definidos pelo parser upstream.

Validar defensivamente o subconjunto lido: `skills` quando presente é tabela; `skills.config` quando presente é array de tabelas; cada regra relevante tem seletor `name` ou `path` string e `enabled`, quando presente, booleano. Ausência de `skills/config` ou regra enabled não cria desabilitação. Estruturas incompatíveis nesse subconjunto bloqueiam com ação de reconciliação; não tentar validar/reescrever o restante do schema Codex.

Manter o critério conservador atual de conflito por nome canônico ou componentes do path, agora aplicado ao **valor decodificado**, sem redesenhar resolução de paths/seleção, mesclar profiles/projeto/trust ou anunciar config efetiva do runtime. Regras canônicas false continuam exigindo reconciliação explícita; o instalador não modifica regras para habilitá-las. Comentários, literais contendo texto TOML e regras de outras skills não são regras canônicas.

Capturar falhas de leitura/UTF-8, `TOMLDecodeError`, estrutura/tipos inválidos e limites de parser com mensagem delimitada: caminho + classe de causa, posição numérica quando disponível, nunca dump do documento/linha, `repr` do erro ou valor de chave. Não executar hooks/commands do documento, iniciar auth ou serializar config.

Executar esse guard antes de preparar links/orientação/ownership/ativação, na fronteira já usada. Não promete que nenhum diretório temporário/cache de preparação exista; promete instalação anterior utilizável e nenhum efeito gerenciado parcial publicado. Testar config/auth bytes e modos, active, launcher, links e ownership antes/depois no caso multiagente. Não criar ledger, novo schema de instalação nem mudar rollback das demais fases.

### D5 — Manutenção e publicação A_R1/B_R1

Atualização da dependência é trabalho explícito revisado: conferir release imutável, Python mínimo, changelog/correções, licença e hashes; substituir payload inteiro por bytes upstream verificados, atualizar proveniência e regenerar pins; executar testes offline. Não resolver `latest`, instalar wheel binária, executar build script ou autoatualizar dependência no HOME do usuário.

Após correção/testes pertinentes, criar **novo** A_R1 contendo instalador completo e licença/proveniência. Criar B_R1 posterior pinando SHA completo de A_R1 e SHA-256 literal de `git show A_R1:scripts/install-global`. Atualizar testes públicos e receitas pt/en, mantendo aviso de confiança limitada do launcher obtido de main. Não emendar A/B existentes nem usar SHA/digest de B_R1, ref móvel ou cálculo dinâmico no bootstrap.

O payload está dentro do instalador: não há grafo novo de downloads/arquivos que o launcher precisaria autenticar separadamente. Testes devem provar isolamento standalone em arquivo temporário sem módulos vizinhos, cadeia completa externa/interna, preservação de seleção e comportamento nos três modos. A integração final continua por **merge commit**, preservando âncoras antigas e novas alcançáveis; verificar disponibilidade pública efetiva antes de declarar publicação.

## Risks / Trade-offs

- [Nova dependência executável] → release pequena, completa, sem dependências de runtime, puro Python, MIT, código upstream intacto; revisão independente desta fronteira obrigatória.
- [Payload codificado dificulta diff] → bytes exatos do sdist com digest conhecido, tabela de arquivos/hashes, licença legível e procedimento offline de inspeção; tests não dependem de download.
- [Extração/import cria superfície de execução] → hash antes de ler archive, allowlist de membros regulares, paths fixos em temporário privado e namespace isolado; nunca `extractall`/setup ou import ambiente.
- [Python varia gramática] → uma versão Tomli em 3.10+, com teste em interpretador 3.10 real; não declarar compatibilidade só por mock de `sys.version_info`.
- [Erro de config revela credencial] → mensagem fixa/posição/caminho sem texto de valor; fixture malformada com segredo sentinela deve provar ausência em stdout/stderr.
- [Guard começa a ignorar documento inválido] → falha fechada e teste de instalação/update conjunto preservando estado anterior, não apenas teste unitário do parser.
- [Novo instalador fica atrás do pin antigo] → novo par A_R1/B_R1, igualdade de bytes testada; gate final invalida após qualquer commit.

## Migration Plan

1. Não alterar instalação real. Corrigir/testar em fixtures descartáveis com HOME/CODEX_HOME/XDG/PATH isolados, preservando `scripts/__pycache__/install-globalcpython-314.pyc` preexistente.
2. Não migrar schema nem seleção: o payload viaja no instalador já inventariado; documentação/licença sob `scripts/` segue inventário recursivo existente. Versões anteriores e arquivos desconhecidos permanecem intocados.
3. Entrada standalone nova usa payload autenticado antes de diagnosticar config. Config inválida/guard recusado mantém instalação anterior; usuário reconcilia explicitamente o próprio documento, sem reparo automático.
4. Publish novos A_R1/B_R1, Verify/strict/archive da follow-up na mesma PR e suite final no HEAD limpo exato; conferir revisão independente e pins/método de merge antes de entrega. Não reabrir/reescrever archive anterior.

## Requirement → Test Risk Matrix

No planejamento todos os testes de correção estavam PENDING/NOT RUN. A tabela abaixo registra a execução Apply; `ev-20261123T031826Z-1962e5f7` permanece reprodução histórica, não aprova nenhuma linha.

| ID | Requisito/risco e consumidor | Menor prova planejada | Estado |
|---|---|---|---|
| R1.1 / T8 | `inspect_codex` ignora 3 formas válidas; seletor nome/path decodificado | `test_codex_semantic_spellings_and_non_rule_controls`: quatro grafias + quoted, nome/path e escapes; bloqueio e bytes/modos | PASS focados `ev-20261123T034454Z-873758bb` |
| R1.2 / T8 | falso positivo textual | mesmo teste: ausente, skills ausentes, true, enabled ausente, outra skill false, comentário/string | PASS mesmos focados |
| R1.3 / T7/T8 | parse/leitura/schema/limites, segredo/efeito parcial | `test_codex_invalid_config_preserves_multiagent_update_and_secrets` + erro IO mockado: UTF-8, duplicata/truncamento, tipos/subconjunto, 1 MiB/aninhamento; snapshot de bytes/modos/active/ownership/links/launcher/auth | PASS mesmos focados |
| R1.4 / T1/T2/T3 | standalone/Python mínimo/shadowing | grupos completos em Python **3.10.22 real**, sem tomli/tomllib ambiente; standalone/cwd/PYTHONPATH sentinelas e OpenCode-only | PASS 71/71 `ev-20261123T034502Z-ce423f52`; atual 71/71 |
| R1.5 / P1/P2 | proveniência/licença/integridade | distribuição decodifica sdist offline, seis membros intactos e licença; corrupção rejeitada antes de archive/import; standalone/limpeza; pin externo cobre payload | PASS nos dois grupos completos |
| R1.6 / T3/T8 | inventário/rollback/update | casos existentes preservados; missing/modified ampliado para instalador/docs novos; manifesto, failpoints, migração anterior, três seleções | PASS nos dois grupos completos |
| R1.7 / P1 | novo par imutável | A_R1 `7c4cfb4…`, B_R1 `a080649…`, digest literal/bytes/ancestralidade; fluxos públicos e receitas pt/en | PASS nos focados; disponibilidade pública pós-merge ainda não declarada |
| R1.8 / T1–T11/P1/P2 | regressão restante | focados 71/71; novo smoke OpenCode 15 sessões `ev-20261123T034740Z-944cc10c`; novo diagnóstico nativo Codex 3 locais `ev-20261123T034748Z-e6f908ea`; gate completo somente no HEAD final pós-archive | PASS focados/superfícies afetadas; gate final registrado fora do commit/na PR |

### Commands and evidence

Pré-flight de Apply: confirmar proposta/revisão exatas, stopped-writer e reserva, HEAD/política/fixtures, hashes/licença; verificar interpretador 3.10 realmente disponível ou sandbox descartável suportado. Não instalar/atualizar Python nem pacote no sistema como efeito implícito. Se falta ambiente 3.10, registrar bloqueio de R1.4, não simular sucesso nem elevar o mínimo.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_global_install.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_install_launcher.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_instrumentation_distribution.py
PYTHONDONTWRITEBYTECODE=1 python3.10 -m unittest discover -s tests -p test_global_install.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/smoke_global_codex.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/smoke_global_opencode.py
openspec validate issue-77-codex-toml-r1 --strict --no-interactive --json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

O comando 3.10 usa o interpretador verificado ou equivalente em sandbox suportado, nunca um alias para Python atual. Focados vêm antes dos smokes/suite. Manter T1–T11/P1/P2 do archive anterior; R1 refina T7/T8 e acrescenta prova do novo limite de dependência/publicação. Provas anteriores continuam históricas; revalidar superfícies afetadas, e suite final local obrigatória após todos os commits/archive no HEAD limpo exato. Não apresentar smoke antigo ou reprodução como aprovação do candidato novo.

Verify oficial não substitui esses testes. No pós-Archive usar validações oficiais de specs/archives do CLI efetivo. Registrar IDs acessíveis no handoff/descrição existente da PR, sem comentário rotineiro. Não executar gates de implementação neste planner.

## Planning handoff and independent review request

- run `wf-20261123T000922Z-ff820328`; worker `planning-77-r1`; native session `ses_dfa4014d7ffe3jZCSEGGQOv3c4`; task `planning_only_material_replan_R1`.
- Issue https://github.com/rocker-code/my-ai-skills/issues/77; PR https://github.com/rocker-code/my-ai-skills/pull/81; scope `single_issue`; modo herdado `auto-if-green`, método obrigatório merge commit. Sem nova issue/PR/worktree.
- Checkout `/home/beto/Projetos/my-ai-skills-worktrees/issue-77-native-codex`, branch `issue-77-native-codex`; input HEAD `32c2b64225e2d24fbcf1e39ee5d1daf95919662c`; archive anterior intacto. Bytecode ignorado diagnosticado anteriormente é preservado, não reivindicado para limpeza.
- O commit contendo estes seis artefatos é o novo pin de planejamento retornado ao coordenador. Não confundir com o pin original `2a6572d8271a467118aa61f0e952365783af8626` nem com novos A_R1/B_R1 ainda inexistentes.
- **Revisão independente PENDING** antes de fresh Apply: confirmar escolha/versionamento/licença do parser, payload completo/allowlist/import isolado, ausência de dependência ambiente/rede, erros sem vazamento e publicação A_R1/B_R1. Esta sessão não certifica independência própria.
- Sem decisão material de produto/política pendente após pesquisa. Implementação, gates da correção, push/PR edit e mudanças globais não foram executados. Após commit/strict, parar planner e liberar reserva WAITING ownerless para revisão/transferência coordenada; preservar arquivos ignorados.

### Planning validation

`openspec status --change issue-77-codex-toml-r1 --json` confirmou os quatro artefatos de planejamento completos. `openspec validate issue-77-codex-toml-r1 --strict --no-interactive --json` aprovou 1/1, `valid=true`, `issues=[]`; `git diff --check` retornou 0. Revalidar no commit pinado e devolver o SHA exato, sem converter validação de planejamento em prova da implementação.

Pesquisa da dependência foi somente leitura/verificação de bytes em memória. Não houve carregamento de Tomli, código de produção alterado ou teste de correção executado neste planner.

## Apply R1 — execução e publicação corretiva

- Pin revisado: `2d44b9ae5433cef60278907c53b23bd979057aed`, APPROVED pelo revisor independente `ses_df98b447bffeOIMFzgGKO3RDea` conforme handoff do coordenador; strict 1/1 sem findings. Apply novo: `ses_df9887c87ffeq1uOQTv7rj52cn`, reserva própria após planner parado/WAITING ownerless. Não é autoaprovação da implementação.
- Políticas locais de Apply/TEST_STRATEGY/OpenSpec conferidas contra o pin: inalteradas; pacote global antigo não substitui as skills deste checkout. Nenhum update global ou comentário operacional executado.
- A_R1: `7c4cfb4433c4f56b9af463759e8215174b5b9663`; SHA-256 de **todos** os bytes do instalador: `93cd9371b602a47c66b6bc3b20be448f6c124fc88b10a9f5d041f611dddc1a5f`. Launcher posterior fixa ambos literalmente; receitas pt/en e testes usam os mesmos bytes. Âncoras A/B anteriores preservadas, sem amend; merge commit continua obrigatório.
- Focados completos: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_global_install test_install_launcher test_instrumentation_distribution`: **71/71**, exit 0, `ev-20261123T034454Z-873758bb`, `verified/passed` no estado de desenvolvimento. Inclui os três fluxos públicos com transporte local e instalador real standalone; config existente força carregamento, bloqueio/update não publicam e corrupção só do payload falha no pin externo.
- Mesmo grupo em **Python 3.10.22 real**: **71/71**, exit 0, `ev-20261123T034502Z-ce423f52`, `verified/passed` com `--tool python=3.10.22`. Sem `tomli`/`tomllib` ambiente (`find_spec` comprovado), sem pip. Sandbox em `/tmp/opencode/issue77-r1-python310`, não altera Python do usuário; distribuição astral-sh/python-build-standalone `20261009`, asset `cpython-3.10.22+20261009-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz`, digest publicado/conferido `caa66b308e10f35b8114054df7d927903f971f631cfa3237b84c40d5d5f35549`.
- Preflight: descoberta/fixtures `unittest`, ferramentas Git/gh/jq/curl/OpenSpec disponíveis; HOME/CODEX_HOME/XDG/PATH isolados por teste, transporte Git fixture; sem serviços, manifests de dependências ou DB compartilhados. Nenhum modelo/credencial nos testes focados.
- Um desenvolvimento falhou (`ev-20261123T033858Z-13f4eda9`): cauda de teste existente deslocada por inserção, corrigida sem remover asserts; o teste de receita ainda apontava A antigo antes da criação obrigatória de A_R1/B_R1. Não foi atribuído ao base nem aprovado; focados posteriores passaram. Não houve episódio de falha repetida. O wrapper rejeitou um identificador `--tool` com path antes de executar teste; corrigido para versão não secreta, não é execução de teste.
- Provas de desenvolvimento ficam históricas após commits; `no_required_gate` dá exit 3 no verifier mesmo para `verified/passed`. Nenhuma delas substitui a suite local obrigatória no HEAD final limpo após archive/commits.
- B_R1: `a0806493280d062ae477a608ccdcc67a3ca337e5`, posterior a A_R1. Os bytes do instalador não mudam após A_R1; arquivo `update.sh` permanece byte-idêntico ao head anterior.
- Smokes no B_R1: OpenCode `ev-20261123T034740Z-944cc10c`, `verified/passed`, cinco skills oficiais invocadas por API em 15 sessões/3 locais, sem modelo; Codex `ev-20261123T034748Z-e6f908ea`, `verified/passed`, instalação nova com config existente e `codex debug prompt-input` comprova paths nativos/canônicos em dois projetos + worktree com espaços. O probe issue-local, inputs JSON e relatório estão checksum-bound. **Não** executou modelo nem repetiu lifecycle Codex.
- Reuso limitado: o smoke Codex completo `ev-20261123T024546Z-fe334d2b` (20 threads/duas issues) e OpenCode anterior `ev-20261123T030740Z-e416dfdf` são históricos, não gates atuais. Comparação de bytes contra `87543a49a4302017cbe558cfeacbcbf57e521ee3` confirmou **todos** os arquivos `skills/`, `protocol/`, `templates/`, os dois `tests/smoke_global_*.py`, `scripts/worktree-reservation` e `scripts/worktree_registry.py` idênticos. Assim somente semântica de workflow/lifecycle/recovery inalterada retém prova histórica; instalação/parser/discovery afetados receberam novas provas. Não alega novo modelo, delegação, CI ou merge hospedados.

## Verification Report: issue-77-codex-toml-r1

Skill oficial nativa `.agents/skills/openspec-verify-change/SKILL.md` invocada nesta sessão Apply, não uma revisão independente. `status`/`instructions apply` oficiais consultados no root correto; quatro artefatos legíveis e completos. Tarefa 3.2 encerrada após conferência/strict, seguida de nova leitura de progresso.

| Dimension | Status |
|---|---|
| Completeness | 8/8 tarefas; 4/4 requisitos ADDED, sem REMOVED/RENAMED |
| Correctness | 4/4 requisitos mapeados; 12/12 cenários com código/testes; nenhum check aplicável omitido |
| Coherence | D1–D5 seguidas; stdlib 3.10, parser upstream intacto, publicação A_R1/B_R1 literal; padrões existentes preservados |

| Requisito | Implementação e prova |
|---|---|
| Inspeção semântica | `scripts/install-global:369–402,737–753`: estrutura Tomli decodificada/seletores; grafias/escapes/controles em `test_codex_semantic_spellings_and_non_rule_controls` |
| Erro sem perda/vazamento | `scripts/install-global:358–402,993` antes da publicação; teste multiagente negativo e fluxos públicos, IO/limites/segredos, mesmos bytes/modos/links/active/ownership |
| Parser portátil/rastreável | `scripts/install-global:43–355`, `scripts/vendor/TOMLI.md`, READMEs; payload/hash/membros/licença/standalone/limpeza; 71 testes em Python 3.10.22 real e atual |
| Pin completo | `scripts/install.sh:6–7,59–64`, testes launcher/receitas e corrupção interna/externa; inventário missing/modified ampliado para instalador/docs; A_R1 ancestral de B_R1, ambas âncoras antigas preservadas |

**CRITICAL: 0. WARNING: 0. SUGGESTION: 0.** Todos os checks da skill passaram; pronto para Archive com sincronização solicitada. Strict oficial da change: 1/1, `issues=[]`, exit 0. Não substitui suite final pós-commit, revisão independente ou guardas vivos/merge. Disponibilidade pública após integração continua pendente por definição; nada declara a correção publicada em main.

### Archive e preparação do candidato final

Sync oficial executado inline após `instructions specs`: dois requisitos adicionados em cada uma das duas specs. Comparação exata confirmou `main_anterior + blocos_ADDED`, com título/Purpose/todos os requisitos anteriores intactos e sem headings delta. `openspec validate --specs --strict --no-interactive --json`: **12/12**.

Depois da sincronização já verificada, `openspec archive issue-77-codex-toml-r1 --yes --skip-specs --json` moveu a change para este diretório com **8/8** tarefas. O flag evita aplicar novamente deltas **já sincronizados**, não dispensa sync/validação. `openspec validate --archived --strict --no-interactive --json`: **16/16**. Archive original `2026-11-23-issue-77-native-codex/` byte-idêntico ao head de implementação anterior.

Self-review de Prepare PR/address-pr-review: R1 MUST FIX classificado VALID e corrigido; nenhuma finding independente adicional conhecida. Sem alteração da semântica de workflow, runtime, seleção, ownership ou schema; parser/guard e sua distribuição seguem o plano revisado. Changelog corrigido em Não lançado, README pt/en em paridade, sem segredos/debug/arquivos locais no commit. Nenhuma evolução independente nova qualificada. A PR81 existente será atualizada sem comentários operacionais e sem merge; revisão independente do novo HEAD permanece responsabilidade do coordenador.

Suite local obrigatória final e IDs atuais serão registrados **fora deste commit**, após todos os commits/archive/pins, no HEAD limpo exato. Qualquer novo commit exige novo gate. Provas de desenvolvimento/smokes históricos não são promovidas a final; `Proof` hospedado SKIPPED não é PASS nem gate obrigatório comprovado.
