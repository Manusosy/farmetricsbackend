"""
Management command to create default system roles for all organizations.
"""

from django.core.management.base import BaseCommand
from apps.organizations.models import Organization
from apps.accounts.models import Role


class Command(BaseCommand):
    help = 'Create default system roles for organizations'
    
    DEFAULT_ROLES = {
        'super_admin': {
            'name': 'Super Admin',
            'description': 'Platform owner - manages all countries, billing, system configuration',
            'permissions': ['*']  # All permissions
        },
        'country_admin': {
            'name': 'Country Admin',
            'description': 'Manages entire country: approve accounts, assign supervisors, approve transfers, country-level analytics',
            'permissions': [
                'farmer.*', 'farm.*', 'visit.view', 'visit.approve', 'media.view',
                'user.view', 'user.approve', 'user.assign', 'user.deactivate',
                'supervisor.view', 'supervisor.approve', 'supervisor.assign',
                'request.*',  # All request permissions (approve transfers, etc.)
                'role.view', 'role.assign',
                'region.view', 'region.assign',
                'analytics.view', 'analytics.export',
                'report.view', 'report.create', 'report.export',
            ]
        },
        'supervisor': {
            'name': 'Regional Supervisor',
            'description': 'Manages regional field officers, tracks activity, approves requests, views regional analytics',
            'permissions': [
                'farmer.view', 'farm.view', 
                'visit.view', 'visit.approve', 'visit.reject',
                'media.view',
                'field_officer.view', 'field_officer.manage',
                'request.view', 'request.create', 'request.approve_fo', 'request.reject_fo',
                'transfer.request',  # Can request own transfer
                'analytics.view', 'report.view',
            ]
        },
        'field_officer': {
            'name': 'Field Officer',
            'description': 'Mobile app only - creates visits, uploads media, manages assigned farms/farmers',
            'permissions': [
                'farmer.view', 'farmer.edit_assigned',
                'farm.view', 'farm.edit_assigned',
                'visit.create', 'visit.submit',
                'media.upload',
                'request.create',
                'transfer.request',
            ]
        },
        'analyst': {
            'name': 'Analyst',
            'description': 'Read-only access to analytics, dashboards, and data exports',
            'permissions': [
                'farmer.view', 'farm.view', 'visit.view', 'media.view',
                'analytics.view', 'analytics.export', 
                'report.view', 'report.create', 'report.export',
            ]
        },
        'auditor': {
            'name': 'Auditor',
            'description': 'Access to audit logs and complete activity trail (read-only)',
            'permissions': [
                'audit.view', 'audit.export',
                'farmer.view', 'farm.view', 'visit.view', 'media.view',
                'user.view', 'request.view',
            ]
        },
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--organization',
            type=str,
            help='Organization slug to create roles for (if not provided, creates for all)',
        )
    
    def handle(self, *args, **options):
        org_slug = options.get('organization')
        
        if org_slug:
            try:
                organizations = [Organization.objects.get(slug=org_slug)]
            except Organization.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Organization with slug "{org_slug}" not found'))
                return
        else:
            organizations = Organization.objects.filter(is_active=True)
        
        for organization in organizations:
            self.stdout.write(f'Creating roles for organization: {organization.name}')
            
            for slug, role_data in self.DEFAULT_ROLES.items():
                role, created = Role.objects.get_or_create(
                    organization=organization,
                    slug=slug,
                    defaults={
                        'name': role_data['name'],
                        'description': role_data['description'],
                        'permissions': role_data['permissions'],
                        'is_system_role': True,
                        'is_active': True,
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created role: {role.name}'))
                else:
                    # Update permissions for existing system roles
                    role.permissions = role_data['permissions']
                    role.description = role_data['description']
                    role.save()
                    self.stdout.write(self.style.WARNING(f'  ≈ Updated role: {role.name}'))
        
        self.stdout.write(self.style.SUCCESS('\\nDefault roles created/updated successfully!'))

