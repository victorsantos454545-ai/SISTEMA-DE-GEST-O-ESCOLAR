from sqlalchemy import or_
from app.extensions import db
from app.models.teacher import Teacher
from app.models.class_teacher import ClassTeacher
from app.models.user import User
from app.models.role import Role
from app.services.audit_service import log_action
import re

def can_view_teacher(user, teacher):
    if user.role.name in ['admin', 'secretaria']:
        return True
    if user.role.name == 'professor':
        return getattr(user.teacher_profile, 'id', None) == teacher.id
    return False

def can_edit_teacher(user, teacher):
    return user.role.name in ['admin', 'secretaria']

def can_manage_teacher_classes(user):
    return user.role.name in ['admin', 'secretaria']

def can_manage_teacher_subjects(user):
    return user.role.name in ['admin', 'secretaria']

def search_teachers(query=None, status=None, page=1, per_page=20):
    base_query = Teacher.query
    
    if query:
        search_term = f"%{query}%"
        numeric_query = re.sub(r'[^0-9]', '', query)
        
        if numeric_query:
            base_query = base_query.filter(or_(
                Teacher.full_name.ilike(search_term),
                Teacher.email.ilike(search_term),
                Teacher.cpf.ilike(f"%{numeric_query}%"),
                Teacher.registration.ilike(f"%{numeric_query}%")
            ))
        else:
            base_query = base_query.filter(or_(
                Teacher.full_name.ilike(search_term),
                Teacher.email.ilike(search_term),
                Teacher.registration.ilike(search_term)
            ))
            
    if status:
        base_query = base_query.filter_by(status=status)
            
    base_query = base_query.order_by(Teacher.full_name.asc())
    return base_query.paginate(page=page, per_page=per_page, error_out=False)

def _generate_teacher_username(full_name, email):
    """Gera um nome de usuário único para o professor."""
    if email and '@' in email:
        base = email.split('@')[0].strip().lower()
    else:
        parts = [p.lower() for p in re.findall(r'[a-zA-Z0-9]+', full_name)]
        if len(parts) >= 2:
            base = f"{parts[0]}.{parts[-1]}"
        elif parts:
            base = parts[0]
        else:
            base = "professor"
    
    base = re.sub(r'[^a-z0-9_.]', '', base) or 'professor'
    username = base
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f"{base}{counter}"
        counter += 1
    return username

def create_teacher(data):
    username = data.pop('username', None)
    password = data.pop('password', None)
    data.pop('confirm_password', None)

    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    # 1. Localizar ou obter o papel de professor
    role_prof = Role.query.filter_by(name='professor').first()
    if not role_prof:
        from app.services.seed_service import seed_roles
        seed_roles()
        role_prof = Role.query.filter_by(name='professor').first()

    # 2. Criar conta de usuário de acesso
    email = data.get('email')
    if not username:
        username = _generate_teacher_username(data.get('full_name', ''), email)

    if not password:
        password = 'professor01'

    user = User(
        username=username,
        email=email or f"{username}@escola.local",
        role_id=role_prof.id if role_prof else 1,
        active=(data.get('status', 'ativo') == 'ativo'),
        must_change_password=False
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # 3. Criar professor associado
    teacher = Teacher(**data)
    teacher.user_id = user.id
    db.session.add(teacher)
    db.session.commit()
    
    log_action('TEACHER_CREATED', entity='teacher', entity_id=teacher.id, description=f'Criou professor {teacher.full_name} com usuário {user.username}')
    return teacher

def update_teacher(teacher, data):
    username = data.pop('username', None)
    password = data.pop('password', None)
    data.pop('confirm_password', None)

    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    # Atualiza conta de usuário se já existir
    if teacher.user:
        if username and username != teacher.user.username:
            teacher.user.username = username
        if data.get('email'):
            teacher.user.email = data['email']
        if password:
            teacher.user.set_password(password)
        if 'status' in data:
            teacher.user.active = (data['status'] == 'ativo')
    elif password or username:
        # Se for um professor legado sem usuário, cria a conta agora
        role_prof = Role.query.filter_by(name='professor').first()
        if not username:
            username = _generate_teacher_username(teacher.full_name, data.get('email', teacher.email))
        new_user = User(
            username=username,
            email=data.get('email', teacher.email) or f"{username}@escola.local",
            role_id=role_prof.id if role_prof else 1,
            active=(data.get('status', teacher.status) == 'ativo'),
            must_change_password=False
        )
        new_user.set_password(password or 'professor01')
        db.session.add(new_user)
        db.session.flush()
        teacher.user_id = new_user.id

    for key, value in data.items():
        if hasattr(teacher, key):
            setattr(teacher, key, value)
            
    db.session.commit()
    log_action('TEACHER_UPDATED', entity='teacher', entity_id=teacher.id, description=f'Atualizou professor ID {teacher.id}')
    return teacher

def deactivate_teacher(teacher):
    teacher.status = 'inativo'
    if teacher.user:
        teacher.user.active = False
    db.session.commit()
    log_action('TEACHER_DEACTIVATED', entity='teacher', entity_id=teacher.id, description=f'Desativou professor ID {teacher.id}')
    return teacher

def activate_teacher(teacher):
    teacher.status = 'ativo'
    if teacher.user:
        teacher.user.active = True
    db.session.commit()
    log_action('TEACHER_ACTIVATED', entity='teacher', entity_id=teacher.id, description=f'Ativou professor ID {teacher.id}')
    return teacher

def link_teacher_subject(teacher, subject):
    if subject not in teacher.subjects:
        teacher.subjects.append(subject)
        db.session.commit()
        log_action('TEACHER_SUBJECT_LINKED', entity='teacher', entity_id=teacher.id, description=f'Vinculou disciplina {subject.id} ao professor ID {teacher.id}')
        return True
    return False

def unlink_teacher_subject(teacher, subject):
    if subject in teacher.subjects:
        teacher.subjects.remove(subject)
        db.session.commit()
        log_action('TEACHER_SUBJECT_UNLINKED', entity='teacher', entity_id=teacher.id, description=f'Removeu disciplina {subject.id} do professor ID {teacher.id}')
        return True
    return False

def link_teacher_class(teacher, school_class, is_coordinator=False):
    # Check if link exists
    existing = ClassTeacher.query.filter_by(teacher_id=teacher.id, class_id=school_class.id).first()
    if existing:
        return False, "Professor já vinculado à turma."
        
    try:
        if is_coordinator:
            # Demote existing coordinator for this class if any
            ClassTeacher.query.filter_by(class_id=school_class.id, is_coordinator=True).update({'is_coordinator': False})
            
        link = ClassTeacher(
            teacher_id=teacher.id,
            class_id=school_class.id,
            is_coordinator=is_coordinator
        )
        db.session.add(link)
        db.session.commit()
        
        log_action('TEACHER_CLASS_LINKED', entity='teacher', entity_id=teacher.id, description=f'Vinculou professor {teacher.id} à turma {school_class.id}')
        return True, "Turma vinculada."
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def unlink_teacher_class(teacher_id, class_id):
    link = ClassTeacher.query.filter_by(teacher_id=teacher_id, class_id=class_id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        log_action('TEACHER_CLASS_UNLINKED', entity='teacher', entity_id=teacher_id, description=f'Removeu professor {teacher_id} da turma {class_id}')
        return True
    return False

def set_class_coordinator(teacher_id, class_id):
    try:
        # Demote existing coordinator
        ClassTeacher.query.filter_by(class_id=class_id, is_coordinator=True).update({'is_coordinator': False})
        
        link = ClassTeacher.query.filter_by(teacher_id=teacher_id, class_id=class_id).first()
        if link:
            link.is_coordinator = True
            db.session.commit()
            log_action('TEACHER_COORDINATOR_CHANGED', entity='teacher', entity_id=teacher_id, description=f'Professor {teacher_id} definido como coordenador da turma {class_id}')
            return True
        return False
    except Exception as e:
        db.session.rollback()
        return False
