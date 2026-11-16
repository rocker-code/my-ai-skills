# interrupted-workflow-resume Specification

## Purpose

Safely recover a previously started issue or milestone from a new OpenCode session using persisted, verifiable evidence.

## ADDED Requirements

### Requirement: Recover from a new session without prior chat

The workflow SHALL recognize a natural request to continue interrupted development and SHALL identify a unique repository and execution scope from durable evidence before starting mutating actions. If multiple plausible candidates exist, it MUST request the minimal disambiguation and MUST NOT guess a scope.

#### Scenario: Single issue is uniquely identified
- **WHEN** a new OpenCode session is opened in a known checkout with one evidenced interrupted issue
- **THEN** the agent identifies that issue, its verified last stage and next safe action before delegating the same issue to the existing orchestrator

#### Scenario: Ambiguous candidates
- **WHEN** multiple issues or milestones could match “continue de onde parou”
- **THEN** the agent displays the candidates and pauses before a modifying action, without selecting one from recency alone

#### Scenario: Explicit choice after ambiguous pause in the same session
- **WHEN** the agent has paused on two equally plausible issue/run candidates and the user explicitly chooses one issue/run in that same OpenCode session
- **THEN** the agent SHALL re-inventory the checkout, both reservations and ledgers and check independent stopped-writer evidence before any ownership transition; if safe, it SHALL invoke the applicable native OpenSpec 2.0 skill read-only in that same session, with discovery and invocation events tied to its canonical path/hash and session ID, and SHALL recheck both reservations and ledgers, Git, OpenSpec and GitHub without dispatch or writes. Before the explicit choice the agent MAY discover native skills read-only but MUST NOT invoke one; it SHALL pause after one question. Without a safe writer determination or observable post-choice invocation the proof SHALL remain blocked, not PASS

### Requirement: Preserve work and verify ownership

The workflow SHALL reuse verified existing branches/worktrees/OpenSpec/PRs. It MUST inspect staged, unstaged, untracked and relevant ignored data and MUST NOT perform writer takeover without grounded stopped-writer evidence and helper reconciliation.

#### Scenario: Interrupted dirty worktree
- **WHEN** a checkout contains partially written/staged/untracked changes
- **THEN** it is preserved, reconciled and reused or explicitly retained with a blocker, never reset or replaced

#### Scenario: Active or uncertain owner
- **WHEN** the previous writer remains active or ownership evidence is inconclusive
- **THEN** writing is blocked for that checkout; no automatic takeover is attempted

#### Scenario: Null PID without terminal runtime proof
- **WHEN** a reservation has no PID or a fixture merely describes the writer as stopped without independent terminal runtime evidence for its execution
- **THEN** the agent does not claim the writer has stopped and blocks ownership transition and Apply pending authoritative evidence

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
