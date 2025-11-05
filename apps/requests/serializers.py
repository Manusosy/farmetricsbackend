"""
Serializers for requests app.
"""

from rest_framework import serializers
from .models import Request, RequestComment


class RequestSerializer(serializers.ModelSerializer):
    """Serializer for Request model."""
    
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    rejected_by_name = serializers.CharField(source='rejected_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Request
        fields = [
            'id', 'organization', 'request_code', 'request_type', 'request_type_display',
            'title', 'description', 'requested_by', 'requested_by_name', 'status',
            'status_display', 'priority', 'priority_display', 'assigned_to', 'assigned_to_name',
            'approved_at', 'approved_by', 'approved_by_name', 'rejected_at', 'rejected_by',
            'rejected_by_name', 'rejection_reason', 'request_data', 'related_farmer',
            'related_farm', 'related_visit', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'request_code', 'approved_at', 'rejected_at', 'created_at', 'updated_at'
        ]


class RequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating requests."""
    
    class Meta:
        model = Request
        fields = [
            'organization', 'request_type', 'title', 'description', 'priority',
            'assigned_to', 'request_data', 'related_farmer', 'related_farm', 'related_visit', 'metadata'
        ]


class RequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for request lists."""
    
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Request
        fields = [
            'id', 'request_code', 'request_type', 'title', 'status', 'status_display',
            'priority', 'requested_by', 'requested_by_name', 'assigned_to', 'assigned_to_name',
            'created_at'
        ]


class RequestCommentSerializer(serializers.ModelSerializer):
    """Serializer for RequestComment model."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = RequestComment
        fields = [
            'id', 'request', 'user', 'user_name', 'user_email',
            'comment', 'is_internal', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RequestApproveSerializer(serializers.Serializer):
    """Serializer for approving/rejecting requests."""
    
    action = serializers.ChoiceField(choices=['approve', 'reject', 'cancel'])
    reason = serializers.CharField(required=False, allow_blank=True)


class TransferRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating transfer requests."""
    
    current_region_id = serializers.UUIDField(required=True)
    target_region_id = serializers.UUIDField(required=True)
    reason = serializers.CharField(required=True)
    effective_date = serializers.DateField(required=False, allow_null=True)
    assigned_to_id = serializers.UUIDField(required=False, allow_null=True)

