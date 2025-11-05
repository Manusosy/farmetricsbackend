"""
Views for requests app.
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import Request, RequestComment
from .serializers import (
    RequestSerializer,
    RequestCreateSerializer,
    RequestListSerializer,
    RequestCommentSerializer,
    RequestApproveSerializer,
    TransferRequestCreateSerializer,
)


class RequestListView(generics.ListCreateAPIView):
    """
    List all requests or create a new request.
    """
    queryset = Request.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'request_type', 'priority', 'requested_by', 'assigned_to', 'organization']
    search_fields = ['request_code', 'title', 'description']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RequestCreateSerializer
        return RequestListSerializer
    
    @extend_schema(
        summary="List requests",
        description="Get list of all requests with filtering",
        tags=["Requests"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create request",
        description="Create a new request",
        tags=["Requests"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        # Filter by user's requests or assigned requests
        user_filter = self.request.query_params.get('user_filter')
        if user_filter == 'my_requests':
            queryset = queryset.filter(requested_by=self.request.user)
        elif user_filter == 'assigned_to_me':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        return queryset.select_related('requested_by', 'assigned_to', 'approved_by', 'rejected_by')
    
    def perform_create(self, serializer):
        # Set organization and requested_by
        if hasattr(self.request, 'organization') and self.request.organization:
            serializer.save(
                organization=self.request.organization,
                requested_by=self.request.user
            )
        else:
            serializer.save(requested_by=self.request.user)


class RequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or cancel a request.
    """
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get request detail",
        description="Get detailed information about a specific request",
        tags=["Requests"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update request",
        description="Update request (only if pending)",
        tags=["Requests"]
    )
    def put(self, request, *args, **kwargs):
        req = self.get_object()
        
        # Only allow updates for pending requests
        if req.status != 'pending':
            return Response(
                {"error": "Cannot update request that is not pending"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Cancel request",
        description="Cancel a pending request",
        tags=["Requests"]
    )
    def delete(self, request, *args, **kwargs):
        req = self.get_object()
        
        if req.status != 'pending':
            return Response(
                {"error": "Can only cancel pending requests"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        req.status = 'cancelled'
        req.save()
        
        return Response(
            {"message": "Request cancelled successfully"},
            status=status.HTTP_200_OK
        )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        return queryset.select_related('requested_by', 'assigned_to', 'approved_by', 'rejected_by')


class RequestApproveView(APIView):
    """
    Approve, reject, or cancel a request.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Approve/reject request",
        description="Approve, reject, or cancel a request",
        tags=["Requests"],
        request=RequestApproveSerializer
    )
    def post(self, request, pk):
        serializer = RequestApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            req = Request.objects.get(pk=pk)
            
            if req.status != 'pending':
                return Response(
                    {"error": "Request must be in pending status"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            action = serializer.validated_data['action']
            reason = serializer.validated_data.get('reason', '')
            
            if action == 'approve':
                req.status = 'approved'
                req.approved_by = request.user
                req.approved_at = timezone.now()
            elif action == 'reject':
                req.status = 'rejected'
                req.rejected_by = request.user
                req.rejected_at = timezone.now()
                req.rejection_reason = reason
            elif action == 'cancel':
                req.status = 'cancelled'
            
            req.save()
            
            # TODO: Send notification to requester
            
            return Response(
                RequestSerializer(req).data,
                status=status.HTTP_200_OK
            )
        except Request.DoesNotExist:
            return Response(
                {"error": "Request not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class RequestCommentListView(generics.ListCreateAPIView):
    """
    List or create comments on a request.
    """
    queryset = RequestComment.objects.all()
    serializer_class = RequestCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List request comments",
        description="Get comments on a request",
        tags=["Requests"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Add comment",
        description="Add a comment to a request",
        tags=["Requests"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        request_id = self.kwargs.get('request_id')
        return RequestComment.objects.filter(request_id=request_id).select_related('user')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransferRequestCreateView(APIView):
    """
    Create a transfer request.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Create transfer request",
        description="Create a transfer request for moving between regions",
        tags=["Requests"],
        request=TransferRequestCreateSerializer
    )
    def post(self, request):
        serializer = TransferRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Build request_data
        request_data = {
            'current_region_id': str(serializer.validated_data['current_region_id']),
            'target_region_id': str(serializer.validated_data['target_region_id']),
            'reason': serializer.validated_data['reason'],
            'effective_date': serializer.validated_data.get('effective_date'),
        }
        
        # Create request
        req = Request.objects.create(
            organization=request.organization if hasattr(request, 'organization') else None,
            request_type='transfer',
            title=f"Transfer Request - {request.user.get_full_name()}",
            description=serializer.validated_data['reason'],
            requested_by=request.user,
            assigned_to_id=serializer.validated_data.get('assigned_to_id'),
            request_data=request_data,
            priority='normal'
        )
        
        return Response(
            RequestSerializer(req).data,
            status=status.HTTP_201_CREATED
        )

