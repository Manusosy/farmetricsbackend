"""
Audit logging functionality for tracking all system changes.
"""

import json
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    """
    Audit log entry for tracking all changes in the system.
    """
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('soft_delete', 'Soft Delete'),
        ('restore', 'Restore'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('submit', 'Submit'),
        ('verify', 'Verify'),
        ('merge', 'Merge'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('permission_change', 'Permission Change'),
        ('other', 'Other'),
    ]
    
    # Actor
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Action
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    
    # Target object (Generic Foreign Key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Object details
    object_repr = models.CharField(max_length=200, blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    
    # Changes
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dictionary of field changes: {'field': {'old': value, 'new': value}}"
    )
    previous_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of object before change"
    )
    new_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of object after change"
    )
    
    # Context
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Additional info
    description = models.TextField(blank=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional audit metadata"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['model_name', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} - {self.object_repr}"


def log_audit_event(
    action,
    user=None,
    obj=None,
    changes=None,
    previous_values=None,
    new_values=None,
    organization=None,
    request=None,
    description='',
    metadata=None
):
    """
    Create an audit log entry.
    
    Args:
        action: Action type (from ACTION_CHOICES)
        user: User performing the action
        obj: Object being acted upon
        changes: Dict of field changes
        previous_values: Snapshot before change
        new_values: Snapshot after change
        organization: Organization context
        request: HTTP request object (for IP, path, etc.)
        description: Description of the action
        metadata: Additional metadata
    
    Returns:
        AuditLog instance
    """
    content_type = None
    object_id = None
    object_repr = ''
    model_name = ''
    
    if obj:
        content_type = ContentType.objects.get_for_model(obj)
        object_id = obj.pk
        object_repr = str(obj)
        model_name = f"{obj._meta.app_label}.{obj._meta.model_name}"
    
    ip_address = None
    user_agent = ''
    request_path = ''
    request_method = ''
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        request_path = request.path[:500]
        request_method = request.method
    
    if not user and request and hasattr(request, 'user'):
        user = request.user if request.user.is_authenticated else None
    
    if not organization and request and hasattr(request, 'organization'):
        organization = request.organization
    
    audit_log = AuditLog.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        action=action,
        content_type=content_type,
        object_id=object_id,
        object_repr=object_repr,
        model_name=model_name,
        changes=changes or {},
        previous_values=previous_values or {},
        new_values=new_values or {},
        organization=organization,
        request_path=request_path,
        request_method=request_method,
        description=description,
        metadata=metadata or {}
    )
    
    return audit_log


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AuditLogMixin:
    """
    Mixin to add audit logging to models.
    """
    
    def save_with_audit(self, user=None, request=None, action='update', *args, **kwargs):
        """Save model and create audit log."""
        # Get previous values if updating
        previous_values = {}
        if self.pk:
            try:
                old_obj = self.__class__.objects.get(pk=self.pk)
                previous_values = self._get_field_values(old_obj)
            except self.__class__.DoesNotExist:
                pass
        
        # Save the object
        super().save(*args, **kwargs)
        
        # Get new values
        new_values = self._get_field_values(self)
        
        # Calculate changes
        changes = {}
        for field, value in new_values.items():
            if field not in previous_values or previous_values[field] != value:
                changes[field] = {
                    'old': previous_values.get(field),
                    'new': value
                }
        
        # Determine action
        if action == 'update' and not self.pk:
            action = 'create'
        
        # Create audit log
        log_audit_event(
            action=action,
            user=user,
            obj=self,
            changes=changes,
            previous_values=previous_values,
            new_values=new_values,
            request=request
        )
    
    def _get_field_values(self, obj):
        """Get all field values from model instance."""
        values = {}
        for field in obj._meta.fields:
            if not field.primary_key and field.name != 'password':
                try:
                    value = getattr(obj, field.name)
                    # Convert to JSON-serializable format
                    if hasattr(value, 'isoformat'):
                        values[field.name] = value.isoformat()
                    elif isinstance(value, models.Model):
                        values[field.name] = str(value.pk)
                    else:
                        values[field.name] = value
                except:
                    pass
        return values

