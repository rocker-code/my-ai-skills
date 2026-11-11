# AI Engineering Workflow

[Português (Brasil)](README.md) · English

Skills and tools for issue-driven AI development. GitHub records decisions and delivery; OpenSpec structures planning and implementation.

## Install or update (OpenCode)

Linux/macOS prerequisites: Git, Python 3.10+, `curl`, `gh`, `jq`, and OpenCode V2 on `PATH`. OpenSpec is required **to use the workflow**, but it need not be preinstalled: the installer preserves an existing CLI or installs the official standalone distribution for your user when missing. Authenticate GitHub CLI separately with `gh auth login`.

The command pins the entrypoint to `57733e891659174b79c772fb4f16d8b47fe6c93c` and checks its literal SHA-256 `07caf29cb6a331fbb00310a3e3df836834b8f55aa89059f28032f6f8a8215fa1` before execution:

```bash
( tmp=$(mktemp) && trap 'rm -f "$tmp"' EXIT &&
  curl -fsSL 'https://raw.githubusercontent.com/rocker-code/my-ai-skills/57733e891659174b79c772fb4f16d8b47fe6c93c/scripts/install-global' -o "$tmp" &&
  python3 -c 'import hashlib,sys;sys.exit(0 if hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest()==sys.argv[2] else 1)' "$tmp" '07caf29cb6a331fbb00310a3e3df836834b8f55aa89059f28032f6f8a8215fa1' &&
  python3 "$tmp" --revision 57733e891659174b79c772fb4f16d8b47fe6c93c --agent opencode )
```

To **update**, approve a full Git source revision and replace **only** the `--revision` SHA above; the installer URL and digest remain pinned. Re-running the same command does not fetch `main`. Do not use `npx skills update` or the active installation's installer to update the bundle. [Details, conflicts and migration](https://github.com/rocker-code/my-ai-skills/wiki/Global-installation).

## Verify and use

```bash
test -f "${XDG_DATA_HOME:-$HOME/.local/share}/my-ai-skills/active/manifest.json"
test -f "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills/apply-issue/SKILL.md"
openspec --version
```

Open a new OpenCode session. On first use in a project, the agent checks OpenSpec integration and asks for authorization before initializing it; global installation does not modify projects. Check `/opsx-explore`, `/opsx-propose`, `/opsx-apply`, and `/opsx-archive` before implementing.

Ask **“Take care of this issue: URL”**, **“Take care of this project queue”**, or **“Take care of this milestone: URL”**; add **“no merge”** for manual integration. The workflow plans with OpenSpec, implements, tests, prepares the PR and reviews; default merge happens only after required checks pass. The agent needs GitHub access and isolated sessions/worktrees to run the full flow.

[Workflow guide and other resources](https://github.com/rocker-code/my-ai-skills/wiki/Workflow-guide) · [Legacy per-project installation](https://github.com/rocker-code/my-ai-skills/wiki/Legacy-installation) (not needed for global installation) · [Wiki](https://github.com/rocker-code/my-ai-skills/wiki)
