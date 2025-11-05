"""
Django settings package for Farmetrics project.

This module loads the appropriate settings based on DJANGO_ENVIRONMENT.
"""

import os
from decouple import config

# Determine which settings to load
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'staging':
    from .staging import *
else:
    from .development import *
