import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Configuração base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-temporaria-trocar-em-producao'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # Sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True  # Impede acesso via JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protege contra CSRF via links externos

    # Paginação
    ITEMS_PER_PAGE = 20

    # Configurações da escola (padrões)
    SCHOOL_NAME = os.environ.get('SCHOOL_NAME', 'Sistema de Gestão Escolar')
    SCHOOL_ABBREVIATION = os.environ.get('SCHOOL_ABBREVIATION', 'SGE')

    # Configurações de e-mail (para recuperação de senha)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@escola.com')

    # Segurança - tentativas de login
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    LOCKOUT_DURATION_MINUTES = int(os.environ.get('LOCKOUT_DURATION_MINUTES', 15))


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'sge_dev.db')
    # Em desenvolvimento, SESSION_COOKIE_SECURE é False (sem HTTPS local)
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Configuração de testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Configuração de produção."""
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url and _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif _db_url and _db_url.startswith('postgresql://'):
        _db_url = _db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    # Em produção com HTTPS, habilitar cookie seguro
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
