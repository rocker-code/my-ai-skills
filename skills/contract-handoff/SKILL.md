---
name: contract-handoff
description: Validate and freeze an implemented producer-to-consumer integration contract, especially Magento GraphQL to Expo mobile. Use after producer changes are merged and before consumer implementation to compare final code/schema/tests with the consumer issue and update or propose updates without implementing the consumer.
metadata:
  category: workflow
  stage: ready
---

# Contract Handoff

Turn the producer's final implementation—not its original intention—into the consumer's authoritative contract. Do not implement consumer code.

## Inputs

Accept one or more producer issues/PRs/commits and a consumer issue. Resolve and refresh every source, including decisions and final merged code.

## Verify producer reality

Inspect final schemas, resolvers/controllers, service contracts, types, enums, nullability, serialization, errors, authorization, state behavior and producer tests. Distinguish public contract from internal implementation.

Build the contract using [the integration contract template](references/integration-contract.md):

- operations;
- inputs/outputs;
- types/enums/nullability;
- datetime format, timezone and precision;
- authentication/authorization;
- public errors and localization ownership;
- state transitions/invariants;
- compatibility/versioning;
- producer and consumer assumptions;
- contract-test evidence.

## Compare the consumer issue

Identify missing, stale or contradictory assumptions. If authorized, update the consumer issue while preserving its unrelated content; otherwise provide an exact patch/comment. Do not hide breaking changes behind implementation notes.

## Freeze rule

Declare `CONTRACT FROZEN` only when:

```text
[ ] producer changes are merged or an explicit immutable ref was selected
[ ] public contract was verified in final code/schema
[ ] producer tests/evidence were inspected
[ ] consumer issue matches the final contract
[ ] no blocking cross-repository question remains
```

If the producer contract changes afterward, explicitly revise the consumer issue and repeat the handoff.

End with `CONTRACT FROZEN` or `CONTRACT NOT READY — <reason>`.
