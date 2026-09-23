from flask import Blueprint, render_template, abort
from flask_login import current_user
from app.models import Student, SchoolClass, Enrollment
from app.services.academic_service import get_student_report_card
from app.utils.decorators import permission_required

bp = Blueprint('academic', __name__, url_prefix='/academico')

@bp.route('/aluno/<int:student_id>/boletim')
@permission_required('grades.view')
def report_card(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Validação de isolamento
    if current_user.role.name == 'aluno':
        if student.user_id != current_user.id:
            abort(403)
    elif current_user.role.name == 'responsavel':
        from app.models.guardian import Guardian
        guardian = Guardian.query.filter_by(user_id=current_user.id).first()
        if not guardian or student not in guardian.students:
            abort(403)
            
    # Assumindo matrícula mais recente ou um seletor no frontend
    enrollment = Enrollment.query.filter_by(student_id=student_id).order_by(Enrollment.enrollment_date.desc()).first()
    if not enrollment:
        return render_template('academic/report_card.html', report_data=None, student=student)
        
    report_data = get_student_report_card(student_id, enrollment.school_year_id)
    return render_template('academic/report_card.html', report_data=report_data, student=student)

@bp.route('/turma/<int:class_id>/desempenho')
@permission_required('grades.view')
def class_performance(class_id):
    school_class = SchoolClass.query.get_or_404(class_id)
    # Lógica similar isolando professores que não dão aula aqui
    return render_template('academic/performance.html', school_class=school_class)
