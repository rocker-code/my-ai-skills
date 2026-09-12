---
name: magento-review
description: Review or guide Adobe Commerce/Magento implementation decisions using framework-native conventions, module boundaries, contracts, GraphQL, persistence, scope, lifecycle, concurrency and tests. Use as a domain checklist during issue exploration, implementation or PR review in a Magento repository.
metadata:
  category: domain
  platform: adobe-commerce
---

# Magento Review

Apply this domain lens inside the surrounding workflow. It does not replace issue/OpenSpec gates and does not authorize implementation.

## Native-first rule

Before introducing an abstraction, lifecycle, status, checkout/payment flow, repository or persistence mechanism, verify whether Adobe Commerce already provides an appropriate native API or extension point. Prefer project-established patterns and framework service contracts over parallel infrastructure.

## Inspect as relevant

- module/domain ownership and dependency direction;
- DI preferences/plugins/virtual types and generated-code implications;
- service contracts, repositories, APIs and extension attributes;
- GraphQL schema, resolvers, batching, cache/identity, auth and public errors;
- ACL, Admin routes/controllers/UI components and form keys;
- declarative schema, patches, upgrade idempotency and historical data;
- store/website scope and configuration fallback;
- store timezone vs UTC persistence and serialization;
- quote/order/payment/status lifecycle and native sales APIs;
- transactions, lock order, atomicity, retries, idempotency and races;
- indexers, cache invalidation, cron/queues and operational behavior;
- backward compatibility and public contract stability;
- unit/integration/GraphQL/API tests at the correct boundary.

## Review questions

- Does the solution reuse a native Magento mechanism?
- Is business logic outside controllers/resolvers and testable?
- Are transaction and lock boundaries around the invariant, not only persistence?
- Are store scope and timezone semantics explicit?
- Are GraphQL nullability, enums and localized errors deliberate?
- Do tests prove concurrency/state/authorization failures when relevant?
- Is obsolete or duplicate mechanism removed when replacement is in scope?

Report concrete evidence and severity through the active review workflow; do not generate generic Magento warnings unrelated to the change.
