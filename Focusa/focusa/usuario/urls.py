from django.urls import path
from .views import *

urlpatterns = [
    path('login/', iniciar_sesion, name='login'),
    path('registrar/', registrar, name='registrar'),
]
