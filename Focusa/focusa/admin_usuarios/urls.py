from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(admin_usuarios), name='admin_usuarios'),
    path('editar/<int:user_id>/', login_required(editar_usuario), name='editar_usuario'),
    path('eliminar/<int:user_id>/', login_required(eliminar_usuario), name='eliminar_usuario'),
    path('crear/', login_required(crear_usuario), name='crear_usuario'),
    path('toggle-activo/<int:user_id>/', login_required(toggle_usuario_activo), name='toggle_usuario_activo')
    
]