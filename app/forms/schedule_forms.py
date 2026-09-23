from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TimeField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.models.schedule import Schedule

class ScheduleForm(FlaskForm):
    day_of_week = SelectField('Dia da Semana', choices=[(d, d) for d in Schedule.DAYS], validators=[DataRequired()])
    start_time = TimeField('Horário de Início', validators=[DataRequired()])
    end_time = TimeField('Horário de Término', validators=[DataRequired()])
    
    subject_id = SelectField('Disciplina', coerce=int, validators=[DataRequired()])
    teacher_id = SelectField('Professor', coerce=int, validators=[DataRequired()])
    room = StringField('Sala', validators=[Optional()])
    
    submit = SubmitField('Salvar Horário')
