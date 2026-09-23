from app.extensions import db
from app.models.base import TimestampMixin


# Tabela associativa para Role <-> Permission (N:N)
role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)


class Permission(TimestampMixin, db.Model):
    """Permissoes granulares do sistema (RBAC).

    Cada permissao representa uma acao especifica em um modulo:
    - module: modulo do sistema (students, grades, users, etc.)
    - action: acao permitida (view, create, edit, delete, manage)
    - name: identificador unico no formato 'module.action'
    """
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    module = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

    # Relacionamentos
    roles = db.relationship(
        'Role', secondary=role_permissions,
        back_populates='permissions', lazy='dynamic'
    )

    def __repr__(self):
        return f'<Permission {self.name}>'
