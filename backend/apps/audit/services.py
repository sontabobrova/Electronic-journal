import logging
from typing import Any

from django.http import HttpRequest

from .context import request_id_var
from .models import AuditLog


logger = logging.getLogger("apps.audit")


def get_client_ip(request: HttpRequest | None) -> str | None:
    if request is None:
        return None
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_audit_event(
    *,
    action: str,
    actor=None,
    request: HttpRequest | None = None,
    obj: Any = None,
    object_type: str = "",
    object_id: str = "",
    object_repr: str = "",
    metadata: dict | None = None,
) -> AuditLog:
    if obj is not None:
        object_type = object_type or obj.__class__.__name__
        object_id = object_id or str(getattr(obj, "pk", ""))
        object_repr = object_repr or str(obj)[:255]

    audit_log = AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        object_type=object_type,
        object_id=object_id,
        object_repr=object_repr,
        ip_address=get_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "") if request else ""),
        request_id=getattr(request, "audit_request_id", request_id_var.get()),
        metadata=metadata or {},
    )
    logger.info("audit action=%s actor=%s object=%s:%s", action, getattr(actor, "id", None), object_type, object_id)
    return audit_log
