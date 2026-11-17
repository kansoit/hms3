"""
URL configuration for hms_project.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('core.urls')),
]
