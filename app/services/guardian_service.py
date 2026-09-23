"""Serviços para Gestão de Responsáveis."""
import re
from sqlalchemy import or_
from app.extensions import db
from app.models.guardian import Guardian
from app.models.student_guardian import StudentGuardian
from app.services.audit_service import log_action

def can_view_guardian(user, guardian):
    if user.role.name in ['admin', 'secretaria']:
        return True
    
    if user.role.name == 'responsavel':
        return getattr(user.guardian_profile, 'id', None) == guardian.id
        
    return False

def can_edit_guardian(user, guardian):
    if user.role.name in ['admin', 'secretaria']:
        return True
    return False

def search_guardians(query=None, page=1, per_page=20):
    base_query = Guardian.query
    if query:
        search_term = f"%{query}%"
        numeric_query = re.sub(r'[^0-9]', '', query)
        
        if numeric_query:
            base_query = base_query.filter(or_(
                Guardian.full_name.ilike(search_term),
                Guardian.cpf.ilike(f"%{numeric_query}%")
            ))
        else:
            base_query = base_query.filter(
                Guardian.full_name.ilike(search_term)
            )
            
    base_query = base_query.order_by(Guardian.full_name.asc())
    return base_query.paginate(page=page, per_page=per_page, error_out=False)

def create_guardian(data, user_id):
    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    guardian = Guardian(**data)
    db.session.add(guardian)
    db.session.commit()
    
    log_action('GUARDIAN_CREATED', entity='guardian', entity_id=guardian.id, description=f'Criou responsável ID {guardian.id}')
    return guardian

def update_guardian(guardian, data, user_id):
    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    for key, value in data.items():
        if hasattr(guardian, key):
            setattr(guardian, key, value)
            
    db.session.commit()
    log_action('GUARDIAN_UPDATED', entity='guardian', entity_id=guardian.id, description=f'Atualizou responsável ID {guardian.id}')
    return guardian

def link_guardian_to_student(student_id, guardian_id, relationship, is_primary, user_id):
    """Vincula um responsável a um aluno, tratando a regra de is_primary transacionalmente."""
    # Valida duplicidade
    existing = StudentGuardian.query.filter_by(student_id=student_id, guardian_id=guardian_id).first()
    if existing:
        return False, "O vínculo já existe."
        
    try:
        # Se for marcar como principal, tira o outro que for principal
        if is_primary:
            StudentGuardian.query.filter_by(student_id=student_id, is_primary=True).update({'is_primary': False})
            
        link = StudentGuardian(
            student_id=student_id,
            guardian_id=guardian_id,
            relationship=relationship,
            is_primary=is_primary
        )
        db.session.add(link)
        db.session.commit()
        
        log_action('GUARDIAN_LINKED', entity='student', entity_id=student_id, description=f'Vinculou responsável ID {guardian_id} ao aluno ID {student_id}')
        return True, "Vínculo criado com sucesso."
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao criar vínculo: {str(e)}"

def unlink_guardian(student_id, guardian_id, user_id):
    link = StudentGuardian.query.filter_by(student_id=student_id, guardian_id=guardian_id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        log_action('GUARDIAN_UNLINKED', entity='student', entity_id=student_id, description=f'Removeu vínculo de responsável ID {guardian_id} do aluno ID {student_id}')
        return True
    return False

def set_primary_guardian(student_id, guardian_id, user_id):
    try:
        StudentGuardian.query.filter_by(student_id=student_id, is_primary=True).update({'is_primary': False})
        
        link = StudentGuardian.query.filter_by(student_id=student_id, guardian_id=guardian_id).first()
        if link:
            link.is_primary = True
            db.session.commit()
            log_action('PRIMARY_GUARDIAN_CHANGED', entity='student', entity_id=student_id, description=f'Definiu responsável ID {guardian_id} como principal do aluno ID {student_id}')
            return True, "Responsável definido como principal."
        return False, "Vínculo não encontrado."
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao definir responsável principal: {str(e)}"
