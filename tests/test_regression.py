import pytest
from app.models import User, SchoolYear, SchoolClass, Subject, Period, Student, Enrollment, Assessment, Grade, Teacher, Attendance, ClassSubject
from datetime import date

def _login(client, username, password='password'):
    r = client.post('/login', data={'login': username, 'password': password}, follow_redirects=True)
    print('Login Status:', r.status_code, r.data)
    return r
    return client.post('/login', data={'login': username, 'password': password}, follow_redirects=True)

class TestRegression:
    def test_full_academic_workflow(self, client, seeded_app, admin_user):
        with seeded_app.app_context():
            db = seeded_app.extensions['sqlalchemy'].session
            user = User.query.get(admin_user)
            _login(client, user.username, 'admin123')
    
            year = SchoolYear(year=2030, name='Ano 2030', start_date=date(2030, 2, 1), end_date=date(2030, 12, 15), active=True)
            db.add(year)
            db.flush()
    
            period = Period(school_year_id=year.id, name='1 Bimestre', sequence=1, start_date=date(2030, 2, 1), end_date=date(2030, 4, 30))
            db.add(period)
    
            subj = Subject(name='Matematica Integrada', code='MATINT', status='ativa')
            db.add(subj)
            db.flush()
    
            cls = SchoolClass(name='Turma Regressao', school_year_id=year.id, shift='Manhã', status='ativa')
            db.add(cls)
            db.flush()
    
            student = Student(full_name='Aluno Regressao', cpf='99999999999', status='ativo')
            db.add(student)
            db.flush()
    
            enr = Enrollment(student_id=student.id, school_class_id=cls.id, school_year_id=year.id, enrollment_date=date.today(), status='ativa')
            db.add(enr)
            db.flush()
    
            teacher = Teacher(user_id=user.id, full_name='Professor X', cpf='555', status='ativo')
            db.add(teacher)
            db.flush()
            
            cs = ClassSubject(class_id=cls.id, subject_id=subj.id)
            db.add(cs)
            db.flush()
    
            asmnt = Assessment(school_class_id=cls.id, subject_id=subj.id, teacher_id=teacher.id, period_id=period.id, title='Prova 1', date=date.today(), max_value=10.0, weight=1.0)
            db.add(asmnt)
            db.flush()
    
            grade = Grade(student_id=student.id, assessment_id=asmnt.id, value=8.5)
            db.add(grade)
    
            att = Attendance(student_id=student.id, school_class_id=cls.id, subject_id=subj.id, date=date.today(), period=1, present=True)
            db.add(att)
    
            db.commit()
    
            _login(client, user.username, 'admin123')
            resp = client.get(f'/relatorios/boletim/{student.id}?year_id={year.id}')
            print(resp.headers.get('Location'))
            assert resp.status_code == 200
    
            html = resp.data.decode('utf-8')
            assert 'Aluno Regressao' in html
            assert 'Matematica Integrada' in html
