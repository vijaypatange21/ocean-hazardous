from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from visualizer.views import dashboard as visual_dashboard

urlpatterns = [
    # Core Pages
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('operations/', views.operations, name='operations'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),
    
    # Dashboards
    path('reporter-dashboard/', views.reporter_dashboard, name='reporter_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # External App Integration
    path('satellite/', include('ocean_monitor.urls')),
    path("map/", visual_dashboard, name="reporter_dashboard_map"),
    
    # Wallet Management
    path("verify-wallet/", views.verify_wallet, name="verify_wallet"),
    path("save-wallet/", views.save_wallet_address, name="save_wallet_address"),
    
    # Report Management - Hazard Reports
    path('reports/submit/', views.submit_hazard_report, name='submit_report'),
    path('reports/my-reports/', views.my_reports, name='my_reports'),
    path('reports/all/', views.view_all_reports, name='all_reports'),
    path('reports/<str:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<str:report_id>/update-status/', views.update_report_status, name='update_report_status'),
    
    # Report Management - Analyst Reports
    path('reports/analyst/', views.admin_view_analyst_reports, name='admin_view_analyst_reports'),
    path('reports/analyst/<int:report_id>/', views.admin_report_detail, name='admin_report_detail'),
    path('reports/analyst/<int:report_id>/update/', views.admin_update_report_status, name='admin_update_report_status'),
    
    # API Endpoints
    path('api/map-data/', views.map_data_api, name='map_data_api'),
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)