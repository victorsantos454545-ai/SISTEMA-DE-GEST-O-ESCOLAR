from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import current_user
from datetime import datetime, date
from app.models import CalendarEvent, SchoolYear, SchoolClass, Subject
from app.forms.calendar_forms import CalendarEventForm
from app.services.calendar_service import get_calendar_events_json, create_calendar_event, update_calendar_event
from app.utils.decorators import permission_required

bp = Blueprint('calendar', __name__, url_prefix='/calendario')

@bp.route('/')
@permission_required('calendar.view')
def index():
    return render_template('calendar/index.html')

@bp.route('/api/events')
@permission_required('calendar.view')
def api_events():
    """Endpoint consumido pelo FullCalendar via AJAX."""
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    status_filter = request.args.get('status')
    
    if not start_str or not end_str:
        return jsonify([])
        
    start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00')).replace(tzinfo=None)
    end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00')).replace(tzinfo=None)
    
    events = get_calendar_events_json(start_date, end_date, current_user, status_filter)
    return jsonify(events)

def _fill_choices(form):
    form.school_year_id.choices = [(0, '---')] + [(y.id, y.year) for y in SchoolYear.query.order_by(SchoolYear.year.desc()).all()]
    form.school_class_id.choices = [(0, '---')] + [(c.id, c.name) for c in SchoolClass.query.filter_by(status='ativa').all()]
    form.subject_id.choices = [(0, '---')] + [(s.id, s.name) for s in Subject.query.filter_by(status='ativa').all()]

@bp.route('/novo', methods=['GET', 'POST'])
@permission_required('calendar.create')
def create():
    form = CalendarEventForm()
    _fill_choices(form)
    
    if form.validate_on_submit():
        data = form.data
        data['school_year_id'] = None if data['school_year_id'] == 0 else data['school_year_id']
        data['school_class_id'] = None if data['school_class_id'] == 0 else data['school_class_id']
        data['subject_id'] = None if data['subject_id'] == 0 else data['subject_id']
        
        try:
            ce = create_calendar_event(data, current_user.id)
            flash('Evento salvo e adicionado ao calendário com sucesso!', 'success')
            return redirect(url_for('calendar.index'))
        except ValueError as e:
            flash(str(e), 'danger')
            
    return render_template('calendar/form.html', form=form, title="Novo Evento")

@bp.route('/<int:id>')
@permission_required('calendar.view')
def detail(id):
    ce = CalendarEvent.query.get_or_404(id)
    return render_template('calendar/detail.html', event=ce)

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@permission_required('calendar.edit')
def edit(id):
    ce = CalendarEvent.query.get_or_404(id)
    form = CalendarEventForm(obj=ce)
    _fill_choices(form)
    
    # Init zero-value selects properly if None
    if request.method == 'GET':
        form.school_year_id.data = ce.school_year_id or 0
        form.school_class_id.data = ce.school_class_id or 0
        form.subject_id.data = ce.subject_id or 0
    
    if form.validate_on_submit():
        data = form.data
        data['school_year_id'] = None if data['school_year_id'] == 0 else data['school_year_id']
        data['school_class_id'] = None if data['school_class_id'] == 0 else data['school_class_id']
        data['subject_id'] = None if data['subject_id'] == 0 else data['subject_id']
        
        try:
            update_calendar_event(id, data, current_user.id)
            flash('Evento atualizado com sucesso.', 'success')
            return redirect(url_for('calendar.index'))
        except ValueError as e:
            flash(str(e), 'danger')
            
    return render_template('calendar/form.html', form=form, title="Editar Evento")
