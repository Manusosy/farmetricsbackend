"""
Serializers for visits app.
"""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Visit, VisitComment, VisitMedia


class VisitSerializer(GeoFeatureModelSerializer):
    """Serializer for Visit model with GeoJSON support."""
    
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    farm_code = serializers.CharField(source='farm.farm_code', read_only=True)
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    field_officer_name = serializers.CharField(source='field_officer.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    visit_type_display = serializers.CharField(source='get_visit_type_display', read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Visit
        geo_field = 'gps_location'
        fields = [
            'id', 'organization', 'visit_code', 'farm', 'farm_name', 'farm_code',
            'farmer', 'farmer_name', 'visit_type', 'visit_type_display',
            'visit_date', 'status', 'status_display', 'field_officer', 'field_officer_name',
            'gps_location', 'gps_accuracy', 'checklist_data', 'observations',
            'recommendations', 'farmer_feedback', 'submitted_at', 'approved_at',
            'approved_by', 'approved_by_name', 'rejection_reason', 'is_gps_validated',
            'validation_notes', 'weather_conditions', 'metadata', 'duration_minutes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'visit_code', 'submitted_at', 'approved_at', 'is_gps_validated',
            'created_at', 'updated_at'
        ]


class VisitCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating visits."""
    
    class Meta:
        model = Visit
        fields = [
            'organization', 'farm', 'farmer', 'visit_type', 'visit_date',
            'gps_location', 'gps_accuracy', 'checklist_data', 'observations',
            'recommendations', 'farmer_feedback', 'weather_conditions', 'metadata'
        ]


class VisitListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for visit lists."""
    
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    field_officer_name = serializers.CharField(source='field_officer.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Visit
        fields = [
            'id', 'visit_code', 'farm', 'farm_name', 'farmer', 'farmer_name',
            'visit_type', 'visit_date', 'status', 'status_display',
            'field_officer', 'field_officer_name', 'is_gps_validated',
            'submitted_at', 'approved_at', 'created_at'
        ]


class VisitCommentSerializer(serializers.ModelSerializer):
    """Serializer for VisitComment model."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = VisitComment
        fields = [
            'id', 'visit', 'user', 'user_name', 'user_email',
            'comment', 'is_internal', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VisitMediaSerializer(serializers.ModelSerializer):
    """Serializer for VisitMedia link."""
    
    media_file_name = serializers.CharField(source='media.file_name', read_only=True)
    media_url = serializers.SerializerMethodField()
    
    class Meta:
        model = VisitMedia
        fields = ['id', 'visit', 'media', 'media_file_name', 'media_url', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_media_url(self, obj):
        return obj.media.file_url if obj.media else None


class VisitApproveSerializer(serializers.Serializer):
    """Serializer for approving/rejecting visits."""
    
    action = serializers.ChoiceField(choices=['approve', 'reject', 'needs_revision'])
    notes = serializers.CharField(required=False, allow_blank=True)

