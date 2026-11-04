# Proposta — issue #31: validar e transportar evidências de testes entre implementação e revisão

Issue: https://github.com/rocker-code/my-ai-skills/issues/31 · Milestone: https://github.com/rocker-code/my-ai-skills/milestone/1 · Auditoria: https://github.com/rocker-code/my-ai-skills/issues/31#issuecomment-6621682202

## Why

Hoje `apply-issue`, `prepare-pr`, `pr-audit` e `post-pr-audit` exigem em prosa prova local do código exato, mas não existe registro materializado nem verificação: `scripts/workflow-event` só aceita URL do GitHub ou SHA em `--evidence` e nenhum helper registra comando, seleção, fingerprint do working tree, exit code, contagens ou integridade dos relatórios. Na Rancho #432 os revisores não localizaram as provas citadas (caminhos locais de outro ambiente) e gastaram ~38 min recuperando/reexecutando testes. É preciso um registro genérico, verificável por outra sessão, que diga com precisão se a prova vale para o candidato atual.

## What Changes

- Novo helper genérico `scripts/workflow-evidence` (CLI) com biblioteca `scripts/workflow_evidence.py` (stdlib, Python 3.10+), construído sobre a API pública `code_state`/`drift_report` de `scripts/worktree_registry.py` aprovada em #35 @ `75b8740` (dependência serial rígida: implementar e mergear #35 antes do Apply de #31), que:
  - **registra** a execução de um comando de teste (local) ou um resultado hospedado (CI) num registro versionado (`schema: my-ai-skills.test-evidence/v1`) com repositório, HEAD, fingerprint do working tree, configuração e identificadores de ambiente/toolchain relevantes declarados e comparáveis, comando/seleção, runner, horários, exit code, contagens, relatórios e checksums SHA-256, além das obrigações da matriz requisito→teste que a execução prova; nomes de variáveis podem ser anotados, mas seus valores nunca são registrados/publicados;
  - emite o `evidence_id` antes de executar o comando e armazena registro e artefatos fora da árvore de trabalho, em `<git-common-dir>/ai-workflow/evidence/` (compartilhado por todas as worktrees do mesmo clone);
  - **verifica** um registro contra o candidato atual e devolve um estado explícito (`verified`, `metadata_only`, `incomplete`, `stale`, `ambiguous`, `not_applicable`) com motivo concreto, caminhos alterados inclusive alterações staged, compatibilidade do ambiente declarado e escopo de recuperação por obrigação; gates hospedados só passam após confirmação de status/HEAD/run **e do check obrigatório mapeado pela política efetiva do ramo-base** na origem confiável, para o SHA exato do candidato limpo — um manifesto importado não pode atribuir um run qualquer ao gate;
  - **exporta/importa** um pacote portátil (manifesto + artefatos + checksums) e **publica** uma projeção estritamente permitida (não o manifesto inteiro, sem logs, argv, seleção, extensões ou campos livres) num comentário estruturado oculto da issue/PR; publicação local sem artefatos resulta `metadata_only`, enquanto execução hospedada confirmada pela API pode ser `verified` sem artefato local;
  - lista e remove registros (`list`, `prune`) com retenção explícita, nunca automática.
- `scripts/workflow-event --evidence` passa a aceitar também a referência `evidence:<evidence_id>` (retrocompatível; URL/SHA continuam válidos; formato do registro de run `schema_version: 1` inalterado).
- `protocol/TEST_STRATEGY.md` e `protocol/AI_WORKFLOW.md`: a matriz requisito→código→teste ganha a coluna de prova (`evidence_id`), regras de transporte, retenção, conteúdo sensível, invalidação e precedência dos gates do projeto (tipados `local|hosted`). `templates/pull-request.md`: formato de linha da seção Validation `PASS|FAIL|NOT RUN: <obrigação> — evidence:<id> (<estado>)`.
- Skills `apply-issue`, `prepare-pr`, `pr-audit`, `post-pr-audit`, `address-pr-review`, `milestone-orchestrator` e `update-ai-workflow`: encerrar Apply com pacote acessível; conferir integridade/correspondência; distinguir prova disponível, metadados sem log e prova incompleta; reexecutar apenas a obrigação invalidada, preservando os gates finais. Arquivar/sincronizar, preparar todos os arquivos da PR e commitar antes de executar/registrar o gate local final no HEAD limpo e imutável; se HEAD mudar, refazer esse gate, sem gravar o ID no próprio commit.
- Distribuição: `scripts/sync-plugin` passa a copiar o novo helper e seus companheiros obrigatórios (`workflow_evidence.py`, `worktree_registry.py`); README.md/README.en.md (paridade) documentam instalação e uso; plugin regenerado.
- Testes de regressão T1–T5, compatibilidade de ambiente, gate após freeze do commit e projeção segura de publicação, com repositórios Git temporários e `gh` falso.

Fora do escopo (follow-up bloqueado): leitura/adaptação do registro nativo M2T. O produtor [M2T #12](https://github.com/rocker-code/m2t/issues/12) ainda não entregou nem congelou contrato versionado (`contract-handoff` design-review: CONTRACT GAP para esse cenário). Comandos M2T continuam suportados agora pelo caminho genérico (o helper envolve o comando como qualquer outro), sem acoplamento a Magento. Nenhum campo M2T é desenhado contra schema não congelado; o bloco `producer` é provisório, não validado e null/ausente nesta versão; `extensions` é genérico.

## Capabilities

### New Capabilities
- `test-evidence`: registro, armazenamento, transporte, verificação e invalidação de evidências de execução de testes vinculadas ao código testado e à matriz requisito→teste, consumidas por Apply, prepare-pr e auditorias.
- `workflow-metrics`: registro de execução do workflow por issue (comentário estruturado) e sua leitura retrocompatível, incluindo referências de evidência.

### Modified Capabilities
<!-- Nenhuma: openspec/specs/ está vazio nesta base. -->

## Impact

- Código: novo `scripts/workflow-evidence`, `scripts/workflow_evidence.py` (importa `scripts/worktree_registry.py` de #35 sem alterá-lo); ajuste pontual em `scripts/workflow-event`; `scripts/sync-plugin`; `templates/pull-request.md`.
- Documentação/protocolo: `protocol/TEST_STRATEGY.md`, `protocol/AI_WORKFLOW.md`, SKILL.md das skills citadas, README.md, README.en.md; cópias empacotadas e `plugins/my-ai-skills/**` regeneradas por `scripts/sync-plugin`.
- Testes: novo `tests/test_workflow_evidence.py`; `tests/test_workflow_metrics.py` estendido (T5).
- Dependências: nenhuma externa nova (stdlib, `git`, `gh` opcional para publicar). Dependência rígida interna: #35 mergeado (fingerprint canônico, `test_helpers_do_not_write_bytecode`).
- Coordenação (ordem serializada #35 → #31 → #32 → #33 → #34): #35 é dono do fingerprint; #32 correlaciona por `execution {kind,id}` (id = `evidence_id`) sem alterar o manifesto; #34 referencia `evidence:<id>` e o ID de obrigação; #33 edita outra seção de `TEST_STRATEGY.md`.
