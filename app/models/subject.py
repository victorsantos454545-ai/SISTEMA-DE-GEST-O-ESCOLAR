from app.extensions import db
from app.models.base import TimestampMixin


class Subject(TimestampMixin, db.Model):
    """Disciplinas.

    Utiliza status como string ('ativa'/'inativa') em vez de enum rígido,
    permitindo extensão futura sem alterar o banco.
    Carga horária (workload) é armazenada em horas.
    """
    __tablename__ = 'subjects'

    STATUSES = ['ativa', 'inativa']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True)  # Código único da disciplina
    workload = db.Column(db.Integer, default=0)  # Carga horária em horas
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='ativa', nullable=False)

    # Relacionamentos
    teachers = db.relationship(
        'Teacher', secondary='teacher_subjects',
        back_populates='subjects', lazy='dynamic'
    )
    class_links = db.relationship('ClassSubject', back_populates='subject', lazy='dynamic')
    assessments = db.relationship('Assessment', back_populates='subject', lazy='dynamic')
    attendances = db.relationship('Attendance', back_populates='subject', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='subject', lazy='dynamic')
    activities = db.relationship('Activity', back_populates='subject', lazy='dynamic')

    @db.validates('workload')
    def validate_workload(self, key, value):
        """Carga horária não pode ser negativa."""
        if value is not None and value < 0:
            raise ValueError('Carga horária não pode ser negativa.')
        return value

    def __repr__(self):
        return f'<Subject {self.name}>'
