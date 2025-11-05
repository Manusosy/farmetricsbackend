"""
Global search functionality across all models.
"""

from django.db.models import Q


def global_search(query, organization=None, model_types=None, limit=50):
    """
    Perform global search across multiple models.
    
    Args:
        query: Search query string
        organization: Filter by organization
        model_types: List of model types to search (e.g., ['farmer', 'farm'])
        limit: Maximum results per model type
    
    Returns:
        Dictionary with results grouped by model type
    """
    results = {}
    
    if not query or len(query.strip()) < 2:
        return results
    
    query = query.strip()
    
    # Build base filter
    base_filter = Q()
    if organization:
        base_filter = Q(organization=organization)
    
    # Import here to avoid circular imports
    from apps.farmers.models import Farmer
    from apps.farms.models import Farm
    from apps.visits.models import Visit
    from apps.regions.models import Region
    from apps.accounts.models import User
    from apps.requests.models import Request
    
    # Search Farmers
    if not model_types or 'farmer' in model_types:
        farmer_q = Q(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(farmer_id__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(national_id__icontains=query) |
            Q(email__icontains=query)
        )
        farmers = Farmer.objects.filter(base_filter & farmer_q)[:limit]
        results['farmers'] = [
            {
                'id': str(f.id),
                'type': 'farmer',
                'title': f.get_full_name(),
                'subtitle': f.farmer_id,
                'description': f.phone_number,
                'url': f'/api/v1/farmers/{f.id}/'
            }
            for f in farmers
        ]
    
    # Search Farms
    if not model_types or 'farm' in model_types:
        farm_q = Q(
            Q(name__icontains=query) |
            Q(farm_code__icontains=query) |
            Q(description__icontains=query) |
            Q(owner__first_name__icontains=query) |
            Q(owner__last_name__icontains=query)
        )
        farms = Farm.objects.filter(base_filter & farm_q)[:limit]
        results['farms'] = [
            {
                'id': str(f.id),
                'type': 'farm',
                'title': f.name,
                'subtitle': f.farm_code,
                'description': f'Owner: {f.owner.get_full_name()}',
                'url': f'/api/v1/farms/{f.id}/'
            }
            for f in farms
        ]
    
    # Search Visits
    if not model_types or 'visit' in model_types:
        visit_q = Q(
            Q(visit_code__icontains=query) |
            Q(farm__name__icontains=query) |
            Q(farmer__first_name__icontains=query) |
            Q(farmer__last_name__icontains=query) |
            Q(observations__icontains=query)
        )
        visits = Visit.objects.filter(base_filter & visit_q)[:limit]
        results['visits'] = [
            {
                'id': str(v.id),
                'type': 'visit',
                'title': f'Visit {v.visit_code}',
                'subtitle': v.farm.name,
                'description': f'Farmer: {v.farmer.get_full_name()}',
                'url': f'/api/v1/visits/{v.id}/'
            }
            for v in visits
        ]
    
    # Search Regions
    if not model_types or 'region' in model_types:
        region_q = Q(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query)
        )
        regions = Region.objects.filter(base_filter & region_q)[:limit]
        results['regions'] = [
            {
                'id': str(r.id),
                'type': 'region',
                'title': r.name,
                'subtitle': r.code,
                'description': r.full_path,
                'url': f'/api/v1/regions/{r.id}/'
            }
            for r in regions
        ]
    
    # Search Users
    if not model_types or 'user' in model_types:
        user_q = Q(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(employee_id__icontains=query)
        )
        users = User.objects.filter(user_q)[:limit]
        results['users'] = [
            {
                'id': str(u.id),
                'type': 'user',
                'title': u.get_full_name(),
                'subtitle': u.email,
                'description': u.employee_id or '',
                'url': f'/api/v1/auth/users/{u.id}/'
            }
            for u in users
        ]
    
    # Search Requests
    if not model_types or 'request' in model_types:
        request_q = Q(
            Q(request_code__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
        requests = Request.objects.filter(base_filter & request_q)[:limit]
        results['requests'] = [
            {
                'id': str(r.id),
                'type': 'request',
                'title': r.title,
                'subtitle': r.request_code,
                'description': r.get_request_type_display(),
                'url': f'/api/v1/requests/{r.id}/'
            }
            for r in requests
        ]
    
    # Calculate total count
    total_count = sum(len(v) for v in results.values())
    
    return {
        'query': query,
        'total_count': total_count,
        'results': results
    }

