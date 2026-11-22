---
name: resolve-questions
description: Resolve GitHub issue comments marked [QUESTION] through evidence-backed product and architectural analysis, then write or propose authoritative [DECISION] responses. Use in Web supervision after executor exploration; does not implement code.
metadata:
  category: web-supervision
  stage: discovery
---

# Resolve Questions

Refresh the issue and all comments. Collect unresolved `[QUESTION]` items and inspect relevant code, OpenSpec, architecture, linked issues/PRs and framework behavior before answering.

For each question:

1. state the verified current behavior and constraints;
2. compare realistic options and trade-offs;
3. prefer existing product decisions and native/project mechanisms;
4. choose only when evidence and user authority allow it;
5. identify contract, acceptance, test and migration consequences.

Do not disguise uncertainty as a decision. If owner input is required, narrow the question and present a recommendation.

Record each approved answer using `[DECISION]` and [the decision template](references/decision.md). Update the existing issue body when authorized, preserving unrelated decisions. A concise comment is reserved for a material question not adequately represented there or owner-action blocker. Otherwise provide copy-ready canonical content. Do not edit code, run apply or close the issue.

End with `ALL BLOCKING QUESTIONS RESOLVED` or `OWNER DECISION REQUIRED — <items>`. Refresh canonical issue/OpenSpec decisions and re-explore only material changes; do not require a second exploration for unchanged context.
