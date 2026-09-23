from app.models import Schedule, Teacher, SchoolClass
from app.extensions import db
from app.services.audit_service import log_action

def _check_conflicts(teacher_id, school_class_id, room, day_of_week, start_time, end_time, exclude_id=None):
    """
    Verifica conflitos de professor, turma ou sala no mesmo horário.
    """
    query = Schedule.query.filter_by(day_of_week=day_of_week)
    if exclude_id:
        query = query.filter(Schedule.id != exclude_id)
        
    schedules_on_day = query.all()
    
    for sch in schedules_on_day:
        # Check time overlap
        # Overlap happens if: start < sch.end and end > sch.start
        if start_time < sch.end_time and end_time > sch.start_time:
            if sch.teacher_id == teacher_id:
                return f"Professor {sch.teacher.full_name} já possui aula na Turma {sch.school_class.name} neste horário."
            if sch.school_class_id == school_class_id:
                return f"A Turma {sch.school_class.name} já possui aula de {sch.subject.name} neste horário."
            if room and sch.room == room:
                return f"A sala {room} já está ocupada pela Turma {sch.school_class.name}."
    return None

def create_schedule(data, user_id):
    if data['start_time'] >= data['end_time']:
        raise ValueError("Horário inicial não pode ser maior ou igual ao final.")
        
    conflict = _check_conflicts(
        data['teacher_id'], data['school_class_id'], data.get('room'),
        data['day_of_week'], data['start_time'], data['end_time']
    )
    if conflict:
        log_action('schedule_conflict', 'schedules', 0, f"Tentativa falha: {conflict}", user_id)
        raise ValueError(f"Conflito detectado: {conflict}")
        
    sch = Schedule(
        school_class_id=data['school_class_id'],
        subject_id=data['subject_id'],
        teacher_id=data['teacher_id'],
        day_of_week=data['day_of_week'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        room=data.get('room')
    )
    db.session.add(sch)
    db.session.commit()
    log_action('create_schedule', 'schedules', sch.id, "Horário criado", user_id)
    return sch

def update_schedule(schedule_id, data, user_id):
    sch = Schedule.query.get_or_404(schedule_id)
    
    start_time = data.get('start_time', sch.start_time)
    end_time = data.get('end_time', sch.end_time)
    if start_time >= end_time:
        raise ValueError("Horário inicial não pode ser maior ou igual ao final.")
        
    conflict = _check_conflicts(
        data.get('teacher_id', sch.teacher_id), 
        data.get('school_class_id', sch.school_class_id), 
        data.get('room', sch.room),
        data.get('day_of_week', sch.day_of_week), 
        start_time, end_time, 
        exclude_id=sch.id
    )
    if conflict:
        log_action('schedule_conflict', 'schedules', sch.id, f"Tentativa falha update: {conflict}", user_id)
        raise ValueError(f"Conflito detectado: {conflict}")
        
    sch.school_class_id = data.get('school_class_id', sch.school_class_id)
    sch.subject_id = data.get('subject_id', sch.subject_id)
    sch.teacher_id = data.get('teacher_id', sch.teacher_id)
    sch.day_of_week = data.get('day_of_week', sch.day_of_week)
    sch.start_time = start_time
    sch.end_time = end_time
    sch.room = data.get('room', sch.room)
    
    db.session.commit()
    log_action('update_schedule', 'schedules', sch.id, "Horário atualizado", user_id)
    return sch

def delete_schedule(schedule_id, user_id):
    sch = Schedule.query.get_or_404(schedule_id)
    db.session.delete(sch)
    db.session.commit()
    log_action('delete_schedule', 'schedules', schedule_id, "Horário excluído", user_id)
    return True
