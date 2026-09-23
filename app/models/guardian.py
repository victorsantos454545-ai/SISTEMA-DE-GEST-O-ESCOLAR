from app.extensions import db
from app.models.base import TimestampMixin


class Guardian(TimestampMixin, db.Model):
    """Responsáveis pelos alunos.

    Um responsável pode ser vinculado a vários alunos,
    e um aluno pode ter vários responsáveis (relação N:N
    via tabela student_guardians).
    """
    __tablename__ = 'guardians'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    full_name = db.Column(db.String(200), nullable=False, index=True)
    cpf = db.Column(db.String(11), unique=True, index=True)
    phone = db.Column(db.String(20))
    secondary_phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    number = db.Column(db.String(20))
    complement = db.Column(db.String(100))
    neighborhood = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(8))

    # Relacionamentos
    user = db.relationship('User', backref=db.backref('guardian_profile', uselist=False))
    student_links = db.relationship(
        'StudentGuardian', back_populates='guardian',
        cascade='all, delete-orphan', lazy='dynamic'
    )

    @property
    def students(self):
        """Retorna a lista de alunos vinculados a este responsável."""
        return [link.student for link in self.student_links]

    def __repr__(self):
        return f'<Guardian {self.full_name}>'
