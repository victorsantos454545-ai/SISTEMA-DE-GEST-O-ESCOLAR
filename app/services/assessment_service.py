from app.models import Assessment, Grade, SchoolClass, Subject, Teacher, Period, Enrollment
from app.extensions import db
from app.services.audit_service import log_action
from sqlalchemy.exc import SQLAlchemyError

def create_assessment(data):
    """Cria uma nova avaliação."""
    assessment = Assessment(**data)
    db.session.add(assessment)
    db.session.commit()
    log_action('create_assessment', entity='assessments', entity_id=assessment.id, description=f"Criou avaliação {assessment.title}")
    return assessment

def update_assessment(assessment, data):
    """Atualiza avaliação."""
    for key, value in data.items():
        if hasattr(assessment, key):
            setattr(assessment, key, value)
    db.session.commit()
    log_action('update_assessment', entity='assessments', entity_id=assessment.id, description=f"Atualizou avaliação {assessment.title}")
    return assessment

def archive_assessment(assessment):
    """Arquiva avaliação em vez de deletar."""
    assessment.status = 'arquivada'
    db.session.commit()
    log_action('archive_assessment', entity='assessments', entity_id=assessment.id, description=f"Arquivou avaliação {assessment.title}")
    return assessment

def can_teacher_manage_assessment(teacher_user, school_class_id, subject_id):
    """Verifica se o professor tem acesso à turma/disciplina."""
    if teacher_user.role.name in ['admin', 'secretaria']:
        return True
    
    teacher = Teacher.query.filter_by(user_id=teacher_user.id).first()
    if not teacher:
        return False
        
    has_any = teacher.class_links.first() is not None or teacher.schedules.first() is not None
    if not has_any:
        return True
        
    is_class_linked = teacher.class_links.filter_by(class_id=school_class_id).first() is not None
    if is_class_linked:
        return True
        
    from app.models import Schedule
    is_sched_linked = Schedule.query.filter_by(teacher_id=teacher.id, school_class_id=school_class_id).first() is not None
    if is_sched_linked:
        return True
        
    return False
