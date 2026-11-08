"""Inventário GitHub completamente paginado em escopos explícitos."""
import re

from .common import MonitorError, command, text, parse_time
from .ingest import comments_snapshot


class GitHub:
    def __init__(self, call=command, timeout=10):
        self.call, self.timeout = call, timeout

    def get(self, path):
        return self.call(["gh", "api", "--method", "GET", "--include", path], timeout=self.timeout)

    def pages(self, path):
        separator = "&" if "?" in path else "?"
        page, result = 1, []
        while True:
            values = self.get(f"{path}{separator}per_page=100&page={page}")
            if not isinstance(values, list) or any(not isinstance(item, dict) for item in values):
                raise MonitorError("resposta inválida")
            result.extend(values)
            if len(values) < 100:
                return result
            page += 1

    def inventory(self, repo, milestones):
        groups, issues = [], {}
        for number in milestones:
            raw = self.get(f"repos/{repo}/milestones/{number}")
            if not isinstance(raw, dict) or raw.get("number") != number or not isinstance(raw.get("title"), str):
                raise MonitorError("resposta inválida")
            groups.append({"repository": repo, "number": number, "title": text(raw["title"])})
            for item in self.pages(f"repos/{repo}/issues?milestone={number}&state=all"):
                if "pull_request" in item:
                    continue
                n = item.get("number")
                if (type(n) is not int or n <= 0 or item.get("state") not in {"open", "closed"}
                        or not isinstance(item.get("milestone"), dict) or item["milestone"].get("number") != number
                        or item.get("html_url") != f"https://github.com/{repo}/issues/{n}"
                        or not isinstance(item.get("title"), str)):
                    raise MonitorError("resposta inválida")
                if n in issues and issues[n]["milestone"] != number:
                    # A movement during paging is not a coherent complete snapshot.
                    raise MonitorError("inventário em reconciliação")
                issues[n] = {"repository": repo, "number": n, "milestone": number, "title": text(item["title"]),
                             "state": item["state"], "url": item["html_url"]}
        return {"milestones": groups, "issues": list(issues.values())}

    def comments(self, repo, number):
        return comments_snapshot(self.pages(f"repos/{repo}/issues/{number}/comments"), repo, number)

    def pull_requests(self, repo, number):
        candidates = set()
        for item in self.pages(f"repos/{repo}/issues/{number}/timeline"):
            source = item.get("source", {}).get("issue", {}) if isinstance(item.get("source"), dict) else {}
            if not isinstance(source, dict) or "pull_request" not in source:
                continue
            url = source.get("html_url")
            if not isinstance(url, str):
                raise MonitorError("resposta inválida")
            match = re.fullmatch(rf"https://github.com/{re.escape(repo)}/pull/([1-9][0-9]*)", url)
            if match:
                candidates.add(int(match[1]))
        verified = []
        # GraphQL closure references, not a prose regex or mere cross-reference.
        owner, name = repo.split("/")
        for candidate in sorted(candidates):
            cursor, matches, facts = None, False, None
            while True:
                query = """query($owner:String!,$name:String!,$number:Int!,$cursor:String){repository(owner:$owner,name:$name){pullRequest(number:$number){
                    number url state mergedAt mergeCommit{oid} headRefOid
                    closingIssuesReferences(first:100,after:$cursor){nodes{number repository{nameWithOwner}} pageInfo{hasNextPage endCursor}}
                }}}"""
                argv = ["gh", "api", "graphql", "-f", f"query={query}", "-f", f"owner={owner}", "-f", f"name={name}", "-F", f"number={candidate}"]
                if cursor:
                    argv += ["-f", f"cursor={cursor}"]
                raw = self.call(argv, timeout=self.timeout)
                try:
                    if raw.get("errors"):
                        raise ValueError()
                    pr = raw["data"]["repository"]["pullRequest"]
                    connection = pr["closingIssuesReferences"]
                    for node in connection["nodes"]:
                        matches |= node["number"] == number and node["repository"]["nameWithOwner"].lower() == repo.lower()
                    if pr["url"] != f"https://github.com/{repo}/pull/{candidate}" or pr["state"] not in {"OPEN", "CLOSED", "MERGED"}:
                        raise ValueError()
                    facts = {"number": candidate, "url": pr["url"], "state": pr["state"], "merged_at": pr.get("mergedAt"),
                             "head": pr.get("headRefOid"), "merge_commit": (pr.get("mergeCommit") or {}).get("oid")}
                    if facts["merged_at"] is not None and (not isinstance(facts["merged_at"], str) or not parse_time(facts["merged_at"])):
                        raise ValueError()
                    for field in ("head", "merge_commit"):
                        if facts[field] is not None and not re.fullmatch(r"[a-fA-F0-9]{40,64}", facts[field]):
                            raise ValueError()
                    info = connection["pageInfo"]
                    if not info["hasNextPage"]:
                        break
                    if not isinstance(info["endCursor"], str) or info["endCursor"] == cursor:
                        raise ValueError()
                    cursor = info["endCursor"]
                except (KeyError, TypeError, ValueError, AttributeError):
                    raise MonitorError("resposta inválida") from None
            if matches:
                verified.append(facts)
        return {"candidates": verified, "ambiguous": len(verified) > 1}
