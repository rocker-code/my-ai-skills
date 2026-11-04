# Proposta — issue #31: validar e transportar evidências de testes entre implementação e revisão

Issue: https://github.com/rocker-code/my-ai-skills/issues/31 · Milestone: https://github.com/rocker-code/my-ai-skills/milestone/1 · Auditoria: https://github.com/rocker-code/my-ai-skills/issues/31#issuecomment-6621682202

## Why

Hoje `apply-issue`, `prepare-pr`, `pr-audit` e `post-pr-audit` exigem em prosa prova local do código exato, mas não existe registro materializado nem verificação: `scripts/workflow-event` só aceita URL do GitHub ou SHA em `--evidence` e nenhum helper registra comando, seleção, fingerprint do working tree, exit code, contagens ou integridade dos relatórios. Na Rancho #432 os revisores não localizaram as provas citadas (caminhos locais de outro ambiente) e gastaram ~38 min recuperando/reexecutando testes. É preciso um registro genérico, verificável por outra sessão, que diga com precisão se a prova vale para o candidato atual.

## What Changes

- Novo helper genérico `scripts/workflow-evidence` (CLI) com biblioteca `scripts/workflow_evidence.py` (stdlib, Python 3.10+) que:
  - **registra** a execução de um comando de teste (local) ou um resultado hospedado (CI) num registro versionado (`schema: my-ai-skills.test-evidence/v1`) com repositório, HEAD, fingerprint do working tree e de configuração declarada, comando/seleção, runner/ambiente, horários, exit code, contagens, relatórios e checksums SHA-256, além das obrigações da matriz requisito→teste que a execução prova;
  - armazena registro e artefatos fora da árvore de trabalho, no diretório Git comum (compartilhado por todas as worktrees do mesmo clone);
  - **verifica** um registro contra o candidato atual e devolve um estado explícito (`verified`, `metadata_only`, `incomplete`, `stale`, `ambiguous`, `not_applicable`) com motivo concreto, caminhos alterados e escopo de recuperação por obrigação;
  - **exporta/importa** um pacote portátil (manifesto + artefatos + checksums) e **publica** somente metadados (sem logs) num comentário estruturado oculto da issue/PR, para outro runtime;
  - lista e remove registros (`list`, `prune`) com retenção explícita, nunca automática.
- `scripts/workflow-event --evidence` passa a aceitar também a referência `evidence:<evidence_id>` (retrocompatível; URL/SHA continuam válidos; formato do registro de run `schema_version: 1` inalterado).
- `protocol/TEST_STRATEGY.md` e `protocol/AI_WORKFLOW.md`: a matriz requisito→código→teste ganha a coluna de prova (`evidence_id`), regras de transporte, retenção, conteúdo sensível, invalidação e precedência dos gates do projeto.
- Skills `apply-issue`, `prepare-pr`, `pr-audit`, `post-pr-audit`, `address-pr-review`, `milestone-orchestrator` e `update-ai-workflow`: encerrar Apply com pacote acessível; conferir integridade/correspondência; distinguir prova disponível, metadados sem log e prova incompleta; reexecutar apenas a obrigação invalidada, preservando os gates finais.
- Distribuição: `scripts/sync-plugin` passa a copiar o novo helper; README.md/README.en.md (paridade) documentam instalação e uso; plugin regenerado.
- Testes de regressão T1–T5 com repositórios Git temporários e `gh` falso.

Fora do escopo (follow-up bloqueado): leitura/adaptação do registro nativo M2T. O produtor [M2T #12](https://github.com/rocker-code/m2t/issues/12) ainda não entregou nem congelou contrato versionado (`contract-handoff` design-review: CONTRACT GAP para esse cenário). Comandos M2T continuam suportados agora pelo caminho genérico (o helper envolve o comando como qualquer outro), sem acoplamento a Magento. Nenhum campo M2T é desenhado contra schema não congelado; o registro reserva apenas um bloco `producer` opcional e extensões.

## Capabilities

### New Capabilities
- `test-evidence`: registro, armazenamento, transporte, verificação e invalidação de evidências de execução de testes vinculadas ao código testado e à matriz requisito→teste, consumidas por Apply, prepare-pr e auditorias.
- `workflow-metrics`: registro de execução do workflow por issue (comentário estruturado) e sua leitura retrocompatível, incluindo referências de evidência.

### Modified Capabilities
<!-- Nenhuma: openspec/specs/ está vazio nesta base. -->

## Impact

- Código: novo `scripts/workflow-evidence`, `scripts/workflow_evidence.py`; ajuste pontual em `scripts/workflow-event`; `scripts/sync-plugin`.
- Documentação/protocolo: `protocol/TEST_STRATEGY.md`, `protocol/AI_WORKFLOW.md`, SKILL.md das skills citadas, README.md, README.en.md; cópias empacotadas e `plugins/my-ai-skills/**` regeneradas por `scripts/sync-plugin`.
- Testes: novo `tests/test_workflow_evidence.py`; `tests/test_workflow_metrics.py` estendido (T5).
- Dependências: nenhuma nova (stdlib, `git`, `gh` opcional para publicar).
- Coordenação: #32 (edita `workflow-event`/`workflow_metrics.py` e correlaciona execuções) e #34 (tentativas/hipóteses) estendem este registro via `correlation`/`extensions`; #35 pode reutilizar a função de fingerprint; #33 edita `TEST_STRATEGY.md` em seção distinta.
