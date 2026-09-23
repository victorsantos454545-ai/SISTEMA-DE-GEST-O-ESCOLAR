import pytest
from datetime import date
from app.extensions import db
from app.models import User, Role, SchoolClass, Subject, SchoolYear, Teacher, ClassTeacher, ClassSubject
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
        
        # Criando o ano letivo para as turmas
        if not SchoolYear.query.filter_by(year=2024).first():
            sy = SchoolYear(year=2024, name="2024", start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), active=True)
            db.session.add(sy)
            
        db.session.commit()
    return app

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

class TestClassModule:
    def test_class_crud_admin(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_env('admin', 'admin_class')
            sy = SchoolYear.query.filter_by(year=2024).first()
            sy_id = sy.id
            
        _login(client, 'admin_class')
        
        # Test Create
        resp_post = client.post('/turmas/novo', data={
            'name': '9A',
            'school_year_id': sy_id,
            'grade': '9º Ano',
            'shift': 'Manhã',
            'room': 'Sala 1',
            'capacity': 30,
            'status': 'ativa'
        }, follow_redirects=True)
        assert b'Turma cadastrada com sucesso' in resp_post.data or b'9A' in resp_post.data
        
        with seeded_app.app_context():
            cls = SchoolClass.query.filter_by(name='9A').first()
            assert cls is not None
            c_id = cls.id
            
        # Test Edit
        resp_edit = client.post(f'/turmas/{c_id}/editar', data={
            'name': '9A Editada',
            'school_year_id': sy_id,
            'grade': '9º Ano',
            'shift': 'Manhã',
            'room': 'Sala 1',
            'capacity': 35,
            'status': 'ativa'
        }, follow_redirects=True)
        assert b'Turma atualizada com sucesso' in resp_edit.data or b'9A Editada' in resp_edit.data
        
        # Test Deactivate
        resp_deact = client.post(f'/turmas/{c_id}/desativar', follow_redirects=True)
        with seeded_app.app_context():
            cls = SchoolClass.query.get(c_id)
            assert cls.status == 'inativa'
            
    def test_class_teacher_coordinator(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_env('admin', 'admin_coord')
            sy = SchoolYear.query.filter_by(year=2024).first()
            cls = SchoolClass(name='10A', school_year_id=sy.id, shift='Manhã', status='ativa')
            t1 = Teacher(full_name='Prof 1', registration='P1')
            t2 = Teacher(full_name='Prof 2', registration='P2')
            db.session.add_all([cls, t1, t2])
            db.session.commit()
            
            c_id, t1_id, t2_id = cls.id, t1.id, t2.id
            
        _login(client, 'admin_coord')
        
        # Vincula T1 como coordenador
        client.post(f'/turmas/{c_id}/vincular-professor', data={'teacher_id': t1_id, 'is_coordinator': 'y'}, follow_redirects=True)
        with seeded_app.app_context():
            link = ClassTeacher.query.filter_by(class_id=c_id, teacher_id=t1_id).first()
            assert link.is_coordinator is True
            
        # Vincula T2 como coordenador, deve remover de T1
        client.post(f'/turmas/{c_id}/vincular-professor', data={'teacher_id': t2_id, 'is_coordinator': 'y'}, follow_redirects=True)
        with seeded_app.app_context():
            link1 = ClassTeacher.query.filter_by(class_id=c_id, teacher_id=t1_id).first()
            link2 = ClassTeacher.query.filter_by(class_id=c_id, teacher_id=t2_id).first()
            assert link1.is_coordinator is False
            assert link2.is_coordinator is True

class TestSubjectModule:
    def test_subject_crud(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_env('admin', 'admin_subj')
            
        _login(client, 'admin_subj')
        
        # Test Create
        resp_post = client.post('/disciplinas/novo', data={
            'name': 'Física',
            'code': 'FIS01',
            'workload': 80,
            'status': 'ativa'
        }, follow_redirects=True)
        
        with seeded_app.app_context():
            s = Subject.query.filter_by(code='FIS01').first()
            assert s is not None
            s_id = s.id
            
        # Test Edit
        client.post(f'/disciplinas/{s_id}/editar', data={
            'name': 'Física Avançada',
            'code': 'FIS01',
            'workload': 100,
            'status': 'ativa'
        }, follow_redirects=True)
        
        with seeded_app.app_context():
            s = Subject.query.get(s_id)
            assert s.name == 'Física Avançada'
            assert s.workload == 100
            
    def test_subject_duplicate_code(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_env('admin', 'admin_dup')
            s1 = Subject(name='Química', code='QUI01')
            db.session.add(s1)
            db.session.commit()
            
        _login(client, 'admin_dup')
        resp = client.post('/disciplinas/novo', data={
            'name': 'Outra Química',
            'code': 'QUI01',
            'workload': 80,
            'status': 'ativa'
        }, follow_redirects=True)
        assert b'j\xc3\xa1 est\xc3\xa1 em uso' in resp.data

class TestPermissions:
    def test_professor_cannot_edit_class(self, client, seeded_app):
        with seeded_app.app_context():
            u_prof = create_user_env('professor', 'prof_access')
            sy = SchoolYear.query.filter_by(year=2024).first()
            cls = SchoolClass(name='11A', school_year_id=sy.id, shift='Manhã', status='ativa')
            prof = Teacher(full_name='Prof Access', registration='PA', user_id=u_prof.id)
            db.session.add_all([cls, prof])
            db.session.commit()
            
            # Vincular professor
            link = ClassTeacher(class_id=cls.id, teacher_id=prof.id)
            db.session.add(link)
            db.session.commit()
            c_id = cls.id
            
        _login(client, 'prof_access')
        
        # Pode visualizar
        assert client.get(f'/turmas/{c_id}').status_code == 200
        # Não pode editar
        assert client.get(f'/turmas/{c_id}/editar').status_code == 403
