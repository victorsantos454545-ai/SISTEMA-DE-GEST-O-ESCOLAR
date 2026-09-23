import pytest
from datetime import date, timedelta
from app.models import Enrollment, Student, SchoolClass, SchoolYear, User, Role
from app.services.enrollment_service import (
    create_enrollment, transfer_enrollment, cancel_enrollment, 
    complete_enrollment, renew_enrollment, check_class_capacity,
    check_existing_active_enrollment
)
from app.extensions import db
from app.services.seed_service import seed_all_permissions

@pytest.fixture
def basic_data(app):
    with app.app_context():
        seed_all_permissions()
        roles = ['admin', 'professor', 'secretaria', 'responsavel', 'aluno']
        for r_name in roles:
            if not Role.query.filter_by(name=r_name).first():
                r = Role(name=r_name, description=r_name)
                db.session.add(r)
        
        # Ano letivo 1 e 2
        sy1 = SchoolYear(year=2026, name="2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), active=True)
        sy2 = SchoolYear(year=2027, name="2027", start_date=date(2027, 1, 1), end_date=date(2027, 12, 31), active=False)
        db.session.add_all([sy1, sy2])
        db.session.commit()
        
        # Turmas
        c1 = SchoolClass(name="9º A", school_year_id=sy1.id, shift="Manhã", capacity=2)
        c2 = SchoolClass(name="9º B", school_year_id=sy1.id, shift="Manhã", capacity=40)
        c3 = SchoolClass(name="1º Ano", school_year_id=sy2.id, shift="Manhã", capacity=40)
        db.session.add_all([c1, c2, c3])
        
        # Alunos
        s1 = Student(full_name="Aluno 1", cpf="11111111111", status="ativo")
        s2 = Student(full_name="Aluno 2", cpf="22222222222", status="ativo")
        s3 = Student(full_name="Aluno 3", cpf="33333333333", status="ativo")
        db.session.add_all([s1, s2, s3])
        db.session.commit()
        
        return {
            'sy1': sy1.id, 'sy2': sy2.id,
            'c1': c1.id, 'c2': c2.id, 'c3': c3.id,
            's1': s1.id, 's2': s2.id, 's3': s3.id
        }

def create_user_env(role_name, username):
    role = Role.query.filter_by(name=role_name).first()
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, email=f"{username}@test.com", role_id=role.id)
        user.set_password('senha12345')
        db.session.add(user)
        db.session.commit()
    return user

def _login(client, username, password='senha12345'):
    return client.post('/login', data={'login': username, 'password': password}, follow_redirects=True)

class TestEnrollmentService:
    def test_create_enrollment_capacity(self, app, basic_data):
        with app.app_context():
            # A turma c1 tem capacidade 2
            has_cap, av = check_class_capacity(basic_data['c1'])
            assert has_cap is True
            assert av == 2
            
            e1 = create_enrollment({
                'student_id': basic_data['s1'],
                'school_class_id': basic_data['c1'],
                'school_year_id': basic_data['sy1'],
                'status': 'ativa'
            })
            assert e1.id is not None
            
            has_cap, av = check_class_capacity(basic_data['c1'])
            assert av == 1
            
            e2 = create_enrollment({
                'student_id': basic_data['s2'],
                'school_class_id': basic_data['c1'],
                'school_year_id': basic_data['sy1'],
                'status': 'ativa'
            })
            
            has_cap, av = check_class_capacity(basic_data['c1'])
            assert has_cap is False
            assert av == 0
            
            assert check_existing_active_enrollment(basic_data['s1'], basic_data['sy1']) is not None

    def test_transfer_enrollment(self, app, basic_data):
        with app.app_context():
            e1 = create_enrollment({
                'student_id': basic_data['s1'],
                'school_class_id': basic_data['c1'],
                'school_year_id': basic_data['sy1'],
                'status': 'ativa'
            })
            
            old_id = e1.id
            t_date = date.today()
            
            new_e = transfer_enrollment(e1, basic_data['c2'], t_date, "Mudança de turno")
            
            old_e = Enrollment.query.get(old_id)
            assert old_e.status == 'transferida'
            assert "Mudança de turno" in old_e.notes
            
            assert new_e.status == 'ativa'
            assert new_e.school_class_id == basic_data['c2']
            assert new_e.student_id == basic_data['s1']

    def test_renew_enrollment(self, app, basic_data):
        with app.app_context():
            e1 = create_enrollment({
                'student_id': basic_data['s1'],
                'school_class_id': basic_data['c1'],
                'school_year_id': basic_data['sy1'],
                'status': 'concluida'
            })
            
            r_date = date(2027, 1, 10)
            
            new_e = renew_enrollment(e1, basic_data['c3'], basic_data['sy2'], r_date, 'ativa')
            
            old_e = Enrollment.query.get(e1.id)
            assert old_e.status == 'concluida'
            
            assert new_e.status == 'ativa'
            assert new_e.school_year_id == basic_data['sy2']
            assert new_e.school_class_id == basic_data['c3']
            assert new_e.enrollment_date == r_date

    def test_cancel_complete(self, app, basic_data):
        with app.app_context():
            e1 = create_enrollment({
                'student_id': basic_data['s1'],
                'school_class_id': basic_data['c1'],
                'school_year_id': basic_data['sy1'],
                'status': 'ativa'
            })
            
            cancel_enrollment(e1, date.today(), "Desistência")
            assert e1.status == 'cancelada'
            
            e2 = create_enrollment({
                'student_id': basic_data['s2'],
                'school_class_id': basic_data['c1'],
                'school_year_id': basic_data['sy1'],
                'status': 'ativa'
            })
            
            complete_enrollment(e2, date.today(), "Aprovado direto")
            assert e2.status == 'concluida'

class TestEnrollmentsUI:
    def test_enrollment_list_admin(self, client, basic_data):
        with client.application.app_context():
            create_user_env('admin', 'admin_enr')
            create_enrollment({
                'student_id': basic_data['s1'],
                'school_class_id': basic_data['c1'],
                'school_year_id': basic_data['sy1'],
                'status': 'ativa'
            })
            
        _login(client, 'admin_enr')
        response = client.get('/matriculas/')
        assert response.status_code == 200
        assert b"Aluno 1" in response.data
        assert b"Ativa" in response.data
        assert b"9\xc2\xba A" in response.data

    def test_create_enrollment_ui(self, client, basic_data):
        with client.application.app_context():
            create_user_env('admin', 'admin_enr2')
            
        _login(client, 'admin_enr2')
        
        response = client.post('/matriculas/nova', data={
            'student_id': basic_data['s3'],
            'school_year_id': basic_data['sy1'],
            'school_class_id': basic_data['c2'],
            'enrollment_date': '2026-02-01',
            'status': 'ativa'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Matr\xc3\xadcula efetuada com sucesso" in response.data
        
        with client.application.app_context():
            e = Enrollment.query.filter_by(student_id=basic_data['s3']).first()
            assert e is not None
            assert e.status == 'ativa'
            
    def test_teacher_cannot_create_enrollment(self, client, basic_data):
        with client.application.app_context():
            create_user_env('professor', 'prof_enr')
            
        _login(client, 'prof_enr')
        response = client.get('/matriculas/nova')
        assert response.status_code == 403
