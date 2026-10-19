import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

app = create_app(os.environ.get('FLASK_ENV', 'production'))

with app.app_context():
    try:
        db.create_all()
    except Exception:
        pass
