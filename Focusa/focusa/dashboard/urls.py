from django.urls import path
from .views import *

urlpatterns = [
    # Define your URL patterns here
    path('', dashboard, name='dashboard'),
    path('export/excel/', export_dashboard_excel, name='export_dashboard_excel'),
    path('export/pdf/', export_dashboard_pdf, name='export_dashboard_pdf'),
]