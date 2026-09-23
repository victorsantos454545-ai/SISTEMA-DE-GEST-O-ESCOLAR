import secrets
from datetime import datetime, timezone, timedelta
from app.extensions import db


class PasswordResetToken(db.Model):
    """Tokens para recuperacao de senha.

    Tokens sao de uso unico, possuem expiracao (1 hora por padrao)
    e sao armazenados como hash para seguranca.
    """
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token_hash = db.Column(db.String(256), nullable=False, index=True)
    used = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relacionamentos
    user = db.relationship('User', backref=db.backref('reset_tokens', lazy='dynamic'))

    @staticmethod
    def generate_token():
        """Gera um token seguro aleatorio."""
        return secrets.token_urlsafe(48)

    @staticmethod
    def hash_token(token):
        """Cria hash do token para armazenamento seguro."""
        import hashlib
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    @classmethod
    def create_for_user(cls, user, expiration_hours=1):
        """Cria um novo token de reset para o usuario."""
        token = cls.generate_token()
        reset = cls(
            user_id=user.id,
            token_hash=cls.hash_token(token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
        )
        db.session.add(reset)
        db.session.commit()
        return token  # Retorna o token em texto para enviar ao usuario

    @classmethod
    def verify_token(cls, token):
        """Verifica e retorna o token de reset se valido."""
        token_hash = cls.hash_token(token)
        reset = cls.query.filter_by(token_hash=token_hash, used=False).first()
        if reset is None:
            return None
        if reset.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None
        return reset

    def invalidate(self):
        """Marca o token como utilizado."""
        self.used = True
        db.session.commit()

    def __repr__(self):
        return f'<PasswordResetToken user={self.user_id} used={self.used}>'
