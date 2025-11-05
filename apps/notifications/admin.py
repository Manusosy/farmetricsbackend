"""
Admin configuration for Notifications app.
"""

from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    
    list_display = [
        'title', 'user', 'notification_type', 'priority',
        'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'read_at']
    autocomplete_fields = ['user', 'related_farmer', 'related_farm', 'related_visit', 'related_request']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Recipient', {
            'fields': ('user',)
        }),
        ('Notification Details', {
            'fields': ('notification_type', 'title', 'message', 'priority')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Action', {
            'fields': ('action_url', 'action_text')
        }),
        ('Related Objects', {
            'fields': ('related_farmer', 'related_farm', 'related_visit', 'related_request')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for NotificationPreference model."""
    
    list_display = ['user', 'email_enabled', 'push_enabled', 'sms_enabled']
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['user']

