"""Reducer e renderização curses independentes de rede."""
import curses
import copy
import locale
import queue
import unicodedata

from .common import text, utc_now, fresh
from .projection import STAGES, STAGE_LABELS, issue_view

FILTERS = (None, "running", "pending", "blocked", "done")
FILTER_LABELS = ("todas", "executando", "pendentes", "bloqueadas", "concluídas")


def cells(value):
    return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in value)


def fit(value, width, ascii_only=False):
    value = text(value, 10000)
    if ascii_only:
        value = "".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c)).encode("ascii", "replace").decode()
    result, size = [], 0
    for char in value:
        length = cells(char)
        if size + length > max(0, width):
            break
        result.append(char)
        size += length
    return "".join(result)


class UIState:
    def __init__(self, saved=None):
        saved = saved or {}
        self.expanded = {tuple(key) for key in saved.get("expanded", [])}
        self.details = {tuple(key) for key in saved.get("details", [])}
        self.selected = tuple(saved["selected"]) if saved.get("selected") else None
        self.filter = saved.get("filter", 0) if saved.get("filter", 0) in range(5) else 0
        self.detailed = bool(saved.get("detailed", False))
        self.history, self.offset = 0, 0
        self.scrolling = False

    def save(self):
        return {"expanded": sorted(self.expanded), "details": sorted(self.details), "selected": self.selected,
                "filter": self.filter, "detailed": self.detailed}

    def rows(self, model):
        rows = []
        for group in model.get("milestones", []):
            key = ("milestone", group["repository"], group["number"])
            rows.append((key, group))
            if key in self.expanded:
                for issue in group["issues"]:
                    if FILTERS[self.filter] is None or issue["group"] == FILTERS[self.filter]:
                        rows.append((("issue", issue["repository"], issue["number"]), issue))
        return rows

    def reconcile(self, model):
        keys = [key for key, _ in self.rows(model)]
        if self.selected not in keys:
            self.selected = (next((key for key in keys if key > self.selected), keys[-1]) if self.selected and keys else keys[0] if keys else None)
            self.history = 0

    def action(self, key, model):
        self.scrolling = False
        self.reconcile(model)
        rows = self.rows(model)
        keys = [k for k, _ in rows]
        previous = self.selected
        if key in ("j", "down", "k", "up") and keys:
            index = keys.index(self.selected)
            self.selected = keys[max(0, min(len(keys)-1, index + (1 if key in ("j", "down") else -1)))]
        elif key in ("enter", " ") and self.selected:
            collection = self.expanded if self.selected[0] == "milestone" else self.details
            collection.symmetric_difference_update({self.selected})
        elif key == "a":
            self.expanded = {("milestone", g["repository"], g["number"]) for g in model.get("milestones", [])}
        elif key == "c":
            self.expanded.clear()
        elif key == "f":
            self.filter = (self.filter + 1) % len(FILTERS)
        elif key == "v":
            self.detailed = not self.detailed
        elif key in ("[", "]"):
            item = next((value for k, value in rows if k == self.selected), {})
            self.history = max(0, min(item.get("history_count", 0)-1, self.history + (1 if key == "]" else -1)))
        if previous != self.selected:
            self.history = 0
        self.reconcile(model)


def ruler(issue, width, ascii_only=False):
    marks = {"completed": "+", "current": ">", "failed": "!", "interrupted": "!", "unknown": "?", "blocked": "B", "decision": "H"}
    states = issue.get("stages", {})
    current = issue.get("summary", {}).get("current_stage") if issue.get("summary") else None
    current = current or next((s for s in reversed(list(states)) if states[s] in {"current", "blocked", "decision"}), None)
    sequence = list(STAGES)
    if current and current not in sequence:
        sequence.append(current)
    tokens = [f"[{marks.get(states.get(s), '.')} {STAGE_LABELS.get(s, 'outra: '+s)}]" for s in sequence]
    index = sequence.index(current) if current in sequence else 0
    chosen = [tokens[index]]
    left, right = index-1, index+1
    while True:
        if right < len(tokens) and cells(" ".join(chosen + [tokens[right]])) <= width:
            chosen.append(tokens[right]); right += 1
        elif left >= 0 and cells(" ".join([tokens[left]] + chosen)) <= width:
            chosen.insert(0, tokens[left]); left -= 1
        else:
            break
    return fit(" ".join(chosen), width, ascii_only)


def detail_lines(issue):
    summary = issue.get("summary") or {}
    lines = [issue["url"], f"Run: {issue.get('run') or 'indisponível'} | histórico {issue.get('history', 0)+1}/{issue.get('history_count', 0)}",
             "Avisos: " + (", ".join(issue.get("warnings", [])) or "nenhum"),
             "Próximo passo registrado: " + (summary.get("status_summary", {}).get("next_action") or "indisponível"),
             "Tempos canônicos (s): trabalho registrado=" + str(summary.get("recorded_work_seconds", "indisponível")) +
             " calendário=" + str(summary.get("cycle_elapsed_seconds", "indisponível")),
             "Evidência: referência não implica aprovação"]
    proof = summary.get("status_summary", {}).get("last_confirmed") or {}
    if proof:
        lines += [f"Confirmação workflow ({proof.get('source')}): {proof.get('at')} UTC",
                  "Referência: " + (proof.get("evidence") or "indisponível / não verificada")]
    for stage in summary.get("stages", []):
        lines += [f"Tempo registrado {STAGE_LABELS.get(stage['stage'], 'outra: '+stage['stage'])}: trabalho {stage['recorded_work_seconds']}s / janela {stage['elapsed_seconds']}s"]
    for worker in issue.get("workers", []):
        execution = worker["execution"] or {}
        lines += [f"{STAGE_LABELS.get(worker['stage'], 'outra: '+worker['stage'])} / {worker['worker']}: {worker['label']}",
                  f"  {execution.get('kind', 'legado')}:{execution.get('id', 'indisponível')} | abertura {worker['opened_at']} UTC",
                  f"  observação workflow: {worker.get('last_observed_at') or 'indisponível'} UTC"]
        binding, runtime = worker.get("binding"), worker.get("runtime")
        if binding:
            lines += [f"  branch: {binding.get('branch') or 'indisponível'} | worktree: {binding['worktree']}"]
        if runtime:
            label = {"active": "agente ativo", "inactive": "sessão inativa", "absent": "sessão ausente", "incompatible": "vínculo incompatível",
                     "context_changed": "contexto alterado; refazer vínculo", "unknown": "desconhecido"}.get(runtime["state"], "desconhecido")
            lines += [f"  runtime: {label} em {runtime['at']} UTC (agente, não teste/CI)"]
    if not issue.get("workers"):
        lines += ["Etapa/atividade/tempo/branch/worktree: indisponíveis"]
    pr = issue.get("pr") or {}
    lines += ["PR: " + ("ambígua" if pr.get("ambiguous") else "sem entrega verificada" if not pr.get("candidates") else "vínculo GitHub verificado")]
    for candidate in pr.get("candidates", []):
        state_label = {"OPEN": "aberta", "CLOSED": "fechada", "MERGED": "mergeada"}.get(candidate["state"], "desconhecida")
        lines += [f"  {candidate['url']} {state_label} | merge {candidate.get('merged_at') or 'indisponível'}",
                  f"  head {candidate.get('head') or 'indisponível'}"]
    for label, health in (("GitHub", issue.get("inventory_health", {})), ("workflow", issue.get("comments_health", {})),
                          ("PR", issue.get("pr_health", {})), ("runtime", issue.get("runtime_health", {}))):
        lines += [f"Fonte {label}: coleta {health.get('fetched_at') or 'indisponível'} UTC | erro {health.get('error') or 'nenhum'}",
                  f"  tentativa {health.get('attempted_at') or 'indisponível'} | observação {health.get('observed_at') or 'indisponível'} UTC",
                  f"  próxima tentativa {health.get('retry_at') or 'indisponível'} UTC"]
    return lines


def render(model, state, width, height, ascii_only=False, detail=None):
    """Retorna linhas com identidade para viewport/seleção sem índices frágeis."""
    state.reconcile(model)
    lines = []
    for key, item in state.rows(model):
        if key[0] == "milestone":
            totals = item["totals"]
            count = len(item["issues"])
            percent = str(item["percent"]) + "%" if count else "--%"
            counts = (f"concluidas {totals['done']} executando {totals['running']} pendentes {totals['pending']} bloqueadas {totals['blocked']}" if width >= 100
                      else f"C{totals['done']} E{totals['running']} P{totals['pending']} B{totals['blocked']}")
            lines += [(key, f"{'v' if key in state.expanded else '>'} {item['repository']} #{item['number']} {item['title']}"),
                      (key, f"  {percent} ({totals['done']}/{count}) | {counts}")]
            if key in state.expanded and not any(FILTERS[state.filter] is None or i["group"] == FILTERS[state.filter] for i in item["issues"]):
                lines.append((key, "  Nenhuma issue neste filtro"))
        else:
            status = item["label"] if width >= 100 else {"done": "fechada", "running": "executando", "pending": "pendente", "blocked": "bloqueada"}[item["group"]]
            prefix, suffix = f"  #{item['number']} ", " | " + status
            title = fit(item["title"], max(0, width-1-cells(prefix+suffix)), ascii_only)
            lines.append((key, prefix + title + suffix))
            lines.append((key, "    " + ruler(item, max(1, width-5), ascii_only)))
            if state.detailed or key in state.details:
                lines += [(key, "    " + line) for line in detail_lines(detail if detail and key == state.selected else item)]
    if not lines:
        lines = [(None, "Sem alvos. Configure $XDG_CONFIG_HOME/aew/config.json (aew --help).")]
    # Scroll within a tall selected detail with PageUp/PageDown; keep selection
    # visible on ordinary navigation, without an ever-growing screen buffer.
    positions = [i for i, (key, _) in enumerate(lines) if key == state.selected]
    available = max(1, height-5)
    if positions and not state.scrolling:
        target = positions[0]
        # Keep the selected issue's named ruler visible, not merely its title
        # on the final content row. Explicit detail scrolling is independent.
        last = target + (1 if state.selected[0] == "issue" else 0)
        if target < state.offset:
            state.offset = target
        elif last >= state.offset + available:
            state.offset = max(0, last - available + 1)
    state.offset = max(0, min(state.offset, max(0, len(lines)-available)))
    health = model.get("health", [])
    live = bool(health) and all(s.get("fresh") for s in health)
    errors = [s["error"] for s in health + [model.get("runtime_health", {})] if s.get("error")]
    fetched = min((s["fetched_at"] for s in health if s.get("fetched_at")), default="sem coleta")
    header = ["AI ENGINEERING WORKFLOW / MILESTONE MONITOR", "GitHub " + ("recente" if live else "cache desatualizado / indisponivel") + " | " + fetched + " UTC",
              "Filtro: " + FILTER_LABELS[state.filter] + " | " + (model.get("error") or ", ".join(errors) or "leitura apenas")]
    visible = [(None, fit(line, width-1, ascii_only)) for line in header]
    visible += [(key, fit(line, width-1, ascii_only)) for key, line in lines[state.offset:state.offset+available]]
    visible += [(None, fit("j/k mover Enter abrir a/c todos f filtro v modo r atualizar [/] run PgUp/Dn q sair", width-1, ascii_only))]
    return visible[:max(0, height-1)]


def expire_samples(value, timing, now=None):
    """Expiração pura mesmo enquanto uma coleta grande/sem rede está em curso."""
    now = now or utc_now()
    result = copy.deepcopy(value)
    for source in result.get("health", []):
        source["fresh"] = bool(source.get("fresh") and fresh(source.get("fetched_at"), now, timing["github_ttl"]))
    for group in result.get("milestones", []):
        for issue in group["issues"]:
            if issue["group"] != "running":
                continue
            for worker in issue["workers"]:
                if worker["state"] != "running":
                    continue
                at = worker.get("runtime", {}).get("at") if worker.get("binding") and worker.get("runtime") else worker.get("last_observed_at")
                if not fresh(at, now, timing["activity_ttl"]):
                    worker.update(state="unknown", label="confirmação vencida")
            if not any(w["state"] == "running" for w in issue["workers"]):
                issue.update(group="pending", label="confirmação vencida; desconhecida")
                group["totals"]["running"] -= 1
                group["totals"]["pending"] += 1
    return result


def dashboard(screen, store, config, background, initial, no_color=False, ascii_only=False):
    state, current = UIState(store.local("ui", {})), initial
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.timeout(100)
    screen.keypad(True)
    use_color = not no_color and curses.has_colors()
    if use_color:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)
    try:
        while True:
            try:
                update = background.models.get_nowait()
                if "error" in update:
                    current = {**current, "error": update["error"]}
                else:
                    current = update
            except queue.Empty:
                pass
            current = expire_samples(current, config["timing"])
            height, width = screen.getmaxyx()
            screen.erase()
            detail = None
            if state.history and state.selected and state.selected[0] == "issue":
                issue = next((i for g in current.get("milestones", []) for i in g["issues"]
                              if ("issue", i["repository"], i["number"]) == state.selected), None)
                if issue:
                    snapshots = store.source(f"comments:{issue['repository']}:{issue['number']}").get("payload")
                    detail = {**issue, **issue_view(issue, snapshots, {}, store.bindings(), utc_now(), config["timing"], background.session_started, state.history)}
            for row, (identity, line) in enumerate(render(current, state, width, height, ascii_only, detail)):
                attr = curses.A_REVERSE if identity and identity == state.selected else curses.A_NORMAL
                if identity and identity[0] == "milestone":
                    attr |= curses.A_BOLD
                try:
                    screen.addstr(row, 0, line, attr)
                except curses.error:
                    pass  # resize/bottom-right cell; next frame redraws
            screen.refresh()
            key = screen.getch()
            if key in (ord("q"), 27):
                break
            if key == ord("r"):
                background.request()
            elif key in (curses.KEY_NPAGE, curses.KEY_PPAGE):
                state.scrolling = True
                state.offset = max(0, state.offset + (max(1, height-7) if key == curses.KEY_NPAGE else -max(1, height-7)))
            elif key != -1:
                translated = {curses.KEY_DOWN: "down", curses.KEY_UP: "up", 10: "enter", 13: "enter", curses.KEY_ENTER: "enter"}.get(key)
                state.action(translated or (chr(key) if 0 <= key < 256 else "resize"), current)
    finally:
        background.close()
        store.put_local("ui", state.save())


def ascii_locale():
    return "UTF" not in locale.getpreferredencoding(False).upper()
