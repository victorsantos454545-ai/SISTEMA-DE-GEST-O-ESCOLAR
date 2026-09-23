from datetime import date, datetime, timedelta
from app.extensions import db
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.employee import Employee
from app.models.school_class import SchoolClass
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.assessment import Assessment
from app.models.activity import Activity
from app.models.calendar_event import CalendarEvent
from app.models.announcement import Announcement, AnnouncementRecipient
from app.models.attendance import Attendance
from app.models.schedule import Schedule
from app.models.student_guardian import StudentGuardian

def get_announcements_for_user(user, limit=5):
    """Busca os comunicados visíveis para o usuário atual delegando ao announcement_service."""
    from app.services.announcement_service import get_visible_announcements
    if not user.is_authenticated:
        return []
    return get_visible_announcements(user, limit=limit)


def get_upcoming_events(limit=5):
    """Eventos futuros."""
    now = datetime.now()
    return CalendarEvent.query.filter(
        CalendarEvent.start_datetime >= now
    ).order_by(CalendarEvent.start_datetime.asc()).limit(limit).all()


def get_admin_dashboard_data():
    """Dados agregados para o dashboard do administrador."""
    stats = {
        'total_students': Student.query.filter_by(status='ativo').count(),
        'total_teachers': Teacher.query.filter_by(status='ativo').count(),
        'total_employees': Employee.query.filter_by(status='ativo').count(),
        'total_classes': SchoolClass.query.filter_by(status='ativa').count(),
        'total_subjects': Subject.query.filter_by(status='ativa').count(),
        'active_enrollments': Enrollment.query.filter_by(status='ativa').count(),
        'pending_enrollments': Enrollment.query.filter_by(status='pendente').count()
    }

    # Proximas avaliações
    upcoming_assessments = Assessment.query.filter(
        Assessment.date >= date.today()
    ).order_by(Assessment.date.asc()).limit(5).all()
    
    # Alunos com baixa frequencia (placeholder para cálculo)
    # Precisaria calcular presenças/ausências. Por performance, limitaremos a 5 recentes.
    # Em um sistema real, poderia haver uma view materializada ou task de consolidação.
    low_attendance_students = []

    events = get_upcoming_events()

    return {
        'stats': stats,
        'upcoming_assessments': upcoming_assessments,
        'events': events,
        'low_attendance_students': low_attendance_students
    }


def get_secretary_dashboard_data():
    """Dados operacionais para a secretaria."""
    stats = {
        'total_students': Student.query.filter_by(status='ativo').count(),
        'active_enrollments': Enrollment.query.filter_by(status='ativa').count(),
        'pending_enrollments': Enrollment.query.filter_by(status='pendente').count(),
        'total_classes': SchoolClass.query.filter_by(status='ativa').count(),
    }

    recent_enrollments = Enrollment.query.order_by(Enrollment.enrollment_date.desc()).limit(5).all()
    events = get_upcoming_events()

    return {
        'stats': stats,
        'recent_enrollments': recent_enrollments,
        'events': events
    }


def get_teacher_dashboard_data(teacher_profile):
    """Dados das turmas e avaliações do professor."""
    if not teacher_profile:
        return {
            'stats': {'total_classes': 0, 'total_students': 0},
            'my_classes': [],
            'upcoming_assessments': [],
            'recent_activities': [],
            'todays_classes': []
        }
    
    teacher_id = teacher_profile.id

    from app.models.class_teacher import ClassTeacher
    
    # Minhas Turmas
    cts = ClassTeacher.query.filter_by(teacher_id=teacher_id).all()
    my_classes = [ct.school_class for ct in cts if ct.school_class.status == 'ativa']
    
    class_ids = [c.id for c in my_classes]
    
    # Total de alunos únicos nas turmas do professor (ativas)
    students_count = 0
    if class_ids:
        students_count = db.session.query(Enrollment.student_id).filter(
            Enrollment.school_class_id.in_(class_ids),
            Enrollment.status == 'ativa'
        ).distinct().count()

    stats = {
        'total_classes': len(my_classes),
        'total_students': students_count
    }

    # Proximas avaliações criadas por este professor
    upcoming_assessments = Assessment.query.filter(
        Assessment.teacher_id == teacher_id,
        Assessment.date >= date.today()
    ).order_by(Assessment.date.asc()).limit(5).all()

    # Atividades recentes do professor
    recent_activities = Activity.query.filter(
        Activity.teacher_id == teacher_id
    ).order_by(Activity.created_at.desc()).limit(5).all()
    
    # Aulas de hoje
    today_num = date.today().weekday() + 1 # 1=Segunda, 7=Domingo
    # Se quiser mapear string
    weekday_map = {1: 'Segunda-feira', 2: 'Terça-feira', 3: 'Quarta-feira', 4: 'Quinta-feira', 5: 'Sexta-feira', 6: 'Sábado', 7: 'Domingo'}
    day_str = weekday_map.get(today_num, 'Segunda-feira')
    
    todays_classes = Schedule.query.filter(
        Schedule.teacher_id == teacher_id,
        Schedule.day_of_week == day_str
    ).order_by(Schedule.start_time.asc()).all()

    return {
        'stats': stats,
        'my_classes': my_classes,
        'upcoming_assessments': upcoming_assessments,
        'recent_activities': recent_activities,
        'todays_classes': todays_classes
    }


def get_guardian_dashboard_data(guardian_profile):
    """Dados dos alunos vinculados ao responsável."""
    if not guardian_profile:
        return {'students': [], 'upcoming_assessments': [], 'recent_activities': []}

    sgs = StudentGuardian.query.filter_by(guardian_id=guardian_profile.id).all()
    students = [sg.student for sg in sgs if sg.student.status == 'ativo']
    student_ids = [s.id for s in students]
    
    if not student_ids:
         return {'students': [], 'upcoming_assessments': [], 'recent_activities': []}

    # Turmas atuais dos alunos
    enrollments = Enrollment.query.filter(
        Enrollment.student_id.in_(student_ids),
        Enrollment.status == 'ativa'
    ).all()
    
    class_ids = [e.school_class_id for e in enrollments]

    # Proximas avaliações das turmas dos alunos
    upcoming_assessments = []
    recent_activities = []
    
    if class_ids:
        upcoming_assessments = Assessment.query.filter(
            Assessment.school_class_id.in_(class_ids),
            Assessment.date >= date.today()
        ).order_by(Assessment.date.asc()).limit(10).all()
        
        recent_activities = Activity.query.filter(
            Activity.school_class_id.in_(class_ids),
            Activity.status == 'publicada'
        ).order_by(Activity.due_date.desc()).limit(10).all()

    return {
        'students': students,
        'upcoming_assessments': upcoming_assessments,
        'recent_activities': recent_activities
    }


def get_student_dashboard_data(student_profile):
    """Dados das turmas e notas do aluno."""
    if not student_profile:
        return {
            'my_classes': [],
            'upcoming_assessments': [],
            'recent_activities': [],
            'todays_classes': [],
            'frequency': {
                'total': 0,
                'presents': 0,
                'absences': 0,
                'percent': 0
            }
        }
        
    student_id = student_profile.id
    
    enrollments = Enrollment.query.filter_by(student_id=student_id, status='ativa').all()
    class_ids = [e.school_class_id for e in enrollments]
    
    upcoming_assessments = []
    recent_activities = []
    todays_classes = []
    
    if class_ids:
        upcoming_assessments = Assessment.query.filter(
            Assessment.school_class_id.in_(class_ids),
            Assessment.date >= date.today()
        ).order_by(Assessment.date.asc()).limit(5).all()
        
        recent_activities = Activity.query.filter(
            Activity.school_class_id.in_(class_ids),
            Activity.status == 'publicada'
        ).order_by(Activity.due_date.asc()).limit(5).all()
        
        today_num = date.today().weekday() + 1
        weekday_map = {1: 'Segunda-feira', 2: 'Terça-feira', 3: 'Quarta-feira', 4: 'Quinta-feira', 5: 'Sexta-feira', 6: 'Sábado', 7: 'Domingo'}
        day_str = weekday_map.get(today_num, 'Segunda-feira')
        
        todays_classes = Schedule.query.filter(
            Schedule.school_class_id.in_(class_ids),
            Schedule.day_of_week == day_str
        ).order_by(Schedule.start_time.asc()).all()

    # Buscar frequencia agregada
    # Conta total de dias/aulas registradas vs. presenças
    total_attendances = Attendance.query.filter_by(student_id=student_id).count()
    total_presents = Attendance.query.filter_by(student_id=student_id, present=True).count()
    
    freq_percent = 100
    if total_attendances > 0:
        freq_percent = round((total_presents / total_attendances) * 100, 1)

    return {
        'my_classes': [e.school_class for e in enrollments],
        'upcoming_assessments': upcoming_assessments,
        'recent_activities': recent_activities,
        'todays_classes': todays_classes,
        'frequency': {
            'total': total_attendances,
            'presents': total_presents,
            'absences': total_attendances - total_presents,
            'percent': freq_percent
        }
    }
