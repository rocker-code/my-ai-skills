# AI Development Workflow

## Source of truth

GitHub is the shared memory for people and agents. OpenSpec is the validated behavioral and architectural contract for this workflow. The repository is current implementation reality; tests are executable evidence.

The latest explicit approved decision supersedes older conflicting discussion. Do not silently infer a material product or architectural decision.

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
3. Add material ambiguities as `[QUESTION]` and stop.
4. Record approved answers as `[DECISION]`.
5. Refresh GitHub and run `/opsx-explore` again after decisions.
6. Pass `issue-ready`.
7. Run `/opsx-propose` to create or update OpenSpec proposal/spec/design/tasks.
8. Validate each proposal with the official OpenSpec command and a traceability review against the issue, decisions, current code, architecture and tests. Use an independent planning reviewer when available for material boundary changes; record the exact immutable proposal revision and review evidence. Show a consolidated progress summary without pausing for blanket owner approval. Stop only on a material decision that evidence and project policy cannot resolve, or if validation fails.
9. Use `openspec-workflow` as the canonical proposal and closeout procedure. Start a genuinely new child session per issue with `apply-issue`; verify the pinned validated revision, review evidence and durable handoff, then run `/opsx-apply`. For milestones, schedule these sessions dynamically by dependency and conflict risk. ai-memory is supplementary.
10. After Apply, complete focused tests and supported OpenSpec implementation verification; strictly validate the active change and archive it on the feature branch after all gates pass. Inspect the archived artifacts and synchronized live specs so they enter the same issue PR. Then self-review and invoke `/prepare-pr` with requirement → code → test evidence. This invocation authorizes staging only issue-scoped files, committing, pushing the feature branch without force, and opening the PR; no second confirmation is needed. Preserve unrelated work. This does not authorize merge, release, deploy or force-push. If the owner explicitly says prepare-only, stop at `READY FOR PR`.
11. Independently run `pr-audit`, with `architecture-audit` for boundary changes. Route valid findings to `github-resolution`, which invokes `address-pr-review` for corrections on the same PR branch.
12. After corrections, refresh `pr-audit` on the current materially changed head; run an independent `post-pr-audit` as the final review and merge eligibility gate. A newer push invalidates affected audit, review and test evidence.
13. By default use `merge_mode=auto-if-green` for the selected run: `post-pr-audit` may merge after all gates pass, or enable GitHub auto-merge while checks are pending only when repository rules enforce every applicable check and review. A direct "do not merge" or `merge_mode=manual` request overrides the default and ends at READY_TO_MERGE. Never bypass repository policy; verify the merged PR and issue closure, then run `kaizen` before hard dependents.

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
- API/GraphQL/data contracts, errors and edge cases are defined when relevant;
- dependencies and cross-repository sequencing are known;
- test expectations and acceptance criteria are observable;
- approved decisions are recorded;
- no blocking `[QUESTION]` remains.

## Stop conditions

Stop and record a `[QUESTION]` when ambiguity materially changes behavior, data, public contract, authorization, concurrency, compatibility or scope. Do not use assumptions to bypass the READY gate.

During implementation, if new evidence changes the validated contract, stop the affected work, update the issue/OpenSpec, rerun proposal review and validation, and resume in the required fresh implementation context. Seek the owner only for an unresolved material product/architecture decision.

## Automatic CI performance expertise

Apply [CI_PERFORMANCE.md](CI_PERFORMANCE.md) in the existing stages. issue-audit diagnoses relevant issues; implement-issue and apply-issue use optimize-ci; prepare-pr self-reviews and pr-audit independently verifies relevant CI/test-infrastructure changes. post-pr-audit checks current evidence and kaizen diagnoses recurring slowdown. The orchestrator carries these hooks automatically and isolates comparable experiments. No new user command, lifecycle, routine approval or unconditional hosted benchmark is required.
