"""
Admin configuration for Requests app.
"""

from django.contrib import admin
from .models import Request, RequestComment


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    """Admin interface for Request model."""
    
    list_display = [
        'request_code', 'request_type', 'title', 'requested_by',
        'status', 'priority', 'assigned_to', 'created_at'
    ]
    list_filter = ['status', 'request_type', 'priority', 'created_at']
    search_fields = ['request_code', 'title', 'description']
    readonly_fields = ['id', 'request_code', 'created_at', 'updated_at', 'approved_at', 'rejected_at']
    autocomplete_fields = ['requested_by', 'assigned_to', 'approved_by', 'rejected_by', 'related_farmer', 'related_farm']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'request_code', 'request_type', 'title', 'description', 'priority')
        }),
        ('Requester', {
            'fields': ('requested_by',)
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_to')
        }),
        ('Approval', {
            'fields': ('approved_at', 'approved_by', 'rejected_at', 'rejected_by', 'rejection_reason')
        }),
        ('Related Objects', {
            'fields': ('related_farmer', 'related_farm', 'related_visit')
        }),
        ('Data', {
            'fields': ('request_data', 'metadata')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RequestComment)
class RequestCommentAdmin(admin.ModelAdmin):
    """Admin interface for RequestComment model."""
    
    list_display = ['request', 'user', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['comment', 'request__request_code', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['request', 'user']

