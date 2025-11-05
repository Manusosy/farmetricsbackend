"""
Views for regions app.
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Region, RegionSupervisor
from .serializers import (
    RegionSerializer,
    RegionListSerializer,
    RegionHierarchySerializer,
    RegionSupervisorSerializer,
    AssignSupervisorSerializer,
)


class RegionListView(generics.ListCreateAPIView):
    """
    List all regions or create a new region.
    """
    queryset = Region.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'level_type', 'is_active', 'parent_region', 'organization']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'level', 'created_at']
    ordering = ['level', 'name']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            # Use lightweight serializer for list view
            return RegionListSerializer
        return RegionSerializer
    
    @extend_schema(
        summary="List regions",
        description="Get list of all regions with filtering",
        tags=["Regions"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create region",
        description="Create a new region with geospatial data",
        tags=["Regions"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        # Filter by parent if provided
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_region_id=parent_id)
        
        # Filter by level if provided
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        return queryset.select_related('parent_region', 'organization')
    
    def perform_create(self, serializer):
        # Set organization from middleware
        if hasattr(self.request, 'organization') and self.request.organization:
            serializer.save(organization=self.request.organization)
        else:
            serializer.save()


class RegionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a region.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get region detail",
        description="Get detailed information about a specific region with geospatial data",
        tags=["Regions"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update region",
        description="Update region information including boundaries",
        tags=["Regions"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete region",
        description="Delete a region (must have no children or farms)",
        tags=["Regions"]
    )
    def delete(self, request, *args, **kwargs):
        region = self.get_object()
        
        # Check if region has children
        if region.subregions.filter(is_active=True).exists():
            return Response(
                {"error": "Cannot delete region with active subregions"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if region has farms
        if region.farms.exists():
            return Response(
                {"error": "Cannot delete region with associated farms"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        region.delete()
        return Response(
            {"message": "Region deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        return queryset.select_related('parent_region', 'organization')


class RegionHierarchyView(APIView):
    """
    Get region hierarchy tree.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get region hierarchy",
        description="Get complete region hierarchy tree starting from root regions",
        tags=["Regions"]
    )
    def get(self, request):
        queryset = Region.objects.filter(parent_region__isnull=True, is_active=True)
        
        # Filter by organization
        if hasattr(request, 'organization') and request.organization:
            queryset = queryset.filter(organization=request.organization)
        
        serializer = RegionHierarchySerializer(queryset, many=True)
        return Response(serializer.data)


class RegionChildrenView(generics.ListAPIView):
    """
    Get direct children of a region.
    """
    serializer_class = RegionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get region children",
        description="Get direct child regions",
        tags=["Regions"]
    )
    def get_queryset(self):
        region_id = self.kwargs.get('pk')
        return Region.objects.filter(parent_region_id=region_id, is_active=True)


class RegionSupervisorListView(generics.ListCreateAPIView):
    """
    List or assign supervisors to a region.
    """
    queryset = RegionSupervisor.objects.all()
    serializer_class = RegionSupervisorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List region supervisors",
        description="Get supervisors assigned to a region",
        tags=["Regions"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Assign supervisor",
        description="Assign a supervisor to a region",
        tags=["Regions"],
        request=AssignSupervisorSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = AssignSupervisorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        region_id = self.kwargs.get('region_id')
        try:
            region = Region.objects.get(id=region_id)
        except Region.DoesNotExist:
            return Response(
                {"error": "Region not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        supervisor = serializer.validated_data['supervisor_id']
        expires_at = serializer.validated_data.get('expires_at')
        
        # Check if already assigned
        existing = RegionSupervisor.objects.filter(
            region=region,
            supervisor=supervisor,
            is_active=True
        ).first()
        
        if existing:
            return Response(
                {"error": "Supervisor already assigned to this region"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment = RegionSupervisor.objects.create(
            region=region,
            supervisor=supervisor,
            assigned_by=request.user,
            expires_at=expires_at
        )
        
        return Response(
            RegionSupervisorSerializer(assignment).data,
            status=status.HTTP_201_CREATED
        )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        region_id = self.kwargs.get('region_id')
        if region_id:
            queryset = queryset.filter(region_id=region_id, is_active=True)
        
        return queryset.select_related('region', 'supervisor', 'assigned_by')

