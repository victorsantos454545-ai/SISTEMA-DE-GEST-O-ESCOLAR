"""Rotas de autenticacao: login, logout, alteracao e recuperacao de senha."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from urllib.parse import urlparse
from app.forms.auth_forms import (
    LoginForm, ChangePasswordForm, ForgotPasswordForm, ResetPasswordForm
)
from app.services.auth_service import (
    authenticate_user, login_authenticated_user, logout_current_user,
    change_password, request_password_reset, reset_password_with_token,
    get_dashboard_redirect
)

auth_bp = Blueprint('auth', __name__)


def _is_safe_url(target):
    """Verifica se a URL de destino e segura (previne open redirect)."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('', 'http', 'https') and ref_url.netloc == test_url.netloc


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Pagina de login."""
    if current_user.is_authenticated:
        return redirect(url_for(get_dashboard_redirect(current_user)))

    form = LoginForm()
    if form.validate_on_submit():
        user, error = authenticate_user(form.login.data, form.password.data)
        if user is None:
            flash(error, 'danger')
            return render_template('auth/login.html', form=form)

        login_authenticated_user(user)
        flash('Login realizado com sucesso.', 'success')

        next_page = request.args.get('next')
        if next_page and _is_safe_url(next_page):
            return redirect(next_page)

        return redirect(url_for(get_dashboard_redirect(user)))

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do sistema."""
    logout_current_user(current_user)
    flash('Voce saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def change_password_view():
    """Alteracao de senha do usuario autenticado."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        success, error = change_password(
            current_user, form.current_password.data, form.new_password.data
        )
        if success:
            flash('Senha alterada com sucesso.', 'success')
            return redirect(url_for('main.dashboard'))
        flash(error, 'danger')

    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Solicita recuperacao de senha."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        token = request_password_reset(form.email.data)

        # Em desenvolvimento, mostra o link de reset no console
        if token and current_app.debug:
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            current_app.logger.info(f'\n*** LINK DE RECUPERACAO (DEV) ***\n{reset_url}\n')
            flash(f'[DEV] Link de recuperacao: {reset_url}', 'warning')
        else:
            # Mensagem generica que NAO revela se o email existe
            flash(
                'Se o endereco estiver cadastrado, enviaremos as instrucoes para recuperacao.',
                'info'
            )

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Redefine a senha usando token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        success, error = reset_password_with_token(token, form.new_password.data)
        if success:
            flash('Senha redefinida com sucesso. Faca login com a nova senha.', 'success')
            return redirect(url_for('auth.login'))
        flash(error, 'danger')

    return render_template('auth/reset_password.html', form=form, token=token)
