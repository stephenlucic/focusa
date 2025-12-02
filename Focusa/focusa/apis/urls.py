from django.urls import path
from .views import *

urlpatterns = [
    # Tareas
    path('tareas/crear/', crear_tarea, name='api_crear_tarea'),
    path('tareas/<str:username>/', listar_tareas_usuario, name='api_listar_tareas_usuario'),
    path('tareas/<int:tarea_id>/editar/', editar_tarea, name='api_editar_tarea'),
    path('tareas/<int:tarea_id>/eliminar/', eliminar_tarea_api, name='api_eliminar_tarea'),

    # Tags
    path('tags/crear/', crear_tag, name='api_crear_tag'),
    path('tags/<str:username>/', listar_tags_usuario, name='api_listar_tags_usuario'),
    path('tags/<int:tag_id>/editar/', editar_tag, name='api_editar_tag'),
    path('tags/<int:tag_id>/eliminar/', eliminar_tag_api, name='api_eliminar_tag'),

    # Usuarios
    path('usuarios/crear/', crear_usuario, name='api_crear_usuario'),
    path('usuarios/', listar_usuarios, name='api_listar_usuarios'),
    path('usuarios/<int:user_id>/editar/', editar_usuario_api, name='api_editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', eliminar_usuario_api, name='api_eliminar_usuario'),

]
