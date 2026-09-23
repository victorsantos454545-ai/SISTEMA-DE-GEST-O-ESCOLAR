from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, TextAreaField, SubmitField, StringField, HiddenField
from wtforms.validators import DataRequired, Optional
from app.models import Enrollment, SchoolYear, SchoolClass, Student
from datetime import date

class EnrollmentForm(FlaskForm):
    student_id = SelectField('Aluno', coerce=int, validators=[DataRequired()])
    school_year_id = SelectField('Ano Letivo', coerce=int, validators=[DataRequired()])
    school_class_id = SelectField('Turma', coerce=int, validators=[DataRequired()])
    enrollment_date = DateField('Data da Matrícula', default=date.today, validators=[DataRequired()])
    status = SelectField('Situação', choices=[(s, s.capitalize()) for s in Enrollment.STATUSES], validators=[DataRequired()])
    notes = TextAreaField('Observações', validators=[Optional()])
    submit = SubmitField('Salvar')

class EditEnrollmentForm(FlaskForm):
    # O aluno, ano letivo e turma não são alteráveis diretamente por este form (turma tem form próprio de transfer).
    enrollment_date = DateField('Data da Matrícula', validators=[DataRequired()])
    status = SelectField('Situação', choices=[(s, s.capitalize()) for s in Enrollment.STATUSES], validators=[DataRequired()])
    notes = TextAreaField('Observações', validators=[Optional()])
    submit = SubmitField('Salvar')

class TransferEnrollmentForm(FlaskForm):
    new_class_id = SelectField('Nova Turma', coerce=int, validators=[DataRequired()])
    transfer_date = DateField('Data da Transferência', default=date.today, validators=[DataRequired()])
    reason = TextAreaField('Motivo', validators=[DataRequired()])
    submit = SubmitField('Transferir')

class CancelEnrollmentForm(FlaskForm):
    cancel_date = DateField('Data de Cancelamento', default=date.today, validators=[DataRequired()])
    reason = TextAreaField('Motivo', validators=[DataRequired()])
    submit = SubmitField('Cancelar Matrícula')

class CompleteEnrollmentForm(FlaskForm):
    complete_date = DateField('Data de Conclusão', default=date.today, validators=[DataRequired()])
    notes = TextAreaField('Observações', validators=[Optional()])
    submit = SubmitField('Concluir Matrícula')

class RenewEnrollmentForm(FlaskForm):
    new_year_id = SelectField('Novo Ano Letivo', coerce=int, validators=[DataRequired()])
    new_class_id = SelectField('Nova Turma', coerce=int, validators=[DataRequired()])
    renew_date = DateField('Data da Renovação', default=date.today, validators=[DataRequired()])
    status = SelectField('Situação Inicial', choices=[('ativa', 'Ativa'), ('pendente', 'Pendente')], default='ativa', validators=[DataRequired()])
    notes = TextAreaField('Observações', validators=[Optional()])
    submit = SubmitField('Renovar Matrícula')
