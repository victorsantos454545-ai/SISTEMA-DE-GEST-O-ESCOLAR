from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user
from app.extensions import db
from app.models import Activity, SchoolClass, Subject, Teacher
from app.forms.activity_forms import ActivityForm, ActivityCancelForm
from app.services.activity_service import create_activity, update_activity, change_activity_status, delete_activity
from app.utils.decorators import permission_required
from datetime import datetime

bp = Blueprint('activities', __name__, url_prefix='/atividades')

def _fill_activity_choices(form, user, current_teacher_id=None):
    """Preenche opções do form baseado no usuário logado."""
    if user.role.name == 'professor':
        teacher = Teacher.query.filter_by(user_id=user.id).first()
        if not teacher:
            return False
            
        classes = [link.school_class for link in teacher.class_links if link.school_class.status == 'ativa']
        if not classes:
            from app.models import Schedule
            classes = [s.school_class for s in teacher.schedules if s.school_class and s.school_class.status == 'ativa']
        if not classes:
            classes = SchoolClass.query.filter_by(status='ativa').all()
            
        subjects = teacher.subjects.all()
        if not subjects:
            subjects = Subject.query.all()
        
        form.school_class_id.choices = [(c.id, c.name) for c in classes]
        form.subject_id.choices = [(s.id, s.name) for s in subjects]
        form.teacher_id.choices = [(teacher.id, teacher.name)]
        form.teacher_id.data = teacher.id
        return True
    else:
        # Admin ou secretaria vêm todas
        form.school_class_id.choices = [(c.id, c.name) for c in SchoolClass.query.filter_by(status='ativa').all()]
        form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
        form.teacher_id.choices = [(t.id, t.name) for t in Teacher.query.filter_by(status='ativo').all()]
        if current_teacher_id:
            form.teacher_id.data = current_teacher_id
        return True

@bp.route('/')
@permission_required('activities.view')
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Activity.query
    
    if current_user.role.name == 'professor':
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if teacher:
            query = query.filter_by(teacher_id=teacher.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    activities = query.order_by(Activity.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('activities/index.html', activities=activities, status_filter=status_filter)

@bp.route('/nova', methods=['GET', 'POST'])
@permission_required('activities.create')
def create():
    form = ActivityForm()
    if not _fill_activity_choices(form, current_user):
        abort(403)
        
    if form.validate_on_submit():
        data = form.data
        if not data.get('teacher_id') and current_user.role.name == 'professor':
            teacher = Teacher.query.filter_by(user_id=current_user.id).first()
            data['teacher_id'] = teacher.id
            
        try:
            create_activity(data, current_user.id)
            flash('Atividade criada com sucesso.', 'success')
            return redirect(url_for('activities.index'))
        except ValueError as e:
            flash(str(e), 'danger')
            
    return render_template('activities/form.html', form=form, title='Nova Atividade')

@bp.route('/<int:id>')
@permission_required('activities.view')
def detail(id):
    activity = Activity.query.get_or_404(id)
    
    # Aluno/Resp só veem se publicada ou encerrada
    if current_user.role.name in ['aluno', 'responsavel'] and activity.status in ['rascunho', 'cancelada']:
        abort(403)
        
    return render_template('activities/detail.html', activity=activity)

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@permission_required('activities.edit')
def edit(id):
    activity = Activity.query.get_or_404(id)
    
    # Professor só edita as próprias
    if current_user.role.name == 'professor':
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if activity.teacher_id != teacher.id:
            abort(403)
            
    form = ActivityForm(obj=activity)
    _fill_activity_choices(form, current_user, activity.teacher_id)
    
    if form.validate_on_submit():
        try:
            update_activity(activity.id, form.data, current_user.id)
            flash('Atividade atualizada.', 'success')
            return redirect(url_for('activities.detail', id=activity.id))
        except ValueError as e:
            flash(str(e), 'danger')
            
    return render_template('activities/form.html', form=form, title='Editar Atividade')

@bp.route('/<int:id>/cancelar', methods=['GET', 'POST'])
@permission_required('activities.edit')
def cancel(id):
    activity = Activity.query.get_or_404(id)
    if activity.status == 'cancelada':
        flash('Atividade já cancelada.', 'info')
        return redirect(url_for('activities.detail', id=id))
        
    form = ActivityCancelForm()
    if form.validate_on_submit():
        change_activity_status(activity.id, 'cancelada', current_user.id, reason=form.reason.data)
        flash('Atividade cancelada com sucesso.', 'warning')
        return redirect(url_for('activities.detail', id=activity.id))
        
    return render_template('activities/cancel.html', form=form, activity=activity)

@bp.route('/<int:id>/excluir', methods=['POST'])
@permission_required('activities.delete')
def delete(id):
    delete_activity(id, current_user.id)
    flash('Atividade excluída permanentemente.', 'success')
    return redirect(url_for('activities.index'))
