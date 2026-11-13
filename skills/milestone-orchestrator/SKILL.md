---
name: milestone-orchestrator
description: Run one GitHub issue, a repository work queue or a specific milestone as one supervised workflow that audits eligible issues and PRs, batches OpenSpec proposal reviews, schedules isolated workers by dependencies, and continues through verified merge or an explicit blocker. Use for "cuide da fila deste projeto", "cuide da fila deste projeto, sem merges", "cuide deste milestone", or "cuide da issue <issue URL>".
---

# Issue, Work Queue and Milestone Orchestrator

For global installations, resolve `scripts/<helper>` against
`"${XDG_DATA_HOME:-$HOME/.local/share}/my-ai-skills/active/scripts/<helper>"`.
Run from the actual checkout and quote paths; execution data stays in the
checkout's Git common directory, not in the global package.

Run the entire selected scope: one issue, a project queue or a milestone. Read repository instructions and [the AI workflow protocol](references/AI_WORKFLOW.md). Coordinate issue-audit, implement-issue, apply-issue, prepare-pr, pr-audit, architecture-audit when relevant, github-resolution and kaizen. Delegate per-PR correction, final independent audit and merge to github-resolution; this skill owns the milestone dependency scheduler. Each worker must follow its skill gates. For new capabilities, route optional evolution candidates through `capture-evolutions` at planning/Apply checkpoints using a fresh child context when possible; do not add future-milestone evolution issues to the current execution queue or expand selected milestone/single-issue scope. A missing child worker uses a bounded sequential checkpoint fallback; no mandatory separate approval. Proposal review and approval are owned by the agent: never interrupt the owner for routine proposal approval. Apply the shared evidence checklist, record the exact revision and rationale, then schedule a validated proposal automatically. Escalate only an unresolved material decision or a defined high-impact boundary.

## Lightweight orchestrator and worker boundaries

The parent session is a **control plane**, not a code reader, planner, implementer, or reviewer. Its non-delegable duties are to determine the exact authorized scope and merge mode, enforce dependency/scheduling and resource limits, keep the one-writer run/issue ledger, validate worker identities and evidence, select the next eligible gate, and escalate material decisions to the owner. It may inspect the minimum trusted metadata required to verify those duties; it must not absorb full source diffs, test logs, issue transcripts or OpenSpec documents when a bounded worker can inspect them.

Use existing skills inside **logical workers** rather than creating one child per skill:

| Worker | Scope and existing skills | Allowed output |
| --- | --- | --- |
| Discovery (read-only) | Fetch scoped issues, comments, PRs, SHA-pinned code, OpenSpec, checks and worktree inventory; run evidence-backed issue/PR inventory and dependency research | Compact inventory, dependency proposals, authoritative refs, uncertainty/blockers |
| Planning (one issue/worktree) | `issue-audit`, `issue-explore`, `issue-ready`, `implement-issue`, `openspec-workflow` Explore/Propose | Exact validated proposal SHA, review/validation evidence, accepted decisions, READY FOR APPLY or blocker |
| Apply (fresh session) | `apply-issue`, tests, verification, archive, `prepare-pr` | Exact branch/PR HEAD, checks, evidence IDs and completion/unknown state |
| Review/resolution | `pr-audit`, `architecture-audit` when applicable, `github-resolution`, `post-pr-audit` | Independent findings, exact-head gate verdict and verified merge state |
| Evolution | `capture-evolutions` at checkpoint only | Linked future issues/milestone evidence, without entering current queue |

**Dispatch and trust rules:**

1. Verify runtime support for genuinely fresh child contexts and worktree isolation before dispatch; do not simulate independence by changing a role prompt in the same conversation. If discovery cannot be delegated, a bounded **read-only** inventory fallback is permitted. Planning may use the existing bounded fallback only where its skill allows it. Never run Apply in the planning/parent context or self-certify a final independent review.
2. Dispatch Discovery with the exact repository/scope, merge mode, base revision and desired fields. It must not mutate GitHub or files. The parent checks referenced issue/PR identity and revalidates hard dependency/merge eligibility before acting on its suggestions. Discovery does not own DAG or authorization.
3. Dispatch Planning per eligible issue to a fresh child and isolated checkout; avoid sending a full prior transcript. The parent accepts READY FOR APPLY only with an immutable proposal revision and official validation/review evidence matching current decisions and dependency commits. A stale plan is returned to Planning, not silently amended by the parent.
4. Every worker result must carry `run_id`, `worker_id`, `task_kind`, exact `repository`/`scope`/`issue_url`, `input_refs` with known SHAs, `outcome` (`completed|blocked|failed|unknown`), `output_refs` with evidence references, `blocker` when applicable and `next_action`. These are **handoff metadata**, not a new persistence service or a claim that a runtime supports a specific schema; reuse the durable handoff and workflow-event mechanisms below. A missing/ambiguous field or unsupported execution status means UNKNOWN until independently reconciled.
5. Child workers provide timestamps/execution IDs and references, never concurrently write the orchestrator's run record. Parent validates current heads, worktree writer reservation, exact evidence, applicable gates and authorized merge mode. An emitted result is not automatically a verified result.
6. Keep full logs, investigation and implementation history within their owning workers and durable artifacts; summarize only state, evidence, blockers and next safe action to the parent. Preserve isolated independent review and fresh Apply boundaries through retries, recovery and resumed runs.

## Invocation and operating modes

Accept these natural requests without requiring a mode parameter:
- "Cuide da fila deste projeto": use the single repository established by the current checkout/remote or explicit conversation context; inventory all open PRs and open issues in that repository.
- "Cuide da fila deste projeto, sem merges": use the same queue with `merge_mode=manual` for this run.
- "Cuide deste milestone": use the supplied milestone URL or a unique milestone identified by the current request/context. Do not guess among multiple candidates; request only the missing milestone identifier when needed.

- "Cuide da issue: <GitHub issue URL>" or "Cuide desta issue: <GitHub issue URL>": use `scope=single_issue`, selecting exactly that issue and its verified linked implementation PR. A number is sufficient only when the repository is uniquely established; ask only for a missing/ambiguous identifier.
- "Cuide da issue: <GitHub issue URL>, sem merge" or "sem merges": use the same single-issue scope with `merge_mode=manual`.

A repository URL/name is sufficient if there is no local checkout. Never silently widen a named milestone to the whole repository or another repository's queue. A single invocation carries eligible work through the workflow and resumes from durable state after interruption; never ask the owner to invoke another skill for each issue.

Default merge mode is `auto-if-green` under the owner's standing instruction for this workflow. A direct "do not merge" or `merge_mode=manual` request overrides it for the selected run. The default authorizes merge only after all configured repository requirements and this workflow's review gates pass. Apply this only to the selected single issue, repository queue or milestone run. It never bypasses branch protection, required human reviews, required checks, or repository policy. If the merge method or eligibility cannot be established, stop that PR at `READY_TO_MERGE`. Never force-push, release, deploy, or tag as a side effect.

At startup, inspect available orchestration capabilities: ability to create fresh child sessions (OpenCode Task/subagent or equivalent), isolated worktrees, GitHub reads/writes, and repository-local test commands. Do not claim automation that the runtime cannot perform. If child sessions are unavailable, still inventory and prepare a consolidated plan/proposal batch, then report the precise missing capability; do not silently run Apply in the planning context. Use the available number of workers as a resource ceiling, not a fixed issue-count policy.

## Single-issue scope

For `scope=single_issue`, run the same gates and workers below with a one-ticket ledger. Refresh the issue, comments, decisions, code, existing OpenSpec artifacts, linked PRs and current checks. Verify repository identity before any write; an explicit issue URL determines the target repository, so a different checkout requires the correct checkout/worktree or a capability blocker. A PR URL is not an issue identifier.

Read related issues and prerequisite PRs only to establish dependency/contract evidence. Do not implement, modify or merge prerequisites, siblings, other milestone issues or unrelated PRs without an explicit scope expansion. If a hard prerequisite is unmerged or its contract is unfrozen, report `BLOCKED` with evidence and the exact prerequisite; do not start dependent implementation.

Resume the last verified gate. For an existing implementation PR, independently audit its current head and hand it to `github-resolution`; do not recreate the plan, branch or PR when their evidence remains valid. If multiple candidate PRs exist, verify which delivers this issue and report unresolved ambiguity instead of selecting or merging every linked PR. A closed issue does not authorize reopening or new work: verify existing delivery and report its state; if closed without delivered work, report that fact and request a scope decision.

For a new eligible issue, run issue-audit, implement-issue, exact-revision proposal review/validation, fresh-session apply-issue, tests/verification/archive, prepare-pr, independent pr-audit (architecture-audit when relevant), then github-resolution and independent post-pr-audit. Continue automatically through confirmed merge/closure and kaizen in auto-if-green mode, or `READY_TO_MERGE` in manual mode. Do not ask the owner to invoke each skill. Material unanswered questions and missing runtime capabilities remain explicit blockers. Carry the existing automatic CI performance hooks.

## One-run workflow

1. Resolve the unique repository and selected scope. Delegate scoped issue/PR/code/OpenSpec/check inventory to a read-only Discovery worker, then verify its identity, refs and uncertainty before scheduling; refresh only the minimum authoritative metadata necessary in the parent. Skip drafts from implementation with reasons; audit eligible existing PRs before scheduling new issue work. Reconstruct existing progress and resume it; never duplicate a branch, OpenSpec change, or PR.
2. Build and own a dependency DAG from verified Discovery evidence links. Classify hard dependencies, coordination dependencies, likely file/module conflicts, and independent work. An open PR does not satisfy a hard dependency. Unknown edges block only affected issues; detect cycles. For cross-repository producer-to-consumer work, run contract-handoff during planning before releasing the consumer proposal and again in final-freeze mode after producer delivery, before consumer implementation. A missing contract capability is a hard dependency for only the affected consumer issues.
3. Create a ledger for every issue and pre-existing PR in scope. Preserve existing decisions, validated proposal revisions, branches, implementations, PRs, reviews, and checks when their SHAs still match.
4. Schedule planning for all currently eligible issues. Use fresh planning child sessions and isolated worktrees when available. Independent issues may be planned in parallel, up to runtime capacity. Run issue-audit, then implement-issue (/opsx-explore, issue-ready, /opsx-propose). Do not implement production code during planning. Do not create/release a dependent consumer proposal until the required producer capability is delivered in merged code or verified at an explicit immutable producer ref and contract-handoff passes. An open producer issue or planned schema is not delivery; mark only affected consumer issues CONTRACT_BLOCKED and continue eligible producer/unrelated work. Record material questions as [QUESTION], mark that issue NEEDS_INPUT, and continue with unrelated eligible issues.
5. Collect each planning worker's compact, evidence-backed review references (not its full transcript) against the issue, latest [DECISION] comments, current code, architecture, requirements, tests, dependencies and OpenSpec scenarios. Verify the official validation result and immutable proposal SHA; use an independent planning reviewer for material boundaries when available if not already completed. Reuse matching evidence instead of rerunning unchanged validation. Publish a consolidated progress summary without waiting for owner approval; proposal approval is an internal agent gate, not a user checkpoint. Questions that require a new product or architecture decision mark only affected issues NEEDS_INPUT; failed validation returns them to planning. A material proposal change invalidates the prior review and must be reviewed again.
6. Schedule validated, decision-complete proposals automatically. For each issue, start a genuinely fresh implementation child session with a compact durable handoff, verify the exact reviewed proposal SHA, validation evidence and merged dependency commits. For dependent consumers, rerun contract-handoff in final-freeze mode against merged producer code/schema and require CONTRACT FROZEN before apply-issue plus official /opsx-apply. One issue gets one branch/worktree and one PR. Do not send the planning transcript as the only handoff.
7. Parallelize implementation only when all hard dependencies are merged, tasks are independent, expected code paths do not conflict, and each worker has an isolated worktree and fresh session. Determine concurrency from the dependency DAG, overlap risk, available agent/session capacity, CI resources, and repository limits. Serialize likely overlapping edits. Re-evaluate after each audit/diff; if a conflict appears, stop/reschedule the affected work safely. Never exceed runtime capacity or start dependent work early.
8. Each implementer runs focused tests and supported OpenSpec verification, completes validated tasks, strictly validates and archives the validated change on its feature branch, inspects archived artifacts and synchronized live specs, and invokes prepare-pr. Invoking prepare-pr authorizes only the scoped commit, non-force push, and PR creation described by that skill.
9. Run independent pr-audit and architecture-audit when relevant in fresh reviewer sessions. Hand each audited PR to github-resolution with the verified issue/proposal SHA and this run's merge mode. That skill coordinates address-pr-review corrections, refreshed audit, independent post-pr-audit and exact-head CI. While PRs wait for checks/reviews, schedule other eligible issues; do not schedule hard dependents until their prerequisite PR is merged.
10. With `merge_mode=manual`, collect the per-PR `READY_TO_MERGE` results for the owner. With the default `merge_mode=auto-if-green`, let github-resolution/post-pr-audit perform or queue the eligible merge; verify actual merge and issue closure before running kaizen or scheduling hard dependents. If GitHub cannot enforce applicable gates or any signal is unknown/stale, report that PR's blocker.
11. Continue the scheduler until all issues are merged/kaizen-complete, blocked on owner input/dependencies, or the runtime reaches an explicit capability/resource limit. Do not stop after one issue merely because it is the first in milestone order.

## Dynamic scheduling rules

- Hard prerequisites always determine order; issue number and milestone display order do not.
- Run independent planning or implementation work concurrently only with isolated worktrees. Start with the largest safe worker count supported by available capacity, then lower it for shared code paths, migration/contract coupling, limited test environments, provider limits, or rate limits.
- For uncertain overlap, inspect each issue's expected files/modules and current diffs. Prefer serialization when isolation or conflict risk is unclear.
- An unresolved product/architecture question blocks its issue and its dependents, not unrelated work.
- If runtime capacity is lower than safe parallelism, queue the remaining eligible work and continue automatically as workers finish.
- If a prerequisite PR is awaiting manual merge, report the dependent queue and continue independent branches where safe. Resume dependents automatically after verifying the prerequisite merge.

## Evidence ledger

GitHub issues/comments, approved product decision records, committed OpenSpec artifacts, PRs, commits, review results, and checks on exact SHAs are durable. ai-memory is useful for handoff but is never a proposal validation or decision record. Build the ledger from live evidence after every interruption; a label, chat summary, or workflow-status heuristic cannot prove a gate.

| State | Minimum evidence |
|---|---|
| BACKLOG | Open issue or PR in the selected queue with no verified audit. |
| AUDITED | Current-code issue-audit report linked to the issue. |
| EXPLORING | Planning worker is exploring and refreshing questions/decisions. |
| SPECIFIED | issue-ready passed; proposal/spec/design/tasks created and pinned to a commit, pending review. |
| PLAN_REVIEW | Exact proposal SHA undergoing traceability and official validation. |
| PLAN_VALIDATED | Exact proposal SHA, review evidence and official validation recorded; no unresolved material decision. For cross-repository consumers, contract design review passed. |
| CONTRACT_BLOCKED | Consumer has an evidenced missing/unfrozen producer capability; exact producer dependency, scenario gap and next action are recorded. Independent work continues. |\n| IMPLEMENTING | Fresh child session verified the validated proposal SHA and began apply-issue; dependent consumers also have CONTRACT FROZEN evidence. |
| PR_OPEN | PR at known head SHA with issue linkage, test evidence, and archived/synchronized OpenSpec when applicable. |
| PR_AUDITED | Independent audits tied to current PR head; rerun after material push. |
| CI_GREEN | Required checks succeeded on current head with no pending/failing required jobs. |
| READY_TO_MERGE | Final audits pass and CI is green; awaiting owner merge in manual mode. |
| AUTO_MERGE_ENABLED | Auto-if-green mode applies and GitHub auto-merge is enabled without bypassing protections. |
| MERGED | PR merged and issue closure verified independently. |
| KAIZEN_DONE | Merged work reviewed by kaizen; record a concrete improvement or NO PROCESS CHANGE. |

Exceptional states: NEEDS_INPUT, NEEDS_REPLAN, BLOCKED, FAILED, RESOURCE_QUEUED. Classify a blocker with evidence: technical → BLOCKED (`workflow-event` wait reason `environment` for sandbox/service, or `dependency`/`external`), missing capacity → RESOURCE_QUEUED (`runtime_capacity`), material business decision with options/impact → NEEDS_INPUT (`owner_input`); investigate researchable technical facts instead of escalating them. Accepted material replan → NEEDS_REPLAN through OpenSpec review; a valid blocked attempt group is not PR-ready. Preserve the last verified state, exact blocker, evidence and next automatic action. A closed issue without verified delivered/merged work is not MERGED; empty or stale checks are not CI_GREEN.

Record repository and selected scope (`single_issue`, `project_queue` or `milestone`), issue/PR, state, evidence links and SHAs, dependency gate, branch/worktree, proposal revision/review evidence, PR head/checks, merge mode, blocker and next action. Use existing issue/PR records and committed artifacts; do not create a competing source of truth.

## Per-issue invariants

- No implementation before the exact OpenSpec proposal revision is reviewed, officially validated and pinned.
- Material behavior, data, authorization, architecture, public-contract, concurrency, or compatibility changes require a new plan review and validation; seek the owner when a new decision cannot be derived from existing decisions and project policy.
- One issue = one branch/worktree, one validated OpenSpec change, one PR, unless resuming compatible existing artifacts.
- Preserve unrelated local work; never use broad staging such as `git add .`.
- Re-run only checks invalidated by a change, but always run final-head audits and required checks after a material push.
- Never merge when the final head is unknown, CI is pending/failing, review findings remain, required repository human reviews are missing, or repository rules disallow it.
- Use the owner's standing auto-if-green instruction by default for the selected run; never merge after an explicit manual-mode or no-merge instruction.

## Durable handoff

Use actual repository paths and commands, not this sample layout:

```yaml
repository: owner/name
scope: single_issue # or project_queue / milestone
# Include milestone_url only for scope: milestone.
issue_url: https://github.com/owner/name/issues/123
base_ref: main
branch: issue-123-short-name
worktree: /absolute/path/to/issue-worktree
openspec_change: issue-123-short-name
planning_commit: <sha>
decision_urls: [<applicable-issue-decisions-if-any>]
validated_proposal_sha: <planning-commit-sha>
proposal_review_evidence: <durable-review-record>
openspec_validation: <exact-command-and-result>
artifact_paths: [<proposal-spec-design-task-paths>]
dependency_commits: [<merged-commit-shas>]
architecture_constraints: [<repository-instructions-or-decision-links>]
validation_commands: [<actual-supported-commands>]
evidence_ids: [<evidence:ev-... plus state and obligation; package location if another runtime>]
merge_mode: auto-if-green
```

Reject a handoff when issue, validated proposal SHA, review/validation evidence, worktree tree, or merged dependencies disagree. Never pass the planning transcript as the only evidence.

When `workflow-evidence` is installed, carry `evidence_id`/integrity-checked bundle in the Apply → prepare-pr → review handoff and attach `workflow-event --evidence evidence:<id>` to the run. A foreign `/tmp` path or public local metadata alone is not a verified local proof. Verify on the recipient's candidate and respect per-obligation recovery; keep the final gate's ID outside the commit and rerun it after any HEAD change. Hosted gates require an independent trusted base-policy/check binding and exact-SHA API confirmation, never a local-gate substitution. Without the helper, retain the manual proof and label helper verification NOT RUN.

## Recovery and output

On interruption, refresh GitHub and Git, inspect partial work and PR state, preserve unrelated changes, and resume from the last verified gate. Do not rerun valid work. If a session fails, retry that issue within the configured attempt/resource limits; after repeated failure, mark FAILED and continue unrelated eligible issues. Never silently skip a blocked issue or claim a failed check passed.

For a report-only milestone request, route to `milestone-progress` without starting this execution workflow. During an authorized run, use its table format for progress updates when available.

Return a compact status table of the selected scope's issues and PRs, dependency graph/order, active workers, states, evidence/SHAs, checks, blockers, merge mode, and the next automatic action. In manual mode, report all `READY_TO_MERGE` items together. In auto-if-green mode, report which PRs are queued for GitHub auto-merge and why any could not be queued. ghpending may aid triage; GitHub Project is a product view, not an execution gate.

## Workflow timing instrumentation

When the helper scripts are installed and GitHub access is available, record timing events for every orchestrated issue. Instrumentation is evidence collection; if it is unavailable or fails, report that fact and continue the development workflow.

1. At invocation start, create one run ID with `scripts/workflow-event new-run-id`. Pass that same ID to all issues and child sessions in the selected milestone/queue run. Record `run-start` once for every issue in scope, including blocked and not-yet-eligible issues, with the scope and milestone URL.
2. Surround actual gates with `stage-start` / `stage-end`: `issue_audit`, `explore`, `resolve_questions`, `proposal`, `proposal_review`, `apply`, `tests`, `verify_archive`, `prepare_pr`, `pr_audit`, `ci`, `merge`, and `kaizen`. Use the gate names consistently. For an asynchronous worker, use `dispatch --stage S --worker-id W [--execution-kind K --execution-id ID]` at dispatch time, not the immediate dispatch response as completion. Close a typed stage only with the same execution kind and ID. Record callbacks with `observe --stage S --worker-id W --state ... --source ... [--observed-at ISO-8601]`; `recorded_at` preserves when the callback was written. The orchestrator remains the sole writer: workers return timestamps, execution IDs and observations rather than patching the issue comment concurrently. A local `workflow-evidence` run uses `--execution-kind test_run --execution-id <evidence_id>` (emitted before execution) and `--evidence evidence:<evidence_id>` on `observe`/`stage-end`; a hosted `ci_run` ID is the CI run ID. Report presence or a linked evidence ID is not a verified/approved proof; only `workflow-evidence verify` can establish that verdict.
3. Mark only explicit waits with `wait-start` / `wait-end` and a reason: `owner_input`, `dependency`, `ci`, `tests`, `review`, `environment`, `runtime_capacity`, `external`, or `other`. `tests` means local tests in progress. #34 blocker mapping: `technical` → `BLOCKED` with `environment` (sandbox/service), `dependency` or `external`; `capacity` → `RESOURCE_QUEUED` with `runtime_capacity`; `business_decision` → `NEEDS_INPUT` with `owner_input`; accepted `replan` → `NEEDS_REPLAN`. Do not infer waiting from elapsed time.
4. Record a `rework` event when work returns to a completed gate because of a review finding, failed check, replan, or issue reopening. Link the evidence; do not label normal first-pass work as rework.
5. Before announcing activity/completion, including after interruption, compaction or resume, reconcile the execution against a runtime completion callback or supported query and its evidence. Prefer notifications/callbacks; never poll without a purpose. Agent prose and container state alone cannot confirm activity or completion. If no supported confirmation exists, record `unknown` with the available source and report unknown, not a pass. An absent JUnit/termination is incomplete evidence. On resume, reuse the run ID, close only waits actually ended, keep the issue/worker/stage/execution identity, and continue automatically without asking the owner for a command per gate. A conversation containing multiple issues does not merge their records: write each issue's own run comment, and expand the selected scope only when authorized. Never put credentials or arbitrary log text in `--log-ref`.
6. At the end of the selected run, record `run-end` with `completed` or `failed`. A missing permission, missing helper, or GitHub API failure must never block implementation or be presented as valid timing data.

The logger maintains one machine-readable comment per issue/run. Use `scripts/workflow-report <issue-or-milestone-URL>` to report the latest runs, or add `--run-id <id>` for a milestone-wide run. Its `status_summary` gives current stage, observed state, last confirmed observation, blocker, next action and verification time; `incomplete_evidence` identifies test runs without confirmed termination/report. These are runtime observations, not proof verdicts. The report separates calendar duration, registered stage work (cut at confirmed terminal observation), explicit waits, and quality evidence. Registered work is wall-clock time inside recorded stage windows minus declared waits; it is not model-internal thinking time. Never add parallel worker durations and call the result calendar time.

## Automatic CI performance routing

Read [the CI performance protocol](references/CI_PERFORMANCE.md). Carry automatic `ci-performance-audit`/`optimize-ci` routing in relevant worker handoffs. Permit independent planning, but serialize optimization experiments sharing workflows, databases/sandboxes, runner resources or measured workload unless isolation and contention are explicitly accounted for. Reconstruct baseline/candidate evidence from the ledger; do not require the owner to invoke another skill or add an unconditional benchmark job.

## Proportionate test coverage

Read [the test strategy](references/TEST_STRATEGY.md). Carry each issue's risk-based scenario matrix through planning, Apply and review handoffs. Use the existing matrix and gates; do not introduce a test-planning approval checkpoint, fixed test quota or per-issue benchmark.

## Worktree lifecycle

Follow [the worktree protocol](references/WORKTREES.md) before checkout writes or worker dispatch. Inventory and reuse the verified issue checkout; transfer its single writer reservation across fresh sessions. Preserve partial work, isolate test resources and retain manual-merge work. Automatically remove verified eligible managed worktrees after delivery/kaizen, reconcile leftovers at startup/resume and run end, and report retained paths with precise reasons. Use only non-forced Git operations.

When installed, use `worktree-reservation reserve --planned --repository <existing-checkout>` before creation, `cancel-planned` only if add failed without a destination or Git entry, `reserve` to activate, `verify` before mutations, `checkpoint` after own writes, and `handoff` only after the prior worker returned; stop on drift until explicit recorded acceptance, and on registry loss until inventory and stopped-writer evidence have been reviewed. Without the helper, coordinate manually under WORKTREES and report the gap.
