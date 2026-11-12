# interrupted-workflow-resume Specification

## Purpose

Safely recover a previously started issue or milestone from a new OpenCode session using persisted, verifiable evidence.

## Requirements

### Requirement: Recover from a new session without prior chat

The workflow SHALL recognize a natural request to continue interrupted development and SHALL identify a unique repository and execution scope from durable evidence before starting mutating actions. If multiple plausible candidates exist, it MUST request the minimal disambiguation and MUST NOT guess a scope.

#### Scenario: Single issue is uniquely identified
- **WHEN** a new OpenCode session is opened in a known checkout with one evidenced interrupted issue
- **THEN** the agent identifies that issue, its verified last stage and next safe action before delegating the same issue to the existing orchestrator

#### Scenario: Ambiguous candidates
- **WHEN** multiple issues or milestones could match “continue de onde parou”
- **THEN** the agent displays the candidates and pauses before a modifying action, without selecting one from recency alone

### Requirement: Preserve work and verify ownership

The workflow SHALL reuse verified existing branches/worktrees/OpenSpec/PRs. It MUST inspect staged, unstaged, untracked and relevant ignored data and MUST NOT perform writer takeover without grounded stopped-writer evidence and helper reconciliation.

#### Scenario: Interrupted dirty worktree
- **WHEN** a checkout contains partially written/staged/untracked changes
- **THEN** it is preserved, reconciled and reused or explicitly retained with a blocker, never reset or replaced

#### Scenario: Active or uncertain owner
- **WHEN** the previous writer remains active or ownership evidence is inconclusive
- **THEN** writing is blocked for that checkout; no automatic takeover is attempted

### Requirement: Continue only from verified gates

The workflow SHALL reconstruct verified status from current GitHub, Git/OpenSpec and runtime evidence. Missing callbacks, stale tests and interrupted commands MUST NOT be treated as successful gates, and unchanged valid gates SHOULD be reused.

#### Scenario: Test process interrupted without an authoritative result
- **WHEN** a test command stops without an accessible final report/exit confirmation
- **THEN** the result is recorded as unknown and only affected verification is rerun after safe preflight

### Requirement: Respect original scope and recovery limits

The workflow SHALL preserve explicit issue/milestone boundaries and known merge mode, SHALL NOT create duplicate implementation artifacts, and MUST disclose missing local-only data instead of claiming it was restored.

#### Scenario: Existing PR and blocked dependency in milestone
- **WHEN** a milestone includes an existing PR and a dependent issue
- **THEN** the orchestrator rechecks the PR on its current head and does not prematurely start the consumer

#### Scenario: Lost local machine
- **WHEN** GitHub and committed artifacts survive but uncommitted local files were lost
- **THEN** only retained artifacts are reconstructed and the local-only loss is reported
