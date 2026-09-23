"""Formularios de gerenciamento de usuarios."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from app.forms.auth_forms import validate_password_strength


class UserCreateForm(FlaskForm):
    """Formulario de criacao de usuario."""
    username = StringField('Nome de Usuario', validators=[
        DataRequired(message='Nome de usuario obrigatorio.'),
        Length(min=3, max=80, message='Nome deve ter entre 3 e 80 caracteres.')
    ])
    email = StringField('E-mail', validators=[
        DataRequired(message='E-mail obrigatorio.'),
        Email(message='E-mail invalido.')
    ])
    role_id = SelectField('Papel', coerce=int, validators=[
        DataRequired(message='Selecione um papel.')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='Senha obrigatoria.'),
        validate_password_strength
    ])
    confirm_password = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Confirme a senha.'),
        EqualTo('password', message='As senhas nao coincidem.')
    ])
    active = BooleanField('Ativo', default=True)
    submit = SubmitField('Criar Usuario')


class UserEditForm(FlaskForm):
    """Formulario de edicao de usuario."""
    username = StringField('Nome de Usuario', validators=[
        DataRequired(message='Nome de usuario obrigatorio.'),
        Length(min=3, max=80, message='Nome deve ter entre 3 e 80 caracteres.')
    ])
    email = StringField('E-mail', validators=[
        DataRequired(message='E-mail obrigatorio.'),
        Email(message='E-mail invalido.')
    ])
    role_id = SelectField('Papel', coerce=int, validators=[
        DataRequired(message='Selecione um papel.')
    ])
    active = BooleanField('Ativo')
    submit = SubmitField('Salvar')


class AdminResetPasswordForm(FlaskForm):
    """Formulario para admin redefinir senha de usuario."""
    new_password = PasswordField('Nova Senha', validators=[
        DataRequired(message='Informe a nova senha.'),
        validate_password_strength
    ])
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[
        DataRequired(message='Confirme a nova senha.'),
        EqualTo('new_password', message='As senhas nao coincidem.')
    ])
    submit = SubmitField('Redefinir Senha')
