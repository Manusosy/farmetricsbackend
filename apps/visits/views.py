"""
Views for visits app.
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import Visit, VisitComment, VisitMedia
from .serializers import (
    VisitSerializer,
    VisitCreateSerializer,
    VisitListSerializer,
    VisitCommentSerializer,
    VisitMediaSerializer,
    VisitApproveSerializer,
)


class VisitListView(generics.ListCreateAPIView):
    """
    List all visits or create a new visit.
    """
    queryset = Visit.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'visit_type', 'farm', 'farmer', 'field_officer', 'organization']
    search_fields = ['visit_code', 'farm__name', 'farmer__first_name', 'farmer__last_name']
    ordering_fields = ['visit_date', 'created_at']
    ordering = ['-visit_date']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VisitCreateSerializer
        return VisitListSerializer
    
    @extend_schema(
        summary="List visits",
        description="Get list of all visits with filtering",
        tags=["Visits"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create visit",
        description="Create a new field visit",
        tags=["Visits"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        # Filter by date range if provided
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(visit_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(visit_date__lte=date_to)
        
        return queryset.select_related('farm', 'farmer', 'field_officer', 'approved_by')
    
    def perform_create(self, serializer):
        # Set organization and field officer
        if hasattr(self.request, 'organization') and self.request.organization:
            serializer.save(
                organization=self.request.organization,
                field_officer=self.request.user
            )
        else:
            serializer.save(field_officer=self.request.user)


class VisitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a visit.
    """
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get visit detail",
        description="Get detailed information about a specific visit",
        tags=["Visits"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update visit",
        description="Update visit information (only if draft or in_progress)",
        tags=["Visits"]
    )
    def put(self, request, *args, **kwargs):
        visit = self.get_object()
        
        # Only allow updates for draft or in_progress visits
        if visit.status not in ['draft', 'in_progress']:
            return Response(
                {"error": "Cannot update visit that is already submitted"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete visit",
        description="Soft delete a visit",
        tags=["Visits"]
    )
    def delete(self, request, *args, **kwargs):
        visit = self.get_object()
        visit.delete()  # Soft delete
        return Response(
            {"message": "Visit deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        return queryset.select_related('farm', 'farmer', 'field_officer', 'approved_by')


class VisitSubmitView(APIView):
    """
    Submit a visit for approval.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Submit visit",
        description="Submit a visit for supervisor approval",
        tags=["Visits"]
    )
    def post(self, request, pk):
        try:
            visit = Visit.objects.get(pk=pk)
            
            # Check permissions
            if visit.field_officer != request.user:
                return Response(
                    {"error": "Only the field officer who created the visit can submit it"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if visit.status not in ['draft', 'in_progress']:
                return Response(
                    {"error": "Visit has already been submitted"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            visit.status = 'submitted'
            visit.submitted_at = timezone.now()
            visit.save()
            
            # TODO: Send notification to supervisor
            
            return Response(
                VisitSerializer(visit).data,
                status=status.HTTP_200_OK
            )
        except Visit.DoesNotExist:
            return Response(
                {"error": "Visit not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class VisitApproveView(APIView):
    """
    Approve, reject, or request revision for a visit.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Approve/reject visit",
        description="Approve, reject, or request revision for a submitted visit",
        tags=["Visits"],
        request=VisitApproveSerializer
    )
    def post(self, request, pk):
        serializer = VisitApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            visit = Visit.objects.get(pk=pk)
            
            if visit.status != 'submitted':
                return Response(
                    {"error": "Visit must be in submitted status"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            action = serializer.validated_data['action']
            notes = serializer.validated_data.get('notes', '')
            
            if action == 'approve':
                visit.status = 'approved'
                visit.approved_at = timezone.now()
                visit.approved_by = request.user
            elif action == 'reject':
                visit.status = 'rejected'
                visit.rejection_reason = notes
            elif action == 'needs_revision':
                visit.status = 'needs_revision'
                visit.rejection_reason = notes
            
            visit.save()
            
            # TODO: Send notification to field officer
            
            return Response(
                VisitSerializer(visit).data,
                status=status.HTTP_200_OK
            )
        except Visit.DoesNotExist:
            return Response(
                {"error": "Visit not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class VisitCommentListView(generics.ListCreateAPIView):
    """
    List or create comments on a visit.
    """
    queryset = VisitComment.objects.all()
    serializer_class = VisitCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List visit comments",
        description="Get comments on a visit",
        tags=["Visits"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Add comment",
        description="Add a comment to a visit",
        tags=["Visits"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        visit_id = self.kwargs.get('visit_id')
        return VisitComment.objects.filter(visit_id=visit_id).select_related('user')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VisitMediaListView(generics.ListCreateAPIView):
    """
    List or link media to a visit.
    """
    queryset = VisitMedia.objects.all()
    serializer_class = VisitMediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List visit media",
        description="Get media files linked to a visit",
        tags=["Visits"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Link media",
        description="Link a media file to a visit",
        tags=["Visits"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        visit_id = self.kwargs.get('visit_id')
        return VisitMedia.objects.filter(visit_id=visit_id).select_related('media', 'visit')

