"""
Views for farmers app.
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema

from .models import Farmer, FarmerMergeHistory
from .serializers import (
    FarmerSerializer,
    FarmerCreateSerializer,
    FarmerListSerializer,
    FarmerMergeHistorySerializer,
    FarmerDuplicateCheckSerializer,
    FarmerMergeSerializer,
)


class FarmerListView(generics.ListCreateAPIView):
    """
    List all farmers or create a new farmer.
    """
    queryset = Farmer.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['verification_status', 'region', 'organization']
    search_fields = ['farmer_id', 'first_name', 'last_name', 'phone_number', 'national_id']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FarmerCreateSerializer
        return FarmerListSerializer
    
    @extend_schema(
        summary="List farmers",
        description="Get list of all farmers with filtering and search",
        tags=["Farmers"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create farmer",
        description="Create a new farmer record",
        tags=["Farmers"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization from middleware
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        # Filter by region if user has geographic scope
        # TODO: Add geographic filtering based on user's assignment
        
        return queryset.select_related('region', 'created_by', 'verified_by')
    
    def perform_create(self, serializer):
        # Set organization from middleware
        if hasattr(self.request, 'organization') and self.request.organization:
            serializer.save(
                organization=self.request.organization,
                created_by=self.request.user
            )
        else:
            serializer.save(created_by=self.request.user)


class FarmerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or soft delete a farmer.
    """
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get farmer detail",
        description="Get detailed information about a specific farmer",
        tags=["Farmers"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update farmer",
        description="Update farmer information",
        tags=["Farmers"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete farmer",
        description="Soft delete a farmer (data retained)",
        tags=["Farmers"]
    )
    def delete(self, request, *args, **kwargs):
        farmer = self.get_object()
        farmer.delete()  # Soft delete
        return Response(
            {"message": "Farmer deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        return queryset.select_related('region', 'created_by', 'verified_by', 'last_updated_by')
    
    def perform_update(self, serializer):
        serializer.save(last_updated_by=self.request.user)


class FarmerVerifyView(APIView):
    """
    Verify or reject a farmer.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Verify farmer",
        description="Verify or reject a farmer with optional notes",
        tags=["Farmers"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'enum': ['verified', 'rejected', 'flagged'],
                        'description': 'Verification status'
                    },
                    'notes': {
                        'type': 'string',
                        'description': 'Verification notes'
                    }
                }
            }
        }
    )
    def post(self, request, pk):
        try:
            farmer = Farmer.objects.get(pk=pk)
            
            # Check organization access
            if hasattr(request, 'organization') and request.organization:
                if farmer.organization != request.organization:
                    return Response(
                        {"error": "Farmer not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            status_value = request.data.get('status')
            notes = request.data.get('notes', '')
            
            if status_value not in ['verified', 'rejected', 'flagged']:
                return Response(
                    {"error": "Invalid status. Must be 'verified', 'rejected', or 'flagged'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            farmer.verification_status = status_value
            farmer.verification_notes = notes
            farmer.verified_by = request.user
            from django.utils import timezone
            farmer.verified_at = timezone.now()
            farmer.save()
            
            return Response(
                FarmerSerializer(farmer).data,
                status=status.HTTP_200_OK
            )
        except Farmer.DoesNotExist:
            return Response(
                {"error": "Farmer not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class FarmerDuplicateCheckView(APIView):
    """
    Check for duplicate farmers based on phone, national ID, or name.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Check for duplicates",
        description="Search for potential duplicate farmers",
        tags=["Farmers"],
        request=FarmerDuplicateCheckSerializer
    )
    def post(self, request):
        serializer = FarmerDuplicateCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        queryset = Farmer.objects.all()
        
        # Filter by organization
        if hasattr(request, 'organization') and request.organization:
            queryset = queryset.filter(organization=request.organization)
        
        phone_number = serializer.validated_data.get('phone_number')
        national_id = serializer.validated_data.get('national_id')
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        
        # Build query
        q = Q()
        if phone_number:
            q |= Q(phone_number=phone_number) | Q(alternate_phone=phone_number)
        if national_id:
            q |= Q(national_id=national_id)
        if first_name and last_name:
            q |= Q(first_name__iexact=first_name, last_name__iexact=last_name)
        
        duplicates = queryset.filter(q)
        
        return Response({
            'count': duplicates.count(),
            'results': FarmerListSerializer(duplicates, many=True).data
        })


class FarmerMergeView(APIView):
    """
    Merge duplicate farmers.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Merge farmers",
        description="Merge duplicate farmer records",
        tags=["Farmers"],
        request=FarmerMergeSerializer
    )
    def post(self, request):
        serializer = FarmerMergeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            primary_farmer = Farmer.objects.get(
                id=serializer.validated_data['primary_farmer_id']
            )
            duplicate_farmer = Farmer.objects.get(
                id=serializer.validated_data['duplicate_farmer_id']
            )
            
            # Check organization access
            if hasattr(request, 'organization') and request.organization:
                if (primary_farmer.organization != request.organization or 
                    duplicate_farmer.organization != request.organization):
                    return Response(
                        {"error": "Farmers must belong to the same organization"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Create snapshot of duplicate farmer data
            duplicate_data = {
                'farmer_id': duplicate_farmer.farmer_id,
                'first_name': duplicate_farmer.first_name,
                'last_name': duplicate_farmer.last_name,
                'phone_number': str(duplicate_farmer.phone_number),
                'national_id': duplicate_farmer.national_id,
            }
            
            # Transfer farms to primary farmer
            duplicate_farmer.farms.update(owner=primary_farmer)
            
            # Create merge history record
            merge_history = FarmerMergeHistory.objects.create(
                organization=primary_farmer.organization,
                primary_farmer=primary_farmer,
                merged_farmer_id=duplicate_farmer.farmer_id,
                merged_farmer_data=duplicate_data,
                merged_by=request.user,
                merge_reason=serializer.validated_data['merge_reason']
            )
            
            # Soft delete duplicate farmer
            duplicate_farmer.delete()
            
            return Response({
                'message': 'Farmers merged successfully',
                'primary_farmer': FarmerSerializer(primary_farmer).data,
                'merge_history': FarmerMergeHistorySerializer(merge_history).data
            }, status=status.HTTP_200_OK)
            
        except Farmer.DoesNotExist:
            return Response(
                {"error": "One or both farmers not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class FarmerMergeHistoryListView(generics.ListAPIView):
    """
    List farmer merge history records.
    """
    queryset = FarmerMergeHistory.objects.all()
    serializer_class = FarmerMergeHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List merge history",
        description="Get history of farmer merges",
        tags=["Farmers"]
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        # Filter by primary farmer if provided
        farmer_id = self.request.query_params.get('farmer_id')
        if farmer_id:
            queryset = queryset.filter(primary_farmer_id=farmer_id)
        
        return queryset.select_related('primary_farmer', 'merged_by', 'organization')

