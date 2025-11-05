"""
Production-specific Django settings for Farmetrics project.
"""

from .base import *

# Note: All base settings are imported above
# Production-specific overrides below

# Debug mode - always False in production
DEBUG = False

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CORS - restrict to specific origins in production
CORS_ALLOW_ALL_ORIGINS = False
# CORS_ALLOWED_ORIGINS set in base.py from environment variable

# Static files - use WhiteNoise compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Use Cloudinary for media in production (if configured)
# Fallback to local storage if Cloudinary credentials are not set
USE_CLOUDINARY = config('USE_CLOUDINARY', default=False, cast=bool)
if USE_CLOUDINARY and config('CLOUDINARY_CLOUD_NAME', default=''):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # Use local storage if Cloudinary is not configured
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Email backend - use SMTP in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Sentry Configuration for error tracking
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,  # Sample 10% of transactions for performance monitoring
        send_default_pii=False,  # Don't send personally identifiable information
        environment=config('ENVIRONMENT', default='production'),
    )

# Production logging - structured JSON for log aggregation
# Update JSON formatter format while preserving the formatter class
if 'json' in LOGGING.get('formatters', {}):
    LOGGING['formatters']['json'].update({
        'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
    })
# Use JSON formatter for console in production (for log aggregation systems)
if 'console' in LOGGING.get('handlers', {}):
    LOGGING['handlers']['console']['formatter'] = 'json'
    LOGGING['handlers']['console']['level'] = 'WARNING'

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
}

# Cache - increase timeouts for production
CACHES['default']['TIMEOUT'] = 900  # 15 minutes

# Celery - production settings
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Admin site header
ADMIN_SITE_HEADER = 'Farmetrics Administration'

print("🚀 Running in PRODUCTION mode")

