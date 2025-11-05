"""
Celery configuration for Farmetrics project.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmetrics.settings.production')

app = Celery('farmetrics')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Example: Cleanup expired password reset tokens daily
    'cleanup-expired-tokens': {
        'task': 'apps.accounts.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    # Add more scheduled tasks here as needed
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')

