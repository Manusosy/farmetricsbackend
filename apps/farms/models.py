"""
Farm models for managing farm records, boundaries, and history.
"""

from django.contrib.gis.db import models as gis_models
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import TimeStampedModel, SoftDeleteModel


class Farm(SoftDeleteModel):
    """
    Farm model representing agricultural land parcels with geospatial data.
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending_verification', 'Pending Verification'),
        ('verified', 'Verified'),
        ('flagged', 'Flagged'),
    ]
    
    SOIL_TYPE_CHOICES = [
        ('clay', 'Clay'),
        ('sandy', 'Sandy'),
        ('loam', 'Loam'),
        ('silt', 'Silt'),
        ('peat', 'Peat'),
        ('chalk', 'Chalk'),
        ('mixed', 'Mixed'),
        ('unknown', 'Unknown'),
    ]
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='farms'
    )
    
    # Basic Information
    farm_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique farm identifier (auto-generated if not provided)"
    )
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    
    # Ownership
    owner = models.ForeignKey(
        'farmers.Farmer',
        on_delete=models.CASCADE,
        related_name='farms'
    )
    
    # Location
    region = models.ForeignKey(
        'regions.Region',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='farms'
    )
    
    # Geospatial Data
    primary_location = gis_models.PointField(
        srid=4326,
        help_text="Primary GPS point for the farm (center or entrance)"
    )
    polygon = gis_models.MultiPolygonField(
        null=True,
        blank=True,
        srid=4326,
        help_text="Farm boundary polygon(s)"
    )
    area_m2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Farm area in square meters (auto-calculated from polygon)"
    )
    area_acres = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Farm area in acres (auto-calculated)"
    )
    
    # Farm Characteristics
    soil_type = models.CharField(
        max_length=20,
        choices=SOIL_TYPE_CHOICES,
        default='unknown'
    )
    crop_type = models.CharField(
        max_length=100,
        default='Cocoa',
        help_text="Primary crop grown"
    )
    other_crops = models.JSONField(
        default=list,
        blank=True,
        help_text="List of other crops grown on this farm"
    )
    
    planting_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when primary crop was planted"
    )
    tree_count_estimate = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Estimated number of trees"
    )
    tree_density = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Trees per hectare (auto-calculated if tree count available)"
    )
    
    # Status
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending_verification',
        db_index=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_farms'
    )
    
    # Management
    management_notes = models.TextField(blank=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional farm metadata (irrigation, certifications, etc.)"
    )
    
    # Data Management
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_farms'
    )
    last_updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_farms'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['owner']),
            models.Index(fields=['region']),
            models.Index(fields=['farm_code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.farm_code})"
    
    def save(self, *args, **kwargs):
        # Auto-generate farm code if not provided
        if not self.farm_code:
            self.farm_code = self.generate_farm_code()
        
        # Auto-calculate area from polygon
        if self.polygon:
            # Transform to equal-area projection for accurate area calculation
            area_m2 = self.polygon.transform(3857, clone=True).area
            self.area_m2 = area_m2
            self.area_acres = area_m2 / 4046.86  # Convert sq meters to acres
        
        # Auto-calculate tree density
        if self.tree_count_estimate and self.area_m2:
            hectares = self.area_m2 / 10000
            if hectares > 0:
                self.tree_density = self.tree_count_estimate / hectares
        
        super().save(*args, **kwargs)
    
    def generate_farm_code(self):
        """Generate unique farm code."""
        import random
        import string
        from django.utils import timezone
        
        # Format: FARM-YEAR-RANDOM (e.g., FARM-2025-X1Y2Z3)
        year = timezone.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        farm_code = f"FARM-{year}-{random_part}"
        
        # Ensure uniqueness
        while Farm.objects.filter(farm_code=farm_code).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            farm_code = f"FARM-{year}-{random_part}"
        
        return farm_code
    
    @property
    def age_years(self):
        """Calculate farm age in years from planting date."""
        if self.planting_date:
            from django.utils import timezone
            today = timezone.now().date()
            delta = today - self.planting_date
            return delta.days / 365.25
        return None
    
    @property
    def visit_count(self):
        """Get total number of visits to this farm."""
        return self.visits.count()


class FarmHistory(TimeStampedModel):
    """
    Track changes to farm boundaries and key attributes for auditing.
    """
    
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='history_records'
    )
    
    # What changed
    change_type = models.CharField(
        max_length=50,
        choices=[
            ('polygon_update', 'Polygon Updated'),
            ('ownership_transfer', 'Ownership Transferred'),
            ('status_change', 'Status Changed'),
            ('general_update', 'General Update'),
        ],
        db_index=True
    )
    
    # Snapshot of key fields at time of change
    polygon_snapshot = gis_models.MultiPolygonField(
        null=True,
        blank=True,
        srid=4326,
        help_text="Polygon at time of change"
    )
    area_m2_snapshot = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    owner_snapshot = models.CharField(
        max_length=200,
        blank=True,
        help_text="Owner name at time of change"
    )
    status_snapshot = models.CharField(max_length=30, blank=True)
    
    # Change metadata
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='farm_changes'
    )
    change_reason = models.TextField(
        blank=True,
        help_text="Reason for the change"
    )
    
    # Full data snapshot (for complete audit trail)
    data_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete farm data at time of change"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['farm', 'change_type']),
            models.Index(fields=['changed_by']),
        ]
        verbose_name = 'Farm History'
        verbose_name_plural = 'Farm Histories'
    
    def __str__(self):
        return f"{self.farm.name} - {self.change_type} ({self.created_at.strftime('%Y-%m-%d')})"


class FarmBoundaryPoint(TimeStampedModel):
    """
    Individual GPS points collected for farm boundary mapping.
    Useful for storing raw GPS data before creating final polygon.
    """
    
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='boundary_points'
    )
    
    point = gis_models.PointField(
        srid=4326,
        help_text="GPS coordinate point"
    )
    sequence = models.IntegerField(
        help_text="Order in which point was collected"
    )
    
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="GPS accuracy in meters"
    )
    altitude = models.FloatField(
        null=True,
        blank=True,
        help_text="Altitude in meters"
    )
    
    collected_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='collected_boundary_points'
    )
    collected_at = models.DateTimeField(auto_now_add=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['farm', 'sequence']
        indexes = [
            models.Index(fields=['farm', 'sequence']),
        ]
    
    def __str__(self):
        return f"{self.farm.name} - Point {self.sequence}"

