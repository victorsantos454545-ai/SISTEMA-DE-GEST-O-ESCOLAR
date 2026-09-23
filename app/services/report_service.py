import csv
import io
try:
    import openpyxl
    import weasyprint
except ImportError:
    openpyxl = None
    weasyprint = None

from datetime import datetime
from flask import render_template, current_app
from sqlalchemy import or_, and_, asc, desc
from app.extensions import db
from app.models import Student, SchoolClass, Enrollment, Grade, Assessment, Attendance, Activity, Teacher, Employee

def _apply_pagination(query, page, per_page):
    if not page or not per_page:
        return query.all(), None
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination

def generate_csv(headers, data, filename="relatorio.csv"):
    output = io.StringIO()
    # Adicionando BOM para garantir UTF-8 correto no Excel
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')
    writer.writerow(headers)
    for row in data:
        # Prevent CSV Injection
        clean_row = []
        for cell in row:
            if isinstance(cell, str) and cell.startswith(('=', '+', '-', '@')):
                clean_row.append(f"'{cell}")
            else:
                clean_row.append(cell)
        writer.writerow(clean_row)
    return output.getvalue(), filename

def generate_excel(headers, data, filename="relatorio.xlsx"):
    if not openpyxl:
        return b'Excel export requires openpyxl', filename
        
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Relatório"
    ws.append(headers)
    for row in data:
        ws.append(row)
    
    # Formatação básica
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue(), filename

def generate_pdf(html_content, filename="relatorio.pdf"):
    if not weasyprint:
        return html_content.encode('utf-8'), filename
        
    pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
    return pdf_bytes, filename

def get_students_report(filters, user, page=None, per_page=None):
    query = Student.query
    
    # RBAC Filters
    if user.role.name == 'responsavel':
        student_ids = [s.id for s in user.profile.students]
        query = query.filter(Student.id.in_(student_ids))
    elif user.role.name == 'professor':
        class_ids = [ct.class_id for ct in user.profile.class_links]
        query = query.join(Enrollment).filter(
            Enrollment.school_class_id.in_(class_ids),
            Enrollment.status == 'ativa'
        )
    elif user.role.name == 'aluno':
        query = query.filter(Student.id == user.profile.id)
        
    # User Filters
    if 'name' in filters and filters['name']:
        query = query.filter(Student.full_name.ilike(f"%{filters['name']}%"))
    if 'status' in filters and filters['status']:
        query = query.filter(Student.status == filters['status'])
    if 'school_class_id' in filters and filters['school_class_id']:
        query = query.join(Enrollment).filter(Enrollment.school_class_id == filters['school_class_id'])
    
    query = query.order_by(Student.full_name.asc())
    
    if page and per_page:
        return _apply_pagination(query, page, per_page)
    return query.all(), None
