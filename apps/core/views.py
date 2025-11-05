"""
Views for core app (audit logs, search, analytics).
"""

from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema

from .audit import AuditLog
from .serializers import AuditLogSerializer, AuditLogListSerializer
from .search import global_search
from .analytics import (
    get_dashboard_stats,
    get_visit_analytics,
    get_farmer_analytics,
    get_farm_analytics
)


class AuditLogListView(generics.ListAPIView):
    """
    List audit log entries.
    Only accessible to admins and auditors.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'user', 'model_name', 'organization']
    search_fields = ['object_repr', 'description', 'user__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @extend_schema(
        summary="List audit logs",
        description="Get audit log entries (admin/auditor only)",
        tags=["Audit"]
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Filter by model
        model_name = self.request.query_params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name__icontains=model_name)
        
        return queryset.select_related('user', 'organization', 'content_type')


class AuditLogDetailView(generics.RetrieveAPIView):
    """
    Retrieve detailed audit log entry.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get audit log detail",
        description="Get detailed audit log entry",
        tags=["Audit"]
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        return queryset.select_related('user', 'organization', 'content_type')


class GlobalSearchView(APIView):
    """
    Global search across all models.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Global search",
        description="Search across farmers, farms, visits, regions, users, and requests",
        tags=["Search"],
        parameters=[
            {
                'name': 'q',
                'in': 'query',
                'description': 'Search query',
                'required': True,
                'schema': {'type': 'string'}
            },
            {
                'name': 'types',
                'in': 'query',
                'description': 'Comma-separated model types to search (farmer, farm, visit, region, user, request)',
                'required': False,
                'schema': {'type': 'string'}
            },
            {
                'name': 'limit',
                'in': 'query',
                'description': 'Maximum results per type',
                'required': False,
                'schema': {'type': 'integer', 'default': 50}
            }
        ]
    )
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query or len(query) < 2:
            return Response({
                'query': query,
                'total_count': 0,
                'results': {}
            })
        
        model_types = None
        types_param = request.query_params.get('types')
        if types_param:
            model_types = [t.strip() for t in types_param.split(',')]
        
        limit = int(request.query_params.get('limit', 50))
        
        organization = None
        if hasattr(request, 'organization') and request.organization:
            organization = request.organization
        
        results = global_search(
            query=query,
            organization=organization,
            model_types=model_types,
            limit=limit
        )
        
        return Response(results)


class DashboardStatsView(APIView):
    """
    Get dashboard statistics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get dashboard stats",
        description="Get dashboard statistics for organization",
        tags=["Analytics"],
        parameters=[
            {
                'name': 'date_from',
                'in': 'query',
                'description': 'Start date (ISO format)',
                'required': False,
                'schema': {'type': 'string', 'format': 'date-time'}
            },
            {
                'name': 'date_to',
                'in': 'query',
                'description': 'End date (ISO format)',
                'required': False,
                'schema': {'type': 'string', 'format': 'date-time'}
            }
        ]
    )
    def get(self, request):
        if not hasattr(request, 'organization') or not request.organization:
            return Response(
                {"error": "Organization context required"},
                status=400
            )
        
        date_from = None
        date_to = None
        
        date_from_str = request.query_params.get('date_from')
        date_to_str = request.query_params.get('date_to')
        
        if date_from_str:
            try:
                date_from = timezone.datetime.fromisoformat(date_from_str.replace('Z', '+00:00'))
            except:
                pass
        
        if date_to_str:
            try:
                date_to = timezone.datetime.fromisoformat(date_to_str.replace('Z', '+00:00'))
            except:
                pass
        
        stats = get_dashboard_stats(
            organization=request.organization,
            date_from=date_from,
            date_to=date_to
        )
        
        return Response(stats)


class VisitAnalyticsView(APIView):
    """
    Get visit analytics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get visit analytics",
        description="Get visit analytics and statistics",
        tags=["Analytics"]
    )
    def get(self, request):
        if not hasattr(request, 'organization') or not request.organization:
            return Response(
                {"error": "Organization context required"},
                status=400
            )
        
        analytics = get_visit_analytics(organization=request.organization)
        return Response(analytics)


class FarmerAnalyticsView(APIView):
    """
    Get farmer analytics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get farmer analytics",
        description="Get farmer analytics and statistics",
        tags=["Analytics"]
    )
    def get(self, request):
        if not hasattr(request, 'organization') or not request.organization:
            return Response(
                {"error": "Organization context required"},
                status=400
            )
        
        analytics = get_farmer_analytics(organization=request.organization)
        return Response(analytics)


class FarmAnalyticsView(APIView):
    """
    Get farm analytics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get farm analytics",
        description="Get farm analytics and statistics",
        tags=["Analytics"]
    )
    def get(self, request):
        if not hasattr(request, 'organization') or not request.organization:
            return Response(
                {"error": "Organization context required"},
                status=400
            )
        
        analytics = get_farm_analytics(organization=request.organization)
        return Response(analytics)
