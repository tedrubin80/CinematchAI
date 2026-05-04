# config.py - Production Configuration

import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY environment variable is not set')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    FORCE_HTTPS = True
    
    # Admin
    ADMIN_SECRET_PATH = os.environ.get('ADMIN_SECRET_PATH')
    if not ADMIN_SECRET_PATH:
        raise ValueError('ADMIN_SECRET_PATH environment variable is not set')
    ALLOW_REGISTRATION = os.environ.get('ALLOW_REGISTRATION', 'False') == 'True'
    
    # DigitalOcean Spaces
    DO_SPACES_KEY = os.environ.get('DO_SPACES_KEY')
    DO_SPACES_SECRET = os.environ.get('DO_SPACES_SECRET')
    DO_SPACES_REGION = 'nyc3'
    DO_SPACES_ENDPOINT = 'https://nyc3.digitaloceanspaces.com'
    DO_SPACES_BUCKET = os.environ.get('DO_SPACES_BUCKET')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or os.environ.get('DATABASE_URL')
    RATELIMIT_DEFAULT = "1000 per day"
    RATELIMIT_HEADERS_ENABLED = True
    
    # CORS - No wildcard default for security
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else []
    
    # Encryption
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # OAuth Providers
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'False') == 'True'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Content settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_EXTENSIONS = ['.txt', '.pdf', '.json', '.csv']
    
    # Cache settings (using PostgreSQL)
    CACHE_TYPE = 'custom'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # =====================================================
    # WEB SCRAPING & INTELLIGENCE SYSTEM
    # =====================================================
    
    # API Keys for enhanced functionality
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    LLAMA_API_KEY = os.environ.get('LLAMA_API_KEY')
    OMDB_API_KEY = os.environ.get('OMDB_API_KEY')
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
    TMDB_READ_ACCESS_TOKEN = os.environ.get('TMDB_READ_ACCESS_TOKEN')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    
    # Scraping Configuration
    SCRAPING_ENABLED = os.environ.get('SCRAPING_ENABLED', 'True') == 'True'
    SCRAPING_USER_AGENT = os.environ.get('SCRAPING_USER_AGENT', 'Cinematch/1.0')
    SCRAPING_DELAY_MIN = float(os.environ.get('SCRAPING_DELAY_MIN', '2'))
    SCRAPING_DELAY_MAX = float(os.environ.get('SCRAPING_DELAY_MAX', '5'))
    MAX_CONCURRENT_SCRAPERS = int(os.environ.get('MAX_CONCURRENT_SCRAPERS', '3'))
    
    # Wikipedia Priority
    WIKIPEDIA_SCRAPING_ENABLED = os.environ.get('WIKIPEDIA_SCRAPING_ENABLED', 'True') == 'True'
    WIKIPEDIA_DELAY_SECONDS = int(os.environ.get('WIKIPEDIA_DELAY_SECONDS', '3'))
    
    # S3-Compatible Storage (requires environment variables)
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    S3_REGION = os.environ.get('S3_REGION', 'nbg1')
    ENABLE_S3_BACKUP = os.environ.get('ENABLE_S3_BACKUP', 'False') == 'True'  # Disabled by default until configured
    
    # Conversation Intelligence
    ENABLE_PERSONALITY_LAYER = os.environ.get('ENABLE_PERSONALITY_LAYER', 'True') == 'True'
    CONVERSATION_PATTERN_LEARNING = os.environ.get('CONVERSATION_PATTERN_LEARNING', 'True') == 'True'
    MOOD_DETECTION_THRESHOLD = float(os.environ.get('MOOD_DETECTION_THRESHOLD', '0.7'))
    SCRAPED_DATA_INSIGHT_FREQUENCY = float(os.environ.get('SCRAPED_DATA_INSIGHT_FREQUENCY', '0.3'))
    
    # Data Retention
    SCRAPED_DATA_RETENTION_MONTHS = int(os.environ.get('SCRAPED_DATA_RETENTION_MONTHS', '12'))
    ENABLE_DATA_COMPRESSION = os.environ.get('ENABLE_DATA_COMPRESSION', 'True') == 'True'
    
    # Celery Configuration for scheduled tasks
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # =====================================================
    # STRIPE PAYMENT CONFIGURATION
    # =====================================================
    
    # Stripe API Keys
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Stripe Price IDs for subscription tiers
    STRIPE_BASIC_PRICE_ID = os.environ.get('STRIPE_BASIC_PRICE_ID')
    STRIPE_PREMIUM_PRICE_ID = os.environ.get('STRIPE_PREMIUM_PRICE_ID')
    
    # Age Verification Settings
    REQUIRE_AGE_VERIFICATION = True
    MINIMUM_AGE = 13
    PARENTAL_CONSENT_REQUIRED_AGE = 18
    
    # Subscription Features
    SUBSCRIPTION_TIERS = {
        'free': {'queries_per_day': 10, 'features': ['basic']},
        'basic': {'queries_per_day': 100, 'features': ['basic', 'enhanced']},
        'premium': {'queries_per_day': float('inf'), 'features': ['all']}
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    SESSION_COOKIE_SECURE = False
    FORCE_HTTPS = False
    CORS_ORIGINS = []  # Development should specify exact origins

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Stricter security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_NAME = '__Host-session'  # Chrome security feature
    
    # Performance
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files
    
    # Additional security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Content-Security-Policy': "default-src 'self' https://apis.google.com; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://apis.google.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://apis.google.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.anthropic.com https://api.openai.com https://accounts.google.com; frame-src 'self' https://accounts.google.com https://apis.google.com;"
    }

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    WTF_CSRF_ENABLED = False
    
    # Use in-memory cache for tests
    CACHE_TYPE = 'simple'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}