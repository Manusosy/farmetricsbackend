"""
Management script to create test data for development.
Run: python manage.py shell < scripts/create_test_data.py
Or use as Django management command
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmetrics.settings.development')
django.setup()

from apps.accounts.models import User
from apps.organizations.models import Organization, OrganizationMembership
from apps.accounts.models import Role
from apps.regions.models import Region
from apps.farmers.models import Farmer
from apps.farms.models import Farm
from django.contrib.gis.geos import Point, Polygon
from django.utils import timezone

def create_test_data():
    """Create test data for development"""
    print("Creating test data...")
    
    # Create organization
    org, created = Organization.objects.get_or_create(
        name="Test Organization",
        defaults={
            'slug': 'test-org',
            'description': 'Test organization for development',
            'subscription_tier': 'professional'
        }
    )
    print(f"{'Created' if created else 'Found'} organization: {org.name}")
    
    # Create superuser if doesn't exist
    if not User.objects.filter(email='admin@farmetrics.com').exists():
        admin = User.objects.create_superuser(
            email='admin@farmetrics.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print(f"Created superuser: {admin.email}")
    else:
        admin = User.objects.get(email='admin@farmetrics.com')
        print(f"Found superuser: {admin.email}")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email='test@farmetrics.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    if created:
        user.set_password('test123')
        user.save()
    print(f"{'Created' if created else 'Found'} test user: {user.email}")
    
    # Add users to organization
    OrganizationMembership.objects.get_or_create(
        organization=org,
        user=admin,
        defaults={'role': 'super_admin', 'is_active': True}
    )
    OrganizationMembership.objects.get_or_create(
        organization=org,
        user=user,
        defaults={'role': 'field_officer', 'is_active': True}
    )
    print("Added users to organization")
    
    # Create default roles
    from django.core.management import call_command
    call_command('create_default_roles', organization=org.slug)
    print("Created default roles")
    
    # Create test region
    region, created = Region.objects.get_or_create(
        organization=org,
        code='TEST-REGION-001',
        defaults={
            'name': 'Test Region',
            'level': 1,
            'level_type': 'Region',
            'center_point': Point(0.0, 0.0, srid=4326),
            'is_active': True
        }
    )
    print(f"{'Created' if created else 'Found'} test region: {region.name}")
    
    # Create test farmer
    farmer, created = Farmer.objects.get_or_create(
        organization=org,
        farmer_id='TEST-FARMER-001',
        defaults={
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+233241234567',
            'region': region,
            'verification_status': 'verified',
            'primary_crop': 'Cocoa'
        }
    )
    print(f"{'Created' if created else 'Found'} test farmer: {farmer.get_full_name()}")
    
    # Create test farm
    farm_point = Point(-1.0, 5.0, srid=4326)  # Ghana coordinates
    farm, created = Farm.objects.get_or_create(
        organization=org,
        farm_code='TEST-FARM-001',
        defaults={
            'name': 'Test Farm',
            'owner': farmer,
            'region': region,
            'primary_location': farm_point,
            'crop_type': 'Cocoa',
            'status': 'active',
            'area_m2': 10000  # 1 hectare
        }
    )
    print(f"{'Created' if created else 'Found'} test farm: {farm.name}")
    
    print("\n✅ Test data created successfully!")
    print(f"\nLogin credentials:")
    print(f"  Admin: admin@farmetrics.com / admin123")
    print(f"  User:  test@farmetrics.com / test123")
    print(f"\nOrganization: {org.name} (slug: {org.slug})")

if __name__ == '__main__':
    create_test_data()

