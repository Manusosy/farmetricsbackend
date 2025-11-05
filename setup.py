"""
Setup script for Farmetrics backend.
Run this script to verify the project setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.13+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 13):
        print("❌ Python 3.13+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'django',
        'djangorestframework',
        'djangorestframework_simplejwt',
        'rest_framework_gis',
        'phonenumber_field',
        'drf_spectacular',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    return len(missing) == 0

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        print("✅ .env file exists")
        return True
    else:
        print("⚠️  .env file not found (copy from .env.example)")
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
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Farmetrics Backend Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Database Connection", check_database),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        results.append(check_func())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed! Backend is ready.")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
    print("=" * 60)

if __name__ == '__main__':
    main()

