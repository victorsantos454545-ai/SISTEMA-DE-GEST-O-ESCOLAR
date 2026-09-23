from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Optional

class AnnouncementForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(message="O título é obrigatório.")])
    content = TextAreaField('Conteúdo', validators=[DataRequired(message="O conteúdo é obrigatório.")])
    priority = SelectField('Prioridade', choices=[
        ('normal', 'Normal'),
        ('important', 'Importante'),
        ('urgent', 'Urgente')
    ], default='normal')
    status = SelectField('Status', choices=[
        ('rascunho', 'Rascunho'),
        ('agendado', 'Agendado'),
        ('publicado', 'Publicado')
    ], default='rascunho')
    
    target_audiences = SelectMultipleField('Público(s)', choices=[
        ('todos', 'Todos'),
        ('admin', 'Administradores'),
        ('secretaria', 'Secretaria'),
        ('professor', 'Professores'),
        ('aluno', 'Alunos'),
        ('responsavel', 'Responsáveis'),
        ('turma', 'Turma Específica')
    ], validators=[DataRequired(message="Selecione pelo menos um público-alvo.")])
    
    target_class_id = SelectField('Turma (se selecionada a opção acima)', choices=[], coerce=int, validators=[Optional()])
    
    published_at = DateTimeLocalField('Data de Publicação', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    expires_at = DateTimeLocalField('Data de Expiração', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    
    submit = SubmitField('Salvar')
