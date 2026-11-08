"""Fronteiras compartilhadas de validação e apresentação."""
import json
import re
import subprocess
import unicodedata
from urllib.parse import urlsplit

from workflow_metrics import iso_time, parse_time, utc_now

SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,99}\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
ANSI = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\))")


class MonitorError(Exception):
    def __init__(self, category, retry_after=None):
        self.category = category
        self.retry_after = retry_after
        super().__init__(category)


def text(value, limit=500):
    if not isinstance(value, str):
        return ""
    value = ANSI.sub("", value)
    return "".join(c for c in value if not unicodedata.category(c).startswith("C"))[:limit]


def identifier(value):
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise MonitorError("identidade inválida")
    return value


def issue_identity(url):
    match = re.fullmatch(r"https://github.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)", url or "")
    if not match:
        raise MonitorError("URL de issue inválida")
    return match[1], int(match[2])


def server_url(value):
    if not isinstance(value, str):
        raise MonitorError("servidor inválido")
    parsed = urlsplit(value)
    if (parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment or any(c.isspace() for c in value)):
        raise MonitorError("servidor inválido")
    return value.rstrip("/")


def command(argv, timeout=10):
    """Não devolver stderr nem incorporar dados sensíveis em exceções."""
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError:
        raise MonitorError("fonte ausente") from None
    except subprocess.TimeoutExpired:
        raise MonitorError("timeout") from None
    except (OSError, UnicodeError):
        raise MonitorError("transporte") from None
    if result.returncode:
        raw = result.stderr + result.stdout
        category = "fonte indisponível"
        for code, label in [(401, "não autorizado"), (429, "rate limit"), (403, "acesso negado"), (404, "ausente")]:
            if re.search(rf"\b{code}\b", raw):
                category = label
                break
        if "not found" in raw.lower():
            category = "ausente"
        if "rate limit" in raw.lower():
            category = "rate limit"
        retry = re.search(r"retry-after:\s*(\d+)", raw, re.I)
        reset = re.search(r"x-ratelimit-reset:\s*(\d+)", raw, re.I)
        delay = int(retry[1]) if retry else max(0, int(reset[1]) - int(utc_now().timestamp())) if reset else None
        raise MonitorError(category, delay)
    if argv == ["opencode", "--version"]:
        match = re.fullmatch(r"opencode v([0-9]+\.[0-9]+\.[0-9]+)\s*", result.stdout)
        if not match:
            raise MonitorError("contrato OpenCode incompatível")
        return match[1]
    payload = result.stdout
    # gh --include exposes Retry-After/reset on failures. Strip only a real
    # HTTP header block on success; never persist headers or auth material.
    if payload.startswith("HTTP/"):
        parts = re.split(r"\r?\n\r?\n", payload, maxsplit=1)
        if len(parts) != 2:
            raise MonitorError("resposta inválida")
        payload = parts[1]
    try:
        return json.loads(payload)
    except (ValueError, TypeError):
        raise MonitorError("resposta inválida") from None


def fresh(value, now, ttl):
    at = parse_time(value)
    return at is not None and 0 <= (now - at).total_seconds() <= ttl
