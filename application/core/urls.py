from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboard UI
    path('', views.dashboard, name='dashboard'),

    # English REST API endpoints
    path('api/health/', views.api_health, name='api_health'),
    path('api/patients/', views.patient_list, name='patient_list'),
    path('api/doctors/', views.doctor_list, name='doctor_list'),
    path('api/patient/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('api/patient/save/', views.patient_save, name='patient_save'),
    path('api/patient/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
]

