#!/usr/bin/env python3
"""AI Engineering Workflow: demo TUI (stdlib curses, no external dependencies)."""
from __future__ import annotations

import curses
import locale
from dataclasses import dataclass

locale.setlocale(locale.LC_ALL, "")

STAGES = ["Explore", "Proposal", "Apply", "Tests", "PR", "Review", "Merge", "Archive"]
STATUS = {"done": "concluida", "running": "executando", "pending": "pendente", "blocked": "bloqueada"}

@dataclass
class Issue:
    number: int
    title: str
    status: str
    stage: int = 0  # 0 not started; 1..8 stage in progress; 9 all finished
    agent: str = ""
    elapsed: str = ""

@dataclass
class Milestone:
    number: int
    title: str
    repo: str
    issues: list[Issue]
    expanded: bool = False

MILESTONES = [
    Milestone(31, "Configuracao inicial da loja", "rancho-das-figueiras-magento2", [
        Issue(381, "Configuracoes regionais do Brasil", "done", 9),
        Issue(382, "Metodos de pagamento", "running", 3, "OpenCode", "18min"),
        Issue(383, "Validacao de configuracoes no deploy", "running", 5, "OpenCode", "7min"),
        Issue(384, "Metodos de entrega", "pending"),
        Issue(385, "Smoke tests da loja", "pending"),
    ], True),
    Milestone(13, "Rancho Club - Backend", "rancho-das-figueiras-magento2", [
        Issue(415, "Sample data do Rancho Club", "done", 9),
        Issue(421, "Acumulo de pontos e brindes", "done", 9),
        Issue(428, "Correcao no saldo de pontos", "blocked", 4, "OpenCode", "1h12min"),
        Issue(434, "Ajustes de idempotencia", "pending"),
    ]),
    Milestone(15, "Rancho Club - Mobile", "rancho-das-figueiras-mobile", [
        Issue(254, "Integracao GraphQL do clube", "done", 9),
        Issue(285, "Resgate de brindes", "running", 6, "OpenCode", "26min"),
        Issue(287, "UX e mensagens do Rancho Club", "pending"),
        Issue(302, "Configuracao do Sonar", "pending"),
    ]),
    Milestone(5, "Retirada de Pedidos", "rancho-das-figueiras-operacional-mobile", [
        Issue(36, "Fluxo de retirada", "pending"),
        Issue(37, "Validacao de pedidos", "pending"),
        Issue(38, "Historico de retiradas", "pending"),
    ]),
]

# curses color pairs
NORMAL, GREEN, BLUE, YELLOW, RED, DIM, SELECT, HEADER = range(1, 9)

def safe_add(win, y, x, string, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0 or string == "":
        if x < 0 and string:
            string = string[-x:]
            x = 0
        else:
            return
    try:
        win.addnstr(y, x, string, max(0, w-x-1), attr)
    except curses.error:
        pass

def text_fit(s, n):
    if n <= 0: return ""
    return s if len(s) <= n else (s[:max(0, n-1)] + "…")

def init_colors():
    if not curses.has_colors(): return
    curses.start_color()
    try: curses.use_default_colors()
    except curses.error: pass
    for pair, fg in [(NORMAL, curses.COLOR_WHITE), (GREEN, curses.COLOR_GREEN),
                     (BLUE, curses.COLOR_CYAN), (YELLOW, curses.COLOR_YELLOW),
                     (RED, curses.COLOR_RED), (DIM, curses.COLOR_WHITE),
                     (SELECT, curses.COLOR_BLACK), (HEADER, curses.COLOR_CYAN)]:
        curses.init_pair(pair, fg, curses.COLOR_BLUE if pair == SELECT else -1)

def color(pair, bold=False):
    return (curses.color_pair(pair) if curses.has_colors() else 0) | (curses.A_BOLD if bold else 0)

def counts(issues):
    return {s: sum(i.status == s for i in issues) for s in STATUS}

def stage_bar(w, issue):
    # Full labels on wide terminals; short labels on narrower ones.
    labels = STAGES if w >= 100 else ["Expl", "Prop", "Apply", "Test", "PR", "Rev", "Merge", "Arch"]
    cells = []
    for idx, name in enumerate(labels, 1):
        if issue.stage == 9 or idx < issue.stage:
            attr, prefix = color(GREEN, True), "✓"
        elif idx == issue.stage:
            attr = color(RED if issue.status == "blocked" else BLUE, True)
            prefix = "!" if issue.status == "blocked" else ">"
        else:
            attr, prefix = color(DIM), "·"
        cells.append((f"[{prefix}{name}]", attr))
    return cells

def build_view(milestones, filter_status, details):
    """List of (type, milestone index, issue index), for both drawing and navigation."""
    rows = []
    for mi, m in enumerate(milestones):
        matches = [(ii,i) for ii,i in enumerate(m.issues) if filter_status == "all" or i.status == filter_status]
        if not matches: continue
        rows.append(("milestone", mi, -1))
        if m.expanded:
            for ii, _ in matches:
                rows.append(("issue", mi, ii))
                if details == (mi,ii): rows.append(("details",mi,ii))
        rows.append(("blank",mi,-1))
    return rows

def render(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.timeout(250)
    init_colors()
    selected = 0
    offset = 0
    status_filter = "all"
    details = None
    filters = ["all", "running", "pending", "blocked", "done"]
    while True:
        h,w = stdscr.getmaxyx()
        stdscr.erase()
        view = build_view(MILESTONES, status_filter, details)
        selectable = [r for r in view if r[0] in ("milestone", "issue")]
        selected = min(selected, max(0,len(selectable)-1))
        active = selectable[selected] if selectable else None
        totals = counts([i for m in MILESTONES for i in m.issues])
        safe_add(stdscr,0,2," AI ENGINEERING WORKFLOW  /  MILESTONE MONITOR ",color(HEADER,True))
        safe_add(stdscr,1,2,"DEMO OFFLINE  |  OpenCode + my-ai-skills (dados simulados)",color(DIM))
        safe_add(stdscr,3,2,f"{len(MILESTONES)} milestones   {sum(len(m.issues) for m in MILESTONES)} issues",color(NORMAL,True))
        stats = f"  {totals['done']} concluidas   {totals['running']} executando   {totals['pending']} pendentes   {totals['blocked']} bloqueadas"
        safe_add(stdscr,4,2,stats,color(NORMAL))
        safe_add(stdscr,5,2,f"Filtro: {status_filter.upper()}  [f alternar]    [a expandir todos] [c recolher todos]",color(BLUE))
        safe_add(stdscr,6,2,"─"*max(0,w-4),color(DIM))
        y0, yend = 7, h-3
        display_rows = []
        for entry in view:
            typ, mi, ii = entry
            if typ == "milestone": display_rows.extend([(entry,"m_title"),(entry,"m_stats")])
            elif typ == "issue": display_rows.extend([(entry,"i_title"),(entry,"i_stages")])
            elif typ == "details": display_rows.extend([(entry,"d_info"),(entry,"d_help")])
            else: display_rows.append((entry,"blank"))
        target_pos = next((i for i,(r,t) in enumerate(display_rows) if r == active and t in ("m_title","i_title")),0)
        if target_pos < offset: offset = target_pos
        if target_pos >= offset + max(1,yend-y0): offset=target_pos-max(1,yend-y0)+1
        offset=max(0,min(offset,max(0,len(display_rows)-(yend-y0))))
        for position in range(offset,min(len(display_rows),offset+max(0,yend-y0))):
            entry, subtype=display_rows[position]
            typ,mi,ii=entry
            m=MILESTONES[mi]
            y=y0+position-offset
            focus=(entry==active)
            fg=color(HEADER,True) if focus else color(NORMAL,True)
            if subtype=="m_title":
                sign="▼" if m.expanded else "▶"
                pct=round(100*counts(m.issues)["done"]/len(m.issues))
                right=f"{pct:3}%  ({len(m.issues)} issues)"
                safe_add(stdscr,y,2,f"{'>' if focus else ' '} {sign} #{m.number} {text_fit(m.title,max(8,w-len(right)-20))}",fg)
                safe_add(stdscr,y,max(2,w-len(right)-3),right,color(GREEN,True))
            elif subtype=="m_stats":
                ct=counts(m.issues)
                summary=f"{ct['done']} concluidas   {ct['running']} executando   {ct['pending']} pendentes   {ct['blocked']} bloqueadas"
                safe_add(stdscr,y,6,text_fit(f"{m.repo}  |  {summary}",w-10),color(DIM))
            elif subtype=="i_title":
                iss=m.issues[ii]
                status_attr={"done":GREEN,"running":BLUE,"pending":DIM,"blocked":RED}[iss.status]
                icon={"done":"✓","running":"●","pending":"○","blocked":"!"}[iss.status]
                stage_label=STAGES[iss.stage-1] if 1<=iss.stage<=8 else ("Finalizada" if iss.stage==9 else "Nao iniciada")
                safe_add(stdscr,y,6,f"{'>' if focus else ' '} {icon} #{iss.number} {text_fit(iss.title,max(12,w-40))}",fg if focus else color(status_attr,True))
                safe_add(stdscr,y,max(10,w-25),text_fit(f"{STATUS[iss.status]} / {stage_label}",22),color(status_attr))
            elif subtype=="i_stages":
                x=10
                iss=m.issues[ii]
                for cell,attr in stage_bar(w,iss):
                    if x+len(cell)>=w-2: break
                    safe_add(stdscr,y,x,cell,attr)
                    x+=len(cell)+1
            elif subtype=="d_info":
                iss=m.issues[ii]
                safe_add(stdscr,y,10,f"Agente: {iss.agent or '-'}   Tempo no step: {iss.elapsed or '-'}   Status: {STATUS[iss.status]}",color(YELLOW))
            elif subtype=="d_help":
                safe_add(stdscr,y,10,"Detalhes de demonstracao; nenhuma conexao real com OpenCode/GitHub.",color(DIM))
        if h>=4:
            safe_add(stdscr,h-3,2,"─"*max(0,w-4),color(DIM))
            safe_add(stdscr,h-2,2,"↑↓ / j k navegar   Enter expandir/detalhes   f filtro   a todos   c fechar   q sair",color(NORMAL))
        stdscr.refresh()
        key=stdscr.getch()
        if key in (ord('q'),27): break
        if key in (curses.KEY_DOWN,ord('j')): selected=min(selected+1,max(0,len(selectable)-1))
        elif key in (curses.KEY_UP,ord('k')): selected=max(0,selected-1)
        elif key in (10,13,curses.KEY_ENTER,ord(' ')) and active:
            kind,mi,ii=active
            if kind=="milestone": MILESTONES[mi].expanded=not MILESTONES[mi].expanded
            else: details=None if details==(mi,ii) else (mi,ii)
        elif key==ord('a'):
            for m in MILESTONES: m.expanded=True
        elif key==ord('c'):
            for m in MILESTONES: m.expanded=False
            details=None
        elif key==ord('f'):
            status_filter=filters[(filters.index(status_filter)+1)%len(filters)]
            selected=0; offset=0; details=None
        elif key==curses.KEY_RESIZE: offset=0

def main():
    try: curses.wrapper(render)
    except KeyboardInterrupt: pass

if __name__ == "__main__": main()
