import pytest
from app.services.attendance_service import calculate_student_attendance, process_attendance_batch
from app.models import Attendance, SystemConfig, Teacher, Student, Guardian, SchoolClass, SchoolYear, Subject, Enrollment, Role, User
from app.extensions import db
from datetime import date

def test_calculate_attendance_empty(app):
    """Testa estatísticas de um aluno sem registros."""
    with app.app_context():
        stats = calculate_student_attendance(999, 999)
        assert stats['total'] == 0
        assert stats['percentage'] == 100.0
        assert stats['status'] == 'Sem dados suficientes'

def test_attendance_service_import(app):
    """Testa se o service não quebra imports."""
    assert process_attendance_batch is not None

def test_model_name_properties(app):
    """Garante que Teacher, Student e Guardian possuem a propriedade .name."""
    with app.app_context():
        t = Teacher(full_name='Prof. Carlos Silva')
        s = Student(full_name='Lucas Almeida')
        s_social = Student(full_name='Lucas Almeida', social_name='Lukinhas')
        g = Guardian(full_name='Maria Responsavel')
        
        assert t.name == 'Prof. Carlos Silva'
        assert s.name == 'Lucas Almeida'
        assert s_social.name == 'Lukinhas'
        assert g.name == 'Maria Responsavel'

def test_batch_attendance_flow(app, seeded_app):
    """Testa o processamento de presença em lote com e sem professor vinculado."""
    with seeded_app.app_context():
        sy = SchoolYear(year=2026, name='Ano Letivo 2026', start_date=date(2026, 2, 1), end_date=date(2026, 12, 15), active=True)
        db.session.add(sy)
        db.session.flush()

        sc = SchoolClass(name='9º Ano B', school_year_id=sy.id, shift='Manhã', status='ativa')
        sub = Subject(name='História', code='HIST9')
        db.session.add_all([sc, sub])
        db.session.flush()

        st = Student(full_name='Aluno Teste Presença', cpf='11122233344')
        db.session.add(st)
        db.session.flush()

        enr = Enrollment(student_id=st.id, school_class_id=sc.id, school_year_id=sy.id, enrollment_date=date(2026, 2, 1), status='ativa')
        db.session.add(enr)
        db.session.commit()

        # Chamada sem professor (feita por admin sem professor atribuído)
        data = {str(st.id): {'status': 'presente', 'justification': ''}}
        success, count = process_attendance_batch(None, sc.id, sub.id, '2026-03-10', '1ª Aula', data)
        assert success is True
        assert count == 1

        rec = Attendance.query.filter_by(student_id=st.id, school_class_id=sc.id, subject_id=sub.id).first()
        assert rec is not None
        assert rec.present is True
        assert rec.teacher_id is None

        # Atualização para ausente com justificativa
        data_update = {str(st.id): {'status': 'justificado', 'justification': 'Consulta médica'}}
        success, count = process_attendance_batch(None, sc.id, sub.id, '2026-03-10', '1ª Aula', data_update)
        assert success is True
        assert count == 1

        rec_updated = Attendance.query.filter_by(student_id=st.id, school_class_id=sc.id, subject_id=sub.id).first()
        assert rec_updated.present is False
        assert rec_updated.justification == 'Consulta médica'
