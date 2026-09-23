from sqlalchemy import or_
from app.extensions import db
from app.models import SchoolClass, ClassTeacher, ClassSubject, SchoolYear
from app.services.audit_service import log_action

def can_view_class(user, school_class):
    if user.role.name in ['admin', 'secretaria']:
        return True
    if user.role.name == 'professor':
        # Professor pode ver as turmas que ele leciona
        return school_class.teacher_links.filter_by(teacher_id=user.profile.id).first() is not None
    if user.role.name == 'responsavel':
        # Responsável só pode ver a turma dos seus filhos
        for student in user.profile.students:
            for enrollment in student.enrollments.filter_by(status='ativa').all():
                if enrollment.class_id == school_class.id:
                    return True
        return False
    if user.role.name == 'aluno':
        # Aluno só pode ver sua própria turma
        for enrollment in user.profile.enrollments.filter_by(status='ativa').all():
            if enrollment.class_id == school_class.id:
                return True
        return False
    return False

def can_edit_class(user, school_class=None):
    return user.role.name in ['admin', 'secretaria']

def can_manage_class_teachers(user):
    return user.role.name in ['admin', 'secretaria']

def can_manage_class_subjects(user):
    return user.role.name in ['admin', 'secretaria']

def get_classes(user, page=1, per_page=10, search='', status='', shift='', year_id='', grade=''):
    query = SchoolClass.query
    
    # RBAC: Professor vê só suas turmas, alunos/pais não listam todas, etc.
    if user.role.name == 'professor':
        query = query.join(ClassTeacher).filter(ClassTeacher.teacher_id == user.profile.id)
    elif user.role.name in ['aluno', 'responsavel']:
        # Geralmente não acessam a lista de turmas global, mas vamos bloquear no nível da rota
        query = query.filter(SchoolClass.id == -1)
        
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(
            SchoolClass.name.ilike(search_term),
            SchoolClass.room.ilike(search_term),
            SchoolClass.grade.ilike(search_term)
        ))
        
    if status:
        query = query.filter(SchoolClass.status == status)
    if shift:
        query = query.filter(SchoolClass.shift == shift)
    if year_id:
        query = query.filter(SchoolClass.school_year_id == year_id)
    if grade:
        query = query.filter(SchoolClass.grade == grade)
        
    return query.order_by(SchoolClass.name.asc()).paginate(page=page, per_page=per_page, error_out=False)

def create_class(data, user):
    school_class = SchoolClass(
        name=data.get('name'),
        school_year_id=data.get('school_year_id'),
        grade=data.get('grade'),
        shift=data.get('shift'),
        room=data.get('room'),
        capacity=data.get('capacity', 40),
        status=data.get('status', 'ativa')
    )
    db.session.add(school_class)
    db.session.commit()
    log_action('CLASS_CREATED', 'school_classes', school_class.id, f"Turma {school_class.name} criada")
    return school_class

def update_class(school_class, data, user):
    for key, value in data.items():
        if hasattr(school_class, key):
            setattr(school_class, key, value)
    db.session.commit()
    log_action('CLASS_UPDATED', 'school_classes', school_class.id, f"Turma {school_class.name} atualizada")
    return school_class

def change_class_status(school_class, status, user):
    old_status = school_class.status
    school_class.status = status
    db.session.commit()
    action = 'CLASS_ACTIVATED' if status == 'ativa' else 'CLASS_DEACTIVATED'
    log_action(action, 'school_classes', school_class.id, f"Status alterado de {old_status} para {status}")
    return school_class

def link_teacher_to_class(school_class, teacher_id, is_coordinator, user):
    link = ClassTeacher.query.filter_by(class_id=school_class.id, teacher_id=teacher_id).first()
    if not link:
        # Se is_coordinator, remove outros coordenadores
        if is_coordinator:
            ClassTeacher.query.filter_by(class_id=school_class.id, is_coordinator=True).update({'is_coordinator': False})
            
        link = ClassTeacher(class_id=school_class.id, teacher_id=teacher_id, is_coordinator=is_coordinator)
        db.session.add(link)
        db.session.commit()
        log_action('CLASS_TEACHER_LINKED', 'school_classes', school_class.id, f"Professor {teacher_id} vinculado")
    elif is_coordinator != link.is_coordinator:
        if is_coordinator:
            ClassTeacher.query.filter_by(class_id=school_class.id, is_coordinator=True).update({'is_coordinator': False})
        link.is_coordinator = is_coordinator
        db.session.commit()
        log_action('CLASS_COORDINATOR_CHANGED', 'school_classes', school_class.id, f"Professor {teacher_id} coordinator={is_coordinator}")
    return link

def unlink_teacher_from_class(school_class, teacher_id, user):
    link = ClassTeacher.query.filter_by(class_id=school_class.id, teacher_id=teacher_id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        log_action('CLASS_TEACHER_UNLINKED', 'school_classes', school_class.id, f"Professor {teacher_id} removido")
    return True

def link_subject_to_class(school_class, subject_id, workload, user):
    link = ClassSubject.query.filter_by(class_id=school_class.id, subject_id=subject_id).first()
    if not link:
        link = ClassSubject(class_id=school_class.id, subject_id=subject_id, workload=workload)
        db.session.add(link)
        db.session.commit()
        log_action('CLASS_SUBJECT_LINKED', 'school_classes', school_class.id, f"Disciplina {subject_id} vinculada")
    else:
        link.workload = workload
        db.session.commit()
    return link

def unlink_subject_from_class(school_class, subject_id, user):
    link = ClassSubject.query.filter_by(class_id=school_class.id, subject_id=subject_id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        log_action('CLASS_SUBJECT_UNLINKED', 'school_classes', school_class.id, f"Disciplina {subject_id} removida")
    return True
