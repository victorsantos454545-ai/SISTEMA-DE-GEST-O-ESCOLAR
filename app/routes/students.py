from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.student import Student
from app.models.guardian import Guardian
from app.forms.student_forms import StudentForm
from app.forms.guardian_forms import StudentGuardianForm
from app.services.student_service import (
    search_students, create_student, update_student, deactivate_student,
    activate_student, can_view_student, can_edit_student, can_manage_guardians,
    get_student_history
)
from app.services.guardian_service import link_guardian_to_student, unlink_guardian, set_primary_guardian
from app.utils.decorators import permission_required

students_bp = Blueprint('students', __name__, url_prefix='/alunos')

@students_bp.route('/')
@login_required
@permission_required('students.view')
def index():
    """Listagem e busca de alunos."""
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Previne valores absurdos
    if per_page not in [10, 20, 50]:
        per_page = 20

    pagination = search_students(query=query, status=status, page=page, per_page=per_page)
    return render_template('students/index.html', pagination=pagination, query=query, status=status)

@students_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permission_required('students.create')
def create():
    """Cadastro de novo aluno."""
    form = StudentForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token', 'student_id']}
        student = create_student(data, current_user.id)
        flash('Aluno cadastrado com sucesso.', 'success')
        return redirect(url_for('students.detail', student_id=student.id))
        
    return render_template('students/create.html', form=form)

@students_bp.route('/<int:student_id>')
@login_required
def detail(student_id):
    """Detalhes completos do aluno."""
    student = Student.query.get_or_404(student_id)
    
    if not can_view_student(current_user, student):
        abort(403)
        
    history = get_student_history(student)
    
    # Formulário para vincular responsável rápido (apenas quem pode gerenciar responsáveis)
    link_form = StudentGuardianForm() if can_manage_guardians(current_user) else None
    if link_form:
        # Preenche os choices com responsáveis disponíveis
        guardians = Guardian.query.order_by(Guardian.full_name).all()
        link_form.guardian_id.choices = [(g.id, f"{g.full_name} ({g.cpf or 'S/ CPF'})") for g in guardians]

    return render_template(
        'students/detail.html', 
        student=student, 
        history=history,
        link_form=link_form,
        can_edit=can_edit_student(current_user, student),
        can_manage_guardians=can_manage_guardians(current_user)
    )

@students_bp.route('/<int:student_id>/editar', methods=['GET', 'POST'])
@login_required
def edit(student_id):
    """Edição de aluno."""
    student = Student.query.get_or_404(student_id)
    
    if not can_edit_student(current_user, student):
        abort(403)
        
    form = StudentForm(obj=student, student_id=student.id)
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token', 'student_id']}
        update_student(student, data, current_user.id)
        flash('Aluno atualizado com sucesso.', 'success')
        return redirect(url_for('students.detail', student_id=student.id))
        
    return render_template('students/edit.html', form=form, student=student)

@students_bp.route('/<int:student_id>/desativar', methods=['POST'])
@login_required
def deactivate(student_id):
    """Desativa um aluno."""
    student = Student.query.get_or_404(student_id)
    if not can_edit_student(current_user, student):
        abort(403)
        
    deactivate_student(student, current_user.id)
    flash('Aluno desativado com sucesso.', 'success')
    return redirect(url_for('students.detail', student_id=student.id))

@students_bp.route('/<int:student_id>/ativar', methods=['POST'])
@login_required
def activate(student_id):
    """Ativa um aluno."""
    student = Student.query.get_or_404(student_id)
    if not can_edit_student(current_user, student):
        abort(403)
        
    activate_student(student, current_user.id)
    flash('Aluno reativado com sucesso.', 'success')
    return redirect(url_for('students.detail', student_id=student.id))

@students_bp.route('/<int:student_id>/vincular-responsavel', methods=['POST'])
@login_required
@permission_required('guardians.edit')
def link_guardian(student_id):
    """Vincula um responsável ao aluno via POST."""
    form = StudentGuardianForm()
    # Carrega choices para validar form
    form.guardian_id.choices = [(g.id, g.full_name) for g in Guardian.query.all()]
    
    if form.validate_on_submit():
        success, msg = link_guardian_to_student(
            student_id, 
            form.guardian_id.data, 
            form.relationship.data, 
            form.is_primary.data,
            current_user.id
        )
        if success:
            flash(msg, 'success')
        else:
            flash(msg, 'danger')
    else:
        flash('Formulário inválido. Verifique os dados.', 'danger')
        
    return redirect(url_for('students.detail', student_id=student_id))

@students_bp.route('/<int:student_id>/desvincular-responsavel/<int:guardian_id>', methods=['POST'])
@login_required
@permission_required('guardians.edit')
def unlink(student_id, guardian_id):
    """Remove o vínculo entre aluno e responsável."""
    if unlink_guardian(student_id, guardian_id, current_user.id):
        flash('Vínculo removido com sucesso.', 'success')
    else:
        flash('Não foi possível remover o vínculo.', 'danger')
    return redirect(url_for('students.detail', student_id=student_id))

@students_bp.route('/<int:student_id>/responsavel-principal/<int:guardian_id>', methods=['POST'])
@login_required
@permission_required('guardians.edit')
def set_primary(student_id, guardian_id):
    """Define o responsável como principal."""
    success, msg = set_primary_guardian(student_id, guardian_id, current_user.id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('students.detail', student_id=student_id))
