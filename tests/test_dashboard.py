"""Testes da Fase 4 - Dashboard e Permissões."""

import pytest
from app.extensions import db
from app.models import User, Role, Student, Teacher, Employee, Guardian, SchoolClass, Enrollment
from app.services.seed_service import seed_all_permissions


@pytest.fixture
def seeded_app(app):
    """Garante que as permissões e roles básicas existem."""
    with app.app_context():
        seed_all_permissions()
        
        # Cria as roles básicas se não existirem
        roles = ['admin', 'professor', 'secretaria', 'responsavel', 'aluno']
        for r_name in roles:
            if not Role.query.filter_by(name=r_name).first():
                r = Role(name=r_name, description=r_name)
                db.session.add(r)
        db.session.commit()
    return app


def create_user(role_name, username, password):
    role = Role.query.filter_by(name=role_name).first()
    user = User(username=username, email=f"{username}@test.com", role_id=role.id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def _login(client, username, password):
    return client.post('/login', data={'login': username, 'password': password}, follow_redirects=True)


class TestDashboardAccess:
    def test_unauthenticated_access(self, client, seeded_app):
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_admin_dashboard(self, client, seeded_app):
        with seeded_app.app_context():
            create_user('admin', 'admin_dash', 'senha12345')
            
        _login(client, 'admin_dash', 'senha12345')
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Vis\xc3\xa3o Geral da Escola' in response.data or b'Visao Geral da Escola' in response.data or b'Alunos por Turma' in response.data

    def test_teacher_dashboard(self, client, seeded_app):
        with seeded_app.app_context():
            user = create_user('professor', 'prof_dash', 'senha12345')
            teacher = Teacher(user_id=user.id, full_name='Professor Teste', cpf='00011122233', registration='T1')
            db.session.add(teacher)
            db.session.commit()
            
        _login(client, 'prof_dash', 'senha12345')
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Painel do Professor' in response.data or b'Minhas Turmas' in response.data

    def test_secretary_dashboard(self, client, seeded_app):
        with seeded_app.app_context():
            create_user('secretaria', 'sec_dash', 'senha12345')
            
        _login(client, 'sec_dash', 'senha12345')
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Painel da Secretaria' in response.data or b'Matr\xc3\xadculas Recentes' in response.data

    def test_guardian_dashboard(self, client, seeded_app):
        with seeded_app.app_context():
            user = create_user('responsavel', 'resp_dash', 'senha12345')
            guardian = Guardian(user_id=user.id, full_name='Responsavel Teste', cpf='11122233344')
            db.session.add(guardian)
            db.session.commit()
            
        _login(client, 'resp_dash', 'senha12345')
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Painel do Respons\xc3\xa1vel' in response.data or b'Painel do Responsavel' in response.data or b'Estudantes Vinculados' in response.data

    def test_student_dashboard(self, client, seeded_app):
        with seeded_app.app_context():
            user = create_user('aluno', 'aluno_dash', 'senha12345')
            student = Student(user_id=user.id, full_name='Aluno Teste', cpf='22233344455')
            db.session.add(student)
            db.session.commit()
            
        _login(client, 'aluno_dash', 'senha12345')
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Meu Painel Escolar' in response.data or b'Minha Frequ' in response.data


class TestDashboardDataIsolation:
    def test_admin_api_charts_access(self, client, seeded_app):
        with seeded_app.app_context():
            create_user('admin', 'admin_api', 'senha12345')
            create_user('aluno', 'aluno_api', 'senha12345')
            
        # Admin deve conseguir acessar
        _login(client, 'admin_api', 'senha12345')
        response = client.get('/dashboard/api/admin-charts')
        assert response.status_code == 200
        assert b'labels' in response.data
        
        # Aluno não deve conseguir acessar
        client.get('/logout')
        _login(client, 'aluno_api', 'senha12345')
        response = client.get('/dashboard/api/admin-charts')
        assert response.status_code == 403
