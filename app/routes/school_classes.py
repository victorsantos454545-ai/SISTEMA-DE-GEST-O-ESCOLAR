from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import SchoolClass, Teacher, Subject, SchoolYear
from app.forms.class_forms import ClassForm, LinkTeacherForm, LinkSubjectForm
from app.services.class_service import (
    get_classes, create_class, update_class, change_class_status,
    link_teacher_to_class, unlink_teacher_from_class,
    link_subject_to_class, unlink_subject_from_class,
    can_view_class, can_edit_class,
    can_manage_class_teachers, can_manage_class_subjects
)

bp = Blueprint('classes', __name__, url_prefix='/turmas')

@bp.route('/')
@login_required
def index():
    if current_user.role.name in ['aluno', 'responsavel']:
        abort(403)
        
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    status = request.args.get('status', '')
    shift = request.args.get('shift', '')
    year_id = request.args.get('year_id', '')
    grade = request.args.get('grade', '')
    
    classes_paginated = get_classes(
        current_user, page=page, per_page=10, search=search,
        status=status, shift=shift, year_id=year_id, grade=grade
    )
    
    years = SchoolYear.query.order_by(SchoolYear.year.desc()).all()
    
    return render_template(
        'classes/list.html', 
        classes=classes_paginated,
        search=search,
        status=status,
        shift=shift,
        year_id=year_id,
        grade=grade,
        years=years,
        can_edit=current_user.role.name in ['admin', 'secretaria']
    )

@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    if not can_edit_class(current_user):
        abort(403)
        
    form = ClassForm()
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        cls = create_class(data, current_user)
        flash('Turma cadastrada com sucesso.', 'success')
        return redirect(url_for('classes.detail', id=cls.id))
        
    return render_template('classes/form.html', form=form, title="Nova Turma", cls=None)

@bp.route('/<int:id>')
@login_required
def detail(id):
    cls = SchoolClass.query.get_or_404(id)
    if not can_view_class(current_user, cls):
        abort(403)
        
    teacher_form = LinkTeacherForm()
    # Populate teachers
    teacher_form.teacher_id.choices = [(t.id, t.full_name) for t in Teacher.query.filter_by(status='ativo').all()]
    
    subject_form = LinkSubjectForm()
    subject_form.subject_id.choices = [(s.id, s.name) for s in Subject.query.filter_by(status='ativa').all()]
    
    # Calculate occupation
    enrolled = cls.enrolled_count
    capacity = cls.capacity or 0
    available = max(0, capacity - enrolled)
    occupancy = (enrolled / capacity * 100) if capacity > 0 else 0
    
    return render_template(
        'classes/detail.html',
        cls=cls,
        enrolled=enrolled,
        available=available,
        occupancy=occupancy,
        teacher_form=teacher_form,
        subject_form=subject_form,
        can_edit=can_edit_class(current_user, cls),
        can_manage_teachers=can_manage_class_teachers(current_user),
        can_manage_subjects=can_manage_class_subjects(current_user)
    )

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def edit(id):
    cls = SchoolClass.query.get_or_404(id)
    if not can_edit_class(current_user, cls):
        abort(403)
        
    form = ClassForm(obj=cls, class_id=cls.id)
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        update_class(cls, data, current_user)
        flash('Turma atualizada com sucesso.', 'success')
        return redirect(url_for('classes.detail', id=cls.id))
        
    return render_template('classes/form.html', form=form, title="Editar Turma", cls=cls)

@bp.route('/<int:id>/desativar', methods=['POST'])
@login_required
def deactivate(id):
    cls = SchoolClass.query.get_or_404(id)
    if not can_edit_class(current_user, cls):
        abort(403)
    change_class_status(cls, 'inativa', current_user)
    flash('Turma desativada.', 'info')
    return redirect(url_for('classes.index'))

@bp.route('/<int:id>/ativar', methods=['POST'])
@login_required
def activate(id):
    cls = SchoolClass.query.get_or_404(id)
    if not can_edit_class(current_user, cls):
        abort(403)
    change_class_status(cls, 'ativa', current_user)
    flash('Turma ativada.', 'success')
    return redirect(url_for('classes.index'))

@bp.route('/<int:id>/vincular-professor', methods=['POST'])
@login_required
def link_teacher(id):
    cls = SchoolClass.query.get_or_404(id)
    if not can_manage_class_teachers(current_user):
        abort(403)
        
    form = LinkTeacherForm()
    form.teacher_id.choices = [(t.id, t.full_name) for t in Teacher.query.filter_by(status='ativo').all()]
    
    if form.validate_on_submit():
        link_teacher_to_class(cls, form.teacher_id.data, form.is_coordinator.data, current_user)
        flash('Professor vinculado com sucesso.', 'success')
    else:
        flash('Erro ao vincular professor.', 'danger')
        
    return redirect(url_for('classes.detail', id=cls.id))

@bp.route('/<int:id>/desvincular-professor/<int:teacher_id>', methods=['POST'])
@login_required
def unlink_teacher(id, teacher_id):
    cls = SchoolClass.query.get_or_404(id)
    if not can_manage_class_teachers(current_user):
        abort(403)
        
    unlink_teacher_from_class(cls, teacher_id, current_user)
    flash('Professor desvinculado.', 'info')
    return redirect(url_for('classes.detail', id=cls.id))

@bp.route('/<int:id>/vincular-disciplina', methods=['POST'])
@login_required
def link_subject(id):
    cls = SchoolClass.query.get_or_404(id)
    if not can_manage_class_subjects(current_user):
        abort(403)
        
    form = LinkSubjectForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.filter_by(status='ativa').all()]
    
    if form.validate_on_submit():
        link_subject_to_class(cls, form.subject_id.data, form.workload.data, current_user)
        flash('Disciplina vinculada com sucesso.', 'success')
    else:
        flash('Erro ao vincular disciplina.', 'danger')
        
    return redirect(url_for('classes.detail', id=cls.id))

@bp.route('/<int:id>/desvincular-disciplina/<int:subject_id>', methods=['POST'])
@login_required
def unlink_subject(id, subject_id):
    cls = SchoolClass.query.get_or_404(id)
    if not can_manage_class_subjects(current_user):
        abort(403)
        
    unlink_subject_from_class(cls, subject_id, current_user)
    flash('Disciplina desvinculada.', 'info')
    return redirect(url_for('classes.detail', id=cls.id))
