# Proposal

## Why

The established orchestrator and worktree helpers already prescribe resuming after an interrupted run, but a **new OpenCode session** has no explicit, globally discoverable recovery entrypoint for a natural request such as “continue de onde parou”. The request must trigger evidence-first recovery without trusting old chat, guessing a worktree, repeating passed gates, or stealing a running writer.

## What Changes

- Add the global `resume-workflow` skill to identify scope and reconstruct the last verified state before handing off to the existing `milestone-orchestrator`.
- Add a short routing rule in the managed global OpenCode `AGENTS.md` guidance to use the skill after interruptions.
- Cover global skill installation/discovery in the existing isolated installer test and document the user journey.
- Leave worktree reservations, event records, GitHub state, validation gates and merge permissions unchanged.

## Capabilities

### New Capabilities

- `interrupted-workflow-resume`: evidence-based safe recovery from a new OpenCode session.

### Modified Capabilities

- `global-workflow-distribution`: managed global guidance also routes natural recovery requests.

## Impact

`skills/resume-workflow/SKILL.md`, `scripts/install-global`, `tests/test_global_install.py`, `README.md`, `README.en.md`, changelog. Reuse the existing worktree and workflow protocols. No new runtime service, persisted database, UI or public API.

## Continuação da issue aberta

A PR #62 já foi incorporada: sua implementação inicial permanece válida, mas não comprova os cenários T1/T5/T7 nem arquiva/sincroniza este change. A continuação da #61 na branch/worktree `issue-61-resume-closeout` SHALL preservar o trabalho entregue, construir e executar uma prova isolada em sessões novas reais do OpenCode com modelo e com a **revisão candidata** da skill instalada, e registrar respostas e estado antes/depois. Uma PR de acompanhamento desta mesma issue SHALL conter apenas o escopo residual verificado, incluindo o OpenSpec arquivado/sincronizado; o gate final SHALL incidir sobre o HEAD limpo e exato dessa PR de acompanhamento, não sobre o HEAD histórico da #62. Não recriar a implementação inicial nem duplicar a PR incorporada.
