from flask import Flask
from app.utils import is_admin

def create_app():
    app = Flask(__name__)
    app.secret_key = "your_secret_key_here"

    @app.context_processor
    def inject_admin():
        return dict(is_admin=is_admin())

    from app.routes import register_routes
    register_routes(app)

    return app
