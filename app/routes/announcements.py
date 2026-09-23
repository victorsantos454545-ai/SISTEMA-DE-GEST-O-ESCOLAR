from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Announcement, AnnouncementRecipient, SchoolClass
from app.forms.announcement_forms import AnnouncementForm
from app.services.announcement_service import (
    get_visible_announcements, create_announcement, update_announcement, 
    cancel_announcement, mark_as_read, get_unread_count
)
from app.utils.decorators import permission_required

announcements_bp = Blueprint('announcements', __name__, url_prefix='/comunicados')

@announcements_bp.route('/')
@login_required
def index():
    if current_user.has_permission('announcements.manage'):
        # Managers can see everything based on status filter
        status = request.args.get('status', 'todos')
        query = Announcement.query
        if status != 'todos':
            query = query.filter_by(status=status)
        query = query.order_by(Announcement.created_at.desc())
        
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(page=page, per_page=10, error_out=False)
        return render_template('announcements/index_manage.html', pagination=pagination, status=status)
    else:
        # Regular users see visible ones
        announcements = get_visible_announcements(current_user)
        # Check read status for visual hints
        from app.models import AnnouncementRead
        reads = {r.announcement_id for r in AnnouncementRead.query.filter_by(user_id=current_user.id).all()}
        return render_template('announcements/index.html', announcements=announcements, reads=reads)

@announcements_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permission_required('announcements.create')
def create():
    form = AnnouncementForm()
    # Populate classes for selection
    form.target_class_id.choices = [(0, '--- Selecione ---')] + [(c.id, c.name) for c in SchoolClass.query.filter_by(status='ativa').all()]
    
    if form.validate_on_submit():
        targets = []
        for audience in form.target_audiences.data:
            if audience == 'turma':
                targets.append({'type': 'turma', 'id': form.target_class_id.data})
            else:
                targets.append({'type': audience, 'id': None})
                
        data = {
            'title': form.title.data,
            'content': form.content.data,
            'priority': form.priority.data,
            'status': form.status.data,
            'published_at': form.published_at.data,
            'expires_at': form.expires_at.data,
            'targets': targets
        }
        create_announcement(data, current_user.id)
        flash('Comunicado criado com sucesso.', 'success')
        return redirect(url_for('announcements.index'))
        
    return render_template('announcements/form.html', form=form, title="Novo Comunicado")

@announcements_bp.route('/<int:id>')
@login_required
def detail(id):
    announcement = Announcement.query.get_or_404(id)
    
    # Check visibility if not manager
    if not current_user.has_permission('announcements.manage'):
        visible = get_visible_announcements(current_user)
        if announcement.id not in [a.id for a in visible]:
            abort(403)
            
        # Mark as read
        mark_as_read(announcement.id, current_user.id)
        
    return render_template('announcements/detail.html', announcement=announcement)

@announcements_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@permission_required('announcements.edit')
def edit(id):
    announcement = Announcement.query.get_or_404(id)
    form = AnnouncementForm(obj=announcement)
    form.target_class_id.choices = [(0, '--- Selecione ---')] + [(c.id, c.name) for c in SchoolClass.query.filter_by(status='ativa').all()]
    
    if request.method == 'GET':
        audiences = [r.target_type for r in announcement.recipients]
        form.target_audiences.data = audiences
        class_rec = next((r for r in announcement.recipients if r.target_type == 'turma'), None)
        if class_rec:
            form.target_class_id.data = class_rec.target_id
            
    if form.validate_on_submit():
        targets = []
        for audience in form.target_audiences.data:
            if audience == 'turma':
                targets.append({'type': 'turma', 'id': form.target_class_id.data})
            else:
                targets.append({'type': audience, 'id': None})
                
        data = {
            'title': form.title.data,
            'content': form.content.data,
            'priority': form.priority.data,
            'status': form.status.data,
            'published_at': form.published_at.data,
            'expires_at': form.expires_at.data,
            'targets': targets
        }
        update_announcement(announcement.id, data, current_user.id)
        flash('Comunicado atualizado.', 'success')
        return redirect(url_for('announcements.detail', id=announcement.id))
        
    return render_template('announcements/form.html', form=form, title="Editar Comunicado", announcement=announcement)

@announcements_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
@permission_required('announcements.manage')
def cancel(id):
    reason = request.form.get('reason', '')
    cancel_announcement(id, current_user.id, reason)
    flash('Comunicado cancelado.', 'success')
    return redirect(url_for('announcements.index'))
