from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class ActivityForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descrição', validators=[Optional()])
    
    activity_type = SelectField('Tipo de Atividade', choices=[
        ('Exercício', 'Exercício'),
        ('Tarefa', 'Tarefa de Casa'),
        ('Trabalho', 'Trabalho'),
        ('Pesquisa', 'Pesquisa'),
        ('Projeto', 'Projeto'),
        ('Leitura', 'Leitura'),
        ('Seminário', 'Seminário'),
        ('Atividade em sala', 'Atividade em sala'),
        ('Outro', 'Outro')
    ], validators=[DataRequired()])
    
    school_class_id = SelectField('Turma', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Disciplina', coerce=int, validators=[DataRequired()])
    
    # professor pode ser preenchido dinamicamente se o usuario for admin
    teacher_id = SelectField('Professor Responsável', coerce=int, validators=[Optional()])
    
    published_at = DateTimeField('Data de Publicação', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    due_date = DateTimeField('Prazo de Entrega', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    
    status = SelectField('Status', choices=[
        ('rascunho', 'Rascunho (Não visível aos alunos)'),
        ('publicada', 'Publicada'),
        ('encerrada', 'Encerrada')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Salvar Atividade')

class ActivityCancelForm(FlaskForm):
    reason = TextAreaField('Motivo do Cancelamento', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Confirmar Cancelamento')
