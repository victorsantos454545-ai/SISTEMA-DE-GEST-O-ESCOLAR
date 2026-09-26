from app.models import Activity, Teacher, SchoolClass, Subject, ClassTeacher
from app.extensions import db
from app.services.audit_service import log_action
from datetime import datetime

def check_teacher_authorization(teacher_id, school_class_id, subject_id):
    """
    Verifica se o professor pode criar atividade na combinação turma/disciplina.
    """
    if not teacher_id:
        return True
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return False
        
    has_any = teacher.class_links.first() is not None or teacher.schedules.first() is not None
    if not has_any:
        return True
        
    is_class_linked = teacher.class_links.filter_by(class_id=school_class_id).first() is not None
    if is_class_linked:
        return True
        
    from app.models import Schedule
    is_sched_linked = Schedule.query.filter_by(teacher_id=teacher_id, school_class_id=school_class_id).first() is not None
    if is_sched_linked:
        return True
        
    return False

def create_activity(data, user_id):
    """
    Cria uma nova atividade.
    """
    # Se teacher_id estiver presente nos dados (ex: admin enviando) usamos ele,
    # senão pegamos o id do próprio professor logado.
    teacher_id = data.get('teacher_id')
    
    if not check_teacher_authorization(teacher_id, data['school_class_id'], data['subject_id']):
        raise ValueError("Professor não autorizado para esta turma e disciplina.")
        
    activity = Activity(
        title=data['title'],
        description=data.get('description', ''),
        activity_type=data.get('activity_type', 'Outro'),
        subject_id=data['subject_id'],
        school_class_id=data['school_class_id'],
        teacher_id=teacher_id,
        published_at=data.get('published_at'),
        due_date=data.get('due_date'),
        status=data.get('status', 'rascunho')
    )
    
    db.session.add(activity)
    db.session.commit()
    
    log_action('create_activity', 'activities', activity.id, f"Atividade '{activity.title}' criada", user_id)
    return activity

def update_activity(activity_id, data, user_id):
    activity = Activity.query.get_or_404(activity_id)
    
    # Se tentar trocar disciplina/turma/professor, tem que validar
    t_id = data.get('teacher_id', activity.teacher_id)
    c_id = data.get('school_class_id', activity.school_class_id)
    s_id = data.get('subject_id', activity.subject_id)
    
    if not check_teacher_authorization(t_id, c_id, s_id):
        raise ValueError("Professor não autorizado para esta turma e disciplina.")
        
    activity.title = data.get('title', activity.title)
    activity.description = data.get('description', activity.description)
    activity.activity_type = data.get('activity_type', activity.activity_type)
    activity.subject_id = s_id
    activity.school_class_id = c_id
    activity.teacher_id = t_id
    activity.published_at = data.get('published_at', activity.published_at)
    activity.due_date = data.get('due_date', activity.due_date)
    
    # Atualiza o status se fornecido
    new_status = data.get('status')
    if new_status and new_status in Activity.STATUSES:
        activity.status = new_status
        
    db.session.commit()
    log_action('update_activity', 'activities', activity.id, f"Atividade atualizada", user_id)
    return activity

def change_activity_status(activity_id, new_status, user_id, reason=""):
    activity = Activity.query.get_or_404(activity_id)
    if new_status not in Activity.STATUSES:
        raise ValueError("Status inválido.")
        
    old_status = activity.status
    activity.status = new_status
    
    # Se for publicar agora, ajusta data
    if new_status == 'publicada' and old_status == 'rascunho':
        if not activity.published_at:
            activity.published_at = datetime.utcnow()
            
    db.session.commit()
    desc = f"Status alterado: {old_status} -> {new_status}"
    if reason:
        desc += f" | Motivo: {reason}"
    log_action('status_activity', 'activities', activity.id, desc, user_id)
    return activity

def delete_activity(activity_id, user_id):
    """
    Exclui atividade permanentemente (normalmente preferimos cancelar, 
    mas a permissão 'delete' exige essa capacidade).
    """
    activity = Activity.query.get_or_404(activity_id)
    title = activity.title
    db.session.delete(activity)
    db.session.commit()
    log_action('delete_activity', 'activities', activity_id, f"Atividade excluída: {title}", user_id)
    return True
