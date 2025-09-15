# ============================================================================
# analyst/models.py - Analyst application models
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import requests
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ============================================================================
# BUOY MONITORING MODELS
# ============================================================================

class DartBuoy(models.Model):
    """Model for DART (Deep-ocean Assessment and Reporting of Tsunamis) buoys"""
    
    buoy_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, default="Unnamed Buoy")
    latitude = models.FloatField()
    longitude = models.FloatField()
    last_report_time = models.DateTimeField(null=True, blank=True)
    
    # Sensor data fields
    wave_height = models.FloatField(null=True, blank=True)  # in meters
    water_temperature = models.FloatField(null=True, blank=True)  # in celsius
    wind_speed = models.FloatField(null=True, blank=True)  # in m/s
    pressure = models.FloatField(null=True, blank=True)  # in hPa
    
    # Status and timestamps
    status = models.CharField(max_length=20, default="unknown")  # active / maintenance / offline
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.buoy_id} - {self.name}"

    def fetch_live_data(self):
        """Fetch live data from NOAA NDBC for this buoy"""
        try:
            # Use NOAA's real-time data API
            url = f"https://www.ndbc.noaa.gov/data/realtime2/{self.buoy_id}.txt"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                if len(lines) >= 3:  # Header, units, data
                    headers = lines[0].split()
                    data_line = lines[2].split()
                    
                    # Parse the most recent data
                    data_dict = dict(zip(headers, data_line))
                    
                    # Update fields based on available data
                    if 'WVHT' in data_dict and data_dict['WVHT'] != 'MM':
                        self.wave_height = float(data_dict['WVHT'])
                    
                    if 'WTMP' in data_dict and data_dict['WTMP'] != 'MM':
                        self.water_temperature = float(data_dict['WTMP'])
                    
                    if 'WSPD' in data_dict and data_dict['WSPD'] != 'MM':
                        self.wind_speed = float(data_dict['WSPD'])
                    
                    if 'PRES' in data_dict and data_dict['PRES'] != 'MM':
                        self.pressure = float(data_dict['PRES'])
                    
                    self.last_report_time = timezone.now()
                    self.status = "active"
                    logger.info(f"Successfully updated buoy {self.buoy_id}")
                else:
                    self.status = "offline"
            else:
                self.status = "offline"
                
        except Exception as e:
            logger.error(f"Failed to fetch data for buoy {self.buoy_id}: {e}")
            self.status = "offline"
        finally:
            self.save()

    def get_historical_data(self, hours=24):
        """Get historical data for charting"""
        return BuoyReading.objects.filter(
            buoy=self,
            timestamp__gte=timezone.now() - timedelta(hours=hours)
        ).order_by('timestamp')


class BuoyReading(models.Model):
    """Store historical buoy readings for charting and analysis"""
    
    buoy = models.ForeignKey(DartBuoy, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField()
    wave_height = models.FloatField(null=True, blank=True)
    water_temperature = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        unique_together = ['buoy', 'timestamp']

# ============================================================================
# REPORT MANAGEMENT MODELS
# ============================================================================

class Report(models.Model):
    """Analyst reports submitted to administrators"""
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    REPORT_TYPES = (
        ('event', 'Event Analysis Report'),
        ('risk', 'Risk Assessment Summary'),
        ('performance', 'Performance Evaluation'),
        ('compliance', 'Compliance Report'),
    )
    
    # Basic report information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=32, choices=REPORT_TYPES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft')
    
    # User relationships
    created_by = models.ForeignKey(User, related_name='reports_created', on_delete=models.CASCADE)
    submitted_to = models.ForeignKey(User, related_name='reports_assigned', blank=True, null=True, on_delete=models.SET_NULL)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    
    # File attachment
    attachment = models.FileField(upload_to='report_attachments/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class ReportComment(models.Model):
    """Comments and feedback on reports from administrators"""
    
    report = models.ForeignKey(Report, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def update_india_buoys():
    """Update Indian Ocean buoys with real NOAA buoy IDs"""
    # Real NOAA buoy IDs near Indian Ocean/Indian coastline
    indian_buoys = [
        {"id": "23001", "name": "Arabian Sea", "lat": 17.35, "lon": 68.13},
        {"id": "23101", "name": "Arabian Sea North", "lat": 15.00, "lon": 61.50},
        {"id": "23007", "name": "Lakshadweep Sea", "lat": 13.07, "lon": 74.00},
        {"id": "46002", "name": "Indian Ocean", "lat": -17.75, "lon": 63.45},
    ]
    
    try:
        for buoy_data in indian_buoys:
            obj, created = DartBuoy.objects.get_or_create(
                buoy_id=buoy_data['id'],
                defaults={
                    'name': buoy_data['name'],
                    'latitude': buoy_data['lat'],
                    'longitude': buoy_data['lon'],
                    'status': 'unknown'
                }
            )
            
            # Fetch live data
            obj.fetch_live_data()
            
            # Store reading for historical data
            if obj.status == "active":
                BuoyReading.objects.get_or_create(
                    buoy=obj,
                    timestamp=obj.last_report_time or timezone.now(),
                    defaults={
                        'wave_height': obj.wave_height,
                        'water_temperature': obj.water_temperature,
                        'wind_speed': obj.wind_speed,
                        'pressure': obj.pressure,
                    }
                )
                
        logger.info("Successfully updated Indian Ocean buoys")
    except Exception as e:
        logger.error(f"Failed to fetch Indian Ocean buoys: {e}")