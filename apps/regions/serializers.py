"""
Serializers for regions app.
"""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Region, RegionSupervisor


class RegionSerializer(GeoFeatureModelSerializer):
    """Serializer for Region model with GeoJSON support."""
    
    parent_region_name = serializers.CharField(source='parent_region.name', read_only=True)
    full_path = serializers.CharField(read_only=True)
    children_count = serializers.IntegerField(read_only=True)
    level_type_display = serializers.CharField(source='get_level_type_display', read_only=True)
    
    class Meta:
        model = Region
        geo_field = 'polygon'
        fields = [
            'id', 'organization', 'name', 'code', 'description',
            'parent_region', 'parent_region_name', 'level', 'level_type', 
            'level_type_display', 'polygon', 'center_point', 'area_sqkm',
            'is_active', 'metadata', 'full_path', 'children_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'area_sqkm', 'center_point', 'level', 'created_at', 'updated_at']


class RegionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for region lists (without geometry)."""
    
    parent_region_name = serializers.CharField(source='parent_region.name', read_only=True)
    level_type_display = serializers.CharField(source='get_level_type_display', read_only=True)
    children_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Region
        fields = [
            'id', 'name', 'code', 'parent_region', 'parent_region_name',
            'level', 'level_type', 'level_type_display', 'area_sqkm',
            'is_active', 'children_count'
        ]


class RegionHierarchySerializer(serializers.ModelSerializer):
    """Serializer for displaying region hierarchy with nested children."""
    
    children = serializers.SerializerMethodField()
    level_type_display = serializers.CharField(source='get_level_type_display', read_only=True)
    
    class Meta:
        model = Region
        fields = [
            'id', 'name', 'code', 'level', 'level_type', 'level_type_display',
            'area_sqkm', 'is_active', 'children'
        ]
    
    def get_children(self, obj):
        """Get direct children of this region."""
        children = obj.subregions.filter(is_active=True)
        return RegionHierarchySerializer(children, many=True).data


class RegionSupervisorSerializer(serializers.ModelSerializer):
    """Serializer for RegionSupervisor model."""
    
    region_name = serializers.CharField(source='region.name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    supervisor_email = serializers.EmailField(source='supervisor.email', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    
    class Meta:
        model = RegionSupervisor
        fields = [
            'id', 'region', 'region_name', 'supervisor', 'supervisor_name',
            'supervisor_email', 'assigned_by', 'assigned_by_name',
            'assigned_at', 'is_active', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'created_at']


class AssignSupervisorSerializer(serializers.Serializer):
    """Serializer for assigning a supervisor to a region."""
    
    supervisor_id = serializers.UUIDField(required=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_supervisor_id(self, value):
        from apps.accounts.models import User
        try:
            user = User.objects.get(id=value)
            # Check if user has supervisor role
            if not user.organization_memberships.filter(
                role='supervisor', is_active=True
            ).exists():
                raise serializers.ValidationError("User must have supervisor role")
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

