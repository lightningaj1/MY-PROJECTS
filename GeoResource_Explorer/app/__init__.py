from flask import Flask
from .utils import is_admin
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import os
import secrets

def create_app():
    # Get the parent directory (GeoResource_Explorer)
    instance_path = os.path.dirname(os.path.dirname(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(instance_path, 'templates'),
                static_folder=os.path.join(instance_path, 'static'))
    
    # Security: Load secret key from environment or generate secure default
    app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Security: CSRF Protection
    csrf = CSRFProtect(app)
    
    # Security: Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Performance: Caching configuration
    cache_config = {
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    cache = Cache(app, config=cache_config)
    
    # Security: Session configuration
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    
    # Security: File upload limits
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
    
    @app.context_processor
    def inject_admin():
        return dict(is_admin=is_admin())
    
    # Security: Add security headers to all responses
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        # Updated CSP to allow map tiles, Font Awesome icons, and external resources needed for functionality
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com unpkg.com; style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com fonts.googleapis.com fonts.gstatic.com unpkg.com; img-src 'self' data: https://*.tile.openstreetmap.org https://*.openstreetmap.org https://*.leafletjs.com *.unpkg.com; font-src 'self' fonts.gstatic.com cdnjs.cloudflare.com https://cdnjs.cloudflare.com; connect-src 'self' https://*.tile.openstreetmap.org https://*.openstreetmap.org https://*.leafletjs.com *.unpkg.com"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
    
    # Security: Error handlers that don't leak information
    @app.errorhandler(404)
    def page_not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        return {'error': 'Internal server error'}, 500

    # Database connection management
    from .db import init_db_connection
    init_db_connection(app)

    from .routes import register_routes
    register_routes(app)

    return app
