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
refine issue
→ /opsx-explore (using the issue-explore protocol)
→ [QUESTION] / [DECISION] loop when needed
→ /opsx-explore again after decisions
→ issue-ready
→ /opsx-proposal
→ proposal review
→ /opsx-apply
→ prepare-pr
→ independent review
→ address-pr-review
→ final-pr-review + final-review
→ merge
```

For milestone execution, invoke `milestone-orchestrator` with the GitHub milestone URL. It runs one issue at a time by default, pins validated OpenSpec artifacts to a commit, then starts `apply` in a genuinely new session. If isolated sessions are unavailable, it stops with a handoff instead of applying in the planning context.

Production implementation does not begin while blocking questions remain or before the OpenSpec readiness gate passes. A second exploration after decisions is mandatory for material changes.

## Skills

### Shared workflow

| Skill | Responsibility |
|---|---|
| `milestone-orchestrator` | Order milestone issues by dependency and hand each issue across isolated OpenSpec planning, apply and verification sessions. |
| `issue-explore` | Add the supervised GitHub question/output protocol to OpenSpec's official CLI command `/opsx-explore`; it is not a replacement CLI command. |
| `issue-ready` | Re-read decisions and enforce the Definition of Ready. |
| `implement-issue` | Resume from completed checkpoints, run OpenSpec-first implementation and leave work ready for a PR. |
| `openspec-workflow` | Maintain proposal, specs, design and tasks as a pre-code contract. |
| `prepare-pr` | Self-review, validate and create/prepare a traceable PR. |
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
  --skill issue-explore \
  --skill issue-ready \
  --skill implement-issue \
  --skill prepare-pr \
  --skill address-pr-review \
  --skill final-pr-review \
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

## Recommended cross-repository flow

For backend → mobile work:

1. merge backend contract issues;
2. run `contract-handoff` against the final backend code and the mobile issue;
3. update the consumer issue if necessary;
4. declare `CONTRACT FROZEN`;
5. only then implement the consumer.

If the producer contract changes after the freeze, explicitly revise the consumer issue and repeat the handoff.
