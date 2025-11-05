"""
Verification script to check if backend is properly configured.
"""

import os
import sys
import django
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verify_imports():
    """Verify all critical imports work"""
    print("Checking imports...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmetrics.settings.development')
        django.setup()
        
        # Test app imports
        from apps.core.models import TimeStampedModel, SoftDeleteModel
        from apps.accounts.models import User
        from apps.organizations.models import Organization
        from apps.farmers.models import Farmer
        from apps.farms.models import Farm
        from apps.visits.models import Visit
        from apps.media.models import Media
        from apps.requests.models import Request
        from apps.notifications.models import Notification
        
        print("✅ All model imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def verify_urls():
    """Verify URL configuration"""
    try:
        from django.urls import reverse
        from farmetrics.urls import urlpatterns
        print(f"✅ URL configuration loaded ({len(urlpatterns)} patterns)")
        return True
    except Exception as e:
        print(f"❌ URL error: {e}")
        return False

def verify_settings():
    """Verify settings configuration"""
    try:
        from django.conf import settings
        print(f"✅ Settings loaded: {settings.DJANGO_ENVIRONMENT}")
        print(f"   Installed apps: {len(settings.INSTALLED_APPS)}")
        print(f"   Middleware: {len(settings.MIDDLEWARE)}")
        return True
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Farmetrics Backend Verification")
    print("=" * 60)
    print()
    
    results = [
        verify_imports(),
        verify_urls(),
        verify_settings(),
    ]
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ Backend verification successful!")
    else:
        print("❌ Some verifications failed")
    print("=" * 60)

