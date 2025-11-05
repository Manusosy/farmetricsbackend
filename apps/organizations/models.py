"""
Organization models for multi-tenancy support.
"""

from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel


class Organization(TimeStampedModel):
    """
    Organization model for multi-tenancy.
    Each organization represents a separate farm monitoring entity.
    """
    
    SUBSCRIPTION_TIERS = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    # Contact information
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Subscription & billing
    subscription_tier = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TIERS,
        default='free'
    )
    
    # Settings stored as JSON
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Organization-specific configuration settings"
    )
    
    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Branding
    logo = models.ImageField(upload_to='organizations/logos/', null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_enterprise(self):
        """Check if organization is on enterprise tier."""
        return self.subscription_tier == 'enterprise'
    
    @property
    def member_count(self):
        """Get total number of members in the organization."""
        return self.memberships.filter(is_active=True).count()


class OrganizationMembership(TimeStampedModel):
    """
    Link between users and organizations with role information.
    """
    
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('country_admin', 'Country Admin'),
        ('supervisor', 'Supervisor'),
        ('field_officer', 'Field Officer'),
        ('analyst', 'Analyst'),
        ('auditor', 'Auditor'),
    ]
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        'accounts.User',  # String reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='field_officer')
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Who added this user to the organization
    invited_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_memberships'
    )
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['organization', 'user']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.organization.name} ({self.role})"

