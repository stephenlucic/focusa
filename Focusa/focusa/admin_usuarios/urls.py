from django.urls import path
from .views import admin_usuarios, editar_usuario, eliminar_usuario, crear_usuario
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(admin_usuarios), name='admin_usuarios'),
    path('editar/<int:user_id>/', login_required(editar_usuario), name='editar_usuario'),
    path('eliminar/<int:user_id>/', login_required(eliminar_usuario), name='eliminar_usuario'),
    path('crear/', login_required(crear_usuario), name='crear_usuario'),
]