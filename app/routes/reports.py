import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app, Response
from flask_login import login_required, current_user
import io

from app.services.report_service import (
    get_students_report, 
    generate_csv, generate_excel, generate_pdf
)
from app.services.report_card_service import get_full_report_card
from app.models import SchoolYear, SchoolClass, Subject, Period, Student
from app.extensions import db

reports_bp = Blueprint('reports', __name__, url_prefix='/relatorios')

@reports_bp.route('/')
@login_required
def index():
    if not current_user.has_any_permission('reports.view'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
    return render_template('reports/index.html')

@reports_bp.route('/alunos')
@login_required
def students_report():
    if not current_user.has_any_permission('reports.view'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    page = request.args.get('page', 1, type=int)
    filters = {
        'name': request.args.get('name', ''),
        'status': request.args.get('status', ''),
        'school_class_id': request.args.get('school_class_id', type=int)
    }
    
    export_format = request.args.get('export')
    
    # Se for exportação, busca sem paginação
    if export_format:
        students, _ = get_students_report(filters, current_user)
        headers = ['ID', 'Nome Completo', 'Data Nasc.', 'Matrícula', 'Turmas', 'Status']
        data = []
        for s in students:
            turmas = ', '.join([e.school_class.name for e in s.enrollments if e.status == 'ativa'])
            data.append([
                s.id, 
                s.full_name, 
                s.birth_date.strftime('%d/%m/%Y') if s.birth_date else '',
                s.cpf, # Apenas demonstrativo
                turmas, 
                s.status.capitalize()
            ])
            
        if export_format == 'csv':
            csv_content, filename = generate_csv(headers, data, "relatorio_alunos.csv")
            return Response(csv_content, mimetype='text/csv', headers={"Content-Disposition": f"attachment;filename={filename}"})
        elif export_format == 'xlsx':
            excel_content, filename = generate_excel(headers, data, "relatorio_alunos.xlsx")
            return Response(excel_content, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={"Content-Disposition": f"attachment;filename={filename}"})
        elif export_format == 'pdf':
            html = render_template('reports/pdf_students.html', students=students, filters=filters)
            pdf_content, filename = generate_pdf(html, "relatorio_alunos.pdf")
            return Response(pdf_content, mimetype='application/pdf', headers={"Content-Disposition": f"inline;filename={filename}"})

    # Visualização normal com paginação
    students, pagination = get_students_report(filters, current_user, page=page, per_page=15)
    classes = SchoolClass.query.filter_by(status='ativa').order_by(SchoolClass.name).all()
    
    return render_template('reports/students.html', 
                          students=students, 
                          pagination=pagination, 
                          filters=filters,
                          classes=classes)

@reports_bp.route('/boletim/<int:student_id>')
@login_required
def report_card(student_id):
    if not current_user.has_any_permission('reports.view'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    student = Student.query.get_or_404(student_id)
    
    # RBAC para aluno e responsável
    if current_user.role.name == 'aluno' and current_user.profile.id != student.id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
    if current_user.role.name == 'responsavel':
        student_ids = [s.id for s in current_user.profile.students]
        if student.id not in student_ids:
            flash('Acesso negado.', 'danger')
            return redirect(url_for('main.dashboard'))
            
    # Pega o ano letivo ativo ou selecionado
    year_id = request.args.get('year_id', type=int)
    if not year_id:
        current_year = SchoolYear.query.filter_by(is_current=True).first()
        if current_year:
            year_id = current_year.id
            
    report = None
    if year_id:
        report = get_full_report_card(student.id, year_id)
        
    export_format = request.args.get('export')
    if export_format == 'pdf' and report:
        html = render_template('reports/pdf_report_card.html', report=report)
        pdf_content, filename = generate_pdf(html, f"boletim_{student.full_name}.pdf")
        return Response(pdf_content, mimetype='application/pdf', headers={"Content-Disposition": f"inline;filename={filename}"})
        
    years = SchoolYear.query.order_by(SchoolYear.start_date.desc()).all()
    
    return render_template('reports/report_card.html', 
                           student=student, 
                           report=report, 
                           years=years,
                           year_id=year_id)
