from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError, EqualTo
from app.models.teacher import Teacher
from app.models.user import User
import re

def validate_cpf(form, field):
    cpf = re.sub(r'[^0-9]', '', field.data) if field.data else ''
    if not cpf:
        return
        
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos.')
        
    # Verifica se todos os digitos são iguais (ex: 111.111.111-11)
    if len(set(cpf)) == 1:
        raise ValidationError('CPF inválido.')
        
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(cpf[9]):
        raise ValidationError('CPF inválido.')
        
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(cpf[10]):
        raise ValidationError('CPF inválido.')

def check_duplicate_cpf(form, field):
    cpf = re.sub(r'[^0-9]', '', field.data) if field.data else ''
    if not cpf:
        return
        
    teacher = Teacher.query.filter_by(cpf=cpf).first()
    
    # Se encontrou um professor com este CPF e não é o professor sendo editado
    if teacher:
        if hasattr(form, 'teacher_id') and str(form.teacher_id) == str(teacher.id):
            return
        raise ValidationError('Já existe um professor cadastrado com este CPF.')

def check_duplicate_registration(form, field):
    registration = field.data
    if not registration:
        return
        
    teacher = Teacher.query.filter_by(registration=registration).first()
    
    if teacher:
        if hasattr(form, 'teacher_id') and str(form.teacher_id) == str(teacher.id):
            return
        raise ValidationError('Já existe um professor cadastrado com esta matrícula.')

def check_duplicate_username(form, field):
    username = field.data
    if not username:
        return
    user = User.query.filter_by(username=username).first()
    if user:
        if hasattr(form, 'teacher_id') and form.teacher_id:
            teacher = Teacher.query.get(form.teacher_id)
            if teacher and teacher.user_id == user.id:
                return
        raise ValidationError('Este nome de usuário já está em uso.')

class TeacherForm(FlaskForm):
    # Acesso ao Sistema (Login)
    username = StringField('Usuário de Acesso (Login)', validators=[Optional(), Length(min=3, max=80, message="Usuário deve ter entre 3 e 80 caracteres."), check_duplicate_username])
    password = PasswordField('Senha de Acesso', validators=[Optional(), Length(min=6, message="A senha deve ter no mínimo 6 caracteres.")])
    confirm_password = PasswordField('Confirmar Senha', validators=[EqualTo('password', message="As senhas não coincidem.")])

    # Dados pessoais
    full_name = StringField('Nome Completo', validators=[DataRequired(message="Campo obrigatório."), Length(max=200)])
    cpf = StringField('CPF', validators=[Optional(), validate_cpf, check_duplicate_cpf, Length(max=14)])
    birth_date = DateField('Data de Nascimento', validators=[Optional()])
    
    # Contato
    phone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    email = StringField('E-mail', validators=[Optional(), Email(message="E-mail inválido."), Length(max=120)])
    
    # Endereço
    zip_code = StringField('CEP', validators=[Optional(), Length(max=9)])
    state = StringField('Estado (UF)', validators=[Optional(), Length(max=2)])
    city = StringField('Cidade', validators=[Optional(), Length(max=100)])
    neighborhood = StringField('Bairro', validators=[Optional(), Length(max=100)])
    address = StringField('Rua/Logradouro', validators=[Optional(), Length(max=200)])
    number = StringField('Número', validators=[Optional(), Length(max=20)])
    complement = StringField('Complemento', validators=[Optional(), Length(max=100)])
    
    # Profissional
    registration = StringField('Matrícula Funcional', validators=[DataRequired(message="A matrícula é obrigatória."), check_duplicate_registration, Length(max=50)])
    education = StringField('Formação', validators=[Optional(), Length(max=200)])
    specialization = StringField('Especialização', validators=[Optional(), Length(max=200)])
    status = SelectField('Status', choices=[(s, s.capitalize()) for s in Teacher.STATUSES], validators=[DataRequired()])
    
    submit = SubmitField('Salvar')
    
    def __init__(self, *args, **kwargs):
        self.teacher_id = kwargs.pop('teacher_id', None)
        super().__init__(*args, **kwargs)

class LinkSubjectForm(FlaskForm):
    subject_id = SelectField('Disciplina', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Vincular')

class LinkClassForm(FlaskForm):
    class_id = SelectField('Turma', coerce=int, validators=[DataRequired()])
    is_coordinator = SelectField('É Coordenador?', choices=[('n', 'Não'), ('y', 'Sim')], validators=[DataRequired()])
    submit = SubmitField('Vincular')
