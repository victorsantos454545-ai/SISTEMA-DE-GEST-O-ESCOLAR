from app.extensions import db


class ClassSubject(db.Model):
    """Associação entre turmas e disciplinas (N:N com carga horária).

    Modelo completo (não db.Table) porque armazena workload específica
    da disciplina nesta turma, que pode diferir da carga horária padrão.
    """
    __tablename__ = 'class_subjects'
    __table_args__ = (
        db.UniqueConstraint('class_id', 'subject_id', name='uq_class_subject'),
    )

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('school_classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    workload = db.Column(db.Integer)  # Carga horária específica para esta turma

    # Relacionamentos
    school_class = db.relationship('SchoolClass', back_populates='subject_links')
    subject = db.relationship('Subject', back_populates='class_links')

    def __repr__(self):
        return f'<ClassSubject class={self.class_id} subject={self.subject_id}>'
