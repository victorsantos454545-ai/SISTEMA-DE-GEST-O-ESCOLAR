"""Rotas de gerenciamento de usuarios (administrativo)."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.utils.decorators import permission_required
from app.forms.user_forms import UserCreateForm, UserEditForm, AdminResetPasswordForm
from app.services.user_service import (
    create_user, update_user, toggle_user_active, admin_reset_password,
    get_users_paginated
)

users_bp = Blueprint('users', __name__, url_prefix='/usuarios')


def _populate_role_choices(form):
    """Preenche opcoes de role no formulario."""
    form.role_id.choices = [
        (r.id, r.description or r.name) for r in Role.query.order_by(Role.name).all()
    ]


@users_bp.route('/')
@login_required
@permission_required('users.view')
def index():
    """Lista de usuarios com busca, filtros e paginacao."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_id = request.args.get('role_id', None, type=int)
    status = request.args.get('status', '')

    pagination = get_users_paginated(
        page=page, per_page=20, search=search,
        role_id=role_id, status=status
    )
    roles = Role.query.order_by(Role.name).all()

    return render_template(
        'users/index.html',
        pagination=pagination,
        users=pagination.items,
        roles=roles,
        search=search,
        role_id=role_id,
        status=status
    )


@users_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permission_required('users.create')
def create():
    """Cria novo usuario."""
    form = UserCreateForm()
    _populate_role_choices(form)

    if form.validate_on_submit():
        user, error = create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role_id=form.role_id.data,
            active=form.active.data
        )
        if user:
            flash(f'Usuario {user.username} criado com sucesso.', 'success')
            return redirect(url_for('users.index'))
        flash(error, 'danger')

    return render_template('users/create.html', form=form)


@users_bp.route('/<int:user_id>')
@login_required
@permission_required('users.view')
def detail(user_id):
    """Detalhes do usuario."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    return render_template('users/detail.html', user=user)


@users_bp.route('/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
@permission_required('users.edit')
def edit(user_id):
    """Edita usuario."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)

    form = UserEditForm(obj=user)
    _populate_role_choices(form)

    if form.validate_on_submit():
        success, error = update_user(
            user,
            username=form.username.data,
            email=form.email.data,
            role_id=form.role_id.data,
            active=form.active.data
        )
        if success:
            flash(f'Usuario {user.username} atualizado com sucesso.', 'success')
            return redirect(url_for('users.detail', user_id=user.id))
        flash(error, 'danger')

    return render_template('users/edit.html', form=form, user=user)


@users_bp.route('/<int:user_id>/ativar', methods=['POST'])
@login_required
@permission_required('users.manage')
def activate(user_id):
    """Ativa usuario."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    toggle_user_active(user, True)
    flash(f'Usuario {user.username} ativado com sucesso.', 'success')
    return redirect(url_for('users.detail', user_id=user.id))


@users_bp.route('/<int:user_id>/desativar', methods=['POST'])
@login_required
@permission_required('users.manage')
def deactivate(user_id):
    """Desativa usuario."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        flash('Voce nao pode desativar a si mesmo.', 'danger')
        return redirect(url_for('users.detail', user_id=user.id))
    toggle_user_active(user, False)
    flash(f'Usuario {user.username} desativado com sucesso.', 'success')
    return redirect(url_for('users.detail', user_id=user.id))


@users_bp.route('/<int:user_id>/redefinir-senha', methods=['GET', 'POST'])
@login_required
@permission_required('users.manage')
def reset_password(user_id):
    """Admin redefine senha do usuario."""
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)

    form = AdminResetPasswordForm()
    if form.validate_on_submit():
        admin_reset_password(user, form.new_password.data)
        flash(f'Senha de {user.username} redefinida com sucesso.', 'success')
        return redirect(url_for('users.detail', user_id=user.id))

    return render_template('users/reset_password.html', form=form, user=user)


@users_bp.route('/meu-perfil')
@login_required
def profile():
    """Perfil do usuario autenticado."""
    return render_template('users/profile.html', user=current_user)
