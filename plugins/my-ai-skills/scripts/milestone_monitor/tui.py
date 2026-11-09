"""Reducer e renderização curses independentes de rede."""
import curses
import copy
import locale
import queue
import unicodedata
from dataclasses import dataclass

from .common import text, utc_now, fresh
from .projection import STAGES, STAGE_LABELS, issue_view

FILTERS = (None, "running", "pending", "blocked", "done")
FILTER_LABELS = ("todas", "executando", "pendentes", "bloqueadas", "concluídas")


@dataclass(frozen=True)
class Span:
    text: str
    role: str = "text"


@dataclass(frozen=True)
class Line:
    identity: object
    spans: tuple
    kind: str = "text"
    context: str = ""

    @property
    def text(self):
        return "".join(span.text for span in self.spans)


def clipped(spans, width, ascii_only=False):
    """Recorta por células sem perder os papéis nem sanitização por trecho."""
    result = []
    for span in spans:
        value = fit(span.text, width, ascii_only)
        if value:
            result.append(Span(value, span.role))
        width -= cells(value)
        if width <= 0:
            break
    return tuple(result)


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


def stage_tokens(issue):
    marks = {"completed": "+", "current": ">", "failed": "!", "interrupted": "!", "unknown": "?", "blocked": "B", "decision": "H"}
    states = issue.get("stages", {})
    current = issue.get("summary", {}).get("current_stage") if issue.get("summary") else None
    current = current or next((s for s in reversed(list(states)) if states[s] in {"current", "blocked", "decision"}), None)
    sequence = list(STAGES)
    if current and current not in sequence:
        sequence.append(current)
    roles = {"completed": "done", "current": "current", "failed": "failed", "interrupted": "failed",
             "blocked": "blocked", "decision": "blocked", "unknown": "warning"}
    tokens = [Span(f"[{marks.get(states.get(s), '.')} {STAGE_LABELS.get(s, 'outra: '+s)}]",
                   roles.get(states.get(s), "muted")) for s in sequence]
    index = sequence.index(current) if current in sequence else 0
    return tokens, index


def ruler_spans(issue, width, ascii_only=False):
    tokens, index = stage_tokens(issue)
    chosen = [tokens[index]]
    left, right = index-1, index+1
    while True:
        if right < len(tokens) and sum(cells(s.text) for s in chosen + [tokens[right]]) + len(chosen) + 8 <= width:
            chosen.append(tokens[right]); right += 1
        elif left >= 0 and sum(cells(s.text) for s in [tokens[left]] + chosen) + len(chosen) + 8 <= width:
            chosen.insert(0, tokens[left]); left -= 1
        else:
            break
    result = [Span("... ", "muted")] if left >= 0 and width >= cells(chosen[0].text) + 4 else []
    for token in chosen:
        if result and result[-1].text != "... ":
            result.append(Span(" "))
        result.append(Span(token.text, "pill_" + token.role))
    if right < len(tokens):
        result.append(Span(" ...", "muted"))
    return clipped(result, width, ascii_only)


def ruler(issue, width, ascii_only=False):
    return "".join(span.text for span in ruler_spans(issue, width, ascii_only))


def detail_lines(issue):
    summary = issue.get("summary") or {}
    lines = ["Execução", f"#{issue['number']} {issue['title']}", issue["url"], "Estado: " + issue["label"],
             f"Run: {issue.get('run') or 'indisponível'} | histórico {issue.get('history', 0)+1}/{issue.get('history_count', 0)}",
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
    lines += ["Etapas (registro, não confirmação de atividade): " + " ".join(s.text for s in stage_tokens(issue)[0])]
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
            for request in runtime.get("requests", []):
                label = "aguardando autorização" if request["kind"] == "permission" else "aguardando resposta"
                lines += [f"  {label} (observada): {request['request_id']} | sem duração canônica inferida"]
            if runtime.get("signal"):
                lines += ["  último sinal local: " + runtime["signal"]["type"] + " (não encerra etapa)"]
            if runtime.get("coverage_gap"):
                lines += ["  cobertura de pedidos incompleta; horários ausentes não medidos"]
    if not issue.get("workers"):
        lines += ["Etapa/atividade/tempo/branch/worktree: indisponíveis"]
    observer = issue.get("observer")
    if observer:
        lines += [f"Observador: {observer.get('state') or 'desconhecido'} | saúde {'recente' if observer['healthy'] else 'indisponível/vencida'}",
                  f"  epoch {observer['epoch']} | heartbeat {observer['heartbeat_at']} UTC"]
        coverage = observer.get("coverage", {})
        if coverage.get("gap_at"):
            lines += [f"  última lacuna: {coverage['gap_at']} UTC | {coverage.get('reason') or 'indisponível'}",
                      "  consulta recupera estado atual, não duração ausente"]
    for operation in issue.get("publication_pending", []):
        lines += [f"Publicação/vínculo pendente: {operation.get('operation_id')} | {operation.get('state')} / {operation.get('binding_state') or 'sem vínculo'}",
                  "  intenção local, não etapa publicada no GitHub"]
    pr = issue.get("pr") or {}
    lines += ["Entrega", "PR: " + ("ambígua" if pr.get("ambiguous") else "sem entrega verificada" if not pr.get("candidates") else "vínculo GitHub verificado")]
    for candidate in pr.get("candidates", []):
        state_label = {"OPEN": "aberta", "CLOSED": "fechada", "MERGED": "mergeada"}.get(candidate["state"], "desconhecida")
        lines += [f"  {candidate['url']} {state_label} | merge {candidate.get('merged_at') or 'indisponível'}",
                  f"  head {candidate.get('head') or 'indisponível'}"]
    lines.append("Fontes")
    for label, health in (("GitHub", issue.get("inventory_health", {})), ("workflow", issue.get("comments_health", {})),
                          ("PR", issue.get("pr_health", {})), ("runtime", issue.get("runtime_health", {}))):
        lines += [f"Fonte {label}: coleta {health.get('fetched_at') or 'indisponível'} UTC | erro {health.get('error') or 'nenhum'}",
                  f"  tentativa {health.get('attempted_at') or 'indisponível'} | observação {health.get('observed_at') or 'indisponível'} UTC",
                  f"  próxima tentativa {health.get('retry_at') or 'indisponível'} UTC"]
    return lines


GROUPS = ("done", "running", "pending", "blocked")
GROUP_LABELS = ("concluídas", "executando", "pendentes", "bloqueadas")
MARKS = {"done": "✓", "running": "▶", "pending": "○", "blocked": "!"}
ASCII_MARKS = dict(zip(GROUPS, ("+", ">", "o", "!")))


def ellipsis(value, width, ascii_only=False):
    value = fit(value, 10000, ascii_only)
    if cells(value) <= width:
        return value
    mark = "..." if ascii_only else "…"
    return fit(value, max(0, width-cells(mark))) + fit(mark, width)


def padded(spans, width, ascii_only=False):
    spans = clipped(spans, width, ascii_only)
    return spans + (Span(" " * max(0, width-sum(cells(s.text) for s in spans))),)


def counts_spans(totals, compact=False, ascii_only=False, digits=None):
    marks = ASCII_MARKS if ascii_only else MARKS
    result = []
    for index, group in enumerate(GROUPS):
        if index:
            result.append(Span("   "))
        label = "CEPB"[index] if compact else marks[group]
        suffix = "" if compact else " " + GROUP_LABELS[index]
        value = str(totals[group]).rjust((digits or {}).get(group, 1))
        result.append(Span(f"{label} {value}{suffix}", group))
    return tuple(result)


def distribution(totals, width, ascii_only=False):
    """Maiores restos: soma exata por células, sem alterar os contadores."""
    total = sum(totals[g] for g in GROUPS)
    if not total or width <= 0:
        return ()
    sizes = [totals[g] * width // total for g in GROUPS]
    order = sorted(range(4), key=lambda i: -(totals[GROUPS[i]] * width % total))
    for index in order[:width-sum(sizes)]:
        sizes[index] += 1
    # ASCII também distingue segmentos quando não há cores.
    return tuple(Span(("DERB"[i] if ascii_only else "█") * size, "bar_pending" if group == "pending" else group)
                 for i, (group, size) in enumerate(zip(GROUPS, sizes)) if size)


def duration(issue):
    value = (issue.get("summary") or {}).get("recorded_work_seconds")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        return "indisponível"
    seconds = int(value)
    if seconds < 60:
        return f"{seconds}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}min" + (f" {seconds}s" if seconds else "")
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02}min" + (f" {seconds}s" if seconds else "")


def missing_inventory(group):
    # Placeholder explícito já fornecido pela projeção; não reinterpretar vazio.
    return group["title"] == "sem inventário" and not group["issues"]


def health_spans(model, width=10000):
    sources = model.get("health", [])
    live = bool(sources) and all(s.get("fresh") for s in sources)
    partial = any(missing_inventory(g) for g in model.get("milestones", []))
    status = "cobertura parcial / sem inventário" if partial else "recente" if live else "cache desatualizado / indisponível"
    fetched = min((s["fetched_at"] for s in sources if s.get("fetched_at")), default="sem coleta")
    errors = [s["error"] for s in sources + [model.get("runtime_health", {})] if s.get("error")]
    observer = model.get("observer")
    if observer and (observer.get("error") or not observer.get("healthy")):
        errors.append(observer.get("error") or "observador indisponível/vencido")
    if model.get("error"):
        errors.insert(0, model["error"])
    if errors and width < 120:
        return (Span("Fonte: " + ", ".join(errors) + " | GitHub: " + status, "warning"),)
    return (Span("GitHub: " + status, "muted" if live else "warning"),
            Span(" | " + ", ".join(errors), "warning") if errors else Span(""),
            Span(" | coleta " + fetched + " UTC", "muted"),
            Span(" | observador " + ("recente" if observer["healthy"] else "vencido"), "muted" if observer["healthy"] else "warning") if observer else Span(""))


def header_lines(model, state, width, height, ascii_only):
    terminal_width = width+1
    groups = model.get("milestones", [])
    totals = {g: sum(m["totals"][g] for m in groups) for g in GROUPS}
    partial = any(missing_inventory(g) for g in groups)
    def line(spans, kind="header"):
        return Line(None, clipped(spans, width, ascii_only), kind)
    filters = [Span("Filtro: ", "muted")]
    for index, label in enumerate(FILTER_LABELS):
        filters.append(Span((f"[{label}]" if index == state.filter else label) + "  ", "current" if index == state.filter else "muted"))
    summary = f"{len(groups)} milestones  ·  {sum(totals.values())} issues" + (" conhecidas (parcial)" if partial else "")
    if height < 18 or terminal_width < 80:
        # Ativo primeiro em telas pequenas, em vez de truncar a opção ativa.
        return [line((Span("Milestone Monitor", "title"), Span(" | [" + FILTER_LABELS[state.filter] + "]", "current"))),
                line(counts_spans(totals, True, ascii_only) + ((Span(" parcial", "warning"),) if partial else ())),
                line(health_spans(model, width), "health")]
    result = [line((Span(" >_ ", "done"), Span("AI Engineering Workflow", "title"))),
              line((Span("    Milestone Monitor  |  OpenCode + my-ai-skills  |  somente leitura", "muted"),)),
              line((Span(("-" if ascii_only else "─") * width, "border"),))]
    columns = 4 if terminal_width >= 120 else 2
    card_width = (width-(columns-1)*2)//columns
    tl, tr, bl, br, h, v = ("+", "+", "+", "+", "-", "|") if ascii_only else ("╭", "╮", "╰", "╯", "─", "│")
    for offset in range(0, 4, columns):
        top, middle, subtitle, bottom = [], [], [], []
        for index in range(offset, offset+columns):
            group = GROUPS[index]
            if index != offset:
                for row in (top, middle, subtitle, bottom):
                    row.append(Span("  "))
            top.append(Span(tl+h*(card_width-2)+tr, "border"))
            bottom.append(Span(bl+h*(card_width-2)+br, "border"))
            middle += [Span(v + " ", "border")]
            value = str(totals[group]) + ("+" if partial else "")
            content = (Span((ASCII_MARKS if ascii_only else MARKS)[group] + "  │  " + value, group),)
            if ascii_only:
                content = (Span(ASCII_MARKS[group] + "  |  " + value, group),)
            middle += list(padded(content, card_width-4, ascii_only)) + [Span(" " + v, "border")]
            subtitle += [Span(v+" ", "border")] + list(padded((Span("      " + GROUP_LABELS[index]),), card_width-4, ascii_only)) + [Span(" "+v, "border")]
        result += [line(top), line(middle), line(subtitle), line(bottom)]
    total_span = (Span(summary, "current"),)
    if cells(summary) + sum(cells(s.text) for s in filters) + 4 <= width:
        result.append(line(padded(total_span, width-sum(cells(s.text) for s in filters), ascii_only) + tuple(filters)))
    else:
        result += [line(total_span), line(filters)]
    result.append(line(health_spans(model, width), "health"))
    result.append(line((Span(""),)))
    return result


def content_lines(model, state, width, height, ascii_only, detail):
    """Composição independente das cores curses e das fontes externas."""
    lines = []
    terminal_width = width+1
    box = width >= 60 and height >= 18
    inner = max(1, width-4 if box else width-1)
    roomy = height >= 30
    digits = {g: max((len(str(m["totals"][g])) for m in model.get("milestones", [])), default=1) for g in GROUPS}
    tl, tr, bl, br, h, v = ("+", "+", "+", "+", "-", "|") if ascii_only else ("╭", "╮", "╰", "╯", "─", "│")
    for group in model.get("milestones", []):
        key = ("milestone", group["repository"], group["number"])
        context = f"{group['repository']} / #{group['number']} {group['title']}"
        focused = state.selected == key or any(state.selected == ("issue", i["repository"], i["number"]) for i in group["issues"])
        border_role = "focus_border" if focused else "border"
        def add(spans, identity=None, kind="text"):
            spans = padded(spans, inner, ascii_only) if box else clipped(spans, inner, ascii_only)
            if box:
                spans = (Span(v+" ", border_role),) + spans + (Span(" "+v, border_role),)
            lines.append(Line(identity, spans, kind, context))
        if box:
            lines.append(Line(None, (Span(tl+h*(width-2)+tr, border_role),), "card_top", context))
        expanded = key in state.expanded
        arrow = ("v" if expanded else ">") if ascii_only else ("▼" if expanded else "▶")
        title = f"{arrow} #{group['number']} {group['title']}"
        count = len(group["issues"])
        missing = missing_inventory(group)
        progress = "--% sem inventário" if missing else (f"{group['percent']}%" if count else "--% vazio") + f" ({group['totals']['done']}/{count})"
        focus = ("* " if ascii_only else "● ") if state.selected == key else "  "
        title_role = "focus" if state.selected == key else "title"
        progress_role = "done" if group["totals"]["done"] and not missing else "muted"
        if terminal_width >= 120:
            right_width = min(inner//2, 82)
            label_width = cells(progress)+2
            bar_width = max(0, right_width-label_width)
            bar = distribution(group["totals"], bar_width, ascii_only) if not missing else ()
            add(padded((Span(focus+ellipsis(title, inner-right_width-2, ascii_only), title_role),), inner-right_width, ascii_only)
                + padded(bar, bar_width, ascii_only) + (Span("  " + progress, progress_role),), key, "milestone")
        else:
            add((Span(focus+ellipsis(title, inner-2, ascii_only), title_role),), key, "milestone")
        if terminal_width >= 180 and not expanded:
            repo_width = inner//3
            add(padded((Span("  " + ellipsis(group["repository"], repo_width-2, ascii_only), "muted"),), repo_width, ascii_only)
                + counts_spans(group["totals"], False, ascii_only, digits), kind="repository")
        else:
            add((Span("  " + ellipsis(group["repository"], inner-2, ascii_only), "muted"),), kind="repository")
            counts = counts_spans(group["totals"], terminal_width < 120, ascii_only, digits if terminal_width >= 120 else None)
            add(((Span(progress + " | ", progress_role),) if terminal_width < 120 else ()) + counts)
        if expanded:
            issues = [i for i in group["issues"] if FILTERS[state.filter] is None or i["group"] == FILTERS[state.filter]]
            if not issues:
                add((Span("Nenhuma issue neste filtro", "muted"),))
            table = terminal_width >= 180
            title_width = int(inner*.29)
            time_width = 17
            status_width = max(20, int(inner*.14))
            workflow_width = inner-title_width-status_width-time_width-9
            def columns(title_spans, workflow, status, timing):
                result = ()
                for index, (spans, size) in enumerate(((title_spans, title_width), (workflow, workflow_width), (status, status_width), (timing, time_width))):
                    if index:
                        result += (Span(" │ " if not ascii_only else " | ", "border"),)
                    result += padded(spans, size, ascii_only)
                return result
            if issues and terminal_width >= 120:
                add((Span(h*inner, "border"),))
                if table:
                    add(columns((Span("Issue", "title"),), (Span("Workflow (etapas registradas)", "title"),),
                                (Span("Status", "title"),), (Span("Tempo registrado", "title"),)))
            for issue in issues:
                identity = ("issue", issue["repository"], issue["number"])
                mark = (ASCII_MARKS if ascii_only else MARKS)[issue["group"]]
                issue_title = f"{mark} #{issue['number']} {issue['title']}"
                selected = identity == state.selected
                prefix = "> " if selected else "  "
                status = (Span("["+issue["label"]+"]", "pill_" + issue["group"]),)
                timing = (Span(duration(issue), "muted"),)
                if table:
                    add(columns((Span(prefix+ellipsis(issue_title, title_width-2, ascii_only), "focus" if selected else "text"),),
                                ruler_spans(issue, workflow_width, ascii_only),
                                (Span(ellipsis(status[0].text, status_width, ascii_only), "pill_" + issue["group"]),), timing), identity, "issue")
                else:
                    # Número e estado têm prioridade sobre títulos longos.
                    short_status = "[" + issue["label"] + "]"
                    status_budget = min(cells(short_status), max(12, inner//2))
                    label = ellipsis(short_status, status_budget, ascii_only)
                    timing_text = " " + duration(issue) if terminal_width >= 120 else ""
                    left_width = max(0, inner-cells(label+timing_text)-1)
                    add(padded((Span(prefix+ellipsis(issue_title, max(0, left_width-2), ascii_only), "focus" if selected else "text"),), left_width, ascii_only)
                        + (Span(" "), Span(label, "pill_" + issue["group"]), Span(timing_text, "muted")), identity, "issue")
                    add(ruler_spans(issue, inner, ascii_only), identity, "ruler")
                if state.detailed or identity in state.details:
                    for value in detail_lines(detail if detail and identity == state.selected else issue):
                        section = value in {"Execução", "Entrega", "Fontes"}
                        value = fit(value, 10000, ascii_only)
                        while value:
                            part = fit(value, max(1, inner-2))
                            if not part:
                                break
                            add((Span("  " + part, "section" if section else "muted"),), identity, "detail")
                            value = value[len(part):]
                if roomy and table:
                    add((Span(h*inner, "divider"),))
        if box:
            lines.append(Line(None, (Span(bl+h*(width-2)+br, border_role),), "card_bottom", context))
        if roomy and expanded:
            lines.append(Line(None, (), "space", context))
    if not lines:
        lines.append(Line(None, (Span("Sem alvos. Configure $XDG_CONFIG_HOME/aew/config.json (aew --help).", "warning"),)))
    return lines


def render_frame(model, state, width, height, ascii_only=False, detail=None):
    state.reconcile(model)
    width, budget = max(0, width-1), max(0, height-1)
    if not width or not budget:
        return []
    header = header_lines(model, state, width, height, ascii_only)
    if budget-len(header)-3 < 3:
        header = header_lines(model, state, width, 12, ascii_only)
    # Conservar saúde e conteúdo mesmo em terminais extremamente baixos.
    if budget < 7:
        header = header[-1:] if budget >= 4 else []
    footer = [Line(None, (Span("[↑↓/jk]" if not ascii_only else "[jk]", "key"), Span(" navegar  "), Span("[Enter]", "key"), Span(" abrir/recolher  "),
                         Span("[a/c]", "key"), Span(" todos  "), Span("[f]", "key"), Span(" filtrar  "), Span("[v]", "key"), Span(" detalhes  "),
                         Span("[r]", "key"), Span(" atualizar  "), Span("[ / ]", "key"), Span(" run  "), Span("[PgUp/Dn]", "key"), Span(" rolar  "), Span("[q]", "key"), Span(" sair")), "footer")]
    if width < 150:
        footer = [Line(None, (Span("[jk] mover [Enter] abrir [a/c] todos [f] filtro [v] detalhes [q] sair", "key"),), "footer")]
    if width < 80:
        footer = [Line(None, (Span("[jk] [Enter] abrir [f] filtro [q] sair", "key"),), "footer")]
    if budget < 4:
        footer = []
    elif height >= 30:
        footer.insert(0, Line(None, (Span(("-" if ascii_only else "─")*width, "border"),), "border"))
    lines = content_lines(model, state, width, height, ascii_only, detail)
    # Navegação usa um orçamento conservador; a linha de contexto só é desenhada
    # quando necessária. Cartões curtos rolam pelos limites, não pelo título.
    area = max(1, budget-len(header)-len(footer))
    available = max(1, area-1)
    bounds = {}
    for index, line in enumerate(lines):
        start, _ = bounds.get(line.context, (index, index))
        bounds[line.context] = (start, index+1)
    positions = [i for i, line in enumerate(lines) if line.identity == state.selected and line.kind in {"milestone", "issue", "ruler"}]
    selected_context = lines[positions[0]].context if positions else None
    if positions and not state.scrolling:
        first, last = positions[0], positions[-1]
        if state.selected[0] == "milestone":
            start, end = bounds[selected_context]
            first = start
            last = end-1 if end-start <= available else min(positions[0]+2, first+available-1)
        if first < state.offset:
            state.offset = first
        elif last >= state.offset+available:
            state.offset = first if state.selected[0] == "milestone" else max(0, last-available+1)
        state.offset = max(0, min(state.offset, len(lines)-1))
        start, end = bounds[lines[state.offset].context]
        if start < state.offset and end-start <= available:
            state.offset = end if end <= first else start
        while state.offset < first and lines[state.offset].kind in {"card_bottom", "space"}:
            state.offset += 1
    state.offset = max(0, min(state.offset, len(lines)-1))
    context = lines[state.offset].context
    context_visible = any(line.context == context and line.kind in {"milestone", "repository"}
                          for line in lines[state.offset:state.offset+area])
    sticky = bool(context and not context_visible and state.offset > bounds[context][0])
    content = [Line(None, (Span(ellipsis(context, width, ascii_only), "context"),), "context")] if sticky else []
    visible = lines[state.offset:state.offset+max(1, area-len(content))]
    if visible:
        # Não iniciar um cartão que não cabe no espaço restante. Cartões grandes
        # e detalhes continuam recortáveis, preservando a navegação/rolagem.
        start, end = bounds[visible[-1].context]
        tail_start = start-state.offset
        if end > state.offset+len(visible) and tail_start >= 0:
            orphan = all(line.kind in {"card_top", "space"} for line in visible[tail_start:])
            short_card = end-start <= area and visible[-1].context != selected_context
            if orphan or short_card:
                visible = visible[:tail_start]
    content += visible
    frame = header + content
    # Rodapé fixo na base, não imediatamente após uma lista curta.
    while len(frame) < budget-len(footer):
        frame.append(Line(None, ()))
    frame = frame[:max(0, budget-len(footer))] + footer
    return [Line(line.identity, clipped(line.spans, width, ascii_only), line.kind, line.context) for line in frame[:budget]]


def render(model, state, width, height, ascii_only=False, detail=None):
    """Adaptador textual: mesmas identidades e textos do frame rico."""
    return [(line.identity, line.text) for line in render_frame(model, state, width, height, ascii_only, detail)]


def init_styles(no_color=False):
    """Paleta local: não redefine cores globais nem exige 256 cores."""
    emphasis = {"title": curses.A_BOLD, "focus": curses.A_BOLD | curses.A_UNDERLINE,
                "current": curses.A_BOLD | curses.A_UNDERLINE, "running": curses.A_BOLD,
                "section": curses.A_BOLD, "warning": curses.A_BOLD, "key": curses.A_BOLD, "done": curses.A_BOLD,
                "context": curses.A_BOLD, "muted": curses.A_DIM, "pending": curses.A_DIM,
                "focus_border": curses.A_BOLD, "bar_pending": curses.A_DIM}
    styles = {role: emphasis.get(role, curses.A_NORMAL) for role in
              ("text", "border", "focus_border", "divider", "title", "focus", "current", "running", "done", "blocked", "failed", "warning", "key", "context", "muted", "pending", "bar_pending", "section")}
    for role in ("done", "current", "running", "blocked", "failed", "warning", "muted", "pending"):
        styles["pill_" + role] = styles[role]
    if no_color:
        return styles
    try:
        if not curses.has_colors():
            return styles
        curses.start_color()
        curses.use_default_colors()
        extended = curses.COLORS >= 256
        colors = {"text": 252, "border": 23, "focus_border": 80, "divider": 23, "title": 255, "focus": 255, "current": 45,
                  "running": 39, "done": 48, "blocked": 214, "failed": 203,
                  "warning": 214, "key": 80, "context": 80, "muted": 245, "pending": 245, "bar_pending": 238, "section": 80}
        basic = {"border": curses.COLOR_CYAN, "focus_border": curses.COLOR_CYAN, "divider": curses.COLOR_CYAN,
                 "current": curses.COLOR_CYAN, "running": curses.COLOR_CYAN,
                 "done": curses.COLOR_GREEN, "blocked": curses.COLOR_YELLOW, "warning": curses.COLOR_YELLOW,
                 "failed": curses.COLOR_RED, "key": curses.COLOR_CYAN, "context": curses.COLOR_CYAN, "section": curses.COLOR_CYAN}
        if curses.COLOR_PAIRS <= len(styles):
            return styles
        colored = {}
        for index, role in enumerate(styles, 1):
            semantic = role.removeprefix("pill_")
            background = {"done": 22, "current": 24, "running": 24, "blocked": 58, "failed": 52, "warning": 58, "muted": 235, "pending": 235}.get(semantic, 0) if extended and role.startswith("pill_") else curses.COLOR_BLACK
            curses.init_pair(index, colors[semantic] if extended else basic.get(semantic, curses.COLOR_WHITE), background)
            colored[role] = curses.color_pair(index) | styles[role]
        # Cinza explícito: não reduzir ainda mais o contraste com dim.
        for role in ("muted", "pending", "bar_pending", "pill_muted", "pill_pending"):
            if extended:
                colored[role] &= ~curses.A_DIM
        return colored
    except curses.error:
        return styles


def draw_frame(screen, frame, styles):
    """Atributos por span; não pinta seleção sobre estados ou detalhes."""
    try:
        screen.bkgd(" ", styles["text"])
    except curses.error:
        pass
    screen.erase()
    for row, line in enumerate(frame):
        column = 0
        for span in line.spans:
            try:
                screen.addstr(row, column, span.text, styles.get(span.role, styles["text"]))
            except curses.error:
                pass  # resize/borda: próximo frame redesenha
            column += cells(span.text)


def expire_samples(value, timing, now=None):
    """Expiração pura mesmo enquanto uma coleta grande/sem rede está em curso."""
    now = now or utc_now()
    result = copy.deepcopy(value)
    observer = result.get("observer")
    if observer:
        observer["healthy"] = bool(observer.get("healthy") and fresh(observer.get("heartbeat_at"), now, 15))
    for source in result.get("health", []):
        source["fresh"] = bool(source.get("fresh") and fresh(source.get("fetched_at"), now, timing["github_ttl"]))
    for group in result.get("milestones", []):
        for issue in group["issues"]:
            for worker in issue["workers"]:
                if worker["state"] not in {"running", "waiting"}:
                    continue
                at = worker.get("runtime", {}).get("at") if worker.get("binding") and worker.get("runtime") else worker.get("last_observed_at")
                if not fresh(at, now, timing["activity_ttl"]) or worker.get("independent") and not (observer or {}).get("healthy"):
                    worker.update(state="unknown", label="confirmação vencida")
            if issue["group"] != "running" and not issue.get("local_block"):
                continue
            if not any(w["state"] in {"running", "waiting"} for w in issue["workers"]):
                previous = issue["group"]
                issue.update(group="pending", label="confirmação vencida; desconhecida", local_block=False)
                group["totals"][previous] -= 1
                group["totals"]["pending"] += 1
            elif issue.get("local_block") and not any(w["state"] == "waiting" for w in issue["workers"]):
                issue.update(group="running", label="executando confirmado", local_block=False)
                group["totals"]["blocked"] -= 1
                group["totals"]["running"] += 1
    return result


def dashboard(screen, store, config, background, initial, no_color=False, ascii_only=False):
    state, current = UIState(store.local("ui", {})), initial
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.timeout(100)
    screen.keypad(True)
    styles = init_styles(no_color)
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
            detail = None
            if state.history and state.selected and state.selected[0] == "issue":
                issue = next((i for g in current.get("milestones", []) for i in g["issues"]
                              if ("issue", i["repository"], i["number"]) == state.selected), None)
                if issue:
                    snapshots = store.source(f"comments:{issue['repository']}:{issue['number']}").get("payload")
                    detail = {**issue, **issue_view(issue, snapshots, {}, store.bindings(), utc_now(), config["timing"], background.session_started, state.history)}
            draw_frame(screen, render_frame(current, state, width, height, ascii_only, detail), styles)
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
