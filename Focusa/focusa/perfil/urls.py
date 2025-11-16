from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(ver_perfil_publico), name='perfil'),
    path('editar/', login_required(editar_perfil_ficticio), name='perfil_editar'),
]