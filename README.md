# my-ai-skills

Personal reusable AI agent skills.

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

## Install with skills.sh

Install only `implement-issue` for OpenCode:

```bash
npx skills add rocker-code/my-ai-skills --skill implement-issue -a opencode
```

Install globally:

```bash
npx skills add rocker-code/my-ai-skills --skill implement-issue -a opencode -g
```

Install all skills from this repository:

```bash
npx skills add rocker-code/my-ai-skills --all -a opencode
```

For a private GitHub repository, the skills CLI can use the GitHub authentication already configured in the local environment.

## Layout

```text
skills/
└── implement-issue/
    └── SKILL.md
```
