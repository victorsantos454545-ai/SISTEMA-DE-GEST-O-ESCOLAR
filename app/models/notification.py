from app.extensions import db
from app.models.base import TimestampMixin

class Notification(TimestampMixin, db.Model):
    """Notificações do sistema para usuários específicos.
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False) # announcement, system, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255))
    read_at = db.Column(db.DateTime)
    
    # Identifier to prevent duplicate notifications (e.g. "announcement_123")
    reference_id = db.Column(db.String(100))

    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Notification {self.title} to {self.user_id}>'
