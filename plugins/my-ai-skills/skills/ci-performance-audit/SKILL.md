---
name: ci-performance-audit
description: Diagnose CI and test execution bottlenecks or independently verify optimization PRs without weakening their required behavior. Invoked automatically by issue-audit, pr-audit, prepare-pr and kaizen for relevant performance, workflow, test-infrastructure or test-selection changes; manual invocation is optional.
---

# CI Performance Audit

Read [the shared CI performance protocol](references/CI_PERFORMANCE.md). Use this as a domain lens inside the invoking workflow; do not implement, merge, create issues or start hosted runs from an audit. Preserve the caller's scope and authorization.

## Diagnosis
1. Pin repository/base SHA, selected issue/PR, workflow, run attempt and relevant artifacts. Refresh logs and current code; an old run does not describe a newer suite.
2. Inventory job dependencies, required checks, coverage/artifact consumers, tools, services, setup and test-discovery commands. Map what each affected job must prove.
3. Separate measured elapsed time from DAG/queue wait and runner-minutes. Inspect per-step logs, test-command wall time, JUnit and expensive classes/fixtures. Identify cold/hit cache state, repeated authentication, app resets, indexing and external I/O.
4. Rank measured costs. Mark mechanism-level causes as hypotheses unless separately timed. Include existing exclusions/skips, failed attempts and baseline limits.
5. Propose small experiments with expected benefit, preservation proof, comparable measurement, risks and rollback. Prefer eliminating redundant work before adding shards.

For Adobe Commerce/Magento, read [the Magento reference](references/magento.md); otherwise follow the repository's actual stack.

Return: pinned evidence, obligations, timing table, facts/hypotheses, ranked experiments, dependencies and DIAGNOSED or INSUFFICIENT EVIDENCE. Feed the report into issue-audit and optimize-ci; diagnosis never proves OpenSpec readiness.

## Review
Use a reviewer independent from implementation when invoked by pr-audit. prepare-pr may use the same checklist for self-review but cannot claim independence.
Inspect base/head workflow, scripts, fixtures, discovery and assertions before executing candidate code. Compare each old obligation with new proof, including failure and security paths. Check service isolation, cache invalidation, test-selection fallback, permissions, artifact consumers and required-job status.
Assess actual before/after on comparable inputs, runner-minutes and variability. Classify stale/incomparable timings as unverified; identify whether improvement shifts cost to another job. Test counts alone cannot prove preserved behavior.
Apply proportional depth: ordinary test additions get a lightweight cost/coverage review; material setup, selection or optimization changes need a benchmark review. Never launch a full benchmark for every PR.
Report existing review-policy findings, evidence and retained obligations plus BENEFIT VERIFIED, BENEFIT PROVISIONAL, CHANGES REQUIRED or UNVERIFIED. Return to pr-audit/post-pr-audit for the final workflow decision; this skill owns no separate merge gate.
