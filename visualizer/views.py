from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from login.models import HazardReport
from datetime import timedelta

# ============================================================================
# MAIN DASHBOARD VIEWS
# ============================================================================

# @login_required  # Commented out - uncomment when authentication is needed
def dashboard(request):
    """Main dashboard view with filtering capabilities for hazard reports"""
    
    if request.method == "GET":
        # Default view - show all hazards
        hazards = HazardReport.objects.all()
        filters = {}
        
    elif request.method == "POST":
        # Apply filters based on form data
        hazards = HazardReport.objects.all()
        filters = {}
        
        # Time range filtering
        time_range = request.POST.get('time-range')
        if time_range:
            time_threshold = _parse_time_range(time_range)
            hazards = hazards.filter(created_at__gte=time_threshold)
            filters['time_range'] = time_range
        
        # Hazard type filtering
        hazard_type = request.POST.get('hazard-type')
        if hazard_type:
            hazards = hazards.filter(hazard_type=hazard_type)
            filters['hazard_type'] = hazard_type
        
        # Severity filtering
        severity = request.POST.get('severity')
        if severity:
            hazards = hazards.filter(severity=severity)
            filters['severity'] = severity
    
    # Convert hazards to JSON format for frontend consumption
    hazards_json = _convert_hazards_to_json(hazards)
    
    return render(request, 'dashboard.html', {
        'hazards': hazards_json, 
        'filters': filters
    })

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _parse_time_range(time_range):
    """Parse time range string (e.g., '7d', '24h') and return datetime threshold"""
    if not time_range or len(time_range) < 2:
        return timezone.now()
    
    try:
        value = int(time_range[:-1])
        unit = time_range[-1].lower()
        
        if unit == 'd':
            return timezone.now() - timedelta(days=value)
        elif unit == 'h':
            return timezone.now() - timedelta(hours=value)
        else:
            # Default to hours if unit is not recognized
            return timezone.now() - timedelta(hours=value)
            
    except (ValueError, IndexError):
        # Return current time if parsing fails
        return timezone.now()

def _convert_hazards_to_json(hazards):
    """Convert hazard queryset to JSON-serializable format for frontend"""
    hazards_json = []
    
    for hazard in hazards:
        hazard_data = {
            'lat': hazard.latitude,
            'lng': hazard.longitude,
            'hazardType': hazard.hazard_type,
            'severity': hazard.severity,
            'time': hazard.created_at,
            'location': hazard.location_name,
            'description': hazard.description
        }
        hazards_json.append(hazard_data)
    
    return hazards_json