"""
Notification models for user notifications and alerts.
"""

from django.db import models
from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    """
    User notification for various events.
    """
    
    NOTIFICATION_TYPE_CHOICES = [
        ('visit_submitted', 'Visit Submitted'),
        ('visit_approved', 'Visit Approved'),
        ('visit_rejected', 'Visit Rejected'),
        ('request_created', 'Request Created'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
        ('transfer_approved', 'Transfer Approved'),
        ('farmer_verified', 'Farmer Verified'),
        ('farm_verified', 'Farm Verified'),
        ('comment_added', 'Comment Added'),
        ('media_uploaded', 'Media Uploaded'),
        ('system', 'System Notification'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Recipient
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Notification Details
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES,
        db_index=True
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    
    # Status
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Action/URL
    action_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL to navigate to when notification is clicked"
    )
    action_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Text for action button"
    )
    
    # Related Objects (flexible)
    related_farmer = models.ForeignKey(
        'farmers.Farmer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_visit = models.ForeignKey(
        'visits.Visit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_request = models.ForeignKey(
        'requests.Request',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional notification metadata"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class NotificationPreference(TimeStampedModel):
    """
    User preferences for notification types.
    """
    
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Preferences stored as JSON
    # e.g., {"visit_submitted": true, "visit_approved": false, ...}
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Notification type preferences (enabled/disabled)"
    )
    
    # Delivery methods
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.email}"

