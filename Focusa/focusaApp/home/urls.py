from django.urls import path
from .views import home_inicio

urlpatterns = [
    path('', home_inicio, name='home_inicio'),
]
