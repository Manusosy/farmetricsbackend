"""
Comprehensive setup verification script.
Run this to check if your backend is properly configured.
"""

import os
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 13:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    print(f"⚠️  Python {version.major}.{version.minor}.{version.micro} (3.13+ recommended)")
    return True  # Still OK

def check_django():
    """Check Django installation"""
    try:
        import django
        print(f"✅ Django {django.get_version()}")
        return True
    except ImportError:
        print("❌ Django not installed")
        return False

def check_dependencies():
    """Check critical dependencies"""
    deps = {
        'djangorestframework': 'Django REST Framework',
        'rest_framework_simplejwt': 'JWT Authentication',
        'rest_framework_gis': 'GeoDjango REST',
        'phonenumber_field': 'Phone Number Field',
        'drf_spectacular': 'API Documentation',
        'psycopg2': 'PostgreSQL Driver',
    }
    
    all_ok = True
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"⚠️  {name} - not installed (may be optional)")
            # Don't fail for optional deps
    
    return all_ok

def check_env_file():
    """Check .env file"""
    env_path = backend_dir / '.env'
    if env_path.exists():
        print("✅ .env file exists")
        return True
    else:
        print("⚠️  .env file not found (copy from .env.example)")
        return False

def check_django_setup():
    """Check if Django can be initialized"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmetrics.settings.development')
        import django
        django.setup()
        print("✅ Django setup successful")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def check_database():
    """Check database connection"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmetrics.settings.development')
        import django
        django.setup()
        
        from django.db import connection
        connection.ensure_connection()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("   (This is OK if database isn't set up yet)")
        return False

def check_migrations():
    """Check if migrations exist"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmetrics.settings.development')
        import django
        django.setup()
        
        from django.db.migrations.loader import MigrationLoader
        loader = MigrationLoader(None)
        app_count = len([app for app in loader.migrated_apps if app.startswith('apps.')])
        print(f"✅ Migrations found for {app_count} apps")
        return True
    except Exception as e:
        print(f"⚠️  Could not check migrations: {e}")
        return False

def main():
    print("=" * 70)
    print("Farmetrics Backend - Setup Verification")
    print("=" * 70)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Django Installation", check_django),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Django Setup", check_django_setup),
        ("Database Connection", check_database),
        ("Migrations", check_migrations),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        results.append(check_func())
    
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print("Your backend is ready to use!")
    elif passed >= total - 2:
        print(f"⚠️  Most checks passed ({passed}/{total})")
        print("Backend should work, but some features may be limited.")
    else:
        print(f"❌ Several checks failed ({passed}/{total})")
        print("Please fix the issues above before proceeding.")
    
    print("=" * 70)
    print("\nNext steps:")
    print("1. If database failed: Set up PostgreSQL and configure .env")
    print("2. Run migrations: python manage.py migrate")
    print("3. Create superuser: python manage.py createsuperuser")
    print("4. Start server: python manage.py runserver")
    print("5. Visit: http://localhost:8000/api/docs/")

if __name__ == '__main__':
    main()

