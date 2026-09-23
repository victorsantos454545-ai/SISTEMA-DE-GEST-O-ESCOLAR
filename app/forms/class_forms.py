from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange, ValidationError, Length
from app.models import SchoolClass, SchoolYear

class ClassForm(FlaskForm):
    name = StringField('Nome da Turma', validators=[DataRequired(), Length(max=100)])
    school_year_id = SelectField('Ano Letivo', coerce=int, validators=[DataRequired()])
    grade = StringField('Série/Ano', validators=[Optional()])
    shift = SelectField('Turno', choices=[(s, s) for s in SchoolClass.SHIFTS], validators=[DataRequired()])
    room = StringField('Sala', validators=[Optional()])
    capacity = IntegerField('Capacidade', validators=[Optional(), NumberRange(min=1)])
    status = SelectField('Status', choices=[(s, s.capitalize()) for s in SchoolClass.STATUSES], validators=[DataRequired()])
    submit = SubmitField('Salvar')

    def __init__(self, *args, **kwargs):
        self.class_id = kwargs.pop('class_id', None)
        super().__init__(*args, **kwargs)
        # Populando os choices de anos letivos dinamicamente
        self.school_year_id.choices = [(sy.id, str(sy.year) + (' (Ativo)' if sy.active else '')) for sy in SchoolYear.query.order_by(SchoolYear.year.desc()).all()]

    def validate_name(self, field):
        # A combinação Nome + Ano Letivo + Turno geralmente é única, ou só nome e ano letivo
        # Para ser seguro, vamos apenas avisar duplicidade exata no mesmo ano letivo
        cls = SchoolClass.query.filter_by(name=field.data, school_year_id=self.school_year_id.data).first()
        if cls:
            if hasattr(self, 'class_id') and str(self.class_id) == str(cls.id):
                return
            raise ValidationError('Já existe uma turma com este nome neste ano letivo.')

class LinkTeacherForm(FlaskForm):
    teacher_id = SelectField('Professor', coerce=int, validators=[DataRequired()])
    is_coordinator = BooleanField('Professor Coordenador')
    submit = SubmitField('Vincular')

class LinkSubjectForm(FlaskForm):
    subject_id = SelectField('Disciplina', coerce=int, validators=[DataRequired()])
    workload = IntegerField('Carga Horária (opcional)', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Vincular')
