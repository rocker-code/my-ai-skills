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

1. Refine the GitHub issue.
2. Explore issue, all comments, code, tests, docs and current OpenSpec. Do not implement.
3. Add material ambiguities as `[QUESTION]` and stop.
4. Record approved answers as `[DECISION]`.
5. Refresh GitHub and explore again after decisions.
6. Pass `issue-ready`.
7. Create or update OpenSpec proposal/spec/design/tasks.
8. Review the proposal before apply for medium or large changes.
9. Implement only after the gate passes.
10. Self-review, test and prepare the PR.
11. Independently review against issue + decisions + OpenSpec + diff + architecture.
12. Address valid feedback and run `final-pr-review`.
13. Perform `final-review`; merge after `FINAL REVIEW: APPROVED`.

## Checkpoint reuse

Agents resume rather than restart:

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
