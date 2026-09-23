from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.guardian import Guardian
from app.forms.guardian_forms import GuardianForm
from app.services.guardian_service import (
    search_guardians, create_guardian, update_guardian, 
    can_view_guardian, can_edit_guardian
)
from app.utils.decorators import permission_required

guardians_bp = Blueprint('guardians', __name__, url_prefix='/responsaveis')

@guardians_bp.route('/')
@login_required
@permission_required('guardians.view')
def index():
    """Listagem e busca de responsáveis."""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if per_page not in [10, 20, 50]:
        per_page = 20

    pagination = search_guardians(query=query, page=page, per_page=per_page)
    return render_template('guardians/index.html', pagination=pagination, query=query)

@guardians_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permission_required('guardians.create')
def create():
    """Cadastro de novo responsável."""
    form = GuardianForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token', 'guardian_id']}
        guardian = create_guardian(data, current_user.id)
        flash('Responsável cadastrado com sucesso.', 'success')
        return redirect(url_for('guardians.detail', guardian_id=guardian.id))
        
    return render_template('guardians/create.html', form=form)

@guardians_bp.route('/<int:guardian_id>')
@login_required
def detail(guardian_id):
    """Detalhes do responsável."""
    guardian = Guardian.query.get_or_404(guardian_id)
    
    if not can_view_guardian(current_user, guardian):
        abort(403)

    return render_template(
        'guardians/detail.html', 
        guardian=guardian,
        can_edit=can_edit_guardian(current_user, guardian)
    )

@guardians_bp.route('/<int:guardian_id>/editar', methods=['GET', 'POST'])
@login_required
def edit(guardian_id):
    """Edição de responsável."""
    guardian = Guardian.query.get_or_404(guardian_id)
    
    if not can_edit_guardian(current_user, guardian):
        abort(403)
        
    form = GuardianForm(obj=guardian, guardian_id=guardian.id)
    
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k not in ['submit', 'csrf_token', 'guardian_id']}
        update_guardian(guardian, data, current_user.id)
        flash('Responsável atualizado com sucesso.', 'success')
        return redirect(url_for('guardians.detail', guardian_id=guardian.id))
        
    return render_template('guardians/edit.html', form=form, guardian=guardian)
