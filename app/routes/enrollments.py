from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Enrollment, Student, SchoolClass, SchoolYear
from app.forms.enrollment_forms import (
    EnrollmentForm, EditEnrollmentForm, TransferEnrollmentForm, 
    CancelEnrollmentForm, CompleteEnrollmentForm, RenewEnrollmentForm
)
from app.services.enrollment_service import (
    get_enrollments, create_enrollment, update_enrollment, 
    transfer_enrollment, cancel_enrollment, complete_enrollment, renew_enrollment,
    can_view_enrollment, can_create_enrollment, can_edit_enrollment, 
    can_transfer_enrollment, can_cancel_enrollment, can_complete_enrollment, can_renew_enrollment,
    check_class_capacity, check_existing_active_enrollment
)

bp = Blueprint('enrollments', __name__, url_prefix='/matriculas')

def populate_choices(form, year_id=None):
    if hasattr(form, 'student_id'):
        form.student_id.choices = [(s.id, f"{s.full_name} ({s.cpf or 'Sem reg.'})") for s in Student.query.filter_by(status='ativo').order_by(Student.full_name).all()]
    if hasattr(form, 'school_year_id'):
        form.school_year_id.choices = [(sy.id, str(sy.year) + (' (Ativo)' if sy.active else '')) for sy in SchoolYear.query.order_by(SchoolYear.year.desc()).all()]
    
    if hasattr(form, 'school_class_id'):
        classes_query = SchoolClass.query.filter(SchoolClass.status != 'encerrada')
        if year_id:
            classes_query = classes_query.filter_by(school_year_id=year_id)
        form.school_class_id.choices = [(c.id, f"{c.name} ({c.shift}) - {c.school_year.year}") for c in classes_query.all()]

    if hasattr(form, 'new_year_id'):
        form.new_year_id.choices = [(sy.id, str(sy.year) + (' (Ativo)' if sy.active else '')) for sy in SchoolYear.query.order_by(SchoolYear.year.desc()).all()]

    if hasattr(form, 'new_class_id'):
        classes_query = SchoolClass.query.filter(SchoolClass.status != 'encerrada')
        if year_id:
            classes_query = classes_query.filter_by(school_year_id=year_id)
        form.new_class_id.choices = [(c.id, f"{c.name} ({c.shift}) - {c.school_year.year}") for c in classes_query.all()]

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    status = request.args.get('status', '')
    year_id = request.args.get('year_id', '')
    class_id = request.args.get('class_id', '')
    
    enrollments_paginated = get_enrollments(
        current_user, page=page, per_page=15, search=search, 
        status=status, year_id=year_id, class_id=class_id
    )
    
    years = SchoolYear.query.order_by(SchoolYear.year.desc()).all()
    
    # Busca turmas do ano selecionado ou todas
    if year_id:
        classes = SchoolClass.query.filter_by(school_year_id=year_id).order_by(SchoolClass.name).all()
    else:
        classes = SchoolClass.query.order_by(SchoolClass.name).all()
        
    return render_template(
        'enrollments/list.html',
        enrollments=enrollments_paginated,
        search=search, status=status, year_id=year_id, class_id=class_id,
        years=years, classes=classes,
        can_create=can_create_enrollment(current_user)
    )

@bp.route('/nova', methods=['GET', 'POST'])
@login_required
def create():
    if not can_create_enrollment(current_user):
        abort(403)
        
    form = EnrollmentForm()
    
    # Se ano não estiver selecionado e o form for submitted, preenche opções sem filtro
    year_to_filter = request.form.get('school_year_id') or request.args.get('year_id')
    populate_choices(form, year_id=year_to_filter)
    
    # Pré-seleção se vier via query string (ex: de dentro da página do aluno)
    student_id = request.args.get('student_id', type=int)
    if request.method == 'GET' and student_id:
        form.student_id.data = student_id
        
    class_id = request.args.get('class_id', type=int)
    if request.method == 'GET' and class_id:
        cls = SchoolClass.query.get(class_id)
        if cls:
            form.school_class_id.data = class_id
            form.school_year_id.data = cls.school_year_id
            populate_choices(form, year_id=cls.school_year_id)

    if form.validate_on_submit():
        # Validação 1: Aluno já matriculado ativo neste ano?
        if form.status.data == 'ativa':
            existing = check_existing_active_enrollment(form.student_id.data, form.school_year_id.data)
            if existing:
                flash(f'O aluno já possui matrícula ativa neste ano letivo (Matrícula {existing.id}).', 'danger')
                return render_template('enrollments/form.html', form=form, title="Nova Matrícula")

        # Validação 2: Compatibilidade de Ano Letivo e Turma
        cls = SchoolClass.query.get(form.school_class_id.data)
        if str(cls.school_year_id) != str(form.school_year_id.data):
            flash('A turma selecionada não pertence ao ano letivo selecionado.', 'danger')
            return render_template('enrollments/form.html', form=form, title="Nova Matrícula")
            
        # Validação 3: Capacidade
        if form.status.data == 'ativa':
            has_capacity, available = check_class_capacity(form.school_class_id.data)
            if not has_capacity:
                flash(f'Esta turma está lotada. Capacidade máxima atingida ({cls.capacity} alunos).', 'danger')
                return render_template('enrollments/form.html', form=form, title="Nova Matrícula")

        # Ok, cria
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        enrollment = create_enrollment(data)
        flash('Matrícula efetuada com sucesso.', 'success')
        return redirect(url_for('enrollments.detail', id=enrollment.id))
        
    return render_template('enrollments/form.html', form=form, title="Nova Matrícula")

@bp.route('/<int:id>')
@login_required
def detail(id):
    enrollment = Enrollment.query.get_or_404(id)
    if not can_view_enrollment(current_user, enrollment):
        abort(403)
        
    history = enrollment.student.enrollments.order_by(Enrollment.enrollment_date.desc()).all()
        
    return render_template(
        'enrollments/detail.html',
        enrollment=enrollment,
        history=history,
        can_edit=can_edit_enrollment(current_user, enrollment),
        can_transfer=can_transfer_enrollment(current_user),
        can_cancel=can_cancel_enrollment(current_user),
        can_complete=can_complete_enrollment(current_user),
        can_renew=can_renew_enrollment(current_user)
    )

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def edit(id):
    enrollment = Enrollment.query.get_or_404(id)
    if not can_edit_enrollment(current_user, enrollment):
        abort(403)
        
    form = EditEnrollmentForm(obj=enrollment)
    
    if form.validate_on_submit():
        # Verificação de capacidade e unicidade ao reativar matrícula
        if form.status.data == 'ativa' and enrollment.status != 'ativa':
            existing = check_existing_active_enrollment(enrollment.student_id, enrollment.school_year_id)
            if existing and str(existing.id) != str(enrollment.id):
                flash(f'O aluno já possui matrícula ativa neste ano letivo.', 'danger')
                return render_template('enrollments/edit.html', form=form, enrollment=enrollment)
                
            has_capacity, _ = check_class_capacity(enrollment.school_class_id)
            if not has_capacity:
                flash('A turma selecionada está lotada.', 'danger')
                return render_template('enrollments/edit.html', form=form, enrollment=enrollment)
                
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        update_enrollment(enrollment, data)
        flash('Matrícula atualizada com sucesso.', 'success')
        return redirect(url_for('enrollments.detail', id=enrollment.id))
        
    return render_template('enrollments/edit.html', form=form, enrollment=enrollment)

@bp.route('/<int:id>/transferir', methods=['GET', 'POST'])
@login_required
def transfer(id):
    enrollment = Enrollment.query.get_or_404(id)
    if not can_transfer_enrollment(current_user) or enrollment.status not in ['ativa', 'pendente']:
        flash('Apenas matrículas ativas ou pendentes podem ser transferidas.', 'warning')
        return redirect(url_for('enrollments.detail', id=enrollment.id))
        
    form = TransferEnrollmentForm()
    # Povoar turmas apenas do MESMO ano letivo
    populate_choices(form, year_id=enrollment.school_year_id)
    # Remove a turma atual da lista
    form.new_class_id.choices = [(c, n) for c, n in form.new_class_id.choices if c != enrollment.school_class_id]
    
    if form.validate_on_submit():
        has_capacity, _ = check_class_capacity(form.new_class_id.data)
        if not has_capacity:
            flash('A turma destino está lotada.', 'danger')
            return render_template('enrollments/transfer.html', form=form, enrollment=enrollment)
            
        new_enrollment = transfer_enrollment(
            enrollment, form.new_class_id.data, 
            form.transfer_date.data, form.reason.data
        )
        flash('Aluno transferido com sucesso.', 'success')
        return redirect(url_for('enrollments.detail', id=new_enrollment.id))
        
    return render_template('enrollments/transfer.html', form=form, enrollment=enrollment)

@bp.route('/<int:id>/cancelar', methods=['GET', 'POST'])
@login_required
def cancel(id):
    enrollment = Enrollment.query.get_or_404(id)
    if not can_cancel_enrollment(current_user) or enrollment.status in ['cancelada', 'concluida', 'transferida']:
        flash('Situação da matrícula não permite cancelamento.', 'warning')
        return redirect(url_for('enrollments.detail', id=enrollment.id))
        
    form = CancelEnrollmentForm()
    
    if form.validate_on_submit():
        cancel_enrollment(enrollment, form.cancel_date.data, form.reason.data)
        flash('Matrícula cancelada com sucesso.', 'success')
        return redirect(url_for('enrollments.detail', id=enrollment.id))
        
    return render_template('enrollments/cancel.html', form=form, enrollment=enrollment)

@bp.route('/<int:id>/concluir', methods=['GET', 'POST'])
@login_required
def complete(id):
    enrollment = Enrollment.query.get_or_404(id)
    if not can_complete_enrollment(current_user) or enrollment.status != 'ativa':
        flash('Apenas matrículas ativas podem ser concluídas.', 'warning')
        return redirect(url_for('enrollments.detail', id=enrollment.id))
        
    form = CompleteEnrollmentForm()
    
    if form.validate_on_submit():
        complete_enrollment(enrollment, form.complete_date.data, form.notes.data)
        flash('Matrícula concluída com sucesso.', 'success')
        return redirect(url_for('enrollments.detail', id=enrollment.id))
        
    return render_template('enrollments/complete.html', form=form, enrollment=enrollment)

@bp.route('/<int:id>/renovar', methods=['GET', 'POST'])
@login_required
def renew(id):
    old_enrollment = Enrollment.query.get_or_404(id)
    if not can_renew_enrollment(current_user):
        abort(403)
        
    form = RenewEnrollmentForm()
    # Povoar selects, não precisamos filtrar classes ainda no get por conta de dinamismo, mas na rota sim
    year_to_filter = request.form.get('new_year_id')
    populate_choices(form, year_id=year_to_filter)
    
    # Remover o ano atual das opções (geralmente renova pro ano seguinte)
    form.new_year_id.choices = [(c, n) for c, n in form.new_year_id.choices if c != old_enrollment.school_year_id]
    
    if form.validate_on_submit():
        if form.status.data == 'ativa':
            existing = check_existing_active_enrollment(old_enrollment.student_id, form.new_year_id.data)
            if existing:
                flash('O aluno já possui matrícula ativa neste novo ano letivo.', 'danger')
                return render_template('enrollments/renew.html', form=form, enrollment=old_enrollment)
            has_capacity, _ = check_class_capacity(form.new_class_id.data)
            if not has_capacity:
                flash('A nova turma está lotada.', 'danger')
                return render_template('enrollments/renew.html', form=form, enrollment=old_enrollment)
                
        cls = SchoolClass.query.get(form.new_class_id.data)
        if str(cls.school_year_id) != str(form.new_year_id.data):
            flash('A nova turma selecionada não pertence ao novo ano letivo.', 'danger')
            return render_template('enrollments/renew.html', form=form, enrollment=old_enrollment)
            
        new_enr = renew_enrollment(
            old_enrollment, form.new_class_id.data, form.new_year_id.data,
            form.renew_date.data, form.status.data, form.notes.data
        )
        flash('Matrícula renovada com sucesso.', 'success')
        return redirect(url_for('enrollments.detail', id=new_enr.id))
        
    return render_template('enrollments/renew.html', form=form, enrollment=old_enrollment)
