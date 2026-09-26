from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.utils.decorators import permission_required
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.school_class import SchoolClass
from app.forms.teacher_forms import TeacherForm, LinkSubjectForm, LinkClassForm
from app.services.teacher_service import (
    search_teachers, create_teacher, update_teacher, 
    activate_teacher, deactivate_teacher, can_view_teacher, can_edit_teacher,
    link_teacher_subject, unlink_teacher_subject, link_teacher_class, unlink_teacher_class,
    set_class_coordinator, can_manage_teacher_classes, can_manage_teacher_subjects
)
from app.extensions import db

bp = Blueprint('teachers', __name__, url_prefix='/professores')

@bp.route('/')
@login_required
@permission_required('teachers.view')
def index():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    pagination = search_teachers(query=query, status=status, page=page, per_page=15)
    
    return render_template('teachers/index.html', pagination=pagination, query=query, status=status)

@bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permission_required('teachers.create')
def create():
    form = TeacherForm()
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        teacher = create_teacher(data)
        flash('Professor cadastrado com sucesso.', 'success')
        return redirect(url_for('teachers.detail', id=teacher.id))
        
    return render_template('teachers/form.html', form=form, title="Novo Professor")

@bp.route('/<int:id>')
@login_required
def detail(id):
    teacher = Teacher.query.get_or_404(id)
    
    if not can_view_teacher(current_user, teacher):
        abort(403)
        
    subject_form = LinkSubjectForm()
    # Populate subject choices
    subject_form.subject_id.choices = [(s.id, s.name) for s in Subject.query.filter_by(status='ativa').all()]
    
    class_form = LinkClassForm()
    # Populate class choices
    class_form.class_id.choices = [(c.id, c.name) for c in SchoolClass.query.filter_by(status='ativa').all()]
    
    return render_template(
        'teachers/detail.html', 
        teacher=teacher, 
        can_edit=can_edit_teacher(current_user, teacher),
        can_manage_classes=can_manage_teacher_classes(current_user),
        can_manage_subjects=can_manage_teacher_subjects(current_user),
        subject_form=subject_form,
        class_form=class_form
    )

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def edit(id):
    teacher = Teacher.query.get_or_404(id)
    
    if not can_edit_teacher(current_user, teacher):
        abort(403)
        
    form = TeacherForm(obj=teacher, teacher_id=teacher.id)
    if request.method == 'GET' and teacher.user:
        form.username.data = teacher.user.username
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        update_teacher(teacher, data)
        flash('Professor atualizado com sucesso.', 'success')
        return redirect(url_for('teachers.detail', id=teacher.id))
        
    return render_template('teachers/form.html', form=form, title="Editar Professor", teacher=teacher)

@bp.route('/<int:id>/ativar', methods=['POST'])
@login_required
@permission_required('teachers.activate')
def activate(id):
    teacher = Teacher.query.get_or_404(id)
    activate_teacher(teacher)
    flash('Professor ativado com sucesso.', 'success')
    return redirect(url_for('teachers.detail', id=teacher.id))

@bp.route('/<int:id>/desativar', methods=['POST'])
@login_required
@permission_required('teachers.deactivate')
def deactivate(id):
    teacher = Teacher.query.get_or_404(id)
    deactivate_teacher(teacher)
    flash('Professor desativado com sucesso.', 'success')
    return redirect(url_for('teachers.detail', id=teacher.id))

@bp.route('/<int:id>/vincular-disciplina', methods=['POST'])
@login_required
@permission_required('teachers.manage_subjects')
def link_subject(id):
    teacher = Teacher.query.get_or_404(id)
    form = LinkSubjectForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.filter_by(status='ativa').all()]
    
    if form.validate_on_submit():
        subject = Subject.query.get(form.subject_id.data)
        if subject:
            link_teacher_subject(teacher, subject)
            flash('Disciplina vinculada com sucesso.', 'success')
        else:
            flash('Disciplina não encontrada.', 'danger')
            
    return redirect(url_for('teachers.detail', id=teacher.id))

@bp.route('/<int:id>/desvincular-disciplina/<int:subject_id>', methods=['POST'])
@login_required
@permission_required('teachers.manage_subjects')
def unlink_subject(id, subject_id):
    teacher = Teacher.query.get_or_404(id)
    subject = Subject.query.get_or_404(subject_id)
    
    if unlink_teacher_subject(teacher, subject):
        flash('Disciplina desvinculada com sucesso.', 'success')
    else:
        flash('Vínculo não encontrado.', 'warning')
        
    return redirect(url_for('teachers.detail', id=teacher.id))

@bp.route('/<int:id>/vincular-turma', methods=['POST'])
@login_required
@permission_required('teachers.manage_classes')
def link_class(id):
    teacher = Teacher.query.get_or_404(id)
    form = LinkClassForm()
    form.class_id.choices = [(c.id, c.name) for c in SchoolClass.query.filter_by(status='ativa').all()]
    
    if form.validate_on_submit():
        school_class = SchoolClass.query.get(form.class_id.data)
        if school_class:
            is_coordinator = form.is_coordinator.data == 'y'
            success, msg = link_teacher_class(teacher, school_class, is_coordinator)
            if success:
                flash(msg, 'success')
            else:
                flash(msg, 'danger')
        else:
            flash('Turma não encontrada.', 'danger')
            
    return redirect(url_for('teachers.detail', id=teacher.id))

@bp.route('/<int:id>/desvincular-turma/<int:class_id>', methods=['POST'])
@login_required
@permission_required('teachers.manage_classes')
def unlink_class(id, class_id):
    if unlink_teacher_class(id, class_id):
        flash('Turma desvinculada com sucesso.', 'success')
    else:
        flash('Vínculo não encontrado.', 'warning')
        
    return redirect(url_for('teachers.detail', id=id))

@bp.route('/<int:id>/coordenador/<int:class_id>', methods=['POST'])
@login_required
@permission_required('teachers.manage_classes')
def set_coordinator(id, class_id):
    if set_class_coordinator(id, class_id):
        flash('Professor definido como coordenador da turma.', 'success')
    else:
        flash('Não foi possível alterar o coordenador.', 'danger')
        
    return redirect(url_for('teachers.detail', id=id))
