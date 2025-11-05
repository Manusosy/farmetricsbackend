"""
Region models for geographic hierarchy and management.
"""

from django.contrib.gis.db import models as gis_models
from django.db import models
from apps.core.models import TimeStampedModel


class Region(TimeStampedModel):
    """
    Geographic region model with hierarchical structure.
    Supports PostGIS for polygon boundaries.
    """
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='regions'
    )
    
    # Basic information
    name = models.CharField(max_length=200, db_index=True)
    code = models.CharField(
        max_length=50,
        help_text="Unique region code within organization (e.g., GH-ASHANTI-KUMASI)"
    )
    description = models.TextField(blank=True)
    
    # Hierarchy support
    parent_region = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subregions',
        help_text="Parent region for hierarchical structure"
    )
    level = models.IntegerField(
        default=0,
        help_text="Hierarchy level: 0=Country, 1=Region, 2=District, 3=Location/Community"
    )
    
    LEVEL_CHOICES = [
        (0, 'Country'),
        (1, 'Region'),
        (2, 'District'),
        (3, 'Location'),
    ]
    
    level_type = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='location',
        help_text="Type of geographic level"
    )
    
    # Geospatial data
    polygon = gis_models.MultiPolygonField(
        null=True,
        blank=True,
        srid=4326,  # WGS 84 coordinate system
        help_text="Geographic boundary of the region"
    )
    center_point = gis_models.PointField(
        null=True,
        blank=True,
        srid=4326,
        help_text="Center point of the region (for map markers)"
    )
    area_sqkm = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Area in square kilometers"
    )
    
    # Management
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional region metadata (population, climate, etc.)"
    )
    
    class Meta:
        ordering = ['organization', 'level', 'name']
        unique_together = [['organization', 'code']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['parent_region']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate level from parent
        if self.parent_region:
            self.level = self.parent_region.level + 1
        else:
            self.level = 0
        
        # Auto-calculate area from polygon if not set
        if self.polygon and not self.area_sqkm:
            # Transform to equal-area projection for accurate area calculation
            # Then convert from sq meters to sq kilometers
            area_m2 = self.polygon.transform(3857, clone=True).area
            self.area_sqkm = area_m2 / 1_000_000
        
        # Auto-calculate center point from polygon if not set
        if self.polygon and not self.center_point:
            self.center_point = self.polygon.centroid
        
        super().save(*args, **kwargs)
    
    @property
    def full_path(self):
        """Get full hierarchical path (e.g., Ghana > Ashanti > Kumasi)."""
        path = [self.name]
        parent = self.parent_region
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent_region
        return ' > '.join(path)
    
    @property
    def children_count(self):
        """Get count of direct child regions."""
        return self.subregions.filter(is_active=True).count()
    
    def get_all_children(self):
        """Recursively get all descendant regions."""
        children = list(self.subregions.filter(is_active=True))
        for child in list(children):
            children.extend(child.get_all_children())
        return children
    
    def get_all_ancestors(self):
        """Get all parent regions up to the root."""
        ancestors = []
        parent = self.parent_region
        while parent:
            ancestors.append(parent)
            parent = parent.parent_region
        return ancestors


class RegionSupervisor(TimeStampedModel):
    """
    Assignment of supervisors to regions.
    A supervisor can manage multiple regions.
    """
    
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='supervisor_assignments'
    )
    supervisor = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='supervised_regions'
    )
    
    assigned_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_region_supervisors'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Optional: supervisor can be temporary
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-assigned_at']
        unique_together = [['region', 'supervisor']]
        indexes = [
            models.Index(fields=['region', 'is_active']),
            models.Index(fields=['supervisor', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.supervisor.get_full_name()} supervises {self.region.name}"

