from app.extensions import db
from app.models.base import TimestampMixin


class Announcement(TimestampMixin, db.Model):
    """Comunicados do sistema.

    O autor é um usuário do sistema.
    Os destinatários são definidos via AnnouncementRecipient,
    permitindo publicar para múltiplos públicos simultaneamente.
    """
    __tablename__ = 'announcements'

    STATUSES = ['rascunho', 'agendado', 'publicado', 'expirado', 'arquivado', 'cancelado']
    PRIORITIES = ['normal', 'important', 'urgent']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    priority = db.Column(db.String(20), default='normal', server_default='normal', nullable=False)
    published_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='rascunho', nullable=False)

    # Relacionamentos
    author = db.relationship('User', back_populates='announcements')
    # Destinatários são dependentes: ao excluir comunicado, destinatários são removidos
    recipients = db.relationship(
        'AnnouncementRecipient', back_populates='announcement',
        cascade='all, delete-orphan', lazy='dynamic'
    )
    reads = db.relationship(
        'AnnouncementRead', back_populates='announcement',
        cascade='all, delete-orphan', lazy='dynamic'
    )

    def __repr__(self):
        return f'<Announcement {self.title}>'


class AnnouncementRecipient(db.Model):
    """Destinatários dos comunicados.

    Permite publicar um comunicado para múltiplos públicos:
    - target_type='todos': todos os usuários (target_id=NULL)
    - target_type='admin': administradores (target_id=NULL)
    - target_type='professor': professores (target_id=NULL)
    - target_type='secretaria': secretaria (target_id=NULL)
    - target_type='aluno': alunos (target_id=NULL)
    - target_type='responsavel': responsáveis (target_id=NULL)
    - target_type='turma': turma específica (target_id=school_class.id)
    """
    __tablename__ = 'announcement_recipients'
    __table_args__ = (
        db.UniqueConstraint(
            'announcement_id', 'target_type', 'target_id',
            name='uq_announcement_recipient'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # todos, admin, professor, etc.
    target_id = db.Column(db.Integer)  # NULL para roles, class_id para turma

    # Relacionamentos
    announcement = db.relationship('Announcement', back_populates='recipients')

    def __repr__(self):
        return f'<AnnouncementRecipient type={self.target_type} id={self.target_id}>'

class AnnouncementRead(db.Model):
    __tablename__ = 'announcement_reads'
    __table_args__ = (
        db.UniqueConstraint(
            'announcement_id', 'user_id',
            name='uq_announcement_read'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    announcement = db.relationship('Announcement', back_populates='reads')
    user = db.relationship('User', backref=db.backref('announcement_reads', lazy='dynamic'))

    def __repr__(self):
        return f'<AnnouncementRead announcement={self.announcement_id} user={self.user_id}>'
