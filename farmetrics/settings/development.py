"""
Development-specific Django settings for Farmetrics project.
"""

from .base import *

# Note: All base settings are imported above
# Development-specific overrides below

# Debug mode
DEBUG = True

# Development-specific apps
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# Development middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Internal IPs for Django Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Email backend - console for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use local file storage in development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Disable template caching in development
for template_engine in TEMPLATES:
    template_engine['OPTIONS']['debug'] = True

# Relaxed CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# Security settings - relaxed for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Development logging - more verbose
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# Celery - eager execution for easier debugging
CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=True, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = True

# Development-specific settings
ALLOWED_HOSTS = ['*']  # Allow all hosts in development

print("🚀 Running in DEVELOPMENT mode")

