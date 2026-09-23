from app.extensions import db
from app.models.base import TimestampMixin


class StudentGuardian(TimestampMixin, db.Model):
    """Associação entre alunos e responsáveis (N:N com dados extras).

    Modelo completo (não apenas db.Table) porque armazena:
    - relationship: grau de parentesco (pai, mãe, avô, tio, etc.)
    - is_primary: se é o responsável principal
    """
    __tablename__ = 'student_guardians'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'guardian_id', name='uq_student_guardian'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    guardian_id = db.Column(db.Integer, db.ForeignKey('guardians.id'), nullable=False)
    relationship = db.Column(db.String(50))  # pai, mãe, avô, avó, tio, etc.
    is_primary = db.Column(db.Boolean, default=False, nullable=False)

    # Relacionamentos
    student = db.relationship('Student', back_populates='guardian_links')
    guardian = db.relationship('Guardian', back_populates='student_links')

    def __repr__(self):
        return f'<StudentGuardian student={self.student_id} guardian={self.guardian_id}>'
