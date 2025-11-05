"""
Media models for handling images, videos, and documents with EXIF extraction.
"""

from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.files.storage import default_storage
from apps.core.models import TimeStampedModel, SoftDeleteModel
import os


class Media(SoftDeleteModel):
    """
    Media file (image, video, document) with EXIF metadata extraction.
    """
    
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
    ]
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='media_files'
    )
    
    # File Information
    file = models.FileField(
        upload_to='media/%Y/%m/%d/',
        help_text="Uploaded media file"
    )
    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPE_CHOICES,
        db_index=True
    )
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(
        help_text="File size in bytes"
    )
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Upload Information
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='uploaded_media'
    )
    
    # GPS Location (from EXIF or manual entry)
    gps_location = gis_models.PointField(
        srid=4326,
        null=True,
        blank=True,
        help_text="GPS location where media was captured"
    )
    gps_accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="GPS accuracy in meters"
    )
    
    # EXIF Data (stored as JSON)
    exif_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extracted EXIF metadata from image"
    )
    
    # Common EXIF fields (extracted for easy querying)
    camera_make = models.CharField(max_length=100, blank=True)
    camera_model = models.CharField(max_length=100, blank=True)
    date_taken = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date/time when photo was taken (from EXIF)"
    )
    orientation = models.IntegerField(
        null=True,
        blank=True,
        help_text="Image orientation (1-8)"
    )
    
    # Image-specific fields
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    
    # Video-specific fields
    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Video duration in seconds"
    )
    
    # Description & Tags
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of tags for categorization"
    )
    
    # Relationships
    related_farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='media_files'
    )
    related_farmer = models.ForeignKey(
        'farmers.Farmer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='media_files'
    )
    
    # Status
    is_public = models.BooleanField(
        default=False,
        help_text="Whether media is publicly accessible"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether media has been verified"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'media_type']),
            models.Index(fields=['uploaded_by', 'created_at']),
            models.Index(fields=['date_taken']),
            models.Index(fields=['related_farm']),
            models.Index(fields=['related_farmer']),
        ]
    
    def __str__(self):
        return f"{self.file_name} ({self.media_type})"
    
    def save(self, *args, **kwargs):
        # Extract file information if new file
        if self.file and not self.file_name:
            self.file_name = os.path.basename(self.file.name)
            self.file_size = self.file.size
        
        # Determine media type from file extension if not set
        if not self.media_type and self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic']:
                self.media_type = 'image'
            elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                self.media_type = 'video'
            elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt']:
                self.media_type = 'document'
            elif ext in ['.mp3', '.wav', '.m4a', '.aac']:
                self.media_type = 'audio'
        
        super().save(*args, **kwargs)
        
        # Extract EXIF data for images (async task recommended)
        if self.media_type == 'image' and self.file:
            self.extract_exif_data()
    
    def extract_exif_data(self):
        """
        Extract EXIF data from image file.
        Uses Pillow for EXIF extraction.
        """
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            import json
            from datetime import datetime
            
            if not self.file:
                return
            
            # Open image and extract EXIF
            with Image.open(self.file) as img:
                exif_dict = {}
                
                # Get EXIF data
                exif = img._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = str(value)
                        
                        # Extract common fields
                        if tag == 'Make':
                            self.camera_make = str(value)
                        elif tag == 'Model':
                            self.camera_model = str(value)
                        elif tag == 'DateTime':
                            try:
                                self.date_taken = datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                            except:
                                pass
                        elif tag == 'Orientation':
                            self.orientation = value
                
                # Get image dimensions
                self.width = img.width
                self.height = img.height
                
                # Extract GPS data
                gps_info = exif_dict.get('GPSInfo')
                if gps_info:
                    gps_data = {}
                    for key, value in gps_info.items():
                        tag = GPSTAGS.get(key, key)
                        gps_data[tag] = str(value)
                    
                    # Convert GPS to Point if coordinates available
                    if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                        try:
                            lat = self._convert_to_degrees(gps_data.get('GPSLatitude'))
                            lon = self._convert_to_degrees(gps_data.get('GPSLongitude'))
                            
                            # Handle North/South and East/West
                            if gps_data.get('GPSLatitudeRef') == 'S':
                                lat = -lat
                            if gps_data.get('GPSLongitudeRef') == 'W':
                                lon = -lon
                            
                            from django.contrib.gis.geos import Point
                            self.gps_location = Point(lon, lat, srid=4326)
                        except:
                            pass
                
                # Store full EXIF data
                self.exif_data = exif_dict
                
                # Save updates
                self.save(update_fields=[
                    'exif_data', 'camera_make', 'camera_model', 'date_taken',
                    'orientation', 'width', 'height', 'gps_location'
                ])
                
        except Exception as e:
            # Log error but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to extract EXIF data: {e}")
    
    def _convert_to_degrees(self, value):
        """Convert GPS coordinate to decimal degrees."""
        try:
            # Handle different formats
            if isinstance(value, str):
                # Parse string format like "41/1, 5/1, 0/1"
                parts = value.split(',')
                degrees = float(parts[0].split('/')[0]) / float(parts[0].split('/')[1])
                minutes = float(parts[1].split('/')[0]) / float(parts[1].split('/')[1])
                seconds = float(parts[2].split('/')[0]) / float(parts[2].split('/')[1])
                return degrees + (minutes / 60.0) + (seconds / 3600.0)
            elif isinstance(value, tuple):
                degrees = value[0] / value[1] if value[1] != 0 else 0
                minutes = value[2] / value[3] if value[3] != 0 else 0
                seconds = value[4] / value[5] if value[5] != 0 else 0
                return degrees + (minutes / 60.0) + (seconds / 3600.0)
            else:
                return float(value)
        except:
            return None
    
    @property
    def file_url(self):
        """Get URL for the media file."""
        if self.file:
            return self.file.url
        return None
    
    @property
    def thumbnail_url(self):
        """Get thumbnail URL (to be implemented with image processing)."""
        # TODO: Generate and return thumbnail URL
        return self.file_url

