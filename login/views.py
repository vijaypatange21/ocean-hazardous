from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json
# Password reset imports
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomUserCreationForm, LoginForm, HazardReportForm, ReportFilterForm
from .models import UserProfile, HazardReport, HazardMedia
from visualizer.views import dashboard as visual_dashboard
from ocean_monitor.views import dashboard

def verify_wallet(request):
    return render(request, "login/verify_wallet.html")

@csrf_exempt
def save_wallet_address(request):
    if request.method == "POST":
        wallet_address = request.POST.get("wallet_address")
        if request.user.is_authenticated:
            profile = UserProfile.objects.get(user=request.user)
            profile.wallet_address = wallet_address
            profile.save()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})

def home(request):
    return render(request, 'home.html')
def menu(request):
    return render(request, 'menu.html')

from analyst import views as analysis_views
ANALYST_DASHBOARD = 'analyst:dashboard_home'
REPORTER_DASHBOARD = 'reporter_dashboard'
ADMIN_DASHBOARD = 'verify_wallet'

def user_login(request):
    # Redirect already authenticated users
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.user_type == 'analyst':
                return redirect(ANALYST_DASHBOARD)
            elif profile.user_type == 'reporter':
                return redirect(REPORTER_DASHBOARD)
            elif profile.user_type == 'admin':
                return redirect(ADMIN_DASHBOARD)
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found. Please contact administrator.')
            logout(request)
            return redirect('login')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.user_type == 'analyst':
                    return redirect(ANALYST_DASHBOARD)
                elif profile.user_type == 'reporter':
                    return redirect(REPORTER_DASHBOARD)
                elif profile.user_type == 'admin':
                    return redirect(ADMIN_DASHBOARD)
                else:
                    messages.error(request, 'Invalid user type.')
                    logout(request)
                    return redirect('login')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact administrator.')
                logout(request)
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'login/register.html', {'form': form})

def check_user_type(user, required_type):
    """Helper function to check if user has the required user type"""
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.user_type == required_type
    except UserProfile.DoesNotExist:
        return False


@login_required
def reporter_dashboard(request):
    if not check_user_type(request.user, 'reporter'):
        messages.error(request, 'Access denied. You do not have reporter permissions.')
        return redirect('login')
    
    # Get user profile for additional info
    profile = UserProfile.objects.get(user=request.user)
    
    # Get reporter statistics
    user_reports = HazardReport.objects.filter(reporter=request.user)
    total_reports = user_reports.count()
    this_month_reports = user_reports.filter(
        created_at__month=timezone.now().month,
        created_at__year=timezone.now().year
    ).count()
    verified_reports = user_reports.filter(status='verified').count()
    approval_rate = (verified_reports / total_reports * 100) if total_reports > 0 else 0
    
    context = {
        'user': request.user,
        'profile': profile,
        'total_reports': total_reports,
        'this_month_reports': this_month_reports,
        'approval_rate': round(approval_rate),
        'recent_reports': user_reports[:5],  # Last 5 reports
    }
    return render(request, 'login/reporter_dashboard.html', context)

@login_required
@login_required
def admin_dashboard(request):
    if not check_user_type(request.user, 'admin'):
        messages.error(request, 'Access denied. You do not have admin permissions.')
        return redirect('login')
    
    # Get user profile for additional info
    profile = UserProfile.objects.get(user=request.user)
    
    # Get some stats for admin
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    analyst_count = UserProfile.objects.filter(user_type='analyst').count()
    reporter_count = UserProfile.objects.filter(user_type='reporter').count()
    admin_count = UserProfile.objects.filter(user_type='admin').count()
    
    # Report statistics
    total_reports = HazardReport.objects.count()
    pending_reports = HazardReport.objects.filter(status='pending').count()
    critical_reports = HazardReport.objects.filter(severity='critical').count()
    today_reports = HazardReport.objects.filter(created_at__date=timezone.now().date()).count()
    
    context = {
        'user': request.user,
        'profile': profile,
        'total_users': total_users,
        'analyst_count': analyst_count,
        'reporter_count': reporter_count,
        'admin_count': admin_count,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'critical_reports': critical_reports,
        'today_reports': today_reports,
        # Add satellite dashboard link
        'show_satellite_link': True,
    }
    return render(request, 'login/admin_dashboard.html', context)


@login_required
def my_reports(request):
    """Display user's submitted reports"""
    if not check_user_type(request.user, 'reporter'):
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    # Get user's reports
    reports = HazardReport.objects.filter(reporter=request.user)
    
    # Apply filters
    filter_form = ReportFilterForm(request.GET or None)
    if filter_form.is_valid():
        time_filter = filter_form.cleaned_data['time_filter']
        hazard_type = filter_form.cleaned_data['hazard_type']
        severity = filter_form.cleaned_data['severity']
        status = filter_form.cleaned_data['status']
        search = filter_form.cleaned_data['search']
        
        # Apply time filter
        if time_filter == 'today':
            reports = reports.filter(created_at__date=timezone.now().date())
        elif time_filter == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            reports = reports.filter(created_at__gte=week_ago)
        elif time_filter == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            reports = reports.filter(created_at__gte=month_ago)
        
        # Apply other filters
        if hazard_type != 'all':
            reports = reports.filter(hazard_type=hazard_type)
        if severity != 'all':
            reports = reports.filter(severity=severity)
        if status != 'all':
            reports = reports.filter(status=status)
        if search:
            reports = reports.filter(
                Q(description__icontains=search) |
                Q(location_name__icontains=search) |
                Q(report_id__icontains=search)
            )
    
    # Pagination
    paginator = Paginator(reports, 10)  # 10 reports per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj,
        'filter_form': filter_form,
        'total_reports': reports.count(),
    }
    return render(request, 'my_reports.html', context)

@login_required
def view_all_reports(request):
    """View all reports (for analysts and admins)"""
    if not check_user_type(request.user, 'analyst') and not check_user_type(request.user, 'admin'):
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    # Get all reports
    reports = HazardReport.objects.all()
    
    # Apply filters
    filter_form = ReportFilterForm(request.GET or None)
    if filter_form.is_valid():
        time_filter = filter_form.cleaned_data['time_filter']
        hazard_type = filter_form.cleaned_data['hazard_type']
        severity = filter_form.cleaned_data['severity']
        status = filter_form.cleaned_data['status']
        search = filter_form.cleaned_data['search']
        
        # Apply time filter
        if time_filter == 'today':
            reports = reports.filter(created_at__date=timezone.now().date())
        elif time_filter == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            reports = reports.filter(created_at__gte=week_ago)
        elif time_filter == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            reports = reports.filter(created_at__gte=month_ago)
        
        # Apply other filters
        if hazard_type != 'all':
            reports = reports.filter(hazard_type=hazard_type)
        if severity != 'all':
            reports = reports.filter(severity=severity)
        if status != 'all':
            reports = reports.filter(status=status)
        if search:
            reports = reports.filter(
                Q(description__icontains=search) |
                Q(location_name__icontains=search) |
                Q(report_id__icontains=search) |
                Q(reporter__username__icontains=search)
            )
    
    # Pagination
    paginator = Paginator(reports, 15)  # 15 reports per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj,
        'filter_form': filter_form,
        'total_reports': reports.count(),
    }
    return render(request, 'reports/all_reports.html', context)

@login_required
def report_detail(request, report_id):
    """View detailed report information"""
    report = get_object_or_404(HazardReport, report_id=report_id)
    
    # Check permissions
    is_owner = report.reporter == request.user
    is_admin_or_analyst = check_user_type(request.user, 'admin') or check_user_type(request.user, 'analyst')
    
    if not (is_owner or is_admin_or_analyst):
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    context = {
        'report': report,
        'media_files': report.media_files.all(),
        'can_verify': is_admin_or_analyst,
    }
    return render(request, 'reports/report_detail.html', context)

@login_required
def update_report_status(request, report_id):
    """Update report status (admin/analyst only)"""
    if not (check_user_type(request.user, 'admin') or check_user_type(request.user, 'analyst')):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        report = get_object_or_404(HazardReport, report_id=report_id)
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        
        if new_status in ['pending', 'verified', 'rejected', 'investigating']:
            report.status = new_status
            report.admin_notes = admin_notes
            if new_status == 'verified':
                report.verified_by = request.user
                report.verified_at = timezone.now()
            report.save()
            
            return JsonResponse({'success': True, 'message': 'Report status updated successfully'})
        else:
            return JsonResponse({'error': 'Invalid status'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def map_data_api(request):
    """API endpoint for map data"""
    # Get all verified reports or all reports for admin/analyst
    if check_user_type(request.user, 'admin') or check_user_type(request.user, 'analyst'):
        reports = HazardReport.objects.all()
    else:
        reports = HazardReport.objects.filter(status='verified')
    
    # Apply filters from request
    time_filter = request.GET.get('time_filter', 'all')
    hazard_type = request.GET.get('hazard_type', 'all')
    severity = request.GET.get('severity', 'all')
    
    if time_filter == 'today':
        reports = reports.filter(created_at__date=timezone.now().date())
    elif time_filter == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        reports = reports.filter(created_at__gte=week_ago)
    
    if hazard_type != 'all':
        reports = reports.filter(hazard_type=hazard_type)
    
    if severity != 'all':
        reports = reports.filter(severity=severity)
    
    # Format data for map
    map_data = []
    for report in reports:
        map_data.append({
            'id': report.report_id,
            'lat': float(report.latitude),
            'lng': float(report.longitude),
            'hazard_type': report.get_hazard_type_display(),
            'severity': report.severity,
            'description': report.description[:100] + '...' if len(report.description) > 100 else report.description,
            'status': report.status,
            'created_at': report.created_at.strftime('%Y-%m-%d %H:%M'),
            'urgent': report.urgent,
            'reporter': report.reporter.get_full_name() or report.reporter.username,
        })
    
    return JsonResponse({'reports': map_data})

@login_required
def dashboard_stats_api(request):
    """API endpoint for dashboard statistics"""
    if check_user_type(request.user, 'reporter'):
        # Reporter stats
        user_reports = HazardReport.objects.filter(reporter=request.user)
        stats = {
            'total_reports': user_reports.count(),
            'this_month': user_reports.filter(
                created_at__month=timezone.now().month,
                created_at__year=timezone.now().year
            ).count(),
            'verified': user_reports.filter(status='verified').count(),
            'pending': user_reports.filter(status='pending').count(),
        }
    elif check_user_type(request.user, 'analyst') or check_user_type(request.user, 'admin'):
        # Analyst/Admin stats
        all_reports = HazardReport.objects.all()
        stats = {
            'total_reports': all_reports.count(),
            'today': all_reports.filter(created_at__date=timezone.now().date()).count(),
            'pending': all_reports.filter(status='pending').count(),
            'verified': all_reports.filter(status='verified').count(),
            'critical': all_reports.filter(severity='critical', status='pending').count(),
            'urgent': all_reports.filter(urgent=True, status='pending').count(),
        }
    else:
        stats = {}
    
    return JsonResponse(stats)

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def submit_hazard_report(request):
    """Handle hazard report submission with JSON response"""
    if not check_user_type(request.user, 'reporter'):
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Access denied. You do not have reporter permissions.'}, status=403)
        else:
            messages.error(request, 'Access denied. You do not have reporter permissions.')
            return redirect('login')
    
    if request.method == 'POST':
        # Debug: Print all POST data
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        
        form = HazardReportForm(request.POST)
        
        # Validate the form
        if form.is_valid():
            try:
                # Create the report
                report = form.save(commit=False)
                report.reporter = request.user
                
                # Try to reverse geocode the location name
                try:
                    latitude = float(form.cleaned_data['latitude'])
                    longitude = float(form.cleaned_data['longitude'])
                    report.location_name = get_location_name(latitude, longitude)
                except:
                    report.location_name = f"Lat: {report.latitude}, Lng: {report.longitude}"
                
                report.save()
                
                # Handle file uploads
                files = request.FILES.getlist('media_files')
                uploaded_files = []
                
                for file in files:
                    try:
                        # Create media object
                        media = HazardMedia(report=report, file=file)
                        
                        # Auto-detect media type
                        file_ext = file.name.lower().split('.')[-1]
                        if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                            media.media_type = 'image'
                        elif file_ext in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm']:
                            media.media_type = 'video'
                        
                        media.save()
                        uploaded_files.append({
                            'name': file.name,
                            'size': file.size,
                            'type': media.media_type
                        })
                    except Exception as e:
                        print(f"Error uploading file {file.name}: {str(e)}")
                        continue
                
                # Send urgent notification if needed
                if report.urgent:
                    send_urgent_notification(report)
                
                # Return JSON response for AJAX requests
                if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Report {report.report_id} submitted successfully! Thank you for helping keep our coastal communities safe.',
                        'report_id': report.report_id,
                        'uploaded_files': uploaded_files
                    })
                else:
                    # Regular form submission
                    messages.success(request, f'Report {report.report_id} submitted successfully! Thank you for helping keep our coastal communities safe.')
                    return redirect('reporter_dashboard')
                    
            except Exception as e:
                error_message = f'Error saving report: {str(e)}'
                print(error_message)
                
                if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': error_message}, status=500)
                else:
                    messages.error(request, error_message)
                    return redirect('reporter_dashboard')
        else:
            # Form validation errors
            print("Form errors:", form.errors)
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            error_text = "; ".join(error_messages)
            
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Please correct the errors in the form.',
                    'form_errors': form.errors,
                    'details': error_text
                }, status=400)
            else:
                messages.error(request, f'Please correct the errors: {error_text}')
                return redirect('reporter_dashboard')
    
    # GET request - this shouldn't happen for AJAX, but handle it anyway
    form = HazardReportForm()
    return redirect('reporter_dashboard')

# Fixed get_location_name function
def get_location_name(latitude, longitude):
    """
    Reverse geocode coordinates to get location name using OpenStreetMap Nominatim
    """
    try:
        import requests
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'OceanHazardSystem/1.0'  # Required by Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'display_name' in data:
                return data['display_name'][:255]  # Limit to model field length
        
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    # Fallback to coordinates
    return f"Lat: {latitude:.4f}, Lng: {longitude:.4f}"

def send_urgent_notification(report):
    """
    Send notifications for urgent reports
    """
    try:
        # You can implement email/SMS notifications here
        print(f"URGENT REPORT: {report.report_id} - {report.hazard_type} at {report.location_name}")

        # Example: Send email to administrators
        # from django.core.mail import send_mail
        # admin_emails = ['admin@oceanhazard.com']
        # send_mail(
        #     subject=f'URGENT: {report.hazard_type} Report #{report.report_id}',
        #     message=f'Urgent hazard report submitted: {report.description}',
        #     from_email='noreply@oceanhazard.com',
        #     recipient_list=admin_emails,
        #     fail_silently=True,
        # )

    except Exception as e:
        print(f"Notification error: {e}")


# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with custom template"""
    template_name = 'login/password_reset.html'
    email_template_name = 'login/password_reset_email.html'
    subject_template_name = 'login/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    form_class = PasswordResetForm


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Password reset done view"""
    template_name = 'login/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirm view"""
    template_name = 'login/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Password reset complete view"""
    template_name = 'login/password_reset_complete.html'


# Function-based views for password reset (alternative approach)
def password_reset_request(request):
    """Handle password reset request"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='login/password_reset_email.html',
                subject_template_name='login/password_reset_subject.txt'
            )
            messages.success(request, 'Password reset email has been sent. Please check your email.')
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'login/password_reset.html', {'form': form})


def password_reset_done(request):
    """Show password reset done page"""
    return render(request, 'login/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    """Handle password reset confirmation"""
    from django.contrib.auth.views import PasswordResetConfirmView
    from django.contrib.auth.forms import SetPasswordForm

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'login/password_reset_confirm.html', {'form': form, 'validlink': True})
    else:
        return render(request, 'login/password_reset_confirm.html', {'form': None, 'validlink': False})


def password_reset_complete(request):
    """Show password reset complete page"""
    return render(request, 'login/password_reset_complete.html')


# Import required modules for password reset confirm
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User