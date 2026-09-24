---
name: sonar
description: Use SonarQube CLI as an agent-agnostic quality and security verification layer. Analyze current changes, inspect issues, scan secrets, classify findings, run remediation loops, and return structured evidence for surrounding workflows such as apply-issue, prepare-pr, pr-audit, and milestone-orchestrator.
metadata:
  category: quality
  tool: sonarqube-cli
---

# SonarQube CLI

Use the `sonar` CLI as a reusable verification capability. This skill does not replace tests, domain review, OpenSpec validation, or PR review, and it does not authorize GitHub or Git write operations.

## Operating principles

- Prefer analysis of the current change over treating the project's historical backlog as a blocker.
- Prefer machine-readable `--format toon` output when an AI agent will consume the result.
- Never invent Sonar results when the CLI, authentication, project binding, network, or server is unavailable.
- Never expose Sonar tokens or detected secret values in output, logs, issues, commits, or PRs.
- Do not expand scope with unrelated refactoring only to make Sonar clean.
- Distinguish findings introduced by the current change from pre-existing findings.

## Preflight

Verify that the CLI is available:

```bash
sonar --version
```

Verify authentication:

```bash
sonar auth status
```

Prefer project auto-detection through `sonar-project.properties` or SonarLint connected-mode configuration. Only pass an explicit project key when auto-detection is unavailable or the surrounding workflow provides the verified key.

If preflight cannot complete, return `SONAR UNAVAILABLE` with the concrete reason. Do not silently skip verification.

## Analyze the current change

Prefer analysis against the verified target branch:

```bash
sonar analyze --base <base-branch> --format toon
```

For a specific file:

```bash
sonar analyze --file <path> --format toon
```

The base branch must come from repository/PR context. Do not guess it when multiple targets are plausible.

## Inspect project issues

List issues when historical/project context is needed:

```bash
sonar list issues --format toon
```

Filter high-severity findings when appropriate:

```bash
sonar list issues --severities BLOCKER,CRITICAL --format toon
```

Existing project issues are context, not proof that the current implementation introduced them.

## Secret detection

Use secret scanning for configuration, credentials-adjacent files, generated configuration, or when the surrounding workflow requests a security check:

```bash
sonar analyze secrets <path>
```

Treat an actual secret finding as blocking. Redact the secret value from all agent output.

## Classify findings

For every material finding, classify it as exactly one of:

- `introduced` — caused by the current change;
- `preexisting` — demonstrably existed before the current change;
- `out-of-scope` — legitimate issue not caused by the task and whose remediation would materially expand scope;
- `false-positive` — the rule does not apply after inspecting the code and rule semantics.

Do not classify by assumption. Use diff/base evidence, repository history, Sonar context, or code inspection.

## Remediation loop

For actionable findings introduced by the current implementation:

1. inspect the rule, location, message and affected code;
2. identify the root cause rather than patching only the symptom;
3. make the smallest in-scope correction;
4. run the relevant project tests/static checks;
5. rerun the relevant Sonar analysis;
6. repeat until blocking introduced findings are resolved or a concrete blocker remains.

Do not suppress or ignore a rule solely to obtain a passing result. Rule suppression requires an explicit, technically justified project convention or decision.

## Blocking policy

Return a blocked result for:

- introduced `BLOCKER` findings;
- introduced `CRITICAL` findings;
- detected secrets;
- security findings directly introduced by the implementation;
- an unresolved Sonar finding explicitly defined as blocking by repository policy.

Lower-severity introduced findings require engineering judgment. Fix them when the remediation is local and proportionate; otherwise report them as non-blocking evidence or recommend a follow-up issue.

Pre-existing and out-of-scope findings do not block the current task unless repository policy explicitly says otherwise.

## Workflow integration

This skill returns evidence to the calling workflow; it does not decide GitHub lifecycle state on its own.

Typical composition:

```text
apply-issue
  -> tests / static checks
  -> sonar
  -> prepare-pr
  -> pr-audit
```

A surrounding workflow may use `SONAR BLOCKED` as a readiness gate. A passing Sonar result alone is never sufficient to declare an implementation complete.

## Output contract

Return a concise evidence block:

```text
Sonar Verification
- CLI: available | unavailable
- Authentication: valid | unavailable
- Project: <detected key or unavailable>
- Base: <branch or n/a>
- Analysis: passed | findings | unavailable
- New blocking findings: <count>
- New non-blocking findings: <count>
- Pre-existing findings observed: <count>
- Secrets: none | found | not checked

Findings
- <severity> | <rule> | <file:location> | <classification> | <status/remediation>

Conclusion
SONAR PASS
| SONAR PASS WITH NON-BLOCKING FINDINGS
| SONAR BLOCKED — <reason>
| SONAR UNAVAILABLE — <reason>
```

Omit the Findings section when there are no material findings. Never include secret values.

## Command reference

When a command is unclear or the installed CLI version differs from this skill, prefer the installed CLI's `--help` output and SonarQube CLI's machine-readable documentation at `docs/llms.txt` in the official `SonarSource/sonarqube-cli` repository. Do not guess unsupported flags.
