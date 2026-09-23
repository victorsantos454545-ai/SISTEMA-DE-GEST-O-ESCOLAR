from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app.extensions import db
from app.models.base import TimestampMixin


class User(UserMixin, TimestampMixin, db.Model):
    """Usuarios do sistema.

    Cada usuario possui uma Role que define seu nivel de acesso.
    Opcionalmente, pode estar vinculado a um perfil especifico
    (Student, Teacher, Guardian, Employee) via relacionamento one-to-one.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)
    last_password_change = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime)

    # Relacionamentos
    role = db.relationship('Role', back_populates='users')
    calendar_events = db.relationship('CalendarEvent', back_populates='creator', lazy='dynamic')
    announcements = db.relationship('Announcement', back_populates='author', lazy='dynamic')

    def set_password(self, password):
        """Armazena o hash seguro da senha (nunca texto puro)."""
        self.password_hash = generate_password_hash(password)
        self.last_password_change = datetime.now(timezone.utc)

    def check_password(self, password):
        """Verifica a senha contra o hash armazenado."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        """Retorna se o usuario esta ativo (exigido pelo Flask-Login)."""
        return self.active

    @property
    def is_locked(self):
        """Verifica se a conta esta bloqueada temporariamente."""
        if self.locked_until is None:
            return False
        now = datetime.now(timezone.utc)
        locked = self.locked_until.replace(tzinfo=timezone.utc) if self.locked_until.tzinfo is None else self.locked_until
        if now >= locked:
            self.locked_until = None
            self.failed_login_attempts = 0
            db.session.commit()
            return False
        return True

    def record_failed_login(self, max_attempts=5, lockout_minutes=15):
        """Registra tentativa de login falha e bloqueia se necessario."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            from datetime import timedelta
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=lockout_minutes)
        db.session.commit()

    def record_successful_login(self):
        """Registra login bem-sucedido."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()

    def has_permission(self, permission_name):
        """Verifica se o usuario possui a permissao especificada via sua Role."""
        if self.role.name == 'admin':
            return True
        return any(p.name == permission_name for p in self.role.permissions)

    def has_any_permission(self, *permission_names):
        """Verifica se o usuario possui pelo menos uma das permissoes."""
        if self.role.name == 'admin':
            return True
        user_perms = {p.name for p in self.role.permissions}
        return bool(user_perms & set(permission_names))

    @property
    def profile(self):
        """Retorna o perfil vinculado ao usuario (Student, Teacher, etc.)."""
        if hasattr(self, 'student_profile') and self.student_profile:
            return self.student_profile
        if hasattr(self, 'teacher_profile') and self.teacher_profile:
            return self.teacher_profile
        if hasattr(self, 'guardian_profile') and self.guardian_profile:
            return self.guardian_profile
        if hasattr(self, 'employee_profile') and self.employee_profile:
            return self.employee_profile
        return None

    @property
    def display_name(self):
        """Retorna o nome para exibicao."""
        p = self.profile
        if p and hasattr(p, 'full_name'):
            return p.full_name
        return self.username

    def __repr__(self):
        return f'<User {self.username}>'
