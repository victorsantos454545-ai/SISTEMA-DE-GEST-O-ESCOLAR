"""Testes da Fase 3 - Autenticação, Permissões, Usuários e Segurança."""

import pytest
from datetime import date, datetime, timezone, timedelta
from app.extensions import db
from app.models import (
    Role, User, Permission, Student, Guardian, StudentGuardian,
    Teacher, SchoolYear, SchoolClass, ClassTeacher, Enrollment,
    AuditLog, PasswordResetToken
)
from app.services.seed_service import seed_all_permissions
from app.services.permission_service import (
    can_access_student, can_access_class
)


@pytest.fixture
def seeded_app(app):
    """App com roles e permissões configuradas."""
    with app.app_context():
        seed_all_permissions()
    return app


@pytest.fixture
def admin_user(seeded_app):
    """Cria usuário admin."""
    with seeded_app.app_context():
        role = Role.query.filter_by(name='admin').first()
        user = User(username='admin_test', email='admin@test.com', role_id=role.id)
        user.set_password('admintest01')
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def teacher_user(seeded_app):
    """Cria usuário professor com perfil Teacher."""
    with seeded_app.app_context():
        role = Role.query.filter_by(name='professor').first()
        user = User(username='prof_test', email='prof@test.com', role_id=role.id)
        user.set_password('proftest0101')
        db.session.add(user)
        db.session.flush()

        teacher = Teacher(
            user_id=user.id, full_name='Prof Teste',
            cpf='99988877700', registration='PROFTE', status='ativo'
        )
        db.session.add(teacher)
        db.session.commit()
        return user.id


@pytest.fixture
def student_user(seeded_app):
    """Cria usuário aluno com perfil Student."""
    with seeded_app.app_context():
        role = Role.query.filter_by(name='aluno').first()
        user = User(username='aluno_test', email='aluno@test.com', role_id=role.id)
        user.set_password('alunotest01')
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id, full_name='Aluno Teste',
            cpf='11122233300', status='ativo'
        )
        db.session.add(student)
        db.session.commit()
        return user.id


def _login(client, username, password):
    """Helper para fazer login."""
    return client.post('/login', data={
        'login': username,
        'password': password
    }, follow_redirects=True)


# ============================================================
# TESTES DE LOGIN
# ============================================================

class TestLogin:
    def test_login_page_loads(self, client, seeded_app):
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Entrar' in response.data

    def test_login_correct(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            response = _login(client, 'admin_test', 'admintest01')
            assert response.status_code == 200
            assert b'Dashboard' in response.data

    def test_login_wrong_password(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            response = _login(client, 'admin_test', 'errada12345')
            assert b'invalidas' in response.data

    def test_login_nonexistent_user(self, client, seeded_app):
        with seeded_app.app_context():
            response = _login(client, 'inexistente', 'password123')
            assert b'invalidas' in response.data

    def test_login_deactivated_user(self, client, seeded_app):
        with seeded_app.app_context():
            role = Role.query.filter_by(name='admin').first()
            user = User(username='inactive_user', email='inactive@test.com', role_id=role.id, active=False)
            user.set_password('inativo12345')
            db.session.add(user)
            db.session.commit()

            response = _login(client, 'inactive_user', 'inativo12345')
            assert b'invalidas' in response.data

    def test_logout(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'admintest01')
            response = client.get('/logout', follow_redirects=True)
            assert b'Entrar' in response.data


# ============================================================
# TESTES DE SENHA
# ============================================================

class TestPassword:
    def test_password_hash(self, seeded_app):
        with seeded_app.app_context():
            role = Role.query.filter_by(name='admin').first()
            user = User(username='hash_test', email='hash@test.com', role_id=role.id)
            user.set_password('hashtest0101')
            assert user.password_hash != 'hashtest0101'
            assert user.check_password('hashtest0101') is True
            assert user.check_password('errada') is False

    def test_change_password(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'admintest01')
            response = client.post('/alterar-senha', data={
                'current_password': 'admintest01',
                'new_password': 'novasenha01',
                'confirm_password': 'novasenha01'
            }, follow_redirects=True)
            assert b'Senha alterada' in response.data

    def test_password_reset_token(self, seeded_app, admin_user):
        with seeded_app.app_context():
            user = db.session.get(User, admin_user)
            token = PasswordResetToken.create_for_user(user)
            assert token is not None

            # Verificar token válido
            reset = PasswordResetToken.verify_token(token)
            assert reset is not None
            assert reset.user_id == user.id

            # Usar token
            reset.invalidate()
            assert PasswordResetToken.verify_token(token) is None

    def test_expired_token(self, seeded_app, admin_user):
        with seeded_app.app_context():
            user = db.session.get(User, admin_user)
            token = PasswordResetToken.generate_token()
            reset = PasswordResetToken(
                user_id=user.id,
                token_hash=PasswordResetToken.hash_token(token),
                expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
            )
            db.session.add(reset)
            db.session.commit()

            assert PasswordResetToken.verify_token(token) is None


# ============================================================
# TESTES DE PERMISSÕES
# ============================================================

class TestPermissions:
    def test_admin_has_all_permissions(self, seeded_app, admin_user):
        with seeded_app.app_context():
            user = db.session.get(User, admin_user)
            assert user.has_permission('students.view') is True
            assert user.has_permission('users.manage') is True
            assert user.has_permission('settings.manage') is True

    def test_professor_permissions(self, seeded_app, teacher_user):
        with seeded_app.app_context():
            user = db.session.get(User, teacher_user)
            assert user.has_permission('grades.create') is True
            assert user.has_permission('attendance.create') is True
            assert user.has_permission('users.manage') is False
            assert user.has_permission('settings.manage') is False

    def test_aluno_permissions(self, seeded_app, student_user):
        with seeded_app.app_context():
            user = db.session.get(User, student_user)
            assert user.has_permission('grades.view') is True
            assert user.has_permission('grades.create') is False
            assert user.has_permission('users.view') is False


# ============================================================
# TESTES DE SEGURANÇA - ROTAS PROTEGIDAS
# ============================================================

class TestRouteSecurity:
    def test_protected_route_without_login(self, client, seeded_app):
        with seeded_app.app_context():
            response = client.get('/dashboard')
            assert response.status_code == 302  # Redirect to login

    def test_users_without_permission(self, client, student_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'aluno_test', 'alunotest01')
            response = client.get('/usuarios/')
            assert response.status_code == 403

    def test_users_with_permission(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'admintest01')
            response = client.get('/usuarios/')
            assert response.status_code == 200

    def test_csrf_on_login(self, app, seeded_app):
        """Verifica que CSRF está desabilitado em testes (WTF_CSRF_ENABLED=False)."""
        assert app.config['WTF_CSRF_ENABLED'] is False


# ============================================================
# TESTES DE ISOLAMENTO DE DADOS
# ============================================================

class TestDataIsolation:
    def test_student_cannot_access_other_student(self, seeded_app):
        with seeded_app.app_context():
            role = Role.query.filter_by(name='aluno').first()

            # Aluno A
            user_a = User(username='aluno_a', email='a@test.com', role_id=role.id)
            user_a.set_password('alunotest01')
            db.session.add(user_a)
            db.session.flush()
            student_a = Student(user_id=user_a.id, full_name='Aluno A', cpf='10000000001')
            db.session.add(student_a)

            # Aluno B
            user_b = User(username='aluno_b', email='b@test.com', role_id=role.id)
            user_b.set_password('alunotest01')
            db.session.add(user_b)
            db.session.flush()
            student_b = Student(user_id=user_b.id, full_name='Aluno B', cpf='10000000002')
            db.session.add(student_b)
            db.session.commit()

            # A não pode acessar B
            assert can_access_student(user_a, student_b.id) is False
            # A pode acessar A
            assert can_access_student(user_a, student_a.id) is True

    def test_teacher_can_only_access_own_classes(self, seeded_app):
        with seeded_app.app_context():
            role = Role.query.filter_by(name='professor').first()
            user = User(username='prof_iso', email='profiso@test.com', role_id=role.id)
            user.set_password('proftest0101')
            db.session.add(user)
            db.session.flush()

            teacher = Teacher(
                user_id=user.id, full_name='Prof Iso',
                cpf='50000000001', registration='PROISO', status='ativo'
            )
            db.session.add(teacher)

            sy = SchoolYear(year=2090, name='Test 2090', active=False)
            db.session.add(sy)
            db.session.flush()

            class_a = SchoolClass(name='Turma Iso A', school_year_id=sy.id, shift='Manhã')
            class_b = SchoolClass(name='Turma Iso B', school_year_id=sy.id, shift='Tarde')
            db.session.add_all([class_a, class_b])
            db.session.flush()

            # Prof atribuído apenas à turma A
            db.session.add(ClassTeacher(class_id=class_a.id, teacher_id=teacher.id))
            db.session.commit()

            assert can_access_class(user, class_a.id) is True
            assert can_access_class(user, class_b.id) is False

    def test_guardian_can_only_access_linked_students(self, seeded_app):
        with seeded_app.app_context():
            role_resp = Role.query.filter_by(name='responsavel').first()
            user = User(username='resp_iso', email='respiso@test.com', role_id=role_resp.id)
            user.set_password('resptest0101')
            db.session.add(user)
            db.session.flush()

            guardian = Guardian(
                user_id=user.id, full_name='Resp Iso',
                cpf='60000000001'
            )
            db.session.add(guardian)

            student_ok = Student(full_name='Aluno OK', cpf='60000000011')
            student_no = Student(full_name='Aluno NO', cpf='60000000012')
            db.session.add_all([student_ok, student_no])
            db.session.flush()

            # Vincular apenas student_ok
            db.session.add(StudentGuardian(
                student_id=student_ok.id,
                guardian_id=guardian.id,
                relationship='Pai'
            ))
            db.session.commit()

            assert can_access_student(user, student_ok.id) is True
            assert can_access_student(user, student_no.id) is False


# ============================================================
# TESTES DE AUDITORIA
# ============================================================

class TestAuditLog:
    def test_login_creates_audit(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'admintest01')
            log = AuditLog.query.filter_by(action='LOGIN').first()
            assert log is not None
            assert log.user_id == admin_user

    def test_failed_login_creates_audit(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'wrongpassword')
            log = AuditLog.query.filter_by(action='LOGIN_FAILED').first()
            assert log is not None

    def test_password_change_creates_audit(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'admintest01')
            client.post('/alterar-senha', data={
                'current_password': 'admintest01',
                'new_password': 'novasenha01',
                'confirm_password': 'novasenha01'
            }, follow_redirects=True)
            log = AuditLog.query.filter_by(action='PASSWORD_CHANGED').first()
            assert log is not None


# ============================================================
# TESTES DE USUÁRIOS (CRUD)
# ============================================================

class TestUserManagement:
    def test_create_user(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'admintest01')
            role = Role.query.filter_by(name='aluno').first()

            response = client.post('/usuarios/novo', data={
                'username': 'novo_aluno',
                'email': 'novo@test.com',
                'role_id': role.id,
                'password': 'novoaluno01',
                'confirm_password': 'novoaluno01',
                'active': True
            }, follow_redirects=True)
            assert b'criado com sucesso' in response.data

    def test_duplicate_username(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'admintest01')
            role = Role.query.filter_by(name='aluno').first()

            client.post('/usuarios/novo', data={
                'username': 'dup_user',
                'email': 'dup1@test.com',
                'role_id': role.id,
                'password': 'duplicado01',
                'confirm_password': 'duplicado01',
            }, follow_redirects=True)

            response = client.post('/usuarios/novo', data={
                'username': 'dup_user',
                'email': 'dup2@test.com',
                'role_id': role.id,
                'password': 'duplicado01',
                'confirm_password': 'duplicado01',
            }, follow_redirects=True)
            assert b'ja existe' in response.data

    def test_duplicate_email(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'admintest01')
            role = Role.query.filter_by(name='aluno').first()

            client.post('/usuarios/novo', data={
                'username': 'email_dup1',
                'email': 'dup_email@test.com',
                'role_id': role.id,
                'password': 'duplicado01',
                'confirm_password': 'duplicado01',
            }, follow_redirects=True)

            response = client.post('/usuarios/novo', data={
                'username': 'email_dup2',
                'email': 'dup_email@test.com',
                'role_id': role.id,
                'password': 'duplicado01',
                'confirm_password': 'duplicado01',
            }, follow_redirects=True)
            assert b'ja cadastrado' in response.data

    def test_deactivate_user(self, client, admin_user, seeded_app):
        with seeded_app.app_context():
            _login(client, 'admin_test', 'admintest01')
            role = Role.query.filter_by(name='aluno').first()

            user = User(username='to_deactivate', email='deact@test.com', role_id=role.id)
            user.set_password('deactivate01')
            db.session.add(user)
            db.session.commit()

            response = client.post(f'/usuarios/{user.id}/desativar', follow_redirects=True)
            assert b'desativado' in response.data

            updated = db.session.get(User, user.id)
            assert updated.active is False


# ============================================================
# TESTES BASICOS DA APP (mantidos da Fase 1/2)
# ============================================================

def test_app_creation(app):
    assert app is not None
    assert app.config['TESTING'] is True


def test_index_redirect(client, seeded_app):
    response = client.get('/')
    assert response.status_code == 302


def test_404_page(client, seeded_app):
    response = client.get('/pagina-que-nao-existe')
    assert response.status_code == 404
