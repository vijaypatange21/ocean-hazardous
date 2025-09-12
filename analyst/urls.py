# analyst/urls.py
from django.urls import path
from . import views

app_name = 'analyst'

urlpatterns = [
    # Main pages
    path('', views.dashboard_home, name='dashboard_home'),
    path('analytics/', views.analytics, name='analytics'),
    path('statistics/', views.statistics, name='statistics'),
    path('reports/', views.reports, name='reports'),
    path('data-management/', views.data_management, name='data_management'),
   
    # API endpoints for live data
    path('api/buoy-data/', views.get_buoy_data, name='get_buoy_data'),
    path('api/refresh-data/', views.refresh_buoy_data, name='refresh_buoy_data'),
    
    # New API endpoints for Indian Ocean analytics
    path('api/storm-surge-data/', views.get_storm_surge_data, name='storm_surge_data'),
    path('api/seismic-data/', views.get_seismic_data, name='seismic_data'),
    path('api/risk-assessment/', views.get_risk_assessment, name='risk_assessment'),
    # for report creating 
    path('create-report/', views.create_report, name='create_report'),
    path('submit-report/<int:report_id>/', views.submit_report, name='submit_report'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('update-status/<int:report_id>/', views.update_report_status, name='update_report_status'),
    path('api/report-status/<int:report_id>/', views.get_report_status, name='get_report_status'),
]