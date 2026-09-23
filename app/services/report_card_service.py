from app.services.academic_service import get_student_report_card
from app.services.attendance_service import calculate_student_attendance
from app.models import Student, SchoolYear, Enrollment

def get_full_report_card(student_id, school_year_id):
    """
    Recupera o boletim acadêmico combinando notas e frequências.
    Reaproveita as lógicas existentes de academic_service e attendance_service.
    """
    report = get_student_report_card(student_id, school_year_id)
    if not report:
        return None
        
    enrollment = report['enrollment']
    school_class = report['school_class']
    
    # Adicionar frequência geral
    general_attendance = calculate_student_attendance(student_id, school_class.id)
    report['attendance'] = general_attendance
    
    # Adicionar frequência por disciplina
    for subj_data in report['subjects']:
        subject_id = subj_data['subject'].id
        subj_att = calculate_student_attendance(student_id, school_class.id, subject_id)
        subj_data['attendance'] = subj_att
        
    # Determinar a situação final do aluno com base na nota e frequência
    # As regras exatas podem depender da escola.
    min_perc = general_attendance.get('min_perc', 75.0)
    failed_by_absences = general_attendance['percentage'] < min_perc
    
    any_failed_subject = any(s['status'] == 'Reprovado' for s in report['subjects'])
    any_recovery = any(s['status'] == 'Recuperação' for s in report['subjects'])
    
    if failed_by_absences:
        report['final_status'] = 'Reprovado por Falta'
    elif any_failed_subject:
        report['final_status'] = 'Reprovado'
    elif any_recovery:
        report['final_status'] = 'Em Recuperação'
    else:
        # Só considera aprovado se tiver notas lançadas
        has_grades = any(s['final_average'] is not None for s in report['subjects'])
        if has_grades:
            report['final_status'] = 'Aprovado'
        else:
            report['final_status'] = 'Em andamento'
            
    return report
