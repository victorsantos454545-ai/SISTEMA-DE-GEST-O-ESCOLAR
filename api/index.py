import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
    env = os.environ.get('FLASK_ENV', 'production')
    app = create_app(env)
except Exception as e:
    tb = traceback.format_exc()
    def app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [f"<h1>Startup Debug Info</h1><pre>{tb}</pre>".encode('utf-8')]
