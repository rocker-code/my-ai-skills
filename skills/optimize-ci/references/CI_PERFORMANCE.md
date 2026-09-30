# CI Performance Protocol

## Automatic routing
Apply this protocol inside the existing workflow; never require the owner to invoke a performance skill manually.
- issue-audit: invoke ci-performance-audit in diagnosis mode when the issue targets CI/test speed, cost, fixtures, caching, sharding or test selection.
- implement-issue: use optimize-ci for performance issues after diagnosis. It supplies experiment requirements to the normal OpenSpec plan; it is not a second planner.
- apply-issue: use optimize-ci for validated performance work. For ordinary feature work changing expensive fixtures, discovery or CI setup, apply its preservation checklist without adding unrelated optimizations.
- prepare-pr and pr-audit: route relevant workflow/test-infrastructure changes to ci-performance-audit in review mode. An ordinary behavior test addition needs a lightweight cost/coverage check; deep benchmarking is warranted by material cost or selection/setup changes, not by every test file.
- post-pr-audit: consume the existing current-head performance review. Re-audit only invalidated evidence; do not invent a new benchmark at the final gate.
- kaizen: diagnose evidenced recurring slowdown or performance regression. Record a scoped follow-up in the existing evidence ledger; create issues, change CI or start implementation only within the selected authorization.
- milestone-orchestrator: carry these routes in worker handoffs, schedule experiments without contaminating comparisons, and reuse verified evidence.

If a selectively installed environment lacks either specialist, report that capability gap and use the visible preservation checklist within the caller. Do not claim the specialist ran or that an unverified optimization passed. Ordinary unrelated work can continue; missing required optimization evidence remains unverified. Install both specialists with the workflow bundle for complete automatic routing.

A trigger adds domain expertise to an existing stage, not a new lifecycle, approval checkpoint or mandatory hosted job. Preserve OpenSpec, fresh Apply sessions, independent review and repository merge policy.

## Preservation contract
Before optimizing, inventory the obligations of affected jobs: requirements and proving scenarios, tools and configuration, services/readiness, isolation, discovery, failure propagation, artifacts/coverage consumers, permissions and required checks. Record existing exclusions and skips instead of presenting them as new savings.
For each proposed change, map obligation -> previous proof -> new proof -> remaining uncertainty. Preserve authorization, ownership, persistence, rollback, idempotency, concurrency, migrations and public contracts when applicable.
Counts and coverage percentages are supporting signals, not equivalence proofs. Consolidation or moving a pure rule to unit tests requires equivalent behavioral assertions and retained real-boundary integration coverage. Never silently remove, skip or weaken tests, ignore errors, change failure thresholds or bypass checks for speed.
Use trusted base-branch policy to audit changes to CI policy; a PR cannot authorize its own weaker gate.
A selected-test design needs an explicit dependency map, full fallback for unknown/shared/infrastructure changes, documented complete-run policy and branch-protection compatibility. A skipped required job is not a passing check.

## Measurement and evidence
Pin baseline/candidate SHAs and run attempts. Separate workflow elapsed time, queue/DAG wait, job duration, runner-minutes, services, dependencies/cache, Magento/app setup, test-command wall time, JUnit time and teardown.
JUnit totals exclude some framework work. Wall time minus JUnit is outside-timer overhead, not pure bootstrap. Avoid double-counting nested suites.
Compare equivalent suite/requirements, runner/toolchain, dependencies, service configuration, cache state and workload. Prefer medians and spread from at least three comparable runs for durable conclusions; use existing evidence first. With fewer runs, label estimates provisional and state missing evidence. Do not trigger repeated paid/hosted runs outside authorized scope.
Benchmark one hypothesis at a time. Parallel agents may plan independently, but experiments sharing files, database/sandbox, runner resources or measured workload must be serialized or fully isolated with contention recorded.
Record cache-hit and cold/miss behavior; include restore/upload/extraction, key invalidation and setup duplicated by shards. Distinguish shorter feedback from fewer runner-minutes. A target is a goal, never a measured claim.

## Review and completion
Use the existing REVIEW_POLICY severity and merge gates. Weakened proof or broken required gates are correctness findings. A minor slowdown does not become an invented merge blocker.
For optimization acceptance, report comparable before/after, retained obligations, adopted/rejected hypotheses, cost, stability and rollback. Missing evidence means unverified benefit, not success.
After merge, compare available current runs and let kaizen record regression/follow-up. No permanent polling, scheduled automation, deployment, automatic issue creation or unrequested pipeline execution is implied.
