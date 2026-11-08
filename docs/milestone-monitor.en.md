# Operational Milestone Monitor

`aew dashboard`: read-only Python 3/curses/SQLite TUI (stdlib). The
[offline demo](../examples/milestone-monitor/) stays separate with **SIMULATED
DATA**. The operational panel never invents activity, timing, or approval.

## Install and configure

From a **retained** clone, not a disposable worktree:

```sh
scripts/install-aew --bin-dir "$HOME/.local/bin"
aew --help
```

Add this bin to PATH yourself if needed. The installer only creates a symlink,
refuses a different destination, uses no sudo and changes no shell rc. The launcher
resolves its own path and works from any directory. To uninstall, inspect
`readlink ~/.local/bin/aew` and remove **only that symlink**; retain config/data.
Also distributed through `scripts/sync-plugin` under `plugins/my-ai-skills/scripts/`.

Create `$XDG_CONFIG_HOME/aew/config.json` (fallback `~/.config/aew/config.json`):

```json
{
  "schema_version": 1,
  "targets": [{"repository": "owner/repo", "milestones": [1, 2]}],
  "runtime": {"enabled": false, "expected_version": "2.2.5"},
  "timing": {"github_interval": 60, "runtime_interval": 15,
             "github_ttl": 180, "activity_ttl": 45, "timeout": 10}
}
```

Replace targets with authorized repositories/numbers. GitHub.com only, positive
integers; duplicates consolidated. No targets/config means empty guidance, **not
discovery**. Timing values are positive seconds up to 86400, with defaults above.
Use existing authenticated `gh` to refresh GitHub; never put credentials in config.

```sh
aew collect --once --config /path/config.json --state-dir /path/cache
aew dashboard --config /path/config.json --state-dir /path/cache
aew dashboard --offline --no-color --ascii
```

`collect --once` emits a metadata JSON projection, exiting nonzero on source
failure. `dashboard` requires a TTY, including tmux; no running agent required.
Explicit paths/config are optional. Presentation is pt-BR, preserving proper
names and branches.

## Architecture, state, and privacy

Paginated GitHub → SQLite snapshots → projection/OpenCode overlay → reducer/curses.
Repository inventory, per-issue comments, and runtime are independent sources.
Threaded collection, bounded queue, coalesced refresh and subprocess timeouts;
no per-frame requests, daemon, or mandatory plugin. Exiting closes only the panel,
**never agents, tests, or jobs**.

Schema 1 cache: `$XDG_STATE_HOME/aew/monitor.sqlite3` (fallback
`~/.local/state/aew/monitor.sqlite3`). New directory/file: 0700/0600; existing
permissions unchanged. SQLite serializes short transactions with busy timeout;
network outside locks and generations reject older responses. Page/JSON/network/
write failure retains prior snapshot. Future/corrupt databases are refused, never
automatically deleted, recreated, or downgraded. Preserve a copy and investigate
space/permissions/version before intervention. No GitHub comment migration.

- **GitHub:** repository/number identity, milestone and closure. Timeline PR
  candidates are linked only after official closing references; multiple links
  are ambiguous. Merge/head are separate facts. PRs are excluded from issue totals.
- **Workflow v1 (#16):** canonical parser/summary/correlation, no parallel logger.
  Comment ID/hash upserts include last_seen_at; stable effective event ordering.
  Latest run by UTC creation, then run ID/comment ID, with visible conflicts and
  selectable history. Moving/reopening an issue retains local history.
- **OpenCode:** foreground activity overlay, not proof of child process, tests/CI,
  approval, or stage completion.

Percentage = **closed issues/total**, never implementation estimate. Empty: 0/0
and unavailable percentage. Closed does not prove merged/verified delivery;
merged PR with open issue does not increase completion. Reopening/moving applies
the next complete inventory. Exclusive counts: closed → done; wait → blocked
(human distinct); relevant failure/interruption → blocked; recently confirmed open
incarnation → running; others → pending/unknown/inactive/reconciliation. Waits win
over parallel workers, terminal wins over later running; details retain distinct
executions. Rework does not inherit an earlier incarnation's state or approval.

Reopened cache does not confirm activity. Per-source freshness/UTC timestamps,
default workflow/runtime TTL 45s and GitHub 180s. Errors/cache never renew
confirmation; future clocks never confirm. Timing remains canonical registered
time; parallel work sum is not calendar time. Reports/evidence refs are not approval.

Only allowlisted metadata, no prompts/messages/tokens/logs/arbitrary payloads.
Titles/ANSI controls are sanitized before cache/render. Fixed argv without shell;
external content never becomes instructions. Public failures are categories
(missing, unauthorized, forbidden, rate limit, timeout, invalid response/contract,
storage), never raw stderr. Retry-After/reset when supplied, otherwise bounded
exponential backoff; `r` cannot bypass it.

## Opt-in runtime and continuation

Contract **OpenCode 2.2.5 only**, CLI and server. Official producer
`anomalyco/opencode@9bbb8ce18c80f099e0e448775f59d965ead40a21`, schema
`packages/protocol/openapi.json`, SHA-256
`92cc33ef9a107c8af6295e6fcbdf6d339d4374955910924456bd91a76844a5db`.
Other releases require renewed verification; no V1/prose/internal DB fallback.

Enable `runtime.enabled: true`; optional HTTP(S) `runtime.server` without userinfo,
query or fragment uses the same official context/auth for bind/collection. Omitted
means CLI shared-service discovery; **never --standalone**. Unbound IDs are
discarded. After collection with an existing open run/incarnation:

```sh
aew bind --issue https://github.com/owner/repo/issues/7 \
  --run-id wf-EXISTING --stage apply --worker-id worker-a \
  --execution-kind worker --execution-id EXISTING-EXECUTION \
  --session-id ses_EXISTING --worktree /path/checkout --branch my-branch
aew unbind --issue https://github.com/owner/repo/issues/7 \
  --run-id wf-EXISTING --stage apply --worker-id worker-a \
  --execution-kind worker --execution-id EXISTING-EXECUTION
```

Replace placeholders with real IDs; both accept `--config`/`--state-dir`.
Optional branch is saved only after Git verification. Bind declares that session
executes this worker. Bound test/job/CI can show active agent, but needs its own
canonical observation to confirm the child. Terminal/ambiguous, wrong repository/
checkout, or session already bound to another incarnation is refused without
replacing the prior link. Unbind also removes terminal links, retaining history.

Every confirming cycle checks server.info, session.get, explicit location.get,
and Git identity. location.directory is already absolute: no concatenated subpath
or shared projectID/canonical as checkout proof. Location/process/context changes
invalidate bindings until a new bind. Missing 404, inactive, and API failure are
distinct. Queries are not atomic: movement between samples appears on the next.
Session outcome does not end workflow.

OpenCode/Codex continues using skills and the coordinator's single-writer
workflow-event. The panel does not write events, approve tests, control agents,
close issues, or merge. Codex produces v1, with no native runtime adapter.
Notifications/iPhone, costs/tokens, and web are outside MVP. No Figma dependency:
curses, not a web redesign.

## Keys and ruler

↑/↓ or j/k navigate; Enter/Space accordion/details; a/c expand/collapse all;
f all/running/pending/blocked/done; v compact/detailed; r refresh; [/] run history;
PgUp/PgDn scroll details; q/Esc exit. Preferences persist by identity; history
changes details only, never latest-run totals.

Audit → Explore → Questions → Proposal → Proposal review → Apply → Tests →
**Verify/archive** → Prepare PR → PR audit → CI → Merge → Kaizen.
`+` registered closed/completed; `>` registered current (not running proof);
`.` no record; `!` failure/interruption; `?` reconciliation; `B` blocked; `H` human.
Earlier stages never succeed by position. Unknown stage remains “other”.
Viewport includes current stage; Unicode cell widths, ASCII/no-color fallback,
narrow C/E/P/B counts. Stdlib tests: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
discover -s tests`. Synthetic fixtures are not real integration smoke evidence.
