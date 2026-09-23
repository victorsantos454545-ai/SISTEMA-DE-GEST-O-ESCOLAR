from app.extensions import db
from app.models import Announcement, AnnouncementRecipient, AnnouncementRead, User, Student, Guardian, Teacher, SchoolClass, Enrollment
from app.services.notification_service import create_notification
from app.services.audit_service import log_action
from datetime import datetime
from sqlalchemy import or_, and_

def get_announcement_recipients(announcement):
    """Returns a set of User objects who should receive this announcement."""
    users = set()
    for recipient in announcement.recipients:
        if recipient.target_type == 'todos':
            users.update(User.query.filter_by(active=True).all())
        elif recipient.target_type in ['admin', 'secretaria', 'professor', 'aluno', 'responsavel']:
            # Assuming role names match these or we just filter by role name
            # Usually role names are 'admin', 'secretaria', 'professor', 'aluno', 'responsavel'
            users.update(User.query.join(User.role).filter(User.active == True, User.role.has(name=recipient.target_type)).all())
        elif recipient.target_type == 'turma' and recipient.target_id:
            # Find users related to this class (students, guardians, teachers)
            # Students
            enrollments = Enrollment.query.filter_by(school_class_id=recipient.target_id, status='ativo').all()
            for e in enrollments:
                if e.student and e.student.user and e.student.user.active:
                    users.add(e.student.user)
                # Guardians of this student
                if e.student:
                    for sg in e.student.guardians:
                        if sg.guardian and sg.guardian.user and sg.guardian.user.active:
                            users.add(sg.guardian.user)
            # Teachers of this class
            school_class = SchoolClass.query.get(recipient.target_id)
            if school_class:
                for ct in school_class.teachers:
                    if ct.teacher and ct.teacher.user and ct.teacher.user.active:
                        users.add(ct.teacher.user)
    return users

def get_visible_announcements(user, limit=None):
    """Returns announcements visible to the user."""
    # First, gather all possible target types for this user
    target_types = ['todos']
    if user.role:
        target_types.append(user.role.name)
    
    target_ids = []
    # If student, add their classes
    if user.role and user.role.name == 'aluno' and user.profile:
        for enrollment in user.profile.enrollments:
            if enrollment.status == 'ativo' or enrollment.status == 'ativa':
                target_ids.append(enrollment.school_class_id)
    
    # If guardian, add their students' classes
    if user.role and user.role.name == 'responsavel' and user.profile:
        for student in user.profile.students:
            for enrollment in student.enrollments:
                if enrollment.status == 'ativo' or enrollment.status == 'ativa':
                    target_ids.append(enrollment.school_class_id)
                    
    # If teacher, add their classes
    if user.role and user.role.name == 'professor' and user.profile:
        for ct in user.profile.class_links:
            target_ids.append(ct.class_id)
            
    now = datetime.now()
    
    # Base query for published announcements that haven't expired
    query = Announcement.query.filter(
        Announcement.status == 'publicado',
        (Announcement.published_at <= now) | (Announcement.published_at == None),
        (Announcement.expires_at == None) | (Announcement.expires_at > now)
    )
    
    # Filter by recipients
    query = query.join(AnnouncementRecipient).filter(
        or_(
            AnnouncementRecipient.target_type.in_(target_types),
            and_(AnnouncementRecipient.target_type == 'turma', AnnouncementRecipient.target_id.in_(target_ids))
        )
    )
    
    # Admin and secretaria can see all
    if user.role and user.role.name in ['admin', 'secretaria']:
        query = Announcement.query.filter(
            Announcement.status == 'publicado',
            (Announcement.published_at <= now) | (Announcement.published_at == None),
            (Announcement.expires_at == None) | (Announcement.expires_at > now)
        )
        
    query = query.order_by(
        db.case(
            (Announcement.priority == 'urgent', 1),
            (Announcement.priority == 'important', 2),
            else_=3
        ),
        Announcement.published_at.desc()
    ).distinct()
    
    if limit:
        return query.limit(limit).all()
    return query.all()

def mark_as_read(announcement_id, user_id):
    read = AnnouncementRead.query.filter_by(announcement_id=announcement_id, user_id=user_id).first()
    if not read:
        read = AnnouncementRead(announcement_id=announcement_id, user_id=user_id)
        db.session.add(read)
        db.session.commit()
        
def get_unread_count(user):
    visible = get_visible_announcements(user)
    visible_ids = [a.id for a in visible]
    if not visible_ids:
        return 0
    read_ids = [r.announcement_id for r in AnnouncementRead.query.filter(AnnouncementRead.user_id == user.id).all()]
    return len([a for a in visible_ids if a not in read_ids])

def create_announcement(data, user_id):
    announcement = Announcement(
        title=data['title'],
        content=data['content'],
        priority=data.get('priority', 'normal'),
        author_id=user_id,
        published_at=data.get('published_at'),
        expires_at=data.get('expires_at'),
        status=data.get('status', 'rascunho')
    )
    db.session.add(announcement)
    db.session.flush()
    
    # Process recipients
    targets = data.get('targets', [])
    for target in targets:
        target_type = target.get('type')
        target_id = target.get('id')
        rec = AnnouncementRecipient(
            announcement_id=announcement.id,
            target_type=target_type,
            target_id=target_id
        )
        db.session.add(rec)
        
    db.session.commit()
    log_action('create_announcement', 'announcements', announcement.id, 'Comunicado criado', user_id)
    
    if announcement.status == 'publicado' and announcement.published_at and announcement.published_at <= datetime.now():
        _notify_recipients(announcement)
        
    return announcement

def update_announcement(announcement_id, data, user_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    was_published = announcement.status == 'publicado'
    
    announcement.title = data.get('title', announcement.title)
    announcement.content = data.get('content', announcement.content)
    announcement.priority = data.get('priority', announcement.priority)
    announcement.published_at = data.get('published_at', announcement.published_at)
    announcement.expires_at = data.get('expires_at', announcement.expires_at)
    announcement.status = data.get('status', announcement.status)
    
    # Update targets if provided
    if 'targets' in data:
        # Delete old
        AnnouncementRecipient.query.filter_by(announcement_id=announcement.id).delete()
        for target in data['targets']:
            target_type = target.get('type')
            target_id = target.get('id')
            rec = AnnouncementRecipient(
                announcement_id=announcement.id,
                target_type=target_type,
                target_id=target_id
            )
            db.session.add(rec)
            
    db.session.commit()
    log_action('update_announcement', 'announcements', announcement.id, 'Comunicado atualizado', user_id)
    
    if not was_published and announcement.status == 'publicado' and announcement.published_at and announcement.published_at <= datetime.now():
        _notify_recipients(announcement)
        
    return announcement

def cancel_announcement(announcement_id, user_id, reason=""):
    announcement = Announcement.query.get_or_404(announcement_id)
    announcement.status = 'cancelado'
    db.session.commit()
    log_action('cancel_announcement', 'announcements', announcement.id, f'Comunicado cancelado. Motivo: {reason}', user_id)
    return announcement

def _notify_recipients(announcement):
    users = get_announcement_recipients(announcement)
    for u in users:
        create_notification(
            user_id=u.id,
            notification_type='announcement',
            title=f"Novo Comunicado: {announcement.title}",
            message=announcement.content[:100] + ('...' if len(announcement.content) > 100 else ''),
            link=f"/comunicados/{announcement.id}",
            reference_id=f"announcement_{announcement.id}"
        )
