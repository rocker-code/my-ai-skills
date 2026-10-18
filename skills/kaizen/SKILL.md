---
name: kaizen
description: Review a completed issue or merged PR for recurring process failures and implement a small durable improvement in project instructions, reusable skills, tests, CI or architecture documentation. Use after merge; avoid speculative rules and broad refactors.
---

# Kaizen

Read the issue, approved decisions, proposal, PR history, audit findings, CI failures and final outcome. Identify actual friction: repeated question, wrong architecture, escaped defect, slow check or lost handoff. Cite evidence and choose at most the smallest durable improvement per distinct cause:

- Project-specific fact/invariant → repository AGENTS.md.
- Repeatable procedure across projects → workflow skill.
- Automatically detectable defect → focused test, lint or CI.
- Architectural decision/contract → repository documentation and relevant spec.

Before editing, check whether the rule or validation already exists; avoid duplicating or freezing assumptions as invariants. For changes to skills, follow the repository's canonical source and package synchronization. For code or CI, make a separate scoped change with appropriate review. Report observation → cause → selected change → verification, plus deferred ideas. If no supported change is needed, say `NO PROCESS CHANGE`.

## Workflow timing evidence

When a workflow run record exists and `workflow-report` is available, inspect the issue or milestone report before concluding the Kaizen review. Use the recorded stage durations, explicit waits, rework events, CI failures and review findings together with the qualitative evidence from the work. Link the report/run IDs and state the sample size.

Treat missing instrumentation as unavailable data, not zero time. Do not recommend a change from one unusually slow run alone; look for a recurring, comparable pattern and verify that the proposed change preserves quality. Do not change workflow policy automatically from timing data. If no evidence-backed process change is justified, record `NO PROCESS CHANGE` as usual.

## Automatic CI performance routing

Read [the CI performance protocol](references/CI_PERFORMANCE.md). When completed-work evidence shows recurring slow checks or a performance regression, automatically invoke `ci-performance-audit` in diagnosis mode and record the smallest supported follow-up. Do not create issues, run paid/hosted benchmarks, change CI or start implementation beyond the selected authorization. Return `NO PROCESS CHANGE` when no durable change is supported.
