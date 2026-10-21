# Risk-based Test Strategy

Apply this policy automatically during planning, implementation and review. Use the smallest suite that proves the acceptance criteria and concrete risks of the change. Do not enumerate every imaginable combination, require a fixed test count or chase a coverage percentage. Preserve repository-required checks and explicit validated obligations.

## Plan sufficient coverage

Inspect existing tests and fixtures before adding new ones. Extend the existing OpenSpec evidence matrix instead of creating another artifact or approval step:

| Scenario | Acceptance criterion or concrete risk | Layer | Existing or new proving test/check |
|---|---|---|---|
| Rename a ticket and reload it | The change persists | Integration | Existing test extended |
| Rename another customer's ticket | Ownership is enforced at the API boundary | GraphQL | New test |
| Reject an invalid name | Name validation | Unit | Existing test reused |

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

## Review and stop

Review sufficiency as well as missing coverage. For any requested additional test, identify the acceptance criterion, observed regression or concrete failure that existing evidence would miss, and the smallest appropriate proving layer. A hypothetical permutation without that explanation is not a test requirement or merge blocker. Apply the existing review severity policy; do not demand every layer or reopen accepted scope at final audit.

Stop adding scenarios when acceptance criteria and identified risks have behavioral evidence, relevant assertions pass and applicable required checks pass. Report pending, failed or not-run evidence accurately; missing required proof remains unresolved. Preserve the planned matrix in the existing handoff/PR so reviewers can see both coverage and material residual uncertainty.

Never delete, skip or weaken existing tests, silently narrow discovery, reduce thresholds or bypass required checks to meet a time target. Consolidating existing coverage requires the preservation/equivalence evidence in CI_PERFORMANCE.md. Treat elapsed time as a signal to diagnose scope or setup, not as an automatic pass/fail budget. This policy adds no benchmark, fixed time limit, user command or routine approval checkpoint.
