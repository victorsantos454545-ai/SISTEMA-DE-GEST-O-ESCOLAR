from app.extensions import db
from app.models.base import TimestampMixin


class Period(TimestampMixin, db.Model):
    """Períodos acadêmicos (1º Bimestre, 2º Bimestre, etc.).

    Permite que a escola configure diferentes estruturas:
    bimestres, trimestres, semestres.
    A sequência (sequence) define a ordem dos períodos dentro do ano.
    """
    __tablename__ = 'periods'
    __table_args__ = (
        db.UniqueConstraint('school_year_id', 'sequence', name='uq_period_year_sequence'),
    )

    id = db.Column(db.Integer, primary_key=True)
    school_year_id = db.Column(db.Integer, db.ForeignKey('school_years.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    # Relacionamentos
    school_year = db.relationship('SchoolYear', back_populates='periods')
    assessments = db.relationship('Assessment', back_populates='period', lazy='dynamic')

    def __repr__(self):
        return f'<Period {self.name}>'
