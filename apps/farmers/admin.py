"""
Admin configuration for Farmers app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Farmer, FarmerMergeHistory


@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    """Admin interface for Farmer model."""
    
    list_display = [
        'farmer_id', 'get_full_name', 'phone_number', 'region', 
        'verification_status', 'total_farms', 'created_at'
    ]
    list_filter = [
        'organization', 'verification_status', 'gender', 
        'region', 'created_at'
    ]
    search_fields = [
        'farmer_id', 'first_name', 'last_name', 'phone_number', 
        'national_id', 'email'
    ]
    readonly_fields = [
        'id', 'farmer_id', 'age', 'total_farms', 'total_farm_area',
        'created_at', 'updated_at', 'deleted_at'
    ]
    autocomplete_fields = ['organization', 'region', 'created_by', 'last_updated_by', 'verified_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'farmer_id', 'first_name', 'middle_name', 'last_name')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'alternate_phone', 'email')
        }),
        ('Identification', {
            'fields': ('national_id', 'national_id_type')
        }),
        ('Demographics', {
            'fields': ('date_of_birth', 'age', 'gender')
        }),
        ('Address', {
            'fields': ('address', 'region', 'community', 'gps_coordinates')
        }),
        ('Farming Information', {
            'fields': (
                'years_of_experience', 'primary_crop', 'secondary_crops',
                'total_farms', 'total_farm_area'
            )
        }),
        ('Verification', {
            'fields': (
                'verification_status', 'verified_at', 'verified_by', 
                'verification_notes'
            )
        }),
        ('Media', {
            'fields': ('profile_photo', 'documents')
        }),
        ('Data Management', {
            'fields': ('created_by', 'last_updated_by', 'notes', 'metadata'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_farmers', 'reject_farmers']
    
    def verify_farmers(self, request, queryset):
        """Bulk verify farmers."""
        from django.utils import timezone
        count = queryset.update(
            verification_status='verified',
            verified_at=timezone.now(),
            verified_by=request.user
        )
        self.message_user(request, f'{count} farmer(s) verified successfully.')
    verify_farmers.short_description = "Verify selected farmers"
    
    def reject_farmers(self, request, queryset):
        """Bulk reject farmers."""
        count = queryset.update(verification_status='rejected')
        self.message_user(request, f'{count} farmer(s) rejected.')
    reject_farmers.short_description = "Reject selected farmers"
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'


@admin.register(FarmerMergeHistory)
class FarmerMergeHistoryAdmin(admin.ModelAdmin):
    """Admin interface for FarmerMergeHistory model."""
    
    list_display = ['primary_farmer', 'merged_farmer_id', 'merged_by', 'created_at']
    list_filter = ['organization', 'created_at']
    search_fields = ['primary_farmer__farmer_id', 'merged_farmer_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['organization', 'primary_farmer', 'merged_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Merge Information', {
            'fields': ('organization', 'primary_farmer', 'merged_farmer_id')
        }),
        ('Merge Details', {
            'fields': ('merge_reason', 'merged_by', 'merged_farmer_data')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of merge records
        return False

