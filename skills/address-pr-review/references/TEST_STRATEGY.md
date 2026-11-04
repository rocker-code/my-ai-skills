# Risk-based Test Strategy

Apply this policy automatically during planning, implementation and review. Use the smallest suite that proves the acceptance criteria and concrete risks of the change. Do not enumerate every imaginable combination, require a fixed test count or chase a coverage percentage. Preserve repository-required checks and explicit validated obligations.

## Plan sufficient coverage

Inspect existing tests and fixtures before adding new ones. Extend the existing OpenSpec evidence matrix instead of creating another artifact or approval step:

| Scenario | Acceptance criterion or concrete risk | Layer | Existing or new proving test/check | Evidence |
|---|---|---|---|---|
| Rename a ticket and reload it | The change persists | Integration | Existing test extended | `evidence:<id>` (`verified`/pending) |
| Rename another customer's ticket | Ownership is enforced at the API boundary | GraphQL | New test | `evidence:<id>` (`verified`/pending) |
| Reject an invalid name | Name validation | Unit | Existing test reused | `evidence:<id>` (`verified`/pending) |

Start with the main successful behavior, the relevant business rejection and risks introduced or affected by the change. A scenario may satisfy more than one obligation. Add cases for distinct behavior or failure modes; do not turn this starting point into three mandatory tests for every change. Documentation-only changes may need only documentation/package checks.

Increase depth when the changed path affects payment, authorization/ownership, sensitive data, stock, concurrency, idempotency, rollback, migrations or compatibility. State the failure being prevented and its enforcement point. Do not add unrelated cases merely because those concerns exist elsewhere in the application. Do not omit an explicit acceptance criterion because it is expensive to prove.

## Choose the proving layer

| Layer | Prove | Avoid |
|---|---|---|
| Unit | Isolated calculations, branching rules and representative boundaries | Starting Magento or a database for a pure rule |
| Integration | Real persistence, transactions, framework wiring and interactions between modules | Repeating every pure-rule permutation |
| GraphQL | Changed input/output contract, resolver wiring, authentication/ownership and public error mapping as relevant | Repeating the full service-level rule matrix |

GraphQL tests can also provide integration proof when they exercise the real affected boundary. Classify by what is proven, not by directory or label. Reuse that evidence instead of mandating another test for the same behavior. Keep separate assertions/tests when they prove a distinct boundary, such as API ownership versus service persistence. Do not mock away the boundary the test is supposed to verify.

Reuse fixtures and representative equivalence classes. Add a boundary value when it changes behavior; avoid Cartesian products of customers, products, states and inputs without evidence of an interaction risk. Test custom behavior and affected native integration, not the platform's entire standard feature set.

## Implement and diagnose

Follow the planned scenarios. Add a scenario only for a newly discovered concrete risk, regression, unmet acceptance criterion or distinct boundary; record the reason in the same matrix. Routine test selection needs no owner checkpoint. Follow the normal OpenSpec revision gate if the discovery changes the validated behavior or architecture.

Check environment readiness and fixture assumptions before an expensive run. Reuse the project's supported setup; do not build a new test harness or refactor shared infrastructure as an incidental feature task. Run the narrow failing test/scenario during corrections and the affected group after it passes. Run the repository's required full local/CI gates on the final candidate; targeted success does not replace them.

After two attempts without progress on the same failure, stop blind retries and diagnose: application defect, assertion/fixture defect or environment/setup defect. Record the failure evidence, what changed between attempts and the next hypothesis. Resume when there is a concrete corrective action or new evidence; the retry threshold is a diagnosis trigger, not permission to skip a test, weaken an assertion or declare success. Isolate out-of-scope infrastructure problems and report the precise blocker through the existing workflow.

## Review existing tests proportionately

During ordinary feature work, inspect existing tests in the affected behavior and nearby fixtures for redundancy or obsolete expectations. Record evidence-backed candidates in the same matrix. Make only small, in-scope changes with clear preservation proof; leave wider suite cleanup to a dedicated issue. Do not make every feature audit the entire repository or require a new benchmark.

For an explicitly requested suite audit, apply the existing CI performance workflow and preservation contract:

1. Reuse available timings and reports, then inventory integrated and GraphQL suites, proving behaviors, fixtures and actual runner/local commands. Separate service/dependency setup, Magento bootstrap, fixtures, test execution and teardown. Prioritize measured expensive groups; test count alone is not cost evidence.
2. Classify candidates as retain, consolidate equivalent cases, migrate isolated rules to unit tests, remove obsolete behavior, or optimize setup/fixtures. Record test/class, current obligation, current proof, replacement proof or authoritative obsolescence evidence, distinct boundary risks and expected/measured cost. A test failure or overlap in method names is not redundancy evidence.
3. Preserve unique API authorization, framework wiring, persistence, transaction, stock, concurrency and other relevant boundary assertions. Move only pure-rule variations to units and keep representative real-boundary proof. Remove obsolete tests only after checking current code, consumers and validated decisions/specs; absence of documentation is not obsolescence.
4. Change small, reviewable batches. Verify replacement behavioral assertions, isolated affected tests and the required complete suites. Check ordering/cleanup when shared fixtures change. Reuse equivalent baseline results; gather only the measurements needed to resolve uncertainty. Prefer available comparable runs and label small samples provisional rather than spending repeated hosted runs to satisfy a quota.
5. Report baseline/candidate revisions, commands, equivalent environment/cache/workload, elapsed times by phase and total, runner-minutes when available, counts/assertions/skips and the obligation-preservation map. Include new unit-test cost when moving coverage. Separate measured savings from estimates and explain remaining fixed overhead; do not claim fewer tests guarantee lower runtime.

Require an explicit, reviewed preservation map for every consolidation, migration or removal. If approved requirements still demand an obsolete scenario, reconcile those requirements through the normal validated revision process first. The policy permits evidenced suite simplification, not silent coverage reduction, test disabling, discovery exclusions or weakened quality gates. Existing CI_PERFORMANCE.md rules continue to govern optimization acceptance.

## Review and stop

Review sufficiency as well as missing coverage. For any requested additional test, identify the acceptance criterion, observed regression or concrete failure that existing evidence would miss, and the smallest appropriate proving layer. A hypothetical permutation without that explanation is not a test requirement or merge blocker. Apply the existing review severity policy; do not demand every layer or reopen accepted scope at final audit.

Stop adding scenarios when acceptance criteria and identified risks have behavioral evidence, relevant assertions pass and applicable required checks pass. Report pending, failed or not-run evidence accurately; missing required proof remains unresolved. Preserve the planned matrix in the existing handoff/PR so reviewers can see both coverage and material residual uncertainty.

Never delete, skip or weaken existing tests, silently narrow discovery, reduce thresholds or bypass required checks to meet a time target. Consolidating existing coverage requires the preservation/equivalence evidence in CI_PERFORMANCE.md. Treat elapsed time as a signal to diagnose scope or setup, not as an automatic pass/fail budget. This policy adds no benchmark, fixed time limit, user command or routine approval checkpoint.

## Evidence handoff

Where `workflow-evidence` is installed, record a focused execution with `scripts/workflow-evidence record --obligation T1:src/** --selection tests/ -- python3 -m unittest ...`. It prints an `evidence_id` before running and stores a versioned manifest and checksum-bound log under the Git common directory, shared by worktrees in the same clone. Use `list --obligation T1`, `show <id>` and `verify <id> --format json` to link matrix rows, selections, command, HEAD, indexed/working changes, declared configs, observed Python/platform and non-secret `--tool`/`--env-id` profiles. Declare outputs with `--report`, `--artifact` or `--output-dir` so generated results do not create a false concurrent-change finding. Declare relevant environment profiles with `--env-id NAME=ID`; names alone do not prove compatibility, and verify requires every declared ID again.

States: `verified` proves an accessible matching execution (only `passed` can satisfy a gate); `metadata_only` has public metadata but not a complete local proof, `incomplete` has missing/corrupt artifacts or identifiers, `ambiguous` changed during the run, `stale` differs from candidate HEAD/index/diff/config/environment, and `not_applicable` cannot satisfy that gate type. Consult JSON `reasons`, `changed_paths`, per-obligation `impact` and `recovery`; `unaffected` is informational, never approval of a stale execution. A required local gate needs a local `verified/passed` record at the exact final clean HEAD and matching fingerprint. A required hosted gate needs an exact-SHA clean candidate, API-confirmed run and independent base-branch policy/check mapping plus confirmed successful job; a hosted run cannot satisfy a local gate. Historical CI or an imported manifesto cannot grant a gate. Existing repository gates always take precedence.

Complete archive/sync, self-review, distribution and commit before recording the final required local suite. Verify the gate on the final HEAD; after **any** further commit, record and verify it again. Keep the final `evidence_id` outside the commit (handoff/PR comment). Use `export <id> --output bundle.tar.gz` and `import bundle.tar.gz` for another clone/runtime; a `/tmp` path or public comment alone is not a transferable local log. `publish <id> --issue|--pr URL` publishes only allowlisted metadata; local public metadata is `metadata_only` without the package, while hosted execution needs fresh API confirmation and still lacks a gate binding without trusted policy. Logs and reports stay local/in the package; review packages before sharing, never pass secrets as argv or profile IDs. Retention is explicit: `prune --older-than 30` previews, `--yes` removes. No automatic deletion. If the helper is unavailable, retain the existing command/result handoff and mark helper verification NOT RUN; do not weaken required tests.
