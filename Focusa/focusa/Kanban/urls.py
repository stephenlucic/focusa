from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Define your URL patterns here
    path('', login_required(kanban), name='kanban'),
    path('actualizar-estado/', login_required(actualizar_estado_tarea), name='kanban_actualizar_estado'),
    path('tarea/<int:pk>/', login_required(tarea_detalle_actualizar), name='kanban_tarea_detalle'),
    path('tarea/<int:pk>/eliminar/', login_required(eliminar_tarea), name='kanban_tarea_eliminar'),
    path('tag/<int:pk>/eliminar/', login_required(eliminar_tag), name='kanban_tag_eliminar'),
]