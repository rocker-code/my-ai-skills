---
name: simplify
description: Simplify issue-scoped code when a concrete readability or maintenance problem exists, preserving exact behavior; optional within Apply or on explicit request.
---

# Simplify code while preserving behavior

Adapted from Akita on Rails [simplify](https://github.com/akitaonrails/my-skills/tree/master/simplify), inspected upstream blob `04644aa0f9c1725d55eee8020df3cf30a14feec2`.

Use after implementation works and focused tests pass, only for a demonstrated readability/maintainability problem in changed code, on explicit request, or focused PR feedback. Clean code needs no pass. This is not a required stage, approval, agent or second audit.

Understand responsibility, callers, error/edge paths, tests and neighboring conventions before editing. Look for excessive nesting, unclear names, duplication, dead code and abstractions without demonstrated value. Prefer clarity over cleverness; preserve meaningful boundaries and testability. Make small reversible issue-scoped changes and rerun relevant existing checks.

Preserve exact inputs/outputs, side effects, ordering, authorization, public contracts, errors and edge cases. Do not reduce line count for its own sake, refactor unrelated files or change behavior under a cleanup label. Broader independently valuable untracked opportunities follow the existing evolution policy; trivial style suggestions generate no issue. Existing tests, native OpenSpec verification and applicable independent PR/CI review prove preservation, with no additional audit.
