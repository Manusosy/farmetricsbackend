"""
Views for media app.
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Media
from .serializers import (
    MediaSerializer,
    MediaListSerializer,
    MediaUploadSerializer,
)


class MediaListView(generics.ListCreateAPIView):
    """
    List all media or upload new media.
    """
    queryset = Media.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['media_type', 'related_farm', 'related_farmer', 'organization', 'is_verified']
    search_fields = ['file_name', 'title', 'description']
    ordering_fields = ['created_at', 'date_taken', 'file_size']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MediaUploadSerializer
        return MediaListSerializer
    
    @extend_schema(
        summary="List media",
        description="Get list of all media files with filtering",
        tags=["Media"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Upload media",
        description="Upload a new media file (image, video, document)",
        tags=["Media"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        return queryset.select_related('uploaded_by', 'related_farm', 'related_farmer')
    
    def perform_create(self, serializer):
        # Set organization and uploaded_by
        if hasattr(self.request, 'organization') and self.request.organization:
            serializer.save(
                organization=self.request.organization,
                uploaded_by=self.request.user
            )
        else:
            serializer.save(uploaded_by=self.request.user)


class MediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a media file.
    """
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get media detail",
        description="Get detailed information about a media file including EXIF data",
        tags=["Media"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update media",
        description="Update media metadata (title, description, tags, etc.)",
        tags=["Media"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete media",
        description="Soft delete a media file",
        tags=["Media"]
    )
    def delete(self, request, *args, **kwargs):
        media = self.get_object()
        media.delete()  # Soft delete
        return Response(
            {"message": "Media deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        return queryset.select_related('uploaded_by', 'related_farm', 'related_farmer')


class MediaVerifyView(APIView):
    """
    Verify a media file.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Verify media",
        description="Mark a media file as verified",
        tags=["Media"]
    )
    def post(self, request, pk):
        try:
            media = Media.objects.get(pk=pk)
            
            # Check organization access
            if hasattr(request, 'organization') and request.organization:
                if media.organization != request.organization:
                    return Response(
                        {"error": "Media not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            media.is_verified = True
            media.save()
            
            return Response(
                MediaSerializer(media).data,
                status=status.HTTP_200_OK
            )
        except Media.DoesNotExist:
            return Response(
                {"error": "Media not found"},
                status=status.HTTP_404_NOT_FOUND
            )

