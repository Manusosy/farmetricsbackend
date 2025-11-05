"""
Admin configuration for Visits app.
"""

from django.contrib import admin
from .models import Visit, VisitComment, VisitMedia


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    """Admin interface for Visit model."""
    
    list_display = [
        'visit_code', 'farm', 'farmer', 'field_officer', 'visit_type',
        'visit_date', 'status', 'is_gps_validated', 'created_at'
    ]
    list_filter = ['status', 'visit_type', 'is_gps_validated', 'visit_date', 'created_at']
    search_fields = ['visit_code', 'farm__name', 'farmer__first_name', 'farmer__last_name']
    readonly_fields = ['id', 'visit_code', 'created_at', 'updated_at', 'submitted_at', 'approved_at']
    autocomplete_fields = ['farm', 'farmer', 'field_officer', 'approved_by']
    date_hierarchy = 'visit_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'visit_code', 'farm', 'farmer', 'visit_type', 'visit_date', 'status')
        }),
        ('Field Officer', {
            'fields': ('field_officer',)
        }),
        ('Location', {
            'fields': ('gps_location', 'gps_accuracy', 'is_gps_validated', 'validation_notes')
        }),
        ('Visit Data', {
            'fields': ('checklist_data', 'observations', 'recommendations', 'farmer_feedback', 'weather_conditions')
        }),
        ('Approval', {
            'fields': ('submitted_at', 'approved_at', 'approved_by', 'rejection_reason')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VisitComment)
class VisitCommentAdmin(admin.ModelAdmin):
    """Admin interface for VisitComment model."""
    
    list_display = ['visit', 'user', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['comment', 'visit__visit_code', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['visit', 'user']


@admin.register(VisitMedia)
class VisitMediaAdmin(admin.ModelAdmin):
    """Admin interface for VisitMedia model."""
    
    list_display = ['visit', 'media', 'created_at']
    list_filter = ['created_at']
    search_fields = ['visit__visit_code', 'media__file_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['visit', 'media']

