from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    """Decorador que verifica se o usuario possui uma das roles especificadas.

    Uso:
        @role_required('admin', 'secretaria')
        def minha_rota():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not hasattr(current_user, 'role') or current_user.role.name not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorador que exige que o usuario seja administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not hasattr(current_user, 'role') or current_user.role.name != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission_name):
    """Decorador que verifica se o usuario possui a permissao especificada.

    Uso:
        @permission_required('students.view')
        def listar_alunos():
            ...

    Admin possui todas as permissoes automaticamente.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_permission(permission_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
