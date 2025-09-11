from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from login.models import UserProfile
from .models import DartBuoy, update_india_buoys, BuoyReading
import json
import random
import math
from datetime import datetime, timedelta

def analyst_required(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.userprofile.user_type != 'analyst':
                return redirect('login')
        except UserProfile.DoesNotExist:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)

def get_dashboard_context(user):
    """Generate context dynamically for analyst dashboard"""
    return {
        'user_name': user.first_name,
        'user_role': 'Analyst',
        'metrics': {
            'active_datasets': 142,
            'reports_this_month': 28,
            'active_stations': 89,
            'alert_rate': "97.3%"
        },
    }

@analyst_required
def dashboard_home(request):
    # Update buoys with latest data
    update_india_buoys()
    
    # Get all buoys
    buoys = DartBuoy.objects.all()
    
    context = {
        'buoys': buoys,
        **get_dashboard_context(request.user)
    }
    return render(request, 'analyst/index.html', context)

@analyst_required
def get_buoy_data(request):
    """API endpoint to get live buoy data for charts"""
    try:
        buoys_data = []
        for buoy in DartBuoy.objects.all():
            # Get historical data for the last 24 hours
            readings = buoy.get_historical_data(hours=24)
            
            chart_data = []
            for reading in readings:
                chart_data.append({
                    'timestamp': reading.timestamp.isoformat(),
                    'wave_height': reading.wave_height,
                    'temperature': reading.water_temperature,
                    'wind_speed': reading.wind_speed,
                    'pressure': reading.pressure,
                })
            
            buoys_data.append({
                'buoy_id': buoy.buoy_id,
                'name': buoy.name,
                'status': buoy.status,
                'current_wave_height': buoy.wave_height,
                'last_update': buoy.last_report_time.isoformat() if buoy.last_report_time else None,
                'chart_data': chart_data,
                'latitude': buoy.latitude,
                'longitude': buoy.longitude,
            })
        
        return JsonResponse({
            'success': True,
            'buoys': buoys_data,
            'timestamp': timezone.now().isoformat()
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@analyst_required  
def refresh_buoy_data(request):
    """Manually refresh all buoy data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'}, status=405)
        
    try:
        update_india_buoys()
        return JsonResponse({'success': True, 'message': 'Data refreshed successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# NEW API ENDPOINTS FOR INDIAN OCEAN ANALYTICS

@analyst_required
def get_storm_surge_data(request):
    """API endpoint for storm surge data"""
    try:
        # Generate time labels for 12-hour forecast (2-hour intervals)
        now = timezone.now()
        time_labels = []
        for i in range(12):
            time = now + timedelta(hours=i*2)
            time_labels.append(time.strftime('%H:%M'))
        
        # Indian Ocean regions with simulated surge data
        regions = [
            {
                'name': 'Arabian Sea Coast',
                'surge_data': generate_surge_data(2.1, 12)
            },
            {
                'name': 'Bay of Bengal',
                'surge_data': generate_surge_data(3.2, 12)
            },
            {
                'name': 'Maldives Region',
                'surge_data': generate_surge_data(1.8, 12)
            },
            {
                'name': 'Sri Lanka Coast',
                'surge_data': generate_surge_data(2.7, 12)
            }
        ]
        
        # Generate alerts based on surge predictions
        alerts = []
        for region in regions:
            max_surge = max(region['surge_data'])
            if max_surge > 3.0:
                level = 'high'
            elif max_surge > 2.5:
                level = 'medium'
            else:
                level = 'low'
                
            alerts.append({
                'location': region['name'],
                'height': f'{max_surge:.1f}m surge expected',
                'level': level
            })
        
        return JsonResponse({
            'success': True,
            'regions': regions,
            'time_labels': time_labels,
            'alerts': alerts,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@analyst_required
def get_seismic_data(request):
    """API endpoint for seismic activity data"""
    try:
        plates = [
            {
                'name': 'Indo-Australian Plate',
                'seismic_data': generate_seismic_data('indo_australian', 15)
            },
            {
                'name': 'Eurasian Plate',
                'seismic_data': generate_seismic_data('eurasian', 12)
            },
            {
                'name': 'Burma Plate',
                'seismic_data': generate_seismic_data('burma', 10)
            }
        ]
        
        return JsonResponse({
            'success': True,
            'plates': plates,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@analyst_required
def get_risk_assessment(request):
    """API endpoint for regional risk assessment"""
    try:
        # Simulate dynamic risk assessment for Indian Ocean regions
        base_time = timezone.now()
        
        regions = [
            {
                'region': 'Sumatra Coast',
                'score': round(8.5 + random.uniform(-0.5, 0.5), 1),
                'level': 'very-high'
            },
            {
                'region': 'Andaman Islands',
                'score': round(8.0 + random.uniform(-0.3, 0.4), 1),
                'level': 'high'
            },
            {
                'region': 'Sri Lanka Coast',
                'score': round(7.2 + random.uniform(-0.4, 0.6), 1),
                'level': 'high'
            },
            {
                'region': 'Maldives',
                'score': round(6.8 + random.uniform(-0.3, 0.4), 1),
                'level': 'medium'
            },
            {
                'region': 'Indian West Coast',
                'score': round(6.0 + random.uniform(-0.4, 0.6), 1),
                'level': 'medium'
            },
            {
                'region': 'Bangladesh Coast',
                'score': round(7.6 + random.uniform(-0.4, 0.5), 1),
                'level': 'high'
            }
        ]
        
        # Update risk levels based on scores
        for region in regions:
            if region['score'] >= 8.5:
                region['level'] = 'very-high'
            elif region['score'] >= 7.5:
                region['level'] = 'high'
            elif region['score'] >= 6.0:
                region['level'] = 'medium'
            else:
                region['level'] = 'low'
        
        return JsonResponse({
            'success': True,
            'regions': regions,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# HELPER FUNCTIONS FOR DATA GENERATION

def generate_surge_data(base_height, points):
    """Generate realistic storm surge data"""
    data = []
    for i in range(points):
        # Simulate tidal and storm effects
        tidal = math.sin(i * 0.5) * 0.3
        storm = math.sin(i * 0.2) * 0.8
        random_factor = (random.random() - 0.5) * 0.4
        surge = max(0, base_height + tidal + storm + random_factor)
        data.append(round(surge, 2))
    return data

def generate_seismic_data(plate_type, count):
    """Generate seismic activity data for different plates"""
    data = []
    
    if plate_type == 'indo_australian':
        # Higher tsunami risk due to subduction zones
        for i in range(count):
            magnitude = 4 + random.random() * 4.5
            risk = 6 + random.random() * 3 if magnitude > 7 else 2 + random.random() * 4
            data.append({
                'x': round(magnitude, 1),
                'y': round(risk, 1)
            })
    elif plate_type == 'eurasian':
        # Moderate tsunami risk
        for i in range(count):
            magnitude = 3.5 + random.random() * 4
            risk = 4 + random.random() * 3 if magnitude > 6.5 else 1 + random.random() * 3
            data.append({
                'x': round(magnitude, 1),
                'y': round(risk, 1)
            })
    elif plate_type == 'burma':
        # Variable tsunami risk
        for i in range(count):
            magnitude = 4.2 + random.random() * 3.8
            risk = 7 + random.random() * 2.5 if magnitude > 7.2 else 2.5 + random.random() * 3.5
            data.append({
                'x': round(magnitude, 1),
                'y': round(risk, 1)
            })
    
    return data

# EXISTING VIEW FUNCTIONS
@analyst_required
def analytics(request):
    context = get_dashboard_context(request.user)
    return render(request, 'analyst/index.html', context)

@analyst_required
def statistics(request):
    context = get_dashboard_context(request.user)
    return render(request, 'analyst/index.html', context)

@analyst_required
def reports(request):
    context = get_dashboard_context(request.user)
    return render(request, 'analyst/index.html', context)

@analyst_required
def data_management(request):
    context = get_dashboard_context(request.user)
    return render(request, 'analyst/index.html', context)