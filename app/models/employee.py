from app.extensions import db
from app.models.base import TimestampMixin


class Employee(TimestampMixin, db.Model):
    """Funcionários da instituição (exceto professores).

    O campo 'position' é texto livre, não enum rígido,
    permitindo que a escola defina cargos como:
    Secretário, Diretor, Coordenador, Auxiliar, Inspetor, Bibliotecário.
    """
    __tablename__ = 'employees'

    STATUSES = ['ativo', 'inativo', 'afastado', 'desligado']

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    full_name = db.Column(db.String(200), nullable=False, index=True)
    cpf = db.Column(db.String(11), unique=True, index=True)
    registration = db.Column(db.String(50), unique=True)
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    number = db.Column(db.String(20))
    complement = db.Column(db.String(100))
    neighborhood = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(8))
    position = db.Column(db.String(100))  # Cargo (texto livre)
    department = db.Column(db.String(100))  # Departamento
    status = db.Column(db.String(20), default='ativo', nullable=False)

    # Relacionamentos
    user = db.relationship('User', backref=db.backref('employee_profile', uselist=False))

    def __repr__(self):
        return f'<Employee {self.full_name}>'
