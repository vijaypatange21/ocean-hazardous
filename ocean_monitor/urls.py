from django.urls import path
from . import views

app_name = 'ocean_monitor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/satellite-data/', views.get_satellite_data, name='satellite_data'),
    path('api/ocean-hazards/', views.get_ocean_hazards, name='ocean_hazards'),
]