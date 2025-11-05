"""
Visit models for tracking field visits to farms.
"""

from django.contrib.gis.db import models as gis_models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel, SoftDeleteModel


class Visit(SoftDeleteModel):
    """
    Field visit to a farm for data collection and monitoring.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('needs_revision', 'Needs Revision'),
    ]
    
    VISIT_TYPE_CHOICES = [
        ('routine', 'Routine Visit'),
        ('inspection', 'Inspection'),
        ('training', 'Training'),
        ('harvest', 'Harvest Assessment'),
        ('planting', 'Planting'),
        ('pest_control', 'Pest Control'),
        ('other', 'Other'),
    ]
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='visits'
    )
    
    # Basic Information
    visit_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique visit identifier (auto-generated)"
    )
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        related_name='visits'
    )
    farmer = models.ForeignKey(
        'farmers.Farmer',
        on_delete=models.CASCADE,
        related_name='visits'
    )
    
    # Visit Details
    visit_type = models.CharField(
        max_length=20,
        choices=VISIT_TYPE_CHOICES,
        default='routine'
    )
    visit_date = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    
    # Field Officer
    field_officer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='visits_conducted'
    )
    
    # Location
    gps_location = gis_models.PointField(
        srid=4326,
        help_text="GPS location where visit was conducted"
    )
    gps_accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="GPS accuracy in meters"
    )
    
    # Visit Data (JSON-based checklist)
    checklist_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Visit checklist responses (flexible structure)"
    )
    
    # Observations & Notes
    observations = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    farmer_feedback = models.TextField(blank=True)
    
    # Approval Workflow
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visits_approved'
    )
    rejection_reason = models.TextField(blank=True)
    
    # Verification
    is_gps_validated = models.BooleanField(
        default=False,
        help_text="Whether GPS location was validated against farm polygon"
    )
    validation_notes = models.TextField(blank=True)
    
    # Metadata
    weather_conditions = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional visit metadata"
    )
    
    class Meta:
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['farm', 'visit_date']),
            models.Index(fields=['field_officer', 'visit_date']),
            models.Index(fields=['visit_date']),
        ]
    
    def __str__(self):
        return f"Visit {self.visit_code} - {self.farm.name} ({self.visit_date.date()})"
    
    def save(self, *args, **kwargs):
        # Auto-generate visit code if not provided
        if not self.visit_code:
            self.visit_code = self.generate_visit_code()
        
        # Validate GPS location against farm polygon if farm has polygon
        if self.farm.polygon and self.gps_location:
            # Check if GPS point is within farm polygon (with some tolerance)
            # Using buffer for GPS accuracy
            buffer_distance = self.gps_accuracy or 50  # Default 50m buffer
            self.is_gps_validated = self.farm.polygon.buffer(buffer_distance / 111320).contains(
                self.gps_location
            )
        
        # Set submitted_at when status changes to submitted
        if self.status == 'submitted' and not self.submitted_at:
            from django.utils import timezone
            self.submitted_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def generate_visit_code(self):
        """Generate unique visit code."""
        import random
        import string
        from django.utils import timezone
        
        # Format: VISIT-YEAR-RANDOM (e.g., VISIT-2025-A1B2C3)
        year = timezone.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        visit_code = f"VISIT-{year}-{random_part}"
        
        # Ensure uniqueness
        while Visit.objects.filter(visit_code=visit_code).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            visit_code = f"VISIT-{year}-{random_part}"
        
        return visit_code
    
    @property
    def duration_minutes(self):
        """Calculate visit duration if start/end times are in metadata."""
        start = self.metadata.get('start_time')
        end = self.metadata.get('end_time')
        if start and end:
            # Assuming ISO format timestamps
            from datetime import datetime
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                delta = end_dt - start_dt
                return int(delta.total_seconds() / 60)
            except:
                return None
        return None


class VisitComment(TimeStampedModel):
    """
    Comments on visits for collaboration and feedback.
    """
    
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='visit_comments'
    )
    comment = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal comment (not visible to field officer)"
    )
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.visit.visit_code} by {self.user.get_full_name()}"


class VisitMedia(TimeStampedModel):
    """
    Link media files to visits.
    """
    
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='media_files'
    )
    media = models.ForeignKey(
        'media.Media',
        on_delete=models.CASCADE,
        related_name='visit_links'
    )
    
    class Meta:
        unique_together = [['visit', 'media']]
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.visit.visit_code} - {self.media.file.name}"

