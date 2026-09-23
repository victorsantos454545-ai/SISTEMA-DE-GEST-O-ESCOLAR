"""Servico de permissoes e autorizacao por objeto."""
from app.models.student import Student
from app.models.guardian import Guardian
from app.models.teacher import Teacher
from app.models.school_class import SchoolClass
from app.models.enrollment import Enrollment
from app.models.class_teacher import ClassTeacher
from app.models.student_guardian import StudentGuardian


def can_access_student(user, student_id):
    """Verifica se o usuario pode acessar dados de um aluno.

    - Admin/Secretaria: acesso a todos
    - Professor: somente alunos de suas turmas
    - Responsavel: somente alunos vinculados
    - Aluno: somente a si mesmo
    """
    role = user.role.name

    if role in ('admin', 'secretaria'):
        return True

    if role == 'professor' and user.teacher_profile:
        teacher_class_ids = [
            ct.class_id for ct in
            ClassTeacher.query.filter_by(teacher_id=user.teacher_profile.id).all()
        ]
        enrolled = Enrollment.query.filter(
            Enrollment.school_class_id.in_(teacher_class_ids),
            Enrollment.student_id == student_id,
            Enrollment.status == 'ativa'
        ).first()
        return enrolled is not None

    if role == 'responsavel' and user.guardian_profile:
        link = StudentGuardian.query.filter_by(
            guardian_id=user.guardian_profile.id,
            student_id=student_id
        ).first()
        return link is not None

    if role == 'aluno' and user.student_profile:
        return user.student_profile.id == student_id

    return False


def can_access_class(user, class_id):
    """Verifica se o usuario pode acessar dados de uma turma.

    - Admin/Secretaria: acesso a todas
    - Professor: somente turmas atribuidas
    - Responsavel: turmas onde alunos vinculados estao matriculados
    - Aluno: turma onde esta matriculado
    """
    role = user.role.name

    if role in ('admin', 'secretaria'):
        return True

    if role == 'professor' and user.teacher_profile:
        return ClassTeacher.query.filter_by(
            teacher_id=user.teacher_profile.id,
            class_id=class_id
        ).first() is not None

    if role == 'responsavel' and user.guardian_profile:
        student_ids = [
            sg.student_id for sg in
            StudentGuardian.query.filter_by(guardian_id=user.guardian_profile.id).all()
        ]
        return Enrollment.query.filter(
            Enrollment.student_id.in_(student_ids),
            Enrollment.school_class_id == class_id,
            Enrollment.status == 'ativa'
        ).first() is not None

    if role == 'aluno' and user.student_profile:
        return Enrollment.query.filter_by(
            student_id=user.student_profile.id,
            school_class_id=class_id,
            status='ativa'
        ).first() is not None

    return False


def can_access_grade(user, grade):
    """Verifica se o usuario pode acessar uma nota."""
    role = user.role.name

    if role in ('admin', 'secretaria'):
        return True

    if role == 'professor' and user.teacher_profile:
        return grade.assessment.teacher_id == user.teacher_profile.id

    if role == 'responsavel' and user.guardian_profile:
        return can_access_student(user, grade.student_id)

    if role == 'aluno' and user.student_profile:
        return grade.student_id == user.student_profile.id

    return False


def can_access_attendance(user, attendance):
    """Verifica se o usuario pode acessar registro de frequencia."""
    role = user.role.name

    if role in ('admin', 'secretaria'):
        return True

    if role == 'professor' and user.teacher_profile:
        return attendance.teacher_id == user.teacher_profile.id

    if role == 'responsavel' and user.guardian_profile:
        return can_access_student(user, attendance.student_id)

    if role == 'aluno' and user.student_profile:
        return attendance.student_id == user.student_profile.id

    return False


def can_access_assessment(user, assessment):
    """Verifica se o usuario pode acessar uma avaliacao."""
    role = user.role.name

    if role in ('admin', 'secretaria'):
        return True

    if role == 'professor' and user.teacher_profile:
        return assessment.teacher_id == user.teacher_profile.id

    return can_access_class(user, assessment.school_class_id)


def can_access_activity(user, activity):
    """Verifica se o usuario pode acessar uma atividade."""
    role = user.role.name

    if role in ('admin', 'secretaria'):
        return True

    if role == 'professor' and user.teacher_profile:
        return activity.teacher_id == user.teacher_profile.id

    return can_access_class(user, activity.school_class_id)
