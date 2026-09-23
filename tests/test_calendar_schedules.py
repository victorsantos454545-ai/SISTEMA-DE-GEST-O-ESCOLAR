import pytest
from app.models import CalendarEvent, Schedule, SchoolClass, Subject, Teacher, User
from app.extensions import db
from app.services.calendar_service import create_calendar_event, get_calendar_events_json
from app.services.schedule_service import create_schedule, _check_conflicts
from datetime import datetime, time

def test_create_calendar_event(app):
    with app.app_context():
        data = {
            'title': 'Feriado Nacional',
            'event_type': 'feriado',
            'start_datetime': datetime(2026, 9, 7, 0, 0),
            'all_day': True
        }
        ce = create_calendar_event(data, 1)
        assert ce.title == 'Feriado Nacional'
        assert ce.all_day is True

def test_calendar_event_invalid_dates(app):
    with app.app_context():
        data = {
            'title': 'Erro',
            'start_datetime': datetime(2026, 9, 10, 10, 0),
            'end_datetime': datetime(2026, 9, 9, 10, 0)
        }
        with pytest.raises(ValueError):
            create_calendar_event(data, 1)

def test_schedule_conflicts(app):
    with app.app_context():
        from app.models import SchoolYear
        from datetime import date
        # Setup basic entities directly since test DB might be empty
        sy = SchoolYear(name='2026', year='2026', start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
        db.session.add(sy)
        db.session.commit()
        
        cls = SchoolClass(name='Turma 1', grade='9º', shift='Manhã', status='ativa', school_year_id=sy.id)
        sub = Subject(name='Math', code='MAT')
        u = User(username='test', email='test@test.com', password_hash='test', role_id=1)
        db.session.add_all([cls, sub, u])
        db.session.commit()
        
        t = Teacher(full_name='Prof', email='prof@e.com', user_id=u.id)
        db.session.add(t)
        db.session.commit()
        
        cls_id = cls.id
        sub_id = sub.id
        t_id = t.id
        
        # Criar o primeiro
        data = {
            'school_class_id': cls_id,
            'subject_id': sub_id,
            'teacher_id': t_id,
            'day_of_week': 'Segunda-feira',
            'start_time': time(8, 0),
            'end_time': time(9, 0),
            'room': 'Sala 1'
        }
        sch = create_schedule(data, 1)
        
        # Testar conflito de professor
        data2 = {
            'school_class_id': cls_id,
            'subject_id': sub_id,
            'teacher_id': t_id,
            'day_of_week': 'Segunda-feira',
            'start_time': time(8, 30),
            'end_time': time(9, 30),
            'room': 'Sala 2'
        }
        with pytest.raises(ValueError) as exc:
            create_schedule(data2, 1)
            
        assert "Conflito detectado" in str(exc.value)
