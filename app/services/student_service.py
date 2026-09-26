"""Serviços para Gestão de Alunos."""
import re
from datetime import date
from flask import current_app
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models.student import Student
from app.services.audit_service import log_action

def can_view_student(user, student):
    """Verifica se o usuário pode visualizar o aluno."""
    if user.role.name in ['admin', 'secretaria']:
        return True
    
    if user.role.name == 'aluno':
        return getattr(user.student_profile, 'id', None) == student.id
        
    if user.role.name == 'responsavel':
        guardian_id = getattr(user.guardian_profile, 'id', None)
        if not guardian_id:
            return False
        return any(g.id == guardian_id for g in student.guardians)
        
    if user.role.name == 'professor':
        teacher_id = getattr(user.teacher_profile, 'id', None)
        if not teacher_id:
            return False
        # Verifica se o aluno está em alguma turma do professor
        from app.models.class_teacher import ClassTeacher
        from app.models.enrollment import Enrollment
        
        teacher_classes = ClassTeacher.query.filter_by(teacher_id=teacher_id).all()
        class_ids = [tc.class_id for tc in teacher_classes]
        if not class_ids:
            return False
        
        enrollment = Enrollment.query.filter(
            Enrollment.student_id == student.id,
            Enrollment.school_class_id.in_(class_ids)
        ).first()
        return enrollment is not None

    return False

def can_edit_student(user, student):
    """Verifica se o usuário pode editar o aluno."""
    return user.role.name in ['admin', 'secretaria']

def can_manage_guardians(user):
    """Verifica se o usuário pode gerenciar responsáveis do aluno."""
    return user.role.name in ['admin', 'secretaria']

def search_students(query=None, status=None, class_id=None, page=1, per_page=20):
    """Realiza busca e paginação de alunos."""
    base_query = Student.query
    
    if query:
        search_term = f"%{query}%"
        # Trata query apenas numerico para CPF
        numeric_query = re.sub(r'[^0-9]', '', query)
        if numeric_query:
            base_query = base_query.filter(or_(
                Student.full_name.ilike(search_term),
                Student.social_name.ilike(search_term),
                Student.cpf.ilike(f"%{numeric_query}%")
            ))
        else:
            base_query = base_query.filter(or_(
                Student.full_name.ilike(search_term),
                Student.social_name.ilike(search_term)
            ))
            
    if status:
        base_query = base_query.filter_by(status=status)
        
    if class_id:
        from app.models.enrollment import Enrollment
        base_query = base_query.join(Enrollment).filter(Enrollment.school_class_id == class_id)
        
    # Ordenação padrão por nome
    base_query = base_query.order_by(Student.full_name.asc())
    
    return base_query.paginate(page=page, per_page=per_page, error_out=False)

def create_student(data, user_id):
    """Cria um novo aluno."""
    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    student = Student(**data)
    db.session.add(student)
    db.session.commit()
    
    log_action('STUDENT_CREATED', entity='student', entity_id=student.id, description=f'Criou aluno ID {student.id}')
    return student

def update_student(student, data, user_id):
    """Atualiza um aluno existente."""
    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    for key, value in data.items():
        if hasattr(student, key):
            setattr(student, key, value)
            
    db.session.commit()
    log_action('STUDENT_UPDATED', entity='student', entity_id=student.id, description=f'Atualizou aluno ID {student.id}')
    return student

def deactivate_student(student, user_id):
    """Desativa um aluno."""
    student.status = 'inativo'
    db.session.commit()
    log_action('STUDENT_DEACTIVATED', entity='student', entity_id=student.id, description=f'Desativou aluno ID {student.id}')
    return student

def activate_student(student, user_id):
    """Reativa um aluno."""
    student.status = 'ativo'
    db.session.commit()
    log_action('STUDENT_ACTIVATED', entity='student', entity_id=student.id, description=f'Ativou aluno ID {student.id}')
    return student

def get_student_history(student):
    """Retorna o histórico do aluno consolidado."""
    from app.models.enrollment import Enrollment
    from app.models.attendance import Attendance
    from app.models.assessment import Assessment
    
    enrollments = Enrollment.query.filter_by(student_id=student.id).order_by(Enrollment.enrollment_date.desc()).all()
    
    # Cálculos acadêmicos
    total_attendances = Attendance.query.filter_by(student_id=student.id).count()
    total_presents = Attendance.query.filter_by(student_id=student.id, present=True).count()
    freq_percent = round((total_presents / total_attendances) * 100, 1) if total_attendances > 0 else 0
    
    return {
        'enrollments': enrollments,
        'frequency': {
            'total': total_attendances,
            'presents': total_presents,
            'percent': freq_percent
        },
        'avg_grade': 'N/A',  # Será implementado na fase 8 (Notas)
    }
