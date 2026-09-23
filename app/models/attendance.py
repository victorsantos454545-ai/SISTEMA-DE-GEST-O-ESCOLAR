from app.extensions import db
from app.models.base import TimestampMixin


class Attendance(TimestampMixin, db.Model):
    """Registro de frequência dos alunos.

    UniqueConstraint impede registro duplicado do mesmo aluno
    para a mesma disciplina/turma/data.
    """
    __tablename__ = 'attendance'
    __table_args__ = (
        db.UniqueConstraint(
            'student_id', 'school_class_id', 'subject_id', 'date',
            name='uq_attendance_record'
        ),
        db.Index('ix_attendance_date', 'date'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    school_class_id = db.Column(db.Integer, db.ForeignKey('school_classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    date = db.Column(db.Date, nullable=False)
    period = db.Column(db.String(20))  # Período da aula (1ª aula, 2ª aula, etc.)
    present = db.Column(db.Boolean, default=True, nullable=False)
    justification = db.Column(db.Text)

    # Relacionamentos
    student = db.relationship('Student', back_populates='attendances')
    school_class = db.relationship('SchoolClass', back_populates='attendances')
    subject = db.relationship('Subject', back_populates='attendances')
    teacher = db.relationship('Teacher', back_populates='attendances')

    def __repr__(self):
        return f'<Attendance student={self.student_id} date={self.date} present={self.present}>'
