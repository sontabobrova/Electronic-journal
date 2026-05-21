from contextvars import ContextVar


request_id_var: ContextVar[str] = ContextVar("audit_request_id", default="")
