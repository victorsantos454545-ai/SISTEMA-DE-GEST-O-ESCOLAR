from sqlalchemy import or_
from app.extensions import db
from app.models.employee import Employee
from app.services.audit_service import log_action
import re

def can_view_employee(user, employee):
    if user.role.name in ['admin', 'secretaria']:
        return True
    return False

def can_edit_employee(user, employee):
    return user.role.name in ['admin', 'secretaria']

def search_employees(query=None, status=None, department=None, position=None, page=1, per_page=20):
    base_query = Employee.query
    
    if query:
        search_term = f"%{query}%"
        numeric_query = re.sub(r'[^0-9]', '', query)
        
        if numeric_query:
            base_query = base_query.filter(or_(
                Employee.full_name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.cpf.ilike(f"%{numeric_query}%"),
                Employee.registration.ilike(f"%{numeric_query}%")
            ))
        else:
            base_query = base_query.filter(or_(
                Employee.full_name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.registration.ilike(search_term)
            ))
            
    if status:
        base_query = base_query.filter_by(status=status)
    if department:
        base_query = base_query.filter_by(department=department)
    if position:
        base_query = base_query.filter_by(position=position)
            
    base_query = base_query.order_by(Employee.full_name.asc())
    return base_query.paginate(page=page, per_page=per_page, error_out=False)

def create_employee(data):
    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    employee = Employee(**data)
    db.session.add(employee)
    db.session.commit()
    
    log_action('EMPLOYEE_CREATED', entity='employee', entity_id=employee.id, description=f'Criou funcionário ID {employee.id}')
    return employee

def update_employee(employee, data):
    if data.get('cpf'):
        data['cpf'] = re.sub(r'[^0-9]', '', data['cpf'])

    for key, value in data.items():
        if hasattr(employee, key):
            setattr(employee, key, value)
            
    db.session.commit()
    log_action('EMPLOYEE_UPDATED', entity='employee', entity_id=employee.id, description=f'Atualizou funcionário ID {employee.id}')
    return employee

def deactivate_employee(employee):
    employee.status = 'inativo'
    db.session.commit()
    log_action('EMPLOYEE_DEACTIVATED', entity='employee', entity_id=employee.id, description=f'Desativou funcionário ID {employee.id}')
    return employee

def activate_employee(employee):
    employee.status = 'ativo'
    db.session.commit()
    log_action('EMPLOYEE_ACTIVATED', entity='employee', entity_id=employee.id, description=f'Ativou funcionário ID {employee.id}')
    return employee
