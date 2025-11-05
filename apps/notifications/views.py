"""
Views for notifications app.
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationPreferenceSerializer,
)


class NotificationListView(generics.ListAPIView):
    """
    List user's notifications.
    """
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List notifications",
        description="Get list of notifications for authenticated user",
        tags=["Notifications"]
    )
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Filter by type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset.order_by('-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a notification and mark as read.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get notification",
        description="Get notification detail and mark as read",
        tags=["Notifications"]
    )
    def get(self, request, *args, **kwargs):
        notification = self.get_object()
        
        # Verify ownership
        if notification.user != request.user:
            return Response(
                {"error": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mark as read
        notification.mark_as_read()
        
        return Response(NotificationSerializer(notification).data)
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkReadView(APIView):
    """
    Mark notifications as read.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Mark notifications as read",
        description="Mark one or more notifications as read",
        tags=["Notifications"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'notification_ids': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'List of notification IDs to mark as read'
                    },
                    'mark_all': {
                        'type': 'boolean',
                        'description': 'Mark all notifications as read'
                    }
                }
            }
        }
    )
    def post(self, request):
        notification_ids = request.data.get('notification_ids', [])
        mark_all = request.data.get('mark_all', False)
        
        queryset = Notification.objects.filter(user=request.user, is_read=False)
        
        if mark_all:
            count = queryset.update(is_read=True, read_at=timezone.now())
        elif notification_ids:
            count = queryset.filter(id__in=notification_ids).update(
                is_read=True,
                read_at=timezone.now()
            )
        else:
            return Response(
                {"error": "Either notification_ids or mark_all must be provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "message": f"{count} notification(s) marked as read",
            "count": count
        })


class NotificationUnreadCountView(APIView):
    """
    Get count of unread notifications.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get unread count",
        description="Get count of unread notifications for authenticated user",
        tags=["Notifications"]
    )
    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({"unread_count": count})


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """
    Get or update notification preferences.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get notification preferences",
        description="Get user's notification preferences",
        tags=["Notifications"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update notification preferences",
        description="Update user's notification preferences",
        tags=["Notifications"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference

