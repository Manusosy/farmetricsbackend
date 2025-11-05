"""
Django management command to create test data.
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.organizations.models import Organization, OrganizationMembership
from apps.regions.models import Region
from apps.farmers.models import Farmer
from apps.farms.models import Farm
from django.contrib.gis.geos import Point
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create test data for development'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--organization',
            type=str,
            help='Organization slug (will create if not exists)',
            default='test-org'
        )
    
    def handle(self, *args, **options):
        org_slug = options['organization']
        
        # Create or get organization
        org, created = Organization.objects.get_or_create(
            slug=org_slug,
            defaults={
                'name': 'Test Organization',
                'description': 'Test organization for development',
                'subscription_tier': 'professional'
            }
        )
        self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Found'} organization: {org.name}"))
        
        # Create superuser if doesn't exist
        admin_email = 'admin@farmetrics.com'
        if not User.objects.filter(email=admin_email).exists():
            admin = User.objects.create_superuser(
                email=admin_email,
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {admin.email}"))
        else:
            admin = User.objects.get(email=admin_email)
            self.stdout.write(f"Found superuser: {admin.email}")
        
        # Create test user
        test_email = 'test@farmetrics.com'
        user, created = User.objects.get_or_create(
            email=test_email,
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )
        if created:
            user.set_password('test123')
            user.save()
        self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Found'} test user: {user.email}"))
        
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
        self.stdout.write("Added users to organization")
        
        # Create default roles
        from django.core.management import call_command
        try:
            call_command('create_default_roles', organization=org.slug)
            self.stdout.write("Created default roles")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not create roles: {e}"))
        
        # Create test region
        region, created = Region.objects.get_or_create(
            organization=org,
            code='TEST-REGION-001',
            defaults={
                'name': 'Test Region',
                'level': 1,
                'level_type': 'Region',
                'center_point': Point(-1.0, 5.0, srid=4326),  # Ghana coordinates
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Found'} test region: {region.name}"))
        
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
                'primary_crop': 'Cocoa',
                'created_by': admin
            }
        )
        self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Found'} test farmer: {farmer.get_full_name()}"))
        
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
                'area_m2': 10000,  # 1 hectare
                'created_by': admin
            }
        )
        self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Found'} test farm: {farm.name}"))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Test data created successfully!'))
        self.stdout.write(f'\nLogin credentials:')
        self.stdout.write(f'  Admin: {admin_email} / admin123')
        self.stdout.write(f'  User:  {test_email} / test123')
        self.stdout.write(f'\nOrganization: {org.name} (slug: {org.slug})')

