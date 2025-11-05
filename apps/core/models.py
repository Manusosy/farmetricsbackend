"""
Core models for shared functionality across the Farmetrics platform.
"""

import uuid
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating 
    `created_at` and `updated_at` fields.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteQuerySet(models.QuerySet):
    """Custom QuerySet for soft delete functionality."""
    
    def delete(self):
        """Soft delete all objects in the queryset."""
        return self.update(deleted_at=timezone.now())
    
    def hard_delete(self):
        """Permanently delete all objects in the queryset."""
        return super().delete()
    
    def alive(self):
        """Return only non-deleted objects."""
        return self.filter(deleted_at__isnull=True)
    
    def dead(self):
        """Return only deleted objects."""
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    """Manager that uses SoftDeleteQuerySet."""
    
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()
    
    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        return SoftDeleteQuerySet(self.model, using=self._db).dead()


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract base model that provides soft delete functionality.
    """
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Access all objects including deleted
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete the object."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])
    
    def hard_delete(self):
        """Permanently delete the object."""
        super().delete()
    
    def restore(self):
        """Restore a soft-deleted object."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])
    
    @property
    def is_deleted(self):
        """Check if object is deleted."""
        return self.deleted_at is not None

