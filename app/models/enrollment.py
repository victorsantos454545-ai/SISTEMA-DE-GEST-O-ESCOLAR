from app.extensions import db
from app.models.base import TimestampMixin


class Enrollment(TimestampMixin, db.Model):
    """Matrículas de alunos em turmas.

    Índice composto em (student_id, school_year_id) para consultas rápidas.
    A restrição de matrícula duplicada (mesmo aluno, mesmo ano, status ativa)
    será aplicada na camada de serviço (services), pois envolve lógica condicional.
    """
    __tablename__ = 'enrollments'
    __table_args__ = (
        db.Index('ix_enrollment_student_year', 'student_id', 'school_year_id'),
    )

    STATUSES = ['ativa', 'pendente', 'cancelada', 'transferida', 'concluida']

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    school_class_id = db.Column(db.Integer, db.ForeignKey('school_classes.id'), nullable=False)
    school_year_id = db.Column(db.Integer, db.ForeignKey('school_years.id'), nullable=False, index=True)
    enrollment_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='ativa', nullable=False)
    notes = db.Column(db.Text)

    # Relacionamentos
    student = db.relationship('Student', back_populates='enrollments')
    school_class = db.relationship('SchoolClass', back_populates='enrollments')
    school_year = db.relationship('SchoolYear', back_populates='enrollments')

    def __repr__(self):
        return f'<Enrollment student={self.student_id} class={self.school_class_id}>'
