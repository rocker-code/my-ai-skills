"""Segunda projeção de metadados antes do cache; nunca confiar no IPC bruto."""
import json
from datetime import datetime, timezone

from .common import MonitorError, identifier, parse_time, server_url

MAX_BYTES = 16 * 1024
MAX_FACTS = 1000
TYPES = {"server.connected", "location.shutdown", "session.moved",
         "session.execution.started", "session.execution.succeeded", "session.execution.failed",
         "session.execution.interrupted", "permission.asked", "permission.replied",
         "form.created", "form.replied", "form.cancelled"}


def normalize(line, context, bindings, epoch):
    if len(line) > MAX_BYTES:
        raise MonitorError("envelope de observação excedido")
    try:
        event = json.loads(line)
        if (not isinstance(event, dict) or type(event.get("version")) is not int or event["version"] != 1
                or event.get("type") not in TYPES):
            raise ValueError()
        supplied = event.get("context")
        if supplied != context or set(supplied) != {"endpoint", "version", "pid"}:
            raise ValueError()
        if context["version"] != "2.2.5" or type(context["pid"]) is not int or context["pid"] <= 0:
            raise ValueError()
        if context["endpoint"] != "shared-discovery":
            server_url(context["endpoint"])
        native = event["created"]
        if type(native) is not int or native < 0:
            raise ValueError()
        at = datetime.fromtimestamp(native / 1000, timezone.utc)
        received = parse_time(event.get("received_at"))
        if not received or at > received:
            raise ValueError()
        event_id = identifier(event["event_id"])
        if not event_id.startswith("evt_"):
            raise ValueError()
        fact = {"version": 1, "type": event["type"], "event_id": event_id,
                "created": native, "received_at": received.isoformat(), "context": dict(context),
                "collector_epoch": epoch, "consumed": False}
        if event["type"] in {"server.connected", "location.shutdown"}:
            return fact
        session, revision = identifier(event["session_id"]), identifier(event["binding_revision"])
        matches = [(key, binding) for key, binding in bindings.items()
                   if binding.get("session_id") == session and binding.get("revision") == revision
                   and binding.get("context") == context and not binding.get("invalidated")]
        if len(matches) != 1:
            return None
        key, binding = matches[0]
        bound = parse_time(binding.get("bound_at"))
        if not bound or at < bound:
            return None
        fact.update(binding_key=key, session_id=session, binding_revision=revision)
        if event["type"].startswith("session.execution."):
            if type(event.get("sequence")) is not int or event["sequence"] < 0:
                raise ValueError()
            fact["sequence"] = event["sequence"]
        elif event["type"].startswith(("permission.", "form.")):
            request = identifier(event["request_id"])
            if not request.startswith("per" if event["type"].startswith("permission.") else "frm_"):
                raise ValueError()
            fact["request_id"] = request
            if event["type"] == "permission.replied":
                if event.get("resolution") not in {"answered", "rejected"}:
                    raise ValueError()
                fact["resolution"] = event["resolution"]
        return fact
    except (ValueError, KeyError, TypeError, OverflowError, OSError, AttributeError):
        raise MonitorError("envelope de observação inválido") from None
