"""Servico de autenticacao e controle de acesso."""
from datetime import datetime, timezone
from flask import request
from flask_login import login_user, logout_user
from app.extensions import db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.password_reset import PasswordResetToken


def authenticate_user(login_field, password):
    """Autentica usuario por username ou email.

    Retorna (user, error_message) - user e None se falhar.
    NAO revela se o usuario existe ou nao.
    """
    user = User.query.filter(
        (User.username == login_field) | (User.email == login_field)
    ).first()

    if user is None:
        return None, 'Credenciais invalidas.'

    if user.is_locked:
        return None, 'Conta bloqueada temporariamente. Tente novamente em alguns minutos.'

    if not user.active:
        return None, 'Credenciais invalidas.'

    if not user.check_password(password):
        user.record_failed_login()
        AuditLog.log(
            action='LOGIN_FAILED',
            user_id=user.id,
            entity='User',
            entity_id=user.id,
            description=f'Tentativa de login falha para {user.username}',
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent)[:500]
        )
        return None, 'Credenciais invalidas.'

    return user, None


def login_authenticated_user(user):
    """Registra login do usuario autenticado."""
    user.record_successful_login()
    login_user(user)
    AuditLog.log(
        action='LOGIN',
        user_id=user.id,
        entity='User',
        entity_id=user.id,
        description=f'Login realizado: {user.username}',
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:500]
    )


def logout_current_user(user):
    """Realiza logout e registra auditoria."""
    AuditLog.log(
        action='LOGOUT',
        user_id=user.id,
        entity='User',
        entity_id=user.id,
        description=f'Logout realizado: {user.username}',
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:500]
    )
    logout_user()


def change_password(user, current_password, new_password):
    """Altera a senha do usuario.

    Retorna (success, error_message).
    """
    if not user.check_password(current_password):
        return False, 'Senha atual incorreta.'

    user.set_password(new_password)
    user.must_change_password = False
    db.session.commit()

    AuditLog.log(
        action='PASSWORD_CHANGED',
        user_id=user.id,
        entity='User',
        entity_id=user.id,
        description=f'Senha alterada: {user.username}',
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:500]
    )
    return True, None


def request_password_reset(email):
    """Solicita recuperacao de senha. Retorna token se usuario existe.

    NUNCA revela se o email existe ou nao ao usuario final.
    """
    user = User.query.filter_by(email=email, active=True).first()
    if user is None:
        return None  # Nao revela se o email existe

    token = PasswordResetToken.create_for_user(user)

    AuditLog.log(
        action='PASSWORD_RESET_REQUESTED',
        user_id=user.id,
        entity='User',
        entity_id=user.id,
        description=f'Recuperacao de senha solicitada: {user.username}',
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:500]
    )
    return token


def reset_password_with_token(token_str, new_password):
    """Redefine a senha usando token de recuperacao.

    Retorna (success, error_message).
    """
    reset = PasswordResetToken.verify_token(token_str)
    if reset is None:
        return False, 'Token invalido ou expirado.'

    user = User.query.get(reset.user_id)
    if user is None or not user.active:
        return False, 'Token invalido ou expirado.'

    user.set_password(new_password)
    user.must_change_password = False
    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()

    reset.invalidate()

    AuditLog.log(
        action='PASSWORD_RESET',
        user_id=user.id,
        entity='User',
        entity_id=user.id,
        description=f'Senha redefinida via token: {user.username}',
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:500]
    )
    return True, None


def get_dashboard_redirect(user):
    """Retorna o endpoint de dashboard baseado na role do usuario."""
    role_dashboards = {
        'admin': 'main.dashboard',
        'professor': 'main.dashboard',
        'secretaria': 'main.dashboard',
        'responsavel': 'main.dashboard',
        'aluno': 'main.dashboard',
    }
    return role_dashboards.get(user.role.name, 'main.dashboard')
