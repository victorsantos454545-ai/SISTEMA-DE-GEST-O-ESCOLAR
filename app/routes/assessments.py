from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user
from app.extensions import db
from app.models import Assessment, SchoolClass, Subject, Teacher, Period, Enrollment
from app.forms.assessment_forms import AssessmentForm
from app.forms.grade_forms import GradeBatchForm
from app.services.assessment_service import create_assessment, update_assessment, archive_assessment, can_teacher_manage_assessment
from app.services.grade_service import process_grade_batch
from app.utils.decorators import permission_required

bp = Blueprint('assessments', __name__, url_prefix='/avaliacoes')

@bp.route('/')
@permission_required('assessments.view')
def index():
    page = request.args.get('page', 1, type=int)
    query = Assessment.query.filter_by(status='ativa')
    
    # Se for professor, filtrar apenas avaliações das turmas que leciona
    if current_user.role.name == 'professor':
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if teacher:
            query = query.filter_by(teacher_id=teacher.id)
            
    assessments = query.order_by(Assessment.date.desc()).paginate(page=page, per_page=20)
    return render_template('assessments/list.html', assessments=assessments)

@bp.route('/nova', methods=['GET', 'POST'])
@permission_required('assessments.create')
def create():
    form = AssessmentForm()
    
    # Preencher choices
    form.school_class_id.choices = [(c.id, c.name) for c in SchoolClass.query.all()]
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    
    if current_user.role.name == 'professor':
        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        form.teacher_id.choices = [(teacher.id, teacher.name)] if teacher else []
    else:
        form.teacher_id.choices = [(t.id, t.name) for t in Teacher.query.filter_by(status='ativo').all()]
        
    form.period_id.choices = [(p.id, f"{p.name} ({p.school_year.year})") for p in Period.query.all()]
    
    if form.validate_on_submit():
        if not can_teacher_manage_assessment(current_user, form.school_class_id.data, form.subject_id.data):
            flash('Você não tem permissão para criar avaliação para esta disciplina nesta turma.', 'danger')
            return redirect(url_for('assessments.create'))
            
        data = {
            'title': form.title.data,
            'assessment_type': form.assessment_type.data,
            'school_class_id': form.school_class_id.data,
            'subject_id': form.subject_id.data,
            'teacher_id': form.teacher_id.data,
            'period_id': form.period_id.data,
            'date': form.date.data,
            'max_value': form.max_value.data,
            'weight': form.weight.data,
            'description': form.description.data
        }
        assessment = create_assessment(data)
        flash('Avaliação criada com sucesso!', 'success')
        return redirect(url_for('assessments.index'))
        
    return render_template('assessments/form.html', form=form, title="Nova Avaliação")

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@permission_required('assessments.edit')
def edit(id):
    assessment = Assessment.query.get_or_404(id)
    if assessment.status != 'ativa':
        flash('Avaliações arquivadas não podem ser editadas.', 'danger')
        return redirect(url_for('assessments.index'))
        
    if not can_teacher_manage_assessment(current_user, assessment.school_class_id, assessment.subject_id):
        abort(403)
        
    form = AssessmentForm(obj=assessment)
    form.school_class_id.choices = [(c.id, c.name) for c in SchoolClass.query.all()]
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    form.teacher_id.choices = [(t.id, t.name) for t in Teacher.query.all()]
    form.period_id.choices = [(p.id, f"{p.name} ({p.school_year.year})") for p in Period.query.all()]
    
    if form.validate_on_submit():
        data = {
            'title': form.title.data,
            'assessment_type': form.assessment_type.data,
            'date': form.date.data,
            'max_value': form.max_value.data,
            'weight': form.weight.data,
            'description': form.description.data
            # impedindo troca de turma/disciplina na edição para evitar inconsistência
        }
        update_assessment(assessment, data)
        flash('Avaliação atualizada com sucesso!', 'success')
        return redirect(url_for('assessments.index'))
        
    return render_template('assessments/form.html', form=form, title="Editar Avaliação", assessment=assessment)

@bp.route('/<int:id>/arquivar', methods=['POST'])
@permission_required('assessments.delete')
def archive(id):
    assessment = Assessment.query.get_or_404(id)
    if not can_teacher_manage_assessment(current_user, assessment.school_class_id, assessment.subject_id):
        abort(403)
        
    archive_assessment(assessment)
    flash('Avaliação arquivada com sucesso.', 'success')
    return redirect(url_for('assessments.index'))

@bp.route('/<int:id>/notas', methods=['GET', 'POST'])
@permission_required('grades.create')
def grades(id):
    assessment = Assessment.query.get_or_404(id)
    if assessment.status != 'ativa':
        flash('Esta avaliação está arquivada.', 'danger')
        return redirect(url_for('assessments.index'))
        
    if not can_teacher_manage_assessment(current_user, assessment.school_class_id, assessment.subject_id):
        abort(403)
        
    form = GradeBatchForm()
    
    # Buscar alunos matriculados ativos
    enrollments = Enrollment.query.filter_by(
        school_class_id=assessment.school_class_id,
        status='ativa'
    ).all()
    
    # Criar um dict das notas já lançadas para os inputs
    existing_grades = {g.student_id: g for g in assessment.grades}
    
    if form.validate_on_submit():
        grades_data = request.form.to_dict()
        filtered_data = {k.replace('grade_', ''): v for k, v in grades_data.items() if k.startswith('grade_')}
        
        success, result = process_grade_batch(assessment.id, filtered_data)
        if success:
            flash(f'{result} notas processadas com sucesso!', 'success')
            return redirect(url_for('assessments.index'))
        else:
            for err in result:
                flash(err, 'danger')
                
    return render_template('assessments/grades.html', assessment=assessment, form=form, enrollments=enrollments, existing_grades=existing_grades)
