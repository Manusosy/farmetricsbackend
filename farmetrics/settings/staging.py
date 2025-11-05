"""
Staging-specific Django settings for Farmetrics project.
Similar to production but with some relaxed settings for testing.
"""

from .base import *

# Debug mode - False in staging
DEBUG = False

# Security settings (less strict than production)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600  # 1 hour (lower for staging)

# CORS - allow staging origins
CORS_ALLOW_ALL_ORIGINS = False

# Use Cloudinary for media in staging
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage' if config('USE_CLOUDINARY', default=False, cast=bool) else 'django.core.files.storage.FileSystemStorage'

# Email backend - use SMTP in staging
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Staging logging
LOGGING['handlers']['console']['level'] = 'INFO'
LOGGING['loggers']['apps']['level'] = 'INFO'

# Celery - use Redis in staging
CELERY_TASK_ALWAYS_EAGER = False

# Sentry environment
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment='staging',
    )

print("🚀 Running in STAGING mode")
