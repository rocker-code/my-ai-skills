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

Reopened cache alone never confirms activity. A pre-open sample requires a live,
healthy observer, current epoch/context/binding revision and a valid TTL; reopening
the TUI never renews timestamps. Per-source freshness/UTC timestamps,
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

## Optional event bridge

**Controlled real smoke: completed on 2026-11-09 for issue #440 with explicit authorization; do not enable in other environments without authorization.** The bridge uses the official
client's public `fetch` extension to send the type allowlist in the HTTP request,
in addition to local filtering and IPC sanitization. Subscriptions reject
redirects. The installed package was tested against a simulated server and separately
against an authorized OpenCode 2.2.5 session; integrated validation and real smoke remain distinct from simulated tests. Evidence and limits: `openspec/changes/integrate-opencode-workflow-instrumentation/verification.md`.

[`integrations/opencode-observer`](../integrations/opencode-observer/README.md)
pins `@opencode/client@2.2.5` and its dependency tree in a lockfile. Installation
is voluntary: run `npm ci --ignore-scripts --no-audit --no-fund` in that directory
with Node >=22. `npm test` checks the installed client against simulated transport,
not a real OpenCode instance. Neither dashboard nor `collect --once` installs
anything automatically; both retain their Python stdlib path without Node or
bridge dependencies.

The bridge receives a binding/context allowlist through stdin and emits only
versioned metadata NDJSON, limited to 16 KiB per envelope. The package README
documents the full protocol, timestamp units and synthetic configuration example.
It uses `Service.discover` (never starts a service), official authentication
inherited from the environment and server/session identity revalidation. Never
pass credentials through argv/config. Stopping the bridge cancels only its
subscription, not agents.

Without Node/the package, or on failure, periodic CLI snapshots remain available
but do not provide continuous coverage. The official stream is live-only: loss,
restart or context change requires reconciliation and cannot reconstruct missing
timestamps. Session success does not end a stage or approve a test. Do not enable
real monitoring or use a current session for smoke testing without authorization.

## Foreground observer and collection ownership

With explicit targets and `runtime.enabled: true`, voluntarily start:

```sh
aew observe --config /path/config.json --state-dir /path/cache
```

No TTY/open dashboard is required and no service is installed. `Ctrl+C`/`SIGTERM`
stops only this observer and its bridge, never OpenCode sessions, tests or jobs.
Without Node/the package/confirmed bindings it remains degraded with periodic
CLI snapshots. One source failing or timing out does not stop the other source.

A process lock in `collector.lock` coordinates collection in the same state
directory. Each ownership gets a fresh epoch UUID; two dashboards read shared
snapshots. With a live owner, `collect --once` reads cache and requests refresh,
without creating another collector. `r` also signals the owner; requests coalesce
and never bypass backoff. An observer requests handoff from the TUI (bounded by
the configured timeout); it ceases publication and remains usable as a reader.
Old responses cannot publish under new ownership. A second observer is refused.
Never remove the lock to force collection; a crash releases the descriptor
automatically without deleting history.

Heartbeat every **5s**, health validity **15s**; a heartbeat never renews an
observation timestamp or activity TTL. SQLite remains schema 1, with local
version-1 metadata under `collector:*`, `observer:*` and `runtime-event:*`.
Facts are allowlist-projected again before caching, capped at **1000** per state
domain; NDJSON envelopes are limited to **16 KiB**. Saturation/loss records a gap
before discarding known facts. Unknown versions and pending canonical operations
are never deleted to free space. Consumed facts older than **7 days** are pruned
on new insertions; unconsumed facts remain until consumption or explicitly marked
loss. Backoff is capped at **900s**.

Observer stdout never contains the raw feed; health, facts and gaps stay in local
state. Diagnostics are categorized and raw bridge stderr is discarded. Disk-full
or write failure never renews freshness and preserves the last intact state.
Restart, reconnection or loss requires official reconciliation, not reconstruction
of missing timestamps. For rollback, stop only this observer, preserve SQLite and
prefer offline reading until pending work is reconciled. Do not delete cache/config.
Never run old/new publishers concurrently; the previous version may ignore new
metadata but must not compete for the comment/outbox. Rollback neither undoes
published GitHub stages nor removes an accepted operation to free space.

## Structured coordinator transitions

**GitHub readers:** `dashboard`, `collect --once`, `observe`; `bind`/`unbind` only
change local bindings. **Publishers:** `workflow transition`, `workflow reconcile`
and `scripts/workflow-event`. Reconciliation is not read-only: it may resume the
outbox and publish verified waits. Only the coordinator of a previously authorized
workflow may call it. `coordinator: true`/`--coordinator` declares that context,
not a substitute for human authorization or `gh` permissions; monitor configuration
alone never authorizes writing. Invoking an isolated skill creates no such context.

**Synthetic** examples, for an authorized test environment only. Save `run.json`:

```json
{"version":1,"coordinator":true,"operation_id":"op-run","event":"run-start","issue":"https://github.com/owner/repo/issues/7","run_id":"wf-exemplo","worker_id":"orchestrator","at":"2026-11-08T00:00:00Z"}
```

And `apply.json` (the executor session ID is not available yet):

```json
{"version":1,"coordinator":true,"operation_id":"op-apply-a","event":"dispatch","issue":"https://github.com/owner/repo/issues/7","run_id":"wf-exemplo","worker_id":"worker-a","stage":"apply","execution":{"kind":"worker","id":"exec-apply-a"},"at":"2026-11-08T00:00:01Z","depends_on":["op-run"],"binding":{"worktree":"/fixture/worktree","branch":"fixture"}}
```

```sh
aew workflow transition --input run.json --config /path/config.json --state-dir /path/cache
aew workflow transition --input apply.json --config /path/config.json --state-dir /path/cache
# Retry uses EXACTLY the same file/operation_id/timestamp; --input - is also supported.
aew workflow transition --input apply.json --config /path/config.json --state-dir /path/cache
```

When the worker's **real** session ID arrives, save `session.json`:

```json
{"version":1,"operation_id":"op-apply-a","session_id":"ses_EXECUTORA_REAL"}
```

```sh
aew workflow reconcile --issue https://github.com/owner/repo/issues/7 --run-id wf-exemplo \
  --coordinator --binding-input session.json --config /path/config.json --state-dir /path/cache
```

The late binding intention is separate: never add a session to the original
payload, as a different hash for the same `operation_id` is refused. A different
session for an accepted intention is also refused. Without a real ID, binding
remains pending; never fall back to the coordinator session. Publication and
binding are not a distributed transaction: opening on GitHub may succeed while
binding fails. Retry repairs/revalidates binding without opening another stage.
With an active collector it requests refresh and uses available snapshots; without
an owner it performs targeted one-shot collection respecting targets/backoff.
A changed context/PID or execution requires reconciliation and exact removal of
the previous binding through `aew unbind` before binding again; no silent replacement.

JSON input is limited to **16 KiB**, without duplicate keys. Safe identities and
typed execution are required where applicable; effective UTC timestamps are preserved.
Responses separate `accepted`, `publication` (`pending`/`published`/`conflict`),
`binding` (`not_requested`/`pending`/`bound`/`failed`) and `binding_reason`. Exit 1
signals instrumentation failure/pending work, not a prohibition on authorized
development. Before durable acceptance: `accepted:false`; afterward, remote failure
keeps the operation pending with its original effective time. Never generate a new ID for retry.

Reconciliation stays within the supplied issue/run; it returns at most **20**
operations, `total`/`truncated` and `runtime` counters. Overlapping waits are merged
and existing canonical coverage is subtracted. `wait-intervals` publishes at most
**32** intervals in one edit, requiring complete pairs, unambiguous identity and
continuous coverage. It never closes an explicit open wait; publication is deferred
when it or another pending request prevents safe pairing. A query without a reply
timestamp remains `unmeasured`; never retry in a loop to invent duration. `remaining`
also includes unverified gates/measurements.

Turn success never automatically produces `observe completed`/`stage-end`.
Structured terminal observations require their own evidence; a worker with a runtime
source requires `log_ref: worker-result:<execution-id>`. A `test_run` requires
`report: present`, a `test_report`/`process_exit` source and its own
`evidence:<execution-id>`. A reference is not approval: the coordinator must still
verify gates and record semantic completion separately. Manual CLI and v1 metrics
remain compatible.

### Cooperative publication and concurrency limits

The structured coordinator and `scripts/workflow-event` share a lock per state
directory/repository/issue/run. The manual CLI accepts `--state-dir`; use the same
domain as `aew` (default `$XDG_STATE_HOME/aew`). No new field is required for manual
v1 events. Structured events carry optional `operation` identity/hash metadata;
v1 readers and metrics remain compatible.

The outbox accepts operations before network calls, preserves dependencies and
separates publication from binding. Retry rereads the comment and recognizes an
already saved operation; a lost response does not duplicate events/evidence/time.
Duplicate comments, changed payloads or drift from the known baseline cause a
conflict rather than intentional overwrite. Never delete the journal to bypass
a conflict. Publication requires one authorized coordinator; observer, dashboard
and workers never publish.

This is **not distributed CAS or cross-machine exactly-once**. A noncooperative
external writer can edit between the final read and GitHub write; the comment API
provides no atomic exclusion for that window. Use one coordinator per issue/run
and shared state for cooperative writers; external concurrency requires a pause
and manual reconciliation. The fake test of this window documents a limitation,
not a protection guarantee. Network calls never occur inside SQLite transactions.

### Reading signals without confusing them with the record

- **executando confirmado:** recent execution activity; a bound worker requires
  a valid runtime query. It proves neither test/CI success nor stage completion.
- **aguardando autorização (observada):** a pending permission in the bound session;
  **aguardando resposta (observada):** a pending form. Only IDs/classification are
  shown, never text or answers. The open issue is counted as blocked only once
  while the signal is valid. Inactivity alone never creates a wait.
- **aguardando decisão:** canonical `owner_input` declared in the workflow. It
  outranks parallel activity and remains distinct from a runtime request.
- **último sinal local:** session execution started/succeeded/failed/interrupted,
  without promoting a completed turn to a semantic stage result.
- **Publicação/vínculo pendente:** a local intention not yet published or an
  incomplete binding. Details never present it as an existing GitHub stage.
- **cobertura incompleta / última lacuna:** preserved loss/restart/reconnection;
  queries recover current state, never the timestamp of a missed reply.

Synthetic example: `per_fixture` and `frm_fixture` pending for one worker.
Answering `frm_fixture` resolves only that ID; `per_fixture` remains pending.
If the permission disappears from a query after disconnection, its resolution
time remains unknown. Displayed canonical times receive no inferred duration.
Only the coordinator may publish runtime intervals with reliable native boundaries
and continuous coverage, without overlapping existing canonical waits.
Source errors, old epochs or expired TTLs remove confirmation even with a recent
heartbeat. GitHub closure still outranks local signals in the totals.

## Visual presentation and layouts

The dashboard uses a dark composition with a `>_` mark, four outlined indicators
(done, running, pending and blocked), totals/filter, milestone cards and a footer
with highlighted keys. Each card shows a title, repository subtitle, counters and
state distribution. Incoming order is preserved, including interleaved projects;
scrolling inside a card keeps repository/milestone context at the top only when
both its title and repository are outside the visible area. Normal navigation
frames collapsed cards fully when they fit, without an orphan card start at the
footer. Larger expanded cards and explicit detail scrolling remain contextually
clippable. Borders and dividers are not navigation targets. Collapsed cards use
less outer spacing; wide layouts replace C/E/P/B with full counter labels.

Global indicators and counters use the full inventory, not just visible issues:
filtering or collapsing does not change totals. Partial coverage and stale cache
remain explicit. Missing inventory is not a known empty milestone: both show an
unavailable percentage, but only a known empty milestone is confirmed 0/0.

The bar is **state distribution**, not an implementation estimate: green for
done, blue/cyan for confirmed execution, gray for pending and amber for blocked
or waiting. **Illustrative** example: one closed, two running, one pending and
one blocked gives **20% (1/5)**, not 60%. Tiny segments may occupy no cells;
counters remain exact. ASCII uses D/E/R/B segments (done/running/remaining/blocked,
from the Portuguese labels), with the counters providing the factual legend.

- **≥180 columns:** Issue / Workflow / Status / Tempo registrado table, stage
  pills and textual status badges. The 13 real protocol stages are not reduced
  to the eight in a reference image; `...` marks stages outside the window,
  keeping the current stage visible and full names available in details.
- **120–179:** issue/status/time on the first line, ruler on the next.
- **80–119:** compact fields, indicators in a 2×2 grid when height permits.
- **<80 or low height:** indicator summary, stacked fields and C/E/P/B;
  decoration gives way to selection and the current stage. 8×3 and 1×1 degrade
  without errors but cannot hold all information. Truncated titles use `…`/`...`.

Recorded time is canonical work for the current run, not calendar time or a live
activity stopwatch. Recorded zero is 0s; missing data is unavailable.
**Illustrative** example: 120s of work and 600s of calendar time show 2min in the
table; details retain both in seconds. History changes details only, organized
under Execução / Entrega / Fontes; long text wraps for scrolling. A recorded
current stage does not prove confirmed execution, and closing an issue does not
mark every stage completed or approved.

The theme is local to the app: light text, cyan borders, bold titles and focus
restricted to the main item, without reversing the whole card. The `●` focus
marker (`*` in ASCII) differs from the accordion triangle, with a stronger border
on the selected card and subdued secondary outlines. Pending bars are darker
than their labels and 0% is neutral, not green. Extended colors
are optional, with 8-color and monochrome fallbacks; `--no-color` inherits the
terminal background and `--ascii` replaces glyphs. No special fonts, palette
redefinition, tmux configuration or new dependencies. Cells cannot reproduce
graphical fonts, gradients or corner radii: fidelity is compositional and
semantic, not pixel-perfect. The operational dashboard does not copy a DEMO
badge, version or simulated values from the reference.

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
