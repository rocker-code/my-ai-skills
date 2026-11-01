---
name: update-ai-workflow
description: Update the installed my-ai-skills / AI Engineering Workflow skills, bundled references and project workflow copies to the latest main revision, only when the user explicitly asks to update that installation (for example, "atualize o my-ai-skills" or "atualize o workflow de IA deste projeto"). Preserve the installed agents, scope and local customizations. Do not trigger for ordinary development, status queries, updating an issue, or requests to develop improvements to the source repository.
---

# Update AI Engineering Workflow

Execute one requested update of `rocker-code/my-ai-skills`. Do not schedule checks,
create background jobs, or attach updates to startup, issue, milestone or merge flows.
Treat the request as authorization for routine installation updates in the identified
scope; do not ask again for each safe step. Ask only when the target is ambiguous
or a local customization cannot be reconciled safely.

## 1. Inventory the actual installation

- Identify the target application repository and its instructions. Distinguish it
  from the source checkout of `rocker-code/my-ai-skills`.
- Inspect project and global skill lists, installer lockfiles, symlinks and agent
  configuration. Use `npx skills list` and `npx skills list -g` when available;
  inspect `npx skills --help` / subcommand help before relying on version-specific
  flags. Identify which entries actually belong to `rocker-code/my-ai-skills`.
- Record agents, project/global scope, full versus partial installation, paths,
  current source revision and local modifications. Do not infer an agent from an
  installed binary alone. Preserve a deliberately partial skill selection.
- Detect `.ai-workflow/` copies, alternate documented paths, `AGENTS.md`,
  `CLAUDE.md` and plugin installations. Update only identified installations in
  the requested scope; do not create duplicate plugin and skills.sh installations.
- Default a project request to that project's existing installation. If only a
  global installation exists, identify its cross-project effect before updating.
  If multiple possible targets remain, ask one focused question. If none exists,
  report that fact and ask for the initial agent/scope instead of inventing them.

## 2. Resolve and inspect the current source

- Read the source repository's current default-branch README and installation
  guidance. Use the newest merged `main`, never an unmerged PR or feature branch.
  Record the exact target SHA and inspect changes since the installed revision
  when that revision is available. Otherwise label the previous version unknown.
- Reuse the documented complementary source clone when its remote matches the
  expected repository and its state is safe. Fetch and fast-forward only. Preserve
  dirty/diverged clones, branches and worktrees; use a separate clean source copy
  at the verified SHA when needed. Do not reset, clean, stash or force-push.
- Read current installation/migration instructions and required runtime versions.
  Check prerequisites before writes. Do not upgrade Node, agents, OpenSpec,
  ai-memory or application dependencies as part of this request. Report a required
  prerequisite as blocked and continue independent safe parts.

## 3. Update skills through their existing manager

For a skills.sh installation, reinstall from the verified source revision using
`skills add`, selecting only the detected agents and scope. Confirm the installed
CLI's source/ref syntax first; a verified local source checkout can pin the SHA.
For a full installation, include newly added upstream skills with `--skill '*'`;
for a partial installation, select its existing skills and explicitly required
dependencies. Report removed/renamed skills and handle documented migrations
without deleting unidentified local directories.

Typical upstream-source command for a full project installation:

```bash
npx skills add rocker-code/my-ai-skills --skill '*' -a opencode -y
```

Substitute the detected agent(s); add `-g` only for an identified global target.
Prefer the pinned local source when supported, then verify the resulting files
against it. Do not use `--all`, which selects all agents. Do not run an unscoped
`npx skills update`: it can update unrelated sources and does not ensure newly
added skills are installed. Preserve locally edited skill files before replacement;
reconcile them or leave affected entries blocked rather than overwriting them.

For a plugin installation, use only the plugin manager's documented update
capability discovered through its help/tools. Do not edit caches, remove/reinstall
the plugin as a guessed update method, or claim that a source fetch updated it.
If the environment cannot update it, report the exact pending user action.

## 4. Refresh complementary project files

- If complementary project copies exist, compare them with the same source SHA.
  Refresh protocols, templates and runtime helpers described by the current README.
  Include required companion files such as `workflow_metrics.py` and retain script
  executable permissions. Do not copy the source maintenance script `sync-plugin`
  into application runtime helpers.
- Establish ownership before overwriting. Use the prior source revision or a
  recorded baseline to distinguish unchanged upstream copies from local edits.
  Apply clean three-way updates when a base exists; preserve local additions and
  surface conflicts. Without a reliable baseline, keep differing existing files
  untouched and report them as requiring reconciliation. Never bulk-copy over
  custom files, delete unknown paths or use `rsync --delete`.
- Update existing workflow sections/links in project instructions when the new
  protocol requires it, preserving unrelated rules and avoiding duplicate blocks.
  Inspect relevant protocols together with bundled skill references for coherence.
- Do not initialize OpenSpec, start application development, commit unrelated
  changes, merge, release or deploy. Leave project changes reviewable; commit or
  open a PR only when requested or required by applicable project instructions.

## 5. Verify and report

Re-list installed skills for each updated scope. Compare names, files and bundled
references with the selected source revision; verify manager metadata, symlink
targets and executable helpers where applicable. Inspect the final project diff.
Do not execute helpers that publish GitHub comments merely to verify an update.
If `main` advanced during the run, report the verified SHA and newer pending SHA;
do not claim to be current against a revision that was not installed.

Return a short table with `Component | Result | Pending`, covering skills,
project copies and instructions/plugin when applicable. State scope, agents and
target SHA, newly added skills, preserved customizations and concrete blockers.
Use `updated`, `already current`, `partial`, `blocked` or `not applicable` based
on evidence. Never declare full success after a failed component. Mention a new
session only if the actual manager requires it to load updated skills.

In a Web-only environment, inspect the source and accessible project files but
do not claim to have updated the user's computer. If a repository target is
explicitly identified, prepare reviewable project-file changes within that scope;
otherwise provide the short CLI handoff and state the local execution limitation.
