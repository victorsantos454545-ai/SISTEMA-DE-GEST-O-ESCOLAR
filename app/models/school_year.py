from app.extensions import db
from app.models.base import TimestampMixin


class SchoolYear(TimestampMixin, db.Model):
    """Ano letivo.

    Centraliza o conceito de ano letivo para evitar repetição
    de 'year' como número avulso em várias tabelas.
    Apenas um ano letivo deve estar ativo por vez.
    """
    __tablename__ = 'school_years'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    active = db.Column(db.Boolean, default=False, nullable=False)

    # Relacionamentos
    # Períodos são dependentes do ano letivo (cascade delete)
    periods = db.relationship(
        'Period', back_populates='school_year',
        lazy='dynamic', cascade='all, delete-orphan'
    )
    school_classes = db.relationship('SchoolClass', back_populates='school_year', lazy='dynamic')
    enrollments = db.relationship('Enrollment', back_populates='school_year', lazy='dynamic')

    def __repr__(self):
        return f'<SchoolYear {self.year}>'
