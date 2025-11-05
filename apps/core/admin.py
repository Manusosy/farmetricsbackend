"""
Admin configuration for Core app.
"""

from django.contrib import admin
from .audit import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model."""
    
    list_display = [
        'id', 'user', 'action', 'model_name', 'object_repr',
        'organization', 'created_at'
    ]
    list_filter = ['action', 'model_name', 'created_at', 'organization']
    search_fields = ['object_repr', 'description', 'user__email', 'ip_address']
    readonly_fields = [
        'id', 'user', 'ip_address', 'user_agent', 'action', 'content_type',
        'object_id', 'object_repr', 'model_name', 'changes', 'previous_values',
        'new_values', 'organization', 'request_path', 'request_method',
        'description', 'metadata', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Actor', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Action', {
            'fields': ('action', 'description')
        }),
        ('Target Object', {
            'fields': ('content_type', 'object_id', 'object_repr', 'model_name')
        }),
        ('Changes', {
            'fields': ('changes', 'previous_values', 'new_values'),
            'classes': ('collapse',)
        }),
        ('Context', {
            'fields': ('organization', 'request_path', 'request_method')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent editing of audit logs
        return False

