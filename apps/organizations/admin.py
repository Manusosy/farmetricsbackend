"""
Admin configuration for Organizations app.
"""

from django.contrib import admin
from .models import Organization, OrganizationMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for Organization model."""
    
    list_display = ['name', 'slug', 'subscription_tier', 'is_active', 'member_count', 'created_at']
    list_filter = ['subscription_tier', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'logo')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'address')
        }),
        ('Subscription', {
            'fields': ('subscription_tier',)
        }),
        ('Settings', {
            'fields': ('settings', 'is_active'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    """Admin interface for OrganizationMembership model."""
    
    list_display = ['user', 'organization', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'organization__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['user', 'organization', 'invited_by']
    
    fieldsets = (
        ('Membership Details', {
            'fields': ('organization', 'user', 'role', 'is_active')
        }),
        ('Invitation Info', {
            'fields': ('invited_by',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

