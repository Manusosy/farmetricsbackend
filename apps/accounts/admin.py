"""
Admin configuration for Accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Role, UserRole, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model."""
    
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_staff', 'email_verified', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'email_verified', 'mfa_enabled', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'employee_id']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'employee_id', 'avatar')}),
        (_('Address'), {'fields': ('address', 'city', 'state', 'country')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Security'), {
            'fields': ('email_verified', 'phone_verified', 'mfa_enabled', 'last_login_ip'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
        (_('System'), {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role model."""
    
    list_display = ['name', 'organization', 'slug', 'is_system_role', 'is_active', 'created_at']
    list_filter = ['organization', 'is_system_role', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'description', 'organization__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['organization']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'slug', 'description')
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'description': 'Enter permission strings as a JSON array, e.g., ["farmer.view", "farm.edit"]'
        }),
        ('Status', {
            'fields': ('is_system_role', 'is_active')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin interface for UserRole model."""
    
    list_display = ['user', 'role', 'assigned_by', 'is_active', 'expires_at', 'assigned_at']
    list_filter = ['is_active', 'assigned_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'role__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'assigned_at']
    autocomplete_fields = ['user', 'role', 'assigned_by']
    
    fieldsets = (
        ('Role Assignment', {
            'fields': ('user', 'role', 'is_active')
        }),
        ('Assignment Info', {
            'fields': ('assigned_by', 'assigned_at', 'expires_at')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin interface for PasswordResetToken model."""
    
    list_display = ['user', 'token', 'created_at', 'expires_at', 'used', 'used_at']
    list_filter = ['used', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['id', 'token', 'created_at', 'updated_at', 'used_at']
    autocomplete_fields = ['user']
    
    def has_add_permission(self, request):
        # Prevent manual creation of reset tokens
        return False

