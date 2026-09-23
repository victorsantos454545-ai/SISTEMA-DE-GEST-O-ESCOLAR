from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.models import SchoolClass, Schedule, Subject, Teacher
from app.forms.schedule_forms import ScheduleForm
from app.services.schedule_service import create_schedule, update_schedule, delete_schedule
from app.utils.decorators import permission_required

bp = Blueprint('schedules', __name__, url_prefix='/horarios')

def _fill_choices(form, school_class):
    # Only subjects attached to this class
    subjects = school_class.subjects
    form.subject_id.choices = [(s.id, s.name) for s in subjects]
    # Teachers active
    teachers = Teacher.query.filter_by(status='ativo').all()
    form.teacher_id.choices = [(t.id, t.name) for t in teachers]

@bp.route('/turma/<int:class_id>')
@permission_required('schedules.view')
def class_schedule(class_id):
    school_class = SchoolClass.query.get_or_404(class_id)
    schedules = Schedule.query.filter_by(school_class_id=class_id).order_by(Schedule.start_time).all()
    
    # Montar a matriz: dict[time][day] = list[sch]
    grid = {}
    for sch in schedules:
        time_slot = f"{sch.start_time.strftime('%H:%M')} - {sch.end_time.strftime('%H:%M')}"
        if time_slot not in grid:
            grid[time_slot] = {d: [] for d in Schedule.DAYS}
        grid[time_slot][sch.day_of_week].append(sch)
        
    return render_template('schedules/class_schedule.html', 
                           school_class=school_class, 
                           schedules=schedules,
                           grid=grid,
                           days=Schedule.DAYS)

@bp.route('/turma/<int:class_id>/novo', methods=['GET', 'POST'])
@permission_required('schedules.create')
def create(class_id):
    school_class = SchoolClass.query.get_or_404(class_id)
    form = ScheduleForm()
    _fill_choices(form, school_class)
    
    if form.validate_on_submit():
        data = form.data
        data['school_class_id'] = class_id
        
        try:
            create_schedule(data, current_user.id)
            flash('Horário criado com sucesso.', 'success')
            return redirect(url_for('schedules.class_schedule', class_id=class_id))
        except ValueError as e:
            flash(str(e), 'danger')
            
    return render_template('schedules/form.html', form=form, school_class=school_class, title="Novo Horário")

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@permission_required('schedules.edit')
def edit(id):
    sch = Schedule.query.get_or_404(id)
    form = ScheduleForm(obj=sch)
    _fill_choices(form, sch.school_class)
    
    if form.validate_on_submit():
        try:
            update_schedule(id, form.data, current_user.id)
            flash('Horário atualizado com sucesso.', 'success')
            return redirect(url_for('schedules.class_schedule', class_id=sch.school_class_id))
        except ValueError as e:
            flash(str(e), 'danger')
            
    return render_template('schedules/form.html', form=form, school_class=sch.school_class, title="Editar Horário")

@bp.route('/<int:id>/excluir', methods=['POST'])
@permission_required('schedules.delete')
def delete(id):
    sch = Schedule.query.get_or_404(id)
    class_id = sch.school_class_id
    delete_schedule(id, current_user.id)
    flash('Horário excluído com sucesso.', 'success')
    return redirect(url_for('schedules.class_schedule', class_id=class_id))

@bp.route('/meu-horario')
@permission_required('schedules.view')
def my_schedule():
    # Helper rota para alunos e professores
    if current_user.role.name == 'aluno':
        if not current_user.profile:
            flash("Perfil de aluno não encontrado.", "warning")
            return redirect(url_for('dashboard.index'))
            
        enrollment = current_user.profile.enrollments.filter_by(status='ativa').first()
        if not enrollment:
            flash("Você não possui matrícula ativa em uma turma.", "warning")
            return redirect(url_for('dashboard.index'))
            
        return redirect(url_for('schedules.class_schedule', class_id=enrollment.school_class_id))
        
    elif current_user.role.name == 'professor':
        if not current_user.profile:
            flash("Perfil de professor não encontrado.", "warning")
            return redirect(url_for('dashboard.index'))
            
        # Para professor, criamos uma view especial
        schedules = Schedule.query.filter_by(teacher_id=current_user.profile.id).order_by(Schedule.start_time).all()
        grid = {}
        for sch in schedules:
            time_slot = f"{sch.start_time.strftime('%H:%M')} - {sch.end_time.strftime('%H:%M')}"
            if time_slot not in grid:
                grid[time_slot] = {d: [] for d in Schedule.DAYS}
            grid[time_slot][sch.day_of_week].append(sch)
            
        return render_template('schedules/teacher_schedule.html', 
                               teacher=current_user.profile,
                               grid=grid,
                               days=Schedule.DAYS)
                               
    flash("Esta visualização é para alunos e professores.", "info")
    return redirect(url_for('dashboard.index'))
