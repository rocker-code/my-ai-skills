# Proposal

## Why

`protocol/TEST_STRATEGY.md` já manda diagnosticar após duas tentativas sem progresso, e `apply-issue` já classifica falhas, mas tudo é prosa sem registro nem verificação: no milestone 31 o mesmo teste focal rodou cinco vezes sem evidência nova e o Apply declarou contradição de contrato lendo `showInStore` do grupo como se fosse do campo (issue [#34](https://github.com/rocker-code/my-ai-skills/issues/34)). Falta um registro curto e verificável que torne o limite de tentativas e o diagnóstico de bloqueio observáveis por executores e revisores.

## What Changes

- Definir um **registro de tentativas** (attempt log) curto, embutido no handoff existente (seção de validação do PR/handoff do Apply), com alvo/falha, obrigação, assinatura, classificação, hipótese, mudança entre tentativas, resultado e evidência nova — sem novo documento, etapa ou aprovação.
- Colocar o bloco opcional após as linhas de obrigação de #31 na seção Validation; usar o mesmo ID de obrigação da matriz e `evidence:<evidence_id>` para execuções registradas por `workflow-evidence` (senão URL GitHub ou SHA), sem ler o schema/manifesto nem duplicar o raciocínio em `extensions`. Rejeitar caminhos absolutos/temporários ou `path#Lnn` como evidência de execução; caminhos relativos com linha servem só para citar código/definições.
- Agrupar falhas por **assinatura + obrigação**, de modo que renomear comando ou trocar filtro incidental não reinicie a contagem.
- Exigir **diagnóstico registrado** após duas tentativas equivalentes sem progresso, antes de nova tentativa: fase/escopo/lifecycle/consumidores efetivos, prova de runtime quando relevante, alternativa mais simples compatível com o contrato e hipótese diferente.
- Exigir que toda nova tentativa declare hipótese nova ou, se repetir a hipótese, resuma a observação que mudou desde a anterior e cite evidência nova dessa mudança. Um ID novo com assinatura e efeito observado normalizados iguais não basta; efeito observado realmente diferente, mesmo na mesma classe de falha, não é rejeitado em bloco.
- Exigir, para alegar **contradição de contrato**, citação da definição exata, campo e escopo, separação observação × inferência e confirmação da leitura; citar um elemento ancestral (grupo) no lugar do campo é rejeitado.
- Acionar **replanejamento OpenSpec** apenas com divergência comprovada (alegação aceita), pelo gate de revisão existente.
- Garantir que a terceira tentativa do episódio ininterrupto, qualquer que seja o resultado pretendido, só ocorra após o diagnóstico das duas falhas; o limite dispara investigação e **nunca vira aprovação**. Episódio **ativo** com falha pendente ou bloqueio válido (classificação estruturalmente correta, mas obrigação não aprovada) bloqueia `prepare-pr` no `--final` com estado/exit de não aprovação.
- Corrigir o ciclo de vida de tentativas na mesma obrigação: assinatura diferente marca o episódio falho anterior como **histórico/progredido, nunca aprovado**; só o episódio ativo pode satisfazer o gate final. Retorno à assinatura anterior começa novo episódio e nova sequência de falhas, mantendo o histórico. Falha de ambiente não resolvida mantém o foco mesmo com tentativas intermediárias; apenas sucesso posterior na obrigação ou diagnóstico de reclassificação com prova nova de runtime libera edição de aplicação.
- Exigir que relato de bloqueio diferencie **impedimento técnico**, **falta de capacidade** e **decisão de negócio**, mapeando para os estados existentes do orquestrador (`BLOCKED`, `RESOURCE_QUEUED`, `NEEDS_INPUT`) e as razões de espera de #32 (`environment`/`dependency`/`external`, `runtime_capacity`, `owner_input`).
- Adicionar um helper determinístico (`scripts/attempt-log` + `scripts/attempt_log.py`, stdlib Python) que valida o bloco sem produzir bytecode, com testes `unittest` e fixtures de simulação T1–T4; distribuí-lo via `scripts/sync-plugin` e instruções de instalação existentes.
- Atualizar `TEST_STRATEGY.md` (fonte única do formato), `apply-issue`, `prepare-pr`, `milestone-orchestrator`, `AI_WORKFLOW.md`, template de PR e READMEs (pt-BR/en em paridade).

## Capabilities

### Modified Capabilities

- `retry-diagnosis`: revisa o ciclo de vida do registro e o foco de ambiente já sincronizados pela implementação inicial de #34. A change original, arquivada após Apply, foi **reativada no mesmo path lógico** para correção do PR #41; nenhuma change duplicada foi criada. Re-arquivar e sincronizar a live spec somente após correção, testes e validação estrita. A versão live atual continua descrevendo o comportamento implementado no HEAD antigo até esse gate.

## Impact

- Correção agora: `scripts/attempt_log.py`, `tests/test_attempt_log.py` (fixtures se úteis), `protocol/TEST_STRATEGY.md` (seção "Implement and diagnose"), cópias geradas em `skills/*/references/` e `plugins/my-ai-skills/` via `scripts/sync-plugin`. Conferir `skills/apply-issue/SKILL.md` e `skills/prepare-pr/SKILL.md` por linguagem incompatível; mudar só se necessário.
- A implementação inicial já entregou CLI, template, READMEs e distribuição; a correção não cria helper/schema/dependência nem altera autorização ou dados sensíveis. As dependências serializadas #35 → #31 → #32 → #33 já foram mergeadas na base `07c080e`; ver design.md D1/D8.

## Correção pós-auditoria de PR #41

As duas auditorias independentes do HEAD `86bcc5669b670cb3f29545b3008236df865072a3` identificaram: A falha → B diferente progride → B passa ainda bloqueia o gate final por A pendente; A reaparecendo herda sequência obsoleta; o guard de ambiente olha apenas a tentativa imediatamente anterior, bloqueando após sucesso ou sendo contornado por tentativa intermediária. AC1/AC5 e T1/T4 sustentam a correção sem decisão de produto nova: **progresso não é aprovação da falha antiga**, e falha atual genuinamente pendente não passa. O verificador continua estrutural e revisor confere a verdade da evidência. A correção altera `scripts/attempt_log.py`, testes/fixtures e a descrição na fonte única `protocol/TEST_STRATEGY.md` (cópias geradas via `scripts/sync-plugin`); sem novo formato, helper, etapa ou manifesto.
