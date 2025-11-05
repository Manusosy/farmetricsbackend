"""
Serializers for farms app.
"""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Farm, FarmHistory, FarmBoundaryPoint


class FarmSerializer(GeoFeatureModelSerializer):
    """Serializer for Farm model with GeoJSON support."""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    owner_farmer_id = serializers.CharField(source='owner.farmer_id', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    age_years = serializers.FloatField(read_only=True)
    visit_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Farm
        geo_field = 'polygon'
        fields = [
            'id', 'organization', 'farm_code', 'name', 'description',
            'owner', 'owner_name', 'owner_farmer_id', 'region', 'region_name',
            'primary_location', 'polygon', 'area_m2', 'area_acres',
            'soil_type', 'crop_type', 'other_crops', 'planting_date',
            'tree_count_estimate', 'tree_density', 'status', 'status_display',
            'verified_at', 'verified_by', 'management_notes', 'metadata',
            'created_by', 'created_by_name', 'last_updated_by',
            'age_years', 'visit_count', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'farm_code', 'area_m2', 'area_acres', 'tree_density',
            'age_years', 'visit_count', 'is_deleted', 'created_at', 'updated_at'
        ]


class FarmListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for farm lists (without geometry)."""
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Farm
        fields = [
            'id', 'farm_code', 'name', 'owner', 'owner_name',
            'region_name', 'area_m2', 'area_acres', 'crop_type',
            'status', 'status_display', 'tree_count_estimate',
            'created_at'
        ]


class FarmCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating farms."""
    
    class Meta:
        model = Farm
        fields = [
            'organization', 'name', 'description', 'owner', 'region',
            'primary_location', 'polygon', 'soil_type', 'crop_type',
            'other_crops', 'planting_date', 'tree_count_estimate',
            'management_notes', 'metadata'
        ]


class FarmHistorySerializer(GeoFeatureModelSerializer):
    """Serializer for FarmHistory model."""
    
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    farm_code = serializers.CharField(source='farm.farm_code', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    
    class Meta:
        model = FarmHistory
        geo_field = 'polygon_snapshot'
        fields = [
            'id', 'farm', 'farm_name', 'farm_code', 'change_type',
            'change_type_display', 'polygon_snapshot', 'area_m2_snapshot',
            'owner_snapshot', 'status_snapshot', 'changed_by', 'changed_by_name',
            'change_reason', 'data_snapshot', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FarmBoundaryPointSerializer(serializers.ModelSerializer):
    """Serializer for FarmBoundaryPoint model."""
    
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    collected_by_name = serializers.CharField(source='collected_by.get_full_name', read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = FarmBoundaryPoint
        fields = [
            'id', 'farm', 'farm_name', 'point', 'latitude', 'longitude',
            'sequence', 'accuracy', 'altitude', 'collected_by',
            'collected_by_name', 'collected_at', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'collected_at', 'created_at']
    
    def get_latitude(self, obj):
        return obj.point.y if obj.point else None
    
    def get_longitude(self, obj):
        return obj.point.x if obj.point else None


class FarmNearbySerializer(serializers.Serializer):
    """Serializer for nearby farm query."""
    
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    radius_km = serializers.FloatField(required=False, default=5.0)
    
    def validate_radius_km(self, value):
        if value <= 0 or value > 100:
            raise serializers.ValidationError("Radius must be between 0 and 100 km")
        return value

