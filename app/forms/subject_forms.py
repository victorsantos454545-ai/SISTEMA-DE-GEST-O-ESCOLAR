from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, ValidationError
from app.models import Subject

class SubjectForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    code = StringField('Código', validators=[Optional(), Length(max=20)])
    workload = IntegerField('Carga Horária', validators=[Optional(), NumberRange(min=0)])
    description = TextAreaField('Descrição', validators=[Optional()])
    status = SelectField('Status', choices=[(s, s.capitalize()) for s in Subject.STATUSES], validators=[DataRequired()])
    submit = SubmitField('Salvar')

    def __init__(self, *args, **kwargs):
        self.subject_id = kwargs.pop('subject_id', None)
        super().__init__(*args, **kwargs)

    def validate_code(self, field):
        if not field.data:
            return
        subject = Subject.query.filter_by(code=field.data).first()
        if subject:
            if hasattr(self, 'subject_id') and str(self.subject_id) == str(subject.id):
                return
            raise ValidationError('Este código já está em uso por outra disciplina.')
