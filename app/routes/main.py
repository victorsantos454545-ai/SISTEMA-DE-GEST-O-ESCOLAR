from flask import Blueprint, redirect, url_for, render_template, jsonify
from flask_login import login_required, current_user
from app.services.dashboard_service import (
    get_admin_dashboard_data,
    get_teacher_dashboard_data,
    get_secretary_dashboard_data,
    get_guardian_dashboard_data,
    get_student_dashboard_data,
    get_announcements_for_user
)
from app.models.school_class import SchoolClass
from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redireciona para o dashboard se autenticado, senao para login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal."""
    role = current_user.role.name
    announcements = get_announcements_for_user(current_user)
    
    if role == 'admin':
        data = get_admin_dashboard_data()
        return render_template('dashboard/admin.html', data=data, announcements=announcements)
    elif role == 'professor':
        data = get_teacher_dashboard_data(current_user.profile)
        return render_template('dashboard/teacher.html', data=data, announcements=announcements)
    elif role == 'secretaria':
        data = get_secretary_dashboard_data()
        return render_template('dashboard/secretary.html', data=data, announcements=announcements)
    elif role == 'responsavel':
        data = get_guardian_dashboard_data(current_user.profile)
        return render_template('dashboard/guardian.html', data=data, announcements=announcements)
    elif role == 'aluno':
        data = get_student_dashboard_data(current_user.profile)
        return render_template('dashboard/student.html', data=data, announcements=announcements)
    
    # Fallback genérico
    return render_template('dashboard/index.html')

@main_bp.route('/dashboard/api/admin-charts')
@login_required
def api_admin_charts():
    """Endpoint JSON para gráficos do admin (Alunos por turma)."""
    if current_user.role.name not in ['admin', 'secretaria']:
        return jsonify({'error': 'Acesso negado'}), 403
        
    classes = SchoolClass.query.filter_by(status='ativa').all()
    labels = []
    data = []
    
    for c in classes:
        labels.append(c.name)
        data.append(c.enrolled_count)
        
    return jsonify({
        'labels': labels,
        'data': data
    })

