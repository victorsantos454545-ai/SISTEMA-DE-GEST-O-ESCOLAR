from app.extensions import db
from app.models.base import TimestampMixin


class Assessment(TimestampMixin, db.Model):
    """Avaliações (provas, trabalhos, projetos, seminários).

    Grades (notas) dos alunos são dependentes da avaliação:
    se a avaliação for excluída, suas notas também serão (cascade delete-orphan).
    """
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    school_class_id = db.Column(db.Integer, db.ForeignKey('school_classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    period_id = db.Column(db.Integer, db.ForeignKey('periods.id'), nullable=False)
    date = db.Column(db.Date, index=True)
    max_value = db.Column(db.Float, default=10.0, nullable=False)
    weight = db.Column(db.Float, default=1.0, nullable=False)
    assessment_type = db.Column(db.String(50), default='prova')
    status = db.Column(db.String(20), default='ativa', nullable=False)
    description = db.Column(db.Text)

    # Relacionamentos
    subject = db.relationship('Subject', back_populates='assessments')
    school_class = db.relationship('SchoolClass', back_populates='assessments')
    teacher = db.relationship('Teacher', back_populates='assessments')
    period = db.relationship('Period', back_populates='assessments')
    # Notas são dependentes: ao excluir avaliação, notas são removidas
    grades = db.relationship(
        'Grade', back_populates='assessment',
        cascade='all, delete-orphan', lazy='dynamic'
    )

    @db.validates('max_value')
    def validate_max_value(self, key, value):
        """Valor máximo não pode ser negativo."""
        if value is not None and value < 0:
            raise ValueError('Valor máximo da avaliação não pode ser negativo.')
        return value

    def __repr__(self):
        return f'<Assessment {self.title}>'
