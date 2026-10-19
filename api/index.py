import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

app = create_app(os.environ.get('FLASK_ENV', 'production'))

with app.app_context():
    try:
        db.create_all()
        from app.models.user import User
        if not User.query.filter_by(username='admin').first():
            from app.services.seed_service import seed_all_permissions
            seed_all_permissions()
            import seed
            seed.seed_admin_user()
            seed.seed_school_year()
    except Exception as e:
        print("Auto-seed notice:", e)
