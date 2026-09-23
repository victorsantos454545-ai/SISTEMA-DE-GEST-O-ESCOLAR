from app.extensions import db
from app.models.base import TimestampMixin


class Schedule(TimestampMixin, db.Model):
    """Grade de horários.

    day_of_week utiliza string em vez de enum para compatibilidade
    entre SQLite e MySQL.
    """
    __tablename__ = 'schedules'

    DAYS = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

    id = db.Column(db.Integer, primary_key=True)
    school_class_id = db.Column(db.Integer, db.ForeignKey('school_classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50))

    # Relacionamentos
    school_class = db.relationship('SchoolClass', back_populates='schedules')
    subject = db.relationship('Subject', back_populates='schedules')
    teacher = db.relationship('Teacher', back_populates='schedules')

    def __repr__(self):
        return f'<Schedule {self.day_of_week} {self.start_time}-{self.end_time}>'
