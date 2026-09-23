from app.extensions import db
from app.models.base import TimestampMixin


class Student(TimestampMixin, db.Model):
    """Alunos da instituição.

    Não permite exclusão física quando há histórico acadêmico.
    Utiliza status para desativação (exclusão lógica).
    Opcionalmente vinculado a um User para acesso ao sistema.
    """
    __tablename__ = 'students'

    STATUSES = ['ativo', 'inativo', 'transferido', 'concluido']

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    full_name = db.Column(db.String(200), nullable=False, index=True)
    social_name = db.Column(db.String(200))
    birth_date = db.Column(db.Date)
    cpf = db.Column(db.String(11), unique=True, index=True)
    rg = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    number = db.Column(db.String(20))
    complement = db.Column(db.String(100))
    neighborhood = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(8))
    status = db.Column(db.String(20), default='ativo', nullable=False)
    notes = db.Column(db.Text)

    # Relacionamentos
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))
    enrollments = db.relationship('Enrollment', back_populates='student', lazy='dynamic')
    grades = db.relationship('Grade', back_populates='student', lazy='dynamic')
    attendances = db.relationship('Attendance', back_populates='student', lazy='dynamic')
    guardian_links = db.relationship(
        'StudentGuardian', back_populates='student',
        cascade='all, delete-orphan', lazy='dynamic'
    )

    @property
    def guardians(self):
        """Retorna a lista de responsáveis vinculados ao aluno."""
        return [link.guardian for link in self.guardian_links]

    def __repr__(self):
        return f'<Student {self.full_name}>'
