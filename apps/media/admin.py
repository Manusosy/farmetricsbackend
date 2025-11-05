"""
Admin configuration for Media app.
"""

from django.contrib import admin
from .models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    """Admin interface for Media model."""
    
    list_display = [
        'file_name', 'media_type', 'uploaded_by', 'file_size',
        'date_taken', 'is_verified', 'created_at'
    ]
    list_filter = ['media_type', 'is_verified', 'is_public', 'created_at', 'date_taken']
    search_fields = ['file_name', 'title', 'description', 'camera_make', 'camera_model']
    readonly_fields = [
        'id', 'file_name', 'file_size', 'mime_type', 'exif_data',
        'camera_make', 'camera_model', 'date_taken', 'orientation',
        'width', 'height', 'created_at', 'updated_at'
    ]
    autocomplete_fields = ['uploaded_by', 'related_farm', 'related_farmer']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('File Information', {
            'fields': ('organization', 'file', 'file_name', 'file_size', 'mime_type', 'media_type')
        }),
        ('Upload Information', {
            'fields': ('uploaded_by', 'created_at')
        }),
        ('GPS Location', {
            'fields': ('gps_location', 'gps_accuracy')
        }),
        ('EXIF Data', {
            'fields': ('exif_data', 'camera_make', 'camera_model', 'date_taken', 'orientation', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': ('title', 'description', 'tags')
        }),
        ('Relationships', {
            'fields': ('related_farm', 'related_farmer')
        }),
        ('Status', {
            'fields': ('is_public', 'is_verified')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('System Information', {
            'fields': ('id', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

