"""
Serializers for farmers app.
"""

from rest_framework import serializers
from .models import Farmer, FarmerMergeHistory


class FarmerSerializer(serializers.ModelSerializer):
    """Serializer for Farmer model."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    total_farms = serializers.IntegerField(read_only=True)
    total_farm_area = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    verification_status_display = serializers.CharField(
        source='get_verification_status_display', 
        read_only=True
    )
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Farmer
        fields = [
            'id', 'organization', 'farmer_id', 'first_name', 'middle_name', 
            'last_name', 'full_name', 'phone_number', 'alternate_phone', 'email',
            'national_id', 'national_id_type', 'date_of_birth', 'age', 'gender',
            'address', 'region', 'region_name', 'community', 'gps_coordinates',
            'years_of_experience', 'primary_crop', 'secondary_crops',
            'verification_status', 'verification_status_display', 'verified_at',
            'verified_by', 'verification_notes', 'profile_photo', 'documents',
            'created_by', 'created_by_name', 'last_updated_by', 'notes', 'metadata',
            'total_farms', 'total_farm_area', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'farmer_id', 'age', 'total_farms', 'total_farm_area',
            'is_deleted', 'created_at', 'updated_at'
        ]


class FarmerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating farmers."""
    
    class Meta:
        model = Farmer
        fields = [
            'organization', 'first_name', 'middle_name', 'last_name',
            'phone_number', 'alternate_phone', 'email', 'national_id',
            'national_id_type', 'date_of_birth', 'gender', 'address',
            'region', 'community', 'gps_coordinates', 'years_of_experience',
            'primary_crop', 'secondary_crops', 'profile_photo', 'notes'
        ]


class FarmerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for farmer lists."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    total_farms = serializers.IntegerField(read_only=True)
    verification_status_display = serializers.CharField(
        source='get_verification_status_display',
        read_only=True
    )
    
    class Meta:
        model = Farmer
        fields = [
            'id', 'farmer_id', 'full_name', 'phone_number', 'region_name',
            'verification_status', 'verification_status_display',
            'total_farms', 'created_at'
        ]


class FarmerMergeHistorySerializer(serializers.ModelSerializer):
    """Serializer for FarmerMergeHistory model."""
    
    primary_farmer_name = serializers.CharField(source='primary_farmer.get_full_name', read_only=True)
    merged_by_name = serializers.CharField(source='merged_by.get_full_name', read_only=True)
    
    class Meta:
        model = FarmerMergeHistory
        fields = [
            'id', 'organization', 'primary_farmer', 'primary_farmer_name',
            'merged_farmer_id', 'merged_farmer_data', 'merged_by',
            'merged_by_name', 'merge_reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FarmerDuplicateCheckSerializer(serializers.Serializer):
    """Serializer for checking farmer duplicates."""
    
    phone_number = serializers.CharField(required=False, allow_blank=True)
    national_id = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        # At least one field must be provided
        if not any([
            attrs.get('phone_number'),
            attrs.get('national_id'),
            attrs.get('first_name') and attrs.get('last_name')
        ]):
            raise serializers.ValidationError(
                "At least one search criterion must be provided"
            )
        return attrs


class FarmerMergeSerializer(serializers.Serializer):
    """Serializer for merging duplicate farmers."""
    
    primary_farmer_id = serializers.UUIDField(required=True)
    duplicate_farmer_id = serializers.UUIDField(required=True)
    merge_reason = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['primary_farmer_id'] == attrs['duplicate_farmer_id']:
            raise serializers.ValidationError(
                "Cannot merge a farmer with itself"
            )
        return attrs

