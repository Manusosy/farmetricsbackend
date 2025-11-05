"""
Serializers for media app.
"""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Media


class MediaSerializer(GeoFeatureModelSerializer):
    """Serializer for Media model with GeoJSON support."""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    related_farm_name = serializers.CharField(source='related_farm.name', read_only=True)
    related_farmer_name = serializers.CharField(source='related_farmer.get_full_name', read_only=True)
    file_url = serializers.CharField(read_only=True)
    thumbnail_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = Media
        geo_field = 'gps_location'
        fields = [
            'id', 'organization', 'file', 'file_name', 'file_size', 'mime_type',
            'media_type', 'uploaded_by', 'uploaded_by_name', 'gps_location',
            'gps_accuracy', 'exif_data', 'camera_make', 'camera_model',
            'date_taken', 'orientation', 'width', 'height', 'duration_seconds',
            'title', 'description', 'tags', 'related_farm', 'related_farm_name',
            'related_farmer', 'related_farmer_name', 'is_public', 'is_verified',
            'metadata', 'file_url', 'thumbnail_url', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_name', 'file_size', 'mime_type', 'exif_data',
            'camera_make', 'camera_model', 'date_taken', 'orientation',
            'width', 'height', 'file_url', 'thumbnail_url', 'created_at', 'updated_at'
        ]


class MediaListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for media lists."""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = Media
        fields = [
            'id', 'file_name', 'media_type', 'file_size', 'uploaded_by',
            'uploaded_by_name', 'date_taken', 'gps_location', 'file_url',
            'is_verified', 'created_at'
        ]


class MediaUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading media files."""
    
    class Meta:
        model = Media
        fields = [
            'organization', 'file', 'media_type', 'title', 'description',
            'tags', 'related_farm', 'related_farmer', 'gps_location',
            'gps_accuracy', 'is_public', 'metadata'
        ]
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)

