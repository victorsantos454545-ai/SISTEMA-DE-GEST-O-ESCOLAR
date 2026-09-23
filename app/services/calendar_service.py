from app.models import CalendarEvent, Assessment, Activity, Enrollment
from app.extensions import db
from datetime import datetime
from flask import url_for

def _get_color_by_type(event_type):
    colors = {
        'aula': '#3788d8',
        'prova': '#dc3545',
        'avaliacao': '#fd7e14',
        'reuniao': '#6f42c1',
        'evento': '#20c997',
        'feriado': '#d63384',
        'atividade': '#198754',
        'outro': '#6c757d'
    }
    return colors.get(event_type, '#6c757d')

def get_calendar_events_json(start_date, end_date, user, status_filter=None):
    """
    Constrói a lista de eventos no padrão do FullCalendar para o usuário e o período informado.
    """
    events = []
    
    # Base queries
    ce_query = CalendarEvent.query.filter(
        CalendarEvent.start_datetime >= start_date,
        CalendarEvent.start_datetime <= end_date
    )
    
    ass_query = Assessment.query.filter(
        Assessment.date >= start_date,
        Assessment.date <= end_date
    )
    
    act_query = Activity.query.filter(
        Activity.due_date >= start_date,
        Activity.due_date <= end_date
    )
    
    # 1. Filtros por status
    if status_filter:
        ce_query = ce_query.filter_by(status=status_filter)
        ass_query = ass_query.filter_by(status=status_filter)
        act_query = act_query.filter_by(status=status_filter)
    else:
        # Padrão: esconde rascunhos para aluno/responsável
        if user.role.name in ['aluno', 'responsavel']:
            ce_query = ce_query.filter(CalendarEvent.status.in_(['published', 'completed', 'cancelled']))
            ass_query = ass_query.filter(Assessment.status.in_(['publicada', 'encerrada', 'cancelada']))
            act_query = act_query.filter(Activity.status.in_(['publicada', 'encerrada', 'cancelada']))
            
    # 2. Filtrar o que o usuário pode ver
    if user.role.name == 'aluno':
        # Vê eventos gerais da escola (sem turma) + eventos da própria turma
        class_ids = [e.school_class_id for e in Enrollment.query.filter_by(student_id=user.profile.id, status='ativa').all()]
        ce_query = ce_query.filter(db.or_(CalendarEvent.school_class_id == None, CalendarEvent.school_class_id.in_(class_ids)))
        ass_query = ass_query.filter(Assessment.school_class_id.in_(class_ids))
        act_query = act_query.filter(Activity.school_class_id.in_(class_ids))
        
    elif user.role.name == 'responsavel':
        class_ids = []
        if user.profile:
            students = [sg.student for sg in user.profile.student_links if sg.student.status == 'ativo']
            s_ids = [s.id for s in students]
            enrollments = Enrollment.query.filter(Enrollment.student_id.in_(s_ids), Enrollment.status == 'ativa').all()
            class_ids = [e.school_class_id for e in enrollments]
        
        ce_query = ce_query.filter(db.or_(CalendarEvent.school_class_id == None, CalendarEvent.school_class_id.in_(class_ids)))
        ass_query = ass_query.filter(Assessment.school_class_id.in_(class_ids))
        act_query = act_query.filter(Activity.school_class_id.in_(class_ids))
        
    elif user.role.name == 'professor':
        # Vê geral e das turmas que leciona
        class_ids = [link.school_class_id for link in user.profile.subject_links] if user.profile else []
        ce_query = ce_query.filter(db.or_(CalendarEvent.school_class_id == None, CalendarEvent.school_class_id.in_(class_ids)))
        ass_query = ass_query.filter(Assessment.school_class_id.in_(class_ids))
        act_query = act_query.filter(Activity.school_class_id.in_(class_ids))
        
    # Adicionar CalendarEvents manuais
    for ce in ce_query.all():
        title = ce.title
        if ce.status == 'cancelled': title = f"[CANCELADO] {title}"
        
        events.append({
            'id': f"ce_{ce.id}",
            'title': title,
            'start': ce.start_datetime.isoformat(),
            'end': ce.end_datetime.isoformat() if ce.end_datetime else None,
            'allDay': ce.all_day,
            'color': _get_color_by_type(ce.event_type),
            'url': url_for('calendar.detail', id=ce.id),
            'extendedProps': {
                'type': ce.event_type,
                'location': ce.location,
                'status': ce.status
            }
        })
        
    # Adicionar Assessments (Avaliações da Fase 9)
    for ass in ass_query.all():
        title = f"Avaliação: {ass.title}"
        if ass.status == 'cancelada': title = f"[CANCELADA] {title}"
        
        events.append({
            'id': f"ass_{ass.id}",
            'title': f"{title} ({ass.school_class.name})",
            'start': ass.date.isoformat(),
            'allDay': True,  # Avaliações no modelo atual não tem hora
            'color': _get_color_by_type('avaliacao'),
            'url': url_for('assessments.detail', id=ass.id) if user.has_permission('assessments.view') else '#',
            'extendedProps': {
                'type': 'avaliacao',
                'status': ass.status
            }
        })
        
    # Adicionar Activities (Atividades da Fase 11)
    for act in act_query.all():
        title = f"Entrega: {act.title}"
        if act.status == 'cancelada': title = f"[CANCELADA] {title}"
        
        events.append({
            'id': f"act_{act.id}",
            'title': f"{title} ({act.school_class.name})",
            'start': act.due_date.isoformat(),
            'allDay': False,
            'color': _get_color_by_type('atividade'),
            'url': url_for('activities.detail', id=act.id) if user.has_permission('activities.view') else '#',
            'extendedProps': {
                'type': 'atividade',
                'status': act.status
            }
        })
        
    return events

def create_calendar_event(data, user_id):
    ce = CalendarEvent(
        title=data['title'],
        description=data.get('description', ''),
        event_type=data.get('event_type', 'evento'),
        start_datetime=data['start_datetime'],
        end_datetime=data.get('end_datetime'),
        all_day=data.get('all_day', False),
        location=data.get('location', ''),
        school_year_id=data.get('school_year_id'),
        school_class_id=data.get('school_class_id'),
        subject_id=data.get('subject_id'),
        status=data.get('status', 'draft'),
        created_by=user_id
    )
    
    if ce.end_datetime and ce.start_datetime > ce.end_datetime:
        raise ValueError("Data final não pode ser anterior à data inicial.")
        
    db.session.add(ce)
    db.session.commit()
    from app.services.audit_service import log_action
    log_action('create_calendar_event', 'calendar_events', ce.id, f"Evento criado: {ce.title}", user_id)
    return ce

def update_calendar_event(event_id, data, user_id):
    ce = CalendarEvent.query.get_or_404(event_id)
    
    ce.title = data.get('title', ce.title)
    ce.description = data.get('description', ce.description)
    ce.event_type = data.get('event_type', ce.event_type)
    ce.start_datetime = data.get('start_datetime', ce.start_datetime)
    ce.end_datetime = data.get('end_datetime', ce.end_datetime)
    ce.all_day = data.get('all_day', ce.all_day)
    ce.location = data.get('location', ce.location)
    ce.school_year_id = data.get('school_year_id', ce.school_year_id)
    ce.school_class_id = data.get('school_class_id', ce.school_class_id)
    ce.subject_id = data.get('subject_id', ce.subject_id)
    ce.status = data.get('status', ce.status)
    
    if ce.end_datetime and ce.start_datetime > ce.end_datetime:
        raise ValueError("Data final não pode ser anterior à data inicial.")
        
    db.session.commit()
    from app.services.audit_service import log_action
    log_action('update_calendar_event', 'calendar_events', ce.id, f"Evento atualizado", user_id)
    return ce
