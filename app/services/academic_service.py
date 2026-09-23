from app.models import Grade, Assessment, Period, SchoolClass, Subject, Student, Enrollment
from sqlalchemy.orm import joinedload
from app.extensions import db

# Configurações provisórias de arredondamento e notas (podem vir do banco no futuro)
MINIMUM_PASSING_GRADE = 6.0
MAXIMUM_GRADE = 10.0

def _round_grade(value):
    """Arredonda a nota para 2 casas decimais, ou conforme regra da escola."""
    if value is None:
        return None
    return round(value, 2)

def calculate_student_subject_average(student_id, subject_id, school_class_id):
    """Calcula a média final do aluno em uma disciplina específica na turma atual."""
    assessments = Assessment.query.filter_by(
        subject_id=subject_id, 
        school_class_id=school_class_id, 
        status='ativa'
    ).all()
    
    if not assessments:
        return None, "Sem avaliações"
    
    total_weight = 0.0
    total_score = 0.0
    has_grades = False
    
    for assessment in assessments:
        grade = Grade.query.filter_by(
            student_id=student_id, 
            assessment_id=assessment.id
        ).first()
        
        if grade and grade.value is not None:
            has_grades = True
            w = assessment.weight or 1.0
            total_score += grade.value * w
            total_weight += w
            
    if not has_grades or total_weight == 0:
        return None, "Em andamento"
        
    avg = _round_grade(total_score / total_weight)
    status = "Aprovado" if avg >= MINIMUM_PASSING_GRADE else "Recuperação"
    return avg, status

def get_student_report_card(student_id, school_year_id):
    """Gera o boletim acadêmico de um aluno num ano letivo."""
    student = Student.query.get(student_id)
    if not student:
        return None
        
    enrollment = Enrollment.query.filter_by(student_id=student_id, school_year_id=school_year_id).first()
    if not enrollment:
        return None
        
    school_class = enrollment.school_class
    
    # Pega todos os períodos
    periods = Period.query.filter_by(school_year_id=school_year_id).order_by(Period.sequence).all()
    
    # Disciplinas da turma
    subjects = [link.subject for link in school_class.subject_links]
    
    report_data = {
        'student': student,
        'school_class': school_class,
        'enrollment': enrollment,
        'periods': periods,
        'subjects': []
    }
    
    for subject in subjects:
        subj_data = {
            'subject': subject,
            'periods': {},
            'final_average': None,
            'status': "Sem notas"
        }
        
        # Para cada período, achar avaliações ativas
        for period in periods:
            assessments = Assessment.query.filter_by(
                subject_id=subject.id,
                school_class_id=school_class.id,
                period_id=period.id,
                status='ativa'
            ).all()
            
            p_total_score = 0.0
            p_total_weight = 0.0
            p_has_grades = False
            
            for asmnt in assessments:
                grd = Grade.query.filter_by(student_id=student.id, assessment_id=asmnt.id).first()
                if grd and grd.value is not None:
                    p_has_grades = True
                    w = asmnt.weight or 1.0
                    p_total_score += grd.value * w
                    p_total_weight += w
                    
            if p_has_grades and p_total_weight > 0:
                subj_data['periods'][period.id] = _round_grade(p_total_score / p_total_weight)
            else:
                subj_data['periods'][period.id] = None
                
        # Media final
        final_avg, status = calculate_student_subject_average(student.id, subject.id, school_class.id)
        subj_data['final_average'] = final_avg
        subj_data['status'] = status
        
        report_data['subjects'].append(subj_data)
        
    return report_data
