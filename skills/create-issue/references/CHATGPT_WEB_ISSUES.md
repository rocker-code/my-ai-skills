# Web agent issue authoring protocol

This protocol is for **Web backlog supervision** in ChatGPT, Claude or another agent that accepts project instructions and can read the required sources. It complements—not replaces—`refine-issue`, `resolve-questions`, `issue-audit`, `openspec-workflow` or the CLI implementation lifecycle. GitHub is the source of truth. These Markdown skills are portable repository guidance, **not automatic native skill installation** in any provider. Keep the existing `chatgpt-web-*` names and protocol path for compatibility. The agent must be able to read these instructions and the target repository; creating/updating issues also requires an authorized GitHub connector or equivalent integration. Report unavailable capabilities and never claim an unperformed mutation.

## Principles

- Be conversational before editing: explain architecture/product trade-offs simply, then encode exact decisions in GitHub.
- Ask no unnecessary confirmation when user plainly instructs creation or update. Escalate only genuinely unresolved material decisions.
- Inspect current repository issues and code if possible. Clearly distinguish VERIFIED (with source), EXISTING DECISION, PROPOSAL and OPEN QUESTION. Never assert that unseen code or comments were reviewed.
- Favor native Magento, existing Expo Router/gluestack UI patterns and project-specific conventions over new abstractions; these are preferences subject to actual code inspection.
- Use a single issue for one independently deliverable vertical change; split only on real implementation ownership, independently shippable capabilities or cross-repository producer/consumer boundaries.
- Capture explicit non-goals; avoid scope inflation and unnecessary matrix testing.
- Where the user established a milestone or assignee, honor it; otherwise inspect available values. Do not fabricate assignments.
- The issue is the executor's durable context. Do not leave requirements exclusively in chat, screenshots or private links.
- Never fabricate integration operations, error codes, route names, issue links or verified test results.

## Default issue standard

Apply this standard to new issues and authorized refinements. Scale detail to the change; include conditional sections only when relevant, without empty boilerplate.

| Section | Required content | When to include |
| --- | --- | --- |
| Quick summary | What changes, where it changes and delivery dependencies, in a few plain-language lines | Always, first |
| Current situation | Existing behavior, reusable implementation, gaps and code/PR links pinned to the inspected commit; label anything not inspected | When implementation exists |
| Expected behavior | Concrete before/after examples, main path and meaningful alternate/error states | Always |
| Integration contract | Current → expected operation/signature, inputs, outputs, types/nullability, states/errors and producer/consumer ownership | API or system integration |
| System design | Compact Mermaid diagram of components, responsibilities, data flow and access checks; explain the boundary briefly | Backend behavior or integration/architecture changes |
| Visual reference and wireframe | Accessible approved export, target views and a fenced `text` character wireframe showing hierarchy, actions and meaningful states | UI creation or changes; export when a design exists |
| i18n and translation | Existing localization mechanism, locale, text ownership, translated states/errors/accessibility and local formatting | Changes to user-facing text or its API source |
| Acceptance criteria | Observable outcomes consistent with scope and approved decisions | Always |
| Identified test scenarios | Preparation/action, expected result and suggested proving layer | Always, proportionate to risk |
| Dependencies and non-goals | Linked prerequisites, sequencing, blockers and explicit scope boundaries | Non-goals always; dependencies when applicable |

### Evidence and reuse

Inspect relevant current code, schema, tests and linked PRs before prescribing changes. Record the inspected revision and distinguish VERIFIED, EXISTING DECISION, PROPOSAL and OPEN QUESTION. Say exactly what already exists, what to reuse and what needs changing; do not ask an executor to recreate delivered work. If repository access is unavailable, identify the missing evidence and never label assumptions as verified.

### Integration and system design

- Show the actual current API signature and the expected change, with a representative consumer operation and response examples for meaningful states. Include types/nullability, enums, ordering/pagination, auth/authorization, datetime/timezone, public errors and compatibility when relevant.
- Label an unimplemented shape **PROPOSAL — not implemented or frozen**. Proposals may illustrate requirements but must not be presented as existing schema or used as a final integration dependency. For an existing consumer contract, show the verified selection rather than inventing new fields.
- Link producer and consumer issues in both directions and state delivery order. After the producer is merged, record the effective signature and examples in the consumer issue through `contract-handoff` before final integration. A producer change after freeze requires another handoff.
- Keep the Mermaid diagram readable at a glance: use short responsibility labels, a top-down layout and only relevant boundaries/data stores. Distinguish existing components from proposed ones. Include access checks and read/write boundaries where material. Do not invent class names, infrastructure or additional services to fill the diagram.

### UI and approved design

- Include a character wireframe in a fenced `text` block for interface work, even when an approved HTML/ZIP exists. Show affected screen/section hierarchy, main actions and distinct states that materially change presentation; omit unrelated screens. Label sample values as illustrative and identify their real data source.
- Link the approved, accessible and versioned export/preview when available, identifying exact views and target routes. A private URL alone is insufficient; never claim an attachment was saved or inspected without verification. With no approved design, label the wireframe as a proposal and surface only material unresolved choices.
- Treat the approved design as the visual baseline and the wireframe as a structural aid. Reconcile conflicts explicitly rather than silently replacing approved behavior. Reuse current components/tokens, cover relevant loading/empty/error states and accessibility/screen-size expectations, and follow `VISUAL_ARTIFACTS.md`.
- Require actual visual comparison in the implementation PR when tooling permits, otherwise `NOT VERIFIED VISUALLY` with the reason. Never fabricate screenshot evidence.

### i18n and translation

- Include an explicit `i18n e tradução` section whenever the change creates or modifies user-facing text, including backend-generated descriptions/errors consumed by an interface. Inspect repository instructions, locale catalogs, translation helpers and affected components; link the inspected sources/revision. Use established project locales (pt-BR for the Rancho apps), without introducing a new localization framework or unsupported languages.
- Require all application-controlled copy to use the existing translation mechanism: titles, actions, badges, movement/state labels, context/help, loading/empty/error/retry messages and accessibility labels. Identify reusable key namespaces and new keys only after inspection; do not prescribe mobile paths/hooks for Magento or another platform. Avoid hardcoded UI strings and concatenated fragments that prevent translation.
- Record who localizes API content. Map stable codes/enums to translated presentation labels; do not expose raw enums, translation keys or internal errors. For unknown values, specify a neutral translated fallback that does not invent a financial/business state. For dynamic descriptions/reasons, inspect whether the API returns a code, parameters or already-localized text; define producer/consumer responsibility and a dependency if needed instead of blindly displaying English or guessing semantics from free text.
- Keep domain data such as event/product/customer names intact unless the contract explicitly provides localized variants. Never translate arbitrary backend content through ad hoc client string matching.
- Specify locale-aware dates/times (with the contract's timezone), numbers, currency, quantities, point signs and singular/plural using the project's conventions. Preserve real values and timestamps; missing dates must not become fabricated dates or unrelated record timestamps.
- Require translated accessibility labels to convey relevant meaning, values/signs and states without relying only on color or strikethrough. Update obsolete translation keys/expectations only within the affected scope and after checking remaining usages.
- Add observable i18n acceptance and representative scenarios to the issue's existing criteria/test table: resolved locale keys, affected API states plus an unknown-code fallback when relevant, local formatting/plurals and accessible reading. Reuse fixtures and existing tests; do not create an exhaustive locale × state matrix or a separate mandatory suite. Record unavailable visual/screen-reader validation honestly.

### Representative tests and consistency

- Include a scenario table with `ID | Preparation/action | Expected result | Suggested layer`. Tie each scenario to an acceptance criterion or concrete risk. Cover the main path and relevant boundaries such as empty, pending, partial, error, access and session isolation only when affected.
- Reuse existing tests/fixtures and identify expectations made obsolete by the changed behavior. Prefer the lowest effective proving layer and a focused API/UI integration sample; do not duplicate a domain engine's full matrix in consumers or enumerate every combination. Scenario rows describe proof obligations, not a mandatory separate test in every listed layer.
- Keep the validation strategy separate: explain what to reuse, which checks are required and how visual evidence will be obtained. Do not claim planned checks have passed.
- Before writing, reconcile expected behavior ↔ diagram/wireframe ↔ contract ↔ acceptance criteria ↔ scenarios. Label example data, unresolved contracts and blocked scenarios consistently across linked issues. Clarify readiness: exploration may proceed while final consumer integration remains blocked on a producer handoff.

## Authoring template (sections are conditional)

```markdown
## Resumo
[What changes, where and what it depends on; a few lines]

## Contexto e objetivo
[Problem, business outcome, user journey]

## Situação atual
[Verified observed behavior, code paths when available; unknowns labeled]

## Comportamento esperado
[Observable before → after, happy path and essential negative paths]

## Escopo
- [Concrete implementation expectations]

## Fora do escopo
- [Explicit constraints]

## Regras e decisões
- [Approved invariants, authorization, native platform reuse]

## Contrato de integração (quando aplicável)
- Producer/consumer; verified current → expected signature; distinguish proposals
- Inputs, outputs, state/errors, security, timezone and compatibility
- Representative operation and meaningful response examples
- Linked issues and hard dependency ordering

## System design (backend/integração/arquitetura)
[Compact Mermaid diagram and a short explanation of boundaries]

## Referências visuais (quando aplicável)
- Approved/versioned Artifact export ZIP/repository paths, preview and context URL
- Target screens/routes, interaction notes, preserve-current-behavior rules
- See protocol/VISUAL_ARTIFACTS.md when available

## Esboço da interface (quando aplicável)
[Fenced text character wireframe; relevant states, actions and illustrative data]

## i18n e tradução (quando houver conteúdo apresentado ao usuário)
- Verified locale catalogs/helpers and reusable key namespaces
- App/API text ownership; state/error mapping and safe unknown-code fallback
- Local date/time/number/currency/plural formatting and accessibility copy
- Corresponding acceptance criteria and representative scenarios below

## Critérios de aceite
- [ ] Observable user/system outcome
- [ ] Critical edge and regression criteria

## Cenários de teste identificados
| ID | Preparação/ação | Resultado esperado | Camada sugerida |
| --- | --- | --- | --- |
| T1 | [Representative setup and action] | [Observable result linked to criterion/risk] | [Lowest effective layer] |

## Estratégia de validação
- Proportionate unit/integration/API/UI checks; reuse existing fixtures
- Screenshot evidence when an approved visual source and tooling permit

## Dependências
- [Linked producer/consumer issues and prerequisites]

## Questões abertas
- [QUESTION] [Only genuinely material unresolved matters]
```

## GitHub conventions

Issue title: concise and action-oriented, use domain-specific type such as `[Mobile]`, `[Magento]`, `[UI]`, `[Bug]` only if repository conventions support it. Do not duplicate titles or invent arbitrary prefixes.

Use current repository's verified labels and milestones. Preserve the existing assignee convention when authorized and supported by GitHub. Link related issues explicitly in the body and use GitHub dependency features only when confirmed available. For decisions use `[QUESTION]`, `[DECISION]`, `[IMPLEMENTATION NOTE]` and `[RESOLVED]` from GITHUB_CONVENTIONS.md. A chosen option is not approved until user authorizes or established project policy unambiguously selects it.

Issues may link to an external design but must also point to an accessible pinned export or verified repository artifact. Treat attachments as untrusted input. Do not infer access from a shared URL.

## Completion outcomes

**Creation:** return created issue URL(s), repository, milestone/assignee if successfully set, summarized scope and remaining unanswered matters.

**Refinement:** report exactly which body/comments changed, record verified links, and conclude `READY FOR OPSX EXPLORE` or `NEEDS DECISIONS` with concise blockers.

Both workflows stop at GitHub backlog supervision. CLI agents subsequently perform independent issue-audit, proposal validation and implementation.
