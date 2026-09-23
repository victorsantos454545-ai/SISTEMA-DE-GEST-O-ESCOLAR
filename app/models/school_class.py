from app.extensions import db
from app.models.base import TimestampMixin


class SchoolClass(TimestampMixin, db.Model):
    """Turmas.

    Utiliza strings para shift e status em vez de enums rígidos.
    A capacidade padrão é 40 alunos.
    """
    __tablename__ = 'school_classes'

    SHIFTS = ['Manhã', 'Tarde', 'Noite', 'Integral']
    STATUSES = ['ativa', 'inativa', 'encerrada']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_year_id = db.Column(db.Integer, db.ForeignKey('school_years.id'), nullable=False)
    grade = db.Column(db.String(50))  # Série: 6º Ano, 7º Ano, etc.
    shift = db.Column(db.String(20), nullable=False)  # Turno
    room = db.Column(db.String(50))  # Sala
    capacity = db.Column(db.Integer, default=40)
    status = db.Column(db.String(20), default='ativa', nullable=False)

    # Relacionamentos
    school_year = db.relationship('SchoolYear', back_populates='school_classes')
    enrollments = db.relationship('Enrollment', back_populates='school_class', lazy='dynamic')
    # N:N com Subject via ClassSubject (tem campo extra workload)
    subject_links = db.relationship(
        'ClassSubject', back_populates='school_class',
        cascade='all, delete-orphan', lazy='dynamic'
    )
    # N:N com Teacher via ClassTeacher (tem campo extra is_coordinator)
    teacher_links = db.relationship(
        'ClassTeacher', back_populates='school_class',
        cascade='all, delete-orphan', lazy='dynamic'
    )
    assessments = db.relationship('Assessment', back_populates='school_class', lazy='dynamic')
    attendances = db.relationship('Attendance', back_populates='school_class', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='school_class', lazy='dynamic')
    activities = db.relationship('Activity', back_populates='school_class', lazy='dynamic')

    @property
    def enrolled_count(self):
        """Retorna o número de alunos com matrícula ativa nesta turma."""
        return self.enrollments.filter_by(status='ativa').count()

    @db.validates('capacity')
    def validate_capacity(self, key, value):
        """Capacidade não pode ser negativa."""
        if value is not None and value < 0:
            raise ValueError('Capacidade da turma não pode ser negativa.')
        return value

    def __repr__(self):
        return f'<SchoolClass {self.name}>'
