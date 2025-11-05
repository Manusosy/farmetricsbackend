"""
Admin configuration for Farms app.
"""

from django.contrib.gis import admin
from django.utils.html import format_html
from .models import Farm, FarmHistory, FarmBoundaryPoint


@admin.register(Farm)
class FarmAdmin(admin.GISModelAdmin):
    """Admin interface for Farm model with GIS support."""
    
    list_display = [
        'farm_code', 'name', 'owner', 'region', 'status',
        'area_display', 'tree_count_estimate', 'created_at'
    ]
    list_filter = [
        'organization', 'status', 'crop_type', 'soil_type',
        'region', 'created_at'
    ]
    search_fields = [
        'farm_code', 'name', 'owner__first_name', 'owner__last_name',
        'owner__farmer_id'
    ]
    readonly_fields = [
        'id', 'farm_code', 'area_m2', 'area_acres', 'tree_density',
        'age_years', 'visit_count', 'created_at', 'updated_at', 'deleted_at'
    ]
    autocomplete_fields = [
        'organization', 'owner', 'region', 'created_by',
        'last_updated_by', 'verified_by'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'farm_code', 'name', 'description', 'owner')
        }),
        ('Location', {
            'fields': ('region', 'primary_location')
        }),
        ('Geospatial Data', {
            'fields': ('polygon', 'area_m2', 'area_acres'),
            'description': 'Area is auto-calculated from polygon'
        }),
        ('Farm Characteristics', {
            'fields': (
                'soil_type', 'crop_type', 'other_crops',
                'planting_date', 'age_years'
            )
        }),
        ('Trees', {
            'fields': ('tree_count_estimate', 'tree_density')
        }),
        ('Status', {
            'fields': ('status', 'verified_at', 'verified_by')
        }),
        ('Management', {
            'fields': ('management_notes', 'metadata', 'visit_count')
        }),
        ('Data Management', {
            'fields': ('created_by', 'last_updated_by'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    # GIS map settings
    default_zoom = 14
    default_lat = 7.9465
    default_lon = -1.0232
    map_width = 800
    map_height = 600
    
    actions = ['verify_farms', 'flag_farms']
    
    def verify_farms(self, request, queryset):
        """Bulk verify farms."""
        from django.utils import timezone
        count = queryset.update(
            status='verified',
            verified_at=timezone.now(),
            verified_by=request.user
        )
        self.message_user(request, f'{count} farm(s) verified successfully.')
    verify_farms.short_description = "Verify selected farms"
    
    def flag_farms(self, request, queryset):
        """Bulk flag farms for review."""
        count = queryset.update(status='flagged')
        self.message_user(request, f'{count} farm(s) flagged for review.')
    flag_farms.short_description = "Flag selected farms for review"
    
    def area_display(self, obj):
        """Display area in both sq meters and acres."""
        if obj.area_m2:
            return format_html(
                '{:.2f} m² ({:.2f} acres)',
                obj.area_m2,
                obj.area_acres or 0
            )
        return '-'
    area_display.short_description = 'Area'


@admin.register(FarmHistory)
class FarmHistoryAdmin(admin.GISModelAdmin):
    """Admin interface for FarmHistory model."""
    
    list_display = [
        'farm', 'change_type', 'changed_by', 'created_at'
    ]
    list_filter = ['change_type', 'created_at']
    search_fields = ['farm__farm_code', 'farm__name', 'change_reason']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'polygon_snapshot',
        'area_m2_snapshot', 'owner_snapshot', 'status_snapshot'
    ]
    autocomplete_fields = ['farm', 'changed_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Change Information', {
            'fields': ('farm', 'change_type', 'change_reason', 'changed_by')
        }),
        ('Snapshot Data', {
            'fields': (
                'polygon_snapshot', 'area_m2_snapshot',
                'owner_snapshot', 'status_snapshot', 'data_snapshot'
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Farm history is auto-created, not manually added
        return False


@admin.register(FarmBoundaryPoint)
class FarmBoundaryPointAdmin(admin.GISModelAdmin):
    """Admin interface for FarmBoundaryPoint model."""
    
    list_display = [
        'farm', 'sequence', 'accuracy', 'collected_by', 'collected_at'
    ]
    list_filter = ['collected_at']
    search_fields = ['farm__farm_code', 'farm__name']
    readonly_fields = ['id', 'collected_at', 'created_at', 'updated_at']
    autocomplete_fields = ['farm', 'collected_by']
    date_hierarchy = 'collected_at'
    
    fieldsets = (
        ('Point Information', {
            'fields': ('farm', 'point', 'sequence')
        }),
        ('GPS Data', {
            'fields': ('accuracy', 'altitude')
        }),
        ('Collection Info', {
            'fields': ('collected_by', 'collected_at', 'notes')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # GIS map settings
    default_zoom = 16
    map_width = 800
    map_height = 600

