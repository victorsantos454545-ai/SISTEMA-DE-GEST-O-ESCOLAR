from app.extensions import db
from app.models.base import TimestampMixin


class SystemConfig(TimestampMixin, db.Model):
    """Configurações do sistema escolar.

    Armazena configurações chave-valor para a escola:
    média mínima, frequência mínima, sistema de recuperação, etc.
    Permite que a escola altere regras sem modificar o código.
    """
    __tablename__ = 'system_configs'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<SystemConfig {self.key}={self.value}>'
