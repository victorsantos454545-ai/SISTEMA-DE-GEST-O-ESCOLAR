"""Formulários de Responsáveis."""
import re
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models.guardian import Guardian

def validate_guardian_cpf(form, field):
    """Validação básica de formato de CPF para responsável."""
    if not field.data:
        return
    cpf = re.sub(r'[^0-9]', '', field.data)
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos.')
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido.')
    
    existing = Guardian.query.filter_by(cpf=cpf).first()
    if existing and hasattr(form, 'guardian_id') and str(existing.id) != str(form.guardian_id):
        raise ValidationError('Este CPF já está cadastrado para outro responsável.')

class GuardianForm(FlaskForm):
    """Formulário para Cadastro/Edição de Responsável."""
    # Dados Pessoais
    full_name = StringField('Nome Completo *', validators=[DataRequired(), Length(max=200)])
    cpf = StringField('CPF', validators=[Optional(), validate_guardian_cpf])
    
    # Contato
    phone = StringField('Telefone Principal *', validators=[DataRequired(), Length(max=20)])
    secondary_phone = StringField('Telefone Secundário', validators=[Optional(), Length(max=20)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=120)])
    
    # Endereço
    zip_code = StringField('CEP', validators=[Optional(), Length(max=9)])
    address = StringField('Logradouro', validators=[Optional(), Length(max=200)])
    number = StringField('Número', validators=[Optional(), Length(max=20)])
    complement = StringField('Complemento', validators=[Optional(), Length(max=100)])
    neighborhood = StringField('Bairro', validators=[Optional(), Length(max=100)])
    city = StringField('Cidade', validators=[Optional(), Length(max=100)])
    state = StringField('Estado', validators=[Optional(), Length(max=2)])
    
    submit = SubmitField('Salvar')
    
    def __init__(self, *args, **kwargs):
        self.guardian_id = kwargs.pop('guardian_id', None)
        super().__init__(*args, **kwargs)

class StudentGuardianForm(FlaskForm):
    """Formulário para vincular um Responsável a um Aluno."""
    guardian_id = SelectField('Selecione o Responsável *', coerce=int, validators=[DataRequired()])
    relationship = StringField('Parentesco/Relação *', validators=[DataRequired(), Length(max=50)], render_kw={'placeholder': 'Ex: Pai, Mãe, Avó, Tio'})
    is_primary = BooleanField('Responsável Principal')
    
    submit = SubmitField('Vincular')
