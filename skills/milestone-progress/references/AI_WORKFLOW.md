# AI Development Workflow

## Sources and engineering principles

GitHub owns backlog, approved decisions and delivery; OpenSpec is the behavioral contract; code is implementation reality; executed tests and CI are verification evidence. Reuse existing artifacts and repository conventions. The latest explicit approved decision supersedes conflicting older discussion.

- **Write good code:** inspect callers and established architecture before adding layers. Prefer straightforward maintainable code, native APIs and reuse over speculative abstraction.
- **Verify effectively:** use native OpenSpec Verify when supported, deterministic static checks, focused tests, required suites/CI and genuinely independent risk-proportionate review. Advisory Verify never substitutes for executed tests or required human reviews.
- **Identify meaningful improvements:** register only independently valuable, actionable, untracked evolutions under [INCREMENTAL_DELIVERY.md](https://github.com/rocker-code/my-ai-skills/blob/main/protocol/INCREMENTAL_DELIVERY.md). Cosmetic, speculative or duplicate suggestions create no issue or milestone.

Before adding any skill, wrapper, protocol, persistent record or stage, demonstrate a gap in native OpenSpec, agent capabilities, project tools and conventions. Do not create another framework or mandatory quality gate.

## Native issue lifecycle

[openspec-workflow](https://github.com/rocker-code/my-ai-skills/blob/main/skills/openspec-workflow/SKILL.md) is the small integration adapter; native OpenSpec 2.0 skills own Explore → Propose → Apply → Verify → Archive. Discover actual installed capabilities; never invent commands or simulate a missing native skill.

1. In Explore, inspect live issue/decisions, existing PR/change, code/tests, repository rules, dependencies and approved designs. Check existence, scope, authorization, contracts and test risks here; no separate audit/ready gate or mandatory second exploration. Resume matching artifacts. An existing PR enters review/fix, not duplicate planning.
2. Propose only the agreed scope, using native OpenSpec. Validate and review the exact proposal revision; pin it with acceptance → implementation plan → proving test traceability. Use independent planning review for material boundary changes when supported. The agent approves evidence-backed proposals and continues without routine owner approval.
3. Start Apply in a genuinely fresh implementation context after the planning writer stops and [WORKTREES.md](https://github.com/rocker-code/my-ai-skills/blob/main/protocol/WORKTREES.md) ownership is transferred. Verify pinned proposal, validation/review and actual dependency commits. Unknown capabilities block only the affected action, never create invented independence. Apply native instructions, [TEST_STRATEGY.md](https://github.com/rocker-code/my-ai-skills/blob/main/protocol/TEST_STRATEGY.md), project/M2T checks and approved contracts. Optional [simplify](https://github.com/rocker-code/my-ai-skills/blob/main/skills/simplify/SKILL.md) runs inside Apply only for a concrete maintainability problem or explicit request.
4. Enable official `openspec-verify-change` when supported by the installed profile/runtime and invoke it by default after Apply. A missing generated file is not evidence of incompatibility; inspect official configuration and preserve existing choices during enablement. Report unsupported capability or actual enablement failure precisely. Resolve findings or document them according to severity; do not manufacture another audit. Strictly validate and archive on the feature branch with native OpenSpec, inspecting synchronized specs and archive.
5. Prepare the issue-scoped PR with actual proof, archived contract and changelog. Commit all archive/distribution/preparation changes before the final required local suite on the exact clean HEAD; keep its proof ID outside the commit. Any later commit invalidates that final gate. `workflow-evidence` verifies local proofs/bundles where installed; metadata alone is not passing proof and hosted CI cannot replace a mandatory local gate.
6. Obtain one genuinely independent [pr-audit](https://github.com/rocker-code/my-ai-skills/blob/main/skills/pr-audit/SKILL.md) on the final HEAD under [REVIEW_POLICY.md](https://github.com/rocker-code/my-ai-skills/blob/main/protocol/REVIEW_POLICY.md), with domain/security review as warranted. Reuse valid review of the same immutable HEAD and context. After corrections, independently review affected surfaces and rerun invalidated proofs; do not repeat a full audit without relevant changes. [github-resolution](https://github.com/rocker-code/my-ai-skills/blob/main/skills/github-resolution/SKILL.md) handles actionable feedback and merge eligibility, not another implementation lifecycle.

Material changes to behavior, data, authorization, architecture or public contracts pause only affected work: update issue/OpenSpec, review and validate the revised exact proposal before continuing. Resolve researchable facts from code, official behavior and existing decisions. Escalate only unresolved material choices, unrequested scope, irreversible actions or material external cost/commitment. Never weaken an approved criterion to pass a gate.

## Queue and merge

### Native execution boundaries

OpenCode and Codex consume the same skills and policies; neither requires the
other CLI. Use only tools/sessions actually available in the selected runtime.
For Codex, a new `codex exec --json --cd <checkout>` without `resume`, `fork` or
an inherited transcript is a candidate fresh context: confirm its native
thread/session ID, effective input and terminal completion. Distinct processes,
help text and feature flags alone do not prove independence or subagent support.
OpenCode uses its available native session tools and completion callbacks.

Correlate every result with its native identity, issue, checkout and immutable
input/output SHA. Reject another worker's callback; never reuse the owner's ID,
invent an identity environment variable or derive identity from a PID. When a
worker cannot access its native ID, the runtime must supply it with verifiable
provenance before reservation verification. An independent reviewer uses a
distinct verified execution, immutable input and read-only scope; `codex review`
alone does not certify the complete project review contract. If delegation is
unproven, use distinct native executions with verified completion; if insufficient,
block only that action with a concrete next step in the same selected CLI.

Agent switching transfers durable Git/GitHub/OpenSpec/worktree evidence, never
live chat history. Prove the old writer stopped, reconcile and transfer its
reservation, reuse the existing change/PR, and rerun incomplete or invalidated
tests. Unknown completion, credentials or capabilities remain unknown, not
approval, delivery or a reason to silently switch agents.

`milestone-orchestrator` selects a single issue, exact milestone or authorized repository queue. A single-issue request never authorizes prerequisites or siblings. Inventory dependencies and existing PRs read-only. **At most one active issue per selected queue**, including planning: finish or explicitly park it with reason, branch/revision and next action before starting another, even if independent. Subagents may work only within that active issue, with real runtime support, isolated resources and one writer per checkout. Cross-repository consumers require `contract-handoff` design review and frozen effective producer contract before integration; an unmerged hard prerequisite is not delivery.

Default `merge_mode=auto-if-green` applies only to the authorized scope; explicit manual/no-merge overrides it. Merge only after current HEAD, required checks, independent review, required human approvals, target/method and branch protection are verified. Pending/failed/missing/unknown required signals block merge. Native auto-merge is permitted only if GitHub enforces all applicable gates; otherwise wait and recheck. Use the expected HEAD to reject a concurrent push, then verify actual merge/closure and any required merge-commit checks. Never force-push, deploy, release or bypass protection as a side effect.

After verified delivery, perform eligible safe housekeeping under WORKTREES and select the next issue. Kaizen is on demand or periodic, never a merge, cleanup or dependency prerequisite.

## Communication and recovery

Do not post routine GitHub issue/PR comments for stage transitions, worker handoffs, progress, retries, internal approvals, audit summaries or completion; no hidden structured run comments or replacement event log. Requirements/approved decisions belong in existing issue body and OpenSpec; delivery proof belongs in commits, PR description, checks and actual reviews. Comments are reserved for material questions not adequately represented in the body, owner-action blockers and actionable PR review discussion. Preserve historical comments; update canonical content without erasing unrelated decisions.

Resume from verified Git/GitHub/OpenSpec, worktree ownership, native runtime callbacks/queries and accessible test/CI evidence. Do not infer success from dispatch, transcript, container uptime, missing PID or absent test termination/report; keep unknown/incomplete state explicit. Reconcile old writer liveness and ownership before takeover, retain partial work and existing PR/change, and rerun only incomplete/invalidated obligations. No workflow event comments or timing analytics are required. Use current states queued, planning, implementing, reviewing, blocked and delivered with evidence on demand; status queries are read-only.

## Project-specific checks

Apply [TEST_STRATEGY.md](https://github.com/rocker-code/my-ai-skills/blob/main/protocol/TEST_STRATEGY.md), [WORKTREES.md](https://github.com/rocker-code/my-ai-skills/blob/main/protocol/WORKTREES.md), [REVIEW_POLICY.md](https://github.com/rocker-code/my-ai-skills/blob/main/protocol/REVIEW_POLICY.md), [VISUAL_ARTIFACTS.md](https://github.com/rocker-code/my-ai-skills/blob/main/protocol/VISUAL_ARTIFACTS.md) and [CI_PERFORMANCE.md](https://github.com/rocker-code/my-ai-skills/blob/main/protocol/CI_PERFORMANCE.md) only where relevant, reusing their existing safeguards rather than introducing new stages. CI performance work may measure project CI when explicitly in scope; workflow self-measurement and performance baselines are not delivery gates.
