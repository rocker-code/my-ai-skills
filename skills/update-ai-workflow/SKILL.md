---
name: update-ai-workflow
description: Update the installed my-ai-skills global workflow package ONLY on an explicit request (e.g. "atualize o my-ai-skills"). Route to the verified install-global entrypoint; diagnose local/legacy copies without writing unless separately authorized for a project and exact paths. Never trigger on ordinary tasks, status, issue work or startup.
---

# Update AI Engineering Workflow

This is an on-demand router, not an updater or scheduler. Do not update on
ordinary development, status, issue, milestone, startup or merge. A request to
develop this repository is not a request to install it.

1. Inventory the selected installation: global package at
   `${XDG_DATA_HOME:-$HOME/.local/share}/my-ai-skills/active`, supported agent,
   `active/manifest.json`, global OpenCode skills, `~/.agents/.skill-lock.json`
   (or `$XDG_STATE_HOME/skills/.skill-lock.json`), and only the explicitly
   identified project's `.opencode/skills/` and `.ai-workflow/`. Distinguish a
   full global install from a partial `skills.sh` install or legacy source
   clone. Preserve other agents, sources, credentials and project rules. If
   target/scope is ambiguous, ask. Do not silently change partial selection.
2. For an explicitly requested **global** update, resolve an approved full
   Git commit from the trusted upstream `main` (not a PR, mutable `latest`, or
   an unreviewed ref). The user must explicitly request the update/revision;
   confirm the chosen SHA and review trust before executing. Read the current
   README bootstrap recipe for its independent literal entrypoint digest and
   immutable entrypoint commit. Download that exact entry, verify its SHA-256
   against the independently published literal **before** running Python, then
   invoke the same `scripts/install-global --revision <approved-full-SHA>
   --agent opencode` command. Never execute `active/scripts/install-global`
   as a trust root; never use `npx skills update` or a parallel installer.
   Inspect changed syntax against the entrypoint version before execution.
3. The global request authorizes **read-only diagnosis** of one identified
   project's shadows, even when files match the official baseline. Do not
   edit `.opencode/skills/`, `.ai-workflow/`, `AGENTS.md`, `CLAUDE.md`, or other
   project files merely because the global update was requested. A separate
   explicit request must name the project root, each exact path, and the
   verified old baseline SHA before passing `--project <root>
   --baseline-revision <old-SHA> --reconcile-path <relative-path>`; inspect
   the dry inventory first. A global `skills.sh` collision needs separate
   explicit authorization per verified skill (`--migrate-global-skill <name>`).
   Backups remain under `migration-backups/`; unknown origins/edits block and
   remain untouched. Never assume name alone proves ownership or sweep HOME.
4. Report the actual `state`, previous/target/active SHA, agent, scope, backups,
   pending shadows, and any blocked/partial migration. A current global package
   does **not** mean closed projects or partial installations were migrated.
   A new OpenCode session may be needed to reload skills. Do not update agent
   binaries, OpenSpec, other sources, dependencies or application files.
5. In a Web-only environment without access to the installed machine, provide
   the verified CLI recipe and limitation; do not claim to have updated it.
