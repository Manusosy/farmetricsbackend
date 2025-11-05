#!/usr/bin/env python
"""
Post-deployment script for Render.
Run this after the first deployment to set up the database.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmetrics.settings.production')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()

def main():
    print("🚀 Running post-deployment setup...")
    
    # Run migrations
    print("\n📦 Running migrations...")
    call_command('migrate', verbosity=2, interactive=False)
    
    # Create default roles
    print("\n👥 Creating default roles...")
    try:
        call_command('create_default_roles', verbosity=2)
        print("✅ Default roles created successfully")
    except Exception as e:
        print(f"⚠️  Error creating default roles: {e}")
        print("   (This is okay if roles already exist)")
    
    # Check if superuser exists
    print("\n👤 Checking for superuser...")
    if not User.objects.filter(is_superuser=True).exists():
        print("⚠️  No superuser found!")
        print("   Please create one using:")
        print("   python manage.py createsuperuser")
    else:
        print("✅ Superuser exists")
    
    print("\n✅ Post-deployment setup complete!")
    print("\n📝 Next steps:")
    print("   1. Create superuser: python manage.py createsuperuser")
    print("   2. Enable PostGIS extension in database if not already enabled")
    print("   3. Verify API docs at: /api/docs/")

if __name__ == '__main__':
    main()

