"""
Middleware for organization context in multi-tenant setup.
"""

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import Organization


class OrganizationMiddleware(MiddlewareMixin):
    """
    Middleware to set the current organization context based on:
    1. X-Organization-Slug header (for API requests)
    2. organization_slug query parameter
    3. Subdomain (if ORGANIZATION_SUBDOMAIN_ENABLED is True)
    4. User's default organization (if authenticated)
    """
    
    def process_request(self, request):
        organization = None
        
        # Method 1: Check for organization slug in header (API requests)
        org_slug = request.META.get('HTTP_X_ORGANIZATION_SLUG')
        
        # Method 2: Check for organization slug in query parameters
        if not org_slug:
            org_slug = request.GET.get('organization_slug')
        
        # Method 3: Extract from subdomain if enabled
        if not org_slug and getattr(settings, 'ORGANIZATION_SUBDOMAIN_ENABLED', False):
            host = request.get_host().split(':')[0]  # Remove port if present
            parts = host.split('.')
            if len(parts) > 2:  # Has subdomain
                potential_slug = parts[0]
                if potential_slug not in ['www', 'api', 'admin']:
                    org_slug = potential_slug
        
        # Try to get organization by slug
        if org_slug:
            try:
                organization = Organization.objects.get(
                    slug=org_slug,
                    is_active=True
                )
            except Organization.DoesNotExist:
                pass
        
        # Method 4: Use user's default organization if authenticated
        if not organization and request.user.is_authenticated:
            # Get user's primary organization (first active membership)
            membership = request.user.organization_memberships.filter(
                is_active=True
            ).select_related('organization').first()
            
            if membership:
                organization = membership.organization
        
        # Set organization in request
        request.organization = organization
        request.org = organization  # Short alias
        
        return None
    
    def process_response(self, request, response):
        # Optionally add organization info to response headers
        if hasattr(request, 'organization') and request.organization:
            response['X-Organization-Id'] = str(request.organization.id)
            response['X-Organization-Slug'] = request.organization.slug
        
        return response

