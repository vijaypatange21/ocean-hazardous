from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from login.models import HazardReport
from datetime import timedelta
from django.utils import timezone

# Create your views here.
# @login_required
def dashboard(request):
    if request.method == "GET":
        hazards = HazardReport.objects.all()
        filters = {}
    elif request.method == "POST":
        time_range = request.POST.get('time-range')
        value = int(time_range[:-1])
        unit = (time_range[-1])
        if unit == 'd':
            time = timezone.now() - timedelta(days=value)
        else:
            time = timezone.now() - timedelta(hours=value)
        hazards = HazardReport.objects.filter(created_at__gte =time)
        hazard_type = request.POST.get('hazard-type')
        if request.POST.get('hazard-type'):
            hazards = hazards.filter(hazard_type = request.POST.get('hazard-type'))
        
        severity = request.POST.get('severity')
        if request.POST.get('severity'):
            hazards = hazards.filter(severity = request.POST.get('severity'))
        
        filters = {'time_range': time_range, "hazard_type": hazard_type, "severity": severity}
        
    hazards_in_json = []
    for hazard in hazards:
        hazard_in_json = dict()
        hazard_in_json['lat'] = hazard.latitude
        hazard_in_json['lng'] = hazard.longitude
        hazard_in_json['hazardType'] = hazard.hazard_type
        hazard_in_json['severity'] = hazard.severity
        hazard_in_json['time'] = hazard.created_at
        hazard_in_json['location'] = hazard.location_name
        hazard_in_json['description'] = hazard.description

        hazards_in_json.append(hazard_in_json)
    

    return render(request, 'dashboard.html', {'hazards': hazards_in_json, 'filters': filters})