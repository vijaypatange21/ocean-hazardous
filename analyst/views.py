# ============================================================================
# IMPORTS
# ============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from login.models import UserProfile
from .models import DartBuoy, update_india_buoys, BuoyReading, Report, ReportComment
import json
import random
import math
from datetime import datetime, timedelta

# ============================================================================
# DECORATORS AND HELPER FUNCTIONS
# ============================================================================

def analyst_required(view_func):
    """Decorator to ensure user has analyst privileges"""
    def wrapper(request, *args, **kwargs):
        try:
            user_type = request.user.userprofile.user_type
            # Allow both analysts and admins to access analyst dashboard
            if user_type not in ['analyst', 'admin']:
                return redirect('login')
        except UserProfile.DoesNotExist:
            messages.error(request, "User profile not found.")
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

def get_admin_users():
    """Get all admin users for dropdowns and validation"""
    admin_profiles = UserProfile.objects.filter(user_type='admin').select_related('user')
    return [profile.user for profile in admin_profiles]

# ============================================================================
# MAIN DASHBOARD VIEWS
# ============================================================================

@analyst_required
def dashboard_home(request):
    """Main dashboard view with admin user filtering"""
    update_india_buoys()
    
    buoys = DartBuoy.objects.all()
    admin_list = get_admin_users()
    reports = Report.objects.filter(created_by=request.user)
    
    context = {
        'buoys': buoys,
        'admin_list': admin_list,
        'reports': reports,
        'total_reports': reports.count(),
        'draft_reports': reports.filter(status='draft').count(),
        'submitted_reports': reports.filter(status='submitted').count(),
        'approved_reports': reports.filter(status='approved').count(),
        **get_dashboard_context(request.user)
    }
    return render(request, 'analyst/index.html', context)

@analyst_required
def dashboard(request):
    """Alternative dashboard view"""
    reports = Report.objects.filter(created_by=request.user)
    admin_list = get_admin_users()
    
    context = {
        'reports': reports,
        'admin_list': admin_list,
        'total_reports': reports.count(),
        'draft_reports': reports.filter(status='draft').count(),
        'submitted_reports': reports.filter(status='submitted').count(),
        'approved_reports': reports.filter(status='approved').count(),
    }
    return render(request, 'analyst/index.html', context)

# ============================================================================
# REPORT MANAGEMENT VIEWS
# ============================================================================

@analyst_required
def create_report(request):
    """Create a new report"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        report_type = request.POST.get('report_type')
        submitted_to_id = request.POST.get('submitted_to') or request.POST.get('admin')
        attachment = request.FILES.get('attachment')
        
        if not all([title, report_type, submitted_to_id]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('analyst:dashboard_home')
        
        # Validate submitted_to is actually an admin
        try:
            admin_user = User.objects.get(id=submitted_to_id)
            admin_profile = UserProfile.objects.get(user=admin_user)
            if admin_profile.user_type != 'admin':
                messages.error(request, "Selected user is not an admin.")
                return redirect('analyst:dashboard_home')
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, "Invalid admin selection.")
            return redirect('analyst:dashboard_home')
        
        try:
            report = Report.objects.create(
                title=title,
                description=description,
                report_type=report_type,
                submitted_to=admin_user,
                created_by=request.user,
                attachment=attachment,
            )
            
            messages.success(request, f'Report "{title}" created successfully!')
            return redirect('analyst:dashboard_home')
            
        except Exception as e:
            messages.error(request, f'Error creating report: {str(e)}')
            return redirect('analyst:dashboard_home')
    
    return redirect('analyst:dashboard_home')

@analyst_required
def submit_report(request, report_id):
    """Submit a draft report to an admin"""
    report = get_object_or_404(Report, id=report_id, created_by=request.user)
    
    if request.method == 'POST':
        submitted_to_id = request.POST.get('submitted_to') or request.POST.get('admin_id')
        
        if not submitted_to_id:
            messages.error(request, 'Please select an admin to submit to.')
            return redirect('analyst:dashboard_home')
        
        # Validate submitted_to is actually an admin
        try:
            admin_user = User.objects.get(id=submitted_to_id)
            admin_profile = UserProfile.objects.get(user=admin_user)
            if admin_profile.user_type != 'admin':
                messages.error(request, "Selected user is not an admin.")
                return redirect('analyst:dashboard_home')
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, "Invalid admin selection.")
            return redirect('analyst:dashboard_home')
        
        try:
            report.submitted_to = admin_user
            report.status = 'submitted'
            report.submitted_at = timezone.now()
            report.save()
            
            messages.success(request, f'Report "{report.title}" submitted to {admin_user.get_full_name() or admin_user.username} successfully!')
            
        except Exception as e:
            messages.error(request, f'Error submitting report: {str(e)}')
    
    return redirect('analyst:dashboard_home')

@analyst_required
def report_detail(request, report_id):
    """View detailed report information"""
    report = get_object_or_404(Report, id=report_id, created_by=request.user)
    comments = report.comments.all()
    admin_list = get_admin_users()
    
    context = {
        'report': report,
        'comments': comments,
        'admin_list': admin_list,
    }
    return render(request, 'analyst/report_detail.html', context)

@analyst_required
def edit_report(request, report_id):
    """Edit an existing report (only drafts can be edited)"""
    report = get_object_or_404(Report, id=report_id, created_by=request.user)
    
    if report.status != 'draft':
        messages.error(request, 'Only draft reports can be edited.')
        return redirect('analyst:report_detail', report_id=report.id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        report_type = request.POST.get('report_type')
        submitted_to_id = request.POST.get('submitted_to')
        attachment = request.FILES.get('attachment')
        
        # Validate submitted_to is actually an admin if provided
        if submitted_to_id:
            try:
                admin_user = User.objects.get(id=submitted_to_id)
                admin_profile = UserProfile.objects.get(user=admin_user)
                if admin_profile.user_type != 'admin':
                    messages.error(request, "Selected user is not an admin.")
                    return redirect('analyst:report_detail', report_id=report.id)
                report.submitted_to = admin_user
            except (User.DoesNotExist, UserProfile.DoesNotExist):
                messages.error(request, "Invalid admin selection.")
                return redirect('analyst:report_detail', report_id=report.id)
        
        # Update report fields
        if title:
            report.title = title
        if description:
            report.description = description
        if report_type:
            report.report_type = report_type
        if attachment:
            report.attachment = attachment
        
        report.save()
        messages.success(request, 'Report updated successfully!')
        return redirect('analyst:report_detail', report_id=report.id)
    
    admin_list = get_admin_users()
    context = {
        'report': report,
        'admin_list': admin_list,
    }
    return render(request, 'analyst/edit_report.html', context)

@analyst_required
def my_reports(request):
    """View all reports created by current user"""
    reports = Report.objects.filter(created_by=request.user).order_by('-created_at')
    admin_list = get_admin_users()
    
    context = {
        'reports': reports,
        'admin_list': admin_list,
        'total_reports': reports.count(),
        'draft_reports': reports.filter(status='draft').count(),
        'submitted_reports': reports.filter(status='submitted').count(),
        'approved_reports': reports.filter(status='approved').count(),
    }
    return render(request, 'analyst/my_reports.html', context)

@analyst_required
def update_report_status(request, report_id):
    """Update report status (admin-only function)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'admin':
            messages.error(request, 'Permission denied. Admin privileges required.')
            return redirect('analyst:report_detail', report_id=report_id)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('analyst:report_detail', report_id=report_id)
    
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        comment_text = request.POST.get('comment', '')
        
        if new_status in ['approved', 'rejected']:
            report.status = new_status
            report.save()
            
            if comment_text:
                ReportComment.objects.create(
                    report=report,
                    user=request.user,
                    comment=comment_text
                )
            
            messages.success(request, f'Report status updated to {new_status}.')
        
    return redirect('analyst:report_detail', report_id=report.id)

# ============================================================================
# SECTION VIEWS
# ============================================================================

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
    reports = Report.objects.filter(created_by=request.user)
    admin_list = get_admin_users()
    
    context = {
        'reports': reports,
        'admin_list': admin_list,
        'total_reports': reports.count(),
        'draft_reports': reports.filter(status='draft').count(),
        'submitted_reports': reports.filter(status='submitted').count(),
        'approved_reports': reports.filter(status='approved').count(),
        **get_dashboard_context(request.user)
    }
    return render(request, 'analyst/index.html', context)

@analyst_required
def data_management(request):
    context = get_dashboard_context(request.user)
    return render(request, 'analyst/index.html', context)

# ============================================================================
# API ENDPOINTS - REPORT STATUS
# ============================================================================

@analyst_required
def get_report_status(request, report_id):
    """Get current report status (AJAX endpoint)"""
    report = get_object_or_404(Report, id=report_id, created_by=request.user)
    
    data = {
        'status': report.status,
        'status_display': report.get_status_display(),
        'submitted_to': report.submitted_to.get_full_name() if report.submitted_to else None,
        'submitted_at': report.submitted_at.isoformat() if report.submitted_at else None,
    }
    
    return JsonResponse(data)

@analyst_required
def get_report_status_api(request, report_id):
    """Alternative API endpoint for report status"""
    return get_report_status(request, report_id)

@analyst_required
def get_admin_users_api(request):
    """API endpoint to get admin users (AJAX)"""
    admin_profiles = UserProfile.objects.filter(user_type='admin').select_related('user')
    
    admin_data = []
    for profile in admin_profiles:
        user = profile.user
        admin_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'department': profile.department or 'N/A'
        })
    
    return JsonResponse({'admins': admin_data})

@analyst_required
def validate_admin_api(request, user_id):
    """API endpoint to validate if a user is an admin"""
    try:
        user = User.objects.get(id=user_id)
        profile = UserProfile.objects.get(user=user)
        is_admin = profile.user_type == 'admin'
        
        return JsonResponse({
            'is_admin': is_admin,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'email': user.email
        })
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return JsonResponse({'is_admin': False}, status=404)

# ============================================================================
# API ENDPOINTS - BUOY DATA
# ============================================================================

@analyst_required
def get_buoy_data(request):
    """API endpoint to get live buoy data for charts"""
    try:
        buoys_data = []
        for buoy in DartBuoy.objects.all():
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

# ============================================================================
# API ENDPOINTS - STORM SURGE DATA
# ============================================================================

@analyst_required
def get_storm_surge_data(request):
    """API endpoint for storm surge data"""
    try:
        now = timezone.now()
        time_labels = []
        for i in range(12):
            time = now + timedelta(hours=i*2)
            time_labels.append(time.strftime('%H:%M'))
        
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

# ============================================================================
# API ENDPOINTS - SEISMIC DATA
# ============================================================================

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

# ============================================================================
# DATA GENERATION UTILITIES
# ============================================================================

def generate_surge_data(base_height, points):
    """Generate realistic storm surge data"""
    data = []
    for i in range(points):
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
        for i in range(count):
            magnitude = 4 + random.random() * 4.5
            risk = 6 + random.random() * 3 if magnitude > 7 else 2 + random.random() * 4
            data.append({
                'x': round(magnitude, 1),
                'y': round(risk, 1)
            })
    elif plate_type == 'eurasian':
        for i in range(count):
            magnitude = 3.5 + random.random() * 4
            risk = 4 + random.random() * 3 if magnitude > 6.5 else 1 + random.random() * 3
            data.append({
                'x': round(magnitude, 1),
                'y': round(risk, 1)
            })
    elif plate_type == 'burma':
        for i in range(count):
            magnitude = 4.2 + random.random() * 3.8
            risk = 7 + random.random() * 2.5 if magnitude > 7.2 else 2.5 + random.random() * 3.5
            data.append({
                'x': round(magnitude, 1),
                'y': round(risk, 1)
            })
    
    return data