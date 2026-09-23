from app.extensions import db


class ClassTeacher(db.Model):
    """Associação entre turmas e professores (N:N com flag de coordenador).

    Modelo completo porque armazena is_coordinator, indicando
    se o professor é o coordenador/responsável pela turma.
    """
    __tablename__ = 'class_teachers'
    __table_args__ = (
        db.UniqueConstraint('class_id', 'teacher_id', name='uq_class_teacher'),
    )

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('school_classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    is_coordinator = db.Column(db.Boolean, default=False, nullable=False)

    # Relacionamentos
    school_class = db.relationship('SchoolClass', back_populates='teacher_links')
    teacher = db.relationship('Teacher', back_populates='class_links')

    def __repr__(self):
        return f'<ClassTeacher class={self.class_id} teacher={self.teacher_id}>'
