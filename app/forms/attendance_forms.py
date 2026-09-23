from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Optional
from datetime import date

class AttendanceConfigForm(FlaskForm):
    school_class_id = SelectField('Turma', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Disciplina', coerce=int, validators=[DataRequired()])
    date = DateField('Data da Aula', default=date.today, validators=[DataRequired()])
    period = StringField('Aula/Período (ex: 1ª Aula)', validators=[Optional()])
    submit = SubmitField('Abrir Chamada')

class AttendanceBatchForm(FlaskForm):
    """CSRF apenas para o form em lote, campos dinâmicos renderizados no template"""
    submit = SubmitField('Salvar Chamada')

class AttendanceEditForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('justificado', 'Falta Justificada')
    ], validators=[DataRequired()])
    justification = TextAreaField('Justificativa (obrigatório se justificado)', validators=[Optional()])
    submit = SubmitField('Salvar Correção')
