"""Testes da Fase 5 - Alunos e Responsáveis."""

import pytest
from datetime import date
from app.extensions import db
from app.models import User, Role, Student, Guardian, StudentGuardian, Enrollment, SchoolClass, SchoolYear
from app.services.seed_service import seed_all_permissions

@pytest.fixture
def seeded_app(app):
    with app.app_context():
        seed_all_permissions()
        roles = ['admin', 'professor', 'secretaria', 'responsavel', 'aluno']
        for r_name in roles:
            if not Role.query.filter_by(name=r_name).first():
                r = Role(name=r_name, description=r_name)
                db.session.add(r)
        db.session.commit()
    return app

def create_user_student_env(role_name, username):
    role = Role.query.filter_by(name=role_name).first()
    user = User(username=username, email=f"{username}@test.com", role_id=role.id)
    user.set_password('senha12345')
    db.session.add(user)
    db.session.commit()
    return user

def _login(client, username, password='senha12345'):
    return client.post('/login', data={'login': username, 'password': password}, follow_redirects=True)

class TestStudentModule:
    def test_student_crud_admin(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_student_env('admin', 'admin_stud')
            
        _login(client, 'admin_stud')
        
        # Test Create (GET e POST)
        resp_get = client.get('/alunos/novo')
        assert resp_get.status_code == 200
        
        resp_post = client.post('/alunos/novo', data={
            'full_name': 'João Silva',
            'birth_date': '2012-05-10',
            'status': 'ativo',
            'cpf': '111.222.333-44'
        }, follow_redirects=True)
        
        assert b'Aluno cadastrado com sucesso.' in resp_post.data
        
        # Test Edit
        with seeded_app.app_context():
            student = Student.query.filter_by(full_name='João Silva').first()
            assert student.cpf == '11122233344'  # normalizado
            s_id = student.id
            
        resp_edit = client.post(f'/alunos/{s_id}/editar', data={
            'full_name': 'João Silva Editado',
            'birth_date': '2012-05-10',
            'status': 'ativo',
            'cpf': '11122233344'
        }, follow_redirects=True)
        
        assert b'Aluno atualizado com sucesso' in resp_edit.data
        
        # Test List & Search
        resp_list = client.get('/alunos/?q=Silva')
        assert b'Jo\xc3\xa3o Silva Editado' in resp_list.data or b'Joao Silva Editado' in resp_list.data or b'Silva Editado' in resp_list.data

    def test_student_deactivate_activate(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_student_env('admin', 'admin_stud_status')
            student = Student(full_name='Maria Inativa', birth_date=date(2010, 1, 1), status='ativo')
            db.session.add(student)
            db.session.commit()
            s_id = student.id
            
        _login(client, 'admin_stud_status')
        
        # Desativar (POST)
        client.post(f'/alunos/{s_id}/desativar', follow_redirects=True)
        with seeded_app.app_context():
            assert Student.query.get(s_id).status == 'inativo'
            
        # Ativar (POST)
        client.post(f'/alunos/{s_id}/ativar', follow_redirects=True)
        with seeded_app.app_context():
            assert Student.query.get(s_id).status == 'ativo'

class TestStudentGuardianRelationship:
    def test_link_guardian(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_student_env('admin', 'admin_link')
            s = Student(full_name='Aluno Link', birth_date=date(2010, 1, 1))
            g1 = Guardian(full_name='Pai', phone='1111')
            g2 = Guardian(full_name='Mãe', phone='2222')
            db.session.add_all([s, g1, g2])
            db.session.commit()
            s_id, g1_id, g2_id = s.id, g1.id, g2.id
            
        _login(client, 'admin_link')
        
        # Vincular g1 como principal
        client.post(f'/alunos/{s_id}/vincular-responsavel', data={
            'guardian_id': g1_id,
            'relationship': 'Pai',
            'is_primary': 'y'
        }, follow_redirects=True)
        
        with seeded_app.app_context():
            link = StudentGuardian.query.filter_by(student_id=s_id, guardian_id=g1_id).first()
            assert link is not None
            assert link.is_primary is True
            
        # Vincular g2 como principal (deve desmarcar g1)
        client.post(f'/alunos/{s_id}/vincular-responsavel', data={
            'guardian_id': g2_id,
            'relationship': 'Mãe',
            'is_primary': 'y'
        }, follow_redirects=True)
        
        with seeded_app.app_context():
            assert StudentGuardian.query.filter_by(student_id=s_id, guardian_id=g1_id).first().is_primary is False
            assert StudentGuardian.query.filter_by(student_id=s_id, guardian_id=g2_id).first().is_primary is True

        # Trocar principal manualmente
        client.post(f'/alunos/{s_id}/responsavel-principal/{g1_id}', follow_redirects=True)
        with seeded_app.app_context():
            assert StudentGuardian.query.filter_by(student_id=s_id, guardian_id=g1_id).first().is_primary is True

        # Desvincular
        client.post(f'/alunos/{s_id}/desvincular-responsavel/{g2_id}', follow_redirects=True)
        with seeded_app.app_context():
            assert StudentGuardian.query.filter_by(student_id=s_id, guardian_id=g2_id).first() is None
            
class TestDataIsolation:
    def test_student_isolation(self, client, seeded_app):
        with seeded_app.app_context():
            # Cria 2 alunos e seus usuários
            u_a = create_user_student_env('aluno', 'aluno_a')
            u_b = create_user_student_env('aluno', 'aluno_b')
            s_a = Student(full_name='Aluno A', birth_date=date(2010, 1, 1), user_id=u_a.id)
            s_b = Student(full_name='Aluno B', birth_date=date(2010, 1, 1), user_id=u_b.id)
            db.session.add_all([s_a, s_b])
            db.session.commit()
            sa_id, sb_id = s_a.id, s_b.id
            
        _login(client, 'aluno_a')
        
        # Aluno A acessa a si mesmo
        resp = client.get(f'/alunos/{sa_id}')
        assert resp.status_code == 200
        
        # Aluno A não pode acessar B
        resp2 = client.get(f'/alunos/{sb_id}')
        assert resp2.status_code == 403

    def test_guardian_isolation(self, client, seeded_app):
        with seeded_app.app_context():
            u_resp = create_user_student_env('responsavel', 'resp_a')
            s1 = Student(full_name='Filho A', birth_date=date(2010, 1, 1))
            s2 = Student(full_name='Filho B', birth_date=date(2010, 1, 1))
            g = Guardian(full_name='Resp A', phone='1', user_id=u_resp.id)
            db.session.add_all([s1, s2, g])
            db.session.commit()
            sg = StudentGuardian(student_id=s1.id, guardian_id=g.id, relationship='Pai')
            db.session.add(sg)
            db.session.commit()
            s1_id, s2_id, g_id = s1.id, s2.id, g.id
            
        _login(client, 'resp_a')
        
        # Pode acessar o filho
        assert client.get(f'/alunos/{s1_id}').status_code == 200
        # Não pode acessar outro aluno
        assert client.get(f'/alunos/{s2_id}').status_code == 403
        
        # Pode ver próprio perfil
        assert client.get(f'/responsaveis/{g_id}').status_code == 200
