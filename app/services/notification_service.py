from app.extensions import db
from app.models import Notification
from datetime import datetime

def create_notification(user_id, notification_type, title, message, link=None, reference_id=None):
    if reference_id:
        existing = Notification.query.filter_by(user_id=user_id, reference_id=reference_id).first()
        if existing:
            return existing
            
    notif = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        reference_id=reference_id
    )
    db.session.add(notif)
    db.session.commit()
    return notif

def mark_as_read(notification_id, user_id):
    notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if notif and not notif.read_at:
        notif.read_at = datetime.now()
        db.session.commit()
    return notif

def mark_all_as_read(user_id):
    Notification.query.filter_by(user_id=user_id, read_at=None).update({Notification.read_at: datetime.now()})
    db.session.commit()

def get_unread_count(user_id):
    return Notification.query.filter_by(user_id=user_id, read_at=None).count()

def get_recent_notifications(user_id, limit=5):
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(limit).all()

def get_all_notifications(user_id, page=1, per_page=20, unread_only=False):
    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter(Notification.read_at == None)
    return query.order_by(Notification.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
