"""
User and authentication models.
"""

import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with additional fields for Farmetrics.
    Uses email as the primary identifier instead of username.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Override username to be optional
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    
    # Email as primary identifier
    email = models.EmailField(unique=True, db_index=True)
    
    # Additional profile fields
    phone_number = PhoneNumberField(blank=True, null=True, help_text="User's contact phone number")
    employee_id = models.CharField(max_length=50, blank=True, help_text="Organization employee ID")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Address information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Ghana')
    
    # MFA fields
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True)
    
    # Account status
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return self.get_full_name() or self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
    
    @property
    def primary_organization(self):
        """Get user's primary organization (first active membership)."""
        membership = self.organization_memberships.filter(
            is_active=True
        ).select_related('organization').first()
        return membership.organization if membership else None
    
    @property
    def primary_role(self):
        """Get user's primary role (in first active organization)."""
        membership = self.organization_memberships.filter(
            is_active=True
        ).first()
        return membership.role if membership else None
    
    def has_organization_permission(self, organization, permission):
        """Check if user has a specific permission in an organization."""
        # Super admins have all permissions
        if self.is_superuser:
            return True
        
        # Check if user is member of the organization
        membership = self.organization_memberships.filter(
            organization=organization,
            is_active=True
        ).first()
        
        if not membership:
            return False
        
        # Check user's roles for the permission
        user_roles = self.user_roles.filter(
            role__organization=organization,
            is_active=True
        ).select_related('role')
        
        for user_role in user_roles:
            if permission in user_role.role.permissions:
                return True
        
        return False


class Role(TimeStampedModel):
    """
    Custom role for fine-grained permissions within an organization.
    """
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='roles'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    # Permissions stored as JSON array of permission strings
    # e.g., ["farmer.view", "farmer.create", "farm.edit", "visit.approve"]
    permissions = models.JSONField(
        default=list,
        help_text="List of permission strings for this role"
    )
    
    # Built-in roles cannot be deleted
    is_system_role = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['organization', 'name']
        unique_together = [['organization', 'slug']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class UserRole(TimeStampedModel):
    """
    Assignment of roles to users with tracking information.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Optional: role can be temporary
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-assigned_at']
        unique_together = [['user', 'role']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role.name}"
    
    @property
    def is_expired(self):
        """Check if the role assignment has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class PasswordResetToken(TimeStampedModel):
    """
    Password reset tokens for secure password recovery.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'used']),
        ]
    
    def __str__(self):
        return f"Password reset for {self.user.email}"
    
    @property
    def is_valid(self):
        """Check if token is still valid."""
        return not self.used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark token as used."""
        self.used = True
        self.used_at = timezone.now()
        self.save(update_fields=['used', 'used_at'])

