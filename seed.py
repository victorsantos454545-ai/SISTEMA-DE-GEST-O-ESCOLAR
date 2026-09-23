"""Script para popular o banco de dados com dados iniciais de desenvolvimento.

ATENÇÃO: Este script é apenas para ambiente de DESENVOLVIMENTO.
Não utilize em produção.

Uso:
    python seed.py
"""
import os
from datetime import date

from app import create_app
from app.extensions import db
from app.models import (
    Role, User, SchoolYear, Period, Subject, Teacher, Student,
    SchoolClass, ClassSubject, ClassTeacher, Enrollment, SystemConfig
)
from app.services.seed_service import seed_all_permissions


def seed_admin_user():
    """Cria o usuário administrador padrão."""
    admin_role = Role.query.filter_by(name='admin').first()

    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@escola.com',
            role_id=admin_role.id,
            active=True,
            must_change_password=False
        )
        # ATENÇÃO: Troque esta senha em produção!
        admin.set_password('admin12345')
        db.session.add(admin)
        db.session.commit()
        print('  [+] Usuário admin criado (senha: admin12345)')
        print('  [!] ATENÇÃO: Troque a senha em produção!')
        return 1

    print('  [=] Usuário admin já existe')
    return 0


def seed_school_year():
    """Cria ano letivo e períodos."""
    if not SchoolYear.query.filter_by(year=2026).first():
        sy = SchoolYear(
            year=2026,
            name='Ano Letivo 2026',
            start_date=date(2026, 2, 2),
            end_date=date(2026, 12, 18),
            active=True
        )
        db.session.add(sy)
        db.session.commit()

        periods_data = [
            (1, '1º Bimestre', date(2026, 2, 2), date(2026, 4, 30)),
            (2, '2º Bimestre', date(2026, 5, 1), date(2026, 7, 15)),
            (3, '3º Bimestre', date(2026, 8, 1), date(2026, 9, 30)),
            (4, '4º Bimestre', date(2026, 10, 1), date(2026, 12, 18)),
        ]

        for seq, name, start, end in periods_data:
            db.session.add(Period(
                school_year_id=sy.id, name=name,
                sequence=seq, start_date=start, end_date=end
            ))

        db.session.commit()
        print('  [+] Ano letivo 2026 criado com 4 bimestres')
        return 1

    print('  [=] Ano letivo 2026 já existe')
    return 0


def seed_subjects():
    """Cria disciplinas padrão."""
    subjects_data = [
        ('MAT', 'Matemática', 160),
        ('POR', 'Português', 160),
        ('HIS', 'História', 80),
        ('GEO', 'Geografia', 80),
        ('CIE', 'Ciências', 80),
        ('ING', 'Inglês', 80),
        ('EDF', 'Educação Física', 80),
        ('ART', 'Artes', 40),
    ]

    created = 0
    for code, name, workload in subjects_data:
        if not Subject.query.filter_by(code=code).first():
            db.session.add(Subject(name=name, code=code, workload=workload))
            created += 1
            print(f'  [+] Disciplina: {name} ({code})')

    db.session.commit()
    print(f'  Disciplinas criadas: {created}')
    return created


def seed_teachers():
    """Cria professores de exemplo com usuários vinculados."""
    professor_role = Role.query.filter_by(name='professor').first()

    teachers_data = [
        ('Maria Silva', '11111111111', 'PROF001', 'maria.silva@escola.com'),
        ('João Santos', '22222222222', 'PROF002', 'joao.santos@escola.com'),
        ('Ana Oliveira', '33333333333', 'PROF003', 'ana.oliveira@escola.com'),
        ('Carlos Pereira', '44444444444', 'PROF004', 'carlos.pereira@escola.com'),
    ]

    created = 0
    for name, cpf, reg, email in teachers_data:
        if not Teacher.query.filter_by(cpf=cpf).first():
            user = User(
                username=email.split('@')[0],
                email=email,
                role_id=professor_role.id,
                active=True,
                must_change_password=True
            )
            user.set_password('professor01')
            db.session.add(user)
            db.session.flush()

            teacher = Teacher(
                user_id=user.id, full_name=name, cpf=cpf,
                registration=reg, email=email,
                education='Licenciatura', status='ativo'
            )
            db.session.add(teacher)
            created += 1
            print(f'  [+] Professor: {name}')

    db.session.commit()
    print(f'  Professores criados: {created}')
    return created


def seed_classes():
    """Cria turmas de exemplo."""
    sy = SchoolYear.query.filter_by(year=2026).first()

    classes_data = [
        ('6º Ano A', '6º Ano', 'Manhã', 'Sala 101', 35),
        ('7º Ano A', '7º Ano', 'Manhã', 'Sala 102', 35),
        ('8º Ano A', '8º Ano', 'Tarde', 'Sala 201', 35),
        ('9º Ano A', '9º Ano', 'Tarde', 'Sala 202', 35),
    ]

    created = 0
    for name, grade, shift, room, capacity in classes_data:
        if not SchoolClass.query.filter_by(name=name, school_year_id=sy.id).first():
            sc = SchoolClass(
                name=name, school_year_id=sy.id, grade=grade,
                shift=shift, room=room, capacity=capacity, status='ativa'
            )
            db.session.add(sc)
            created += 1
            print(f'  [+] Turma: {name}')

    db.session.commit()

    # Associar disciplinas às turmas
    subjects = Subject.query.all()
    classes = SchoolClass.query.filter_by(school_year_id=sy.id).all()
    for sc in classes:
        for subj in subjects:
            if not ClassSubject.query.filter_by(class_id=sc.id, subject_id=subj.id).first():
                db.session.add(ClassSubject(class_id=sc.id, subject_id=subj.id))

    # Associar professores às turmas
    teachers = Teacher.query.limit(4).all()
    for i, sc in enumerate(classes):
        if teachers and not ClassTeacher.query.filter_by(class_id=sc.id).first():
            teacher = teachers[i % len(teachers)]
            db.session.add(ClassTeacher(
                class_id=sc.id, teacher_id=teacher.id, is_coordinator=True
            ))

    db.session.commit()
    print(f'  Turmas criadas: {created}')
    return created


def seed_students():
    """Cria alunos de exemplo com usuários vinculados."""
    aluno_role = Role.query.filter_by(name='aluno').first()

    students_data = [
        ('Pedro Henrique Costa', '55555555555', 'pedro.costa@escola.com'),
        ('Julia Fernandes Lima', '66666666666', 'julia.lima@escola.com'),
        ('Lucas Almeida Souza', '77777777777', 'lucas.souza@escola.com'),
        ('Isabela Rodrigues Martins', '88888888888', 'isabela.martins@escola.com'),
        ('Gabriel Nascimento Dias', '99999999999', 'gabriel.dias@escola.com'),
    ]

    created = 0
    for name, cpf, email in students_data:
        if not Student.query.filter_by(cpf=cpf).first():
            user = User(
                username=email.split('@')[0],
                email=email,
                role_id=aluno_role.id,
                active=True,
                must_change_password=True
            )
            user.set_password('estudante01')
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id, full_name=name,
                cpf=cpf, email=email, status='ativo'
            )
            db.session.add(student)
            created += 1
            print(f'  [+] Aluno: {name}')

    db.session.commit()

    # Matricular alunos na primeira turma
    sy = SchoolYear.query.filter_by(year=2026).first()
    first_class = SchoolClass.query.filter_by(school_year_id=sy.id).first()
    if first_class:
        students = Student.query.all()
        for student in students:
            if not Enrollment.query.filter_by(
                student_id=student.id, school_year_id=sy.id
            ).first():
                db.session.add(Enrollment(
                    student_id=student.id,
                    school_class_id=first_class.id,
                    school_year_id=sy.id,
                    enrollment_date=date.today(),
                    status='ativa'
                ))
        db.session.commit()
        print(f'  Alunos matriculados na turma {first_class.name}')

    print(f'  Alunos criados: {created}')
    return created


def seed_system_config():
    """Cria configurações iniciais do sistema."""
    configs = [
        ('media_minima', '6.0', 'Média mínima para aprovação'),
        ('frequencia_minima', '75', 'Frequência mínima (%) para aprovação'),
        ('qtd_periodos', '4', 'Quantidade de períodos (bimestres) no ano'),
        ('sistema_recuperacao', 'sim', 'Sistema de recuperação habilitado'),
        ('nota_maxima', '10.0', 'Nota máxima das avaliações'),
    ]

    created = 0
    for key, value, desc in configs:
        if not SystemConfig.query.filter_by(key=key).first():
            db.session.add(SystemConfig(key=key, value=value, description=desc))
            created += 1
            print(f'  [+] Config: {key} = {value}')

    db.session.commit()
    print(f'  Configurações criadas: {created}')
    return created


def seed_database():
    """Popula o banco de dados com dados de desenvolvimento."""
    print('=' * 60)
    print('SEED: Populando banco com dados de DESENVOLVIMENTO')
    print('ATENÇÃO: NÃO use em produção!')
    print('=' * 60)
    print()

    print('[1/8] Criando roles e permissoes...')
    seed_all_permissions()
    print()

    print('[2/8] Criando usuário admin...')
    seed_admin_user()
    print()

    print('[3/8] Criando ano letivo e períodos...')
    seed_school_year()
    print()

    print('[4/8] Criando disciplinas...')
    seed_subjects()
    print()

    print('[5/8] Criando professores...')
    seed_teachers()
    print()

    print('[6/8] Criando turmas...')
    seed_classes()
    print()

    print('[7/8] Criando alunos...')
    seed_students()
    print()

    print('[8/8] Criando configurações do sistema...')
    seed_system_config()
    print()

    print('=' * 60)
    print('Seed concluída com sucesso!')
    print()
    print('Credenciais de desenvolvimento:')
    print('  Admin:       admin / admin12345')
    print('  Professores: maria.silva / professor01 (e outros)')
    print('  Alunos:      pedro.costa / estudante01 (e outros)')
    print('=' * 60)


if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
    with app.app_context():
        seed_database()
