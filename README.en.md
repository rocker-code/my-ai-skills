# AI Engineering Workflow

[Português (Brasil)](README.md) · English

Skills and tools for issue-driven AI development. GitHub records decisions and delivery; OpenSpec structures planning and implementation.

## Workflow

The workflow starts with the Web agent: describe your need, and the skills inspect context and create/refine the GitHub issue. The CLI agent then receives the issue or milestone and handles planning, implementation and review.

The lifecycle moves through discovery, readiness, implementation, review and completion. OpenSpec is required; `openspec-workflow` governs exploration, proposals, exact-revision validation, implementation verification and archive.

![AI Engineering Workflow: from an idea to a Web-authored issue, then CLI planning, implementation, validation and merge.](docs/images/fluxo-my-ai-skills.en.svg)

[See the full workflow in the wiki](https://github.com/rocker-code/my-ai-skills/wiki/Workflow-guide).

## Install or update

Linux/macOS prerequisites: Git, Python 3.10+, `curl`, `gh`, `jq`, and OpenCode V2 on `PATH`. OpenSpec is required **to use the workflow**, but it need not be preinstalled: the installer preserves an existing CLI or installs the official standalone distribution for your user when missing. Authenticate GitHub CLI separately with `gh auth login`.

Run the installer directly from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/rocker-code/my-ai-skills/main/scripts/install.sh | sh
```

The script installs the latest `main` revision. It downloads a pinned **installer**, checks its SHA-256, and then uses it to install the current revision. If `curl` fails, it reports the error, but the pipeline may still report success without installing anything. **This check does not verify the launcher itself when fetched from `main`**: review [its code](scripts/install.sh) before running it, or use the [verified-entrypoint command](https://github.com/rocker-code/my-ai-skills/wiki/Global-installation) for stronger assurance.

To **update to the latest `main` revision**, run this only when you want an update:

```bash
curl -fsSL https://raw.githubusercontent.com/rocker-code/my-ai-skills/main/scripts/update.sh | sh
```

**Both commands install the latest revision when run.** `update.sh` simply makes the intent to update explicit; it trusts current `main` and invokes the same verified installer. Neither updates in the background. Do not use `npx skills update` or the active installation's installer to update the bundle. [Details, conflicts and migration](https://github.com/rocker-code/my-ai-skills/wiki/Global-installation).

## Configure the Web agent project

To use both skills in project conversations, make a GitHub connector or equivalent authorized integration available with access to `rocker-code/my-ai-skills` and the target repositories. Copy the block below into the **Web agent's project instructions** (ChatGPT, Claude or equivalent). It directs the agent to current GitHub instructions; it does not automatically install skills or change account settings.

You do not need to attach skill files to every conversation when the connector can read them. Detailed rules live in versioned protocols: updates become available after merging into `main`. Update the project configuration if this routing text itself changes. If source access fails, the agent must report which files it could not read instead of claiming to have applied the latest version.

The same text can be used in ChatGPT, Claude or another agent that accepts persistent project descriptions. Capabilities depend on the environment: reading instructions does not grant GitHub access or permission to create issues. Without a write integration, the agent may prepare a draft while stating that it was not published.

### Instructions to copy

```text
# Rocker Code — Project Instructions

This project uses AI Engineering Workflow, available at
https://github.com/rocker-code/my-ai-skills, as its reference
for software engineering and GitHub issue management.

## Web agent skills (ChatGPT, Claude or equivalent)

Use these instructions in ChatGPT, Claude or another agent with project instructions.
The chatgpt-web-* names are retained for compatibility. Source read access is required;
issue mutations require an authorized GitHub integration.

At the start of each issue creation or review task, use the available GitHub
integration to read the current main version of the relevant skill and shared protocol:

- Creation: skills/chatgpt-web-create-issue/SKILL.md
- Review/refinement: skills/chatgpt-web-refine-issue/SKILL.md
- Protocol: protocol/CHATGPT_WEB_ISSUES.md
- Visual design, when applicable: protocol/VISUAL_ARTIFACTS.md

For quick roadmap queries (“me situa”, “where are we”, “how is the MVP”,
“what should I do next”), read skills/roadmap-status/SKILL.md on main through
GitHub integration and follow it. Show up to 5 table rows, one next step and
pending decisions; disclose access limitations and do not execute changes.

When I ask “update my-ai-skills” or “update this project’s AI workflow”, read
skills/update-ai-workflow/SKILL.md on main and follow it. Run only on explicit
request, preserving agents, scope and local changes. If local execution is
unavailable, report the limitation and give the next required CLI command;
do not claim my local installation was updated.

Also read the necessary references linked by these files. Reuse the reads within
the same task; refresh them after relevant changes. If a source is inaccessible,
report the limitation and do not invent its contents.

## Rules

- Apply the appropriate skill without requiring special commands.
- Inspect issues, comments, decisions, PRs and relevant code; identify the inspected
  revision and existing implementation to avoid duplicate work.
- Preserve Magento, Mobile and Operational App conventions. Distinguish verified
  facts, approved decisions, proposals and open questions.
- Start each issue with a plain summary: what changes, where and what it depends on.
  Define expected behavior, scope, non-goals and observable acceptance criteria.
- Include test scenarios in a table with setup/action, expected result and suggested
  proving layer. Focus on real risks, reuse tests and fixtures and avoid exhaustive
  matrices or duplicate coverage.
- For integrations, document current and expected signatures, examples, states,
  errors, authorization and producer/consumer dependencies. Mark proposed contracts
  as unimplemented/unfrozen; record the effective signature after the handoff
  before final integration.
- For backend, integration or architecture changes, include a simple Mermaid system
  design with verifiable responsibilities and data flow.
- For interfaces, include a character wireframe in a text block, key states/actions
  and accessible, versioned, approved visual references when a design exists.
  Illustrative values are not real data. Follow VISUAL_ARTIFACTS.md; a private
  Claude Artifacts link alone does not prove design access.
- For user-facing content, include i18n and translation using the project's existing
  mechanism and locale: copy, states, errors, accessibility, dates, numbers, currency
  and plurals. Define who localizes API text; do not expose raw enums or keys.
  Preserve domain names/data and provide safe translated fallbacks for unknown
  codes, with representative acceptance criteria and tests.
- Keep behavior, design, wireframes, contract, criteria and tests consistent.
  Narrow changes must preserve unrelated content and decisions.
- Explain technical questions and alternatives simply when a material user decision
  is pending. Resolve routine details through evidence and do not request extra
  confirmation for actions already requested or authorized.
- Record approved decisions in issues when requested. Verify GitHub mutations before
  claiming success and provide links and remaining blockers.
- Do not implement code while authoring/refining issues; execution follows the CLI
  workflow with OpenSpec. Do not invent inspected code, contracts, attachments
  or executed tests.

## Working style

Accept natural requests such as:
- "Create an issue for..."
- "Analyze issue #123."
- "Answer the question in this issue."
- "Review the milestone's issues."
- "Update the specification using the attached design."

Do not require the user to repeat these instructions.
```

## Use

The installer and updater verify the package, a skill, and OpenSpec at the end. Open a new OpenCode session. On first use in a project, the agent checks OpenSpec integration and asks for authorization before initializing it; global installation does not modify projects. Check `/opsx-explore`, `/opsx-propose`, `/opsx-apply`, and `/opsx-archive` before implementing.

Ask **“Take care of this issue: URL”**, **“Take care of this project queue”**, or **“Take care of this milestone: URL”**; add **“no merge”** for manual integration. The workflow plans with OpenSpec, implements, tests, prepares the PR and reviews; default merge happens only after required checks pass. The agent needs GitHub access and isolated sessions/worktrees to run the full flow.

PR preparation invokes `update-changelog` to record meaningful changes under **Unreleased**, updating the existing file or creating `CHANGELOG.md`. The `release` skill consolidates version entries before final validation. You can also ask “generate the changelog” directly.

[Workflow guide and other resources](https://github.com/rocker-code/my-ai-skills/wiki/Workflow-guide) · [Legacy per-project installation](https://github.com/rocker-code/my-ai-skills/wiki/Legacy-installation) (not needed for global installation) · [Wiki](https://github.com/rocker-code/my-ai-skills/wiki)
