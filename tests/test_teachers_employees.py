import pytest
from datetime import date
from app.extensions import db
from app.models import User, Role, Teacher, Employee, Subject, SchoolClass, SchoolYear, ClassTeacher
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

def create_user_env(role_name, username):
    role = Role.query.filter_by(name=role_name).first()
    user = User(username=username, email=f"{username}@test.com", role_id=role.id)
    user.set_password('senha12345')
    db.session.add(user)
    db.session.commit()
    return user

def _login(client, username, password='senha12345'):
    return client.post('/login', data={'login': username, 'password': password}, follow_redirects=True)


class TestTeacherModule:
    def test_teacher_crud_admin(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_env('admin', 'admin_teacher')
            
        _login(client, 'admin_teacher')
        
        # Test Create (GET and POST)
        resp_get = client.get('/professores/novo')
        assert resp_get.status_code == 200
        
        resp_post = client.post('/professores/novo', data={
            'full_name': 'Prof Silva',
            'registration': 'MAT123',
            'status': 'ativo',
            'education': 'Mestrado'
        }, follow_redirects=True)
        
        assert b'Professor cadastrado com sucesso.' in resp_post.data
        
        # Test Edit
        with seeded_app.app_context():
            teacher = Teacher.query.filter_by(registration='MAT123').first()
            t_id = teacher.id
            
        resp_edit = client.post(f'/professores/{t_id}/editar', data={
            'full_name': 'Prof Silva Editado',
            'registration': 'MAT123',
            'status': 'inativo',
            'education': 'Doutorado'
        }, follow_redirects=True)
        
        assert b'Professor atualizado com sucesso' in resp_edit.data
        
        # Test Search
        resp_search = client.get('/professores/?q=Silva')
        assert b'Prof Silva Editado' in resp_search.data

    def test_teacher_custom_password_and_login(self, client, seeded_app):
        """Verifica se o admin pode escolher a senha do professor e ele consegue logar."""
        with seeded_app.app_context():
            create_user_env('admin', 'admin_pwd_test')
            
        _login(client, 'admin_pwd_test')
        
        # Cadastra professor com senha escolhida pelo admin
        resp = client.post('/professores/novo', data={
            'full_name': 'Professor Roberto Carlos',
            'registration': 'ROB123',
            'status': 'ativo',
            'username': 'roberto.carlos',
            'password': 'senhaEscolhidaPeloAdmin123',
            'confirm_password': 'senhaEscolhidaPeloAdmin123'
        }, follow_redirects=True)
        assert b'Professor cadastrado com sucesso.' in resp.data
        
        # Desloga admin
        client.get('/logout', follow_redirects=True)
        
        # Tenta logar com o novo professor usando a senha escolhida
        resp_login = _login(client, 'roberto.carlos', 'senhaEscolhidaPeloAdmin123')
        assert resp_login.status_code == 200
        # Verifica que o professor entrou na sessão autenticada
        with client.session_transaction() as sess:
            assert '_user_id' in sess
            
        with seeded_app.app_context():
            u = User.query.filter_by(username='roberto.carlos').first()
            assert u is not None
            assert u.role.name == 'professor'
            assert u.teacher_profile is not None
            assert u.teacher_profile.registration == 'ROB123'
            assert u.name == 'Professor Roberto Carlos'

    def test_teacher_subject_class_links(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_env('admin', 'admin_link')
            teacher = Teacher(full_name='Prof Link', registration='LNK01', status='ativo')
            subject = Subject(name='Matemática', code='MAT01', workload=40, status='ativa')
            sy = SchoolYear(year=2024, name='2024', start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), active=True)
            db.session.add_all([teacher, subject, sy])
            db.session.commit()
            
            sclass = SchoolClass(name='9A', school_year_id=sy.id, shift='Manhã', status='ativa')
            db.session.add(sclass)
            db.session.commit()
            
            t_id = teacher.id
            sub_id = subject.id
            c_id = sclass.id
            
        _login(client, 'admin_link')
        
        # Link Subject
        resp_sub = client.post(f'/professores/{t_id}/vincular-disciplina', data={'subject_id': sub_id}, follow_redirects=True)
        assert b'Disciplina vinculada com sucesso.' in resp_sub.data
        
        with seeded_app.app_context():
            t = Teacher.query.get(t_id)
            assert t.subjects.count() == 1
            
        # Link Class
        resp_cls = client.post(f'/professores/{t_id}/vincular-turma', data={'class_id': c_id, 'is_coordinator': 'y'}, follow_redirects=True)
        assert b'Turma vinculada' in resp_cls.data
        
        with seeded_app.app_context():
            t = Teacher.query.get(t_id)
            assert t.class_links.count() == 1
            assert t.class_links[0].is_coordinator is True
            
        # Unlink Subject
        resp_unsub = client.post(f'/professores/{t_id}/desvincular-disciplina/{sub_id}', follow_redirects=True)
        assert b'Disciplina desvinculada' in resp_unsub.data
        
        # Unlink Class
        resp_uncls = client.post(f'/professores/{t_id}/desvincular-turma/{c_id}', follow_redirects=True)
        assert b'Turma desvinculada' in resp_uncls.data


class TestEmployeeModule:
    def test_employee_crud_admin(self, client, seeded_app):
        with seeded_app.app_context():
            create_user_env('admin', 'admin_emp')
            
        _login(client, 'admin_emp')
        
        resp_post = client.post('/funcionarios/novo', data={
            'full_name': 'Func Oliveira',
            'registration': 'EMP123',
            'position': 'Secretário',
            'department': 'Administração',
            'status': 'ativo'
        }, follow_redirects=True)
        
        assert b'Funcion\xc3\xa1rio cadastrado com sucesso.' in resp_post.data or b'Funcionario cadastrado' in resp_post.data
        
        with seeded_app.app_context():
            emp = Employee.query.filter_by(registration='EMP123').first()
            e_id = emp.id
            
        # Edit
        client.post(f'/funcionarios/{e_id}/editar', data={
            'full_name': 'Func Oliveira Editado',
            'registration': 'EMP123',
            'position': 'Diretor',
            'department': 'Diretoria',
            'status': 'ativo'
        }, follow_redirects=True)
        
        with seeded_app.app_context():
            emp = Employee.query.get(e_id)
            assert emp.position == 'Diretor'
            
        # Deactivate
        client.post(f'/funcionarios/{e_id}/desativar', follow_redirects=True)
        with seeded_app.app_context():
            emp = Employee.query.get(e_id)
            assert emp.status == 'inativo'


class TestIsolation:
    def test_teacher_isolation(self, client, seeded_app):
        with seeded_app.app_context():
            u_t1 = create_user_env('professor', 'prof_a')
            u_t2 = create_user_env('professor', 'prof_b')
            
            t1 = Teacher(full_name='Prof A', registration='A1', user_id=u_t1.id)
            t2 = Teacher(full_name='Prof B', registration='B1', user_id=u_t2.id)
            db.session.add_all([t1, t2])
            db.session.commit()
            
            t1_id, t2_id = t1.id, t2.id
            
        _login(client, 'prof_a')
        
        # Pode ver próprio perfil
        assert client.get(f'/professores/{t1_id}').status_code == 200
        # Não pode ver perfil do outro professor
        assert client.get(f'/professores/{t2_id}').status_code == 403
