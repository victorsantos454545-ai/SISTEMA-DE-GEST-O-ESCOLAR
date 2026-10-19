import sys
import os

# Adiciona a raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)
