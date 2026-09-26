from app.models import Attendance, Enrollment, SystemConfig
from app.extensions import db
from app.services.audit_service import log_action
from sqlalchemy import func

def _get_min_attendance():
    config = SystemConfig.query.filter_by(key='frequencia_minima').first()
    if config and config.value:
        try:
            return float(config.value)
        except ValueError:
            pass
    return 75.0

def process_attendance_batch(teacher_id, school_class_id, subject_id, date, period, attendance_data):
    """
    Processa chamada em lote.
    attendance_data: dict { student_id: {'status': 'presente'|'ausente'|'justificado', 'justification': '...'} }
    """
    if isinstance(date, str):
        from datetime import datetime
        date = datetime.strptime(date, '%Y-%m-%d').date()

    processed = 0
    
    # Obtem matriculas validas para esta turma
    valid_enrollments = Enrollment.query.filter_by(
        school_class_id=school_class_id,
        status='ativa'
    ).all()
    valid_student_ids = {e.student_id for e in valid_enrollments}

    try:
        for student_id_str, data in attendance_data.items():
            student_id = int(student_id_str)
            if student_id not in valid_student_ids:
                continue # Pula IDs invalidos enviados forcadamente

            status = data.get('status', 'presente')
            justification = data.get('justification', '')
            
            present = (status == 'presente')
            if status == 'ausente':
                justification = '' # Limpa se mudou pra ausente sem justificar
                
            att = Attendance.query.filter_by(
                student_id=student_id, 
                school_class_id=school_class_id, 
                subject_id=subject_id, 
                date=date
            ).first()
            
            is_new = False
            if not att:
                att = Attendance(
                    student_id=student_id,
                    school_class_id=school_class_id,
                    subject_id=subject_id,
                    date=date
                )
                db.session.add(att)
                is_new = True
                
            att.teacher_id = teacher_id
            att.period = period
            att.present = present
            att.justification = justification if not present else None
            processed += 1
            
        db.session.commit()
        log_action('batch_attendance', entity='attendance', entity_id=school_class_id, description=f"Chamada registrada: {processed} alunos")
        return True, processed
    except Exception as e:
        db.session.rollback()
        raise e

def calculate_student_attendance(student_id, school_class_id, subject_id=None):
    """
    Calcula estatísticas de frequência do aluno.
    Se subject_id for fornecido, calcula específico para a disciplina.
    """
    query = Attendance.query.filter_by(student_id=student_id, school_class_id=school_class_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
        
    attendances = query.all()
    
    total = len(attendances)
    if total == 0:
        return {
            'total': 0, 'present': 0, 'absent': 0, 'justified': 0,
            'percentage': 100.0, 'status': 'Sem dados suficientes'
        }
        
    present = sum(1 for a in attendances if a.present)
    justified = sum(1 for a in attendances if not a.present and a.justification)
    absent = total - present - justified
    
    # Falta justificada conta como presença ou não afeta o cálculo dependendo da escola
    # Opção: Justificadas contam positivamente ou são abatidas do total.
    # Vamos considerar que falta justificada (abono) abona a falta (na prática conta como presença para o percentual).
    # Ou podemos simplesmente usar (present + justified) / total.
    # Para ser neutro: percentage = (present + justified) / total * 100
    percentage = ((present + justified) / total) * 100
    
    min_perc = _get_min_attendance()
    alert_perc = min_perc + 5.0
    
    if percentage < min_perc:
        status_label = 'Abaixo do mínimo'
    elif percentage < alert_perc:
        status_label = 'Atenção'
    else:
        status_label = 'Frequência normal'
        
    return {
        'total': total,
        'present': present,
        'absent': absent,
        'justified': justified,
        'percentage': round(percentage, 1),
        'status': status_label,
        'min_perc': min_perc
    }

def update_attendance_record(attendance_id, present, justification=None):
    att = Attendance.query.get(attendance_id)
    if not att:
        raise ValueError("Registro não encontrado")
        
    att.present = present
    att.justification = justification if not present else None
    db.session.commit()
    log_action('update_attendance', entity='attendance', entity_id=att.id, description=f"Corrigiu presença para {present}")
    return att
