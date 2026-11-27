# Spec Delta

## MODIFIED Requirements

### Requirement: Registro versionado de execução
O helper SHALL produzir manifesto `my-ai-skills.test-evidence/v1` com evidence_id único, repositório, HEAD/fingerprint, seleção, cwd relativo, runner/ambiente, início/fim UTC ISO-8601, contagens, artefatos e obrigações. A identidade e conclusão SHALL seguir execution_mode: subprocess/legado preserva argv e exit OS originais; fase local usa callable e conclusão tipada, nunca exit OS fictício.

#### Scenario: Comando local registrado
- **WHEN** o implementador registra `python3 -m unittest discover -s tests` com obrigações `T1,T2` e seleção `tests/`
- **THEN** o manifesto contém os campos obrigatórios, o exit code original do comando, o log de saída como artefato com SHA-256 e o helper termina com o mesmo exit code do comando

#### Scenario: Relatório JUnit presente
- **WHEN** a execução declara um relatório JUnit existente
- **THEN** o relatório é copiado como artefato com checksum e as contagens (testes, falhas, erros, ignorados) são extraídas dele com a origem `junit`

#### Scenario: Relatório declarado ausente
- **WHEN** a execução declara um relatório que não existe ao término
- **THEN** o manifesto registra o artefato como `missing` e o registro não pode ser verificado como prova completa

#### Scenario: Identidade de fase não representa um subprocesso
- **WHEN** uma fase é registrada por chamada efetiva no mesmo processo
- **THEN** schema privado v1/kind=local são preservados, execution_mode na raiz é inprocess-phase, command.argv e exit_code são null; command.cwd é relativo e command.callable contém path relativo rastreado, qualname e SHA-256 da fonte efetivamente chamada; phase_identity na raiz contém controller_pid/controller_start reais e execution_id local não secreto; fingerprints/config/ambiente continuam vinculados ao candidato, sem native session ou comando/exit inventados

### Requirement: Prova incompleta ou inacessível permanece não verificada
Campos obrigatórios/conclusão desconhecidos, interrupção, artefato ausente ou checksum divergente SHALL resultar em incomplete ou metadata_only, nunca aprovação. Subprocess com exit desconhecido permanece incomplete. Fase exige phase_completion conhecida/finalizada e exit_code=null por definição, sem interpretar null como sucesso ou fabricar zero.

#### Scenario: Log ausente (T3)
- **WHEN** o log de saída do registro foi removido
- **THEN** o estado é `incomplete` com o artefato faltante e a obrigação a recuperar

#### Scenario: Execução interrompida
- **WHEN** o comando registrado é interrompido antes de terminar
- **THEN** o manifesto registra a interrupção e o estado é `incomplete`

#### Scenario: Fase sem conclusão conhecida ou finalização íntegra
- **WHEN** a fase lança exceção, é interrompida, tem retorno não suportado, perde conclusão ou falha ao finalizar log/artefatos/fingerprint
- **THEN** phase_completion não declara retorno verificado; result é null e verify retorna incomplete, mesmo que status textual alegue passed; o resultado nativo falho observado continua preservado nos artefatos e não recebe exit OS fabricado

### Requirement: Pacote portátil com integridade
O helper SHALL exportar um registro como pacote único (manifesto, artefatos e checksums) e importar/verificar esse pacote em outro diretório ou runtime, rejeitando conteúdo cujo checksum diverja ou cujo caminho escape do pacote. Transporte de fase MUST preservar seu modo e conclusão tipada sem normalização para subprocess.

#### Scenario: Importação em outro runtime (T1)
- **WHEN** o pacote exportado é importado num clone diferente com o mesmo código
- **THEN** a verificação retorna `verified` e os artefatos ficam acessíveis localmente

#### Scenario: Pacote adulterado (T3)
- **WHEN** um artefato do pacote tem checksum divergente do manifesto
- **THEN** a verificação retorna `incomplete` citando o artefato e o escopo de recuperação

#### Scenario: Roundtrip de fase preserva semântica e campos opacos
- **WHEN** um pacote de fase suportado é exportado/importado/reexportado
- **THEN** execution_mode, command.callable, phase_identity, phase_completion e marcador de modo/identidade no log são preservados e confrontados; unknown extensions legadas neutras são preservadas sem ganhar semântica de execução; modo/combinação desconhecidos ou inconsistentes são recusados, nunca convertidos em argv/exit de subprocess

### Requirement: Publicação de metadados sem conteúdo sensível
A publicação SHALL construir projeção pública por allowlist fechada por modo, não serializar manifesto privado, com schema público v1 e idempotência por evidence_id. Campos publicados inválidos MUST ser rejeitados; demais chaves/strings livres omitidas. Logs, relatórios, valores de ambiente e hashes de segredos MUST NOT ser publicados. Argv sensível de subprocess permanece mascarado; fase não recebe argv fictício.

#### Scenario: Metadados publicados
- **WHEN** o implementador publica um registro subprocess/legado ou hosted numa issue
- **THEN** existe um único comentário com projeção `my-ai-skills.test-evidence-public/v1` contendo somente `schema`, `evidence_id`, `kind`, `repository` owner/repo, `code.head` SHA, `status` e, apenas para hosted, `hosted.run_id` decimal e URL canônica `https://github.com/<owner>/<repo>/actions/runs/<run_id>` sem query/fragment/userinfo; republicar atualiza o mesmo comentário

#### Scenario: Segredo no comando
- **WHEN** o argv contém `--token=abc123`
- **THEN** o manifesto armazenado contém o valor mascarado e a projeção publicada não contém argv

#### Scenario: Strings livres e extensões no manifesto
- **WHEN** seleção, ferramenta declarada, extensions e chave desconhecida contêm strings que não devem sair do runtime
- **THEN** nenhuma delas nem `command`, `obligations`, `runner`, `config_paths`, fingerprints/digests, `producer`, `correlation`, `artifacts`, logs ou relatórios aparece no comentário, mesmo que o manifesto privado preserve esses campos; campos incluídos malformados impedem publicação

#### Scenario: Projeção de fase não apaga o modo
- **WHEN** metadados públicos de fase são produzidos
- **THEN** a allowlist contém somente schema público v1/evidence_id/kind=local/repository/code.head/status e execution_mode=inprocess-phase na raiz; não contém phase_identity/phase_completion/command/artefatos; sem pacote local permanece metadata_only e não satisfaz gate, mesmo com status=passed; modo omitido ou inconsistente é recusado, não downgrade silencioso

### Requirement: Precedência dos gates do repositório
Gates obrigatórios SHALL ser local ou hosted. Local exige subprocess local verified/passed no HEAD/fingerprint finais; hosted exige candidato limpo no SHA exato, origem confirmada e vínculo da obrigação ao check da política efetiva do ramo-base. Fase inprocess MUST NOT declarar/satisfazer nenhum desses gates. Projeção/import não criam vínculo; hosted não satisfaz local e unaffected não aprova gate.

#### Scenario: CI antigo para gate local (AC5)
- **WHEN** existe apenas um resultado hospedado aprovado e a obrigação é um gate `local` obrigatório
- **THEN** a verificação retorna `not_applicable` para essa obrigação e ela permanece pendente

#### Scenario: CI do candidato exato para gate hospedado
- **WHEN** a obrigação é um gate `hosted`, a política efetiva do ramo-base a vincula a um workflow/check obrigatório e a API confirma que o job/check desse run passou no SHA do candidato limpo
- **THEN** a verificação retorna `verified` para essa obrigação

#### Scenario: Run não relacionado no mesmo SHA
- **WHEN** um manifesto importado atribui a obrigação a um run bem-sucedido no SHA correto, mas o workflow/check do run não é o mapeado pela política efetiva do ramo-base
- **THEN** a execução pode estar confirmada, mas a obrigação permanece pendente; o manifesto não cria nem altera o vínculo do gate

#### Scenario: Execução hospedada confirmada sem vínculo à obrigação
- **WHEN** a execução hosted publicada é confirmada pela API mas não há política/mapeamento confiável ou job/check específico confirmado que a associe ao gate
- **THEN** a execução é `verified`, mas a obrigação permanece pendente

#### Scenario: Resultado hospedado não confirmável
- **WHEN** apenas metadados de um resultado hospedado estão disponíveis e sua origem/status não podem ser conferidos
- **THEN** o estado permanece `metadata_only` e o gate `hosted` continua pendente

#### Scenario: CI de outro SHA para gate hospedado
- **WHEN** a obrigação é um gate `hosted` e o registro hospedado tem `head` diferente do candidato
- **THEN** a verificação retorna `stale` e a obrigação permanece pendente

#### Scenario: Gate obrigatório após mudança fora do escopo
- **WHEN** um gate obrigatório foi registrado e o candidato altera um caminho fora dos caminhos relevantes declarados
- **THEN** a obrigação continua exigindo nova execução

#### Scenario: Archive e prepare-pr alteram HEAD após uma suíte anterior
- **WHEN** archive/sync ou alterações de prepare-pr são commitados após um teste anterior, mesmo sem mudança do código de produção
- **THEN** o gate local final anterior é `stale`; a suíte final SHALL ser executada/registrada novamente no HEAD limpo após o último commit e verificada antes de PASS

#### Scenario: Commit posterior ao gate final
- **WHEN** qualquer commit muda HEAD depois da suíte final, inclusive correção de PR ou alteração de template/artefato OpenSpec
- **THEN** o gate final não é reutilizado e SHALL ser reexecutado e registrado no novo HEAD; o `evidence_id` fica fora do commit para evitar ciclo

#### Scenario: Fase não pode se promover a gate
- **WHEN** produtor, pacote privado ou transporte declara required_gate local ou hosted para fase, inclusive junto de subprocess/hosted incompatível
- **THEN** gravação/import/export rejeitam a combinação e verify retorna incomplete por identidade inválida, não aprovação; consumidor que pede gate a projeção de fase recebe not_applicable e mantém gate pendente, sem converter fase em subprocess/hosted

## ADDED Requirements

### Requirement: Conclusão tipada de fase local
Fase SHALL declarar phase_completion fechado com state, return_kind, return_code, result, finalized e error_code. Somente retorno normal conhecido/finalizado e evidência íntegra permite verified. Resultado MUST vir dessa conclusão, nunca de exit_code, status textual isolado ou retorno ausente presumido None. Regras de código/configuração/ambiente/artefatos permanecem obrigatórias.

#### Scenario: Retorno normal e falha explícita não são exits OS
- **WHEN** callable retorna normalmente None ou inteiro não bool
- **THEN** state=returned; None usa return_kind=none/return_code=null/result=passed, inteiro usa return_kind=int/return_code original e result=passed se0 ou failed se nãozero; finalized=true e status raiz coerente passed/failed, finished_at/fingerprint_after e log/artefatos íntegros permitem verified/passed ou verified/failed; exit_code permanece null em ambos

#### Scenario: Estados sem retorno conhecido falham fechados
- **WHEN** state é running, raised, interrupted, finalization_failed ou unknown
- **THEN** return_kind/return_code/result são null e finalized=false; status é running para running e interrupted nos demais; error_code é null em running, null ou phase_exception em raised, null ou phase_interrupted em interrupted, null ou phase_finalize_failed em finalization_failed, null/phase_unknown/unsupported_return em unknown; returned exige error_code=null; verify retorna incomplete sem interpretar finished_at como retorno normal

#### Scenario: Campos de conclusão contraditórios são inválidos
- **WHEN** bool é usado como retorno inteiro, falta campo, há campo desconhecido no objeto fechado, result/status/return_code/finalized se contradizem ou fase tem exit_code não null
- **THEN** verify retorna incomplete por esquema inválido e import/export recusam a combinação; nenhuma coerção, preenchimento zero ou normalização de estado concede sucesso

### Requirement: Discriminação e compatibilidade fail-closed
execution_mode SHALL ficar na raiz: ausente em legado local significa subprocess; subprocess explícito mantém a mesma semântica. Fase exige inprocess-phase e seus campos reservados; hosted não usa execution_mode nem campos de fase. Modo desconhecido ou contraditório MUST falhar fechado. Campo/extensão opacos preservados não podem esconder/alterar identidade de execução.

#### Scenario: Registros existentes continuam sendo subprocess ou hosted
- **WHEN** um registro legado sem execution_mode é lido ou um subprocess é registrado explicitamente
- **THEN** argv e exit OS originais e estados/gates atuais são mantidos; ausência de modo não permite phase_completion, phase_identity ou command.callable; hosted mantém origem/política API e recusa campos de fase; unknown extensions neutras continuam preservadas em leitura/reescrita/transporte

#### Scenario: Leitor sem suporte não interpreta fase como OS success
- **WHEN** pacote fase com exit_code=null chega a leitor legado que exige exit conhecido, ou projeção com execution_mode chega a leitor de allowlist antiga
- **THEN** a execução permanece incomplete ou não verificada, nunca subprocess passed; leitor pode reter pacote opaco sem promover sua prova; implementação nova precisa preservar esse fail-closed, sem sintetizar exit0 para interoperar

#### Scenario: Downgrade parcial é detectado
- **WHEN** execution_mode é removido/trocado mas campos de fase ou marcador de modo/identidade/evidence_id do log ainda indicam fase, ou command/exit/projeção contradizem a identidade
- **THEN** gravação/import/export recusam e verify retorna incomplete; manifesto e marcador obrigatório do log são confrontados; checksums preservam integridade, não constituem assinatura contra host malicioso que reescreve coerentemente todos os bytes

### Requirement: Artefatos de fase não incluem material de autenticação
Registro de fase SHALL iniciar somente após auth e confirmação autorizadas e reter log/artefatos não secretos allowlisted. MUST NOT copiar/hash/serializar DB/WAL/SHM, consultar material auth ou reter tokens/codes/raw auth logs/IDs pessoais. Projeção nativa read-only de campos não secretos já permitidos não autoriza acesso a credenciais ou leitura do DB inteiro. Metadata não substitui eventos nativos reais.

#### Scenario: Fase e bundle excluem auth sem descartar fatos nativos
- **WHEN** o controlador registra a fase e exporta/importa o pacote suportado
- **THEN** manifesto/lista de membros são validados antes de payload, sem varredura recursiva de perfil/store; log estruturado e eventos/session/terminal/catalog/source/guard/snapshots exigidos permanecem checksum-bound, mas sentinelas auth, DB/WAL/SHM e raw auth logs nunca são retidos/copied/hasheados; pacote inválido é recusado antes do conteúdo proibido, sem modificar os formatos legacy suportados
