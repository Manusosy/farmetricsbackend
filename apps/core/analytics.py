"""
Analytics and dashboard data functions.
"""

from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta


def get_dashboard_stats(organization, date_from=None, date_to=None):
    """
    Get dashboard statistics for an organization.
    
    Args:
        organization: Organization instance
        date_from: Start date (datetime)
        date_to: End date (datetime)
    
    Returns:
        Dictionary with dashboard statistics
    """
    # Import here to avoid circular imports
    from apps.farmers.models import Farmer
    from apps.farms.models import Farm
    from apps.visits.models import Visit
    from apps.media.models import Media
    from apps.requests.models import Request
    from apps.regions.models import Region
    
    # Base filters
    base_filter = Q(organization=organization)
    
    if date_from:
        base_filter &= Q(created_at__gte=date_from)
    if date_to:
        base_filter &= Q(created_at__lte=date_to)
    
    # Farmers statistics
    farmers_total = Farmer.objects.filter(organization=organization).count()
    farmers_verified = Farmer.objects.filter(
        organization=organization,
        verification_status='verified'
    ).count()
    farmers_pending = Farmer.objects.filter(
        organization=organization,
        verification_status='pending'
    ).count()
    
    # Farms statistics
    farms_total = Farm.objects.filter(organization=organization).count()
    farms_verified = Farm.objects.filter(
        organization=organization,
        status='verified'
    ).count()
    farms_active = Farm.objects.filter(
        organization=organization,
        status='active'
    ).count()
    
    # Total farm area
    total_area = Farm.objects.filter(organization=organization).aggregate(
        total=Sum('area_m2')
    )['total'] or 0
    total_area_acres = Farm.objects.filter(organization=organization).aggregate(
        total=Sum('area_acres')
    )['total'] or 0
    
    # Visits statistics
    visits_filter = base_filter & Q(organization=organization)
    if date_from:
        visits_filter &= Q(visit_date__gte=date_from)
    if date_to:
        visits_filter &= Q(visit_date__lte=date_to)
    
    visits_total = Visit.objects.filter(visits_filter).count()
    visits_approved = Visit.objects.filter(
        visits_filter,
        status='approved'
    ).count()
    visits_pending = Visit.objects.filter(
        visits_filter,
        status__in=['submitted', 'draft', 'in_progress']
    ).count()
    
    # Media statistics
    media_total = Media.objects.filter(base_filter).count()
    media_images = Media.objects.filter(
        base_filter,
        media_type='image'
    ).count()
    media_videos = Media.objects.filter(
        base_filter,
        media_type='video'
    ).count()
    
    # Requests statistics
    requests_total = Request.objects.filter(base_filter).count()
    requests_pending = Request.objects.filter(
        base_filter,
        status='pending'
    ).count()
    requests_approved = Request.objects.filter(
        base_filter,
        status='approved'
    ).count()
    
    # Regions statistics
    regions_total = Region.objects.filter(organization=organization).count()
    
    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_farmers = Farmer.objects.filter(
        organization=organization,
        created_at__gte=week_ago
    ).count()
    recent_farms = Farm.objects.filter(
        organization=organization,
        created_at__gte=week_ago
    ).count()
    recent_visits = Visit.objects.filter(
        organization=organization,
        created_at__gte=week_ago
    ).count()
    
    return {
        'organization': {
            'id': str(organization.id),
            'name': organization.name,
            'member_count': organization.member_count
        },
        'farmers': {
            'total': farmers_total,
            'verified': farmers_verified,
            'pending': farmers_pending,
            'recent': recent_farmers
        },
        'farms': {
            'total': farms_total,
            'verified': farms_verified,
            'active': farms_active,
            'total_area_m2': float(total_area),
            'total_area_acres': float(total_area_acres),
            'recent': recent_farms
        },
        'visits': {
            'total': visits_total,
            'approved': visits_approved,
            'pending': visits_pending,
            'recent': recent_visits
        },
        'media': {
            'total': media_total,
            'images': media_images,
            'videos': media_videos
        },
        'requests': {
            'total': requests_total,
            'pending': requests_pending,
            'approved': requests_approved
        },
        'regions': {
            'total': regions_total
        },
        'period': {
            'from': date_from.isoformat() if date_from else None,
            'to': date_to.isoformat() if date_to else None
        }
    }


def get_visit_analytics(organization, date_from=None, date_to=None):
    """
    Get visit analytics.
    """
    from apps.visits.models import Visit
    
    visits_filter = Q(organization=organization)
    if date_from:
        visits_filter &= Q(visit_date__gte=date_from)
    if date_to:
        visits_filter &= Q(visit_date__lte=date_to)
    
    visits = Visit.objects.filter(visits_filter)
    
    # Visits by status
    by_status = visits.values('status').annotate(count=Count('id'))
    
    # Visits by type
    by_type = visits.values('visit_type').annotate(count=Count('id'))
    
    # Visits by field officer
    by_officer = visits.values(
        'field_officer__first_name',
        'field_officer__last_name',
        'field_officer__email'
    ).annotate(count=Count('id'))[:10]
    
    # Daily visits count
    daily_visits = visits.extra(
        select={'day': "DATE(visit_date)"}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    return {
        'by_status': list(by_status),
        'by_type': list(by_type),
        'by_officer': [
            {
                'name': f"{item['field_officer__first_name']} {item['field_officer__last_name']}",
                'email': item['field_officer__email'],
                'count': item['count']
            }
            for item in by_officer
        ],
        'daily': list(daily_visits)
    }


def get_farmer_analytics(organization):
    """
    Get farmer analytics.
    """
    from apps.farmers.models import Farmer
    
    farmers = Farmer.objects.filter(organization=organization)
    
    # By verification status
    by_status = farmers.values('verification_status').annotate(count=Count('id'))
    
    # By region
    by_region = farmers.values('region__name').annotate(count=Count('id'))[:10]
    
    # By primary crop
    by_crop = farmers.values('primary_crop').annotate(count=Count('id'))[:10]
    
    return {
        'by_status': list(by_status),
        'by_region': list(by_region),
        'by_crop': list(by_crop)
    }


def get_farm_analytics(organization):
    """
    Get farm analytics.
    """
    from apps.farms.models import Farm
    
    farms = Farm.objects.filter(organization=organization)
    
    # By status
    by_status = farms.values('status').annotate(
        count=Count('id'),
        total_area=Sum('area_m2')
    )
    
    # By crop type
    by_crop = farms.values('crop_type').annotate(
        count=Count('id'),
        total_area=Sum('area_m2')
    )[:10]
    
    # By region
    by_region = farms.values('region__name').annotate(
        count=Count('id'),
        total_area=Sum('area_m2')
    )[:10]
    
    return {
        'by_status': list(by_status),
        'by_crop': list(by_crop),
        'by_region': list(by_region)
    }

