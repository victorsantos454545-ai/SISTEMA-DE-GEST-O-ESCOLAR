from sqlalchemy import or_
from app.extensions import db
from app.models.teacher import Teacher
from app.models.class_teacher import ClassTeacher
from app.services.audit_service import log_action
import re

def can_view_teacher(user, teacher):
    if user.role.name in ['admin', 'secretaria']:
        return True
    if user.role.name == 'professor':
        return getattr(user.teacher_profile, 'id', None) == teacher.id
    return False

def can_edit_teacher(user, teacher):
    return user.role.name in ['admin', 'secretaria']

def can_manage_teacher_classes(user):
    return user.role.name in ['admin', 'secretaria']

def can_manage_teacher_subjects(user):
    return user.role.name in ['admin', 'secretaria']

def search_teachers(query=None, status=None, page=1, per_page=20):
    base_query = Teacher.query
    
    if query:
        search_term = f"%{query}%"
        numeric_query = re.sub(r'[^0-9]', '', query)
        
        if numeric_query:
            base_query = base_query.filter(or_(
                Teacher.full_name.ilike(search_term),
                Teacher.email.ilike(search_term),
                Teacher.cpf.ilike(f"%{numeric_query}%"),
                Teacher.registration.ilike(f"%{numeric_query}%")
            ))
        else:
            base_query = base_query.filter(or_(
                Teacher.full_name.ilike(search_term),
                Teacher.email.ilike(search_term),
                Teacher.registration.ilike(search_term)
            ))
            
    if status:
        base_query = base_query.filter_by(status=status)
            
    base_query = base_query.order_by(Teacher.full_name.asc())
    return base_query.paginate(page=page, per_page=per_page, error_out=False)

def create_teacher(data):
    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    teacher = Teacher(**data)
    db.session.add(teacher)
    db.session.commit()
    
    log_action('TEACHER_CREATED', entity='teacher', entity_id=teacher.id, description=f'Criou professor ID {teacher.id}')
    return teacher

def update_teacher(teacher, data):
    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    for key, value in data.items():
        if hasattr(teacher, key):
            setattr(teacher, key, value)
            
    db.session.commit()
    log_action('TEACHER_UPDATED', entity='teacher', entity_id=teacher.id, description=f'Atualizou professor ID {teacher.id}')
    return teacher

def deactivate_teacher(teacher):
    teacher.status = 'inativo'
    db.session.commit()
    log_action('TEACHER_DEACTIVATED', entity='teacher', entity_id=teacher.id, description=f'Desativou professor ID {teacher.id}')
    return teacher

def activate_teacher(teacher):
    teacher.status = 'ativo'
    db.session.commit()
    log_action('TEACHER_ACTIVATED', entity='teacher', entity_id=teacher.id, description=f'Ativou professor ID {teacher.id}')
    return teacher

def link_teacher_subject(teacher, subject):
    if subject not in teacher.subjects:
        teacher.subjects.append(subject)
        db.session.commit()
        log_action('TEACHER_SUBJECT_LINKED', entity='teacher', entity_id=teacher.id, description=f'Vinculou disciplina {subject.id} ao professor ID {teacher.id}')
        return True
    return False

def unlink_teacher_subject(teacher, subject):
    if subject in teacher.subjects:
        teacher.subjects.remove(subject)
        db.session.commit()
        log_action('TEACHER_SUBJECT_UNLINKED', entity='teacher', entity_id=teacher.id, description=f'Removeu disciplina {subject.id} do professor ID {teacher.id}')
        return True
    return False

def link_teacher_class(teacher, school_class, is_coordinator=False):
    # Check if link exists
    existing = ClassTeacher.query.filter_by(teacher_id=teacher.id, class_id=school_class.id).first()
    if existing:
        return False, "Professor já vinculado à turma."
        
    try:
        if is_coordinator:
            # Demote existing coordinator for this class if any
            ClassTeacher.query.filter_by(class_id=school_class.id, is_coordinator=True).update({'is_coordinator': False})
            
        link = ClassTeacher(
            teacher_id=teacher.id,
            class_id=school_class.id,
            is_coordinator=is_coordinator
        )
        db.session.add(link)
        db.session.commit()
        
        log_action('TEACHER_CLASS_LINKED', entity='teacher', entity_id=teacher.id, description=f'Vinculou professor {teacher.id} à turma {school_class.id}')
        return True, "Turma vinculada."
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def unlink_teacher_class(teacher_id, class_id):
    link = ClassTeacher.query.filter_by(teacher_id=teacher_id, class_id=class_id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        log_action('TEACHER_CLASS_UNLINKED', entity='teacher', entity_id=teacher_id, description=f'Removeu professor {teacher_id} da turma {class_id}')
        return True
    return False

def set_class_coordinator(teacher_id, class_id):
    try:
        # Demote existing coordinator
        ClassTeacher.query.filter_by(class_id=class_id, is_coordinator=True).update({'is_coordinator': False})
        
        link = ClassTeacher.query.filter_by(teacher_id=teacher_id, class_id=class_id).first()
        if link:
            link.is_coordinator = True
            db.session.commit()
            log_action('TEACHER_COORDINATOR_CHANGED', entity='teacher', entity_id=teacher_id, description=f'Professor {teacher_id} definido como coordenador da turma {class_id}')
            return True
        return False
    except Exception as e:
        db.session.rollback()
        return False
