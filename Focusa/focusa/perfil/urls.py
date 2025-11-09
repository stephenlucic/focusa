from django.urls import path
from .views import *

urlpatterns = [
    path('', ver_perfil_publico, name='perfil'),
    path('editar/', editar_perfil_ficticio, name='perfil_editar'),
]