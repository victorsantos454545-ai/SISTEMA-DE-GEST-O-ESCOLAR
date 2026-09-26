from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateTimeLocalField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class CalendarEventForm(FlaskForm):
    title = StringField('Título do Evento', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descrição', validators=[Optional()])
    
    event_type = SelectField('Tipo de Evento', choices=[
        ('aula', 'Aula'),
        ('prova', 'Prova'),
        ('avaliacao', 'Avaliação'),
        ('reuniao', 'Reunião'),
        ('evento', 'Evento Escolar'),
        ('feriado', 'Feriado'),
        ('atividade', 'Atividade'),
        ('outro', 'Outro')
    ], validators=[DataRequired()])
    
    start_datetime = DateTimeLocalField('Início', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_datetime = DateTimeLocalField('Fim', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    all_day = BooleanField('Dia Inteiro')
    
    location = StringField('Local', validators=[Optional(), Length(max=200)])
    
    # Preenchidos no view
    school_year_id = SelectField('Ano Letivo (Opcional)', coerce=int, validators=[Optional()])
    school_class_id = SelectField('Turma (Opcional)', coerce=int, validators=[Optional()])
    subject_id = SelectField('Disciplina (Opcional)', coerce=int, validators=[Optional()])
    
    status = SelectField('Status', choices=[
        ('published', 'Publicado'),
        ('draft', 'Rascunho'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado')
    ], default='published', validators=[DataRequired()])
    
    submit = SubmitField('Salvar Evento')
