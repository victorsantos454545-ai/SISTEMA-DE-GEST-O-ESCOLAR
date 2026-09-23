import os
from flask import Flask, render_template
from config import config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_name='development'):
    """Application Factory: cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configurar Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        """Carrega o usuário pelo ID (exigido pelo Flask-Login)."""
        from app.models.user import User
        return db.session.get(User, int(user_id))

    # Importar models para que Flask-Migrate os detecte
    from app import models  # noqa: F401

    # Registrar blueprints
    _register_blueprints(app)

    # Registrar error handlers
    _register_error_handlers(app)

    # Registrar comandos CLI
    _register_cli_commands(app)

    # Criar diretório instance se não existir
    os.makedirs(app.instance_path, exist_ok=True)

    # Context processor para variáveis globais nos templates
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        return {
            'school_name': app.config.get('SCHOOL_NAME', 'SGE'),
            'school_abbreviation': app.config.get('SCHOOL_ABBREVIATION', 'SGE'),
        }

    # Headers de Segurança
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Evita setar CSP rígida que quebre CSS inline (Bootstrap/Select2) a não ser que planejado
        return response

    return app


def _register_blueprints(app):
    """Registra todos os blueprints da aplicação."""
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.users import users_bp
    app.register_blueprint(users_bp)
    
    from app.routes.students import students_bp
    app.register_blueprint(students_bp)
    
    from app.routes.guardians import guardians_bp
    app.register_blueprint(guardians_bp)
    from app.routes.teachers import bp as teachers_bp
    app.register_blueprint(teachers_bp)

    from app.routes.calendar import bp as calendar_bp
    app.register_blueprint(calendar_bp)

    from app.routes.schedules import bp as schedules_bp
    app.register_blueprint(schedules_bp)

    # (removed api_docs)
    
    from app.routes.employees import bp as employees_bp
    app.register_blueprint(employees_bp)

    from app.routes.school_classes import bp as classes_bp
    app.register_blueprint(classes_bp)
    
    from app.routes.subjects import bp as subjects_bp
    app.register_blueprint(subjects_bp)

    from app.routes.enrollments import bp as enrollments_bp
    app.register_blueprint(enrollments_bp)
    
    from app.routes.assessments import bp as assessments_bp
    app.register_blueprint(assessments_bp)
    
    from app.routes.academic import bp as academic_bp
    app.register_blueprint(academic_bp)

    from app.routes.attendance import bp as attendance_bp
    app.register_blueprint(attendance_bp)

    from app.routes.activities import bp as activities_bp
    app.register_blueprint(activities_bp)

    from app.routes.announcements import announcements_bp
    app.register_blueprint(announcements_bp)

    from app.routes.notifications import notifications_bp
    app.register_blueprint(notifications_bp)
    
    from app.routes.reports import reports_bp
    app.register_blueprint(reports_bp)


def _register_error_handlers(app):
    """Registra handlers para erros HTTP."""

    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500


def _register_cli_commands(app):
    """Registra comandos CLI do Flask."""
    from app.cli import register_commands
    register_commands(app)
