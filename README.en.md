# AI Engineering Workflow

[Português (Brasil)](README.md) · English

Skills and tools for issue-driven AI development. GitHub records decisions and delivery; OpenSpec structures planning and implementation.

## Install or update (OpenCode)

Linux/macOS prerequisites: Git, Python 3.10+, `curl`, `gh`, `jq`, and OpenCode V2 on `PATH`. OpenSpec is required **to use the workflow**, but it need not be preinstalled: the installer preserves an existing CLI or installs the official standalone distribution for your user when missing. Authenticate GitHub CLI separately with `gh auth login`.

Run the installer directly from GitHub:

```bash
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rocker-code/my-ai-skills/main/scripts/install.sh | sh'
```

The script downloads a pinned installer, checks its SHA-256, and only then executes it. **This check does not verify the launcher itself when fetched from `main`**: review [its code](scripts/install.sh) before running it, or use the [verified-entrypoint command](https://github.com/rocker-code/my-ai-skills/wiki/Global-installation) for stronger assurance.

To **update to the latest `main` revision**, run this only when you want an update:

```bash
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/rocker-code/my-ai-skills/main/scripts/update.sh | sh'
```

`update.sh` trusts current `main` and calls the installer with the resolved revision; the installer's entrypoint SHA-256 check remains in place. It does not verify the launcher itself when fetched from `main`. **Re-running `install.sh` does not automatically fetch the latest revision.** Do not use `npx skills update` or the active installation's installer to update the bundle. [Details, conflicts and migration](https://github.com/rocker-code/my-ai-skills/wiki/Global-installation).

## Verify and use

```bash
test -f "${XDG_DATA_HOME:-$HOME/.local/share}/my-ai-skills/active/manifest.json"
test -f "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills/apply-issue/SKILL.md"
openspec --version
```

Open a new OpenCode session. On first use in a project, the agent checks OpenSpec integration and asks for authorization before initializing it; global installation does not modify projects. Check `/opsx-explore`, `/opsx-propose`, `/opsx-apply`, and `/opsx-archive` before implementing.

Ask **“Take care of this issue: URL”**, **“Take care of this project queue”**, or **“Take care of this milestone: URL”**; add **“no merge”** for manual integration. The workflow plans with OpenSpec, implements, tests, prepares the PR and reviews; default merge happens only after required checks pass. The agent needs GitHub access and isolated sessions/worktrees to run the full flow.

[Workflow guide and other resources](https://github.com/rocker-code/my-ai-skills/wiki/Workflow-guide) · [Legacy per-project installation](https://github.com/rocker-code/my-ai-skills/wiki/Legacy-installation) (not needed for global installation) · [Wiki](https://github.com/rocker-code/my-ai-skills/wiki)
