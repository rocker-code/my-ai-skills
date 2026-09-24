# my-ai-skills

Reusable skills and tools for a supervised, issue-driven AI software development lifecycle using GitHub, OpenSpec, ChatGPT, Codex, Claude and Claude Code.

The repository defines one shared protocol across two operating layers:

- **Web / coordination:** requirements, decisions, architecture, contract handoff and independent review.
- **CLI / execution:** repository exploration, OpenSpec, implementation, tests, PR preparation and review fixes.

GitHub is the source of truth. Material decisions must end up in an issue, PR, architecture document, OpenSpec artifact or code—not only in chat history.

## Lifecycle

```text
DISCOVERY → READY → IMPLEMENTING → REVIEW → DONE
```

For repositories with OpenSpec:

```text
issue-audit → refine issue
→ /opsx-explore (using the issue-explore protocol)
→ [QUESTION] / [DECISION] loop when needed
→ /opsx-explore again after decisions
→ issue-ready
→ /opsx-proposal
→ explicit human approval of pinned revision
→ new session: apply-issue (/opsx-apply)
→ verify implementation, finish tasks, strict validate
→ archive OpenSpec on feature branch (sync delta specs into live specs)
→ /prepare-pr (requirement → code → test; scoped commit, push and PR)
→ independent pr-audit + architecture-audit when relevant
→ address-pr-review
→ final-pr-review + post-pr-audit + final-review
→ merge → kaizen
```

Invoking `/prepare-pr` authorizes the skill to stage and commit only files for the current issue, push its feature branch without force, and open the PR. It does not authorize merging. Explicitly requesting a prepare-only run keeps the work local.

After implementation and tests pass, archive the completed OpenSpec change on the feature branch before `/prepare-pr`. The archive and synchronized live specs belong in the same issue PR, avoiding a follow-up archive-only PR. During PR audits, review the approved change under `openspec/changes/archive/` together with live specs.

For milestone execution, invoke `milestone-orchestrator` **once** with the milestone URL. It inventories all issues, builds a dependency DAG, and schedules independent work in isolated child sessions/worktrees while serializing hard dependencies and likely file conflicts. It prepares eligible OpenSpec proposals as a batch for one owner approval checkpoint (each exact SHA still needs explicit approval), then automatically runs fresh Apply sessions, tests, verification, archive, PR preparation, independent audits and CI. The default is manual merge; an explicit `merge_mode=auto-if-green` opts a specific run into GitHub auto-merge only after all required checks, reviews and branch protections pass. Blocked issues do not stop unrelated work. If the runtime lacks child-session/worktree capability, it reports the missing capability instead of claiming end-to-end automation.

Production implementation does not begin while blocking questions remain or before the OpenSpec readiness gate passes. A second exploration after decisions is mandatory for material changes.

## Skills

### Shared workflow

| Skill | Responsibility |
|---|---|
| `milestone-orchestrator` | Run one milestone invocation across all eligible issues; batch proposal approvals, dynamically schedule isolated workers, run fresh Apply and independent audits, then manual or explicitly opted-in auto-merge. |
| `issue-explore` | Add the supervised GitHub question/output protocol to OpenSpec's official CLI command `/opsx-explore`; it is not a replacement CLI command. |
| `issue-ready` | Re-read decisions and enforce the Definition of Ready. |
| `issue-audit` | Verify the issue's claims against current code before exploration. |
| `implement-issue` | Audit, explore and propose; stop at human approval without implementing. |
| `apply-issue` | Implement an approved OpenSpec revision in a new session. |
| `openspec-workflow` | Maintain proposal, specs, design and tasks as a pre-code contract. |
| `prepare-pr` | Self-review, validate and create/prepare a traceable PR. |
| `pr-audit` | Independently compare requirements, OpenSpec, code and tests. |
| `architecture-audit` | Check boundaries and new coupling without requiring LikeC4. |
| `post-pr-audit` | Verify the final PR head, CI and review findings before merge. |
| `kaizen` | Convert evidenced failures into focused project or process improvements. |
| `address-pr-review` | Refresh feedback, fix valid review findings and reply with evidence. |
| `final-pr-review` | Executor-side final check before external review. |
| `pr-status` | Read-only classification of the current PR state and next action. |
| `contract-handoff` | Freeze an implemented backend contract and validate/update the consumer issue. |

### Web supervision

| Skill | Responsibility |
|---|---|
| `refine-issue` | Convert an idea or draft issue into an implementable specification. |
| `resolve-questions` | Analyze `[QUESTION]` comments and record evidence-backed `[DECISION]` responses. |
| `review-pr` | Compare issue, decisions, OpenSpec, architecture, diff and tests with review severities. |
| `final-review` | Enforce Review Freeze: no scope expansion, only merge-blocking validation. |

### Domain checks

| Skill | Responsibility |
|---|---|
| `magento-review` | Adobe Commerce/Magento architecture and implementation checklist, including native reuse and concurrency. |
| `expo-mobile-review` | Expo/React Native navigation, state, GraphQL, resilience, accessibility and E2E checklist. |
| `sonar` | Agent-agnostic SonarQube CLI quality/security analysis, secret scanning, finding classification and remediation evidence. |

## GitHub protocol

Discussion markers:

```text
[QUESTION]
[DECISION]
[IMPLEMENTATION NOTE]
[RESOLVED]
```

Review severities:

```text
[BLOCKER]
[MUST FIX]
[SHOULD FIX]
[NICE TO HAVE]
```

Read [AI_WORKFLOW.md](protocol/AI_WORKFLOW.md), [GITHUB_CONVENTIONS.md](protocol/GITHUB_CONVENTIONS.md) and [REVIEW_POLICY.md](protocol/REVIEW_POLICY.md) for the canonical rules.

## Helper scripts

The scripts require `gh` and `jq` and are read-only:

```bash
scripts/issue-context https://github.com/owner/repo/issues/123
scripts/pr-context https://github.com/owner/repo/pull/124
scripts/workflow-status https://github.com/owner/repo/issues/123
```

They normalize live GitHub context so agents refresh comments, decisions, reviews and CI instead of relying on stale chat context.

## Install with skills.sh

Install everything for OpenCode:

```bash
npx skills add rocker-code/my-ai-skills --all -a opencode
```

Install globally:

```bash
npx skills add rocker-code/my-ai-skills --all -a opencode -g
```

Install selected skills:

```bash
npx skills add rocker-code/my-ai-skills \
  --skill milestone-orchestrator \
  --skill issue-audit \
  --skill issue-explore \
  --skill issue-ready \
  --skill implement-issue \
  --skill apply-issue \
  --skill sonar \
  --skill prepare-pr \
  --skill pr-audit \
  --skill architecture-audit \
  --skill address-pr-review \
  --skill final-pr-review \
  --skill final-review \
  --skill post-pr-audit \
  --skill kaizen \
  -a opencode
```

For a private repository, configure GitHub authentication in the environment used by `skills.sh`.

## Install as a personal ChatGPT/Codex plugin

The repository also contains a self-contained skills-only plugin at `plugins/my-ai-skills` and a repository marketplace at `.agents/plugins/marketplace.json`.

Add the marketplace once:

```bash
codex plugin marketplace add rocker-code/my-ai-skills --ref main
```

Install the plugin:

```bash
codex plugin add my-ai-skills@rocker-code-ai
```

In the ChatGPT desktop app, restart the app, open the Plugins Directory, select the **Rocker Code AI** marketplace, and install **Rocker Code AI Workflow**. Start a new conversation after installation so the skills are loaded.

The plugin is personal and does not need to be submitted to the public directory. Publishing it to a ChatGPT workspace is a separate administrative action.

The root `skills/`, `protocol/`, `templates/`, and helper scripts remain the canonical source used by `skills.sh`. Their copies inside `plugins/my-ai-skills/` form the self-contained plugin package. After changing canonical files, synchronize the package with:

```bash
scripts/sync-plugin
```

## Milestone operating rules

- Invoke with a milestone URL. The first output is a dependency inventory and the next unblocked issue, including evidence for the proposed order.
- Status is reconstructed from issue decisions, committed OpenSpec revision, PR head, reviews and CI. A helper's inferred status or ai-memory summary cannot grant an approval.
- Keep one issue active by default; parallel work needs explicit authorization and verified isolation. Resolve dependency cycles and unclear links before work on affected issues.
- The owner approves the exact proposal SHA and later decides the merge. The orchestrator does not merge, close issues, release or deploy.
- If a new implementation session is unavailable, keep the committed plan and return a copyable handoff. A failed or interrupted run resumes at its last verified gate.
- A merged PR and closed issue are verified before kaizen. ghpending is optional for daily triage; GitHub Project is a product planning view.

## Recommended cross-repository flow

For backend → mobile work:

1. merge backend contract issues;
2. run `contract-handoff` against the final backend code and the mobile issue;
3. update the consumer issue if necessary;
4. declare `CONTRACT FROZEN`;
5. only then implement the consumer.

If the producer contract changes after the freeze, explicitly revise the consumer issue and repeat the handoff.