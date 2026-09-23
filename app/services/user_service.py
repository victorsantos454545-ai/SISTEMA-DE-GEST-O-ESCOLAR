"""Servico de gerenciamento de usuarios."""
from flask import request
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.models.audit_log import AuditLog


def create_user(username, email, password, role_id, active=True):
    """Cria um novo usuario.

    Retorna (user, error_message).
    """
    if User.query.filter_by(username=username).first():
        return None, 'Nome de usuario ja existe.'

    if User.query.filter_by(email=email).first():
        return None, 'E-mail ja cadastrado.'

    role = db.session.get(Role, role_id)
    if role is None:
        return None, 'Papel invalido.'

    user = User(
        username=username,
        email=email,
        role_id=role_id,
        active=active,
        must_change_password=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    AuditLog.log(
        action='USER_CREATED',
        user_id=None,  # sera preenchido pelo contexto
        entity='User',
        entity_id=user.id,
        description=f'Usuario criado: {user.username} (role: {role.name})',
        ip_address=request.remote_addr if request else None,
        user_agent=str(request.user_agent)[:500] if request else None
    )
    return user, None


def update_user(user, username=None, email=None, role_id=None, active=None):
    """Atualiza dados de um usuario.

    Retorna (success, error_message).
    """
    changes = []

    if username and username != user.username:
        if User.query.filter(User.username == username, User.id != user.id).first():
            return False, 'Nome de usuario ja existe.'
        changes.append(f'username: {user.username} -> {username}')
        user.username = username

    if email and email != user.email:
        if User.query.filter(User.email == email, User.id != user.id).first():
            return False, 'E-mail ja cadastrado.'
        changes.append(f'email: {user.email} -> {email}')
        user.email = email

    if role_id and role_id != user.role_id:
        role = db.session.get(Role, role_id)
        if role is None:
            return False, 'Papel invalido.'
        old_role = user.role.name
        changes.append(f'role: {old_role} -> {role.name}')
        user.role_id = role_id

    if active is not None and active != user.active:
        changes.append(f'active: {user.active} -> {active}')
        user.active = active

    if changes:
        db.session.commit()
        AuditLog.log(
            action='USER_UPDATED',
            entity='User',
            entity_id=user.id,
            description=f'Usuario atualizado: {user.username} | ' + ', '.join(changes),
            ip_address=request.remote_addr if request else None,
            user_agent=str(request.user_agent)[:500] if request else None
        )

    return True, None


def toggle_user_active(user, active):
    """Ativa ou desativa um usuario."""
    user.active = active
    if not active:
        user.failed_login_attempts = 0
        user.locked_until = None
    db.session.commit()

    action = 'USER_ACTIVATED' if active else 'USER_DEACTIVATED'
    AuditLog.log(
        action=action,
        entity='User',
        entity_id=user.id,
        description=f'Usuario {"ativado" if active else "desativado"}: {user.username}',
        ip_address=request.remote_addr if request else None,
        user_agent=str(request.user_agent)[:500] if request else None
    )


def admin_reset_password(user, new_password):
    """Admin redefine a senha de um usuario."""
    user.set_password(new_password)
    user.must_change_password = True
    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()

    AuditLog.log(
        action='PASSWORD_RESET_BY_ADMIN',
        entity='User',
        entity_id=user.id,
        description=f'Senha redefinida pelo admin: {user.username}',
        ip_address=request.remote_addr if request else None,
        user_agent=str(request.user_agent)[:500] if request else None
    )


def get_users_paginated(page=1, per_page=20, search=None, role_id=None, status=None):
    """Retorna usuarios paginados com filtros."""
    query = User.query.join(Role)

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (User.username.ilike(search_term)) |
            (User.email.ilike(search_term))
        )

    if role_id:
        query = query.filter(User.role_id == role_id)

    if status == 'active':
        query = query.filter(User.active == True)
    elif status == 'inactive':
        query = query.filter(User.active == False)

    return query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
