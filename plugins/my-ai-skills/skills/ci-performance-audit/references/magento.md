# Magento CI performance reference

- Read the project's installed framework and actual PHPUnit configuration, not assumptions about another Magento version.
- Separate integration sandbox installation from callbacks, fixtures, application/DB isolation and final teardown. Test-command minus JUnit is an overhead proxy, not a sandbox timer.
- Inspect AbstractBackendController setup and inherited skipped ACL methods; skipped cases can still authenticate and build fixtures. Preserve explicit ACL scenarios.
- Keep controllers/resolvers thin: pure validation matrices may belong in unit tests, while real persistence, rollback, constraints and controller/API wiring still need integration proof.
- Scope fixtures to the scenario. Reuse authentication only where login/token lifecycle is not under test, and never share mutable state across independent cases without verified reset.
- Do not disable Magento subscribers, app/DB isolation or TESTS_CLEANUP globally for speed. Verify changed fixtures individually, as a suite and in another order when shared state is touched.
- Isolated worktrees do not isolate databases, OpenSearch indices or filesystem sandboxes. Shards require distinct resources.
- Functional GraphQL tests exercise HTTP against a running app; retain representative tokens, Store headers, public errors and output shapes. They do not prove the mobile UI or live external providers.
- Measure dump import, config import, upgrade, DI compile, reindex and HTTP readiness separately. Removing compile or narrowing indexes is an experiment requiring environment-clean and relevant schema/config proof.
- Composer plugins may install files outside vendor and overwrite tracked test configurations. Cache/artifact proposals must preserve those files and restore repository-owned configuration, with lock/PHP/OS/plugin inputs in invalidation.
- Never reuse a production dump, secrets or production service endpoints for benchmarks. A cached test database/sandbox requires an explicit reviewed design covering schema/patch/config invalidation and clean-state equivalence; do not introduce it opportunistically.
