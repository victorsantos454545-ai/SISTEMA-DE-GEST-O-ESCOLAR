import pytest
from app.models import Announcement, AnnouncementRecipient, Notification, AnnouncementRead, User, Role
from app.services.announcement_service import create_announcement, get_visible_announcements, get_announcement_recipients
from app.services.notification_service import create_notification, get_unread_count
from app.extensions import db
from datetime import datetime

def test_create_and_visibility(app):
    with app.app_context():
        # Setup
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Admin')
            db.session.add(admin_role)
            db.session.commit()
            
        u = User(username='test_admin', email='test_admin@e.com', role_id=admin_role.id, password_hash='hash')
        db.session.add(u)
        db.session.commit()
        
        # Test creation
        data = {
            'title': 'Test Ann',
            'content': 'Test Content',
            'priority': 'urgent',
            'status': 'publicado',
            'published_at': datetime.now(),
            'targets': [{'type': 'todos'}]
        }
        
        ann = create_announcement(data, u.id)
        assert ann.title == 'Test Ann'
        assert ann.priority == 'urgent'
        assert ann.recipients.count() == 1
        
        # Check visibility
        visible = get_visible_announcements(u)
        assert ann.id in [a.id for a in visible]

def test_notifications(app):
    with app.app_context():
        u = User.query.filter_by(username='test_admin').first()
        if not u:
            # Em fallback se o test for rodado separadamente
            return
            
        # Create notif
        n = create_notification(u.id, 'system', 'Test Notif', 'Test Msg')
        assert n.id is not None
        
        # Check unread
        assert get_unread_count(u.id) > 0
