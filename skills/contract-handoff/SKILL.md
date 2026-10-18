---
name: contract-handoff
description: Review a producer-to-consumer contract during discovery and freeze it against final producer code before consumer implementation, especially Magento GraphQL to Expo mobile. Use for cross-repository issues where user-visible behavior depends on a backend or other system contract.
metadata:
  category: workflow
  stage: ready
---

# Contract Handoff

Prevent consumer work from depending on an implicit, incomplete, or unverified producer contract. This skill has two modes: design review before a dependent proposal is released, and final freeze after producer delivery. Never implement consumer code.

## Inputs and mode

Accept producer issue/PR/commit(s), consumer issue, and available wireframes, requirements, decisions, code/schema, tests, and OpenSpec artifacts.

- Design review: producer capability is pending, incomplete, or not yet merged. Define the contract required by consumer scenarios, compare it with current producer reality, identify the exact producer gap, and record a hard dependency. This is not a contract freeze.
- Final freeze: producer implementation is merged or pinned to an immutable ref. Verify the final public contract and consumer issue against that implementation.

Infer the mode from evidence; state it explicitly. If the consumer, producer, or scenario source is ambiguous, report the ambiguity and do not claim readiness.

## Scenario-to-contract traceability

For every relevant consumer behavior, map:

| Consumer scenario / requirement | Producer operation and fields | State and domain error | Validation point | Evidence / gap |
|---|---|---|---|---|

Include normal, empty, stale, conflicting, concurrent, unauthorized, unavailable, and partial-failure cases where applicable. Use concrete scenarios from wireframes and approved decisions; do not invent product behavior. For each scenario verify the consumer can receive enough authoritative information to render the correct state and the producer enforces the same invariant at the command/commit boundary.

Inspect final schemas, resolvers/controllers, service contracts, types, enums, nullability, serialization, errors, authorization, state behavior and producer tests. Distinguish public contract from internal implementation. Build the contract using the integration contract template, covering:

- operations, inputs, outputs, types/enums/nullability, pagination and identifiers;
- datetime format, timezone and precision;
- authentication, authorization and resource ownership;
- public domain errors, stable codes and localization ownership;
- state transitions, invariants, reservations/locking and transaction boundaries;
- stale reads, retries, idempotency, concurrency and partial failure;
- compatibility/versioning and rollout order;
- producer and consumer assumptions;
- contract-test evidence.

Do not treat a UI mock, prose promise, internal field, or issue description as proof that a public contract exists.

## Design review result

A design review is ready to release a consumer proposal only when:

- producer changes are merged or an immutable producer ref was selected;
- each in-scope scenario maps to the producer's delivered public operation/state/error and enforcement point;
- producer and consumer issue links express the dependency and delivery order;
- no material product or architecture decision is unresolved.

If the capability is missing, only planned in an open issue, or only implicit, report CONTRACT GAP with the exact scenario, missing contract behavior, producer issue to create/update, and affected consumer scope. Do not mark the dependent issue proposal-ready. The orchestrator may continue independent producer or unrelated work.

## Final freeze rule

Declare CONTRACT FROZEN only when:

    [ ] producer changes are merged or an explicit immutable ref was selected
    [ ] public contract was verified in final code/schema
    [ ] producer tests/evidence were inspected
    [ ] every in-scope consumer scenario maps to the final contract
    [ ] consumer issue matches the final contract and links the producer dependency
    [ ] no blocking cross-repository question remains

If producer behavior or schema changes after freeze, explicitly revise the consumer issue and repeat the handoff before continuing consumer implementation.

End with exactly one applicable result:

    CONTRACT GAP — <scenario and missing producer capability>
    CONTRACT DESIGN READY — <producer/consumer refs and evidence>
    CONTRACT FROZEN — <producer immutable ref and evidence>
    CONTRACT NOT READY — <reason>
