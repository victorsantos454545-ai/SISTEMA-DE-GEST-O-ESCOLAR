from datetime import datetime, timezone
from app.extensions import db


class AuditLog(db.Model):
    """Log de auditoria para acoes importantes do sistema.

    Registra acoes como login, logout, criacao/edicao de usuarios,
    alteracao de senha, alteracao de permissoes, etc.
    NAO armazena senhas, tokens ou dados sensiveis.
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False, index=True)
    entity = db.Column(db.String(50))  # Entidade afetada: User, Student, etc.
    entity_id = db.Column(db.Integer)  # ID da entidade afetada
    description = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))  # IPv4 ou IPv6
    user_agent = db.Column(db.String(500))
    details = db.Column(db.Text)  # JSON com detalhes adicionais
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relacionamentos
    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))

    @classmethod
    def log(cls, action, user_id=None, entity=None, entity_id=None,
            description=None, ip_address=None, user_agent=None, details=None):
        """Cria um registro de auditoria."""
        entry = cls(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    def __repr__(self):
        return f'<AuditLog {self.action} user={self.user_id}>'
