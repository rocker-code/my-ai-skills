# Proposal

## Why

`protocol/TEST_STRATEGY.md` já manda diagnosticar após duas tentativas sem progresso, e `apply-issue` já classifica falhas, mas tudo é prosa sem registro nem verificação: no milestone 31 o mesmo teste focal rodou cinco vezes sem evidência nova e o Apply declarou contradição de contrato lendo `showInStore` do grupo como se fosse do campo (issue [#34](https://github.com/rocker-code/my-ai-skills/issues/34)). Falta um registro curto e verificável que torne o limite de tentativas e o diagnóstico de bloqueio observáveis por executores e revisores.

## What Changes

- Definir um **registro de tentativas** (attempt log) curto, embutido no handoff existente (seção de validação do PR/handoff do Apply), com alvo/falha, obrigação, assinatura, classificação, hipótese, mudança entre tentativas, resultado e evidência nova — sem novo documento, etapa ou aprovação.
- Colocar o bloco opcional após as linhas de obrigação de #31 na seção Validation; usar o mesmo ID de obrigação (`obligations[].id`) e `evidence:<evidence_id>` para execuções registradas por `workflow-evidence` (senão URL GitHub ou SHA), sem ler o manifesto nem duplicar o raciocínio em `extensions`. Rejeitar caminhos absolutos/temporários ou `path#Lnn` como evidência de execução; caminhos relativos com linha servem só para citar código/definições.
- Agrupar falhas por **assinatura + obrigação**, de modo que renomear comando ou trocar filtro incidental não reinicie a contagem.
- Exigir **diagnóstico registrado** após duas tentativas equivalentes sem progresso, antes de nova tentativa: fase/escopo/lifecycle/consumidores efetivos, prova de runtime quando relevante, alternativa mais simples compatível com o contrato e hipótese diferente.
- Exigir que toda nova tentativa declare a evidência que mudou ou a hipótese nova; repetir hipótese sem evidência nova é violação.
- Exigir, para alegar **contradição de contrato**, citação da definição exata, campo e escopo, separação observação × inferência e confirmação da leitura; citar um elemento ancestral (grupo) no lugar do campo é rejeitado.
- Acionar **replanejamento OpenSpec** apenas com divergência comprovada (alegação aceita), pelo gate de revisão existente.
- Garantir que o limite dispara investigação e **nunca vira aprovação**: grupo com falha pendente permanece não resolvido e bloqueia `prepare-pr` como já faz um gate falho.
- Exigir que relato de bloqueio diferencie **impedimento técnico**, **falta de capacidade** e **decisão de negócio**, mapeando para os estados existentes do orquestrador (`BLOCKED`, `RESOURCE_QUEUED`, `NEEDS_INPUT`) e as razões de espera de #32 (`environment`/`dependency`/`external`, `runtime_capacity`, `owner_input`).
- Adicionar um helper determinístico (`scripts/attempt-log` + `scripts/attempt_log.py`, stdlib Python) que valida o bloco sem produzir bytecode, com testes `unittest` e fixtures de simulação T1–T4; distribuí-lo via `scripts/sync-plugin` e instruções de instalação existentes.
- Atualizar `TEST_STRATEGY.md` (fonte única do formato), `apply-issue`, `prepare-pr`, `milestone-orchestrator`, `AI_WORKFLOW.md`, template de PR e READMEs (pt-BR/en em paridade).

## Capabilities

### New Capabilities

- `retry-diagnosis`: registro de tentativas por assinatura/obrigação, gatilho de diagnóstico após tentativas sem progresso, prova exigida para alegar contradição de contrato, gatilho de replanejamento e classificação de bloqueios no workflow.

### Modified Capabilities

(nenhuma — `openspec/specs/` está vazio)

## Impact

- Protocolo/skills: `protocol/TEST_STRATEGY.md` (apenas "Implement and diagnose"), `protocol/AI_WORKFLOW.md`, `skills/apply-issue/SKILL.md` (parágrafo "On failure…"), `skills/prepare-pr/SKILL.md`, `skills/milestone-orchestrator/SKILL.md` (linha "Exceptional states"), `skills/update-ai-workflow/SKILL.md`, `templates/pull-request.md` (sem reestruturar Validation), `README.md`, `README.en.md`.
- Novos: `scripts/attempt-log`, `scripts/attempt_log.py`, `tests/test_attempt_log.py`, `tests/fixtures/attempt_log/*.json`.
- Distribuição: `scripts/sync-plugin` (entrada própria no loop de helpers e `install -m 0644` para o módulo); cópias regeneradas em `skills/*/references/` e `plugins/my-ai-skills/`. Teste de #35 `test_helpers_do_not_write_bytecode` cobre o helper novo por descoberta da lista de `sync-plugin`.
- Sem dependência externa nova, sem dados sensíveis, sem mudança de autorização ou acoplamento ao schema de #31/M2T. **Apply serializado** após #35 → #31 → #32 → #33: só iniciar após seus merges e rebase; ver design.md D1/D7.
