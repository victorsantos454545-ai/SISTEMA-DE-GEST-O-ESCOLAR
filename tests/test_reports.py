import pytest
from app.models import User, Student

def _login(client, username, password='password'):
    return client.post('/login', data={'login': username, 'password': password}, follow_redirects=True)

class TestReports:
    def test_reports_index_access_admin(self, client, seeded_app, admin_user):
        with seeded_app.app_context():
            user = User.query.get(admin_user)
            _login(client, user.username, 'admin123')
            response = client.get('/relatorios/')
            assert response.status_code == 200
            assert b'Central de' in response.data

    def test_students_report_export_csv(self, client, seeded_app, admin_user):
        with seeded_app.app_context():
            user = User.query.get(admin_user)
            _login(client, user.username, 'admin123')
            response = client.get('/relatorios/alunos?export=csv')
            assert response.status_code == 200
            assert response.mimetype == 'text/csv'
            assert b'Nome Completo' in response.data

    def test_student_cannot_access_others_report_card(self, client, seeded_app, student_user):
        with seeded_app.app_context():
            # Create a second student
            user_b = User(username='student_b', email='b@test.com', role_id=4) # Assuming 4 is aluno
            user_b.set_password('123')
            seeded_app.extensions['sqlalchemy'].session.add(user_b)
            seeded_app.extensions['sqlalchemy'].session.flush()
            student_b = Student(user_id=user_b.id, full_name='Student B', cpf='000')
            seeded_app.extensions['sqlalchemy'].session.add(student_b)
            seeded_app.extensions['sqlalchemy'].session.commit()
            
            b_id = student_b.id
            user = User.query.get(student_user)
            
            _login(client, user.username, 'student123')
            # Attempt to access student_b report card
            response = client.get(f'/relatorios/boletim/{b_id}', follow_redirects=True)
            assert response.status_code == 200
            assert b'Acesso negado' in response.data # Checked via flash message
