from flask_wtf import FlaskForm
from wtforms import SubmitField

class GradeBatchForm(FlaskForm):
    """Apenas para proteger o envio do lote com CSRF."""
    submit = SubmitField('Salvar Notas')
