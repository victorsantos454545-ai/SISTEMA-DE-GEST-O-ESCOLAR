from datetime import date
from sqlalchemy import or_
from app.extensions import db
from app.models import Enrollment, Student, SchoolClass, SchoolYear
from app.services.audit_service import log_action

def can_view_enrollment(user, enrollment=None):
    if user.role.name in ['admin', 'secretaria']:
        return True
    if user.role.name == 'professor' and enrollment:
        # Verifica se o professor dá aula na turma dessa matrícula
        return enrollment.school_class.teacher_links.filter_by(teacher_id=user.profile.id).first() is not None
    if user.role.name == 'responsavel' and enrollment:
        return enrollment.student in user.profile.students
    if user.role.name == 'aluno' and enrollment:
        return enrollment.student_id == user.profile.id
    return False

def can_create_enrollment(user):
    return user.role.name in ['admin', 'secretaria']

def can_edit_enrollment(user, enrollment=None):
    return user.role.name in ['admin', 'secretaria']

def can_transfer_enrollment(user):
    return user.role.name in ['admin', 'secretaria']

def can_cancel_enrollment(user):
    return user.role.name in ['admin', 'secretaria']

def can_complete_enrollment(user):
    return user.role.name in ['admin', 'secretaria']

def can_renew_enrollment(user):
    return user.role.name in ['admin', 'secretaria']

def get_enrollments(user, page=1, per_page=10, search='', status='', year_id='', class_id='', student_id=''):
    query = Enrollment.query.join(Student).join(SchoolClass)
    
    if user.role.name == 'professor':
        query = query.filter(SchoolClass.teacher_links.any(teacher_id=user.profile.id))
    elif user.role.name == 'responsavel':
        query = query.filter(Student.guardian_links.any(guardian_id=user.profile.id))
    elif user.role.name == 'aluno':
        query = query.filter(Enrollment.student_id == user.profile.id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(
            Student.full_name.ilike(search_term),
            Student.cpf.ilike(search_term),
            SchoolClass.name.ilike(search_term)
        ))
        if search.isdigit():
            query = query.filter(or_(Enrollment.id == int(search), query.whereclause))
            
    if status:
        query = query.filter(Enrollment.status == status)
    if year_id:
        query = query.filter(Enrollment.school_year_id == year_id)
    if class_id:
        query = query.filter(Enrollment.school_class_id == class_id)
    if student_id:
        query = query.filter(Enrollment.student_id == student_id)
        
    return query.order_by(Enrollment.enrollment_date.desc(), Enrollment.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

def check_existing_active_enrollment(student_id, school_year_id):
    """Verifica se o aluno já possui matrícula ativa no ano letivo fornecido."""
    return Enrollment.query.filter_by(
        student_id=student_id,
        school_year_id=school_year_id,
        status='ativa'
    ).first()

def check_class_capacity(school_class_id):
    """Verifica se há vagas na turma."""
    cls = SchoolClass.query.get(school_class_id)
    if not cls or not cls.capacity:
        return True, 0
    enrolled = cls.enrolled_count
    return enrolled < cls.capacity, cls.capacity - enrolled

def create_enrollment(data):
    """Cria a matrícula de fato."""
    enrollment = Enrollment(
        student_id=data['student_id'],
        school_class_id=data['school_class_id'],
        school_year_id=data['school_year_id'],
        enrollment_date=data.get('enrollment_date', date.today()),
        status=data.get('status', 'ativa'),
        notes=data.get('notes')
    )
    db.session.add(enrollment)
    db.session.commit()
    log_action('ENROLLMENT_CREATED', 'enrollments', enrollment.id, f"Matrícula criada para aluno {data['student_id']} na turma {data['school_class_id']}")
    return enrollment

def update_enrollment(enrollment, data):
    if 'enrollment_date' in data:
        enrollment.enrollment_date = data['enrollment_date']
    if 'status' in data:
        enrollment.status = data['status']
    if 'notes' in data:
        enrollment.notes = data['notes']
    db.session.commit()
    log_action('ENROLLMENT_UPDATED', 'enrollments', enrollment.id, f"Matrícula {enrollment.id} atualizada")
    return enrollment

def transfer_enrollment(enrollment, new_class_id, transfer_date, reason):
    """Transfere aluno fechando a matrícula atual e criando uma nova."""
    new_class = SchoolClass.query.get(new_class_id)
    
    # Atualiza a atual para transferida
    old_class_name = enrollment.school_class.name
    enrollment.status = 'transferida'
    if reason:
        if enrollment.notes:
            enrollment.notes += f"\n[Transferido em {transfer_date} para {new_class.name}]: {reason}"
        else:
            enrollment.notes = f"[Transferido em {transfer_date} para {new_class.name}]: {reason}"

    # Cria a nova matrícula na nova turma
    new_enrollment = Enrollment(
        student_id=enrollment.student_id,
        school_class_id=new_class_id,
        school_year_id=enrollment.school_year_id,
        enrollment_date=transfer_date,
        status='ativa',
        notes=f"Transferido da turma {old_class_name} em {transfer_date}. Motivo: {reason}"
    )
    db.session.add(new_enrollment)
    db.session.commit()
    log_action('ENROLLMENT_TRANSFERRED', 'enrollments', enrollment.id, f"Matrícula transferida para turma {new_class_id} (Nova matrícula: {new_enrollment.id})")
    return new_enrollment

def cancel_enrollment(enrollment, cancel_date, reason):
    enrollment.status = 'cancelada'
    if reason:
        if enrollment.notes:
            enrollment.notes += f"\n[Cancelado em {cancel_date}]: {reason}"
        else:
            enrollment.notes = f"[Cancelado em {cancel_date}]: {reason}"
    db.session.commit()
    log_action('ENROLLMENT_CANCELLED', 'enrollments', enrollment.id, f"Matrícula cancelada")
    return enrollment

def complete_enrollment(enrollment, complete_date, notes=None):
    enrollment.status = 'concluida'
    if notes:
        if enrollment.notes:
            enrollment.notes += f"\n[Concluído em {complete_date}]: {notes}"
        else:
            enrollment.notes = f"[Concluído em {complete_date}]: {notes}"
    db.session.commit()
    log_action('ENROLLMENT_COMPLETED', 'enrollments', enrollment.id, f"Matrícula concluída")
    return enrollment

def renew_enrollment(old_enrollment, new_class_id, new_year_id, renew_date, status='ativa', notes=None):
    """Cria nova matrícula baseado na anterior para um novo ano letivo."""
    new_enrollment = Enrollment(
        student_id=old_enrollment.student_id,
        school_class_id=new_class_id,
        school_year_id=new_year_id,
        enrollment_date=renew_date,
        status=status,
        notes=notes
    )
    db.session.add(new_enrollment)
    db.session.commit()
    log_action('ENROLLMENT_RENEWED', 'enrollments', new_enrollment.id, f"Matrícula renovada a partir da matrícula {old_enrollment.id}")
    return new_enrollment
