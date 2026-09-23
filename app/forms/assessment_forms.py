from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date

class AssessmentForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=200)])
    assessment_type = SelectField('Tipo', choices=[
        ('prova', 'Prova'),
        ('trabalho', 'Trabalho'),
        ('seminario', 'Seminário'),
        ('projeto', 'Projeto'),
        ('atividade', 'Atividade'),
        ('recuperacao', 'Recuperação'),
        ('outro', 'Outro')
    ], validators=[DataRequired()])
    
    school_class_id = SelectField('Turma', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Disciplina', coerce=int, validators=[DataRequired()])
    teacher_id = SelectField('Professor', coerce=int, validators=[DataRequired()])
    period_id = SelectField('Período', coerce=int, validators=[DataRequired()])
    
    date = DateField('Data da Avaliação', default=date.today, validators=[DataRequired()])
    max_value = FloatField('Valor Máximo', default=10.0, validators=[DataRequired(), NumberRange(min=0.1)])
    weight = FloatField('Peso', default=1.0, validators=[DataRequired(), NumberRange(min=0.1)])
    
    description = TextAreaField('Descrição (Opcional)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Salvar Avaliação')
