"""Formulários de Alunos."""
import re
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models.student import Student

def validate_cpf(form, field):
    """Validação básica de formato de CPF."""
    if not field.data:
        return
    
    # Remove pontuação
    cpf = re.sub(r'[^0-9]', '', field.data)
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos.')
        
    # Validar CPF repetidos (ex: 111.111.111-11)
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido.')
        
    # Evitar duplicidade
    existing = Student.query.filter_by(cpf=cpf).first()
    # No caso de update, precisamos ignorar o próprio aluno (checamos na rota/serviço)
    if existing and hasattr(form, 'student_id') and str(existing.id) != str(form.student_id):
        raise ValidationError('Este CPF já está cadastrado para outro aluno.')

class StudentForm(FlaskForm):
    """Formulário para Cadastro/Edição de Aluno."""
    # Dados Pessoais
    full_name = StringField('Nome Completo *', validators=[DataRequired(), Length(max=200)])
    social_name = StringField('Nome Social', validators=[Optional(), Length(max=200)])
    birth_date = DateField('Data de Nascimento *', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[Optional(), validate_cpf])
    rg = StringField('RG', validators=[Optional(), Length(max=20)])
    gender = SelectField('Gênero', choices=[
        ('', 'Não informar'), 
        ('M', 'Masculino'), 
        ('F', 'Feminino'), 
        ('O', 'Outro')
    ], default='')
    
    # Contato
    phone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=120)])
    
    # Endereço
    zip_code = StringField('CEP', validators=[Optional(), Length(max=9)])
    address = StringField('Logradouro', validators=[Optional(), Length(max=200)])
    number = StringField('Número', validators=[Optional(), Length(max=20)])
    complement = StringField('Complemento', validators=[Optional(), Length(max=100)])
    neighborhood = StringField('Bairro', validators=[Optional(), Length(max=100)])
    city = StringField('Cidade', validators=[Optional(), Length(max=100)])
    state = StringField('Estado', validators=[Optional(), Length(max=2)])
    
    # Institucional
    status = SelectField('Situação *', choices=[
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('transferido', 'Transferido'),
        ('concluido', 'Concluído')
    ], default='ativo', validators=[DataRequired()])
    notes = TextAreaField('Observações', validators=[Optional()])
    
    submit = SubmitField('Salvar')
    
    def __init__(self, *args, **kwargs):
        self.student_id = kwargs.pop('student_id', None)
        super().__init__(*args, **kwargs)
