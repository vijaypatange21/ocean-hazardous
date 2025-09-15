from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


class UserProfile(models.Model):
    USER_TYPES = [
        ('analyst', 'Analyst'),
        ('reporter', 'Reporter'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    wallet_address = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class HazardReport(models.Model):
    HAZARD_TYPES = [
        ('tsunami', 'Tsunami'),
        ('storm_surge', 'Storm Surge'),
        ('high_waves', 'High Waves'),
        ('swell_surge', 'Swell Surge'),
        ('coastal_flooding', 'Coastal Flooding'),
        ('unusual_tides', 'Unusual Tides'),
        ('coastal_erosion', 'Coastal Erosion'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('investigating', 'Under Investigation'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hazard_reports')
    report_id = models.CharField(max_length=20, unique=True, blank=True)
    hazard_type = models.CharField(max_length=20, choices=HAZARD_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=15, decimal_places=10)
    longitude = models.DecimalField(max_digits=15, decimal_places=10)
    location_name = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    urgent = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_reports'
    )
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.report_id:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.report_id = f"HR{timestamp}"
        
        if self.status == 'verified' and not self.verified_at:
            self.verified_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    def get_severity_color(self):
        colors = {
            'low': 'success',
            'moderate': 'warning',
            'high': 'danger',
            'critical': 'dark'
        }
        return colors.get(self.severity, 'secondary')
    
    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'verified': 'success',
            'rejected': 'danger',
            'investigating': 'info'
        }
        return colors.get(self.status, 'secondary')
    
    def __str__(self):
        return f"{self.report_id} - {self.hazard_type} ({self.severity})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Hazard Report"
        verbose_name_plural = "Hazard Reports"


def hazard_media_upload_path(instance, filename):
    return f'hazard_reports/{instance.report.report_id}/{filename}'


class HazardMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    report = models.ForeignKey(HazardReport, on_delete=models.CASCADE, related_name='media_files')
    file = models.FileField(upload_to=hazard_media_upload_path)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    description = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.file:
            file_ext = os.path.splitext(self.file.name)[1].lower()
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                self.media_type = 'image'
            elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                self.media_type = 'video'
            
            if hasattr(self.file.file, 'size'):
                self.file_size = self.file.file.size
        
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        if not self.file_size:
            return "Unknown"
        
        size = self.file_size
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def __str__(self):
        return f"{self.report.report_id} - {self.media_type}"
    
    class Meta:
        ordering = ['uploaded_at']
        verbose_name = "Hazard Media"
        verbose_name_plural = "Hazard Media Files"


class HazardHotspot(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    radius = models.FloatField(help_text="Radius in kilometers")
    report_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.report_count} reports"
    
    class Meta:
        ordering = ['-report_count', '-last_updated']
        verbose_name = "Hazard Hotspot"
        verbose_name_plural = "Hazard Hotspots"


class ReportFeedback(models.Model):
    FEEDBACK_TYPES = [
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
        ('inaccurate', 'Inaccurate'),
        ('spam', 'Spam'),
    ]
    
    report = models.ForeignKey(HazardReport, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=15, choices=FEEDBACK_TYPES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['report', 'user']
        ordering = ['-created_at']
        verbose_name = "Report Feedback"
        verbose_name_plural = "Report Feedback"