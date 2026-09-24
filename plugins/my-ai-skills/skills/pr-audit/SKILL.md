---
name: pr-audit
description: Independently audit a GitHub PR against the live issue, approved OpenSpec, repository constraints, implementation and tests. Use after a PR opens or changes substantially; produce evidence-backed traceability and actionable findings without editing code.
---

# PR Audit

Use a separate reviewer session from implementation when available. Fetch live issue and decisions, pinned OpenSpec revision, PR head/base and full diff, relevant unchanged code, CI results, dependencies and review threads. Locate the approved OpenSpec change at its active path or under `openspec/changes/archive/`; when archived, inspect both preserved artifacts and synchronized live specs. Confirm archive did not alter approved behavior. Refresh after each new push. Read `../../protocol/REVIEW_POLICY.md` and applicable domain skills.

Build a compact matrix for each acceptance criterion and OpenSpec requirement: requirement → code path → proving test/check → status (met, partial, missing, unverified). Verify tests actually cover behavior, including failures, authorization, retries and compatibility where relevant. Check unexpected scope, migrations, data integrity, GraphQL/API contract, concurrency, security, dependency changes, obsolete code and unresolved feedback. Invoke `architecture-audit` when boundaries or dependencies are touched.

For each finding give severity per review policy, exact evidence at current head, impact and smallest correction. Label uncertain hypotheses as needing verification. Do not report stale/duplicate findings or invent acceptance criteria. Do not modify code, resolve threads or merge. End with `CHANGES REQUIRED`, `READY FOR FINAL REVIEW` or `UNVERIFIED — <missing evidence>`; list validations actually observed.
