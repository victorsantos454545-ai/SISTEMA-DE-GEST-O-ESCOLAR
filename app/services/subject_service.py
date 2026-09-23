from sqlalchemy import or_
from app.extensions import db
from app.models import Subject
from app.services.audit_service import log_action

def can_view_subject(user, subject=None):
    # Todos podem ver as disciplinas cadastradas (leituras)
    return True

def can_edit_subject(user, subject=None):
    return user.role.name in ['admin', 'secretaria']

def get_subjects(user, page=1, per_page=10, search='', status=''):
    query = Subject.query
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(
            Subject.name.ilike(search_term),
            Subject.code.ilike(search_term),
            Subject.description.ilike(search_term)
        ))
        
    if status:
        query = query.filter(Subject.status == status)
        
    return query.order_by(Subject.name.asc()).paginate(page=page, per_page=per_page, error_out=False)

def create_subject(data, user):
    subject = Subject(
        name=data.get('name'),
        code=data.get('code'),
        workload=data.get('workload', 0),
        description=data.get('description'),
        status=data.get('status', 'ativa')
    )
    db.session.add(subject)
    db.session.commit()
    log_action('SUBJECT_CREATED', 'subjects', subject.id, f"Disciplina {subject.name} criada")
    return subject

def update_subject(subject, data, user):
    for key, value in data.items():
        if hasattr(subject, key):
            setattr(subject, key, value)
    db.session.commit()
    log_action('SUBJECT_UPDATED', 'subjects', subject.id, f"Disciplina {subject.name} atualizada")
    return subject

def change_subject_status(subject, status, user):
    old_status = subject.status
    subject.status = status
    db.session.commit()
    action = 'SUBJECT_ACTIVATED' if status == 'ativa' else 'SUBJECT_DEACTIVATED'
    log_action(action, 'subjects', subject.id, f"Status alterado de {old_status} para {status}")
    return subject
