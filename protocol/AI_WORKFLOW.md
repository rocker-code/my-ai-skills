# AI Development Workflow

## Source of truth

GitHub is the shared memory for people and agents. OpenSpec is the approved behavioral and architectural contract when present. The repository is current implementation reality; tests are executable evidence.

The latest explicit approved decision supersedes older conflicting discussion. Do not silently infer a material product or architectural decision.

## States

| State | Predominant role | Exit condition |
|---|---|---|
| `DISCOVERY` | Web supervisor + owner + executor exploration | Problem, current implementation, dependencies and questions are understood. |
| `READY` | Web supervisor / architecture | Definition of Ready passes and no blocking question remains. |
| `IMPLEMENTING` | Codex/Claude Code + OpenSpec | Approved contract implemented and validated. |
| `REVIEW` | Independent reviewer + executor fix loop | Requirements, decisions, spec, diff and tests agree. |
| `DONE` | Owner | PR approved and merged; issue closed according to repository policy. |

## Required flow

1. Run `issue-audit` against the live issue and current code; refine material gaps.
2. Run `/opsx-explore` against the issue, all comments, code, tests, docs and current OpenSpec. Do not implement.
3. Add material ambiguities as `[QUESTION]` and stop.
4. Record approved answers as `[DECISION]`.
5. Refresh GitHub and run `/opsx-explore` again after decisions.
6. Pass `issue-ready`.
7. Run `/opsx-proposal` to create or update OpenSpec proposal/spec/design/tasks.
8. Present eligible milestone proposals together for one owner checkpoint. Record explicit human approval separately for each exact validated proposal revision; do not start Apply for an unapproved SHA.
9. Use `openspec-workflow` as the canonical procedure for proposal approval and closeout. Start a genuinely new child session per issue with `apply-issue`; verify approval and durable handoff, then run `/opsx-apply`. For milestones, schedule these sessions dynamically by dependency and conflict risk. ai-memory is supplementary.
10. After Apply, complete focused tests and supported OpenSpec implementation verification; strictly validate the active change and archive it on the feature branch after all gates pass. Inspect the archived artifacts and synchronized live specs so they enter the same issue PR. Then self-review and invoke `/prepare-pr` with requirement → code → test evidence. This invocation authorizes staging only issue-scoped files, committing, pushing the feature branch without force, and opening the PR; no second confirmation is needed. Preserve unrelated work. This does not authorize merge, release, deploy or force-push. If the owner explicitly says prepare-only, stop at `READY FOR PR`.
11. Independently run `pr-audit`, with `architecture-audit` for boundary changes. Route valid findings to `github-resolution`, which invokes `address-pr-review` for corrections on the same PR branch.
12. After corrections, refresh `pr-audit` on the current materially changed head; run an independent `post-pr-audit` as the final review and merge eligibility gate. A newer push invalidates affected audit, review and test evidence.
13. In manual mode report READY_TO_MERGE after required CI and reviews pass. An explicit request to merge when green or `merge_mode=auto-if-green` authorizes `post-pr-audit` to merge after all gates pass, or to enable GitHub auto-merge while checks are pending only when repository rules enforce every applicable check and review. Never bypass repository policy; verify the merged PR and issue closure, then run `kaizen` before hard dependents.

## Milestone execution

Invoke `milestone-orchestrator` once with a milestone URL. It inventories all issues, builds an evidence-backed dependency DAG and schedules eligible work automatically. It batches proposal reviews into one owner checkpoint while preserving explicit approval for each exact OpenSpec SHA; after approval, fresh child sessions run Apply, tests, verification, archive, prepare-pr and independent audits. Concurrency is calculated from hard dependencies, expected code conflicts, isolated worktrees and runtime/CI capacity; dependent work waits for merged prerequisites while independent work continues. Missing decisions block only the affected issue/dependents. The default merge mode is manual; `auto-if-green` must be explicitly selected for a run and never bypasses branch protections, required reviews, or checks. The ledger comes from GitHub issues, decisions, artifacts, PRs and exact-head CI; ai-memory is supplementary. After verified merge, run kaizen before hard dependents. ghpending is optional triage, and GitHub Project is a product view.

## Checkpoint reuse

Agents resume rather than restart. An approval gate and a fresh-session gate cannot be waived by checkpoint reuse:

- reuse a matching validated OpenSpec change;
- treat existing `[DECISION]` comments as authoritative;
- continue an existing implementation rather than recreate it;
- when a PR exists, switch to review/fix flow;
- always refresh comments newer than the previous execution.

## Definition of Ready

- objective and problem are explicit;
- expected behavior, scope and non-goals are defined;
- current implementation and existing native mechanisms were inspected;
- business rules, authorization and state transitions are defined when relevant;
- API/GraphQL/data contracts, errors and edge cases are defined when relevant;
- dependencies and cross-repository sequencing are known;
- test expectations and acceptance criteria are observable;
- approved decisions are recorded;
- no blocking `[QUESTION]` remains.

## Stop conditions

Stop and record a `[QUESTION]` when ambiguity materially changes behavior, data, public contract, authorization, concurrency, compatibility or scope. Do not use assumptions to bypass the READY gate.

During implementation, if new evidence changes the approved contract, stop the affected work, update the issue/OpenSpec and revalidate before continuing.
