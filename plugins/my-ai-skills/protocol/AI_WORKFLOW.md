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
8. Record explicit human approval of the exact validated proposal revision. Stop the planning session.
9. Start a genuinely new implementation session with `apply-issue`; verify approval and durable handoff, then run `/opsx-apply`. ai-memory is supplementary.
10. Self-review, test and `prepare-pr` with requirement → code → test evidence.
11. Independently run `pr-audit`, and `architecture-audit` for boundary changes; address valid feedback.
12. Run `final-pr-review`, `post-pr-audit` and independent `final-review` against the final PR head.
13. Merge only after required CI, reviews and owner's decision; run `kaizen` after merge.

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
