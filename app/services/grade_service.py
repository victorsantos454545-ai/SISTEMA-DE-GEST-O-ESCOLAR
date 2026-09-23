from app.models import Grade, Assessment, Enrollment
from app.extensions import db
from app.services.audit_service import log_action

def save_grade(student_id, assessment_id, value, observation=None):
    """Cria ou atualiza uma nota individual."""
    assessment = Assessment.query.get(assessment_id)
    if not assessment or assessment.status != 'ativa':
        raise ValueError("Avaliação não encontrada ou arquivada.")
        
    if value is not None and (value < 0 or value > assessment.max_value):
        raise ValueError(f"Nota inválida. Deve estar entre 0 e {assessment.max_value}.")
        
    # Validar se aluno está ativo na turma
    enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        school_class_id=assessment.school_class_id,
        status='ativa'
    ).first()
    
    if not enrollment:
        raise ValueError("Aluno não possui matrícula ativa nesta turma.")

    grade = Grade.query.filter_by(student_id=student_id, assessment_id=assessment_id).first()
    is_new = False
    if not grade:
        grade = Grade(student_id=student_id, assessment_id=assessment_id)
        db.session.add(grade)
        is_new = True
        
    old_value = grade.value
    grade.value = value
    grade.observation = observation
    db.session.commit()
    
    action = 'create_grade' if is_new else 'update_grade'
    desc = f"Lançou nota {value} para aluno {student_id} na aval. {assessment_id}" if is_new else f"Atualizou nota de {old_value} para {value} do aluno {student_id} na aval. {assessment_id}"
    log_action(action, entity='grades', entity_id=grade.id, description=desc)
    
    return grade

def process_grade_batch(assessment_id, grades_data):
    """Processa um lote de notas transacionalmente.
    grades_data: dict { student_id: value }
    """
    assessment = Assessment.query.get(assessment_id)
    if not assessment or assessment.status != 'ativa':
        raise ValueError("Avaliação não encontrada ou arquivada.")
        
    # Obtem matriculas validas para esta avaliacao (turma)
    valid_enrollments = Enrollment.query.filter_by(
        school_class_id=assessment.school_class_id,
        status='ativa'
    ).all()
    valid_student_ids = {e.student_id for e in valid_enrollments}

    processed = 0
    errors = []
    
    try:
        for student_id_str, val_str in grades_data.items():
            if not val_str or not val_str.strip():
                continue # ignora vazios no lote
                
            student_id = int(student_id_str)
            if student_id not in valid_student_ids:
                errors.append(f"Aluno {student_id} nao esta matriculado nesta turma.")
                continue

            try:
                value = float(val_str.replace(',', '.'))
            except ValueError:
                errors.append(f"Aluno {student_id}: Valor de nota inválido '{val_str}'")
                continue
                
            if value < 0 or value > assessment.max_value:
                errors.append(f"Aluno {student_id}: Nota fora do limite (0 - {assessment.max_value})")
                continue
                
            grade = Grade.query.filter_by(student_id=student_id, assessment_id=assessment_id).first()
            if not grade:
                grade = Grade(student_id=student_id, assessment_id=assessment_id)
                db.session.add(grade)
            grade.value = value
            processed += 1
            
        if errors:
            db.session.rollback()
            return False, errors
            
        db.session.commit()
        log_action('batch_grade', entity='assessments', entity_id=assessment_id, description=f"Lançamento em lote processado para aval. {assessment_id}: {processed} notas")
        return True, processed
    except Exception as e:
        db.session.rollback()
        raise e
