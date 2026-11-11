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

## Use

The installer and updater verify the package, a skill, and OpenSpec at the end. Open a new OpenCode session. On first use in a project, the agent checks OpenSpec integration and asks for authorization before initializing it; global installation does not modify projects. Check `/opsx-explore`, `/opsx-propose`, `/opsx-apply`, and `/opsx-archive` before implementing.

Ask **“Take care of this issue: URL”**, **“Take care of this project queue”**, or **“Take care of this milestone: URL”**; add **“no merge”** for manual integration. The workflow plans with OpenSpec, implements, tests, prepares the PR and reviews; default merge happens only after required checks pass. The agent needs GitHub access and isolated sessions/worktrees to run the full flow.

[Workflow guide and other resources](https://github.com/rocker-code/my-ai-skills/wiki/Workflow-guide) · [Legacy per-project installation](https://github.com/rocker-code/my-ai-skills/wiki/Legacy-installation) (not needed for global installation) · [Wiki](https://github.com/rocker-code/my-ai-skills/wiki)
