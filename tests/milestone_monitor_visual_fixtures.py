"""Fixtures determinísticas de apresentação; nenhum dado/cache do usuário."""
import copy

from milestone_monitor_fixtures import ISSUE, NOW, DEFAULTS, STARTED, snapshots, record, event
from milestone_monitor.projection import issue_view


def visual_model(count=4):
    template = issue_view(ISSUE, snapshots(record(event("stage_started"))), {}, {}, NOW, DEFAULTS, STARTED)
    repositories = ("fixture/loja", "fixture/mobile", "fixture/operacional")
    titles = ("Configuração inicial da loja", "Rancho Club — Backend", "Rancho Club — Mobile", "Retirada de pedidos")
    groups = []
    for index in range(count):
        repo = repositories[index % 3]
        issues = []
        for offset, (group, label) in enumerate((("done", "concluída"), ("running", "executando"), ("running", "executando"),
                                                ("pending", "pendente / sem registro"), ("blocked", "aguardando decisão"))):
            issue = copy.deepcopy(template)
            issue.update(repository=repo, number=100+index*5+offset, title=("Configurações regionais do Brasil", "Métodos de pagamento",
                         "Validação de configurações no deploy", "Métodos de entrega", "Smoke tests da loja")[offset],
                         url=f"https://github.com/{repo}/issues/{100+index*5+offset}", group=group, label=label)
            issue["summary"]["recorded_work_seconds"] = 120 if offset == 0 else 0
            issue["summary"]["cycle_elapsed_seconds"] = 600
            issue["workers"] = []
            if offset == 0:
                # Fechamento não implica sucesso das etapas sem registro.
                issue["stages"] = {"explore": "completed", "apply": "completed"}
                issue["summary"]["current_stage"] = None
            elif group != "running":
                issue["stages"] = {}
                issue["summary"] = None
            issues.append(issue)
        groups.append({"repository": repo, "number": index+1, "title": titles[index % 4], "issues": issues,
                       "totals": {"done": 1, "running": 2, "pending": 1, "blocked": 1}, "percent": 20})
    return {"milestones": groups, "health": [{"fresh": True, "fetched_at": "2026-01-01T12:00:00Z"}]}


def collapsed_model():
    """Lista longa como a captura operacional, mas sem dados reais."""
    value = visual_model(40)
    for index, group in enumerate(value["milestones"]):
        group["title"] = ("Pagamentos por Wallet e acesso de convidados — configuração regional da loja " + str(index+1))
        if index % 7:
            for issue in group["issues"]:
                issue.update(group="pending", label="pendente / sem registro", summary=None, stages={})
            group.update(totals={"done": 0, "running": 0, "pending": len(group["issues"]), "blocked": 0}, percent=0)
    return value
