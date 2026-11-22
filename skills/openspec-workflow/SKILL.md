---
name: openspec-workflow
description: Integrate native OpenSpec 2.0 with GitHub requirements, isolated work, project verification and delivery; do not reproduce the official lifecycle.
---

# OpenSpec integration

Read the live issue, approved decisions and repository rules; resume existing change/PR instead of duplicating it. Follow the canonical [AI workflow](references/AI_WORKFLOW.md). This adapter supplies integrations OpenSpec does not own: GitHub scope/decisions, worktree ownership, producer/consumer dependencies, project test evidence and authorized PR/merge.

Discover actual official skills in the installed profile: `openspec-explore`, `openspec-propose`, `openspec-apply-change`, `openspec-verify-change`, `openspec-archive-change`. Invoke them as installed; read CLI help when capability differs. Check the official profile before declaring Verify unsupported: enable it through official configuration when supported but not generated, preserving existing workflows/tools/configuration. Report exact enablement failure or true limitation, never simulate Verify with custom prompts.

Explore checks issue existence, scope, current code/callers/tests, decisions, dependencies, contracts and risks. One sufficient exploration is enough; re-explore only material changes. For cross-repository integration use `contract-handoff` design review, then final freeze against the effective delivered producer contract before consumer Apply.

Pin the exact officially validated proposal and trace acceptance → planned implementation → proving tests. Review architecture/security at the appropriate risk level, independently for material boundary changes when supported. Approve evidence-backed proposals without routine owner approval. A fresh Apply context verifies the pinned revision and ownership transfer after the planning writer stops. Native `openspec instructions apply --change <name> --json` controls tasks; do not replace its state with custom stages.

Use [TEST_STRATEGY.md](references/TEST_STRATEGY.md) for proportionate tests, pre-flight, fixture isolation, repeated-failure diagnosis and final required checks. Follow [WORKTREES.md](references/WORKTREES.md) for a single writer and M2T selections across handoffs. Runtime support, actual completion and proof must be verified, never inferred.

After Apply, invoke official Verify by default when supported, treat findings by severity, complete required tests, strictly validate with the installed command and invoke native Archive on the feature branch. Inspect archive and synchronized live specs in the same PR. Record unsupported Verify as NOT RUN with precise limitation; it does not waive tests/CI/review. Replan material contract changes; implementation-only corrections preserve the approved contract. Do not rewrite archived history to hide a changed requirement.
