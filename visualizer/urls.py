from django.urls import path
from . import views
from login.views import home
urlpatterns = [
    path('', views.dashboard, name='dashboard')
]