from app.extensions import db
from app.models.base import TimestampMixin


class Activity(TimestampMixin, db.Model):
    """Atividades escolares.

    Status como string permite extensão futura:
    rascunho, publicada, encerrada, cancelada.
    """
    __tablename__ = 'activities'

    STATUSES = ['rascunho', 'publicada', 'encerrada', 'cancelada']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    activity_type = db.Column(db.String(50), default='Outro', nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    school_class_id = db.Column(db.Integer, db.ForeignKey('school_classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    published_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='rascunho', nullable=False)

    # Relacionamentos
    subject = db.relationship('Subject', back_populates='activities')
    school_class = db.relationship('SchoolClass', back_populates='activities')
    teacher = db.relationship('Teacher', back_populates='activities')

    def __repr__(self):
        return f'<Activity {self.title}>'
