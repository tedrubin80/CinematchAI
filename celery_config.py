# celery_config.py - Celery configuration for background tasks

from datetime import timedelta
from celery import Celery
from app import create_app
import os

def make_celery(app):
    """Create Celery instance and configure it"""
    
    celery = Celery(
        app.import_name,
        broker=app.config.get('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        backend=app.config.get('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        include=['scraping_tasks']
    )
    
    # Celery configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )
    
    # Periodic task schedule
    celery.conf.beat_schedule = {
        'scrape-imdb-top-movies': {
            'task': 'scraping_tasks.scrape_imdb_top_movies',
            'schedule': timedelta(hours=24),  # Daily
        },
        'scrape-recent-releases': {
            'task': 'scraping_tasks.scrape_recent_releases',
            'schedule': timedelta(hours=6),  # Every 6 hours
        },
        'scrape-genre-collections': {
            'task': 'scraping_tasks.scrape_genre_collections',
            'schedule': timedelta(hours=12),  # Twice daily
        },
        'cleanup-old-scraping-data': {
            'task': 'scraping_tasks.cleanup_old_data',
            'schedule': timedelta(days=7),  # Weekly
        }
    }
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Create app and celery instance
# Note: This will be initialized when imported by other modules
celery = None

def initialize_celery():
    """Initialize celery with app context"""
    global celery
    if celery is None:
        flask_app = create_app()
        celery = make_celery(flask_app)
    return celery