# AI Development Workflow

## Source of truth

GitHub is the shared memory for people and agents. OpenSpec is the validated behavioral and architectural contract for this workflow. The repository is current implementation reality; tests are executable evidence.

The latest explicit approved decision supersedes older conflicting discussion. Do not silently infer a material product or architectural decision.

## Proposal approval without owner checkpoints

OpenSpec proposal approval is an agent-owned quality gate, not a request for owner authorization. The planning agent must analyze, review, revise, and approve a proposal when it is supported by the issue, recorded decisions, current code, repository rules, and established project patterns. Do not pause to ask the owner to approve a proposal just because it was created or reached the validation step.

Before marking a proposal `PLAN_VALIDATED` / `READY FOR APPLY`, confirm that every acceptance criterion maps to proposed behavior and tests; scope and non-goals match the issue; contracts and architecture follow existing decisions and patterns; risks and trade-offs are recorded; the exact proposal revision passes official OpenSpec validation; and required independent review is complete. Record the review and validation evidence, then continue automatically.

Resolve routine questions from current code, native platform behavior, existing approved decisions, repository conventions, and tests. Ask the owner only when a material product or architecture choice remains genuinely unresolved, or when the proposal would add unrequested scope, break a public contract, change authorization or sensitive data handling, introduce an irreversible migration/destructive action, or create a material external cost or commitment. Explain the specific choice and impact. A missing fact that can be researched is not an owner decision. Block only the affected issue and continue independent work.

## States

| State | Predominant role | Exit condition |
|---|---|---|
| `DISCOVERY` | Web supervisor + owner + executor exploration | Problem, current implementation, dependencies and questions are understood. |
| `READY` | Web supervisor / architecture | Definition of Ready passes and no blocking question remains. |
| `IMPLEMENTING` | Codex/Claude Code + OpenSpec | Validated contract implemented and verified. |
| `REVIEW` | Independent reviewer + executor fix loop | Requirements, decisions, spec, diff and tests agree. |
| `DONE` | Owner | PR approved and merged; issue closed according to repository policy. |

## Required flow

Command names follow OpenSpec's per-agent convention: `/opsx-explore`, `/opsx-propose`, `/opsx-apply` and `/opsx-archive` in Codex and OpenCode; `/opsx:explore`, `/opsx:propose`, `/opsx:apply` and `/opsx:archive` in Claude Code. Use the form installed for the current agent.

1. Run `issue-audit` against the live issue and current code; refine material gaps.
2. Run `/opsx-explore` against the issue, all comments, code, tests, docs and current OpenSpec. Do not implement.
3. Investigate ambiguities against approved decisions, current code, native mechanisms, repository policy and tests. Resolve those supported by evidence and record the rationale. Record a `[QUESTION]` and stop only when a material product/architecture decision remains unresolved; block only affected work.
4. Record approved answers as `[DECISION]`.
5. Refresh GitHub and run `/opsx-explore` again after decisions.
6. For cross-repository producer-consumer work, run `contract-handoff` in design-review mode before releasing the consumer proposal. Trace each relevant requirement/wireframe scenario to public operations, fields, states/errors, and the producer's enforcement point. Record linked producer/consumer issues and a hard dependency. A missing or implicit producer capability blocks only that consumer proposal/implementation; continue eligible producer and unrelated work.
7. Pass `issue-ready`.
8. Run `/opsx-propose` to create or update OpenSpec proposal/spec/design/tasks.
9. Validate each proposal with the official OpenSpec command and the approval checklist above. Use an independent planning reviewer when available for material boundary changes; record the exact immutable proposal revision and review evidence. The agent approves the proposal internally when the checklist passes, reports the decision and evidence, and continues without asking for owner approval. Stop only for a genuinely unresolved material decision or failed validation.
10. Use `openspec-workflow` as the canonical proposal and closeout procedure. Start a genuinely new child session per issue with `apply-issue`; verify the pinned validated revision, review evidence and durable handoff, then run `/opsx-apply`. For dependent consumers, first rerun `contract-handoff` in final-freeze mode against merged producer code/schema and require `CONTRACT FROZEN`. For milestones, schedule these sessions dynamically by dependency and conflict risk. ai-memory is supplementary.
11. After Apply, complete focused tests and supported OpenSpec implementation verification; strictly validate the active change and archive it on the feature branch after all gates pass. Inspect the archived artifacts and synchronized live specs so they enter the same issue PR. Then self-review and invoke `/prepare-pr` with requirement → code → test evidence. This invocation authorizes staging only issue-scoped files, committing, pushing the feature branch without force, and opening the PR; no second confirmation is needed. Preserve unrelated work. This does not authorize merge, release, deploy or force-push. If the owner explicitly says prepare-only, stop at `READY FOR PR`.
12. Independently run `pr-audit`, with `architecture-audit` for boundary changes. Route valid findings to `github-resolution`, which invokes `address-pr-review` for corrections on the same PR branch.
13. After corrections, refresh `pr-audit` on the current materially changed head; run an independent `post-pr-audit` as the final review and merge eligibility gate. A newer push invalidates affected audit, review and test evidence.
14. By default use `merge_mode=auto-if-green` for the selected run: `post-pr-audit` may merge after all gates pass, or enable GitHub auto-merge while checks are pending only when repository rules enforce every applicable check and review. A direct "do not merge" or `merge_mode=manual` request overrides the default and ends at READY_TO_MERGE. Never bypass repository policy; verify the merged PR and issue closure, then run `kaizen` before hard dependents.

## Single-issue execution

Invoke `milestone-orchestrator` with "Cuide da issue: <GitHub issue URL>" (or "Cuide desta issue") for `scope=single_issue`. Add "sem merge" to select `merge_mode=manual`; otherwise the existing auto-if-green mode applies only to that issue. Use the same required flow, exact-revision proposal gate, fresh implementation session, independent audits and performance hooks. Resume an existing verified plan or implementation PR rather than creating duplicates. Related issues/PRs are read-only dependency evidence: do not execute prerequisites or widen to the milestone/queue. Unmerged hard dependencies, ambiguous PR links, unresolved material decisions or missing capabilities block this issue with evidence and an exact next action. For a closed issue, verify delivery and report its state without reopening it or starting new work. Continue to confirmed merge/closure and kaizen, or READY_TO_MERGE in manual mode.

## Milestone execution

Invoke `milestone-orchestrator` once with "cuide da fila deste projeto" for the uniquely identified current repository, or "cuide deste milestone" with an identifiable milestone. Add "sem merges" to opt out of the default automatic merge for this run. The project queue inventories open issues and PRs; a milestone scopes work to its issues and linked PRs. It inventories all eligible issues, builds an evidence-backed dependency DAG and schedules eligible work automatically. It reviews proposals against each exact OpenSpec revision without a routine owner checkpoint; after validation, fresh child sessions run Apply, tests, verification, archive, prepare-pr and independent audits. Concurrency is calculated from hard dependencies, expected code conflicts, isolated worktrees and runtime/CI capacity; dependent work waits for merged prerequisites while independent work continues. Missing decisions block only the affected issue/dependents. The default merge mode is `auto-if-green` for the selected run; an explicit "do not merge" or `merge_mode=manual` overrides it. Neither mode bypasses branch protections, required reviews, or checks. The ledger comes from GitHub issues, decisions, artifacts, PRs and exact-head CI; ai-memory is supplementary. After verified merge, run kaizen before hard dependents. ghpending is optional triage, and GitHub Project is a product view.

## Checkpoint reuse

Agents resume rather than restart. The proposal validation gate and fresh-session gate cannot be waived by checkpoint reuse:

- reuse a matching validated OpenSpec change only when the pinned revision and review evidence still match;
- treat existing `[DECISION]` comments as authoritative;
- continue an existing implementation rather than recreate it;
- when a PR exists, switch to review/fix flow;
- always refresh comments newer than the previous execution.

## Definition of Ready

- objective and problem are explicit;
- expected behavior, scope and non-goals are defined;
- current implementation and existing native mechanisms were inspected;
- business rules, authorization and state transitions are defined when relevant;
- API/GraphQL/data contracts, errors and edge cases are defined when relevant; cross-repository scenarios map to producer operations, authoritative states/errors and enforcement points;
- dependencies and cross-repository sequencing are known;
- test expectations and acceptance criteria are observable;
- approved decisions are recorded;
- no blocking `[QUESTION]` remains.

## Stop conditions

Do not turn every ambiguity into an owner question. First investigate it using available project evidence and resolve it when that evidence supports one answer; record the rationale. Stop and record a `[QUESTION]` only when a material product/architecture choice still has multiple plausible outcomes, or a change would add scope, break a public contract, alter authorization/sensitive data handling, introduce an irreversible migration/destructive action, or create a material external cost/commitment. Do not invent a decision to bypass the READY gate. Block only the affected issue and continue unrelated eligible work.

During implementation, if new evidence changes the validated contract, stop the affected work, update the issue/OpenSpec, rerun proposal review and validation, and resume in the required fresh implementation context. Seek the owner only for an unresolved material product/architecture decision.

## Workflow timing and Kaizen metrics

For a run managed by `milestone-orchestrator`, use the optional `workflow-event` and `workflow-report` helpers when installed and GitHub write access is available. Create one stable run ID, reuse it across issues/workers, and record a run comment for each issue in scope. Record timestamps at actual stage boundaries and explicitly mark blocking waits; do not derive timings from labels, status text or chat history. The orchestrator is the single writer for each issue/run record. If timing instrumentation fails, report metrics as unavailable and continue the workflow.

The report separates issue/milestone calendar duration, registered stage work, declared waits, rework and CI/review evidence. Registered work is measured wall-clock time in marked stage windows minus declared waits; it is not model-internal thinking time. Parallel workers may make summed work exceed calendar duration. Use milestone medians and show P90 only with at least five samples. Missing model/token/cost data stays unavailable.

After an issue or milestone completes, kaizen may use the report as additional evidence. Consider timings together with sample size, repeated work, CI failures and review findings. A single slow step is not sufficient to change the process. Never change gates automatically from timing metrics; if no recurring, evidence-backed improvement is justified, report `NO PROCESS CHANGE`.

## Proportionate test coverage

Apply [TEST_STRATEGY.md](TEST_STRATEGY.md) automatically in planning, Apply and review. Extend the existing OpenSpec evidence matrix with scenario, acceptance criterion/concrete risk, proving layer and existing/new test. Choose representative coverage and deepen it for affected high-risk behavior; avoid exhaustive combinations and duplicated rule matrices between unit, integrated and GraphQL tests. Reuse fixtures, diagnose after two attempts without progress on the same failure, and preserve final required checks. Reviewers requesting extra tests must identify the concrete failure current evidence would miss. Stop expanding scenarios when the agreed criteria and identified risks are proven and applicable checks pass. No extra owner approval or workflow stage is required.

## Automatic CI performance expertise

Apply [CI_PERFORMANCE.md](CI_PERFORMANCE.md) in the existing stages. issue-audit diagnoses relevant issues; implement-issue and apply-issue use optimize-ci; prepare-pr self-reviews and pr-audit independently verifies relevant CI/test-infrastructure changes. post-pr-audit checks current evidence and kaizen diagnoses recurring slowdown. The orchestrator carries these hooks automatically and isolates comparable experiments. No new user command, lifecycle, routine approval or unconditional hosted benchmark is required.
