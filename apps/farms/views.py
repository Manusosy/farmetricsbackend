"""
Views for farms app.
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from drf_spectacular.utils import extend_schema

from .models import Farm, FarmHistory, FarmBoundaryPoint
from .serializers import (
    FarmSerializer,
    FarmListSerializer,
    FarmCreateSerializer,
    FarmHistorySerializer,
    FarmBoundaryPointSerializer,
    FarmNearbySerializer,
)


class FarmListView(generics.ListCreateAPIView):
    """
    List all farms or create a new farm.
    """
    queryset = Farm.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'region', 'owner', 'organization', 'crop_type', 'soil_type']
    search_fields = ['farm_code', 'name', 'owner__first_name', 'owner__last_name']
    ordering_fields = ['created_at', 'name', 'area_m2']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FarmCreateSerializer
        return FarmListSerializer
    
    @extend_schema(
        summary="List farms",
        description="Get list of all farms with filtering and search",
        tags=["Farms"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create farm",
        description="Create a new farm record with geospatial data",
        tags=["Farms"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        return queryset.select_related('owner', 'region', 'created_by', 'verified_by')
    
    def perform_create(self, serializer):
        # Set organization from middleware
        if hasattr(self.request, 'organization') and self.request.organization:
            serializer.save(
                organization=self.request.organization,
                created_by=self.request.user
            )
        else:
            serializer.save(created_by=self.request.user)


class FarmDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or soft delete a farm.
    """
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get farm detail",
        description="Get detailed information about a specific farm with geospatial data",
        tags=["Farms"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update farm",
        description="Update farm information including boundaries",
        tags=["Farms"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete farm",
        description="Soft delete a farm (data retained)",
        tags=["Farms"]
    )
    def delete(self, request, *args, **kwargs):
        farm = self.get_object()
        farm.delete()  # Soft delete
        return Response(
            {"message": "Farm deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        return queryset.select_related('owner', 'region', 'created_by', 'verified_by', 'last_updated_by')
    
    def perform_update(self, serializer):
        farm = self.get_object()
        
        # Track changes for history
        old_polygon = farm.polygon
        old_status = farm.status
        old_owner = farm.owner
        
        serializer.save(last_updated_by=self.request.user)
        
        # Create history record if key fields changed
        new_farm = serializer.instance
        change_type = None
        change_reason = "Farm updated"
        
        if old_polygon != new_farm.polygon:
            change_type = 'polygon_update'
        elif old_owner != new_farm.owner:
            change_type = 'ownership_transfer'
        elif old_status != new_farm.status:
            change_type = 'status_change'
        else:
            change_type = 'general_update'
        
        # Create history record
        FarmHistory.objects.create(
            farm=new_farm,
            change_type=change_type,
            polygon_snapshot=old_polygon,
            area_m2_snapshot=farm.area_m2,
            owner_snapshot=str(old_owner),
            status_snapshot=old_status,
            changed_by=self.request.user,
            change_reason=change_reason
        )


class FarmVerifyView(APIView):
    """
    Verify a farm.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Verify farm",
        description="Mark a farm as verified",
        tags=["Farms"]
    )
    def post(self, request, pk):
        try:
            farm = Farm.objects.get(pk=pk)
            
            # Check organization access
            if hasattr(request, 'organization') and request.organization:
                if farm.organization != request.organization:
                    return Response(
                        {"error": "Farm not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            farm.status = 'verified'
            farm.verified_by = request.user
            from django.utils import timezone
            farm.verified_at = timezone.now()
            farm.save()
            
            return Response(
                FarmSerializer(farm).data,
                status=status.HTTP_200_OK
            )
        except Farm.DoesNotExist:
            return Response(
                {"error": "Farm not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class FarmNearbyView(APIView):
    """
    Find farms near a given location.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Find nearby farms",
        description="Find farms within a radius of a given location",
        tags=["Farms"],
        request=FarmNearbySerializer
    )
    def post(self, request):
        serializer = FarmNearbySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']
        radius_km = serializer.validated_data.get('radius_km', 5.0)
        
        # Create point from coordinates
        point = Point(longitude, latitude, srid=4326)
        
        # Query farms within radius
        queryset = Farm.objects.filter(
            primary_location__distance_lte=(point, D(km=radius_km))
        ).distance(point).order_by('distance')
        
        # Filter by organization
        if hasattr(request, 'organization') and request.organization:
            queryset = queryset.filter(organization=request.organization)
        
        return Response({
            'count': queryset.count(),
            'radius_km': radius_km,
            'center': {'latitude': latitude, 'longitude': longitude},
            'results': FarmListSerializer(queryset, many=True).data
        })


class FarmHistoryListView(generics.ListAPIView):
    """
    List farm history records.
    """
    queryset = FarmHistory.objects.all()
    serializer_class = FarmHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List farm history",
        description="Get change history for a farm",
        tags=["Farms"]
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        
        farm_id = self.kwargs.get('farm_id')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        return queryset.select_related('farm', 'changed_by')


class FarmBoundaryPointListView(generics.ListCreateAPIView):
    """
    List or create farm boundary points.
    """
    queryset = FarmBoundaryPoint.objects.all()
    serializer_class = FarmBoundaryPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List boundary points",
        description="Get GPS points collected for farm boundary",
        tags=["Farms"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Add boundary point",
        description="Add a GPS point to farm boundary collection",
        tags=["Farms"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        farm_id = self.kwargs.get('farm_id')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        return queryset.select_related('farm', 'collected_by').order_by('sequence')
    
    def perform_create(self, serializer):
        serializer.save(collected_by=self.request.user)

