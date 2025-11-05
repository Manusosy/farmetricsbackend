"""
Request models for approval workflows (transfers, permissions, etc.).
"""

from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel


class Request(SoftDeleteModel):
    """
    Generic request model for various approval workflows.
    """
    
    REQUEST_TYPE_CHOICES = [
        ('transfer', 'Transfer Request'),
        ('permission', 'Permission Request'),
        ('farmer_merge', 'Farmer Merge Request'),
        ('farm_update', 'Farm Update Request'),
        ('access', 'Access Request'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='requests'
    )
    
    # Basic Information
    request_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique request identifier (auto-generated)"
    )
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPE_CHOICES,
        db_index=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Requester
    requested_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='requests_made'
    )
    
    # Status & Priority
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    
    # Approval Workflow
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests_assigned',
        help_text="User responsible for reviewing/approving this request"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests_approved',
        related_query_name='approved_request'
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests_rejected',
        related_query_name='rejected_request'
    )
    rejection_reason = models.TextField(blank=True)
    
    # Request-specific data (JSON for flexibility)
    request_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Request-specific data (e.g., transfer details, permission details)"
    )
    
    # Related objects (flexible foreign keys)
    related_farmer = models.ForeignKey(
        'farmers.Farmer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests'
    )
    related_farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests'
    )
    related_visit = models.ForeignKey(
        'visits.Visit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests'
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional request metadata"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['request_type', 'status']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.request_code} - {self.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-generate request code if not provided
        if not self.request_code:
            self.request_code = self.generate_request_code()
        
        # Set timestamps for status changes
        from django.utils import timezone
        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        elif self.status == 'rejected' and not self.rejected_at:
            self.rejected_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def generate_request_code(self):
        """Generate unique request code."""
        import random
        import string
        from django.utils import timezone
        
        # Format: REQ-YEAR-RANDOM (e.g., REQ-2025-A1B2C3)
        year = timezone.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        request_code = f"REQ-{year}-{random_part}"
        
        # Ensure uniqueness
        while Request.objects.filter(request_code=request_code).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            request_code = f"REQ-{year}-{random_part}"
        
        return request_code


class RequestComment(TimeStampedModel):
    """
    Comments on requests for collaboration and clarification.
    """
    
    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='request_comments'
    )
    comment = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal comment (not visible to requester)"
    )
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.request.request_code} by {self.user.get_full_name()}"


class TransferRequest(Request):
    """
    Transfer request for moving users between regions/assignments.
    Inherits from Request model with transfer-specific fields.
    """
    
    # Transfer-specific fields stored in request_data JSON:
    # - current_region_id
    # - target_region_id
    # - reason
    # - effective_date
    
    class Meta:
        proxy = True
        verbose_name = 'Transfer Request'
        verbose_name_plural = 'Transfer Requests'

