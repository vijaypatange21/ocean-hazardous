from django.db import models
from django.utils import timezone

# ============================================================================
# SATELLITE MONITORING MODELS
# ============================================================================

class SatelliteReading(models.Model):
    """Satellite readings for ocean and weather monitoring"""
    
    # Location data
    timestamp = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Environmental readings
    sea_surface_temperature = models.FloatField()  # in celsius
    wave_height = models.FloatField()  # in meters
    wind_speed = models.FloatField()  # in m/s
    ocean_color_index = models.FloatField()  # satellite color measurement
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Satellite Reading {self.timestamp} - {self.latitude}, {self.longitude}"

# ============================================================================
# HAZARD MONITORING MODELS
# ============================================================================

class OceanHazard(models.Model):
    """Ocean hazard alerts detected through satellite monitoring"""
    
    HAZARD_TYPES = [
        ('tsunami', 'Tsunami'),
        ('high_waves', 'High Waves'),
        ('storm_surge', 'Storm Surge'),
        ('coastal_current', 'Coastal Current'),
        ('swell_surge', 'Swell Surge'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Hazard classification
    hazard_type = models.CharField(max_length=20, choices=HAZARD_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    
    # Location information
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_name = models.CharField(max_length=200)
    
    # Details and status
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_hazard_type_display()} - {self.location_name} ({self.get_severity_display()})"


# ============================================================================
# dashboard/admin.py - Django admin configuration
# ============================================================================

from django.contrib import admin
from .models import SatelliteReading, OceanHazard

# ============================================================================
# SATELLITE DATA ADMIN
# ============================================================================

@admin.register(SatelliteReading)
class SatelliteReadingAdmin(admin.ModelAdmin):
    """Admin interface for satellite readings"""
    
    list_display = [
        'timestamp', 
        'latitude', 
        'longitude', 
        'sea_surface_temperature', 
        'wave_height'
    ]
    list_filter = ['timestamp']
    search_fields = ['latitude', 'longitude']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Location', {
            'fields': ('timestamp', 'latitude', 'longitude')
        }),
        ('Environmental Data', {
            'fields': ('sea_surface_temperature', 'wave_height', 'wind_speed', 'ocean_color_index')
        }),
    )

# ============================================================================
# HAZARD MONITORING ADMIN
# ============================================================================

@admin.register(OceanHazard)
class OceanHazardAdmin(admin.ModelAdmin):
    """Admin interface for ocean hazard alerts"""
    
    list_display = [
        'hazard_type', 
        'severity', 
        'location_name', 
        'timestamp', 
        'is_active'
    ]
    list_filter = [
        'hazard_type', 
        'severity', 
        'is_active', 
        'timestamp'
    ]
    search_fields = ['location_name', 'description']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Hazard Information', {
            'fields': ('hazard_type', 'severity', 'is_active')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_name')
        }),
        ('Details', {
            'fields': ('description', 'timestamp')
        }),
    )
    
    actions = ['mark_inactive', 'mark_active']
    
    def mark_inactive(self, request, queryset):
        """Mark selected hazards as inactive"""
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} hazards marked as inactive.")
    mark_inactive.short_description = "Mark selected hazards as inactive"
    
    def mark_active(self, request, queryset):
        """Mark selected hazards as active"""
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} hazards marked as active.")
    mark_active.short_description = "Mark selected hazards as active"