import pytest
from app.services.attendance_service import calculate_student_attendance
from app.models import Attendance, SystemConfig
from datetime import date

def test_calculate_attendance_empty(app):
    """Testa estatísticas de um aluno sem registros."""
    with app.app_context():
        stats = calculate_student_attendance(999, 999)
        assert stats['total'] == 0
        assert stats['percentage'] == 100.0
        assert stats['status'] == 'Sem dados suficientes'

def test_attendance_service_import(app):
    """Testa se o service não quebra imports."""
    from app.services.attendance_service import process_attendance_batch
    assert process_attendance_batch is not None
