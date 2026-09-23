from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Subject
from app.forms.subject_forms import SubjectForm
from app.services.subject_service import (
    get_subjects, create_subject, update_subject, change_subject_status,
    can_view_subject, can_edit_subject
)

bp = Blueprint('subjects', __name__, url_prefix='/disciplinas')

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    status = request.args.get('status', '')
    
    subjects_paginated = get_subjects(
        current_user, page=page, per_page=10, search=search, status=status
    )
    
    return render_template(
        'subjects/list.html', 
        subjects=subjects_paginated,
        search=search,
        status=status,
        can_edit=can_edit_subject(current_user)
    )

@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def create():
    if not can_edit_subject(current_user):
        abort(403)
        
    form = SubjectForm()
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        subject = create_subject(data, current_user)
        flash('Disciplina cadastrada com sucesso.', 'success')
        return redirect(url_for('subjects.detail', id=subject.id))
        
    return render_template('subjects/form.html', form=form, title="Nova Disciplina", subject=None)

@bp.route('/<int:id>')
@login_required
def detail(id):
    subject = Subject.query.get_or_404(id)
    if not can_view_subject(current_user, subject):
        abort(403)
        
    return render_template(
        'subjects/detail.html',
        subject=subject,
        can_edit=can_edit_subject(current_user, subject)
    )

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def edit(id):
    subject = Subject.query.get_or_404(id)
    if not can_edit_subject(current_user, subject):
        abort(403)
        
    form = SubjectForm(obj=subject, subject_id=subject.id)
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
        update_subject(subject, data, current_user)
        flash('Disciplina atualizada com sucesso.', 'success')
        return redirect(url_for('subjects.detail', id=subject.id))
        
    return render_template('subjects/form.html', form=form, title="Editar Disciplina", subject=subject)

@bp.route('/<int:id>/desativar', methods=['POST'])
@login_required
def deactivate(id):
    subject = Subject.query.get_or_404(id)
    if not can_edit_subject(current_user, subject):
        abort(403)
    change_subject_status(subject, 'inativa', current_user)
    flash('Disciplina desativada.', 'info')
    return redirect(url_for('subjects.index'))

@bp.route('/<int:id>/ativar', methods=['POST'])
@login_required
def activate(id):
    subject = Subject.query.get_or_404(id)
    if not can_edit_subject(current_user, subject):
        abort(403)
    change_subject_status(subject, 'ativa', current_user)
    flash('Disciplina ativada.', 'success')
    return redirect(url_for('subjects.index'))
