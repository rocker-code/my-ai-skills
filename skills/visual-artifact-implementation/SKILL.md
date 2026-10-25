---
name: visual-artifact-implementation
description: Interpret approved visual assets attached to GitHub issues and apply them to existing application screens within the canonical issue/OpenSpec/PR lifecycle. Trigger for UI redesign, layout, and design-implementation tasks.
---

# Visual Artifact Implementation

Read [the visual artifact protocol](../../protocol/VISUAL_ARTIFACTS.md) and follow it automatically for UI issues with approved design attachments. Do not require a separate `/apply-design` invocation or repeated per-project prompts.

During `issue-audit` / exploration, identify the approved pinned reference and affected screens, obtain and inspect it safely, and produce an existing-components mapping. If the source is inaccessible or visually incomplete, do not guess and do not claim successful inspection.

During `apply-issue`, implement only the validated scope using project-native UI patterns, preserve functional contracts, and validate behavior plus visual fidelity with actual screenshots where supported. During `prepare-pr` / PR review, report evidence and explicit gaps. The normal OpenSpec revision, test, independent audit and merge gates remain in force.
