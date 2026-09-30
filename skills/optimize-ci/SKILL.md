---
name: optimize-ci
description: Guide evidence-backed CI and test-performance improvements while preserving required validation, using the existing issue/OpenSpec/apply/review flow. Invoked automatically for performance issues and relevant changes to fixtures, setup, caching, sharding or test selection; never replaces the milestone scheduler or merge gates.
---

# Optimize CI

Read [the shared CI performance protocol](references/CI_PERFORMANCE.md). Consume ci-performance-audit evidence; request diagnosis through the caller when missing. For Magento, read [the bundled Magento reference](references/magento.md).

## Planning lens
Inside implement-issue, choose one bounded experiment from the audit. Add baseline SHAs/runs, affected job obligations, hypothesis, measurement plan, success/cost limits, retained behavioral proof and rollback to the normal OpenSpec proposal/design/tasks.
Explicitly distinguish performance goals from measured guarantees. Preserve project decisions and ask only when a material scope/policy trade-off is unresolved.
Do not invoke implement-issue recursively: return the experiment contract to the current planner. Do not run Apply or change CI during planning.

## Execution lens
Inside a fresh apply-issue session, verify the pinned validated proposal and implement only its experiment. Do not invoke apply-issue recursively or skip its verification/archive gates.
Prioritize:
1. unnecessary setup for skipped/inapplicable cases;
2. smaller fixtures and repeated authentication or app work;
3. correct allocation of pure rules, persistence and HTTP contracts across test layers;
4. deterministic dependency/setup reuse and narrowly necessary compilation/indexing;
5. reviewed impact selection with full fallback;
6. isolated, duration-balanced shards when earlier evidence justifies setup duplication.

Do not assume every item is appropriate. Keep required checks and failure propagation; do not disable services, isolation or assertions without equivalent reviewed proof.
Run focused validations while iterating. On the final candidate, use applicable repository gates once and reuse only evidence allowed by existing exact-input rules. Record distinct changed inputs and expected failures on base when appropriate.
Compare before/after in equivalent environments, including cold caches, artifacts and repeated setup. Separate elapsed-time benefit from runner-minute cost. Mark insufficient samples provisional and return missing proof; never claim a hypothetical 50% gain as delivered.
If an experiment fails, record the result and revert only its scoped changes; do not force an unrelated optimization into the same validated plan.

## Ordinary feature changes
For feature work touching expensive fixtures or CI setup, apply a lightweight preservation/cost checklist. Keep any unrelated performance refactor as an evidenced follow-up; no extra hosted benchmark or separate optimization PR is mandatory.

## Handoff
Pass the normal prepare-pr/pr-audit flow: obligation -> old proof -> new proof, benchmark inputs/results, stability, cost and rollback. An implementer self-audit is not independent verification.
The existing orchestrator owns issue ordering, github-resolution owns corrections, and post-pr-audit owns merge eligibility. Return EXPERIMENT VERIFIED, EXPERIMENT PROVISIONAL or EXPERIMENT REJECTED with evidence; continue or stop under the caller's normal gates.
