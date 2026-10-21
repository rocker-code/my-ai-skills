---
name: apply-issue
description: Apply a pinned, validated OpenSpec change for a GitHub issue in a fresh implementation session. Use after planning review and durable handoff; verify exact revision and gates, run /opsx-apply and targeted tests, then hand off to prepare-pr.
---

# Apply Issue

Start in a genuinely new agent session from the planning session. Rehydrate from the issue and `[DECISION]` comments, pinned OpenSpec change and commit, repository instructions and concise handoff. ai-memory may supplement this context; it is never the sole source of validation evidence or source of truth.

## Entry gate

Verify the exact issue and OpenSpec proposal/spec/design/tasks, pinned revision, review evidence and official validation result. Check the branch/worktree, current diff and merged prerequisites. If evidence is missing, the revision changed materially, a blocking decision remains or this is still the planning session, stop with a precise handoff. A proposal's existence alone does not pass the gate.

Run the repository's official `/opsx-apply` command; do not invent a substitute command. Implement only the validated contract and applicable repository invariants. If new evidence changes behavior, data, authorization, architecture or public contracts, pause the affected work, update the issue and OpenSpec, then review and validate the revised pinned contract; ask the owner only for unresolved material decisions.

## Integration test feedback loop

For a change requiring integration or API-functional coverage, use the test matrix from planning and inspect the repository's current test instructions and helpers before running anything. In Magento repositories, check the installed PHPUnit configuration, fixtures, service readiness, actual checkout mounted in the container, generated directory, Composer-restored test framework files, and whether the test database/sandbox is disposable and isolated. The worktree alone does not isolate a database or container. Follow project-specific recovery commands; never run functional fixtures against valuable development data. If safe isolation is unavailable, report the blocker instead of substituting a hosted run or silently skipping a required test.

Implement one vertical scenario at a time. Before the first expensive run, check syntax, test discovery and annotations/attributes, fixture existence and rollback ownership, DI/config/schema expectations, and assertions against the real public boundary. Review a nearby passing test and the relevant framework behavior when test setup is uncertain. Use cheap focused unit/static checks for pure rules, then run the narrowest meaningful integration class or method through the repository's supported command. Do not treat mocked unit tests as proof of persistence, transactions, GraphQL wiring or framework lifecycle.

On failure, save the exact command, first relevant exception, test/fixture and setup phase; classify it as environment/bootstrap, fixture/isolation, implementation, assertion/contract, or intermittent. Verify the cause against code/logs and change one cause at a time. For a setup failure, repair only the disposable sandbox using repository instructions; do not repeatedly rewrite application code. For an assertion failure, compare the observed behavior with the approved contract before changing either. Re-run the affected target after the fix, then broaden to the module/related suites and a different order when shared state or rollback is involved. Serialize tests sharing a sandbox, database, search index or mounted checkout. Avoid interrupting initial Magento installation and avoid blanket cleanup between successful focused runs unless the project requires it.

Before commit, run every locally required suite against the exact code and checkout to be committed, even if narrow runs passed. Preserve test cleanup, isolation, failure propagation and repository rules governing hosted heavy tests. Record PASS/FAIL/NOT RUN, commands, target revision, environment, test counts and any setup versus test failure. A missing or failed required suite blocks PR preparation when the repository says it is a commit gate; do not mark a historical or hosted result as a local pass.

Run focused tests and relevant static checks; record actual PASS/FAIL/NOT RUN with reasons. Apply `openspec-workflow` for the mandatory post-Apply closeout: complete validated tasks, verify scenarios against implementation and tests, use the official verifier when available, strictly validate, archive on this feature branch, synchronize validated live specs and inspect both archived artifacts and live specs. If verification or archive fails or changes the validated behavior, stop and follow its revision review and validation gate. Do not hand an active incomplete change to `prepare-pr`.

Then inspect the complete diff for unrelated changes, preserve unrelated user work, and pass to `prepare-pr`. End with `READY FOR PR` only when implementation, verification, archive and validation gates pass; otherwise end with `NOT READY FOR PR — <reason>`.

## Automatic CI performance routing

Read [the CI performance protocol](references/CI_PERFORMANCE.md). Automatically apply `optimize-ci` inside this fresh session for validated performance experiments. For ordinary feature changes to expensive fixtures, test discovery or CI setup, use its lightweight preservation checklist without expanding scope. Record before/after only when the validated work requires it; retain normal verification and archive gates.

## Proportionate test coverage

Read [the test strategy](references/TEST_STRATEGY.md). Implement the planned scenarios using existing fixtures and the smallest proving layer. Record the concrete reason for added coverage. Run narrow checks while correcting failures, diagnose after two attempts without progress on the same failure, and retain the final repository-required gates. Stop expanding scenarios once the agreed criteria and identified risks are proven.

Inspect existing tests for the affected behavior for redundant cases or obsolete expectations under the test strategy. Keep ordinary cleanup small and scope-bound; for a wider suite audit use a dedicated issue. Any consolidation, migration or removal needs a current-obligation → retained/replacement proof (or authoritative obsolescence evidence) map and applicable validation.
