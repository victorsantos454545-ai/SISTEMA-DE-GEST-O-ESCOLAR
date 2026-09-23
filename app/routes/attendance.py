from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user
from app.extensions import db
from app.models import Attendance, SchoolClass, Subject, Teacher, Enrollment, Student
from app.forms.attendance_forms import AttendanceConfigForm, AttendanceBatchForm, AttendanceEditForm
from app.services.attendance_service import process_attendance_batch, update_attendance_record, calculate_student_attendance
from app.utils.decorators import permission_required

bp = Blueprint('attendance', __name__, url_prefix='/frequencia')

@bp.route('/', methods=['GET', 'POST'])
@permission_required('attendance.create')
def index():
    form = AttendanceConfigForm()
    
    # Preencher turmas
    classes = SchoolClass.query.filter_by(status='ativa').all()
    form.school_class_id.choices = [(c.id, c.name) for c in classes]
    
    # Preencher disciplinas
    subjects = Subject.query.all()
    form.subject_id.choices = [(s.id, s.name) for s in subjects]
    
    # Filtrar para professores
    teacher = None
    if current_user.role.name == 'professor':
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if not teacher:
            abort(403)
            
    if form.validate_on_submit():
        # Validar professor leciona
        if teacher:
            link = teacher.subject_links.filter_by(
                school_class_id=form.school_class_id.data,
                subject_id=form.subject_id.data
            ).first()
            if not link:
                flash('Você não tem permissão para lançar chamada nesta turma/disciplina.', 'danger')
                return redirect(url_for('attendance.index'))
                
        return redirect(url_for('attendance.call', 
                                class_id=form.school_class_id.data, 
                                subject_id=form.subject_id.data,
                                date=form.date.data.strftime('%Y-%m-%d'),
                                period=form.period.data))
                                
    return render_template('attendance/index.html', form=form)

@bp.route('/chamada', methods=['GET', 'POST'])
@permission_required('attendance.create')
def call():
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    date_str = request.args.get('date')
    period = request.args.get('period', '')
    
    if not all([class_id, subject_id, date_str]):
        return redirect(url_for('attendance.index'))
        
    school_class = SchoolClass.query.get_or_404(class_id)
    subject = Subject.query.get_or_404(subject_id)
    
    teacher_id = None
    if current_user.role.name == 'professor':
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if not teacher: abort(403)
        teacher_id = teacher.id
    else:
        # Se for admin/secretaria, pegar professor vinculado
        link = school_class.subject_links.filter_by(subject_id=subject.id).first()
        if link:
            teacher_id = link.teacher_id
            
    form = AttendanceBatchForm()
    
    # Alunos matriculados
    enrollments = Enrollment.query.filter_by(school_class_id=class_id, status='ativa').all()
    
    # Busca registros existentes
    existing = Attendance.query.filter_by(school_class_id=class_id, subject_id=subject_id, date=date_str).all()
    existing_dict = {a.student_id: a for a in existing}
    
    if form.validate_on_submit():
        data = request.form.to_dict()
        attendance_data = {}
        
        for e in enrollments:
            sid = str(e.student_id)
            status = data.get(f'status_{sid}')
            justif = data.get(f'justification_{sid}', '')
            if status:
                attendance_data[sid] = {'status': status, 'justification': justif}
                
        if teacher_id:
            success, result = process_attendance_batch(teacher_id, class_id, subject_id, date_str, period, attendance_data)
            if success:
                flash(f'Chamada registrada com sucesso! ({result} alunos)', 'success')
                return redirect(url_for('attendance.index'))
        else:
            flash('Nenhum professor vinculado para assumir o registro.', 'danger')
            
    return render_template('attendance/call.html', 
                          form=form, 
                          school_class=school_class, 
                          subject=subject, 
                          date=date_str, 
                          period=period,
                          enrollments=enrollments,
                          existing=existing_dict)

@bp.route('/aluno/<int:student_id>')
@permission_required('attendance.view')
def student_report(student_id):
    student = Student.query.get_or_404(student_id)
    
    if current_user.role.name == 'aluno' and student.user_id != current_user.id:
        abort(403)
    elif current_user.role.name == 'responsavel':
        from app.models.guardian import Guardian
        guardian = Guardian.query.filter_by(user_id=current_user.id).first()
        if not guardian or student not in guardian.students:
            abort(403)
            
    enrollment = Enrollment.query.filter_by(student_id=student_id).order_by(Enrollment.enrollment_date.desc()).first()
    if not enrollment:
        flash('Aluno sem matrícula ativa.', 'warning')
        return redirect(request.referrer or url_for('main.dashboard'))
        
    class_id = enrollment.school_class_id
    subjects = [link.subject for link in enrollment.school_class.subject_links]
    
    stats = []
    for sub in subjects:
        s = calculate_student_attendance(student.id, class_id, sub.id)
        stats.append({'subject': sub, 'stats': s})
        
    global_stat = calculate_student_attendance(student.id, class_id)
    
    return render_template('attendance/student.html', student=student, stats=stats, global_stat=global_stat, school_class=enrollment.school_class)

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@permission_required('attendance.edit')
def edit(id):
    att = Attendance.query.get_or_404(id)
    form = AttendanceEditForm()
    
    if request.method == 'GET':
        if att.present:
            form.status.data = 'presente'
        elif att.justification:
            form.status.data = 'justificado'
        else:
            form.status.data = 'ausente'
        form.justification.data = att.justification
        
    if form.validate_on_submit():
        present = (form.status.data == 'presente')
        justification = form.justification.data if form.status.data == 'justificado' else None
        
        update_attendance_record(att.id, present, justification)
        flash('Registro de frequência atualizado.', 'success')
        return redirect(url_for('attendance.student_report', student_id=att.student_id))
        
    return render_template('attendance/edit.html', form=form, att=att)
