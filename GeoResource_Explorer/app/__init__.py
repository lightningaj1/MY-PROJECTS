from flask import Flask
from .utils import is_admin
import os

def create_app():
    # Get the parent directory (GeoResource_Explorer)
    instance_path = os.path.dirname(os.path.dirname(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(instance_path, 'templates'),
                static_folder=os.path.join(instance_path, 'static'))
    app.secret_key = "your_secret_key_here"

    @app.context_processor
    def inject_admin():
        return dict(is_admin=is_admin())

    from .routes import register_routes
    register_routes(app)

    return app
