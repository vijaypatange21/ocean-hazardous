from django.db import models
from django.utils import timezone

class SatelliteReading(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField()
    longitude = models.FloatField()
    sea_surface_temperature = models.FloatField()
    wave_height = models.FloatField()
    wind_speed = models.FloatField()
    ocean_color_index = models.FloatField()
    
    class Meta:
        ordering = ['-timestamp']

class OceanHazard(models.Model):
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
    
    hazard_type = models.CharField(max_length=20, choices=HAZARD_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_name = models.CharField(max_length=200)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-timestamp']

# dashboard/admin.py
from django.contrib import admin
from .models import SatelliteReading, OceanHazard

@admin.register(SatelliteReading)
class SatelliteReadingAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'latitude', 'longitude', 'sea_surface_temperature', 'wave_height']
    list_filter = ['timestamp']
    search_fields = ['location_name']

@admin.register(OceanHazard)
class OceanHazardAdmin(admin.ModelAdmin):
    list_display = ['hazard_type', 'severity', 'location_name', 'timestamp', 'is_active']
    list_filter = ['hazard_type', 'severity', 'is_active', 'timestamp']
    search_fields = ['location_name', 'description']
