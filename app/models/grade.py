from app.extensions import db
from app.models.base import TimestampMixin


class Grade(TimestampMixin, db.Model):
    """Notas dos alunos nas avaliações.

    UniqueConstraint impede que um aluno tenha duas notas
    para a mesma avaliação.
    Validação no modelo impede notas negativas.
    A validação de nota > max_value será feita na camada de serviço.
    """
    __tablename__ = 'grades'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'assessment_id', name='uq_student_assessment'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    value = db.Column(db.Float)
    observation = db.Column(db.Text)

    # Relacionamentos
    student = db.relationship('Student', back_populates='grades')
    assessment = db.relationship('Assessment', back_populates='grades')

    @db.validates('value')
    def validate_value(self, key, value):
        """Nota não pode ser negativa."""
        if value is not None and value < 0:
            raise ValueError('Nota não pode ser negativa.')
        return value

    def __repr__(self):
        return f'<Grade student={self.student_id} assessment={self.assessment_id} value={self.value}>'
