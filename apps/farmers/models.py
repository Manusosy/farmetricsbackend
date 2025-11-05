"""
Farmer models for managing farmer records and profiles.
"""

from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from apps.core.models import TimeStampedModel, SoftDeleteModel


class Farmer(SoftDeleteModel):
    """
    Farmer model representing individual farmers or farm owners.
    """
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged for Review'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='farmers'
    )
    
    # Basic Information
    farmer_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique farmer identifier (auto-generated if not provided)"
    )
    first_name = models.CharField(max_length=100, db_index=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, db_index=True)
    
    # Contact Information
    phone_number = PhoneNumberField(help_text="Primary phone number")
    alternate_phone = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True)
    
    # Identification
    national_id = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="National ID, Voter ID, or other government ID"
    )
    national_id_type = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('national_id', 'National ID'),
            ('voter_id', 'Voter ID'),
            ('passport', 'Passport'),
            ('drivers_license', "Driver's License"),
            ('other', 'Other'),
        ]
    )
    
    # Demographics
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    # Address
    address = models.TextField(blank=True)
    region = models.ForeignKey(
        'regions.Region',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='farmers'
    )
    community = models.CharField(max_length=200, blank=True)
    gps_coordinates = models.CharField(
        max_length=100,
        blank=True,
        help_text="GPS coordinates in format: lat,lon"
    )
    
    # Farming Information
    years_of_experience = models.IntegerField(
        null=True,
        blank=True,
        help_text="Years of farming experience"
    )
    primary_crop = models.CharField(max_length=100, blank=True, default='Cocoa')
    secondary_crops = models.JSONField(
        default=list,
        blank=True,
        help_text="List of other crops farmed"
    )
    
    # Verification
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_farmers'
    )
    verification_notes = models.TextField(blank=True)
    
    # Profile Media
    profile_photo = models.ImageField(
        upload_to='farmers/profiles/',
        null=True,
        blank=True
    )
    
    # Documents
    documents = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of document references (land titles, certificates, etc.)"
    )
    
    # Data Management
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_farmers'
    )
    last_updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_farmers'
    )
    
    # Additional Information
    notes = models.TextField(blank=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional farmer metadata"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'verification_status']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['national_id']),
            models.Index(fields=['region']),
            models.Index(fields=['first_name', 'last_name']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.farmer_id})"
    
    def save(self, *args, **kwargs):
        # Auto-generate farmer ID if not provided
        if not self.farmer_id:
            self.farmer_id = self.generate_farmer_id()
        super().save(*args, **kwargs)
    
    def generate_farmer_id(self):
        """Generate unique farmer ID."""
        import random
        import string
        from django.utils import timezone
        
        # Format: ORG-YEAR-RANDOM (e.g., FAR-2025-A1B2C3)
        org_code = self.organization.slug[:3].upper()
        year = timezone.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        farmer_id = f"{org_code}-{year}-{random_part}"
        
        # Ensure uniqueness
        while Farmer.objects.filter(farmer_id=farmer_id).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            farmer_id = f"{org_code}-{year}-{random_part}"
        
        return farmer_id
    
    def get_full_name(self):
        """Return full name of farmer."""
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, parts))
    
    @property
    def age(self):
        """Calculate age from date of birth."""
        if self.date_of_birth:
            from django.utils import timezone
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def total_farms(self):
        """Get total number of farms owned by this farmer."""
        return self.farms.filter(deleted_at__isnull=True).count()
    
    @property
    def total_farm_area(self):
        """Get total area of all farms in square meters."""
        from django.db.models import Sum
        result = self.farms.filter(deleted_at__isnull=True).aggregate(
            total=Sum('area_m2')
        )
        return result['total'] or 0


class FarmerMergeHistory(TimeStampedModel):
    """
    Track farmer merges for auditing duplicate resolution.
    """
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='farmer_merges'
    )
    
    primary_farmer = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE,
        related_name='merge_primary_records',
        help_text="The farmer record that was kept"
    )
    merged_farmer_id = models.CharField(
        max_length=50,
        help_text="ID of the farmer that was merged (and deleted)"
    )
    merged_farmer_data = models.JSONField(
        help_text="Full data snapshot of the merged farmer"
    )
    
    merged_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='farmer_merges_performed'
    )
    merge_reason = models.TextField(help_text="Reason for merge")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['primary_farmer']),
            models.Index(fields=['merged_farmer_id']),
        ]
    
    def __str__(self):
        return f"Merged {self.merged_farmer_id} into {self.primary_farmer.farmer_id}"

