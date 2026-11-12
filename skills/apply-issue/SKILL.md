---
name: apply-issue
description: Apply a pinned, validated OpenSpec change for a GitHub issue in a fresh implementation session. Use after planning review and durable handoff; verify exact revision and gates, run /opsx-apply and targeted tests, then hand off to prepare-pr.
---

# Apply Issue

For global installations, resolve `scripts/<helper>` against
`"${XDG_DATA_HOME:-$HOME/.local/share}/my-ai-skills/active/scripts/<helper>"`.
Run from the actual checkout, quote paths, and pass `--path`/`--repository`
where applicable. Do not require a per-project `.ai-workflow/` copy.

Start in a genuinely new agent session from the planning session. Rehydrate from the issue and `[DECISION]` comments, pinned OpenSpec change and commit, repository instructions and concise handoff. ai-memory may supplement this context; it is never the sole source of validation evidence or source of truth.

## Entry gate

Verify the exact issue and OpenSpec proposal/spec/design/tasks, pinned revision, review evidence and official validation result. Check the branch/worktree, current diff and merged prerequisites. If evidence is missing, the revision changed materially, a blocking decision remains or this is still the planning session, stop with a precise handoff. A proposal's existence alone does not pass the gate.

Run the repository's official `/opsx-apply` command; do not invent a substitute command. Implement only the validated contract and applicable repository invariants. If new evidence changes behavior, data, authorization, architecture or public contracts, pause the affected work, update the issue and OpenSpec, then review and validate the revised pinned contract; ask the owner only for unresolved material decisions.

## Pre-flight and policy reconciliation

Follow TEST_STRATEGY's pre-flight before the first expensive run: check the planned focused sample and real consumers, test discovery/paths, fixtures/rollback, configuration timing/scope, mounted checkout, installed vendor/toolchain versus lockfile and sandbox isolation. A failed prerequisite blocks that run; a focused pass does not replace the broad or hosted required gate. Compare policy paths/commit recorded in the plan to current instructions on resume; document unchanged policy or reconcile divergences with current required gates and retained explicit validated obligations. A hosted required gate needs an exact-SHA hosted result, never a local substitute. Use optional `scripts/preflight-check lock` and `policy --since <plan-commit>` where installed, or perform the same checks manually. For base failures, compare equivalent base evidence (`evidence:<id>` where available), record origin/action and retain a failing required gate; verify scope before changing external tests.

## Integration test feedback loop

For a change requiring integration or API-functional coverage, use the test matrix from planning and inspect the repository's current test instructions and helpers before running anything. In Magento repositories, check the installed PHPUnit configuration, fixtures, service readiness, actual checkout mounted in the container, generated directory, Composer-restored test framework files, and whether the test database/sandbox is disposable and isolated. The worktree alone does not isolate a database or container. Follow project-specific recovery commands; never run functional fixtures against valuable development data. If safe isolation is unavailable, report the blocker instead of substituting a hosted run or silently skipping a required test.

Read [incremental delivery](references/INCREMENTAL_DELIVERY.md). When a newly discovered case is optional and independently valuable, record a compact candidate (reason, parent issue and dependency) in the **existing** Apply handoff without GitHub queries/writes in the coding loop; never defer current safety or approved contract obligations. Do not automatically broaden the implementation. At a natural checkpoint before Prepare PR, invoke [capture-evolutions](capture-evolutions) once for the accumulated batch in a fresh isolated child context when available (bounded sequential fallback otherwise), then notify the owner. Pass the verified links and future milestones or the exact tracking blocker to Prepare PR.

Implement one vertical scenario at a time. Before the first expensive run, check syntax, test discovery and annotations/attributes, fixture existence and rollback ownership, DI/config/schema expectations, and assertions against the real public boundary. Review a nearby passing test and the relevant framework behavior when test setup is uncertain. Use cheap focused unit/static checks for pure rules, then run the narrowest meaningful integration class or method through the repository's supported command. Do not treat mocked unit tests as proof of persistence, transactions, GraphQL wiring or framework lifecycle.

On failure, save the exact command, first relevant exception, test/fixture and setup phase; classify it as environment/bootstrap, fixture/isolation, implementation, assertion/contract, or intermittent. Verify the cause against code/logs and change one cause at a time. Record repeated attempts in the `attempt-log` block of the existing Validation handoff (TEST_STRATEGY); group by obligation/signature, not command/target. Before any third attempt after two equivalent failures, even one expected to pass, the executor MUST inspect and record a complete diagnosis after the second failure and before the next attempt, then run `scripts/attempt-log check <handoff-file>` on that updated log. A non-final exit 0 for a historical log ending at two failures says only that it is structurally valid; it does not authorize the next attempt without diagnosis. Once the next attempt is recorded, the reviewer can check that missing intervening diagnosis produces `E_RETRY_LIMIT`. A repeated hypothesis needs a concrete changed observation/effect and a new supporting reference, not merely a new ID. Reclassify with evidence before changing layers: for setup failures repair only the disposable sandbox; do not rewrite application code. For assertion/contract failures, compare the observed behavior with the approved contract before changing either: cite the exact definition, field and scope, separate observation from inference and confirm the field's reading (a group attribute is not automatically inherited). Check the block before claiming contradiction or blocker; material replan follows the reviewed OpenSpec gate, and a valid blocker still leaves a required check pending. Re-run the affected target after the fix, then broaden to the module/related suites and a different order when shared state or rollback is involved. Serialize tests sharing a sandbox, database, search index or mounted checkout. Avoid interrupting initial Magento installation and avoid blanket cleanup between successful focused runs unless the project requires it.

Before commit, run focused checks and a preliminary full suite against the intended candidate. Where installed, use `workflow-evidence record --obligation <matrix-id> --selection <filter> -- <command>`; declare configs, output paths and non-secret tool/environment IDs, then verify and hand off IDs or integrity-checked bundles, not foreign temporary paths. Complete OpenSpec archive/sync, distribution and PR preparation edits, commit them, and **then** record and verify the final required local suite on the exact clean HEAD. Keep that `evidence_id` outside the commit; any later commit requires a new final run on its HEAD. Preserve test cleanup, isolation, failure propagation and repository rules governing hosted heavy tests. Record PASS/FAIL/NOT RUN, commands, target revision, environment, test counts and any setup versus test failure. A missing or failed required suite blocks PR preparation when the repository says it is a gate; historical or hosted results do not replace a local gate. If the helper is not installed, retain the previous manual evidence and mark helper verification NOT RUN, not the required test as passed without proof. Checkout reservation/verification remains a separate mandatory guard.

Run focused tests and relevant static checks; record actual PASS/FAIL/NOT RUN with reasons. Apply `openspec-workflow` for the mandatory post-Apply closeout: complete validated tasks, verify scenarios against implementation and tests, use the official verifier when available, strictly validate, archive on this feature branch, synchronize validated live specs and inspect both archived artifacts and live specs. If verification or archive fails or changes the validated behavior, stop and follow its revision review and validation gate. Do not hand an active incomplete change to `prepare-pr`.

Then inspect the complete diff for unrelated changes, preserve unrelated user work, and pass to `prepare-pr`. End with `READY FOR PR` only when implementation, verification, archive and validation gates pass; otherwise end with `NOT READY FOR PR — <reason>`.

## Automatic CI performance routing

Read [the CI performance protocol](references/CI_PERFORMANCE.md). Automatically apply `optimize-ci` inside this fresh session for validated performance experiments. For ordinary feature changes to expensive fixtures, test discovery or CI setup, use its lightweight preservation checklist without expanding scope. Record before/after only when the validated work requires it; retain normal verification and archive gates.

## Proportionate test coverage

Read [the test strategy](references/TEST_STRATEGY.md). Implement the planned scenarios using existing fixtures and the smallest proving layer. Record the concrete reason for added coverage. Run narrow checks while correcting failures, diagnose after two attempts without progress on the same failure, and retain the final repository-required gates. Stop expanding scenarios once the agreed criteria and identified risks are proven.

Inspect existing tests for the affected behavior for redundant cases or obsolete expectations under the test strategy. Keep ordinary cleanup small and scope-bound; for a wider suite audit use a dedicated issue. Any consolidation, migration or removal needs a current-obligation → retained/replacement proof (or authoritative obsolescence evidence) map and applicable validation.

## Visual design application

When the validated issue includes an approved UI artifact, automatically apply `visual-artifact-implementation` and [the visual artifact protocol](../../protocol/VISUAL_ARTIFACTS.md) during `/opsx-apply`. Preserve existing behavior and project UI patterns; capture and compare actual screenshots when feasible. Record visual verification limitations honestly in the PR handoff. No extra standalone command or owner checkpoint is required for routine visual decisions.

## Worktree lifecycle

Follow [the worktree protocol](references/WORKTREES.md) before checkout writes or worker dispatch. Inventory and reuse the verified issue checkout; transfer its single writer reservation across fresh sessions. Preserve partial work, isolate test resources and retain manual-merge work. Close out only verified eligible worktrees using non-forced Git operations.

When installed, use `worktree-reservation reserve`/`verify` before mutating, `checkpoint` after own writes and `handoff` between returned workers; drift suspends writes until recorded acceptance. Without the helper, coordinate manually under WORKTREES and report the gap.
