"""
Serializers for core app (audit logs).
"""

from rest_framework import serializers
from .audit import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    content_object_repr = serializers.CharField(source='object_repr', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'user_name', 'ip_address', 'user_agent',
            'action', 'action_display', 'content_type', 'object_id', 'content_object_repr',
            'model_name', 'changes', 'previous_values', 'new_values', 'organization',
            'request_path', 'request_method', 'description', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for audit log lists."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_email', 'action', 'action_display', 'model_name',
            'object_repr', 'organization', 'created_at'
        ]

