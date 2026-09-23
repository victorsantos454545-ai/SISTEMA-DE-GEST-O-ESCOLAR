from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.services.notification_service import (
    get_all_notifications, mark_as_read, mark_all_as_read, get_unread_count, get_recent_notifications
)

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notificacoes')

@notifications_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    unread_only = request.args.get('unread', 'false').lower() == 'true'
    pagination = get_all_notifications(current_user.id, page=page, per_page=20, unread_only=unread_only)
    return render_template('notifications/index.html', pagination=pagination, unread_only=unread_only)

@notifications_bp.route('/<int:id>/ler', methods=['POST'])
@login_required
def read(id):
    notif = mark_as_read(id, current_user.id)
    if notif and notif.link:
        return redirect(notif.link)
    return redirect(url_for('notifications.index'))

@notifications_bp.route('/marcar-todas', methods=['POST'])
@login_required
def read_all():
    mark_all_as_read(current_user.id)
    flash('Todas as notificações foram marcadas como lidas.', 'success')
    return redirect(url_for('notifications.index'))

@notifications_bp.route('/api/unread-count')
@login_required
def api_unread_count():
    count = get_unread_count(current_user.id)
    return jsonify({'unread_count': count})
    
@notifications_bp.route('/api/recent')
@login_required
def api_recent():
    notifs = get_recent_notifications(current_user.id, limit=5)
    result = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'link': n.link,
        'read': n.read_at is not None,
        'created_at': n.created_at.isoformat()
    } for n in notifs]
    return jsonify({'notifications': result})
