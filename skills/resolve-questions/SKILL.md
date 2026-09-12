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

Record each approved answer using `[DECISION]` and [the decision template](../../templates/github/decision.md). When authorized, comment on GitHub; otherwise provide exact copy-ready comments. Do not edit code, run apply or close the issue.

End with `ALL BLOCKING QUESTIONS RESOLVED` or `OWNER DECISION REQUIRED — <items>`. The executor must then refresh GitHub and run `issue-explore` again before `issue-ready`.
