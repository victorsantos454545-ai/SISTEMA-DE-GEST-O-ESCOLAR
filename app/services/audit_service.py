"""Servico de auditoria centralizado."""
from flask import request as flask_request
from flask_login import current_user
from app.models.audit_log import AuditLog


def log_action(action, entity=None, entity_id=None, description=None, details=None):
    """Registra uma acao de auditoria com contexto automatico."""
    user_id = current_user.id if current_user and current_user.is_authenticated else None
    ip = flask_request.remote_addr if flask_request else None
    ua = str(flask_request.user_agent)[:500] if flask_request else None

    return AuditLog.log(
        action=action,
        user_id=user_id,
        entity=entity,
        entity_id=entity_id,
        description=description,
        ip_address=ip,
        user_agent=ua,
        details=details
    )
