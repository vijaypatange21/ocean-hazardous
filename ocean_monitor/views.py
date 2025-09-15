from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
from datetime import datetime, timedelta

# ============================================================================
# MAIN DASHBOARD VIEWS
# ============================================================================
import random
import math

def dashboard(request):
    """Main dashboard view"""
    return render(request, 'dashboard/index.html')

# ============================================================================
# API ENDPOINTS - SATELLITE DATA
# ============================================================================

def get_satellite_data(request):
    """API endpoint to get real-time satellite data"""
    # Simulate real-time satellite monitoring data
    data = {
        'timestamp': datetime.now().isoformat(),
        'sea_surface_temperature': round(random.uniform(20, 30), 2),
        'wave_height': round(random.uniform(0.5, 4.0), 2),
        'wind_speed': round(random.uniform(5, 25), 2),
        'ocean_color_index': round(random.uniform(0.1, 1.0), 2),
        'locations': [
            {
                'lat': 11.5 + random.uniform(-2, 2),
                'lng': 78.0 + random.uniform(-2, 2),
                'temperature': round(random.uniform(24, 28), 1),
                'status': random.choice(['normal', 'warning', 'alert'])
            }
            for _ in range(10)
        ]
    }
    return JsonResponse(data)

# ============================================================================
# API ENDPOINTS - HAZARD MONITORING
# ============================================================================

def get_ocean_hazards(request):
    """API endpoint to get ocean hazard alerts from satellite monitoring"""
    hazards = [
        {
            'id': i,
            'type': random.choice(['tsunami', 'high_waves', 'storm_surge', 'coastal_current']),
            'severity': random.choice(['low', 'medium', 'high']),
            'location': f"Coastal Area {i}",
            'lat': 8.0 + random.uniform(0, 15),
            'lng': 68.0 + random.uniform(0, 20),
            'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
            'description': f"Ocean hazard alert #{i} detected by satellite monitoring"
        }
        for i in range(5)
    ]
    return JsonResponse({'hazards': hazards})
