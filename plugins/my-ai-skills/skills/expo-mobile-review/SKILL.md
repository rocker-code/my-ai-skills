---
name: expo-mobile-review
description: Review or guide Expo/React Native implementation decisions across routing, UI states, GraphQL contracts, forms, authentication, persistence, resilience, accessibility and E2E testability. Use as a domain checklist during issue exploration, implementation or PR review in an Expo mobile repository.
metadata:
  category: domain
  platform: expo-react-native
---

# Expo Mobile Review

Apply this domain lens inside the surrounding workflow. It does not replace issue/OpenSpec gates and does not authorize implementation.

## Inspect as relevant

- Expo Router route ownership, params, deep links and back behavior;
- screen loading, empty, error, retry, success and partial states;
- authentication boundaries, token lifecycle and SecureStore usage;
- GraphQL documents, generated types, nullability, enums, cache invalidation and contract drift;
- forms, normalization, client/server validation and submission idempotency;
- network timeout/offline/retry behavior and duplicate actions;
- local/global state ownership, stale data and optimistic updates;
- navigation after mutations and recoverability after app restart;
- accessibility labels, focus, touch targets, contrast and dynamic text;
- iOS/Android behavioral differences, keyboard/safe areas and permissions;
- design-system/component reuse and visual consistency;
- unit/component/integration/E2E testability with stable selectors.

## Review questions

- Does every remote-data screen render all meaningful states?
- Does the UI consume the final backend contract without guessing localized messages?
- Can retry or rapid taps duplicate a mutation?
- Does deselecting the last item preserve valid domain/form state?
- Are cache and navigation updated after success/failure?
- Are authentication expiry and network failure recoverable?
- Do tests verify user-visible behavior and navigation rather than implementation details?

Report only change-relevant findings using the active review severity policy.
