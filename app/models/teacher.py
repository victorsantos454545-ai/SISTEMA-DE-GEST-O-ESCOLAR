from app.extensions import db
from app.models.base import TimestampMixin


class Teacher(TimestampMixin, db.Model):
    """Professores da instituição.

    Relacionado a disciplinas via teacher_subjects (N:N simples).
    Relacionado a turmas via class_teachers (N:N com flag is_coordinator).
    """
    __tablename__ = 'teachers'

    STATUSES = ['ativo', 'inativo', 'afastado', 'desligado']

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    full_name = db.Column(db.String(200), nullable=False, index=True)
    cpf = db.Column(db.String(11), unique=True, index=True)
    registration = db.Column(db.String(50), unique=True)  # Matrícula funcional
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
    education = db.Column(db.String(200))  # Formação acadêmica
    specialization = db.Column(db.String(200))  # Especialização
    status = db.Column(db.String(20), default='ativo', nullable=False)

    # Relacionamentos
    user = db.relationship('User', backref=db.backref('teacher_profile', uselist=False))
    # N:N com Subject via tabela associativa simples
    subjects = db.relationship(
        'Subject', secondary='teacher_subjects',
        back_populates='teachers', lazy='dynamic'
    )
    # N:N com SchoolClass via modelo ClassTeacher (tem campo extra is_coordinator)
    class_links = db.relationship('ClassTeacher', back_populates='teacher', lazy='dynamic')
    assessments = db.relationship('Assessment', back_populates='teacher', lazy='dynamic')
    activities = db.relationship('Activity', back_populates='teacher', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='teacher', lazy='dynamic')
    attendances = db.relationship('Attendance', back_populates='teacher', lazy='dynamic')

    @property
    def name(self):
        """Retorna o nome completo do professor."""
        return self.full_name

    def __repr__(self):
        return f'<Teacher {self.full_name}>'
