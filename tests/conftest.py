import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """Cria instância da aplicação para testes."""
    app = create_app('testing')

    with app.app_context():
        _db.create_all()

    yield app

    with app.app_context():
        _db.drop_all()


@pytest.fixture(autouse=True)
def cleanup(app):
    """Limpa dados do banco entre cada teste para evitar conflitos."""
    yield
    with app.app_context():
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope='function')
def client(app):
    """Cliente de teste do Flask."""
    return app.test_client()

from app.models import Role, User, Student, Teacher, Guardian
from app.services.seed_service import seed_all_permissions

@pytest.fixture
def seeded_app(app):
    with app.app_context():
        seed_all_permissions()
    return app

@pytest.fixture
def admin_user(seeded_app):
    with seeded_app.app_context():
        role = Role.query.filter_by(name='admin').first()
        user = User(username='admin_reports', email='admin_rep@test.com', role_id=role.id)
        user.set_password('admin123')
        _db.session.add(user)
        _db.session.commit()
        return user.id

@pytest.fixture
def student_user(seeded_app):
    with seeded_app.app_context():
        role = Role.query.filter_by(name='aluno').first()
        user = User(username='student_reports', email='stu_rep@test.com', role_id=role.id)
        user.set_password('student123')
        _db.session.add(user)
        _db.session.flush()
        student = Student(user_id=user.id, full_name='Student Test', cpf='11122233344')
        _db.session.add(student)
        _db.session.commit()
        return user.id
