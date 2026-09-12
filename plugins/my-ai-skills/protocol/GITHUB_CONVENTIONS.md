# GitHub Conventions

## Discussion markers

### `[QUESTION]`

Use for a blocking product, contract or architectural ambiguity. Include context, evidence, affected behavior and concrete alternatives/trade-offs. Group related questions. Do not bury multiple independent decisions in one vague question.

### `[DECISION]`

Use for an approved answer. State the decision, resulting behavior, boundary cases, affected contracts and rejected alternative when useful. Later explicit decisions supersede earlier conflicting ones.

### `[IMPLEMENTATION NOTE]`

Use for a relevant discovery that does not require a business decision: existing framework facility, migration constraint, compatibility behavior or verified implementation detail.

### `[RESOLVED]`

Use only after the decision or correction is incorporated in the source of truth. Link or identify the spec, commit, test or code evidence.

## Refresh rule

Before continuing any issue or PR work, fetch the live issue/PR and read every comment, review and commit newer than the previous execution. Never rely only on cached chat context.

## Integration Contract section

Cross-repository issues should include, as applicable:

- GraphQL/HTTP operations;
- inputs and outputs;
- types, enums and nullability;
- datetime format, timezone and precision;
- authentication and authorization;
- public errors and localization ownership;
- state transitions and invariants;
- producer assumptions;
- consumer assumptions;
- compatibility/versioning notes.

Use `templates/github/integration-contract.md` as the starting structure.

## Pull requests

PRs should identify the issue, OpenSpec change, material decisions, behavior/contract changes, validations actually executed, explicit non-goals and remaining risks. Do not claim a skipped check passed.
