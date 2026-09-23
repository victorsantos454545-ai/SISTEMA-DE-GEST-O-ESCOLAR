from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.utils.decorators import permission_required
from app.models.employee import Employee
from app.forms.employee_forms import EmployeeForm
from app.services.employee_service import (
    search_employees, create_employee, update_employee, 
    activate_employee, deactivate_employee, can_view_employee, can_edit_employee
)

bp = Blueprint('employees', __name__, url_prefix='/funcionarios')

@bp.route('/')
@login_required
@permission_required('employees.view')
def index():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    department = request.args.get('department', '')
    position = request.args.get('position', '')
    page = request.args.get('page', 1, type=int)
    
    pagination = search_employees(query=query, status=status, department=department, position=position, page=page, per_page=15)
    
    return render_template('employees/index.html', pagination=pagination, query=query, status=status, department=department, position=position)

@bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permission_required('employees.create')
def create():
    form = EmployeeForm()
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        employee = create_employee(data)
        flash('Funcionário cadastrado com sucesso.', 'success')
        return redirect(url_for('employees.detail', id=employee.id))
        
    return render_template('employees/form.html', form=form, title="Novo Funcionário")

@bp.route('/<int:id>')
@login_required
def detail(id):
    employee = Employee.query.get_or_404(id)
    
    if not can_view_employee(current_user, employee):
        abort(403)
        
    return render_template(
        'employees/detail.html', 
        employee=employee, 
        can_edit=can_edit_employee(current_user, employee)
    )

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def edit(id):
    employee = Employee.query.get_or_404(id)
    
    if not can_edit_employee(current_user, employee):
        abort(403)
        
    form = EmployeeForm(obj=employee, employee_id=employee.id)
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        update_employee(employee, data)
        flash('Funcionário atualizado com sucesso.', 'success')
        return redirect(url_for('employees.detail', id=employee.id))
        
    return render_template('employees/form.html', form=form, title="Editar Funcionário", employee=employee)

@bp.route('/<int:id>/ativar', methods=['POST'])
@login_required
@permission_required('employees.activate')
def activate(id):
    employee = Employee.query.get_or_404(id)
    activate_employee(employee)
    flash('Funcionário ativado com sucesso.', 'success')
    return redirect(url_for('employees.detail', id=employee.id))

@bp.route('/<int:id>/desativar', methods=['POST'])
@login_required
@permission_required('employees.deactivate')
def deactivate(id):
    employee = Employee.query.get_or_404(id)
    deactivate_employee(employee)
    flash('Funcionário desativado com sucesso.', 'success')
    return redirect(url_for('employees.detail', id=employee.id))
