"""
Farmetrics package initialization.
This will make sure the Celery app is always imported when
Django starts so that shared_task will use this app.
"""

try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not installed - this is OK for development
    celery_app = None
    __all__ = ()

