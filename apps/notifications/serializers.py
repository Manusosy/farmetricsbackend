"""
Serializers for notifications app.
"""

from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'notification_type_display',
            'title', 'message', 'priority', 'priority_display', 'is_read',
            'read_at', 'action_url', 'action_text', 'related_farmer',
            'related_farm', 'related_visit', 'related_request', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'read_at', 'created_at', 'updated_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification lists."""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'title', 'message', 'priority', 'is_read', 'action_url',
            'created_at'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model."""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'preferences', 'email_enabled',
            'push_enabled', 'sms_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

