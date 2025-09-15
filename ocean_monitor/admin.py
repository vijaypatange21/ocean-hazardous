from django.contrib import admin
from .models import SatelliteReading, OceanHazard

# ============================================================================
# ADMIN CLASS DEFINITIONS
# ============================================================================

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
        ('Location & Time', {
            'fields': ('timestamp', 'latitude', 'longitude')
        }),
        ('Environmental Data', {
            'fields': ('sea_surface_temperature', 'wave_height', 'wind_speed', 'ocean_color_index')
        }),
    )


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
        ('Hazard Classification', {
            'fields': ('hazard_type', 'severity', 'is_active')
        }),
        ('Location Details', {
            'fields': ('latitude', 'longitude', 'location_name')
        }),
        ('Additional Information', {
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

# ============================================================================
# MODEL REGISTRATION - CONFLICT SAFE
# ============================================================================

# Register SatelliteReading with conflict handling
try:
    admin.site.register(SatelliteReading, SatelliteReadingAdmin)
except admin.sites.AlreadyRegistered:
    admin.site.unregister(SatelliteReading)
    admin.site.register(SatelliteReading, SatelliteReadingAdmin)

# Register OceanHazard with conflict handling
try:
    admin.site.register(OceanHazard, OceanHazardAdmin)
except admin.sites.AlreadyRegistered:
    admin.site.unregister(OceanHazard)
    admin.site.register(OceanHazard, OceanHazardAdmin)