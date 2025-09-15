from django.urls import path
from . import views

app_name = 'analyst'

urlpatterns = [
    # ========================================================================
    # MAIN DASHBOARD PAGES
    # ========================================================================
    path('', views.dashboard_home, name='dashboard_home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('statistics/', views.statistics, name='statistics'),
    path('reports/', views.reports, name='reports'),
    path('data-management/', views.data_management, name='data_management'),
   
    # ========================================================================
    # REPORT MANAGEMENT
    # ========================================================================
    path('reports/create/', views.create_report, name='create_report'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/edit/', views.edit_report, name='edit_report'),
    path('reports/<int:report_id>/submit/', views.submit_report, name='submit_report'),
    path('reports/my-reports/', views.my_reports, name='my_reports'),
    path('reports/<int:report_id>/update-status/', views.update_report_status, name='update_report_status'),
   
    # ========================================================================
    # API ENDPOINTS - DATA & ANALYTICS
    # ========================================================================
    path('api/buoy-data/', views.get_buoy_data, name='get_buoy_data'),
    path('api/refresh-data/', views.refresh_buoy_data, name='refresh_buoy_data'),
    path('api/storm-surge-data/', views.get_storm_surge_data, name='storm_surge_data'),
    path('api/seismic-data/', views.get_seismic_data, name='seismic_data'),
    path('api/risk-assessment/', views.get_risk_assessment, name='risk_assessment'),
    
    # ========================================================================
    # API ENDPOINTS - USER & REPORT MANAGEMENT
    # ========================================================================
    path('api/admin-users/', views.get_admin_users_api, name='api_admin_users'),
    path('api/report-status/<int:report_id>/', views.get_report_status_api, name='api_report_status'),
    path('api/validate-admin/<int:user_id>/', views.validate_admin_api, name='api_validate_admin'),
]