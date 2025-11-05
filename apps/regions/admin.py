"""
Admin configuration for Regions app.
"""

from django.contrib.gis import admin
from .models import Region, RegionSupervisor


@admin.register(Region)
class RegionAdmin(admin.GISModelAdmin):
    """Admin interface for Region model with GIS support."""
    
    list_display = ['name', 'code', 'organization', 'level', 'parent_region', 'children_count', 'is_active', 'created_at']
    list_filter = ['organization', 'level', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['id', 'area_sqkm', 'center_point', 'created_at', 'updated_at', 'full_path']
    autocomplete_fields = ['organization', 'parent_region']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'code', 'description', 'level')
        }),
        ('Hierarchy', {
            'fields': ('parent_region', 'full_path')
        }),
        ('Geospatial Data', {
            'fields': ('polygon', 'center_point', 'area_sqkm'),
            'description': 'Area and center point are auto-calculated from polygon'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # GIS map settings
    default_zoom = 6
    default_lat = 7.9465  # Ghana latitude
    default_lon = -1.0232  # Ghana longitude
    map_width = 800
    map_height = 600


@admin.register(RegionSupervisor)
class RegionSupervisorAdmin(admin.ModelAdmin):
    """Admin interface for RegionSupervisor model."""
    
    list_display = ['region', 'supervisor', 'assigned_by', 'is_active', 'assigned_at', 'expires_at']
    list_filter = ['is_active', 'assigned_at']
    search_fields = ['region__name', 'supervisor__email', 'supervisor__first_name', 'supervisor__last_name']
    readonly_fields = ['id', 'assigned_at', 'created_at', 'updated_at']
    autocomplete_fields = ['region', 'supervisor', 'assigned_by']
    date_hierarchy = 'assigned_at'
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('region', 'supervisor', 'is_active')
        }),
        ('Assignment Info', {
            'fields': ('assigned_by', 'assigned_at', 'expires_at')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

