# my-ai-skills

Personal reusable AI agent skills for an issue-driven development workflow using GitHub, OpenSpec and coding agents such as OpenCode or Claude Code.

## Skills

### `implement-issue`

Implements a GitHub issue end-to-end in the current repository:

- reads the complete issue and comments;
- inspects the existing implementation before changing code;
- integrates with OpenSpec when present;
- discovers and uses relevant installed technical skills;
- implements the requested behavior;
- removes obsolete code when replacement is part of the issue;
- adds or updates tests;
- runs appropriate validation;
- verifies every acceptance criterion;
- leaves the repository ready for a pull request.

### `openspec-workflow`

Keeps OpenSpec synchronized with approved requirements and implementation:

- locates or creates the correct OpenSpec change;
- reconciles issue, spec, code and tests;
- updates behavioral contracts before implementation diverges;
- manages tasks and validation;
- avoids unnecessary specification churn for implementation-only refactors.

### `prepare-pr`

Turns a completed implementation into a reviewable pull request:

- reviews the complete branch diff;
- checks issue and OpenSpec coverage;
- runs final validation;
- detects unrelated or accidental changes;
- prepares commit/push state;
- creates a structured PR when explicitly requested;
- avoids duplicate PRs for the same branch.

### `address-pr-review`

Processes PR review feedback end-to-end:

- reads PR conversation and inline review findings;
- classifies findings as valid, adapted, resolved, obsolete, conflicting or invalid;
- fixes the underlying issue instead of blindly applying comments;
- updates OpenSpec when review changes behavior;
- runs relevant validation;
- pushes corrections to the same PR branch when the workflow calls for it.

### `pr-status`

Provides a read-only status of an existing pull request:

- correlates issue, OpenSpec, diff, CI and review feedback;
- identifies real remaining blockers;
- distinguishes stale comments from actionable findings;
- classifies the PR state;
- recommends one concrete next action.

## Suggested workflow

```text
Discuss / define feature
        ↓
GitHub Issue
        ↓
implement-issue
        ↓
openspec-workflow (used when OpenSpec is present)
        ↓
prepare-pr
        ↓
Independent PR review
        ↓
address-pr-review
        ↓
Independent PR review
        ↓
pr-status
        ↓
Merge when ready
```

The skills are intentionally composable. Workflow skills should rely on installed domain-specific skills (Magento, React Native, clean architecture, security, testing, etc.) instead of duplicating that technical knowledge.

## Install with skills.sh

Install all skills for OpenCode:

```bash
npx skills add rocker-code/my-ai-skills --all -a opencode
```

Install globally:

```bash
npx skills add rocker-code/my-ai-skills --all -a opencode -g
```

Install only selected skills:

```bash
npx skills add rocker-code/my-ai-skills --skill implement-issue --skill openspec-workflow --skill prepare-pr --skill address-pr-review --skill pr-status -a opencode
```

For a private GitHub repository, the skills CLI can use the GitHub authentication configured in the local environment.

## Layout

```text
skills/
├── implement-issue/
│   └── SKILL.md
├── openspec-workflow/
│   └── SKILL.md
├── prepare-pr/
│   └── SKILL.md
├── address-pr-review/
│   └── SKILL.md
└── pr-status/
    └── SKILL.md
```
