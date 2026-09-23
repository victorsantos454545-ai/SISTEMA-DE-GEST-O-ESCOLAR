from app.extensions import db
from app.models.base import TimestampMixin


class CalendarEvent(TimestampMixin, db.Model):
    """Eventos do calendário escolar.

    event_type utiliza string para flexibilidade.
    created_by referencia o usuário que criou o evento.
    """
    __tablename__ = 'calendar_events'

    EVENT_TYPES = ['aula', 'prova', 'avaliacao', 'reuniao', 'evento', 'feriado', 'atividade', 'outro']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(20), nullable=False, default='evento')
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime)
    all_day = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    school_class_id = db.Column(db.Integer, db.ForeignKey('school_classes.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    school_year_id = db.Column(db.Integer, db.ForeignKey('school_years.id'))
    status = db.Column(db.String(20), default='draft', nullable=False)

    # Relacionamentos
    creator = db.relationship('User', back_populates='calendar_events')
    school_class = db.relationship('SchoolClass')
    subject = db.relationship('Subject')
    school_year = db.relationship('SchoolYear')

    def __repr__(self):
        return f'<CalendarEvent {self.title}>'
