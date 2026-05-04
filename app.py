# app.py - Cinematch Flask Application
import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from config import config
import redis
from celery import Celery

# Initialize extensions
migrate = Migrate()
login_manager = LoginManager()
# Limiter will be initialized with app context
limiter = None

def create_celery_app(app=None):
    """Create Celery application"""
    app = app or create_app()
    celery = Celery(
        app.import_name,
        broker=app.config.get('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        backend=app.config.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'production')
    app.config.from_object(config[config_name])
    
    # Security: Handle proxy headers correctly
    if app.config.get('FORCE_HTTPS'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Import db from models and initialize extensions with app
    from models import db
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure limiter with Redis storage
    global limiter
    redis_url = app.config.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=redis_url
    )
    limiter.init_app(app)
    
    # Configure CORS
    CORS(app, 
         origins=app.config.get('CORS_ORIGINS', ['*']),
         supports_credentials=True)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.session_protection = 'strong'
    
    # Set up logging
    setup_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)

    # Auth rate limits and payment security disabled — homepage only mode
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        if app.config.get('FLASK_ENV') == 'production':
            headers = app.config.get('SECURITY_HEADERS', {})
            for header, value in headers.items():
                response.headers[header] = value
        
        # Add cache-busting headers for HTML pages to prevent caching issues
        if response.content_type and 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    
    # Health check endpoint
    @app.route('/health')
    @limiter.exempt
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            # Check database connection
            from sqlalchemy import text
            from models import db
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        # Check Redis connection
        try:
            redis_client = redis.from_url(app.config.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))
            redis_client.ping()
            redis_status = 'healthy'
        except Exception as e:
            redis_status = f'unhealthy: {str(e)}'
        
        health_status = {
            'status': 'healthy' if db_status == 'healthy' and redis_status == 'healthy' else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': db_status,
                'redis': redis_status
            }
        }
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    
    # Main route
    @app.route('/')
    def index():
        """Main application page"""
        if app.config.get('MAINTENANCE_MODE'):
            return render_template('maintenance.html'), 503
        return render_template('index.html')

    # About page
    @app.route('/about')
    def about():
        """About page for Reddit OAuth and general information"""
        return render_template('about.html')

    return app


def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Set up file handler
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/cinematch.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        # Set logging level
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        app.logger.info('Cinematch startup')

def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f"Bad request: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad request', 'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'}), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        app.logger.warning(f"Unauthorized access attempt: {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"Forbidden access: {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        app.logger.warning(f"Method not allowed: {request.method} {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Method not allowed', 'message': f'{request.method} is not allowed for this endpoint'}), 405
        return render_template('errors/405.html'), 405

    @app.errorhandler(429)
    def ratelimit_handler(error):
        app.logger.warning(f"Rate limit exceeded: {request.remote_addr} on {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Rate limit exceeded', 'message': str(error.description)}), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(error):
        from models import db
        db.session.rollback()
        app.logger.error(f"Internal server error: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(502)
    def bad_gateway_error(error):
        app.logger.error(f"Bad gateway error: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad gateway', 'message': 'Upstream service unavailable'}), 502
        return render_template('errors/502.html'), 502

    @app.errorhandler(503)
    def service_unavailable_error(error):
        app.logger.error(f"Service unavailable: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Service unavailable', 'message': 'The service is temporarily unavailable'}), 503
        return render_template('errors/503.html'), 503

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Global exception handler for uncaught exceptions"""
        from models import db
        db.session.rollback()
        app.logger.error(f"Unhandled exception: {type(error).__name__}: {error}", exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500


def register_blueprints(app):
    """Register application blueprints - homepage only mode"""
    app.logger.info("Running in homepage-only mode — no blueprints or APIs loaded")

def register_cli_commands(app):
    """Register CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        from models import db, User, Session, APIKey, ContentKeyword
        db.create_all()
        print("Database initialized!")
    
    @app.cli.command()
    def create_admin():
        """Create admin user"""
        from models import User, db
        import getpass
        
        username = input("Admin username: ")
        email = input("Admin email: ")
        password = getpass.getpass("Admin password: ")
        
        admin = User(
            username=username,
            email=email,
            is_admin=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user {username} created successfully!")
    
    @app.cli.command()
    def load_default_keywords():
        """Load default content filtering keywords"""
        from models import ContentKeyword, db
        
        # Default keywords for content filtering
        keywords = [
            ('mature', 'violence', 1.0),
            ('mature', 'gore', 1.5),
            ('mature', 'horror', 0.8),
            ('restricted', 'explicit', 2.0),
            ('restricted', 'adult', 2.0),
            ('family', 'animated', -1.0),
            ('family', 'disney', -1.0),
            ('family', 'pixar', -1.0),
        ]
        
        for category, keyword, weight in keywords:
            kw = ContentKeyword(
                category=category,
                keyword=keyword,
                weight=weight
            )
            db.session.add(kw)
        
        db.session.commit()
        print("Default keywords loaded!")

# Create application instance
app = create_app()
celery = create_celery_app(app)

# Import models to ensure they're registered
with app.app_context():
    from models import User, Session, APIKey, ContentKeyword, MovieDocument, ChatLog

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    from models import User
    return User.query.get(user_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)