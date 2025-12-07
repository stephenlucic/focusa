from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_admin, name='dashboard_admin'),
    path('exportar-pdf/', views.exportar_dashboard_pdf, name='exportar_dashboard_pdf'),
]