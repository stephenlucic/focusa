from django.urls import path
from .views import ver_perfil
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(ver_perfil), name='perfil'),
]