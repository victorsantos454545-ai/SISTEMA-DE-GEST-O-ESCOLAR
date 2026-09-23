"""Formularios de autenticacao."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import re


class LoginForm(FlaskForm):
    """Formulario de login."""
    login = StringField('Usuario ou E-mail', validators=[
        DataRequired(message='Informe seu usuario ou e-mail.')
    ], render_kw={'placeholder': 'Usuario ou e-mail', 'autofocus': True})
    password = PasswordField('Senha', validators=[
        DataRequired(message='Informe sua senha.')
    ], render_kw={'placeholder': 'Senha'})
    submit = SubmitField('Entrar')


def validate_password_strength(form, field):
    """Valida forca da senha: minimo 10 caracteres, letras e numeros."""
    password = field.data
    if len(password) < 10:
        raise ValidationError('A senha deve ter no minimo 10 caracteres.')
    if not re.search(r'[a-zA-Z]', password):
        raise ValidationError('A senha deve conter pelo menos uma letra.')
    if not re.search(r'[0-9]', password):
        raise ValidationError('A senha deve conter pelo menos um numero.')


class ChangePasswordForm(FlaskForm):
    """Formulario de alteracao de senha."""
    current_password = PasswordField('Senha Atual', validators=[
        DataRequired(message='Informe a senha atual.')
    ])
    new_password = PasswordField('Nova Senha', validators=[
        DataRequired(message='Informe a nova senha.'),
        validate_password_strength
    ])
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[
        DataRequired(message='Confirme a nova senha.'),
        EqualTo('new_password', message='As senhas nao coincidem.')
    ])
    submit = SubmitField('Alterar Senha')


class ForgotPasswordForm(FlaskForm):
    """Formulario de recuperacao de senha."""
    email = StringField('E-mail', validators=[
        DataRequired(message='Informe seu e-mail.'),
        Email(message='E-mail invalido.')
    ], render_kw={'placeholder': 'seu.email@escola.com'})
    submit = SubmitField('Enviar')


class ResetPasswordForm(FlaskForm):
    """Formulario de redefinicao de senha."""
    new_password = PasswordField('Nova Senha', validators=[
        DataRequired(message='Informe a nova senha.'),
        validate_password_strength
    ])
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[
        DataRequired(message='Confirme a nova senha.'),
        EqualTo('new_password', message='As senhas nao coincidem.')
    ])
    submit = SubmitField('Redefinir Senha')
