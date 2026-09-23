from app.extensions import db
from app.models.base import TimestampMixin


class Role(TimestampMixin, db.Model):
    """Perfis/funcoes do sistema (Admin, Professor, Secretaria, etc.).

    Cada Role pode possuir varias Permissions via tabela role_permissions.
    A verificacao de permissao e feita em User.has_permission().
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    # Relacionamentos
    users = db.relationship('User', back_populates='role', lazy='dynamic')
    permissions = db.relationship(
        'Permission', secondary='role_permissions',
        back_populates='roles', lazy='select'
    )

    def __repr__(self):
        return f'<Role {self.name}>'
