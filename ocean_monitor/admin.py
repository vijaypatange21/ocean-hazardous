from django.contrib import admin
from .models import SatelliteReading, OceanHazard
# Alternative registration method to avoid conflicts
class SatelliteReadingAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'latitude', 'longitude', 'sea_surface_temperature', 'wave_height']
    list_filter = ['timestamp']
    search_fields = ['latitude', 'longitude']

class OceanHazardAdmin(admin.ModelAdmin):
    list_display = ['hazard_type', 'severity', 'location_name', 'timestamp', 'is_active']
    list_filter = ['hazard_type', 'severity', 'is_active', 'timestamp']
    search_fields = ['location_name', 'description']

# Register models manually to avoid duplicate registration
try:
    admin.site.register(SatelliteReading, SatelliteReadingAdmin)
except admin.sites.AlreadyRegistered:
    admin.site.unregister(SatelliteReading)
    admin.site.register(SatelliteReading, SatelliteReadingAdmin)

try:
    admin.site.register(OceanHazard, OceanHazardAdmin)
except admin.sites.AlreadyRegistered:
    admin.site.unregister(OceanHazard)
    admin.site.register(OceanHazard, OceanHazardAdmin)